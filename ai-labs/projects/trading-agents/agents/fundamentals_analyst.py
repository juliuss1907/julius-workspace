"""
Fundamentals Analyst Agent
"""
from datetime import datetime
from typing import Dict, Optional

from agents.base_agent import BaseAgent, AgentResult, SignalDirection
from utils import get_logger, config


logger = get_logger(__name__)


class FundamentalsAnalyst(BaseAgent):
    """Analyze market-structure fundamentals from CoinGecko data."""

    def __init__(self, config_override: Optional[Dict] = None):
        super().__init__("FundamentalsAnalyst", config_override)
        default_config = config.load_default_params()
        self.config = {**default_config.get("fundamentals_analysis", {}), **(config_override or {})}

        self.weights = self.config.get(
            "weights",
            {
                "valuation": 0.35,
                "supply": 0.30,
                "liquidity": 0.20,
                "context": 0.15,
            },
        )

    async def initialize(self):
        if self._initialized:
            return
        logger.info("FundamentalsAnalyst initialized")
        self._initialized = True

    async def analyze(self, symbol: str, data: Dict) -> AgentResult:
        if not self._initialized:
            await self.initialize()

        fundamentals = data.get("fundamentals")
        if not fundamentals:
            return self._create_neutral_result(symbol, "No fundamentals data available")

        valuation = self._score_valuation(fundamentals)
        supply = self._score_supply(fundamentals)
        liquidity = self._score_liquidity(fundamentals)
        context = self._score_context(fundamentals)

        sub_score = self._calculate_overall_score(
            {
                "valuation": valuation["score"],
                "supply": supply["score"],
                "liquidity": liquidity["score"],
                "context": context["score"],
            }
        )
        direction = self._determine_direction(sub_score)
        confidence = self._calculate_confidence(fundamentals)

        analysis = {
            "valuation": valuation,
            "supply": supply,
            "liquidity": liquidity,
            "context": context,
            "overall": {
                "sub_score": sub_score,
                "confidence": confidence,
                "direction": direction.value,
            },
        }

        reasoning = self._generate_reasoning(valuation, supply, liquidity, context, direction)

        return AgentResult(
            agent_name=self.name,
            symbol=symbol,
            timestamp=datetime.now(),
            direction=direction,
            sub_score=sub_score,
            confidence=confidence,
            analysis=analysis,
            reasoning=reasoning,
            metadata={"source": "coingecko"},
        )

    def _score_valuation(self, f: Dict) -> Dict:
        market_cap = float(f.get("market_cap") or 0)
        fdv = float(f.get("fdv") or 0)
        rank = int(f.get("market_cap_rank") or 999999)
        ath_change_pct = float(f.get("ath_change_pct") or 0)

        ratio = (fdv / market_cap) if market_cap > 0 and fdv > 0 else None
        score = 0.5

        if ratio is not None:
            if ratio <= 1.2:
                score += 0.20
            elif ratio <= 1.8:
                score += 0.05
            else:
                score -= 0.15

        if rank <= 10:
            score += 0.10
        elif rank <= 50:
            score += 0.05
        else:
            score -= 0.05

        # Deep drawdown can be attractive if fundamentals are otherwise solid.
        if ath_change_pct <= -60:
            score += 0.05
        elif ath_change_pct >= -10:
            score -= 0.05

        return {
            "market_cap": market_cap,
            "fdv": fdv,
            "fdv_market_cap_ratio": ratio,
            "rank": rank,
            "ath_change_pct": ath_change_pct,
            "score": self._clamp_score(score),
        }

    def _score_supply(self, f: Dict) -> Dict:
        circulating = float(f.get("circulating_supply") or 0)
        max_supply = f.get("max_supply")
        max_supply = float(max_supply) if max_supply else None

        score = 0.5
        circ_ratio = None

        if max_supply and max_supply > 0:
            circ_ratio = circulating / max_supply
            if circ_ratio >= 0.8:
                score += 0.20
            elif circ_ratio >= 0.5:
                score += 0.05
            else:
                score -= 0.15
        else:
            score -= 0.05

        return {
            "circulating_supply": circulating,
            "max_supply": max_supply,
            "circulating_ratio": circ_ratio,
            "score": self._clamp_score(score),
        }

    def _score_liquidity(self, f: Dict) -> Dict:
        market_cap = float(f.get("market_cap") or 0)
        volume_24h = float(f.get("volume_24h") or 0)
        ratio = (volume_24h / market_cap) if market_cap > 0 else 0

        score = 0.5
        if ratio >= 0.10:
            score += 0.20
        elif ratio >= 0.03:
            score += 0.05
        else:
            score -= 0.10

        return {
            "volume_24h": volume_24h,
            "volume_market_cap_ratio": ratio,
            "score": self._clamp_score(score),
        }

    def _score_context(self, f: Dict) -> Dict:
        change_24h = float(f.get("price_change_24h_pct") or 0)
        change_7d = float(f.get("price_change_7d_pct") or 0)
        categories = f.get("categories") or []

        score = 0.5
        if change_7d >= 10:
            score += 0.10
        elif change_7d <= -10:
            score -= 0.10

        if change_24h >= 5:
            score += 0.05
        elif change_24h <= -5:
            score -= 0.05

        if categories:
            score += 0.03

        return {
            "price_change_24h_pct": change_24h,
            "price_change_7d_pct": change_7d,
            "categories": categories[:5],
            "score": self._clamp_score(score),
        }

    def _calculate_overall_score(self, scores: Dict) -> float:
        total = 0.0
        total_weight = 0.0
        for key, weight in self.weights.items():
            total += scores.get(key, 0.5) * weight
            total_weight += weight
        if total_weight == 0:
            return 0.5
        return self._clamp_score(total / total_weight)

    def _calculate_confidence(self, f: Dict) -> float:
        confidence = 0.5

        required_fields = [
            "market_cap",
            "fdv",
            "circulating_supply",
            "volume_24h",
            "market_cap_rank",
        ]
        present = sum(1 for field in required_fields if f.get(field) not in (None, 0, ""))
        confidence += (present / len(required_fields)) * 0.15

        rank = int(f.get("market_cap_rank") or 999999)
        if rank <= 10:
            confidence += 0.10
        elif rank <= 50:
            confidence += 0.05

        if f.get("max_supply"):
            confidence += 0.05
        else:
            confidence -= 0.05

        market_cap = float(f.get("market_cap") or 0)
        volume_24h = float(f.get("volume_24h") or 0)
        if market_cap > 0 and (volume_24h / market_cap) >= 0.03:
            confidence += 0.05
        else:
            confidence -= 0.05

        return self._clamp_score(confidence)

    def _generate_reasoning(self, valuation: Dict, supply: Dict, liquidity: Dict, context: Dict, direction: SignalDirection) -> str:
        parts = []

        ratio = valuation.get("fdv_market_cap_ratio")
        if ratio is not None:
            if ratio <= 1.2:
                parts.append("FDV close to market cap")
            elif ratio > 1.8:
                parts.append("high dilution risk from FDV")

        circ_ratio = supply.get("circulating_ratio")
        if circ_ratio is not None:
            if circ_ratio >= 0.8:
                parts.append("most supply already circulating")
            elif circ_ratio < 0.5:
                parts.append("large remaining supply unlock risk")
        else:
            parts.append("max supply unavailable")

        vol_ratio = liquidity.get("volume_market_cap_ratio", 0)
        if vol_ratio >= 0.10:
            parts.append("strong liquidity participation")
        elif vol_ratio < 0.03:
            parts.append("weak volume relative to market cap")

        rank = valuation.get("rank", 999999)
        if rank <= 10:
            parts.append(f"top-{rank} market cap asset")

        if direction == SignalDirection.BULLISH and context["price_change_7d_pct"] > 0:
            parts.append("positive 7d context")
        elif direction == SignalDirection.BEARISH and context["price_change_7d_pct"] < 0:
            parts.append("negative 7d context")

        return "; ".join(parts) if parts else "Fundamentals mixed"

    def _create_neutral_result(self, symbol: str, reason: str) -> AgentResult:
        return AgentResult(
            agent_name=self.name,
            symbol=symbol,
            timestamp=datetime.now(),
            direction=SignalDirection.NEUTRAL,
            sub_score=0.5,
            confidence=0.3,
            analysis={"error": reason},
            reasoning=reason,
            metadata={"error": True},
        )

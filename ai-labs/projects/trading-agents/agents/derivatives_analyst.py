"""
Derivatives Analyst Agent

Analyzes funding, open interest, long/short ratio, and cross-source agreement.
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from agents.base_agent import BaseAgent, AgentResult, SignalDirection
from dataflows import BinanceDerivativesClient, HyperliquidClient, LighterClient
from utils import get_logger, config


logger = get_logger(__name__)


class DerivativesAnalyst(BaseAgent):
    """Analyze perp market structure for contrarian and confirmation signals."""

    def __init__(self, config_override: Optional[Dict] = None):
        super().__init__("DerivativesAnalyst", config_override)
        default_config = config.load_default_params()
        self.config = {**default_config.get("derivatives_analysis", {}), **(config_override or {})}
        self.binance = BinanceDerivativesClient()
        self.hyperliquid = HyperliquidClient()
        self.lighter = LighterClient()
        self.weights = self.config.get(
            "weights",
            {
                "funding": 0.40,
                "oi_price": 0.35,
                "cross_source": 0.15,
                "data_quality": 0.10,
            },
        )

    async def initialize(self):
        if self._initialized:
            return
        logger.info("DerivativesAnalyst initialized")
        self._initialized = True

    async def analyze(self, symbol: str, data: Dict) -> AgentResult:
        if not self._initialized:
            await self.initialize()

        derivatives = data.get("derivatives")
        if not derivatives:
            derivatives = await self._fetch_derivatives(symbol)

        sources = {name: snapshot for name, snapshot in derivatives.items() if snapshot}
        if not sources:
            return self._neutral_result(symbol, "No derivatives data available", confidence=0.0)

        ohlcv = data.get("ohlcv", [])
        price_trend = self._detect_price_trend(ohlcv, sources)
        scores = {
            "funding": self._score_funding(sources),
            "oi_price": self._score_oi_price(sources, price_trend),
            "cross_source": self._score_cross_source(sources),
            "data_quality": self._score_data_quality(sources),
        }
        sub_score = self._calculate_overall_score(scores)
        confidence = self._calculate_confidence(sources, scores)
        direction = self._determine_direction(sub_score)
        reasoning = self._generate_reasoning(sources, scores, price_trend, direction)

        analysis = {
            "sources": sources,
            "source_count": len(sources),
            "price_trend": price_trend,
            "scores": scores,
            "funding": self._funding_summary(sources),
            "open_interest": self._open_interest_summary(sources),
            "overall": {
                "sub_score": sub_score,
                "confidence": confidence,
                "direction": direction.value,
            },
        }

        return AgentResult(
            agent_name=self.name,
            symbol=symbol,
            timestamp=datetime.now(),
            direction=direction,
            sub_score=sub_score,
            confidence=confidence,
            analysis=analysis,
            reasoning=reasoning,
            metadata={"sources": list(sources.keys()), "price_trend": price_trend},
        )

    async def _fetch_derivatives(self, symbol: str) -> Dict[str, Optional[Dict]]:
        tasks = {
            "binance": self.binance.fetch_derivatives_snapshot(symbol),
            "hyperliquid": self.hyperliquid.fetch_derivatives_snapshot(symbol),
            "lighter": self.lighter.fetch_derivatives_snapshot(symbol),
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        snapshots = {}
        for name, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                logger.warning(f"{name} derivatives fetch failed for {symbol}: {result}")
                snapshots[name] = None
            else:
                snapshots[name] = result
        return snapshots

    def _detect_price_trend(self, ohlcv: List[Dict], sources: Dict[str, Dict]) -> str:
        if len(ohlcv) >= 12:
            recent = float(ohlcv[-1].get("close") or 0)
            previous = float(ohlcv[-12].get("close") or 0)
            if previous > 0:
                change = (recent - previous) / previous
                if change >= 0.01:
                    return "up"
                if change <= -0.01:
                    return "down"

        changes = [s.get("price_change_24h_pct") for s in sources.values() if s.get("price_change_24h_pct") is not None]
        if changes:
            avg_change = sum(changes) / len(changes)
            if avg_change >= 1.0:
                return "up"
            if avg_change <= -1.0:
                return "down"
        return "flat"

    def _score_funding(self, sources: Dict[str, Dict]) -> float:
        rates = [float(s["funding_rate"]) for s in sources.values() if s.get("funding_rate") is not None]
        if not rates:
            return 0.5
        avg = sum(rates) / len(rates)

        if avg <= -0.0010:
            return 0.85
        if avg <= -0.0005:
            return 0.75
        if avg >= 0.0010:
            return 0.20
        if avg >= 0.0005:
            return 0.30
        return 0.50

    def _score_oi_price(self, sources: Dict[str, Dict], price_trend: str) -> float:
        oi_values = [float(s["open_interest_value"] or s["open_interest"]) for s in sources.values() if s.get("open_interest")]
        if not oi_values or price_trend == "flat":
            return 0.5

        ratio_values = [float(s["long_short_ratio"]) for s in sources.values() if s.get("long_short_ratio")]
        avg_ratio = sum(ratio_values) / len(ratio_values) if ratio_values else None

        if price_trend == "up":
            if avg_ratio and avg_ratio >= 1.5:
                return 0.58  # Trend is up, but longs may be crowded.
            return 0.65
        if price_trend == "down":
            if avg_ratio and avg_ratio <= 0.75:
                return 0.42  # Trend is down, but shorts may be crowded.
            return 0.35
        return 0.5

    def _score_cross_source(self, sources: Dict[str, Dict]) -> float:
        rates = [float(s["funding_rate"]) for s in sources.values() if s.get("funding_rate") is not None]
        if len(rates) < 2:
            return 0.5

        signs = set(1 if r > 0.0002 else -1 if r < -0.0002 else 0 for r in rates)
        if len(signs) == 1:
            return 0.65
        if max(rates) - min(rates) >= 0.001:
            return 0.40
        return 0.55

    def _score_data_quality(self, sources: Dict[str, Dict]) -> float:
        source_score = min(len(sources) / 3, 1.0)
        field_count = 0
        total_fields = 0
        for snapshot in sources.values():
            for field in ("funding_rate", "open_interest", "mark_price", "last_price"):
                total_fields += 1
                if snapshot.get(field) is not None:
                    field_count += 1
        field_score = field_count / total_fields if total_fields else 0
        return self._clamp_score(0.35 + source_score * 0.35 + field_score * 0.30)

    def _calculate_overall_score(self, scores: Dict[str, float]) -> float:
        total = 0.0
        total_weight = 0.0
        for key, weight in self.weights.items():
            total += scores.get(key, 0.5) * weight
            total_weight += weight
        if total_weight == 0:
            return 0.5
        return self._clamp_score(total / total_weight)

    def _calculate_confidence(self, sources: Dict[str, Dict], scores: Dict[str, float]) -> float:
        confidence = 0.45 + min(len(sources), 3) * 0.08
        if scores.get("data_quality", 0) >= 0.7:
            confidence += 0.10
        if abs(scores.get("funding", 0.5) - 0.5) >= 0.20:
            confidence += 0.10
        if scores.get("cross_source", 0.5) < 0.45:
            confidence -= 0.10
        return self._clamp_score(confidence)

    def _funding_summary(self, sources: Dict[str, Dict]) -> Dict:
        rates = {name: snapshot.get("funding_rate") for name, snapshot in sources.items() if snapshot.get("funding_rate") is not None}
        avg = sum(rates.values()) / len(rates) if rates else None
        return {"by_source": rates, "average": avg}

    def _open_interest_summary(self, sources: Dict[str, Dict]) -> Dict:
        values = {
            name: snapshot.get("open_interest_value") or snapshot.get("open_interest")
            for name, snapshot in sources.items()
            if snapshot.get("open_interest") is not None
        }
        avg = sum(values.values()) / len(values) if values else None
        return {"by_source": values, "average": avg}

    def _generate_reasoning(self, sources: Dict[str, Dict], scores: Dict[str, float], price_trend: str, direction: SignalDirection) -> str:
        funding = self._funding_summary(sources)
        avg_funding = funding.get("average")
        parts = [f"{len(sources)} derivatives sources", f"price trend {price_trend}"]
        if avg_funding is not None:
            parts.append(f"avg funding {avg_funding:.4%}")
            if avg_funding < -0.0005:
                parts.append("negative funding supports contrarian bullish setup")
            elif avg_funding > 0.0005:
                parts.append("positive funding warns of crowded longs")
        if scores.get("cross_source", 0.5) < 0.45:
            parts.append("source divergence detected")
        parts.append(f"derivatives signal {direction.value}")
        return "; ".join(parts)

    def _neutral_result(self, symbol: str, reason: str, confidence: float = 0.0) -> AgentResult:
        return AgentResult(
            agent_name=self.name,
            symbol=symbol,
            timestamp=datetime.now(),
            direction=SignalDirection.NEUTRAL,
            sub_score=0.5,
            confidence=confidence,
            analysis={"sources": {}, "scores": {}, "overall": {"sub_score": 0.5, "confidence": confidence}},
            reasoning=reason,
            metadata={"sources": []},
        )

    async def close(self):
        await self.binance.close()
        await self.hyperliquid.close()
        await self.lighter.close()

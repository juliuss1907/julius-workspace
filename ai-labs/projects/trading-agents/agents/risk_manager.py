"""
Risk Manager Agent

Rule-based execution gate that validates final trading signals before they are
sent to OrderManager. Phase 5C adds pyramiding, directional exposure, and
drawdown-aware gates.
"""
from typing import Dict, List, Optional

from agents.base_agent import AgentResult, SignalDirection
from utils import get_logger, config


logger = get_logger(__name__)


class RiskManager:
    """Approve/reject signals and attach basic risk sizing hints."""

    def __init__(self, config_override: Optional[Dict] = None):
        default_config = config.load_default_params()
        self.config = {**default_config, **(config_override or {})}
        risk_config = self.config.get("risk_management", {})
        risk_manager_config = self.config.get("risk_manager", {})
        futures_config = self.config.get("futures", {})
        demo_config = self.config.get("demo_trading", {})

        self.max_open_positions = risk_manager_config.get("max_open_positions", risk_config.get("max_open_positions", 5))
        self.min_confidence = risk_manager_config.get(
            "min_signal_confidence",
            demo_config.get("auto_execute", {}).get("min_confidence", 0.70),
        )
        self.block_duplicate_symbol = risk_manager_config.get("block_duplicate_symbol", True)
        self.total_exposure_warning_pct = risk_manager_config.get(
            "total_exposure_warning_pct",
            risk_config.get("max_total_exposure", 0.80) * 0.875,
        )
        self.max_total_exposure_pct = risk_manager_config.get(
            "max_total_exposure_pct",
            risk_config.get("max_total_exposure", 0.80),
        )
        self.correlated_exposure_warning_pct = risk_manager_config.get(
            "correlated_exposure_warning_pct",
            risk_config.get("max_correlated_exposure", 0.50) * 0.80,
        )
        self.max_correlated_exposure_pct = risk_manager_config.get(
            "max_correlated_exposure_pct",
            risk_config.get("max_correlated_exposure", 0.50),
        )
        self.max_acceptable_funding = risk_manager_config.get(
            "max_acceptable_funding",
            futures_config.get("max_acceptable_funding", 0.001),
        )
        self.funding_warning_threshold = risk_manager_config.get(
            "funding_warning_threshold",
            futures_config.get("funding_warning_threshold", 0.0005),
        )
        self.max_atr_pct = risk_manager_config.get("max_atr_pct", 0.08)
        self.high_atr_pct = risk_manager_config.get("high_atr_pct", 0.05)
        self.technical_conflict_multiplier = risk_manager_config.get("technical_conflict_multiplier", 0.50)
        self.analyst_conflict_step = risk_manager_config.get("analyst_conflict_step", 0.15)
        self.analyst_conflict_floor = risk_manager_config.get("analyst_conflict_floor", 0.50)
        self.funding_warning_multiplier = risk_manager_config.get("funding_warning_multiplier", 0.75)
        self.volatility_warning_multiplier = risk_manager_config.get("volatility_warning_multiplier", 0.75)
        self.portfolio_exposure_warning_multiplier = risk_manager_config.get("portfolio_exposure_warning_multiplier", 0.70)
        self.correlated_exposure_warning_multiplier = risk_manager_config.get("correlated_exposure_warning_multiplier", 0.80)
        self.research_opposite_multiplier = risk_manager_config.get("research_opposite_multiplier", 0.50)
        self.high_risk_multiplier_below = risk_manager_config.get("high_risk_multiplier_below", 0.70)
        self.medium_risk_multiplier_below = risk_manager_config.get("medium_risk_multiplier_below", 0.90)
        self.leverage_caps = risk_manager_config.get(
            "leverage_caps",
            {"low": 5, "medium": 3, "high": 1, "blocked": 1},
        )

        # Phase 5C: Pyramiding
        pyramiding_config = risk_manager_config.get("pyramiding", {})
        self.allow_pyramiding = pyramiding_config.get("allow_pyramiding", False)
        self.max_same_symbol_positions = pyramiding_config.get("max_same_symbol_positions", 1)
        self.same_symbol_exposure_warning_pct = pyramiding_config.get("same_symbol_exposure_warning_pct", 0.20)
        self.max_same_symbol_exposure_pct = pyramiding_config.get("max_same_symbol_exposure_pct", 0.30)
        self.same_symbol_warning_multiplier = pyramiding_config.get("same_symbol_warning_multiplier", 0.50)

        # Phase 5C: Directional exposure
        dir_config = risk_manager_config.get("directional_exposure", {})
        self.directional_exposure_warning_pct = dir_config.get("directional_exposure_warning_pct", 0.60)
        self.max_directional_exposure_pct = dir_config.get("max_directional_exposure_pct", 0.75)
        self.directional_exposure_warning_multiplier = dir_config.get("directional_exposure_warning_multiplier", 0.70)

        # Phase 5C: Drawdown
        dd_config = risk_manager_config.get("drawdown", {})
        self.daily_drawdown_warning_pct = dd_config.get("daily_drawdown_warning_pct", -0.03)
        self.daily_drawdown_block_pct = dd_config.get("daily_drawdown_block_pct", -0.05)
        self.total_drawdown_warning_pct = dd_config.get("total_drawdown_warning_pct", -0.08)
        self.total_drawdown_block_pct = dd_config.get("total_drawdown_block_pct", -0.12)
        self.drawdown_warning_multiplier = dd_config.get("drawdown_warning_multiplier", 0.50)

        self._initialized = False

    async def initialize(self):
        if self._initialized:
            return
        logger.info("RiskManager initialized")
        self._initialized = True

    async def evaluate(
        self,
        symbol: str,
        final_signal: AgentResult,
        analyst_signals: Dict[str, Optional[AgentResult]],
        research_debate: Optional[Dict] = None,
        market_snapshot: Optional[Dict] = None,
        open_positions: Optional[List[Dict]] = None,
        portfolio_stats: Optional[Dict] = None,
        portfolio_context: Optional[Dict] = None,
    ) -> Dict:
        if not self._initialized:
            await self.initialize()

        open_positions = open_positions or []
        market_snapshot = market_snapshot or {}
        research_debate = research_debate or {}
        checks = {}
        reductions = []
        blocked_reasons = []
        multiplier = 1.0
        checks["config"] = {
            "min_signal_confidence": self.min_confidence,
            "max_open_positions": self.max_open_positions,
            "high_atr_pct": self.high_atr_pct,
            "max_atr_pct": self.max_atr_pct,
            "funding_warning_threshold": self.funding_warning_threshold,
            "max_acceptable_funding": self.max_acceptable_funding,
            "total_exposure_warning_pct": self.total_exposure_warning_pct,
            "max_total_exposure_pct": self.max_total_exposure_pct,
            "correlated_exposure_warning_pct": self.correlated_exposure_warning_pct,
            "max_correlated_exposure_pct": self.max_correlated_exposure_pct,
        }

        checks["actionable_direction"] = final_signal.direction != SignalDirection.NEUTRAL
        if not checks["actionable_direction"]:
            blocked_reasons.append("final signal is neutral")

        checks["confidence_threshold"] = final_signal.confidence >= self.min_confidence
        if not checks["confidence_threshold"]:
            blocked_reasons.append(
                f"confidence {final_signal.confidence:.3f} below threshold {self.min_confidence:.3f}"
            )

        checks["max_open_positions"] = len(open_positions) < self.max_open_positions
        if not checks["max_open_positions"]:
            blocked_reasons.append(f"max open positions reached ({self.max_open_positions})")

        # Phase 5C: Pyramiding check replaces simple duplicate-symbol block
        pyramiding_check = self._pyramiding_check(symbol, open_positions, portfolio_context or {})
        checks["pyramiding"] = pyramiding_check
        if pyramiding_check["blocked"]:
            blocked_reasons.append(pyramiding_check["reason"])
        elif pyramiding_check["warning"]:
            multiplier *= pyramiding_check["multiplier"]
            reductions.append(pyramiding_check["reason"])

        technical = analyst_signals.get("technical")
        checks["technical_alignment"] = self._is_aligned_or_neutral(technical, final_signal)
        if not checks["technical_alignment"]:
            multiplier *= self.technical_conflict_multiplier
            reductions.append("technical direction conflicts with final signal")

        conflict_count = self._conflict_count(analyst_signals)
        checks["analyst_conflict_count"] = conflict_count
        if conflict_count > 0:
            multiplier *= max(self.analyst_conflict_floor, 1.0 - conflict_count * self.analyst_conflict_step)
            reductions.append(f"{conflict_count} analyst direction conflict(s)")

        funding_check = self._funding_check(final_signal, analyst_signals)
        checks["funding"] = funding_check
        if funding_check["blocked"]:
            blocked_reasons.append(funding_check["reason"])
        elif funding_check["warning"]:
            multiplier *= self.funding_warning_multiplier
            reductions.append(funding_check["reason"])

        volatility_check = self._volatility_check(final_signal, market_snapshot)
        checks["volatility"] = volatility_check
        if volatility_check["blocked"]:
            blocked_reasons.append(volatility_check["reason"])
        elif volatility_check["warning"]:
            multiplier *= self.volatility_warning_multiplier
            reductions.append(volatility_check["reason"])

        portfolio_check = self._portfolio_check(symbol, portfolio_context or {})
        checks["portfolio"] = portfolio_check
        if portfolio_check["blocked"]:
            blocked_reasons.append(portfolio_check["reason"])
        elif portfolio_check["warning"]:
            multiplier *= portfolio_check["multiplier"]
            reductions.append(portfolio_check["reason"])

        # Phase 5C: Directional exposure check
        directional_check = self._directional_exposure_check(final_signal, portfolio_context or {})
        checks["directional_exposure"] = directional_check
        if directional_check["blocked"]:
            blocked_reasons.append(directional_check["reason"])
        elif directional_check["warning"]:
            multiplier *= directional_check["multiplier"]
            reductions.append(directional_check["reason"])

        # Phase 5C: Drawdown check
        drawdown_check = self._drawdown_check(portfolio_stats or {})
        checks["drawdown"] = drawdown_check
        if drawdown_check["blocked"]:
            blocked_reasons.append(drawdown_check["reason"])
        elif drawdown_check["warning"]:
            multiplier *= drawdown_check["multiplier"]
            reductions.append(drawdown_check["reason"])

        consensus = research_debate.get("consensus")
        checks["research_consensus"] = consensus or "unavailable"
        if consensus == "opposite":
            multiplier *= self.research_opposite_multiplier
            reductions.append("research debate is opposite final signal")

        multiplier = self._clamp(multiplier)
        if multiplier <= 0:
            blocked_reasons.append("position multiplier reduced to zero")

        approved = not blocked_reasons
        risk_level = self._risk_level(approved, multiplier, blocked_reasons, reductions)
        max_leverage = self._max_leverage(final_signal.confidence, risk_level)

        return {
            "approved": approved,
            "risk_level": risk_level,
            "reason": "; ".join(blocked_reasons or reductions or ["risk checks passed"]),
            "position_size_multiplier": multiplier if approved else 0.0,
            "market_type_preference": self._market_type_preference(final_signal, analyst_signals),
            "max_leverage": max_leverage if approved else 1,
            "checks": checks,
            "blocked_reasons": blocked_reasons,
            "reductions": reductions,
            "portfolio_stats": portfolio_stats or {},
            "portfolio_context": portfolio_context or {},
        }

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _signal_side(self, final_signal: AgentResult) -> Optional[str]:
        if final_signal.direction == SignalDirection.BULLISH:
            return "LONG"
        if final_signal.direction == SignalDirection.BEARISH:
            return "SHORT"
        return None

    def _opposite_side(self, side: str) -> str:
        return "SHORT" if side == "LONG" else "LONG"

    # ── Phase 5C: Pyramiding ─────────────────────────────────────────────────

    def _pyramiding_check(self, symbol: str, open_positions: List[Dict], portfolio_context: Dict) -> Dict:
        same_symbol_positions = [p for p in open_positions if p.get("symbol") == symbol]
        same_symbol_count = len(same_symbol_positions)
        symbol_exposure_pct = portfolio_context.get("symbol_exposure_pct", {}).get(symbol, 0.0)

        result = {
            "enabled": self.allow_pyramiding,
            "same_symbol_positions": same_symbol_count,
            "same_symbol_exposure_pct": symbol_exposure_pct,
            "warning": False,
            "blocked": False,
            "reason": "pyramiding acceptable",
            "multiplier": 1.0,
        }

        if same_symbol_count == 0:
            return result

        if not self.allow_pyramiding:
            result.update({
                "blocked": True,
                "reason": f"pyramiding disabled for {symbol}",
            })
            return result

        if same_symbol_count >= self.max_same_symbol_positions:
            result.update({
                "blocked": True,
                "reason": f"max same-symbol positions reached for {symbol} ({self.max_same_symbol_positions})",
            })
            return result

        if symbol_exposure_pct >= self.max_same_symbol_exposure_pct:
            result.update({
                "blocked": True,
                "reason": f"same-symbol exposure too high {symbol_exposure_pct:.1%} (max {self.max_same_symbol_exposure_pct:.1%})",
            })
            return result

        if symbol_exposure_pct >= self.same_symbol_exposure_warning_pct:
            result.update({
                "warning": True,
                "reason": f"same-symbol exposure elevated {symbol_exposure_pct:.1%}",
                "multiplier": self.same_symbol_warning_multiplier,
            })

        return result

    # ── Phase 5C: Directional Exposure ───────────────────────────────────────

    def _directional_exposure_check(self, final_signal: AgentResult, portfolio_context: Dict) -> Dict:
        signal_side = self._signal_side(final_signal)
        result = {
            "available": bool(portfolio_context and signal_side),
            "signal_side": signal_side,
            "same_side_exposure_pct": 0.0,
            "opposite_side_exposure_pct": 0.0,
            "net_directional_exposure_pct": 0.0,
            "warning": False,
            "blocked": False,
            "reason": "directional exposure unavailable",
            "multiplier": 1.0,
        }

        if not result["available"]:
            return result

        side_exposure = portfolio_context.get("side_exposure_pct", {})
        same_side_pct = side_exposure.get(signal_side, 0.0)
        opposite_side_pct = side_exposure.get(self._opposite_side(signal_side), 0.0)
        net_directional = same_side_pct - opposite_side_pct

        result["same_side_exposure_pct"] = same_side_pct
        result["opposite_side_exposure_pct"] = opposite_side_pct
        result["net_directional_exposure_pct"] = net_directional

        if same_side_pct >= self.max_directional_exposure_pct:
            result.update({
                "blocked": True,
                "reason": f"same-side {signal_side} exposure too high ({same_side_pct:.1%})",
            })
            return result

        if same_side_pct >= self.directional_exposure_warning_pct:
            result.update({
                "warning": True,
                "reason": f"same-side {signal_side} exposure elevated ({same_side_pct:.1%})",
                "multiplier": self.directional_exposure_warning_multiplier,
            })
            return result

        result["reason"] = f"directional exposure acceptable ({signal_side} {same_side_pct:.1%})"
        return result

    # ── Phase 5C: Drawdown ───────────────────────────────────────────────────

    def _drawdown_check(self, portfolio_stats: Dict) -> Dict:
        latest = portfolio_stats.get("latest_snapshot") or {}
        daily_pnl = latest.get("daily_pnl")
        total_pnl = latest.get("total_pnl")
        total_equity = latest.get("total_equity")
        total_pnl_pct_raw = latest.get("total_pnl_pct")

        available = bool(daily_pnl is not None and total_equity is not None and total_equity > 0)
        result = {
            "available": available,
            "daily_pnl_pct": None,
            "total_pnl_pct": None,
            "warning": False,
            "blocked": False,
            "reason": "drawdown unavailable",
            "multiplier": 1.0,
        }

        if not available:
            return result

        daily_pnl_pct = daily_pnl / total_equity
        total_drawdown_pct = total_pnl_pct_raw / 100 if total_pnl_pct_raw is not None else (total_pnl / total_equity if total_pnl is not None else None)

        result["daily_pnl_pct"] = daily_pnl_pct
        result["total_pnl_pct"] = total_drawdown_pct

        if daily_pnl_pct <= self.daily_drawdown_block_pct:
            result.update({
                "blocked": True,
                "reason": f"daily drawdown limit reached ({daily_pnl_pct:.1%})",
            })
            return result

        if total_drawdown_pct is not None and total_drawdown_pct <= self.total_drawdown_block_pct:
            result.update({
                "blocked": True,
                "reason": f"total drawdown limit reached ({total_drawdown_pct:.1%})",
            })
            return result

        if daily_pnl_pct <= self.daily_drawdown_warning_pct:
            result.update({
                "warning": True,
                "reason": f"daily drawdown elevated ({daily_pnl_pct:.1%})",
                "multiplier": self.drawdown_warning_multiplier,
            })
            return result

        if total_drawdown_pct is not None and total_drawdown_pct <= self.total_drawdown_warning_pct:
            result.update({
                "warning": True,
                "reason": f"total drawdown elevated ({total_drawdown_pct:.1%})",
                "multiplier": self.drawdown_warning_multiplier,
            })
            return result

        result["reason"] = f"drawdown acceptable (daily {daily_pnl_pct:.1%})"
        return result

    # ── Original checks (unchanged) ──────────────────────────────────────────

    def _is_aligned_or_neutral(self, signal: Optional[AgentResult], final_signal: AgentResult) -> bool:
        if not signal or signal.direction == SignalDirection.NEUTRAL:
            return True
        return signal.direction == final_signal.direction

    def _conflict_count(self, analyst_signals: Dict[str, Optional[AgentResult]]) -> int:
        bullish = sum(1 for signal in analyst_signals.values() if signal and signal.direction == SignalDirection.BULLISH)
        bearish = sum(1 for signal in analyst_signals.values() if signal and signal.direction == SignalDirection.BEARISH)
        return min(bullish, bearish)

    def _funding_check(self, final_signal: AgentResult, analyst_signals: Dict[str, Optional[AgentResult]]) -> Dict:
        derivatives = analyst_signals.get("derivatives")
        funding_avg = None
        if derivatives:
            funding_avg = derivatives.analysis.get("funding", {}).get("average")

        result = {"available": funding_avg is not None, "average": funding_avg, "warning": False, "blocked": False, "reason": "funding unavailable"}
        if funding_avg is None:
            return result

        if final_signal.direction == SignalDirection.BULLISH:
            if funding_avg > self.max_acceptable_funding:
                result.update({"blocked": True, "reason": f"long adverse funding too high ({funding_avg:.4%})"})
            elif funding_avg > self.funding_warning_threshold:
                result.update({"warning": True, "reason": f"long adverse funding elevated ({funding_avg:.4%})"})
            else:
                result["reason"] = "funding acceptable for long"
        elif final_signal.direction == SignalDirection.BEARISH:
            if funding_avg < -self.max_acceptable_funding:
                result.update({"blocked": True, "reason": f"short adverse funding too high ({funding_avg:.4%})"})
            elif funding_avg < -self.funding_warning_threshold:
                result.update({"warning": True, "reason": f"short adverse funding elevated ({funding_avg:.4%})"})
            else:
                result["reason"] = "funding acceptable for short"
        else:
            result["reason"] = "neutral signal"
        return result

    def _volatility_check(self, final_signal: AgentResult, market_snapshot: Dict) -> Dict:
        atr = market_snapshot.get("atr") or final_signal.analysis.get("indicators", {}).get("atr")
        price = market_snapshot.get("last_close") or market_snapshot.get("current_price")
        atr_pct = (float(atr) / float(price)) if atr and price else None
        result = {"available": atr_pct is not None, "atr_pct": atr_pct, "warning": False, "blocked": False, "reason": "ATR unavailable"}
        if atr_pct is None:
            return result
        if atr_pct >= self.max_atr_pct:
            result.update({"blocked": True, "reason": f"ATR volatility too high ({atr_pct:.2%})"})
        elif atr_pct >= self.high_atr_pct:
            result.update({"warning": True, "reason": f"ATR volatility elevated ({atr_pct:.2%})"})
        else:
            result["reason"] = "volatility acceptable"
        return result

    def _portfolio_check(self, symbol: str, portfolio_context: Dict) -> Dict:
        if not portfolio_context:
            return {"available": False, "warning": False, "blocked": False, "reason": "portfolio context unavailable", "multiplier": 1.0}

        total_exposure_pct = portfolio_context.get("total_exposure_pct", 0.0)
        symbol_exposure_pct = portfolio_context.get("symbol_exposure_pct", {}).get(symbol, 0.0)
        correlated_pct = portfolio_context.get("correlated_exposure_pct", {})
        max_correlated_group = None
        max_correlated_pct = 0.0
        if correlated_pct:
            max_correlated_group, max_correlated_pct = max(correlated_pct.items(), key=lambda item: item[1])

        result = {
            "available": True,
            "total_exposure_pct": total_exposure_pct,
            "symbol_exposure_pct": symbol_exposure_pct,
            "max_correlated_group": max_correlated_group,
            "max_correlated_exposure_pct": max_correlated_pct,
            "warning": False,
            "blocked": False,
            "reason": "portfolio exposure acceptable",
            "multiplier": 1.0,
        }

        if total_exposure_pct >= self.max_total_exposure_pct:
            result.update({"blocked": True, "reason": f"total exposure too high ({total_exposure_pct:.1%})"})
        elif max_correlated_pct >= self.max_correlated_exposure_pct:
            result.update({"blocked": True, "reason": f"correlated exposure too high ({max_correlated_group}: {max_correlated_pct:.1%})"})
        elif total_exposure_pct >= self.total_exposure_warning_pct:
            result.update({
                "warning": True,
                "reason": f"total exposure elevated ({total_exposure_pct:.1%})",
                "multiplier": self.portfolio_exposure_warning_multiplier,
            })
        elif max_correlated_pct >= self.correlated_exposure_warning_pct:
            result.update({
                "warning": True,
                "reason": f"correlated exposure elevated ({max_correlated_group}: {max_correlated_pct:.1%})",
                "multiplier": self.correlated_exposure_warning_multiplier,
            })
        return result

    def _market_type_preference(self, final_signal: AgentResult, analyst_signals: Dict[str, Optional[AgentResult]]) -> str:
        derivatives = analyst_signals.get("derivatives")
        if final_signal.direction == SignalDirection.BEARISH:
            return "futures"
        if derivatives and derivatives.confidence >= 0.75 and final_signal.confidence >= 0.75:
            return "futures"
        return "auto"

    def _max_leverage(self, confidence: float, risk_level: str) -> int:
        cap = self.leverage_caps.get(risk_level, 1)
        if risk_level == "low" and confidence < 0.8:
            return min(cap, 3)
        if risk_level == "medium" and confidence < 0.7:
            return min(cap, 1)
        return cap

    def _risk_level(self, approved: bool, multiplier: float, blocked_reasons: List[str], reductions: List[str]) -> str:
        if not approved or blocked_reasons:
            return "blocked"
        if multiplier < self.high_risk_multiplier_below or len(reductions) >= 2:
            return "high"
        if multiplier < self.medium_risk_multiplier_below or reductions:
            return "medium"
        return "low"

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, value))

    async def close(self):
        pass

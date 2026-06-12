"""
Position Manager Agent

Rule-based manager for existing open positions. It decides whether to hold,
recommend reducing, close, or recommend reversing a position.
"""
from typing import Dict, List, Optional

from agents.base_agent import AgentResult, SignalDirection
from utils import config, get_logger


logger = get_logger(__name__)


class PositionManager:
    """Evaluate open positions against the latest final trading signal."""

    def __init__(self, config_override: Optional[Dict] = None):
        default_config = config.load_default_params()
        self.config = {**default_config, **(config_override or {})}
        pm_config = self.config.get("position_manager", {})

        self.min_confidence_to_reduce = pm_config.get("min_confidence_to_reduce", 0.60)
        self.min_confidence_to_close = pm_config.get("min_confidence_to_close", 0.70)
        self.min_confidence_to_reverse = pm_config.get("min_confidence_to_reverse", 0.80)
        self.reduce_fraction = pm_config.get("reduce_fraction", 0.50)
        self.close_on_opposite_technical = pm_config.get("close_on_opposite_technical", True)
        self.close_on_research_opposite = pm_config.get("close_on_research_opposite", True)
        self.reverse_enabled = pm_config.get("reverse_enabled", False)

        profit_config = pm_config.get("profit_protection", {})
        self.profit_protection_enabled = profit_config.get("enabled", True)
        self.reduce_when_profit_pct_above = profit_config.get("reduce_when_profit_pct_above", 0.05)
        self.reduce_on_weak_signal_confidence_below = profit_config.get("reduce_on_weak_signal_confidence_below", 0.60)

        loss_config = pm_config.get("loss_control", {})
        self.loss_control_enabled = loss_config.get("enabled", True)
        self.close_when_loss_pct_below = loss_config.get("close_when_loss_pct_below", -0.04)
        self.close_if_opposite_signal = loss_config.get("close_if_opposite_signal", True)
        self._initialized = False

    async def initialize(self):
        if self._initialized:
            return
        logger.info("PositionManager initialized")
        self._initialized = True

    async def evaluate(
        self,
        symbol: str,
        final_signal: AgentResult,
        analyst_signals: Dict[str, Optional[AgentResult]],
        research_debate: Optional[Dict] = None,
        risk_decision: Optional[Dict] = None,
        portfolio_context: Optional[Dict] = None,
        open_positions: Optional[List[Dict]] = None,
        market_snapshot: Optional[Dict] = None,
    ) -> Dict:
        if not self._initialized:
            await self.initialize()

        open_positions = open_positions or []
        position = next((pos for pos in open_positions if pos.get("symbol") == symbol), None)
        if not position:
            return self._decision("no_position", "no open position for symbol", final_signal, None)

        research_debate = research_debate or {}
        risk_decision = risk_decision or {}
        checks = {
            "position_side": position.get("side"),
            "final_direction": final_signal.direction.value,
            "final_confidence": final_signal.confidence,
            "technical_direction": self._direction(analyst_signals.get("technical")),
            "research_consensus": research_debate.get("consensus"),
            "risk_approved": risk_decision.get("approved"),
            "pnl_pct": self._pnl_pct(position, market_snapshot or {}),
        }

        if self._aligned_or_neutral(position, final_signal):
            profit_action = self._profit_protection(position, final_signal, checks)
            if profit_action:
                return profit_action
            return self._decision("hold_position", "position aligned with final signal", final_signal, position, checks=checks)

        if self._should_close_losing_opposite(final_signal, checks):
            return self._decision("close_position", "losing position has opposite signal", final_signal, position, close_fraction=1.0, close_reason="loss_control", checks=checks)

        if final_signal.confidence < self.min_confidence_to_reduce:
            return self._decision("hold_position", "opposite signal confidence too low", final_signal, position, checks=checks)

        if final_signal.confidence < self.min_confidence_to_close:
            return self._decision(
                "reduce_position",
                "opposite signal reached reduce threshold",
                final_signal,
                position,
                close_fraction=self.reduce_fraction,
                close_reason="risk_reduction",
                checks=checks,
            )

        close_confirmed = self._close_confirmed(final_signal, analyst_signals, research_debate)
        if final_signal.confidence >= self.min_confidence_to_reverse and close_confirmed:
            if self.reverse_enabled:
                return self._decision(
                    "reverse_position",
                    "high-confidence opposite signal pending guarded reverse risk check",
                    final_signal,
                    position,
                    close_fraction=1.0,
                    reverse_allowed=True,
                    close_reason="signal_reversal",
                    checks=checks,
                )
            return self._decision(
                "close_position",
                "reverse signal detected but reverse is disabled",
                final_signal,
                position,
                close_fraction=1.0,
                close_reason="signal_reversal",
                checks=checks,
            )

        if close_confirmed:
            return self._decision(
                "close_position",
                "opposite signal confirmed by position checks",
                final_signal,
                position,
                close_fraction=1.0,
                close_reason="signal_reversal",
                checks=checks,
            )

        return self._decision(
            "reduce_position",
            "opposite signal without full close confirmation",
            final_signal,
            position,
            close_fraction=self.reduce_fraction,
            close_reason="risk_reduction",
            checks=checks,
        )

    def _profit_protection(self, position: Dict, final_signal: AgentResult, checks: Dict) -> Optional[Dict]:
        if not self.profit_protection_enabled:
            return None
        pnl_pct = checks.get("pnl_pct")
        if pnl_pct is None:
            return None
        if pnl_pct >= self.reduce_when_profit_pct_above and final_signal.confidence < self.reduce_on_weak_signal_confidence_below:
            return self._decision(
                "reduce_position",
                "profitable position with weakening signal",
                final_signal,
                position,
                close_fraction=self.reduce_fraction,
                close_reason="profit_protection",
                checks=checks,
            )
        return None

    def _should_close_losing_opposite(self, final_signal: AgentResult, checks: Dict) -> bool:
        if not self.loss_control_enabled or not self.close_if_opposite_signal:
            return False
        pnl_pct = checks.get("pnl_pct")
        return pnl_pct is not None and pnl_pct <= self.close_when_loss_pct_below and final_signal.confidence >= self.min_confidence_to_reduce

    def _close_confirmed(self, final_signal: AgentResult, analyst_signals: Dict[str, Optional[AgentResult]], research_debate: Dict) -> bool:
        technical = analyst_signals.get("technical")
        technical_confirms = bool(
            self.close_on_opposite_technical
            and technical
            and technical.direction == final_signal.direction
        )
        research_confirms = bool(self.close_on_research_opposite and research_debate.get("consensus") == "aligned")
        return final_signal.confidence >= self.min_confidence_to_close and (technical_confirms or research_confirms)

    def _aligned_or_neutral(self, position: Dict, final_signal: AgentResult) -> bool:
        if final_signal.direction == SignalDirection.NEUTRAL:
            return True
        side = position.get("side")
        return (side == "LONG" and final_signal.direction == SignalDirection.BULLISH) or (
            side == "SHORT" and final_signal.direction == SignalDirection.BEARISH
        )

    def _pnl_pct(self, position: Dict, market_snapshot: Dict) -> Optional[float]:
        if position.get("pnl_pct") is not None:
            return self._float(position.get("pnl_pct")) / 100.0
        entry = self._float(position.get("entry_price"))
        price = self._float(market_snapshot.get("last_close") or market_snapshot.get("current_price"))
        if entry <= 0 or price <= 0:
            return None
        raw = (price - entry) / entry
        return raw if position.get("side") == "LONG" else -raw

    def _decision(
        self,
        action: str,
        reason: str,
        final_signal: AgentResult,
        position: Optional[Dict],
        close_fraction: float = 0.0,
        reverse_allowed: bool = False,
        close_reason: str = "manual",
        checks: Optional[Dict] = None,
    ) -> Dict:
        return {
            "action": action,
            "reason": reason,
            "confidence": final_signal.confidence,
            "position": position or {},
            "close_fraction": close_fraction,
            "reverse_allowed": reverse_allowed,
            "close_reason": close_reason,
            "checks": checks or {},
        }

    def _direction(self, signal: Optional[AgentResult]) -> str:
        return signal.direction.value if signal else "unavailable"

    def _float(self, value) -> float:
        try:
            return float(value or 0.0)
        except (TypeError, ValueError):
            return 0.0

    async def close(self):
        pass

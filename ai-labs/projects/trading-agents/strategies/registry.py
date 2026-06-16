"""
Strategy registry — pure playbook selection.

Evaluates Phase 1 strategies in regime-dependent order and returns the
single best StrategySignal for a given TechnicalState + MarketState snapshot.
"""
from typing import Dict, List, Optional

from strategies.base import StrategyPolicy
from strategies.breakout import BreakoutStrategy
from strategies.contracts import MarketState, StrategySignal, TechnicalState
from strategies.trend_following import TrendFollowingStrategy
from strategies.volatility_skip import VolatilitySkipStrategy


DEFAULT_REGIME_STRATEGY_ORDER = {
    "trend_up": ["volatility_skip", "trend_following", "breakout"],
    "trend_down": ["volatility_skip", "trend_following", "breakout"],
    "ranging": ["volatility_skip", "breakout"],
    "volatile": ["volatility_skip"],
}

DEFAULT_MIN_ACTION_CONFIDENCE = 0.55


class StrategyRegistry:
    """Registry of Phase 1 pure strategy policies."""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self._strategies: Dict[str, StrategyPolicy] = {
            "volatility_skip": VolatilitySkipStrategy(),
            "trend_following": TrendFollowingStrategy(),
            "breakout": BreakoutStrategy(),
        }
        self._order = self.config.get(
            "regime_strategy_order",
            DEFAULT_REGIME_STRATEGY_ORDER,
        )
        selection_config = self.config.get("selection", {})
        self._min_action_confidence = selection_config.get(
            "min_action_confidence",
            self.config.get("min_action_confidence", DEFAULT_MIN_ACTION_CONFIDENCE),
        )
        self._prefer_action = selection_config.get(
            "prefer_action_over_hold",
            self.config.get("prefer_action_over_hold", True),
        )

    def select(
        self,
        technical_state: TechnicalState,
        market_state: MarketState,
        context: Optional[Dict] = None,
    ) -> StrategySignal:
        """Evaluate strategies in regime order and return the best signal."""
        regime = market_state.regime
        order = self._order.get(regime, ["volatility_skip"])

        evaluated: List[StrategySignal] = []
        for key in order:
            strategy = self._strategies.get(key)
            if strategy is None:
                continue
            signal = strategy.evaluate(technical_state, market_state, context)
            evaluated.append(signal)

            # Volatility skip is a hard no-trade guard.
            if key == "volatility_skip" and signal.action == "skip":
                return self._tag_signal(signal, evaluated)

            # First actionable long/short that passes confidence floor.
            if signal.action in ("long", "short") and signal.confidence >= self._min_action_confidence:
                return self._tag_signal(signal, evaluated)

        # No actionable signal — choose the best fallback.
        return self._tag_signal(self._best_fallback(evaluated), evaluated)

    def _best_fallback(self, evaluated: List[StrategySignal]) -> StrategySignal:
        """Return hold/skip fallback when no strategy passes action threshold."""
        if not evaluated:
            return StrategySignal(
                strategy_id="registry",
                family="registry",
                action="skip",
                confidence=0.0,
                setup="no strategies evaluated",
                trigger="empty strategy order or unknown regime",
                invalidation="n/a",
                sizing_hint="no position",
                exit_plan="n/a",
                no_trade_reason="No strategy evaluated for this state",
                risk_notes=["Registry produced no actionable signal."],
                attribution={"evaluated": []},
            )

        # Prefer hold over weak action; prefer skip with clearest reason otherwise.
        holds = [s for s in evaluated if s.action == "hold"]
        skips = [s for s in evaluated if s.action == "skip"]

        if holds:
            best = max(holds, key=lambda s: s.confidence)
        elif skips:
            best = max(skips, key=lambda s: s.confidence)
        else:
            best = evaluated[0]

        # If somehow a weak action made it here, downgrade to hold.
        if best.action in ("long", "short"):
            best = StrategySignal(
                strategy_id=best.strategy_id,
                family=best.family,
                action="hold",
                confidence=best.confidence,
                setup=best.setup,
                trigger=best.trigger,
                invalidation=best.invalidation,
                sizing_hint="no position",
                exit_plan=best.exit_plan,
                no_trade_reason=f"Action confidence {best.confidence:.2f} below floor {self._min_action_confidence:.2f}",
                risk_notes=best.risk_notes + ["Downgraded to hold by registry."],
                attribution=best.attribution,
            )

        return best

    def _tag_signal(
        self,
        signal: StrategySignal,
        evaluated: List[StrategySignal],
    ) -> StrategySignal:
        """Attach registry-level attribution without mutating the original signal."""
        enriched = StrategySignal(
            strategy_id=signal.strategy_id,
            family=signal.family,
            action=signal.action,
            confidence=signal.confidence,
            setup=signal.setup,
            trigger=signal.trigger,
            invalidation=signal.invalidation,
            sizing_hint=signal.sizing_hint,
            exit_plan=signal.exit_plan,
            no_trade_reason=signal.no_trade_reason,
            risk_notes=list(signal.risk_notes),
            attribution={
                **signal.attribution,
                "registry": True,
                "evaluated": [
                    {"strategy_id": s.strategy_id, "action": s.action, "confidence": s.confidence}
                    for s in evaluated
                ],
            },
        )
        return enriched

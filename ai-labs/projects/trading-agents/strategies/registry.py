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
            "volatility_skip": VolatilitySkipStrategy(self.config.get("volatility_skip", {})),
            "trend_following": TrendFollowingStrategy(self.config.get("trend_following", {})),
            "breakout": BreakoutStrategy(self.config.get("breakout", {})),
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
                return self._tag_signal(
                    signal,
                    evaluated,
                    selection_reason="volatility_skip_direct_guard",
                )

            # First actionable long/short that passes confidence floor.
            if signal.action in ("long", "short") and signal.confidence >= self._min_action_confidence:
                return self._tag_signal(
                    signal,
                    evaluated,
                    selection_reason="action_confidence_above_floor",
                )

        # No actionable signal — choose the best fallback.
        return self._tag_signal(
            self._best_fallback(evaluated),
            evaluated,
            selection_reason="fallback_no_action_above_floor",
        )

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
        *,
        selection_reason: str,
    ) -> StrategySignal:
        """Attach registry-level attribution without mutating the original signal."""
        selected_index = self._selected_candidate_index(signal, evaluated)
        prefer_action_applied = bool(
            self._prefer_action
            and signal.action in ("long", "short")
            and any(candidate.action == "hold" for candidate in evaluated[: selected_index or 0])
        )
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
                "candidate_schema_version": "batch3w-v1",
                "selection_reason": selection_reason,
                "selected_candidate_index": selected_index,
                "prefer_action_over_hold_applied": prefer_action_applied,
                "min_action_confidence": self._min_action_confidence,
                "evaluated": self._candidate_attribution(
                    evaluated,
                    selected_index=selected_index,
                    selected_signal=signal,
                    selection_reason=selection_reason,
                ),
            },
        )
        return enriched

    def _selected_candidate_index(
        self,
        signal: StrategySignal,
        evaluated: List[StrategySignal],
    ) -> Optional[int]:
        """Return the evaluated index that matches the selected signal, if any."""
        for index, candidate in enumerate(evaluated):
            if (
                candidate.strategy_id == signal.strategy_id
                and candidate.family == signal.family
                and candidate.action == signal.action
                and candidate.confidence == signal.confidence
            ):
                return index
        return None

    def _candidate_attribution(
        self,
        evaluated: List[StrategySignal],
        *,
        selected_index: Optional[int],
        selected_signal: StrategySignal,
        selection_reason: str,
    ) -> List[Dict]:
        """Build additive candidate-level attribution for each evaluated strategy."""
        candidates: List[Dict] = []
        for index, candidate in enumerate(evaluated):
            selected = selected_index == index
            candidate_reason = selection_reason if selected else self._rejection_reason(
                candidate,
                selected_signal,
            )
            candidates.append({
                "strategy_id": candidate.strategy_id,
                "family": candidate.family,
                "action": candidate.action,
                "confidence": candidate.confidence,
                "selected": selected,
                "eligible": self._candidate_eligible(candidate),
                "selection_reason": candidate_reason if selected else None,
                "rejection_reason": None if selected else candidate_reason,
                "thresholds": self._candidate_thresholds(candidate),
                "observed": self._candidate_observed(candidate),
            })
        return candidates

    def _candidate_eligible(self, candidate: StrategySignal) -> bool:
        """Return whether a candidate was eligible under registry action rules."""
        if candidate.action in ("long", "short"):
            return candidate.confidence >= self._min_action_confidence
        return candidate.action in ("hold", "skip")

    def _rejection_reason(
        self,
        candidate: StrategySignal,
        selected_signal: StrategySignal,
    ) -> str:
        """Explain why an evaluated candidate was not selected."""
        if candidate.action in ("long", "short") and candidate.confidence < self._min_action_confidence:
            return "action_confidence_below_floor"
        if selected_signal.action in ("long", "short") and candidate.action == "hold" and self._prefer_action:
            return "hold_candidate_overridden_by_action_candidate"
        if selected_signal.action == "skip":
            return "blocked_by_skip_candidate"
        return "candidate_not_selected"

    def _candidate_thresholds(self, candidate: StrategySignal) -> Dict:
        """Expose strategy thresholds already present in candidate attribution."""
        attribution = candidate.attribution or {}
        thresholds = attribution.get("thresholds")
        if isinstance(thresholds, dict):
            return dict(thresholds)
        copied = {}
        for key in (
            "high_atr_pct",
            "volatile_confidence_floor",
            "skip_volatile_regime",
            "min_regime_confidence",
            "rsi_long_cap",
            "rsi_short_floor",
            "allow_volatile",
        ):
            if key in attribution:
                copied[key] = attribution[key]
        return copied

    def _candidate_observed(self, candidate: StrategySignal) -> Dict:
        """Expose observed diagnostics already present in candidate attribution."""
        attribution = candidate.attribution or {}
        observed = attribution.get("observed")
        if isinstance(observed, dict):
            return dict(observed)
        copied = {}
        for key in (
            "atr_pct",
            "atr",
            "close",
            "regime",
            "original_regime",
            "trend_direction",
            "ema_20",
            "ema_50",
            "macd_histogram",
            "rsi",
            "recent_high_20",
            "recent_low_20",
            "breakout_up_20",
            "breakout_down_20",
        ):
            if key in attribution:
                copied[key] = attribution[key]
        return copied

"""
Volatility skip strategy — safety/no-trade guard.

Returns a skip signal when the market is too volatile to express an edge
safely. Otherwise returns hold, letting later strategies in the pipeline
evaluate the same state snapshot.
"""
from typing import Optional

from strategies.base import StrategyPolicy
from strategies.contracts import MarketState, StrategySignal, TechnicalState


class VolatilitySkipStrategy(StrategyPolicy):
    """Skip trades when volatility is excessive."""

    strategy_id = "volatility-skip"
    family = "volatility_skip"

    # Relative ATR threshold above which the market is considered too volatile.
    HIGH_ATR_PCT = 0.08

    def __init__(self, config: Optional[dict] = None):
        """Create a volatility guard with optional replay-only calibration knobs.

        Defaults preserve production behavior. Batch 3H calibration passes
        explicit in-memory config through replay artifacts only; no runtime
        config files or execution behavior are changed here.
        """
        self.config = config or {}
        self.high_atr_pct = float(self.config.get("high_atr_pct", self.HIGH_ATR_PCT))
        self.skip_volatile_regime = bool(self.config.get("skip_volatile_regime", True))
        self.volatile_confidence_floor = float(self.config.get("volatile_confidence_floor", 0.0))

    def evaluate(
        self,
        technical_state: TechnicalState,
        market_state: MarketState,
        context: Optional[dict] = None,
    ) -> StrategySignal:
        """Return skip if volatility is excessive; otherwise hold."""
        close = technical_state.close
        atr = technical_state.atr
        regime = market_state.regime

        atr_pct = (atr / close) if close and close > 0 and atr is not None else 0.0

        if (
            regime == "volatile"
            and self.skip_volatile_regime
            and market_state.confidence >= self.volatile_confidence_floor
        ):
            return StrategySignal(
                strategy_id=self.strategy_id,
                family=self.family,
                action="skip",
                confidence=round(market_state.confidence, 4),
                setup="regime-classified volatile market",
                trigger=(
                    f"regime=volatile (ADX={market_state.adx:.1f}, "
                    f"confidence={market_state.confidence:.2f} >= "
                    f"{self.volatile_confidence_floor:.2f})"
                ),
                invalidation=f"regime exits volatile AND ATR/close < {self.high_atr_pct:.0%}",
                sizing_hint="no position",
                exit_plan="n/a",
                no_trade_reason="Volatile regime — avoid new directional exposure",
                risk_notes=[
                    "Wide price swings increase stop-run and whipsaw risk.",
                    "Wait for volatility compression or directional confirmation.",
                ],
                attribution={
                    "regime": regime,
                    "adx": market_state.adx,
                    "volatile_confidence_floor": self.volatile_confidence_floor,
                    "high_atr_pct": self.high_atr_pct,
                    "skip_volatile_regime": self.skip_volatile_regime,
                    "thresholds": {
                        "high_atr_pct": self.high_atr_pct,
                        "volatile_confidence_floor": self.volatile_confidence_floor,
                        "skip_volatile_regime": self.skip_volatile_regime,
                    },
                    "observed": {
                        "atr_pct": atr_pct,
                        "atr": atr,
                        "close": close,
                        "regime": regime,
                        "regime_confidence": market_state.confidence,
                        "adx": market_state.adx,
                    },
                    "replay_only_calibration": bool(self.config.get("calibration", {}).get("replay_only")),
                },
            )

        if atr_pct >= self.high_atr_pct:
            return StrategySignal(
                strategy_id=self.strategy_id,
                family=self.family,
                action="skip",
                confidence=round(min(atr_pct, 1.0), 4),
                setup="extreme realized volatility",
                trigger=f"ATR/close = {atr_pct:.2%} >= {self.high_atr_pct:.0%}",
                invalidation=f"ATR/close drops below {self.high_atr_pct:.0%}",
                sizing_hint="no position",
                exit_plan="n/a",
                no_trade_reason="High ATR relative to price — volatility skip active",
                risk_notes=[
                    f"atr_pct={atr_pct:.2%} exceeds {self.high_atr_pct:.0%} threshold.",
                    "Reduced edge and wider stops make directional trades unfavorable.",
                ],
                attribution={
                    "atr_pct": atr_pct,
                    "atr": atr,
                    "close": close,
                    "high_atr_pct": self.high_atr_pct,
                    "volatile_confidence_floor": self.volatile_confidence_floor,
                    "thresholds": {
                        "high_atr_pct": self.high_atr_pct,
                        "volatile_confidence_floor": self.volatile_confidence_floor,
                        "skip_volatile_regime": self.skip_volatile_regime,
                    },
                    "observed": {
                        "atr_pct": atr_pct,
                        "atr": atr,
                        "close": close,
                        "regime": regime,
                        "regime_confidence": market_state.confidence,
                    },
                },
            )

        return StrategySignal(
            strategy_id=self.strategy_id,
            family=self.family,
            action="hold",
            confidence=0.5,
            setup="volatility guard check",
            trigger="volatility guard inactive under replay/default thresholds",
            invalidation=f"regime becomes volatile or ATR/close >= {self.high_atr_pct:.0%}",
            sizing_hint="allow downstream strategies to evaluate",
            exit_plan="n/a",
            no_trade_reason=None,
            risk_notes=["Volatility skip not active — normal evaluation continues."],
            attribution={
                "atr_pct": atr_pct,
                "regime": regime,
                "high_atr_pct": self.high_atr_pct,
                "volatile_confidence_floor": self.volatile_confidence_floor,
                "thresholds": {
                    "high_atr_pct": self.high_atr_pct,
                    "volatile_confidence_floor": self.volatile_confidence_floor,
                    "skip_volatile_regime": self.skip_volatile_regime,
                },
                "observed": {
                    "atr_pct": atr_pct,
                    "atr": atr,
                    "close": close,
                    "regime": regime,
                    "regime_confidence": market_state.confidence,
                },
            },
        )

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

        if regime == "volatile":
            return StrategySignal(
                strategy_id=self.strategy_id,
                family=self.family,
                action="skip",
                confidence=round(market_state.confidence, 4),
                setup="regime-classified volatile market",
                trigger=f"regime=volatile (ADX={market_state.adx:.1f})",
                invalidation="regime exits volatile AND ATR/close < 8%",
                sizing_hint="no position",
                exit_plan="n/a",
                no_trade_reason="Volatile regime — avoid new directional exposure",
                risk_notes=[
                    "Wide price swings increase stop-run and whipsaw risk.",
                    "Wait for volatility compression or directional confirmation.",
                ],
                attribution={"regime": regime, "adx": market_state.adx},
            )

        if atr_pct >= self.HIGH_ATR_PCT:
            return StrategySignal(
                strategy_id=self.strategy_id,
                family=self.family,
                action="skip",
                confidence=round(min(atr_pct, 1.0), 4),
                setup="extreme realized volatility",
                trigger=f"ATR/close = {atr_pct:.2%} >= {self.HIGH_ATR_PCT:.0%}",
                invalidation="ATR/close drops below 8%",
                sizing_hint="no position",
                exit_plan="n/a",
                no_trade_reason="High ATR relative to price — volatility skip active",
                risk_notes=[
                    f"atr_pct={atr_pct:.2%} exceeds {self.HIGH_ATR_PCT:.0%} threshold.",
                    "Reduced edge and wider stops make directional trades unfavorable.",
                ],
                attribution={"atr_pct": atr_pct, "atr": atr, "close": close},
            )

        return StrategySignal(
            strategy_id=self.strategy_id,
            family=self.family,
            action="hold",
            confidence=0.5,
            setup="volatility guard check",
            trigger="regime not volatile and ATR/close below threshold",
            invalidation="regime becomes volatile or ATR/close >= 8%",
            sizing_hint="allow downstream strategies to evaluate",
            exit_plan="n/a",
            no_trade_reason=None,
            risk_notes=["Volatility skip not active — normal evaluation continues."],
            attribution={"atr_pct": atr_pct, "regime": regime},
        )

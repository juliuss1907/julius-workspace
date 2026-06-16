"""
Breakout strategy — early-trend / range-expansion trigger.

Acts when price closes beyond the previous 20-candle Donchian range
and momentum (MACD) confirms. Accepts breakouts from ranging markets
as well as trend-continuation breakouts.
"""
from typing import Optional

from strategies.base import StrategyPolicy
from strategies.contracts import MarketState, StrategySignal, TechnicalState


class BreakoutStrategy(StrategyPolicy):
    """Trade 20-candle Donchian breakouts with momentum confirmation."""

    strategy_id = "breakout"
    family = "breakout"

    def evaluate(
        self,
        technical_state: TechnicalState,
        market_state: MarketState,
        context: Optional[dict] = None,
    ) -> StrategySignal:
        """Return long/short on confirmed Donchian breakout; otherwise hold/skip."""
        close = technical_state.close
        recent_high = technical_state.recent_high_20
        recent_low = technical_state.recent_low_20
        breakout_up = technical_state.breakout_up_20
        breakout_down = technical_state.breakout_down_20
        macd_hist = technical_state.macd_histogram
        macd_cross_up = technical_state.macd_crossing_up
        macd_cross_down = technical_state.macd_crossing_down
        regime = market_state.regime

        if regime == "volatile":
            return self._skip(
                technical_state,
                market_state,
                "Volatile regime — breakouts are more likely false",
            )

        if close is None or recent_high is None or recent_low is None:
            return self._skip(
                technical_state,
                market_state,
                "Missing Donchian or close data for breakout evaluation",
                data_quality=True,
            )

        # Long breakout
        if breakout_up:
            if macd_cross_up or (macd_hist is not None and macd_hist > 0):
                return StrategySignal(
                    strategy_id=self.strategy_id,
                    family=self.family,
                    action="long",
                    confidence=round(self._breakout_confidence(market_state, technical_state), 4),
                    setup="20-candle upside breakout",
                    trigger=f"close={close:.4f} > recent_high_20={recent_high:.4f} with MACD confirmation",
                    invalidation="close back below breakout level / prior range / opposite MACD cross",
                    sizing_hint="reduced risk until follow-through confirms",
                    exit_plan="trail if trend develops; exit failed breakout back inside prior range",
                    risk_notes=[
                        "Crypto breakouts often fake — wait for momentum confirmation.",
                        "Wick-only breakouts do not count; trigger uses closing price.",
                    ],
                    attribution={
                        "recent_high_20": recent_high,
                        "recent_low_20": recent_low,
                        "breakout_up_20": breakout_up,
                        "macd_histogram": macd_hist,
                        "macd_crossing_up": macd_cross_up,
                        "regime": regime,
                    },
                )
            return self._hold(
                technical_state,
                market_state,
                "Upside breakout lacks MACD confirmation",
            )

        # Short breakout
        if breakout_down:
            if macd_cross_down or (macd_hist is not None and macd_hist < 0):
                return StrategySignal(
                    strategy_id=self.strategy_id,
                    family=self.family,
                    action="short",
                    confidence=round(self._breakout_confidence(market_state, technical_state), 4),
                    setup="20-candle downside breakout",
                    trigger=f"close={close:.4f} < recent_low_20={recent_low:.4f} with MACD confirmation",
                    invalidation="close back above breakout level / prior range / opposite MACD cross",
                    sizing_hint="reduced risk until follow-through confirms",
                    exit_plan="trail if trend develops; exit failed breakout back inside prior range",
                    risk_notes=[
                        "Crypto breakouts often fake — wait for momentum confirmation.",
                        "Wick-only breakouts do not count; trigger uses closing price.",
                    ],
                    attribution={
                        "recent_high_20": recent_high,
                        "recent_low_20": recent_low,
                        "breakout_down_20": breakout_down,
                        "macd_histogram": macd_hist,
                        "macd_crossing_down": macd_cross_down,
                        "regime": regime,
                    },
                )
            return self._hold(
                technical_state,
                market_state,
                "Downside breakout lacks MACD confirmation",
            )

        return self._hold(
            technical_state,
            market_state,
            "No 20-candle Donchian breakout detected",
        )

    def _breakout_confidence(self, market_state: MarketState, technical_state: TechnicalState) -> float:
        """Confidence bounded 0.55-0.90 based on regime clarity and momentum."""
        base = max(0.55, float(market_state.confidence))

        macd_hist = technical_state.macd_histogram
        if macd_hist is not None:
            # Small boost for stronger histogram
            base += min(0.10, abs(macd_hist) / max(1.0, technical_state.close or 1.0))

        if market_state.regime in ("trend_up", "trend_down"):
            base += 0.05  # continuation breakouts slightly preferred

        return min(0.90, base)

    def _hold(
        self,
        technical_state: TechnicalState,
        market_state: MarketState,
        reason: str,
    ) -> StrategySignal:
        return StrategySignal(
            strategy_id=self.strategy_id,
            family=self.family,
            action="hold",
            confidence=0.5,
            setup="breakout guard check",
            trigger="no confirmed Donchian breakout",
            invalidation="n/a",
            sizing_hint="no position",
            exit_plan="n/a",
            no_trade_reason=reason,
            risk_notes=["Breakout conditions not met."],
            attribution={"regime": market_state.regime},
        )

    def _skip(
        self,
        technical_state: TechnicalState,
        market_state: MarketState,
        reason: str,
        data_quality: bool = False,
    ) -> StrategySignal:
        return StrategySignal(
            strategy_id=self.strategy_id,
            family=self.family,
            action="skip",
            confidence=round(market_state.confidence, 4),
            setup="breakout no-trade guard",
            trigger="state incompatible with breakout edge",
            invalidation="state becomes compatible",
            sizing_hint="no position",
            exit_plan="n/a",
            no_trade_reason=reason,
            risk_notes=[
                "Data quality issue — cannot evaluate breakout." if data_quality else "Conditions unfavorable for breakout entry.",
            ],
            attribution={"regime": market_state.regime},
        )

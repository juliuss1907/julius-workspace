"""
Trend-following strategy — primary Phase 1 momentum playbook.

Expresses the edge that crypto rewards confirmed momentum more than
prediction. Only acts when regime, EMA alignment, MACD, and price
position all agree in one direction.
"""
from typing import Optional

from strategies.base import StrategyPolicy
from strategies.contracts import MarketState, StrategySignal, TechnicalState


class TrendFollowingStrategy(StrategyPolicy):
    """Follow established trends with EMA + MACD confirmation."""

    strategy_id = "trend-following"
    family = "trend_following"

    MIN_REGIME_CONFIDENCE = 0.55
    RSI_LONG_CAP = 75.0
    RSI_SHORT_FLOOR = 25.0

    def __init__(self, config: Optional[dict] = None):
        """Create trend-following strategy with optional replay-only knobs."""
        self.config = config or {}
        self.min_regime_confidence = float(
            self.config.get("min_regime_confidence", self.MIN_REGIME_CONFIDENCE)
        )
        self.rsi_long_cap = float(self.config.get("rsi_long_cap", self.RSI_LONG_CAP))
        self.rsi_short_floor = float(self.config.get("rsi_short_floor", self.RSI_SHORT_FLOOR))
        self.allow_volatile_trend_up = bool(self.config.get("allow_volatile_trend_up", False))
        self.allow_volatile_trend_down = bool(self.config.get("allow_volatile_trend_down", False))

    def evaluate(
        self,
        technical_state: TechnicalState,
        market_state: MarketState,
        context: Optional[dict] = None,
    ) -> StrategySignal:
        """Return long/short if a confirmed trend exists; otherwise hold/skip."""
        close = technical_state.close
        ema_20 = technical_state.ema_20
        ema_50 = technical_state.ema_50
        macd_hist = technical_state.macd_histogram
        rsi = technical_state.rsi
        regime = market_state.regime
        original_regime = regime
        confidence = float(market_state.confidence)

        # Default fail-safe for volatile regime. Batch 3H may opt into
        # replay-only volatile trend exceptions without changing defaults.
        if regime == "volatile":
            if self.allow_volatile_trend_down and market_state.trend_direction == "down":
                regime = "trend_down"
            elif self.allow_volatile_trend_up and market_state.trend_direction == "up":
                regime = "trend_up"
            else:
                return self._skip(
                    technical_state,
                    market_state,
                    "Volatile regime — trend-following does not trade chop",
                )

        # Fail-safe for missing core data.
        if close is None or ema_20 is None or ema_50 is None or macd_hist is None:
            return self._skip(
                technical_state,
                market_state,
                "Missing required EMA/MACD/close data for trend-following",
                data_quality=True,
            )

        if confidence < self.min_regime_confidence:
            return self._hold(
                technical_state,
                market_state,
                "Regime confidence below trend-following threshold",
            )

        # Long setup
        if regime == "trend_up":
            if ema_20 <= ema_50:
                return self._hold(technical_state, market_state, "EMA alignment not bullish")
            if not (close > ema_20 or close > ema_50):
                return self._hold(technical_state, market_state, "Price not above EMAs")
            if macd_hist <= 0:
                return self._hold(technical_state, market_state, "MACD histogram not positive")
            if rsi is not None and rsi >= self.rsi_long_cap:
                return self._skip(
                    technical_state,
                    market_state,
                    f"RSI overbought ({rsi:.1f}) — avoid chasing long",
                )

            signal_confidence = self._trend_confidence(confidence, technical_state)
            return StrategySignal(
                strategy_id=self.strategy_id,
                family=self.family,
                action="long",
                confidence=round(signal_confidence, 4),
                setup="Established uptrend with EMA and MACD confirmation",
                trigger=f"close={close:.4f} > EMAs, EMA20={ema_20:.4f} > EMA50={ema_50:.4f}, MACD histogram={macd_hist:.4f} > 0",
                invalidation="close below EMA50 or MACD histogram flips negative",
                sizing_hint="normal risk when confidence >= 0.70, reduced risk when marginal",
                exit_plan="trail with EMA20; exit on opposite trigger or EMA50 loss",
                risk_notes=[
                    "Trend following works until it doesn't — use stop below EMA50.",
                    f"RSI={rsi:.1f}" if rsi is not None else "RSI unavailable",
                ],
                attribution={
                    "regime": regime,
                    "original_regime": original_regime,
                    "trend_direction": market_state.trend_direction,
                    "ema_20": ema_20,
                    "ema_50": ema_50,
                    "macd_histogram": macd_hist,
                    "rsi": rsi,
                },
            )

        # Short setup
        if regime == "trend_down":
            if ema_20 >= ema_50:
                return self._hold(technical_state, market_state, "EMA alignment not bearish")
            if not (close < ema_20 or close < ema_50):
                return self._hold(technical_state, market_state, "Price not below EMAs")
            if macd_hist >= 0:
                return self._hold(technical_state, market_state, "MACD histogram not negative")
            if rsi is not None and rsi <= self.rsi_short_floor:
                return self._skip(
                    technical_state,
                    market_state,
                    f"RSI oversold ({rsi:.1f}) — avoid chasing short",
                )

            signal_confidence = self._trend_confidence(confidence, technical_state)
            return StrategySignal(
                strategy_id=self.strategy_id,
                family=self.family,
                action="short",
                confidence=round(signal_confidence, 4),
                setup="Established downtrend with EMA and MACD confirmation",
                trigger=f"close={close:.4f} < EMAs, EMA20={ema_20:.4f} < EMA50={ema_50:.4f}, MACD histogram={macd_hist:.4f} < 0",
                invalidation="close above EMA50 or MACD histogram flips positive",
                sizing_hint="normal risk when confidence >= 0.70, reduced risk when marginal",
                exit_plan="trail with EMA20; exit on opposite trigger or EMA50 reclaim",
                risk_notes=[
                    "Trend following works until it doesn't — use stop above EMA50.",
                    f"RSI={rsi:.1f}" if rsi is not None else "RSI unavailable",
                ],
                attribution={
                    "regime": regime,
                    "original_regime": original_regime,
                    "trend_direction": market_state.trend_direction,
                    "ema_20": ema_20,
                    "ema_50": ema_50,
                    "macd_histogram": macd_hist,
                    "rsi": rsi,
                },
            )

        # Non-trend regime
        return self._hold(
            technical_state,
            market_state,
            f"Regime '{regime}' is not trend_up/trend_down — no trend-following setup",
        )

    def _trend_confidence(self, regime_confidence: float, technical_state: TechnicalState) -> float:
        """Combine regime confidence with technical clarity into a 0-1 score."""
        score = regime_confidence

        ema_20 = technical_state.ema_20
        ema_50 = technical_state.ema_50
        close = technical_state.close

        if ema_20 is not None and ema_50 is not None and ema_50 != 0:
            ema_spread = abs(ema_20 - ema_50) / ema_50
            score += min(0.10, ema_spread * 2)

        if close is not None and ema_50 is not None and ema_50 != 0:
            price_spread = abs(close - ema_50) / ema_50
            score += min(0.10, price_spread * 2)

        return min(0.95, max(0.55, score))

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
            setup="trend-following guard check",
            trigger="no confirmed trend setup",
            invalidation="n/a",
            sizing_hint="no position",
            exit_plan="n/a",
            no_trade_reason=reason,
            risk_notes=["Trend-following conditions not met."],
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
            setup="trend-following no-trade guard",
            trigger="state incompatible with trend-following edge",
            invalidation="state becomes compatible",
            sizing_hint="no position",
            exit_plan="n/a",
            no_trade_reason=reason,
            risk_notes=[
                "Data quality issue — cannot evaluate trend." if data_quality else "Conditions unfavorable for trend-following entry.",
            ],
            attribution={"regime": market_state.regime},
        )

#!/usr/bin/env python3
"""Tests for Phase 1 strategy playbooks."""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from strategies.base import StrategyPolicy
from strategies.breakout import BreakoutStrategy
from strategies.contracts import MarketState, StrategyAction, StrategySignal, TechnicalState
from strategies.trend_following import TrendFollowingStrategy
from strategies.volatility_skip import VolatilitySkipStrategy


ERRORS = []


def assert_true(cond, msg=""):
    if not cond:
        ERRORS.append(msg or "assertion failed")


def assert_eq(a, b, msg=""):
    if a != b:
        ERRORS.append(msg or f"expected {b!r}, got {a!r}")


def _run_named(test_fn):
    """Run a test and attribute any ERRORS to it."""
    before = len(ERRORS)
    try:
        test_fn()
    except Exception as e:
        ERRORS.append(f"{test_fn.__name__}: {e}")
        print(f"FAIL {test_fn.__name__}: {e}")
        return
    if len(ERRORS) == before:
        print(f"PASS {test_fn.__name__}")
    else:
        print(f"FAIL {test_fn.__name__}")


# ---------------------------------------------------------------------------
# Base interface
# ---------------------------------------------------------------------------


def test_strategy_policy_abstract():
    """StrategyPolicy cannot be instantiated directly."""
    try:
        StrategyPolicy()
        ERRORS.append("StrategyPolicy should be abstract")
    except TypeError:
        pass


def test_dummy_subclass_evaluate():
    """A concrete subclass returns a StrategySignal."""
    class DummyStrategy(StrategyPolicy):
        strategy_id = "dummy"
        family = "test"

        def evaluate(self, technical_state, market_state, context=None):
            return StrategySignal(
                strategy_id=self.strategy_id,
                family=self.family,
                action=StrategyAction.HOLD.value,
                confidence=0.5,
            )

    strat = DummyStrategy()
    ts = TechnicalState(close=100.0)
    ms = MarketState(regime="ranging")
    sig = strat.evaluate(ts, ms)
    assert_eq(sig.strategy_id, "dummy")
    assert_eq(sig.action, "hold")


# ---------------------------------------------------------------------------
# Volatility skip
# ---------------------------------------------------------------------------


def test_volatility_skip_in_volatile_regime():
    strategy = VolatilitySkipStrategy()
    ts = TechnicalState(close=100.0, atr=3.0)
    ms = MarketState(regime="volatile", confidence=0.8, adx=45.0)
    sig = strategy.evaluate(ts, ms)
    assert_eq(sig.action, "skip")
    assert_true(sig.no_trade_reason is not None)
    assert_true("volatile" in sig.no_trade_reason.lower())


def test_volatility_skip_on_extreme_atr():
    strategy = VolatilitySkipStrategy()
    ts = TechnicalState(close=100.0, atr=9.0)
    ms = MarketState(regime="trend_up")
    sig = strategy.evaluate(ts, ms)
    assert_eq(sig.action, "skip")
    assert_true("ATR" in sig.no_trade_reason or "volatility" in sig.no_trade_reason.lower())


def test_volatility_skip_hold_when_quiet():
    strategy = VolatilitySkipStrategy()
    ts = TechnicalState(close=100.0, atr=2.0)
    ms = MarketState(regime="trend_up", confidence=0.7, adx=30.0)
    sig = strategy.evaluate(ts, ms)
    assert_eq(sig.action, "hold")
    assert_eq(sig.no_trade_reason, None)


def test_volatility_skip_missing_atr_does_not_crash():
    strategy = VolatilitySkipStrategy()
    ts = TechnicalState(close=100.0, atr=None)
    ms = MarketState(regime="ranging")
    sig = strategy.evaluate(ts, ms)
    assert_eq(sig.action, "hold")


# ---------------------------------------------------------------------------
# Trend following
# ---------------------------------------------------------------------------


def test_trend_following_long():
    strategy = TrendFollowingStrategy()
    ts = TechnicalState(
        close=105.0,
        ema_20=102.0,
        ema_50=100.0,
        macd_histogram=1.5,
        rsi=55.0,
    )
    ms = MarketState(regime="trend_up", confidence=0.75, trend_direction="up")
    sig = strategy.evaluate(ts, ms)
    assert_eq(sig.action, "long")
    assert_true(sig.confidence >= 0.55)
    assert_true("ema" in sig.trigger.lower() or "macd" in sig.trigger.lower())


def test_trend_following_short():
    strategy = TrendFollowingStrategy()
    ts = TechnicalState(
        close=95.0,
        ema_20=98.0,
        ema_50=100.0,
        macd_histogram=-1.5,
        rsi=45.0,
    )
    ms = MarketState(regime="trend_down", confidence=0.75, trend_direction="down")
    sig = strategy.evaluate(ts, ms)
    assert_eq(sig.action, "short")
    assert_true(sig.confidence >= 0.55)


def test_trend_following_volatile_regime_skips():
    strategy = TrendFollowingStrategy()
    ts = TechnicalState(close=100.0, ema_20=101.0, ema_50=100.0, macd_histogram=1.0)
    ms = MarketState(regime="volatile", confidence=0.8)
    sig = strategy.evaluate(ts, ms)
    assert_eq(sig.action, "skip")


def test_trend_following_missing_data_skips():
    strategy = TrendFollowingStrategy()
    ts = TechnicalState(close=100.0, ema_20=None, ema_50=100.0, macd_histogram=1.0)
    ms = MarketState(regime="trend_up", confidence=0.75)
    sig = strategy.evaluate(ts, ms)
    assert_eq(sig.action, "skip")


def test_trend_following_ranging_holds():
    strategy = TrendFollowingStrategy()
    ts = TechnicalState(
        close=100.0,
        ema_20=101.0,
        ema_50=100.0,
        macd_histogram=1.0,
    )
    ms = MarketState(regime="ranging", confidence=0.6)
    sig = strategy.evaluate(ts, ms)
    assert_eq(sig.action, "hold")


def test_trend_following_rsi_overbought_prevents_long():
    strategy = TrendFollowingStrategy()
    ts = TechnicalState(
        close=105.0,
        ema_20=102.0,
        ema_50=100.0,
        macd_histogram=1.5,
        rsi=78.0,
    )
    ms = MarketState(regime="trend_up", confidence=0.75)
    sig = strategy.evaluate(ts, ms)
    assert_eq(sig.action, "skip")
    assert_true("RSI" in sig.no_trade_reason or "overbought" in sig.no_trade_reason.lower())


def test_trend_following_rsi_oversold_prevents_short():
    strategy = TrendFollowingStrategy()
    ts = TechnicalState(
        close=95.0,
        ema_20=98.0,
        ema_50=100.0,
        macd_histogram=-1.5,
        rsi=22.0,
    )
    ms = MarketState(regime="trend_down", confidence=0.75)
    sig = strategy.evaluate(ts, ms)
    assert_eq(sig.action, "skip")
    assert_true("RSI" in sig.no_trade_reason or "oversold" in sig.no_trade_reason.lower())


# ---------------------------------------------------------------------------
# Breakout
# ---------------------------------------------------------------------------


def test_breakout_long():
    strategy = BreakoutStrategy()
    ts = TechnicalState(
        close=105.0,
        recent_high_20=100.0,
        recent_low_20=90.0,
        breakout_up_20=True,
        macd_histogram=1.0,
        macd_crossing_up=True,
    )
    ms = MarketState(regime="ranging", confidence=0.6)
    sig = strategy.evaluate(ts, ms)
    assert_eq(sig.action, "long")
    assert_true("breakout" in sig.setup.lower() or "recent_high_20" in sig.trigger)
    assert_true("recent_high_20" in sig.attribution)


def test_breakout_short():
    strategy = BreakoutStrategy()
    ts = TechnicalState(
        close=85.0,
        recent_high_20=100.0,
        recent_low_20=90.0,
        breakout_down_20=True,
        macd_histogram=-1.0,
        macd_crossing_down=True,
    )
    ms = MarketState(regime="ranging", confidence=0.6)
    sig = strategy.evaluate(ts, ms)
    assert_eq(sig.action, "short")
    assert_true("recent_low_20" in sig.attribution)


def test_breakout_volatile_regime_skips():
    strategy = BreakoutStrategy()
    ts = TechnicalState(
        close=105.0,
        recent_high_20=100.0,
        recent_low_20=90.0,
        breakout_up_20=True,
        macd_histogram=1.0,
    )
    ms = MarketState(regime="volatile", confidence=0.8)
    sig = strategy.evaluate(ts, ms)
    assert_eq(sig.action, "skip")


def test_breakout_missing_donchian_skips():
    strategy = BreakoutStrategy()
    ts = TechnicalState(close=105.0, recent_high_20=None, recent_low_20=None)
    ms = MarketState(regime="ranging", confidence=0.6)
    sig = strategy.evaluate(ts, ms)
    assert_eq(sig.action, "skip")


def test_breakout_unconfirmed_breakout_holds():
    strategy = BreakoutStrategy()
    ts = TechnicalState(
        close=105.0,
        recent_high_20=100.0,
        recent_low_20=90.0,
        breakout_up_20=True,
        macd_histogram=-0.5,
        macd_crossing_up=False,
    )
    ms = MarketState(regime="ranging", confidence=0.6)
    sig = strategy.evaluate(ts, ms)
    assert_eq(sig.action, "hold")
    assert_true("confirmation" in sig.no_trade_reason.lower() or "MACD" in sig.no_trade_reason)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def run_tests():
    tests = [
        test_strategy_policy_abstract,
        test_dummy_subclass_evaluate,
        test_volatility_skip_in_volatile_regime,
        test_volatility_skip_on_extreme_atr,
        test_volatility_skip_hold_when_quiet,
        test_volatility_skip_missing_atr_does_not_crash,
        test_trend_following_long,
        test_trend_following_short,
        test_trend_following_volatile_regime_skips,
        test_trend_following_missing_data_skips,
        test_trend_following_ranging_holds,
        test_trend_following_rsi_overbought_prevents_long,
        test_trend_following_rsi_oversold_prevents_short,
        test_breakout_long,
        test_breakout_short,
        test_breakout_volatile_regime_skips,
        test_breakout_missing_donchian_skips,
        test_breakout_unconfirmed_breakout_holds,
    ]
    for t in tests:
        _run_named(t)

    if ERRORS:
        print(f"\n{len(ERRORS)} FAILURES:")
        for err in ERRORS:
            print(f"  - {err}")
        return 1

    print(f"\nAll {len(tests)} tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(run_tests())

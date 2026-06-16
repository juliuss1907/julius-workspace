#!/usr/bin/env python3
"""Tests for Phase 1 strategy playbooks."""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from strategies.base import StrategyPolicy
from strategies.contracts import MarketState, StrategyAction, StrategySignal, TechnicalState
from strategies.volatility_skip import VolatilitySkipStrategy


ERRORS = []


def assert_true(cond, msg=""):
    if not cond:
        ERRORS.append(msg or "assertion failed")


def assert_eq(a, b, msg=""):
    if a != b:
        ERRORS.append(msg or f"expected {b!r}, got {a!r}")


def test_strategy_policy_abstract():
    """StrategyPolicy cannot be instantiated directly."""
    try:
        StrategyPolicy()
        ERRORS.append("StrategyPolicy should be abstract")
    except TypeError:
        pass
    print("PASS test_strategy_policy_abstract")


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
    print("PASS test_dummy_subclass_evaluate")


def test_volatility_skip_in_volatile_regime():
    strategy = VolatilitySkipStrategy()
    ts = TechnicalState(close=100.0, atr=3.0)
    ms = MarketState(regime="volatile", confidence=0.8, adx=45.0)
    sig = strategy.evaluate(ts, ms)
    assert_eq(sig.action, "skip")
    assert_true(sig.no_trade_reason is not None)
    assert_true("volatile" in sig.no_trade_reason.lower())
    print("PASS test_volatility_skip_in_volatile_regime")


def test_volatility_skip_on_extreme_atr():
    strategy = VolatilitySkipStrategy()
    # ATR / close = 9 / 100 = 9% >= 8% threshold
    ts = TechnicalState(close=100.0, atr=9.0)
    ms = MarketState(regime="trend_up")
    sig = strategy.evaluate(ts, ms)
    assert_eq(sig.action, "skip")
    assert_true("ATR" in sig.no_trade_reason or "volatility" in sig.no_trade_reason.lower())
    print("PASS test_volatility_skip_on_extreme_atr")


def test_volatility_skip_hold_when_quiet():
    strategy = VolatilitySkipStrategy()
    ts = TechnicalState(close=100.0, atr=2.0)
    ms = MarketState(regime="trend_up", confidence=0.7, adx=30.0)
    sig = strategy.evaluate(ts, ms)
    assert_eq(sig.action, "hold")
    assert_eq(sig.no_trade_reason, None)
    print("PASS test_volatility_skip_hold_when_quiet")


def test_volatility_skip_missing_atr_does_not_crash():
    strategy = VolatilitySkipStrategy()
    ts = TechnicalState(close=100.0, atr=None)
    ms = MarketState(regime="ranging")
    sig = strategy.evaluate(ts, ms)
    assert_eq(sig.action, "hold")
    print("PASS test_volatility_skip_missing_atr_does_not_crash")


def test_volatility_skip_has_risk_notes():
    strategy = VolatilitySkipStrategy()
    ts = TechnicalState(close=100.0, atr=9.0)
    ms = MarketState(regime="trend_up")
    sig = strategy.evaluate(ts, ms)
    assert_true(len(sig.risk_notes) > 0)
    print("PASS test_volatility_skip_has_risk_notes")


def run_tests():
    tests = [
        test_strategy_policy_abstract,
        test_dummy_subclass_evaluate,
        test_volatility_skip_in_volatile_regime,
        test_volatility_skip_on_extreme_atr,
        test_volatility_skip_hold_when_quiet,
        test_volatility_skip_missing_atr_does_not_crash,
        test_volatility_skip_has_risk_notes,
    ]
    for t in tests:
        try:
            t()
        except Exception as e:
            ERRORS.append(f"{t.__name__}: {e}")
            print(f"FAIL {t.__name__}: {e}")

    if ERRORS:
        print(f"\n{len(ERRORS)} FAILURES:")
        for err in ERRORS:
            print(f"  - {err}")
        return 1

    print(f"\nAll {len(tests)} tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(run_tests())

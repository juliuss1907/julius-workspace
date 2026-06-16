#!/usr/bin/env python3
"""Tests for the Phase 1 strategy registry."""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from strategies.contracts import MarketState, StrategySignal, TechnicalState
from strategies.registry import StrategyRegistry


ERRORS = []


def assert_true(cond, msg=""):
    if not cond:
        ERRORS.append(msg or "assertion failed")


def assert_eq(a, b, msg=""):
    if a != b:
        ERRORS.append(msg or f"expected {b!r}, got {a!r}")


def _run_named(test_fn):
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
# Helpers
# ---------------------------------------------------------------------------


def _make_trend_up_state() -> tuple:
    ts = TechnicalState(
        close=105.0,
        ema_20=102.0,
        ema_50=100.0,
        macd_histogram=1.5,
        rsi=55.0,
        atr=2.0,
    )
    ms = MarketState(regime="trend_up", confidence=0.75, trend_direction="up")
    return ts, ms


def _make_trend_down_state() -> tuple:
    ts = TechnicalState(
        close=95.0,
        ema_20=98.0,
        ema_50=100.0,
        macd_histogram=-1.5,
        rsi=45.0,
        atr=2.0,
    )
    ms = MarketState(regime="trend_down", confidence=0.75, trend_direction="down")
    return ts, ms


def _make_ranging_breakout_state(up: bool = True) -> tuple:
    if up:
        ts = TechnicalState(
            close=105.0,
            recent_high_20=100.0,
            recent_low_20=90.0,
            breakout_up_20=True,
            macd_histogram=1.0,
            macd_crossing_up=True,
            atr=2.0,
        )
    else:
        ts = TechnicalState(
            close=85.0,
            recent_high_20=100.0,
            recent_low_20=90.0,
            breakout_down_20=True,
            macd_histogram=-1.0,
            macd_crossing_down=True,
            atr=2.0,
        )
    ms = MarketState(regime="ranging", confidence=0.6)
    return ts, ms


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------


def test_registry_has_phase_one_families():
    registry = StrategyRegistry()
    assert_true("volatility_skip" in registry._strategies)
    assert_true("trend_following" in registry._strategies)
    assert_true("breakout" in registry._strategies)
    assert_eq(len(registry._strategies), 3)


def test_registry_volatile_state_returns_skip():
    registry = StrategyRegistry()
    ts = TechnicalState(close=100.0, atr=2.0)
    ms = MarketState(regime="volatile", confidence=0.8, adx=40.0)
    sig = registry.select(ts, ms)
    assert_eq(sig.action, "skip")
    assert_eq(sig.strategy_id, "volatility-skip")


def test_registry_trend_up_returns_trend_following_long():
    registry = StrategyRegistry()
    ts, ms = _make_trend_up_state()
    sig = registry.select(ts, ms)
    assert_eq(sig.action, "long")
    assert_eq(sig.strategy_id, "trend-following")


def test_registry_trend_down_returns_trend_following_short():
    registry = StrategyRegistry()
    ts, ms = _make_trend_down_state()
    sig = registry.select(ts, ms)
    assert_eq(sig.action, "short")
    assert_eq(sig.strategy_id, "trend-following")


def test_registry_ranging_returns_breakout_long():
    registry = StrategyRegistry()
    ts, ms = _make_ranging_breakout_state(up=True)
    sig = registry.select(ts, ms)
    assert_eq(sig.action, "long")
    assert_eq(sig.strategy_id, "breakout")


def test_registry_ranging_returns_breakout_short():
    registry = StrategyRegistry()
    ts, ms = _make_ranging_breakout_state(up=False)
    sig = registry.select(ts, ms)
    assert_eq(sig.action, "short")
    assert_eq(sig.strategy_id, "breakout")


def test_registry_weak_confidence_action_blocked():
    registry = StrategyRegistry(config={"min_action_confidence": 0.95})
    ts, ms = _make_trend_up_state()
    ms.confidence = 0.60
    sig = registry.select(ts, ms)
    # trend_following returns long with confidence < 0.95, registry should fallback
    assert_true(sig.action in ("hold", "skip"))


def test_registry_nested_selection_config_sets_confidence_floor():
    registry = StrategyRegistry(config={"selection": {"min_action_confidence": 0.95}})
    ts, ms = _make_trend_up_state()
    ms.confidence = 0.60
    sig = registry.select(ts, ms)
    assert_true(sig.action in ("hold", "skip"))


def test_registry_custom_order_override():
    registry = StrategyRegistry(config={
        "regime_strategy_order": {
            "trend_up": ["volatility_skip", "breakout", "trend_following"],
        },
        "min_action_confidence": 0.55,
    })
    ts = TechnicalState(
        close=105.0,
        ema_20=102.0,
        ema_50=100.0,
        macd_histogram=1.5,
        recent_high_20=100.0,
        recent_low_20=90.0,
        breakout_up_20=True,
        macd_crossing_up=True,
        atr=2.0,
    )
    ms = MarketState(regime="trend_up", confidence=0.75)
    sig = registry.select(ts, ms)
    # With breakout first, it should win over trend_following
    assert_eq(sig.strategy_id, "breakout")
    assert_eq(sig.action, "long")


def test_registry_all_skip_returns_valid_signal():
    registry = StrategyRegistry()
    ts = TechnicalState(close=100.0, atr=12.0)  # high ATR triggers volatility skip
    ms = MarketState(regime="trend_up", confidence=0.75)
    sig = registry.select(ts, ms)
    assert_true(isinstance(sig, StrategySignal))
    assert_eq(sig.action, "skip")
    assert_true("evaluated" in sig.attribution)


def test_registry_attribution_includes_evaluated():
    registry = StrategyRegistry()
    ts, ms = _make_trend_up_state()
    sig = registry.select(ts, ms)
    evaluated = sig.attribution.get("evaluated", [])
    assert_true(len(evaluated) > 0)
    ids = [e["strategy_id"] for e in evaluated]
    assert_true("volatility-skip" in ids)
    assert_true("trend-following" in ids)


def run_tests():
    tests = [
        test_registry_has_phase_one_families,
        test_registry_volatile_state_returns_skip,
        test_registry_trend_up_returns_trend_following_long,
        test_registry_trend_down_returns_trend_following_short,
        test_registry_ranging_returns_breakout_long,
        test_registry_ranging_returns_breakout_short,
        test_registry_weak_confidence_action_blocked,
        test_registry_nested_selection_config_sets_confidence_floor,
        test_registry_custom_order_override,
        test_registry_all_skip_returns_valid_signal,
        test_registry_attribution_includes_evaluated,
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

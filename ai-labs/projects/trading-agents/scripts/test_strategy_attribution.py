#!/usr/bin/env python3
"""Tests for pure strategies/attribution.py helper."""
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from strategies.attribution import build_strategy_signal, fallback_strategy_signal


ERRORS = []


def assert_true(cond, msg=""):
    if not cond:
        ERRORS.append(msg or "assertion failed")


def assert_eq(a, b, msg=""):
    if a != b:
        ERRORS.append(msg or f"expected {b!r}, got {a!r}")


def _technical_analysis_with_states():
    return {
        "technical_state": {
            "close": 68000.0,
            "rsi": 58.0,
            "macd_histogram": 120.0,
            "macd_crossing_up": False,
            "macd_crossing_down": False,
            "bb_position": 0.62,
            "atr": 1500.0,
            "ema_20": 67000.0,
            "ema_50": 65000.0,
            "ema_200": 60000.0,
            "volume": 1000.0,
            "obv": 10000.0,
            "obv_prev": 9500.0,
            "recent_high_20": 67500.0,
            "recent_low_20": 62000.0,
            "breakout_up_20": True,
            "breakout_down_20": False,
            "scores": {"momentum": 0.7},
        },
        "market_state": {
            "regime": "trend_up",
            "confidence": 0.75,
            "trend_direction": "up",
            "trend_strength": 0.7,
            "adx": 28.0,
            "bb_width": 0.04,
            "reason": "uptrend regime",
        },
    }


def test_build_strategy_signal_returns_serialized_dict():
    signal = build_strategy_signal(
        _technical_analysis_with_states(),
        strategy_config={"selection": {"min_action_confidence": 0.55}},
        source="unit_test",
    )

    assert_true(isinstance(signal, dict), "signal must be dict")
    assert_true(signal["action"] in ("long", "short", "hold", "skip"))
    assert_true(signal["strategy_id"] in ("volatility-skip", "trend-following", "breakout", "registry"))
    assert_true("evaluated" in signal["attribution"])
    assert_eq(signal["attribution"].get("source"), "unit_test")


def test_build_strategy_signal_degrades_when_states_missing():
    signal = build_strategy_signal({}, source="unit_test")

    assert_eq(signal["strategy_id"], "registry")
    assert_eq(signal["action"], "skip")
    assert_true("missing" in signal["trigger"])
    assert_eq(signal["attribution"].get("source"), "unit_test")


def test_build_strategy_signal_respects_disabled_config():
    signal = build_strategy_signal(
        _technical_analysis_with_states(),
        strategy_config={"enabled": False},
        source="unit_test",
    )

    assert_eq(signal["action"], "skip")
    assert_eq(signal["no_trade_reason"], "Strategy layer disabled by config")
    assert_eq(signal["attribution"].get("source"), "unit_test")


def test_fallback_strategy_signal_shape():
    signal = fallback_strategy_signal("test reason", source="unit_test")

    assert_eq(signal["strategy_id"], "registry")
    assert_eq(signal["family"], "registry")
    assert_eq(signal["action"], "skip")
    assert_eq(signal["confidence"], 0.0)
    assert_eq(signal["trigger"], "test reason")
    assert_true(isinstance(signal["risk_notes"], list))
    assert_eq(signal["attribution"].get("source"), "unit_test")


def run_tests():
    tests = [
        ("build_strategy_signal_returns_serialized_dict", test_build_strategy_signal_returns_serialized_dict),
        ("build_strategy_signal_degrades_when_states_missing", test_build_strategy_signal_degrades_when_states_missing),
        ("build_strategy_signal_respects_disabled_config", test_build_strategy_signal_respects_disabled_config),
        ("fallback_strategy_signal_shape", test_fallback_strategy_signal_shape),
    ]

    all_errors = []
    passed = 0
    for name, fn in tests:
        ERRORS.clear()
        try:
            fn()
            if ERRORS:
                for err in ERRORS:
                    all_errors.append(f"{name}: {err}")
                    print(f"FAIL {name}: {err}")
            else:
                print(f"PASS {name}")
                passed += 1
        except Exception as exc:
            all_errors.append(f"{name}: {exc}")
            print(f"FAIL {name}: {exc}")

    if all_errors:
        print(f"\n{len(all_errors)} FAILURES:")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print(f"\nAll {passed} strategy attribution tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_tests())

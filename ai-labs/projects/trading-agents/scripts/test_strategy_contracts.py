#!/usr/bin/env python3
"""Tests for pure strategy-layer contracts."""
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from strategies.contracts import (
    StrategyAction,
    StrategyFamily,
    TechnicalState,
    MarketState,
    StrategySignal,
)


ERRORS = []


def assert_true(cond, msg=""):
    if not cond:
        ERRORS.append(msg or "assertion failed")


def assert_eq(a, b, msg=""):
    if a != b:
        ERRORS.append(msg or f"expected {b!r}, got {a!r}")


def test_strategy_action_enum_values():
    assert_true(isinstance(StrategyAction.LONG, str), "StrategyAction should be a string enum")
    assert_eq(StrategyAction.LONG.value, "long")
    assert_eq(StrategyAction.SHORT.value, "short")
    assert_eq(StrategyAction.HOLD.value, "hold")
    assert_eq(StrategyAction.SKIP.value, "skip")
    assert_eq(StrategyAction.EXIT.value, "exit")
    assert_eq(StrategyAction.REDUCE.value, "reduce")
    print("PASS test_strategy_action_enum_values")


def test_strategy_family_enum_values():
    assert_true(isinstance(StrategyFamily.TREND_FOLLOWING, str), "StrategyFamily should be a string enum")
    assert_eq(StrategyFamily.TREND_FOLLOWING.value, "trend_following")
    assert_eq(StrategyFamily.BREAKOUT.value, "breakout")
    assert_eq(StrategyFamily.VOLATILITY_SKIP.value, "volatility_skip")
    assert_eq(StrategyFamily.MEAN_REVERSION.value, "mean_reversion")
    print("PASS test_strategy_family_enum_values")


def test_technical_state_fields():
    ts = TechnicalState(
        close=100.0,
        rsi=55.0,
        macd_histogram=0.5,
        macd_crossing_up=True,
        macd_crossing_down=False,
        bb_position=0.6,
        atr=2.0,
        ema_20=99.0,
        ema_50=98.0,
        ema_200=95.0,
        volume=1000.0,
        obv=5000.0,
        obv_prev=4800.0,
        recent_high_20=105.0,
        recent_low_20=95.0,
        breakout_up_20=True,
        breakout_down_20=False,
        scores={"trend": 0.7, "momentum": 0.6},
    )
    d = ts.to_dict()
    assert_eq(d["close"], 100.0)
    assert_eq(d["recent_high_20"], 105.0)
    assert_eq(d["recent_low_20"], 95.0)
    assert_eq(d["breakout_up_20"], True)
    assert_eq(d["breakout_down_20"], False)
    assert_eq(d["scores"], {"trend": 0.7, "momentum": 0.6})
    print("PASS test_technical_state_fields")


def test_market_state_fields():
    ms = MarketState(
        regime="trend_up",
        confidence=0.75,
        trend_direction="up",
        trend_strength=60.0,
        adx=30.0,
        bb_width=0.05,
        reason="Strong uptrend",
    )
    d = ms.to_dict()
    assert_eq(d["regime"], "trend_up")
    assert_eq(d["confidence"], 0.75)
    assert_eq(d["trend_direction"], "up")
    assert_eq(d["bb_width"], 0.05)
    print("PASS test_market_state_fields")


def test_strategy_signal_fields():
    sig = StrategySignal(
        strategy_id="volatility-skip",
        family="volatility_skip",
        action="skip",
        confidence=0.8,
        setup="volatile regime",
        trigger="ADX high",
        invalidation="ADX falls below 25",
        sizing_hint="no position",
        exit_plan="n/a",
        no_trade_reason="too volatile",
        risk_notes=["wide stops"],
        attribution={"adx": 45.0},
    )
    d = sig.to_dict()
    assert_eq(d["strategy_id"], "volatility-skip")
    assert_eq(d["family"], "volatility_skip")
    assert_eq(d["action"], "skip")
    assert_eq(d["setup"], "volatile regime")
    assert_eq(d["trigger"], "ADX high")
    assert_eq(d["invalidation"], "ADX falls below 25")
    assert_eq(d["sizing_hint"], "no position")
    assert_eq(d["exit_plan"], "n/a")
    assert_eq(d["no_trade_reason"], "too volatile")
    assert_eq(d["risk_notes"], ["wide stops"])
    assert_eq(d["attribution"], {"adx": 45.0})
    print("PASS test_strategy_signal_fields")


def test_contracts_are_json_serializable():
    ts = TechnicalState(close=100.0, breakout_up_20=True)
    ms = MarketState(regime="ranging", confidence=0.5)
    sig = StrategySignal(
        strategy_id="test",
        family="test_family",
        action="hold",
        confidence=0.5,
    )
    payload = {
        "technical_state": ts.to_dict(),
        "market_state": ms.to_dict(),
        "signal": sig.to_dict(),
    }
    s = json.dumps(payload)
    restored = json.loads(s)
    assert_eq(restored["technical_state"]["close"], 100.0)
    assert_eq(restored["market_state"]["regime"], "ranging")
    assert_eq(restored["signal"]["action"], "hold")
    print("PASS test_contracts_are_json_serializable")


def run_tests():
    tests = [
        test_strategy_action_enum_values,
        test_strategy_family_enum_values,
        test_technical_state_fields,
        test_market_state_fields,
        test_strategy_signal_fields,
        test_contracts_are_json_serializable,
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

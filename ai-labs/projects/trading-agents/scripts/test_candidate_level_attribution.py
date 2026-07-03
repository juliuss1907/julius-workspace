#!/usr/bin/env python3
"""Tests for Batch 3W candidate-level StrategySignal attribution."""
from pathlib import Path
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from strategies.contracts import MarketState, TechnicalState
from strategies.registry import StrategyRegistry
ERRORS = []
def assert_true(cond, msg=""):
    if not cond: ERRORS.append(msg or "assertion failed")
def assert_eq(a, b, msg=""):
    if a != b: ERRORS.append(msg or f"expected {b!r}, got {a!r}")
def _variant_d_registry():
    return StrategyRegistry(config={"regime_strategy_order":{"trend_up":["volatility_skip","trend_following","breakout"],"trend_down":["volatility_skip","trend_following","breakout"],"ranging":["volatility_skip","breakout"],"volatile":["volatility_skip","trend_following","breakout"]},"volatility_skip":{"volatile_confidence_floor":0.75,"high_atr_pct":0.10},"trend_following":{"allow_volatile_trend_up":True,"allow_volatile_trend_down":True,"min_regime_confidence":0.50},"breakout":{"allow_volatile":False},"selection":{"min_action_confidence":0.50,"prefer_action_over_hold":True}})
def _trend_up_state():
    return (TechnicalState(close=106.0,atr=2.0,ema_20=103.0,ema_50=100.0,macd_histogram=1.2,rsi=55.0), MarketState(regime="trend_up",confidence=0.75,trend_direction="up"))
def _volatile_trend_up_state(confidence=0.60, atr=9.0):
    return (TechnicalState(close=106.0,atr=atr,ema_20=103.0,ema_50=100.0,macd_histogram=1.2,rsi=55.0,breakout_up_20=True,recent_high_20=105.0,recent_low_20=95.0), MarketState(regime="volatile",confidence=confidence,trend_direction="up",trend_strength=70.0))
def _ranging_breakout_state():
    return (TechnicalState(close=105.0,atr=2.0,recent_high_20=100.0,recent_low_20=90.0,breakout_up_20=True,macd_histogram=1.0,macd_crossing_up=True), MarketState(regime="ranging",confidence=0.60))
def _assert_candidate_shape(candidate):
    for key in ("strategy_id","family","action","confidence","selected","eligible"):
        assert_true(key in candidate, f"candidate missing {key}")
    assert_true("selection_reason" in candidate)
    assert_true("rejection_reason" in candidate)
    assert_true(isinstance(candidate.get("thresholds"), dict))
    assert_true(isinstance(candidate.get("observed"), dict))
def test_trend_up_decision_stable_and_candidates_explain_override():
    ts, ms = _trend_up_state(); sig = StrategyRegistry().select(ts, ms)
    assert_eq(sig.strategy_id, "trend-following"); assert_eq(sig.action, "long")
    attr = sig.attribution
    assert_eq(attr.get("candidate_schema_version"), "batch3w-v1")
    assert_eq(attr.get("selection_reason"), "action_confidence_above_floor")
    assert_eq(attr.get("prefer_action_over_hold_applied"), True)
    evaluated = attr.get("evaluated", [])
    assert_true(len(evaluated) >= 2)
    for candidate in evaluated: _assert_candidate_shape(candidate)
    vol = evaluated[0]
    assert_eq(vol["strategy_id"], "volatility-skip"); assert_eq(vol["selected"], False)
    assert_eq(vol["rejection_reason"], "hold_candidate_overridden_by_action_candidate")
    selected = [c for c in evaluated if c["selected"]]
    assert_eq(len(selected), 1); assert_eq(selected[0]["strategy_id"], "trend-following")
def test_volatile_trend_variant_d_keeps_selected_signal_and_exposes_thresholds():
    ts, ms = _volatile_trend_up_state(confidence=0.60, atr=9.0); sig = _variant_d_registry().select(ts, ms)
    assert_eq(sig.strategy_id, "trend-following"); assert_eq(sig.action, "long")
    vol = sig.attribution.get("evaluated", [])[0]
    assert_eq(vol["strategy_id"], "volatility-skip"); assert_eq(vol["action"], "hold"); assert_eq(vol["selected"], False)
    assert_eq(vol["thresholds"].get("high_atr_pct"), 0.10); assert_eq(vol["thresholds"].get("volatile_confidence_floor"), 0.75)
    assert_true("atr_pct" in vol["observed"])
def test_volatile_direct_skip_marks_selected_candidate():
    ts, ms = _volatile_trend_up_state(confidence=0.80, atr=2.0); sig = _variant_d_registry().select(ts, ms)
    assert_eq(sig.strategy_id, "volatility-skip"); assert_eq(sig.action, "skip")
    attr = sig.attribution; assert_eq(attr.get("selection_reason"), "volatility_skip_direct_guard")
    evaluated = attr.get("evaluated", [])
    assert_eq(len(evaluated), 1); assert_eq(evaluated[0]["selected"], True); assert_eq(evaluated[0]["selection_reason"], "volatility_skip_direct_guard")
def test_ranging_breakout_candidates_are_backward_compatible():
    ts, ms = _ranging_breakout_state(); sig = StrategyRegistry().select(ts, ms)
    assert_eq(sig.strategy_id, "breakout"); assert_eq(sig.action, "long")
    evaluated = sig.attribution.get("evaluated", [])
    ids = [candidate["strategy_id"] for candidate in evaluated]
    assert_true("volatility-skip" in ids); assert_true("breakout" in ids)
    assert_true(all("strategy_id" in candidate and "action" in candidate and "confidence" in candidate for candidate in evaluated))
def run_tests():
    tests=[test_trend_up_decision_stable_and_candidates_explain_override,test_volatile_trend_variant_d_keeps_selected_signal_and_exposes_thresholds,test_volatile_direct_skip_marks_selected_candidate,test_ranging_breakout_candidates_are_backward_compatible]
    for test in tests:
        before=len(ERRORS)
        try: test()
        except Exception as exc: ERRORS.append(f"{test.__name__}: {exc}")
        print(("PASS" if len(ERRORS)==before else "FAIL") + f" {test.__name__}")
    if ERRORS:
        print(f"\n{len(ERRORS)} FAILURES:")
        for error in ERRORS: print(f"  - {error}")
        return 1
    print(f"PASS {len(tests)} candidate-level attribution tests"); return 0
if __name__ == "__main__": raise SystemExit(run_tests())

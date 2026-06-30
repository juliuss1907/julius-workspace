#!/usr/bin/env python3
"""Tests for Batch 3K zero-block volatility-skip review."""
import json
import tempfile
from pathlib import Path

import analyze_volatility_skip_zero_blocks as zero


def _write_jsonl(path: Path, rows):
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def _record(symbol="BTCUSDT", final_action="BUY", close=100.0, atr=10.0, confidence=0.60, regime="volatile"):
    return {
        "symbol": symbol,
        "market_snapshot": {"timeframe": "1h"},
        "analysts": {"technical": {"analysis": {
            "technical_state": {
                "close": close, "rsi": 45.0, "macd_histogram": 1.2,
                "macd_crossing_up": True, "macd_crossing_down": False,
                "bb_position": 0.8, "atr": atr, "ema_20": 105.0,
                "ema_50": 100.0, "ema_200": 90.0, "volume": 1000.0,
                "obv": 20.0, "obv_prev": 10.0, "recent_high_20": 104.0,
                "recent_low_20": 92.0, "breakout_up_20": True,
                "breakout_down_20": False, "scores": {"bullish": 0.7},
            },
            "market_state": {
                "regime": regime, "confidence": confidence,
                "trend_direction": "up", "trend_strength": 80.0,
                "adx": 45.0, "bb_width": 0.08,
                "reason": "fixture volatile trend up",
            },
        }}},
        "final_signal": {"metadata": {"final_action": final_action}},
        "strategy_signal": {
            "strategy_id": "volatility-skip", "family": "volatility_skip",
            "action": "skip", "confidence": confidence, "setup": "fixture",
            "trigger": "fixture volatile", "invalidation": "n/a",
            "sizing_hint": "no position", "exit_plan": "n/a",
            "no_trade_reason": "fixture", "risk_notes": [],
            "attribution": {"regime": regime, "source": "fixture"},
        },
    }


def test_safe_atr_pct_handles_missing_or_zero_close():
    assert zero.atr_pct({"close": 0, "atr": 10}) is None
    assert zero.atr_pct({"close": None, "atr": 10}) is None
    assert zero.atr_pct({"close": 100, "atr": 8}) == 0.08


def test_bucket_classifiers():
    assert zero.confidence_bucket(0.49) == "<0.50"
    assert zero.confidence_bucket(0.60) == "0.50-0.75"
    assert zero.confidence_bucket(0.80) == "0.75-0.95"
    assert zero.confidence_bucket(0.99) == ">=0.95"
    assert zero.atr_bucket(0.07) == "<8%"
    assert zero.atr_bucket(0.09) == "8-10%"
    assert zero.atr_bucket(0.11) == "10-12%"
    assert zero.atr_bucket(0.13) == ">=12%"


def test_finds_baseline_direct_blocks_and_builds_report():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "fixture.jsonl"
        _write_jsonl(path, [_record(), _record(symbol="ETHUSDT", final_action="HOLD", atr=4.0)])
        report = zero.build_report([path], ["variant-d", "variant-b"])
    assert report["batch"] == "3K"
    assert report["aggregate"]["total_baseline_direct_blocks"] == 2
    assert report["production_change_authorized"] is False
    assert report["implementation_authorized"] is False
    assert report["runtime_default_config_change_performed"] is False
    assert report["requires_approval_before_runtime_change"] is True


def test_classifies_variant_d_confidence_and_atr_reasons():
    record = _record(close=100.0, atr=9.0, confidence=0.60)
    signal = zero.rebuild_candidate_signal(record, "variant-d")
    reasons = zero.classify_unblock_reasons(record, "variant-d", signal)
    assert "volatile_confidence_below_floor" in reasons
    assert "atr_below_candidate_threshold" in reasons


def test_classifies_variant_b_breakout_reason_when_selected():
    record = _record(close=100.0, atr=9.0, confidence=0.60)
    signal = zero.rebuild_candidate_signal(record, "variant-b")
    reasons = zero.classify_unblock_reasons(record, "variant-b", signal)
    assert "volatile_confidence_below_floor" in reasons
    assert "atr_below_candidate_threshold" in reasons
    if signal.get("family") == "breakout":
        assert "breakout_allowed_volatile" in reasons


def test_markdown_contains_decision_block():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "fixture.jsonl"
        _write_jsonl(path, [_record()])
        markdown = zero.render_markdown_report(zero.build_report([path], ["variant-d"]))
    assert "Batch 3K Decision" in markdown
    assert "Production change authorized: false" in markdown
    assert "Runtime/default config change: not performed" in markdown


if __name__ == "__main__":
    tests = [
        test_safe_atr_pct_handles_missing_or_zero_close,
        test_bucket_classifiers,
        test_finds_baseline_direct_blocks_and_builds_report,
        test_classifies_variant_d_confidence_and_atr_reasons,
        test_classifies_variant_b_breakout_reason_when_selected,
        test_markdown_contains_decision_block,
    ]
    for test in tests:
        test()
    print(f"PASS {len(tests)} zero-block review tests")

#!/usr/bin/env python3
"""Test Phase 6E: Replay Parameter Sweep — variant generation, scoring, reporting."""
import json
import sys
import tempfile
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.replay_parameter_sweep import (
    VARIANTS, deep_merge, score_variant,
    summarize_simulation, summarize_replay,
    write_json_report, write_md_report,
)


def test_variants_defined():
    expected = ["baseline", "tech_heavy", "deriv_heavy", "lower_thresholds", "higher_thresholds", "more_aggressive", "more_conservative"]
    for name in expected:
        assert name in VARIANTS, f"missing variant: {name}"
    assert VARIANTS["baseline"] == {}, f"baseline should be empty override, got: {VARIANTS['baseline']}"
    print("PASS test_variants_defined")


def test_deep_merge_basic():
    base = {"a": 1, "b": {"c": 2, "d": 3}}
    override = {"b": {"c": 20}}
    result = deep_merge(base, override)
    assert result["a"] == 1
    assert result["b"]["c"] == 20
    assert result["b"]["d"] == 3
    print("PASS test_deep_merge_basic")


def test_deep_merge_nested():
    base = {
        "analyst_weights": {
            "full": {"technical": 0.75, "derivatives": 0.15},
            "direction_thresholds": {"bullish_above": 0.57, "bearish_below": 0.43}
        }
    }
    override = {
        "analyst_weights": {
            "direction_thresholds": {"bullish_above": 0.60}
        }
    }
    result = deep_merge(base, override)
    assert result["analyst_weights"]["full"]["technical"] == 0.75
    assert result["analyst_weights"]["full"]["derivatives"] == 0.15
    assert result["analyst_weights"]["direction_thresholds"]["bullish_above"] == 0.60
    assert result["analyst_weights"]["direction_thresholds"]["bearish_below"] == 0.43
    print("PASS test_deep_merge_nested")


def test_deep_merge_empty_override():
    base = {"a": 1}
    result = deep_merge(base, {})
    assert result == {"a": 1}
    result2 = deep_merge({}, {"a": 2})
    assert result2 == {"a": 2}
    print("PASS test_deep_merge_empty_override")


def test_score_variant_no_penalty():
    sim = {"simulated_trades": 10, "total_pnl_pct": 2.0, "avg_pnl_pct": 0.2, "win_rate": 0.6}
    s = score_variant(sim)
    assert abs(s - (2.0 + 0.4 + 3.0)) < 0.001
    print("PASS test_score_variant_no_penalty")


def test_score_variant_mild_penalty():
    sim = {"simulated_trades": 4, "total_pnl_pct": 2.0, "avg_pnl_pct": 0.5, "win_rate": 0.5}
    s = score_variant(sim)
    assert abs(s - (2.0 + 1.0 + 2.5 - 0.25)) < 0.001
    print("PASS test_score_variant_mild_penalty")


def test_score_variant_severe_penalty():
    sim = {"simulated_trades": 1, "total_pnl_pct": 5.0, "avg_pnl_pct": 5.0, "win_rate": 1.0}
    s = score_variant(sim)
    assert abs(s - (5.0 + 10.0 + 5.0 - 0.5)) < 0.001
    print("PASS test_score_variant_severe_penalty")


def test_summarize_replay_empty():
    summary = summarize_replay([])
    assert summary["signals"] == 0
    assert summary["hold_ratio"] == 0.0
    print("PASS test_summarize_replay_empty")


def test_summarize_replay_mixed():
    records = [
        {"final_signal": {"direction": "bullish", "confidence": 0.8,
                          "analysis": {"trader": {"action": "BUY"}}}},
        {"final_signal": {"direction": "bearish", "confidence": 0.7,
                          "analysis": {"trader": {"action": "SELL"}}}},
        {"final_signal": {"direction": "neutral", "confidence": 0.5,
                          "analysis": {"trader": {"action": "HOLD"}}}},
        {"final_signal": {"direction": "neutral", "confidence": 0.55,
                          "analysis": {"trader": {"action": "HOLD"}}}},
    ]
    summary = summarize_replay(records)
    assert summary["signals"] == 4
    assert summary["by_action"]["HOLD"] == 2
    assert summary["by_action"]["BUY"] == 1
    assert summary["by_action"]["SELL"] == 1
    assert summary["hold_ratio"] == 0.5
    assert abs(summary["avg_confidence"] - 0.6375) < 0.001
    print("PASS test_summarize_replay_mixed")


def test_summarize_simulation_format():
    from collections import Counter
    stats = {
        "simulated_trades": 5,
        "wins": 3,
        "losses": 2,
        "breakeven": 0,
        "pnl_pcts": [0.02, -0.01, 0.03, -0.02, 0.01],
        "hold_durations": [10, 20, 30, 40, 50],
        "exit_reasons": Counter({"opposite_signal": 4, "end_of_data": 1}),
    }
    summary = summarize_simulation([], stats)
    assert summary["trades"] == 5
    assert summary["wins"] == 3
    assert summary["losses"] == 2
    assert summary["win_rate"] == 0.6
    assert abs(summary["total_pnl_pct"] - 0.03) < 0.001
    assert summary["max_pnl_pct"] == 0.03
    assert summary["min_pnl_pct"] == -0.02
    assert summary["avg_hold_candles"] == 30.0
    assert summary["exit_reasons"]["opposite_signal"] == 4
    print("PASS test_summarize_simulation_format")


def test_write_json_report():
    rows = [
        {
            "rank": 1, "variant": "baseline",
            "replay": {"signals": 10, "by_action": {"HOLD": 6, "BUY": 2, "SELL": 2}, "hold_ratio": 0.6, "avg_confidence": 0.7},
            "simulation": {"trades": 2, "wins": 2, "losses": 0, "win_rate": 1.0, "total_pnl_pct": 0.5, "avg_pnl_pct": 0.25, "max_pnl_pct": 0.3, "min_pnl_pct": 0.2, "avg_hold_candles": 5.0},
            "score": 1.0,
        }
    ]
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "report.json")
        write_json_report(rows, Path(tmp), path)
        with open(path) as f:
            data = json.load(f)
    assert data["variants"] == list(VARIANTS.keys())
    assert data["results"][0]["variant"] == "baseline"
    assert data["results"][0]["score"] == 1.0
    print("PASS test_write_json_report")


def test_write_md_report():
    rows = [
        {
            "rank": 1, "variant": "baseline",
            "replay": {"signals": 10, "by_action": {"HOLD": 6, "BUY": 2, "SELL": 2}, "hold_ratio": 0.6, "avg_confidence": 0.7, "by_direction": {}},
            "simulation": {"trades": 2, "wins": 2, "losses": 0, "win_rate": 1.0, "total_pnl_pct": 0.5, "avg_pnl_pct": 0.25, "max_pnl_pct": 0.3, "min_pnl_pct": 0.2, "avg_hold_candles": 5.0},
            "score": 1.0,
        }
    ]
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "report.md")
        write_md_report(rows, path)
        with open(path) as f:
            content = f.read()
    assert "# Replay Parameter Sweep Report" in content
    assert "baseline" in content
    assert "Best Variant" in content
    assert "Do NOT auto-apply" in content
    print("PASS test_write_md_report")


def test_baseline_does_not_mutate_thresholds():
    """baseline variant must not change direction_thresholds."""
    base = {
        "analyst_weights": {
            "direction_thresholds": {
                "bullish_above": 0.57,
                "bearish_below": 0.43,
                "hold_confidence_cap": 0.55,
            }
        }
    }
    merged = deep_merge(base, VARIANTS["baseline"])
    assert merged["analyst_weights"]["direction_thresholds"]["bullish_above"] == 0.57
    assert merged["analyst_weights"]["direction_thresholds"]["bearish_below"] == 0.43
    print("PASS test_baseline_does_not_mutate_thresholds")


def test_variants_have_distinct_overrides():
    """Non-baseline variants should have meaningful override differences."""
    for name in ["tech_heavy", "deriv_heavy", "lower_thresholds", "higher_thresholds"]:
        assert VARIANTS[name] != {}, f"{name} variant should not be empty"
    print("PASS test_variants_have_distinct_overrides")


if __name__ == "__main__":
    test_variants_defined()
    test_deep_merge_basic()
    test_deep_merge_nested()
    test_deep_merge_empty_override()
    test_score_variant_no_penalty()
    test_score_variant_mild_penalty()
    test_score_variant_severe_penalty()
    test_summarize_replay_empty()
    test_summarize_replay_mixed()
    test_summarize_simulation_format()
    test_write_json_report()
    test_write_md_report()
    test_baseline_does_not_mutate_thresholds()
    test_variants_have_distinct_overrides()
    print("\nAll replay parameter sweep tests passed.")

#!/usr/bin/env python3
"""Test Phase 6G: Backtest Report Dashboard."""
import json
import sys
import tempfile
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.generate_backtest_dashboard import (
    load_json, load_jsonl, summarize_replay, summarize_trades,
    generate_warnings, generate_recommendations, render_markdown,
    build_dashboard, DEFAULT_CONFIG,
)


def test_load_json_missing():
    assert load_json(Path("/nonexistent.json")) is None
    print("PASS test_load_json_missing")


def test_load_jsonl_empty():
    assert load_jsonl(Path("/nonexistent.jsonl")) == []
    print("PASS test_load_jsonl_empty")


def test_load_jsonl_valid(tmp_records):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for r in tmp_records:
            f.write(json.dumps(r) + "\n")
        path = Path(f.name)
    loaded = load_jsonl(path)
    assert len(loaded) == len(tmp_records)
    path.unlink()
    print("PASS test_load_jsonl_valid")


def test_summarize_replay_empty():
    summary = summarize_replay([])
    assert summary["signals"] == 0
    assert summary["hold_ratio"] == 0.0
    print("PASS test_summarize_replay_empty")


def test_summarize_replay_mixed():
    records = [
        {"final_signal": {"direction": "bullish", "confidence": 0.8,
                          "analysis": {"trader": {"action": "BUY"}}}},
        {"final_signal": {"direction": "neutral", "confidence": 0.5,
                          "analysis": {"trader": {"action": "HOLD"}}}},
        {"final_signal": {"direction": "neutral", "confidence": 0.55,
                          "analysis": {"trader": {"action": "HOLD"}}}},
    ]
    summary = summarize_replay(records)
    assert summary["signals"] == 3
    assert summary["by_action"]["HOLD"] == 2
    assert abs(summary["hold_ratio"] - 2/3) < 0.001
    print("PASS test_summarize_replay_mixed")


def test_summarize_trades_empty():
    assert summarize_trades([]) == {"count": 0, "by_symbol": {}, "by_side": {}, "by_exit_reason": {}}
    print("PASS test_summarize_trades_empty")


def test_summarize_trades_mixed():
    trades = [
        {"symbol": "BTCUSDT", "side": "LONG", "exit_reason": "take_profit"},
        {"symbol": "BTCUSDT", "side": "SHORT", "exit_reason": "stop_loss"},
        {"symbol": "ETHUSDT", "side": "LONG", "exit_reason": "opposite_signal"},
    ]
    summary = summarize_trades(trades)
    assert summary["count"] == 3
    assert summary["by_symbol"]["BTCUSDT"] == 2
    assert summary["by_side"]["LONG"] == 2
    assert summary["by_exit_reason"]["take_profit"] == 1
    print("PASS test_summarize_trades_mixed")


def test_warning_low_sample_size():
    rep = {"signals": 50, "by_action": {"HOLD": 30, "BUY": 10, "SELL": 10}, "hold_ratio": 0.6, "avg_confidence": 0.7}
    sim = {"simulated_trades": 3, "total_pnl_pct": 0.0, "avg_hold_candles": 10, "win_rate": 0.5, "wins": 1, "losses": 1, "breakeven": 1, "avg_pnl_pct": 0.0, "max_pnl_pct": 0, "min_pnl_pct": 0, "exit_reasons": {}}
    trades = {"count": 3, "by_symbol": {}, "by_side": {"LONG": 3}, "by_exit_reason": {}}
    warnings = generate_warnings(rep, sim, trades, DEFAULT_CONFIG)
    assert any("small" in w.lower() for w in warnings)
    print("PASS test_warning_low_sample_size")


def test_warning_high_hold_ratio():
    rep = {"signals": 100, "by_action": {"HOLD": 90, "BUY": 5, "SELL": 5}, "hold_ratio": 0.90, "avg_confidence": 0.7}
    sim = {"simulated_trades": 10, "total_pnl_pct": 0.0, "avg_hold_candles": 10, "win_rate": 0.5, "wins": 5, "losses": 5, "breakeven": 0, "avg_pnl_pct": 0.0, "max_pnl_pct": 0, "min_pnl_pct": 0, "exit_reasons": {}}
    trades = {"count": 10, "by_symbol": {}, "by_side": {}, "by_exit_reason": {}}
    warnings = generate_warnings(rep, sim, trades, DEFAULT_CONFIG)
    assert any("hold ratio" in w.lower() for w in warnings)
    print("PASS test_warning_high_hold_ratio")


def test_warning_negative_pnl():
    rep = {"signals": 100, "by_action": {"BUY": 50, "SELL": 50}, "hold_ratio": 0.0, "avg_confidence": 0.7}
    sim = {"simulated_trades": 15, "total_pnl_pct": -5.0, "avg_hold_candles": 10, "win_rate": 0.3, "wins": 4, "losses": 11, "breakeven": 0, "avg_pnl_pct": -0.3, "max_pnl_pct": 0.1, "min_pnl_pct": -0.5, "exit_reasons": {}}
    trades = {"count": 15, "by_symbol": {}, "by_side": {}, "by_exit_reason": {}}
    warnings = generate_warnings(rep, sim, trades, DEFAULT_CONFIG)
    assert any("negative" in w.lower() for w in warnings)
    print("PASS test_warning_negative_pnl")


def test_warning_side_bias():
    rep = {"signals": 100, "by_action": {"SELL": 100}, "hold_ratio": 0.0, "avg_confidence": 0.7}
    sim = {"simulated_trades": 15, "total_pnl_pct": 0.0, "avg_hold_candles": 10, "win_rate": 0.5, "wins": 8, "losses": 7, "breakeven": 0, "avg_pnl_pct": 0.0, "max_pnl_pct": 0, "min_pnl_pct": 0, "exit_reasons": {}}
    trades = {"count": 15, "by_symbol": {}, "by_side": {"SHORT": 15}, "by_exit_reason": {}}
    warnings = generate_warnings(rep, sim, trades, DEFAULT_CONFIG)
    assert any("side bias" in w.lower() for w in warnings)
    print("PASS test_warning_side_bias")


def test_warning_stale_positions():
    rep = {"signals": 100, "by_action": {"BUY": 50, "SELL": 50}, "hold_ratio": 0.0, "avg_confidence": 0.7}
    sim = {"simulated_trades": 15, "total_pnl_pct": 0.0, "avg_hold_candles": 100, "win_rate": 0.5, "wins": 8, "losses": 7, "breakeven": 0, "avg_pnl_pct": 0.0, "max_pnl_pct": 0, "min_pnl_pct": 0, "exit_reasons": {}}
    trades = {"count": 15, "by_symbol": {}, "by_side": {}, "by_exit_reason": {}}
    warnings = generate_warnings(rep, sim, trades, DEFAULT_CONFIG)
    assert any("stale" in w.lower() for w in warnings)
    print("PASS test_warning_stale_positions")


def test_warning_sl_tp_imbalance():
    rep = {"signals": 100, "by_action": {"BUY": 50, "SELL": 50}, "hold_ratio": 0.0, "avg_confidence": 0.7}
    sim = {"simulated_trades": 15, "total_pnl_pct": 0.0, "avg_hold_candles": 10, "win_rate": 0.5, "wins": 5, "losses": 10, "breakeven": 0, "avg_pnl_pct": 0.0, "max_pnl_pct": 0, "min_pnl_pct": 0, "exit_reasons": {}}
    trades = {"count": 15, "by_symbol": {}, "by_side": {}, "by_exit_reason": {"stop_loss": 10, "take_profit": 5}}
    warnings = generate_warnings(rep, sim, trades, DEFAULT_CONFIG)
    assert any("imbalance" in w.lower() for w in warnings)
    print("PASS test_warning_sl_tp_imbalance")


def test_no_warnings_clean():
    rep = {"signals": 100, "by_action": {"HOLD": 50, "BUY": 25, "SELL": 25}, "hold_ratio": 0.5, "avg_confidence": 0.7}
    sim = {"simulated_trades": 20, "total_pnl_pct": 2.0, "avg_hold_candles": 10, "win_rate": 0.6, "wins": 12, "losses": 8, "breakeven": 0, "avg_pnl_pct": 0.1, "max_pnl_pct": 0.3, "min_pnl_pct": -0.1, "exit_reasons": {}}
    trades = {"count": 20, "by_symbol": {}, "by_side": {"LONG": 11, "SHORT": 9}, "by_exit_reason": {"stop_loss": 4, "take_profit": 5, "opposite_signal": 6}}
    warnings = generate_warnings(rep, sim, trades, DEFAULT_CONFIG)
    assert len(warnings) == 0
    print("PASS test_no_warnings_clean")


def test_build_dashboard_empty():
    dashboard = build_dashboard([], None, [], None, None, DEFAULT_CONFIG)
    assert dashboard["replay"]["signals"] == 0
    assert dashboard["simulation"] == {}
    assert dashboard["sweep_top"] == []
    assert dashboard["replay_sweep_top"] == []
    print("PASS test_build_dashboard_empty")


def test_build_dashboard_with_data():
    rep_records = [
        {"final_signal": {"direction": "bullish", "confidence": 0.8,
                          "analysis": {"trader": {"action": "BUY"}}}},
        {"final_signal": {"direction": "bearish", "confidence": 0.7,
                          "analysis": {"trader": {"action": "SELL"}}}},
    ]
    sim = {"simulated_trades": 2, "wins": 2, "losses": 0, "breakeven": 0, "win_rate": 1.0,
           "total_pnl_pct": 0.5, "avg_pnl_pct": 0.25, "max_pnl_pct": 0.3, "min_pnl_pct": 0.2,
           "avg_hold_candles": 5.0, "exit_reasons": {"opposite_signal": 2}}
    trades = [
        {"symbol": "BTCUSDT", "side": "LONG", "exit_reason": "opposite_signal"},
        {"symbol": "ETHUSDT", "side": "SHORT", "exit_reason": "opposite_signal"},
    ]
    dashboard = build_dashboard(rep_records, sim, trades, None, None, DEFAULT_CONFIG)
    assert dashboard["replay"]["signals"] == 2
    assert dashboard["simulation"]["simulated_trades"] == 2
    assert dashboard["trades"]["count"] == 2
    print("PASS test_build_dashboard_with_data")


def test_render_markdown_minimal():
    dashboard = {
        "generated_at": "2026-06-08T12:00:00",
        "replay": {"signals": 0, "by_action": {}, "by_direction": {}, "hold_ratio": 0.0, "avg_confidence": 0.0},
        "simulation": {},
        "trades": {"count": 0, "by_symbol": {}, "by_side": {}, "by_exit_reason": {}},
        "warnings": [],
        "recommendations": ["Run more tests."],
        "sweep_top": [],
        "replay_sweep_top": [],
    }
    md = render_markdown(dashboard, DEFAULT_CONFIG)
    assert "# Backtest Report Dashboard" in md
    assert "## Executive Summary" in md
    assert "## Diagnostics / Warnings" in md
    assert "## Signal Distribution" in md
    assert "## Simulation Performance" in md
    assert "## Recommendations" in md
    assert "Run more tests." in md
    print("PASS test_render_markdown_minimal")


def test_render_markdown_with_sections():
    dashboard = {
        "generated_at": "2026-06-08T12:00:00",
        "replay": {"signals": 10, "by_action": {"BUY": 5, "SELL": 5}, "by_direction": {"bullish": 5, "bearish": 5}, "hold_ratio": 0.0, "avg_confidence": 0.8},
        "simulation": {"simulated_trades": 10, "wins": 6, "losses": 4, "breakeven": 0, "win_rate": 0.6,
                      "total_pnl_pct": 1.0, "avg_pnl_pct": 0.1, "max_pnl_pct": 0.2, "min_pnl_pct": -0.1,
                      "avg_hold_candles": 24.0, "exit_reasons": {"take_profit": 4, "stop_loss": 3, "opposite_signal": 3}},
        "trades": {"count": 10, "by_symbol": {"BTCUSDT": 5, "ETHUSDT": 5},
                  "by_side": {"LONG": 6, "SHORT": 4}, "by_exit_reason": {"take_profit": 4}},
        "warnings": ["⚠️ Test warning"],
        "recommendations": ["No changes needed."],
        "sweep_top": [
            {"rank": 1, "min_confidence": 0.55, "trades": 10, "win_rate": 0.6, "total_pnl_pct": 1.0, "score": 2.5},
        ],
        "replay_sweep_top": [
            {"rank": 1, "variant": "baseline", "replay": {"hold_ratio": 0.5},
             "simulation": {"trades": 10, "win_rate": 0.6, "total_pnl_pct": 1.0}, "score": 2.5},
        ],
        "sweep_best": {"min_confidence": 0.55, "score": 2.5},
        "replay_sweep_best": {"variant": "baseline", "score": 2.5},
    }
    md = render_markdown(dashboard, DEFAULT_CONFIG)
    assert "Symbol Breakdown" in md
    assert "Side Bias" in md
    assert "Parameter Sweep Top 3" in md
    assert "Replay Sweep Top Variants" in md
    assert "Test warning" in md
    assert "BTCUSDT" in md
    assert "LONG" in md
    assert "baseline" in md
    print("PASS test_render_markdown_with_sections")


def test_recommendations_small_sample():
    dashboard = {
        "replay": {"hold_ratio": 0.5},
        "simulation": {"simulated_trades": 3, "total_pnl_pct": 0.0},
        "trades": {"by_side": {"LONG": 3}},
        "warnings": [],
    }
    recs = generate_recommendations(dashboard)
    assert any("sample size" in r.lower() for r in recs)
    print("PASS test_recommendations_small_sample")


def test_recommendations_negative_pnl():
    dashboard = {
        "replay": {"hold_ratio": 0.5},
        "simulation": {"simulated_trades": 20, "total_pnl_pct": -2.0},
        "trades": {"by_side": {}},
        "warnings": [],
    }
    recs = generate_recommendations(dashboard)
    assert any("negative" in r.lower() or "sweep" in r.lower() for r in recs)
    print("PASS test_recommendations_negative_pnl")


def test_recommendations_no_sweep_data():
    dashboard = {
        "replay": {"hold_ratio": 0.5},
        "simulation": {"simulated_trades": 20, "total_pnl_pct": 2.0},
        "trades": {"by_side": {}},
        "warnings": [],
    }
    recs = generate_recommendations(dashboard)
    assert any("sweep" in r.lower() for r in recs)
    print("PASS test_recommendations_no_sweep_data")


def test_recommendations_side_bias():
    dashboard = {
        "replay": {"hold_ratio": 0.5},
        "simulation": {"simulated_trades": 20, "total_pnl_pct": 2.0},
        "trades": {"by_side": {"SHORT": 20}},
        "warnings": [],
    }
    recs = generate_recommendations(dashboard)
    assert any("bias" in r.lower() or "suppressed" in r.lower() for r in recs)
    print("PASS test_recommendations_side_bias")


def test_recommendations_hold_heavy():
    dashboard = {
        "replay": {"hold_ratio": 0.9},
        "simulation": {"simulated_trades": 5, "total_pnl_pct": 0.0},
        "trades": {"by_side": {}},
        "warnings": [],
    }
    recs = generate_recommendations(dashboard)
    assert any("hold ratio" in r.lower() or "conservative" in r.lower() for r in recs)
    print("PASS test_recommendations_hold_heavy")


def test_recommendations_clean_run():
    dashboard = {
        "replay": {"hold_ratio": 0.5},
        "simulation": {"simulated_trades": 20, "total_pnl_pct": 2.0},
        "trades": {"by_side": {"LONG": 10, "SHORT": 10}},
        "warnings": [],
        "sweep_top": [{"rank": 1}],
        "replay_sweep_top": [{"rank": 1}],
    }
    recs = generate_recommendations(dashboard)
    assert any("no major issues" in r.lower() for r in recs)
    print("PASS test_recommendations_clean_run")


if __name__ == "__main__":
    tmp_records = [
        {"final_signal": {"direction": "bullish", "confidence": 0.8,
                          "analysis": {"trader": {"action": "BUY"}}}}
    ]
    test_load_json_missing()
    test_load_jsonl_empty()
    test_load_jsonl_valid(tmp_records)
    test_summarize_replay_empty()
    test_summarize_replay_mixed()
    test_summarize_trades_empty()
    test_summarize_trades_mixed()
    test_warning_low_sample_size()
    test_warning_high_hold_ratio()
    test_warning_negative_pnl()
    test_warning_side_bias()
    test_warning_stale_positions()
    test_warning_sl_tp_imbalance()
    test_no_warnings_clean()
    test_build_dashboard_empty()
    test_build_dashboard_with_data()
    test_render_markdown_minimal()
    test_render_markdown_with_sections()
    test_recommendations_small_sample()
    test_recommendations_negative_pnl()
    test_recommendations_no_sweep_data()
    test_recommendations_side_bias()
    test_recommendations_hold_heavy()
    test_recommendations_clean_run()
    print("\nAll backtest dashboard tests passed.")

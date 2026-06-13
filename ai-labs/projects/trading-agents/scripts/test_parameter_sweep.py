#!/usr/bin/env python3
"""Test Phase 6D: Parameter Sweep logic."""
import json
import sys
import tempfile
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.parameter_sweep import (
    generate_sweep_configs, score_result, run_sweep,
    write_json_report, write_md_report,
)


def build_record(symbol, action, direction, confidence, last_close, candle_ts):
    return {
        "timestamp": "2026-06-08T12:00:00",
        "symbol": symbol,
        "final_signal": {
            "direction": direction,
            "confidence": confidence,
            "analysis": {"trader": {"action": action}},
        },
        "market_snapshot": {
            "last_close": last_close,
            "candle_timestamp": candle_ts,
        },
    }


def synthetic_replay():
    """Build a small replay with mixed signals and a few trades per symbol."""
    return [
        build_record("BTCUSDT", "BUY", "bullish", 0.85, 50000, 1000),
        build_record("BTCUSDT", "SELL", "bearish", 0.85, 51000, 2000),
        build_record("BTCUSDT", "BUY", "bullish", 0.85, 50500, 3000),
        build_record("BTCUSDT", "SELL", "bearish", 0.85, 51500, 4000),
        build_record("BTCUSDT", "BUY", "bullish", 0.85, 51000, 5000),
        build_record("BTCUSDT", "SELL", "bearish", 0.85, 52000, 6000),
        build_record("ETHUSDT", "BUY", "bullish", 0.70, 3000, 1100),
        build_record("ETHUSDT", "SELL", "bearish", 0.70, 2900, 2100),
        build_record("ETHUSDT", "BUY", "bullish", 0.70, 2950, 3100),
        build_record("ETHUSDT", "SELL", "bearish", 0.70, 2850, 4100),
    ]


def test_generate_sweep_configs_count():
    sweep_cfg = {
        "min_confidence_values": [0.55, 0.60, 0.70],
        "fee_pct_values": [0.001, 0.002],
        "slippage_pct_values": [0.0005],
    }
    base = {"simulation": {"min_confidence": 0.55}}
    configs = generate_sweep_configs(sweep_cfg, base)
    assert len(configs) == 3 * 2 * 1
    assert configs[0]["min_confidence"] == 0.55
    assert configs[0]["fee_pct"] == 0.001
    assert configs[0]["slippage_pct"] == 0.0005
    assert configs[0]["config"]["simulation"]["min_confidence"] == 0.55
    print("PASS test_generate_sweep_configs_count")


def test_generate_sweep_configs_default():
    sweep_cfg = {}
    base = {"simulation": {"min_confidence": 0.55}}
    configs = generate_sweep_configs(sweep_cfg, base)
    assert len(configs) == 1
    assert configs[0]["min_confidence"] == 0.55
    assert configs[0]["fee_pct"] == 0.001
    print("PASS test_generate_sweep_configs_default")


def test_score_result_no_penalty():
    sweep_cfg = {"min_trades_no_penalty": 5, "min_trades_mild_penalty": 3}
    summary = {"simulated_trades": 10, "total_pnl_pct": 2.0, "avg_pnl_pct": 0.2, "win_rate": 0.6}
    s = score_result(summary, sweep_cfg)
    assert abs(s - (2.0 + 0.4 + 3.0)) < 0.001, f"unexpected score: {s}"
    print("PASS test_score_result_no_penalty")


def test_score_result_mild_penalty():
    sweep_cfg = {"min_trades_no_penalty": 5, "min_trades_mild_penalty": 3}
    summary = {"simulated_trades": 4, "total_pnl_pct": 2.0, "avg_pnl_pct": 0.5, "win_rate": 0.5}
    s = score_result(summary, sweep_cfg)
    assert abs(s - (2.0 + 1.0 + 2.5 - 0.25)) < 0.001, f"unexpected score: {s}"
    print("PASS test_score_result_mild_penalty")


def test_score_result_severe_penalty():
    sweep_cfg = {"min_trades_no_penalty": 5, "min_trades_mild_penalty": 3}
    summary = {"simulated_trades": 1, "total_pnl_pct": 5.0, "avg_pnl_pct": 5.0, "win_rate": 1.0}
    s = score_result(summary, sweep_cfg)
    assert abs(s - (5.0 + 10.0 + 5.0 - 0.5)) < 0.001, f"unexpected score: {s}"
    print("PASS test_score_result_severe_penalty")


def test_run_sweep_ranks_best_first():
    records = synthetic_replay()
    sweep_cfg = {
        "min_confidence_values": [0.55, 0.65, 0.75, 0.85],
        "fee_pct_values": [0.001],
        "slippage_pct_values": [0.0005],
        "min_trades_no_penalty": 5,
        "min_trades_mild_penalty": 3,
    }
    base = {"simulation": {"fee_pct": 0.001, "slippage_pct": 0.0005}}
    rows = run_sweep(records, sweep_cfg, base)
    assert len(rows) == 4
    for i, r in enumerate(rows, 1):
        assert r["rank"] == i
    scores = [r["score"] for r in rows]
    assert scores == sorted(scores, reverse=True), f"results not sorted by score: {scores}"
    print("PASS test_run_sweep_ranks_best_first")


def test_run_sweep_low_trade_count_penalized():
    records = synthetic_replay()
    sweep_cfg = {
        "min_confidence_values": [0.55, 0.99],
        "fee_pct_values": [0.001],
        "slippage_pct_values": [0.0005],
        "min_trades_no_penalty": 5,
        "min_trades_mild_penalty": 3,
    }
    base = {"simulation": {"fee_pct": 0.001, "slippage_pct": 0.0005}}
    rows = run_sweep(records, sweep_cfg, base)
    low_conf = next(r for r in rows if r["min_confidence"] == 0.55)
    high_conf = next(r for r in rows if r["min_confidence"] == 0.99)
    assert high_conf["trades"] <= 2, f"high conf should yield few trades: {high_conf}"
    assert low_conf["trades"] >= 3, f"low conf should yield enough trades: {low_conf}"
    assert high_conf["score"] < low_conf["score"], f"high conf should score lower due to penalty: high={high_conf['score']} low={low_conf['score']}"
    print("PASS test_run_sweep_low_trade_count_penalized")


def test_run_sweep_empty_replay():
    sweep_cfg = {
        "min_confidence_values": [0.55, 0.60],
        "fee_pct_values": [0.001],
        "slippage_pct_values": [0.0005],
    }
    base = {"simulation": {}}
    rows = run_sweep([], sweep_cfg, base)
    assert len(rows) == 2
    for r in rows:
        assert r["trades"] == 0
    print("PASS test_run_sweep_empty_replay")


def test_write_json_report():
    sweep_cfg = {"min_confidence_values": [0.55], "fee_pct_values": [0.001], "slippage_pct_values": [0.0005]}
    rows = [
        {
            "rank": 1, "min_confidence": 0.55, "fee_pct": 0.001, "slippage_pct": 0.0005,
            "trades": 2, "wins": 2, "losses": 0, "win_rate": 1.0,
            "total_pnl_pct": 1.0, "avg_pnl_pct": 0.5, "max_pnl_pct": 0.6, "min_pnl_pct": 0.4,
            "avg_hold_candles": 1.0, "score": 1.5,
        }
    ]
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "report.json")
        write_json_report(rows, sweep_cfg, "test.jsonl", path)
        with open(path) as f:
            data = json.load(f)
    assert data["combinations_run"] == 1
    assert data["source_replay"] == "test.jsonl"
    assert data["results"][0]["min_confidence"] == 0.55
    print("PASS test_write_json_report")


def test_write_md_report():
    rows = [
        {
            "rank": 1, "min_confidence": 0.55, "fee_pct": 0.001, "slippage_pct": 0.0005,
            "trades": 2, "wins": 2, "losses": 0, "win_rate": 1.0,
            "total_pnl_pct": 1.0, "avg_pnl_pct": 0.5, "max_pnl_pct": 0.6, "min_pnl_pct": 0.4,
            "avg_hold_candles": 1.0, "score": 1.5,
        }
    ]
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "report.md")
        write_md_report(rows, "test.jsonl", path)
        with open(path) as f:
            content = f.read()
    assert "# Parameter Sweep Report" in content
    assert "Best Config" in content
    assert "min_confidence" in content
    assert "Do NOT auto-apply" in content
    print("PASS test_write_md_report")


if __name__ == "__main__":
    test_generate_sweep_configs_count()
    test_generate_sweep_configs_default()
    test_score_result_no_penalty()
    test_score_result_mild_penalty()
    test_score_result_severe_penalty()
    test_run_sweep_ranks_best_first()
    test_run_sweep_low_trade_count_penalized()
    test_run_sweep_empty_replay()
    test_write_json_report()
    test_write_md_report()
    print("\nAll parameter sweep tests passed.")

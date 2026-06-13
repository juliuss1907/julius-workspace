#!/usr/bin/env python3
"""Test Phase 6C + 6F: Trade Simulation logic with SL/TP support."""
import json
import sys
import tempfile
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.simulate_trades import (
    simulate, load_records, extract_action, extract_confidence,
    extract_price, extract_timestamp, avg,
    compute_sl_tp, check_candle_exit, compute_mae_mfe,
    load_ohlcv_from_db,
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


def build_candle(timestamp, open_, high, low, close, volume=100.0):
    return {
        "timestamp": timestamp,
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    }


# ============================================================================
# Phase 6C tests (signal-only)
# ============================================================================

def test_extract_action():
    rec = build_record("BTCUSDT", "BUY", "bullish", 0.75, 50000, 1000)
    assert extract_action(rec) == "BUY"
    rec2 = {"final_signal": {"metadata": {"final_action": "SELL"}}}
    assert extract_action(rec2) == "SELL"
    rec3 = {}
    assert extract_action(rec3) == "HOLD"
    print("PASS test_extract_action")


def test_extract_confidence():
    rec = build_record("BTCUSDT", "BUY", "bullish", 0.75, 50000, 1000)
    assert extract_confidence(rec) == 0.75
    assert extract_confidence({}) == 0.0
    print("PASS test_extract_confidence")


def test_extract_price():
    rec = build_record("BTCUSDT", "BUY", "bullish", 0.75, 50000, 1000)
    assert extract_price(rec) == 50000
    assert extract_price({}) == 0
    print("PASS test_extract_price")


def test_extract_timestamp():
    rec = build_record("BTCUSDT", "BUY", "bullish", 0.75, 50000, 1717000000)
    assert extract_timestamp(rec) == 1717000000
    print("PASS test_extract_timestamp")


def test_basic_buy_sell_flow():
    records = [
        build_record("BTCUSDT", "BUY", "bullish", 0.80, 50000, 1000),
        build_record("BTCUSDT", "HOLD", "neutral", 0.55, 50100, 2000),
        build_record("BTCUSDT", "SELL", "bearish", 0.80, 51000, 3000),
    ]
    config = {"simulation": {"fee_pct": 0.0, "slippage_pct": 0.0, "min_confidence": 0.55}}
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "trades.jsonl"
        summary = Path(tmp) / "summary.json"
        trades, stats = simulate(records, config, str(out), str(summary))
    assert len(trades) == 1
    t = trades[0]
    assert t["symbol"] == "BTCUSDT"
    assert t["side"] == "LONG"
    assert t["entry_price"] == 50000
    assert t["exit_price"] == 51000
    assert t["pnl_pct"] > 0.01
    assert t["exit_reason"] == "opposite_signal"
    assert "stop_loss" not in t
    assert "max_adverse_excursion_pct" not in t
    print("PASS test_basic_buy_sell_flow")


def test_basic_sell_buy_flow():
    records = [
        build_record("ETHUSDT", "SELL", "bearish", 0.80, 3000, 1000),
        build_record("ETHUSDT", "BUY", "bullish", 0.80, 2900, 2000),
    ]
    config = {"simulation": {"fee_pct": 0.0, "slippage_pct": 0.0, "min_confidence": 0.55}}
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "trades.jsonl"
        summary = Path(tmp) / "summary.json"
        trades, stats = simulate(records, config, str(out), str(summary))
    assert len(trades) == 1
    t = trades[0]
    assert t["side"] == "SHORT"
    assert t["pnl_pct"] > 0.02
    assert t["exit_reason"] == "opposite_signal"
    print("PASS test_basic_sell_buy_flow")


def test_end_of_data_exit():
    records = [
        build_record("BTCUSDT", "BUY", "bullish", 0.80, 50000, 1000),
        build_record("BTCUSDT", "HOLD", "neutral", 0.55, 50200, 2000),
    ]
    config = {"simulation": {"fee_pct": 0.0, "slippage_pct": 0.0, "min_confidence": 0.55}}
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "trades.jsonl"
        summary = Path(tmp) / "summary.json"
        trades, stats = simulate(records, config, str(out), str(summary))
    assert len(trades) == 1
    assert trades[0]["exit_reason"] == "end_of_data"
    print("PASS test_end_of_data_exit")


def test_min_confidence_filter():
    records = [
        build_record("BTCUSDT", "BUY", "bullish", 0.50, 50000, 1000),
        build_record("BTCUSDT", "SELL", "bearish", 0.50, 51000, 2000),
    ]
    config = {"simulation": {"fee_pct": 0.0, "slippage_pct": 0.0, "min_confidence": 0.55}}
    with tempfile.TemporaryDirectory() as tmp:
        trades, _ = simulate(records, config, "/tmp/out.jsonl", "/tmp/sum.json")
    assert len(trades) == 0
    print("PASS test_min_confidence_filter")


def test_duplicate_ignored():
    records = [
        build_record("BTCUSDT", "BUY", "bullish", 0.80, 50000, 1000),
        build_record("BTCUSDT", "BUY", "bullish", 0.80, 50100, 2000),
        build_record("BTCUSDT", "SELL", "bearish", 0.80, 51000, 3000),
    ]
    config = {"simulation": {"fee_pct": 0.0, "slippage_pct": 0.0, "min_confidence": 0.55}}
    with tempfile.TemporaryDirectory() as tmp:
        trades, _ = simulate(records, config, "/tmp/out.jsonl", "/tmp/sum.json")
    assert len(trades) == 1
    assert trades[0]["entry_price"] == 50000
    print("PASS test_duplicate_ignored")


def test_fees_applied():
    records = [
        build_record("BTCUSDT", "BUY", "bullish", 0.80, 50000, 1000),
        build_record("BTCUSDT", "SELL", "bearish", 0.80, 50000, 2000),
    ]
    config = {"simulation": {"fee_pct": 0.001, "slippage_pct": 0.0005, "min_confidence": 0.55}}
    with tempfile.TemporaryDirectory() as tmp:
        trades, _ = simulate(records, config, "/tmp/out.jsonl", "/tmp/sum.json")
    assert trades[0]["pnl_pct"] < 0
    print("PASS test_fees_applied")


def test_empty_replay():
    config = {"simulation": {"min_confidence": 0.55}}
    with tempfile.TemporaryDirectory() as tmp:
        trades, stats = simulate([], config, "/tmp/out.jsonl", "/tmp/sum.json")
    assert len(trades) == 0
    assert stats["simulated_trades"] == 0
    print("PASS test_empty_replay")


def test_mixed_signals():
    records = [
        build_record("BTCUSDT", "BUY", "bullish", 0.80, 50000, 1000),
        build_record("BTCUSDT", "HOLD", "neutral", 0.55, 50100, 2000),
        build_record("BTCUSDT", "SELL", "bearish", 0.80, 51000, 3000),
        build_record("BTCUSDT", "BUY", "bullish", 0.80, 50500, 4000),
    ]
    config = {"simulation": {"fee_pct": 0.0, "slippage_pct": 0.0, "min_confidence": 0.55}}
    with tempfile.TemporaryDirectory() as tmp:
        trades, _ = simulate(records, config, "/tmp/out.jsonl", "/tmp/sum.json")
    assert len(trades) == 2
    assert trades[0]["exit_reason"] == "opposite_signal"
    assert trades[1]["exit_reason"] == "end_of_data"
    print("PASS test_mixed_signals")


# ============================================================================
# Phase 6F tests (SL/TP-aware)
# ============================================================================

def test_compute_sl_tp_long():
    sl, tp = compute_sl_tp(100, "LONG", 0.03, 0.06)
    assert abs(sl - 97) < 0.001
    assert abs(tp - 106) < 0.001
    print("PASS test_compute_sl_tp_long")


def test_compute_sl_tp_short():
    sl, tp = compute_sl_tp(100, "SHORT", 0.03, 0.06)
    assert abs(sl - 103) < 0.001
    assert abs(tp - 94) < 0.001
    print("PASS test_compute_sl_tp_short")


def test_check_candle_exit_long_tp():
    candle = build_candle(2000, 100, 107, 99, 105)
    reason, px = check_candle_exit(candle, "LONG", 97, 106)
    assert reason == "take_profit"
    assert px == 106
    print("PASS test_check_candle_exit_long_tp")


def test_check_candle_exit_long_sl():
    candle = build_candle(2000, 100, 102, 96, 98)
    reason, px = check_candle_exit(candle, "LONG", 97, 106)
    assert reason == "stop_loss"
    assert px == 97
    print("PASS test_check_candle_exit_long_sl")


def test_check_candle_exit_short_tp():
    candle = build_candle(2000, 100, 102, 93, 95)
    reason, px = check_candle_exit(candle, "SHORT", 103, 94)
    assert reason == "take_profit"
    assert px == 94
    print("PASS test_check_candle_exit_short_tp")


def test_check_candle_exit_short_sl():
    candle = build_candle(2000, 100, 104, 99, 102)
    reason, px = check_candle_exit(candle, "SHORT", 103, 94)
    assert reason == "stop_loss"
    assert px == 103
    print("PASS test_check_candle_exit_short_sl")


def test_check_candle_exit_no_hit():
    candle = build_candle(2000, 100, 101, 99, 100)
    reason, px = check_candle_exit(candle, "LONG", 97, 106)
    assert reason is None
    assert px is None
    print("PASS test_check_candle_exit_no_hit")


def test_check_candle_exit_same_candle_sl_priority():
    candle = build_candle(2000, 100, 110, 90, 95)
    reason, px = check_candle_exit(candle, "LONG", 97, 106)
    assert reason == "stop_loss"
    assert px == 97
    print("PASS test_check_candle_exit_same_candle_sl_priority")


def test_check_candle_exit_same_candle_tp_priority():
    candle = build_candle(2000, 100, 110, 90, 95)
    reason, px = check_candle_exit(candle, "LONG", 97, 106, same_candle_priority="take_profit")
    assert reason == "take_profit"
    assert px == 106
    print("PASS test_check_candle_exit_same_candle_tp_priority")


def test_mae_mfe_long():
    candles = [
        build_candle(1000, 100, 105, 95, 102),
        build_candle(2000, 102, 108, 101, 106),
        build_candle(3000, 106, 112, 104, 110),
    ]
    mae, mfe = compute_mae_mfe(candles, "LONG", 100)
    assert abs(mae - (-0.05)) < 0.001
    assert abs(mfe - 0.12) < 0.001
    print("PASS test_mae_mfe_long")


def test_mae_mfe_short():
    candles = [
        build_candle(1000, 100, 105, 95, 98),
        build_candle(2000, 98, 102, 88, 90),
    ]
    mae, mfe = compute_mae_mfe(candles, "SHORT", 100)
    assert abs(mae - (-0.05)) < 0.001
    assert abs(mfe - 0.12) < 0.001
    print("PASS test_mae_mfe_short")


def _make_candle_provider(candles_by_symbol):
    """Create a fake OHLCV provider for tests."""
    def provider(symbol, start_ts, end_ts):
        candles = candles_by_symbol.get(symbol, [])
        return [c for c in candles if start_ts <= c["timestamp"] <= end_ts]
    return provider


def test_sl_tp_long_hits_tp():
    records = [
        build_record("BTCUSDT", "BUY", "bullish", 0.80, 100, 1000),
        build_record("BTCUSDT", "HOLD", "neutral", 0.55, 108, 2000),
    ]
    candles = [
        build_candle(1000, 100, 100, 100, 100),
        build_candle(2000, 100, 108, 102, 107),
    ]
    provider = _make_candle_provider({"BTCUSDT": candles})
    config = {
        "simulation": {
            "fee_pct": 0.0,
            "slippage_pct": 0.0,
            "min_confidence": 0.55,
            "use_sl_tp": True,
            "stop_loss_pct": 0.03,
            "take_profit_pct": 0.06,
            "max_hold_candles": 48,
            "same_candle_priority": "stop_loss",
        }
    }
    with tempfile.TemporaryDirectory() as tmp:
        trades, stats = simulate(records, config, "/tmp/out.jsonl", "/tmp/sum.json", ohlcv_provider=provider)
    assert len(trades) == 1
    t = trades[0]
    assert t["exit_reason"] == "take_profit"
    assert t["exit_price"] == 106
    assert t["stop_loss"] == 97
    assert t["take_profit"] == 106
    assert t["pnl_pct"] > 0.05
    assert "max_adverse_excursion_pct" in t
    assert "max_favorable_excursion_pct" in t
    print("PASS test_sl_tp_long_hits_tp")


def test_sl_tp_long_hits_sl():
    records = [
        build_record("BTCUSDT", "BUY", "bullish", 0.80, 100, 1000),
        build_record("BTCUSDT", "HOLD", "neutral", 0.55, 96, 2000),
    ]
    candles = [
        build_candle(1000, 100, 100, 100, 100),
        build_candle(2000, 100, 99, 96, 97),
    ]
    provider = _make_candle_provider({"BTCUSDT": candles})
    config = {
        "simulation": {
            "fee_pct": 0.0, "slippage_pct": 0.0, "min_confidence": 0.55,
            "use_sl_tp": True, "stop_loss_pct": 0.03, "take_profit_pct": 0.06,
            "max_hold_candles": 48, "same_candle_priority": "stop_loss",
        }
    }
    with tempfile.TemporaryDirectory() as tmp:
        trades, _ = simulate(records, config, "/tmp/out.jsonl", "/tmp/sum.json", ohlcv_provider=provider)
    assert trades[0]["exit_reason"] == "stop_loss"
    assert trades[0]["exit_price"] == 97
    print("PASS test_sl_tp_long_hits_sl")


def test_sl_tp_short_hits_tp():
    records = [
        build_record("ETHUSDT", "SELL", "bearish", 0.80, 100, 1000),
        build_record("ETHUSDT", "HOLD", "neutral", 0.55, 92, 2000),
    ]
    candles = [
        build_candle(1000, 100, 100, 100, 100),
        build_candle(2000, 100, 98, 92, 95),
    ]
    provider = _make_candle_provider({"ETHUSDT": candles})
    config = {
        "simulation": {
            "fee_pct": 0.0, "slippage_pct": 0.0, "min_confidence": 0.55,
            "use_sl_tp": True, "stop_loss_pct": 0.03, "take_profit_pct": 0.06,
            "max_hold_candles": 48, "same_candle_priority": "stop_loss",
        }
    }
    with tempfile.TemporaryDirectory() as tmp:
        trades, _ = simulate(records, config, "/tmp/out.jsonl", "/tmp/sum.json", ohlcv_provider=provider)
    assert trades[0]["exit_reason"] == "take_profit"
    assert trades[0]["exit_price"] == 94
    assert trades[0]["side"] == "SHORT"
    print("PASS test_sl_tp_short_hits_tp")


def test_sl_tp_max_hold_exit():
    candles = []
    for i in range(5):
        ts = 1000 + i * 3600
        candles.append(build_candle(ts, 100, 101, 100, 100))
    records = [
        build_record("BTCUSDT", "BUY", "bullish", 0.80, 100, 1000),
    ] + [
        build_record("BTCUSDT", "HOLD", "neutral", 0.55, 100, 1000 + i * 3600)
        for i in range(1, 5)
    ]
    provider = _make_candle_provider({"BTCUSDT": candles})
    config = {
        "simulation": {
            "fee_pct": 0.0, "slippage_pct": 0.0, "min_confidence": 0.55,
            "use_sl_tp": True, "stop_loss_pct": 0.03, "take_profit_pct": 0.06,
            "max_hold_candles": 3, "same_candle_priority": "stop_loss",
        }
    }
    with tempfile.TemporaryDirectory() as tmp:
        trades, _ = simulate(records, config, "/tmp/out.jsonl", "/tmp/sum.json", ohlcv_provider=provider)
    assert len(trades) == 1
    assert trades[0]["exit_reason"] == "max_hold"
    print("PASS test_sl_tp_max_hold_exit")


def test_sl_tp_opposite_signal_ignored_when_sl_tp_present():
    """If SL/TP hit first, opposite signal should not override."""
    records = [
        build_record("BTCUSDT", "BUY", "bullish", 0.80, 100, 1000),
        build_record("BTCUSDT", "SELL", "bearish", 0.80, 96, 2000),
    ]
    candles = [
        build_candle(1000, 100, 100, 100, 100),
        build_candle(2000, 100, 99, 96, 97),
    ]
    provider = _make_candle_provider({"BTCUSDT": candles})
    config = {
        "simulation": {
            "fee_pct": 0.0, "slippage_pct": 0.0, "min_confidence": 0.55,
            "use_sl_tp": True, "stop_loss_pct": 0.03, "take_profit_pct": 0.06,
            "max_hold_candles": 48, "same_candle_priority": "stop_loss",
        }
    }
    with tempfile.TemporaryDirectory() as tmp:
        trades, _ = simulate(records, config, "/tmp/out.jsonl", "/tmp/sum.json", ohlcv_provider=provider)
    assert trades[0]["exit_reason"] == "stop_loss"
    print("PASS test_sl_tp_opposite_signal_ignored_when_sl_tp_present")


def test_sl_tp_no_candles_falls_back():
    """When OHLCV is empty and use_sl_tp=true, falls back to opposite/EOD."""
    records = [
        build_record("BTCUSDT", "BUY", "bullish", 0.80, 100, 1000),
        build_record("BTCUSDT", "SELL", "bearish", 0.80, 105, 2000),
    ]
    provider = _make_candle_provider({})
    config = {
        "simulation": {
            "fee_pct": 0.0, "slippage_pct": 0.0, "min_confidence": 0.55,
            "use_sl_tp": True, "stop_loss_pct": 0.03, "take_profit_pct": 0.06,
            "max_hold_candles": 48, "same_candle_priority": "stop_loss",
        }
    }
    with tempfile.TemporaryDirectory() as tmp:
        trades, _ = simulate(records, config, "/tmp/out.jsonl", "/tmp/sum.json", ohlcv_provider=provider)
    assert len(trades) == 1
    assert trades[0]["exit_reason"] == "opposite_signal"
    print("PASS test_sl_tp_no_candles_falls_back")


def test_sl_tp_summary_includes_mae_mfe():
    records = [
        build_record("BTCUSDT", "BUY", "bullish", 0.80, 100, 1000),
        build_record("BTCUSDT", "HOLD", "neutral", 0.55, 108, 2000),
    ]
    candles = [
        build_candle(1000, 100, 100, 100, 100),
        build_candle(2000, 100, 108, 102, 107),
    ]
    provider = _make_candle_provider({"BTCUSDT": candles})
    config = {
        "simulation": {
            "fee_pct": 0.0, "slippage_pct": 0.0, "min_confidence": 0.55,
            "use_sl_tp": True, "stop_loss_pct": 0.03, "take_profit_pct": 0.06,
            "max_hold_candles": 48, "same_candle_priority": "stop_loss",
        }
    }
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "trades.jsonl"
        sum_path = Path(tmp) / "summary.json"
        simulate(records, config, str(out), str(sum_path), ohlcv_provider=provider)
        with open(sum_path) as f:
            summary = json.load(f)
    assert "avg_mae_pct" in summary
    assert "avg_mfe_pct" in summary
    assert summary["avg_mfe_pct"] > 0
    print("PASS test_sl_tp_summary_includes_mae_mfe")


def test_multisymbol():
    records = [
        build_record("BTCUSDT", "BUY", "bullish", 0.80, 50000, 1000),
        build_record("ETHUSDT", "BUY", "bullish", 0.80, 3000, 1100),
        build_record("BTCUSDT", "SELL", "bearish", 0.80, 51000, 2000),
        build_record("ETHUSDT", "SELL", "bearish", 0.80, 2900, 2100),
    ]
    config = {"simulation": {"fee_pct": 0.0, "slippage_pct": 0.0, "min_confidence": 0.55}}
    with tempfile.TemporaryDirectory() as tmp:
        trades, _ = simulate(records, config, "/tmp/out.jsonl", "/tmp/sum.json")
    assert len(trades) == 2
    assert {t["symbol"] for t in trades} == {"BTCUSDT", "ETHUSDT"}
    print("PASS test_multisymbol")


if __name__ == "__main__":
    test_extract_action()
    test_extract_confidence()
    test_extract_price()
    test_extract_timestamp()
    test_basic_buy_sell_flow()
    test_basic_sell_buy_flow()
    test_end_of_data_exit()
    test_min_confidence_filter()
    test_duplicate_ignored()
    test_fees_applied()
    test_empty_replay()
    test_mixed_signals()
    test_compute_sl_tp_long()
    test_compute_sl_tp_short()
    test_check_candle_exit_long_tp()
    test_check_candle_exit_long_sl()
    test_check_candle_exit_short_tp()
    test_check_candle_exit_short_sl()
    test_check_candle_exit_no_hit()
    test_check_candle_exit_same_candle_sl_priority()
    test_check_candle_exit_same_candle_tp_priority()
    test_mae_mfe_long()
    test_mae_mfe_short()
    test_sl_tp_long_hits_tp()
    test_sl_tp_long_hits_sl()
    test_sl_tp_short_hits_tp()
    test_sl_tp_max_hold_exit()
    test_sl_tp_opposite_signal_ignored_when_sl_tp_present()
    test_sl_tp_no_candles_falls_back()
    test_sl_tp_summary_includes_mae_mfe()
    test_multisymbol()
    print("\nAll trade simulation tests passed.")

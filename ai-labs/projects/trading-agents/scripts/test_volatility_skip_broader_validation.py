#!/usr/bin/env python3
"""Tests for Batch 3J broader volatility-skip validation."""
import json
import tempfile
from pathlib import Path

import run_volatility_skip_broader_validation as broader


def _write_jsonl(path: Path, rows):
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def _record(symbol="BTCUSDT", final_action="BUY", close=100.0, atr=10.0, confidence=0.60):
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
                "regime": "volatile", "confidence": confidence,
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
            "attribution": {"regime": "volatile", "source": "fixture"},
        },
    }


def test_discover_default_inputs_returns_existing_non_variant_windows():
    discovered = broader.discover_default_inputs()
    assert all(path.exists() for path in discovered)
    assert all("variant" not in path.name for path in discovered)


def test_window_metadata_counts_symbols_and_regimes():
    rows = [_record(symbol="BTCUSDT"), _record(symbol="ETHUSDT", final_action="SELL")]
    meta = broader.window_metadata(Path("logs/example.jsonl"), rows)
    assert meta["window_id"] == "example"
    assert meta["record_count"] == 2
    assert meta["symbols"] == ["BTCUSDT", "ETHUSDT"]
    assert meta["market_regime_counts"] == {"volatile": 2}


def test_build_report_fixture_preserves_authorization_boundaries():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "fixture.jsonl"
        _write_jsonl(path, [_record(), _record(symbol="ETHUSDT", final_action="HOLD", atr=4.0)])
        report = broader.build_report(broader.load_windows([path]), ["variant-d", "variant-b"])
    assert report["batch"] == "3J"
    assert report["mode"] == "offline_replay_only"
    assert report["production_change_authorized"] is False
    assert report["implementation_authorized"] is False
    assert report["requires_approval_before_runtime_change"] is True
    assert report["candidates"] == ["baseline", "variant-d", "variant-b"]
    assert report["aggregate"]["baseline"]["total_records"] == 2
    assert report["recommendation"]["production_change_authorized"] is False


def test_flags_detect_suspicious_zero_volatility_skip_block():
    results = [{"window": {"window_id": "w1"}, "candidates": {
        "baseline": {"rates": {"volatility_skip_direct_block_rate": 0.5, "conflict_rate": 0.0, "attribution_coverage_rate": 1.0, "directional_strategy_coverage_rate": 0.1}},
        "variant-d": {"rates": {"volatility_skip_direct_block_rate": 0.0, "conflict_rate": 0.0, "attribution_coverage_rate": 1.0, "directional_strategy_coverage_rate": 0.2}, "action_matrix": {"BUY|short": 0, "SELL|long": 0}},
    }}]
    flags = broader.build_flags(results, ["variant-d"])
    assert any(flag["metric"] == "volatility_skip_direct_block_rate" for flag in flags)
    assert not any(flag["severity"] == "regression" for flag in flags)


def test_render_markdown_contains_decision_block():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "fixture.jsonl"
        _write_jsonl(path, [_record()])
        report = broader.build_report(broader.load_windows([path]), ["variant-d"])
    markdown = broader.render_markdown_report(report)
    assert "Batch 3J Decision" in markdown
    assert "Production change authorized: false" in markdown
    assert "Runtime/default config change: not performed" in markdown


if __name__ == "__main__":
    tests = [
        test_discover_default_inputs_returns_existing_non_variant_windows,
        test_window_metadata_counts_symbols_and_regimes,
        test_build_report_fixture_preserves_authorization_boundaries,
        test_flags_detect_suspicious_zero_volatility_skip_block,
        test_render_markdown_contains_decision_block,
    ]
    for test in tests:
        test()
    print(f"PASS {len(tests)} broader validation tests")

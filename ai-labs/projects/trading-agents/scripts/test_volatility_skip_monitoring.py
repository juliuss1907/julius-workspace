#!/usr/bin/env python3
"""Tests for Batch 3O volatility-skip monitoring."""
import json
import tempfile
from pathlib import Path

import run_volatility_skip_monitoring as monitoring


def _record(action="BUY", strategy_action="skip", strategy_id="volatility-skip", family="volatility_skip"):
    return {
        "symbol": "BTCUSDT",
        "market_snapshot": {"timeframe": "1h"},
        "analysts": {"technical": {"analysis": {
            "technical_state": {
                "close": 106.0, "atr": 9.0, "ema_20": 103.0, "ema_50": 100.0,
                "macd_histogram": 1.2, "rsi": 55.0, "breakout_up_20": True,
                "recent_high_20": 105.0,
            },
            "market_state": {"regime": "volatile", "confidence": 0.60, "trend_direction": "up", "trend_strength": 70.0},
        }}},
        "final_signal": {"metadata": {"final_action": action}},
        "strategy_signal": {
            "strategy_id": strategy_id,
            "family": family,
            "action": strategy_action,
            "confidence": 0.6,
            "attribution": {"regime": "volatile"},
        },
    }


def _write_jsonl(path: Path, rows):
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def test_verify_variant_d_config_passes_expected_surface():
    cfg = {
        "regime_strategy_order": {"volatile": ["volatility_skip", "trend_following", "breakout"]},
        "volatility_skip": {"volatile_confidence_floor": 0.75, "high_atr_pct": 0.10},
        "trend_following": {"allow_volatile_trend_up": True, "allow_volatile_trend_down": True, "min_regime_confidence": 0.50},
        "selection": {"min_action_confidence": 0.50},
        "breakout": {"allow_volatile": False},
    }
    result = monitoring.verify_variant_d_config(cfg)
    assert result["matches_variant_d"] is True
    assert result["breakout_allow_volatile_default"] is False


def test_verify_variant_d_config_fails_if_breakout_enabled():
    cfg = {
        "regime_strategy_order": {"volatile": ["volatility_skip", "trend_following", "breakout"]},
        "volatility_skip": {"volatile_confidence_floor": 0.75, "high_atr_pct": 0.10},
        "trend_following": {"allow_volatile_trend_up": True, "allow_volatile_trend_down": True, "min_regime_confidence": 0.50},
        "selection": {"min_action_confidence": 0.50},
        "breakout": {"allow_volatile": True},
    }
    result = monitoring.verify_variant_d_config(cfg)
    assert result["matches_variant_d"] is False
    assert result["breakout_allow_volatile_default"] is True


def test_alert_logic_fails_on_hard_conflict():
    config_check = {"matches_variant_d": True, "breakout_allow_volatile_default": False}
    aggregate = {"total_records": 10, "hard_conflict_count": 1, "volatile_breakout_selected_count": 0, "fallback_or_missing_state_count": 0, "volatile_trend_following_selected_count": 0, "rates_weighted_by_records": {"attribution_coverage_rate": 1.0, "volatility_skip_direct_block_rate": 0.5, "directional_strategy_coverage_rate": 0.1}}
    alerts = monitoring.build_alerts(config_check, aggregate)
    assert monitoring.status_from_alerts(alerts) == "fail"
    assert any(a["metric"] == "hard_conflict_count" for a in alerts)


def test_alert_logic_fails_on_volatile_breakout():
    config_check = {"matches_variant_d": True, "breakout_allow_volatile_default": False}
    aggregate = {"total_records": 10, "hard_conflict_count": 0, "volatile_breakout_selected_count": 1, "fallback_or_missing_state_count": 0, "volatile_trend_following_selected_count": 0, "rates_weighted_by_records": {"attribution_coverage_rate": 1.0, "volatility_skip_direct_block_rate": 0.5, "directional_strategy_coverage_rate": 0.1}}
    alerts = monitoring.build_alerts(config_check, aggregate)
    assert monitoring.status_from_alerts(alerts) == "fail"
    assert any(a["metric"] == "volatile_breakout_selected_count" for a in alerts)


def test_alert_logic_watches_zero_volatility_skip_block():
    config_check = {"matches_variant_d": True, "breakout_allow_volatile_default": False}
    aggregate = {"total_records": 120, "hard_conflict_count": 0, "volatile_breakout_selected_count": 0, "fallback_or_missing_state_count": 0, "volatile_trend_following_selected_count": 1, "rates_weighted_by_records": {"attribution_coverage_rate": 1.0, "volatility_skip_direct_block_rate": 0.0, "directional_strategy_coverage_rate": 0.1}}
    alerts = monitoring.build_alerts(config_check, aggregate)
    assert monitoring.status_from_alerts(alerts) == "watch"
    assert any(a["metric"] == "volatility_skip_direct_block_rate" for a in alerts)


def test_monitoring_report_schema_from_fixture():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "fixture.jsonl"
        _write_jsonl(path, [_record(), _record(action="HOLD")])
        report = monitoring.build_report([path])
    assert report["batch"] == "3O"
    assert report["runtime_default_config_change_performed"] is False
    assert "alerts" in report
    assert "metrics" in report
    assert report["current_config"]["breakout_allow_volatile_default"] is False



def test_candidate_level_counts_from_batch3w_schema():
    record = _record(strategy_action="long", strategy_id="trend-following", family="trend_following")
    record["strategy_signal"]["attribution"] = {
        "candidate_schema_version": "batch3w-v1",
        "evaluated": [
            {
                "strategy_id": "volatility-skip",
                "family": "volatility_skip",
                "action": "hold",
                "confidence": 0.5,
                "selected": False,
                "eligible": True,
                "selection_reason": None,
                "rejection_reason": "hold_candidate_overridden_by_action_candidate",
                "thresholds": {"high_atr_pct": 0.10, "volatile_confidence_floor": 0.75},
                "observed": {"atr_pct": 0.05, "regime_confidence": 0.60},
            },
            {
                "strategy_id": "trend-following",
                "family": "trend_following",
                "action": "long",
                "confidence": 0.95,
                "selected": True,
                "eligible": True,
                "selection_reason": "action_confidence_above_floor",
                "rejection_reason": None,
                "thresholds": {},
                "observed": {},
            },
        ],
    }
    counts = monitoring.candidate_level_counts(record)
    assert counts["volatility_skip_evaluated_count"] == 1
    assert counts["volatility_skip_evaluated_not_selected_count"] == 1
    assert counts["volatility_skip_action_override_count"] == 1
    assert counts["volatility_skip_threshold_failed_count"] == 1
    assert counts["volatility_skip_confidence_floor_failed_count"] == 1
    aggregate_counts = monitoring.monitoring_counts([record])
    assert aggregate_counts["volatility_skip_evaluated_count"] == 1
    assert aggregate_counts["volatility_skip_action_override_count"] == 1

def test_cli_help_is_lightweight():
    import subprocess, sys
    rv = subprocess.run([sys.executable, "scripts/run_volatility_skip_monitoring.py", "--help"], capture_output=True, text=True, timeout=15)
    assert rv.returncode == 0
    assert "--inputs" in rv.stdout and "--overwrite" in rv.stdout


if __name__ == "__main__":
    tests = [
        test_verify_variant_d_config_passes_expected_surface,
        test_verify_variant_d_config_fails_if_breakout_enabled,
        test_alert_logic_fails_on_hard_conflict,
        test_alert_logic_fails_on_volatile_breakout,
        test_alert_logic_watches_zero_volatility_skip_block,
        test_monitoring_report_schema_from_fixture,
        test_candidate_level_counts_from_batch3w_schema,
        test_cli_help_is_lightweight,
    ]
    for test in tests:
        test()
    print(f"PASS {len(tests)} volatility-skip monitoring tests")

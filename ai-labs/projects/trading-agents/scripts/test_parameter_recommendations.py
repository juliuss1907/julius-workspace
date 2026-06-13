#!/usr/bin/env python3
"""Test Phase 7A: Adaptive Parameter Recommendations."""
import json
import sys
import tempfile
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.generate_parameter_recommendations import (
    DEFAULT_RULES,
    APPLY_STATUS,
    load_json,
    load_yaml,
    get_config_value,
    generate_recommendations,
    sort_recommendations,
    build_report,
    render_markdown,
    main as rec_main,
)


def _dashboard(
    simulated_trades=20,
    total_pnl_pct=1.0,
    win_rate=0.6,
    avg_hold_candles=10.0,
    by_side=None,
    warnings=None,
    by_direction=None,
    exit_reasons=None,
):
    return {
        "simulation": {
            "simulated_trades": simulated_trades,
            "total_pnl_pct": total_pnl_pct,
            "win_rate": win_rate,
            "avg_hold_candles": avg_hold_candles,
            "exit_reasons": exit_reasons or {},
        },
        "replay": {
            "signals": simulated_trades * 2,
            "hold_ratio": 0.4,
            "by_direction": by_direction or {"bullish": 10, "bearish": 10, "neutral": 20},
        },
        "trades": {
            "count": simulated_trades,
            "by_side": by_side or {"LONG": 12, "SHORT": 8},
            "by_symbol": {"BTCUSDT": 12, "ETHUSDT": 8},
        },
        "warnings": warnings or [],
    }


def _config():
    return {
        "risk_manager": {"min_signal_confidence": 0.60},
        "analyst_weights": {
            "full": {"derivatives": 0.15},
            "direction_thresholds": {"bullish_above": 0.57, "bearish_below": 0.43},
        },
        "simulation": {
            "min_confidence": 0.55,
            "use_sl_tp": False,
            "max_hold_candles": 48,
        },
        "parameter_sweep": {
            "min_confidence_values": [0.55, 0.60, 0.65, 0.70, 0.75, 0.80],
        },
        "stop_loss": {"atr_multiplier": 2.5},
    }


def test_load_json_missing():
    assert load_json(Path("/nonexistent.json")) is None
    print("PASS test_load_json_missing")


def test_load_json_valid():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"a": 1}, f)
        path = Path(f.name)
    assert load_json(path) == {"a": 1}
    path.unlink()
    print("PASS test_load_json_valid")


def test_load_yaml_valid():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("a: 1\nb:\n  c: 2\n")
        path = Path(f.name)
    data = load_yaml(path)
    assert data == {"a": 1, "b": {"c": 2}}
    path.unlink()
    print("PASS test_load_yaml_valid")


def test_get_config_value_present():
    cfg = {"a": {"b": {"c": 5}}}
    assert get_config_value(cfg, "a.b.c") == 5
    print("PASS test_get_config_value_present")


def test_get_config_value_missing():
    cfg = {"a": {"b": 1}}
    assert get_config_value(cfg, "a.x.y") is None
    print("PASS test_get_config_value_missing")


def test_get_config_value_none_cfg():
    assert get_config_value(None, "a.b") is None
    print("PASS test_get_config_value_none_cfg")


def test_empty_inputs_yield_workflow_fallback():
    recs = generate_recommendations({}, {}, {}, {}, DEFAULT_RULES)
    assert len(recs) == 1
    assert recs[0]["category"] == "workflow"
    assert recs[0]["priority"] == "low"
    assert recs[0]["apply_status"] == APPLY_STATUS
    print("PASS test_empty_inputs_yield_workflow_fallback")


def test_small_sample_size():
    dash = _dashboard(simulated_trades=3)
    recs = generate_recommendations(dash, {}, {}, _config(), DEFAULT_RULES)
    assert any(r["category"] == "data_quality" and "small" in r["finding"].lower() for r in recs)
    assert any(r["priority"] == "high" for r in recs)
    print("PASS test_small_sample_size")


def test_side_bias_short():
    dash = _dashboard(
        simulated_trades=12,
        by_side={"SHORT": 12},
    )
    recs = generate_recommendations(dash, {}, {}, _config(), DEFAULT_RULES)
    side_recs = [r for r in recs if r["category"] == "side_bias"]
    assert side_recs, "expected side_bias recommendation"
    assert side_recs[0]["priority"] == "high"
    assert "SHORT" in side_recs[0]["finding"]
    print("PASS test_side_bias_short")


def test_side_bias_below_threshold_ignored():
    dash = _dashboard(simulated_trades=20, by_side={"LONG": 12, "SHORT": 8})
    recs = generate_recommendations(dash, {}, {}, _config(), DEFAULT_RULES)
    assert not any(r["category"] == "side_bias" for r in recs)
    print("PASS test_side_bias_below_threshold_ignored")


def test_stale_hold_candles():
    dash = _dashboard(simulated_trades=10, avg_hold_candles=120.0)
    recs = generate_recommendations(dash, {}, {}, _config(), DEFAULT_RULES)
    exit_recs = [r for r in recs if r["category"] == "exits"]
    assert exit_recs, "expected exits recommendation"
    assert exit_recs[0]["config_path"] == "simulation.max_hold_candles"
    assert exit_recs[0]["priority"] == "medium"
    print("PASS test_stale_hold_candles")


def test_stale_hold_below_min_trades_ignored():
    dash = _dashboard(simulated_trades=1, avg_hold_candles=200.0)
    recs = generate_recommendations(dash, {}, {}, _config(), DEFAULT_RULES)
    assert not any(r["category"] == "exits" and r.get("config_path") == "simulation.max_hold_candles" for r in recs)
    print("PASS test_stale_hold_below_min_trades_ignored")


def test_negative_pnl_with_enough_trades():
    dash = _dashboard(simulated_trades=15, total_pnl_pct=-3.0)
    recs = generate_recommendations(dash, {}, {}, _config(), DEFAULT_RULES)
    neg = [r for r in recs if r["category"] == "thresholds"]
    assert neg, "expected thresholds recommendation for negative pnl"
    assert neg[0]["priority"] == "high"
    print("PASS test_negative_pnl_with_enough_trades")


def test_negative_pnl_below_min_trades_ignored():
    dash = _dashboard(simulated_trades=2, total_pnl_pct=-3.0)
    recs = generate_recommendations(dash, {}, {}, _config(), DEFAULT_RULES)
    assert not any(
        r["category"] == "thresholds" and "negative expectancy" in r["finding"].lower()
        for r in recs
    )
    print("PASS test_negative_pnl_below_min_trades_ignored")


def test_high_win_rate_with_small_sample():
    dash = _dashboard(simulated_trades=6, win_rate=0.9)
    recs = generate_recommendations(dash, {}, {}, _config(), DEFAULT_RULES)
    win_recs = [
        r for r in recs
        if r["category"] == "data_quality" and "win rate" in r["finding"].lower()
    ]
    assert win_recs, "expected win-rate data_quality rec"
    assert win_recs[0]["priority"] == "medium"
    print("PASS test_high_win_rate_with_small_sample")


def test_sweep_ties_recommendation():
    sweep = {
        "results": [
            {"min_confidence": 0.55, "trades": 10, "score": 5.751, "win_rate": 1.0, "total_pnl_pct": 0.5},
            {"min_confidence": 0.60, "trades": 10, "score": 5.751, "win_rate": 1.0, "total_pnl_pct": 0.5},
            {"min_confidence": 0.65, "trades": 10, "score": 5.751, "win_rate": 1.0, "total_pnl_pct": 0.5},
        ]
    }
    recs = generate_recommendations(_dashboard(), sweep, {}, _config(), DEFAULT_RULES)
    tie_recs = [
        r for r in recs
        if r["category"] == "data_quality" and "differentiating" in r["finding"].lower()
    ]
    assert tie_recs, "expected sweep-tie rec"
    assert tie_recs[0]["priority"] == "low"
    print("PASS test_sweep_ties_recommendation")


def test_sweep_best_too_few_trades():
    sweep = {
        "results": [
            {"min_confidence": 0.55, "trades": 3, "score": 2.0, "win_rate": 0.8, "total_pnl_pct": 0.4},
        ]
    }
    recs = generate_recommendations(_dashboard(simulated_trades=20), sweep, {}, _config(), DEFAULT_RULES)
    few = [
        r for r in recs
        if r["category"] == "data_quality" and "ranking is unreliable" in r["finding"].lower()
    ]
    assert few, "expected sweep-best too-few-trades rec"
    assert few[0]["priority"] == "medium"
    assert few[0]["config_path"] == "simulation.min_confidence"
    print("PASS test_sweep_best_too_few_trades")


def test_replay_sweep_best_negative_pnl_rejected():
    replay = {
        "results": [
            {
                "variant": "lower_thresholds",
                "simulation": {"trades": 6, "win_rate": 0.17, "total_pnl_pct": -0.06},
                "score": 0.26,
            }
        ]
    }
    recs = generate_recommendations(_dashboard(), {}, replay, _config(), DEFAULT_RULES)
    rej = [
        r for r in recs
        if r["category"] == "thresholds" and "do not apply" in r["recommendation"].lower()
    ]
    assert rej, "expected negative best-replay rejection"
    assert rej[0]["priority"] == "high"
    print("PASS test_replay_sweep_best_negative_pnl_rejected")


def test_sl_tp_imbalance_warning_creates_exit_rec():
    dash = _dashboard(
        simulated_trades=20,
        warnings=["⚠️ SL/TP imbalance: stop_loss exits (10) >> take_profit exits (5)."],
        exit_reasons={"stop_loss": 10, "take_profit": 5},
    )
    recs = generate_recommendations(dash, {}, {}, _config(), DEFAULT_RULES)
    sl = [
        r for r in recs
        if r["category"] == "exits" and r.get("config_path") == "stop_loss.atr_multiplier"
    ]
    assert sl, "expected SL/TP imbalance rec"
    assert sl[0]["priority"] == "medium"
    print("PASS test_sl_tp_imbalance_warning_creates_exit_rec")


def test_negative_warning_creates_workflow_rec():
    dash = _dashboard(
        simulated_trades=20,
        warnings=["⚠️ Negative expectancy: total PnL -1.00% across 12 trades."],
        total_pnl_pct=1.0,
    )
    recs = generate_recommendations(dash, {}, {}, _config(), DEFAULT_RULES)
    workflow = [r for r in recs if r["category"] == "workflow"]
    assert any("negative" in r["finding"].lower() for r in workflow)
    print("PASS test_negative_warning_creates_workflow_rec")


def test_apply_status_always_manual():
    dash = _dashboard(simulated_trades=3, by_side={"SHORT": 3}, avg_hold_candles=200)
    recs = generate_recommendations(dash, {}, {}, _config(), DEFAULT_RULES)
    for r in recs:
        assert r["apply_status"] == APPLY_STATUS, f"bad apply_status in {r['id']}"
    print("PASS test_apply_status_always_manual")


def test_sort_recommendations_by_priority():
    recs = [
        {"id": "R001", "priority": "low", "category": "workflow"},
        {"id": "R002", "priority": "high", "category": "data_quality"},
        {"id": "R003", "priority": "medium", "category": "exits"},
    ]
    sorted_recs = sort_recommendations(recs)
    assert [r["id"] for r in sorted_recs] == ["R002", "R003", "R001"]
    print("PASS test_sort_recommendations_by_priority")


def test_render_markdown_contains_sections():
    recs = [
        {
            "id": "R001",
            "priority": "high",
            "category": "data_quality",
            "finding": "Small sample",
            "evidence": "trades=3",
            "recommendation": "Collect more data",
            "config_path": None,
            "current_value": None,
            "suggested_value": None,
            "apply_status": APPLY_STATUS,
        }
    ]
    dash = _dashboard(simulated_trades=3)
    md = render_markdown(recs, dash, DEFAULT_RULES)
    assert "# Adaptive Parameter Recommendations" in md
    assert "## Summary" in md
    assert "## Recommendations" in md
    assert "manual_review_required" in md
    assert "R001" in md
    print("PASS test_render_markdown_contains_sections")


def test_build_report_structure():
    report = build_report(_dashboard(3), {}, {}, _config(), DEFAULT_RULES)
    assert "generated_at" in report
    assert "summary" in report
    assert "trades_analyzed" in report
    assert "recommendations" in report
    assert report["summary"]["total"] == len(report["recommendations"])
    print("PASS test_build_report_structure")


def test_id_format():
    recs = generate_recommendations(_dashboard(3), {}, {}, _config(), DEFAULT_RULES)
    for r in recs:
        assert r["id"].startswith("R") and len(r["id"]) == 4
    print("PASS test_id_format")


def test_main_smoke(tmp_run_dir):
    """Run the CLI end-to-end against current real reports."""
    out_md = tmp_run_dir / "recs.md"
    out_json = tmp_run_dir / "recs.json"
    project_root_real = Path(__file__).parent.parent

    argv_save = sys.argv
    try:
        sys.argv = [
            "generate_parameter_recommendations.py",
            "--md-out", str(out_md),
            "--json-out", str(out_json),
            "--dashboard", str(project_root_real / "reports/backtest-dashboard.json"),
            "--sweep", str(project_root_real / "logs/parameter_sweep_report.json"),
            "--replay-sweep", str(project_root_real / "logs/replay_sweep_report.json"),
            "--config", str(project_root_real / "config/default_params.yaml"),
        ]
        rec_main()
    finally:
        sys.argv = argv_save

    assert out_md.exists()
    assert out_json.exists()
    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert "recommendations" in data
    assert data["summary"]["total"] >= 1
    print(f"PASS test_main_smoke (generated {data['summary']['total']} recommendations)")


def run_all():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_run_dir = Path(tmp)

        tests = [
            test_load_json_missing,
            test_load_json_valid,
            test_load_yaml_valid,
            test_get_config_value_present,
            test_get_config_value_missing,
            test_get_config_value_none_cfg,
            test_empty_inputs_yield_workflow_fallback,
            test_small_sample_size,
            test_side_bias_short,
            test_side_bias_below_threshold_ignored,
            test_stale_hold_candles,
            test_stale_hold_below_min_trades_ignored,
            test_negative_pnl_with_enough_trades,
            test_negative_pnl_below_min_trades_ignored,
            test_high_win_rate_with_small_sample,
            test_sweep_ties_recommendation,
            test_sweep_best_too_few_trades,
            test_replay_sweep_best_negative_pnl_rejected,
            test_sl_tp_imbalance_warning_creates_exit_rec,
            test_negative_warning_creates_workflow_rec,
            test_apply_status_always_manual,
            test_sort_recommendations_by_priority,
            test_render_markdown_contains_sections,
            test_build_report_structure,
            test_id_format,
        ]

        failures = 0
        for t in tests:
            try:
                t()
            except AssertionError as e:
                print(f"FAIL {t.__name__}: {e}")
                failures += 1
            except Exception as e:
                print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
                failures += 1

        test_main_smoke(tmp_run_dir=tmp_run_dir)
        if failures:
            print(f"\n{ failures} test(s) failed")
            sys.exit(1)
        print(f"\nAll {len(tests) + 1} tests passed")


if __name__ == "__main__":
    run_all()

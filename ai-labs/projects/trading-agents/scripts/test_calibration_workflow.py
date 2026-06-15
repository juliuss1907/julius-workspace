#!/usr/bin/env python3
"""Test Phase 7B: Calibration Workflow Orchestrator."""
import json
import sys
import tempfile
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.run_calibration_workflow import (
    PYTHON,
    today_str,
    timestamp,
    build_steps,
    generate_summary_md,
    _dependency_failed,
    _load_json_safe,
)


class _Args:
    """Minimal args namespace for testing."""
    def __init__(self, **kwargs):
        self.symbols = kwargs.get("symbols", ["BTCUSDT", "ETHUSDT"])
        self.days = kwargs.get("days", 30)
        self.sweep_days = kwargs.get("sweep_days", None)
        self.window = kwargs.get("window", 120)
        self.step = kwargs.get("step", 24)
        self.use_sl_tp = kwargs.get("use_sl_tp", False)
        self.no_sl_tp = kwargs.get("no_sl_tp", False)
        self.baseline_only = kwargs.get("baseline_only", False)
        self.config = kwargs.get("config", None)
        self.dry_run = kwargs.get("dry_run", False)
        self.output_date = kwargs.get("output_date", None)
        self.end_date = kwargs.get("end_date", None)
        self.timeout = kwargs.get("timeout", None)
        self.skip_replay = kwargs.get("skip_replay", False)
        self.skip_replay_sweep = kwargs.get("skip_replay_sweep", False)
        self.skip_simulation = kwargs.get("skip_simulation", False)
        self.skip_parameter_sweep = kwargs.get("skip_parameter_sweep", False)
        self.skip_dashboard = kwargs.get("skip_dashboard", False)
        self.skip_recommendations = kwargs.get("skip_recommendations", False)


# ---------------------------------------------------------------------------
# build_steps
# ---------------------------------------------------------------------------

def test_build_steps_default():
    cal = Path("/tmp/cal7b/test-date")
    art = cal / "artifacts"
    args = _Args()
    steps = build_steps(args, cal, art)
    assert len(steps) == 6

    ids = [s["id"] for s in steps]
    assert ids == ["replay", "replay-sweep", "simulation", "parameter-sweep", "dashboard", "recommendations"]

    for s in steps:
        assert not s.get("skip")
        assert s.get("cmd"), f"no cmd for {s['id']}"

    print("PASS test_build_steps_default")


def test_build_steps_sl_tp_flag():
    cal = Path("/tmp/cal7b/t2")
    art = cal / "artifacts"
    args = _Args(use_sl_tp=True)
    sim = [s for s in build_steps(args, cal, art) if s["id"] == "simulation"][0]
    assert "--use-sl-tp" in sim["cmd"]
    print("PASS test_build_steps_sl_tp_flag")


def test_build_steps_no_sl_tp_flag():
    cal = Path("/tmp/cal7b/t3")
    art = cal / "artifacts"
    args = _Args(no_sl_tp=True)
    sim = [s for s in build_steps(args, cal, art) if s["id"] == "simulation"][0]
    assert "--no-sl-tp" in sim["cmd"]
    print("PASS test_build_steps_no_sl_tp_flag")


def test_build_steps_baseline_only():
    cal = Path("/tmp/cal7b/t4")
    art = cal / "artifacts"
    args = _Args(baseline_only=True)
    sweep = [s for s in build_steps(args, cal, art) if s["id"] == "replay-sweep"][0]
    assert "--baseline-only" in sweep["cmd"]
    print("PASS test_build_steps_baseline_only")


def test_build_steps_skip_flags():
    cal = Path("/tmp/cal7b/t5")
    art = cal / "artifacts"
    args = _Args(
        skip_replay=True,
        skip_simulation=True,
        skip_recommendations=True,
    )
    steps = build_steps(args, cal, art)
    for s in steps:
        if s["id"] in ("replay", "simulation", "recommendations"):
            assert s.get("skip"), f"{s['id']} should be skipped"
        else:
            assert not s.get("skip"), f"{s['id']} should NOT be skipped"
    print("PASS test_build_steps_skip_flags")


def test_build_steps_output_paths_are_dated():
    cal = Path("/tmp/cal7b/2026-07-15")
    art = cal / "artifacts"
    args = _Args()
    steps = build_steps(args, cal, art)
    replay = [s for s in steps if s["id"] == "replay"][0]
    assert "2026-07-15/replay_signals.jsonl" in str(replay["outputs"][0])

    dash = [s for s in steps if s["id"] == "dashboard"][0]
    assert "2026-07-15/backtest-dashboard.json" in str(dash["outputs"][0])
    assert "2026-07-15/backtest-dashboard.md" in str(dash["outputs"][1])
    print("PASS test_build_steps_output_paths_are_dated")


def test_build_steps_symbols_in_cmd():
    cal = Path("/tmp/cal7b/t7")
    art = cal / "artifacts"
    args = _Args(symbols=["BTCUSDT", "SOLUSDT"])
    steps = build_steps(args, cal, art)
    replay = [s for s in steps if s["id"] == "replay"][0]
    cmd_str = " ".join(str(a) for a in replay["cmd"])
    assert "BTCUSDT" in cmd_str
    assert "SOLUSDT" in cmd_str
    assert "ETHUSDT" not in cmd_str
    print("PASS test_build_steps_symbols_in_cmd")


def test_build_steps_depends_set():
    cal = Path("/tmp/cal7b/t8")
    art = cal / "artifacts"
    args = _Args()
    steps = build_steps(args, cal, art)
    sim = [s for s in steps if s["id"] == "simulation"][0]
    assert "replay" in sim["depends"]

    dash = [s for s in steps if s["id"] == "dashboard"][0]
    assert "replay" in dash["depends"]
    assert "simulation" in dash["depends"]

    recs = [s for s in steps if s["id"] == "recommendations"][0]
    assert "dashboard" in recs["depends"]
    print("PASS test_build_steps_depends_set")


def test_build_steps_end_date_passthrough():
    from datetime import date
    cal = Path("/tmp/cal7b/t10")
    art = cal / "artifacts"
    args = _Args(end_date=date(2024, 12, 31))
    replay = [s for s in build_steps(args, cal, art) if s["id"] == "replay"][0]
    cmd_str = " ".join(str(a) for a in replay["cmd"])
    assert "--end-date" in cmd_str
    assert "2024-12-31" in cmd_str
    print("PASS test_build_steps_end_date_passthrough")


def test_build_steps_sweep_days_override():
    cal = Path("/tmp/cal7b/t9")
    art = cal / "artifacts"
    args = _Args(days=30, sweep_days=7)
    sweep = [s for s in build_steps(args, cal, art) if s["id"] == "replay-sweep"][0]
    cmd_str = " ".join(str(a) for a in sweep["cmd"])
    assert "--days 7" in cmd_str
    print("PASS test_build_steps_sweep_days_override")


# ---------------------------------------------------------------------------
# _dependency_failed
# ---------------------------------------------------------------------------

def test_dependency_failed_statuses():
    assert _dependency_failed("replay", {})
    assert _dependency_failed("replay", {"replay": {"status": "failed"}})
    assert _dependency_failed("replay", {"replay": {"status": "skipped-dependency"}})
    assert not _dependency_failed("replay", {"replay": {"status": "success"}})
    assert not _dependency_failed("replay", {"replay": {"status": "skipped"}})
    print("PASS test_dependency_failed_statuses")


# ---------------------------------------------------------------------------
# _load_json_safe
# ---------------------------------------------------------------------------

def test_load_json_safe_missing():
    assert _load_json_safe(Path("/nonexistent/foo.json")) is None
    print("PASS test_load_json_safe_missing")


def test_load_json_safe_valid():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"a": 1}, f)
        path = Path(f.name)
    assert _load_json_safe(path) == {"a": 1}
    path.unlink()
    print("PASS test_load_json_safe_valid")


# ---------------------------------------------------------------------------
# generate_summary_md
# ---------------------------------------------------------------------------

def test_generate_summary_md_minimal():
    cal = Path("/tmp/cal7b/2026-01-01")
    cal.mkdir(parents=True, exist_ok=True)
    steps = [
        {"id": "replay", "label": "Signal Replay", "cmd": ["python", "replay.py"]},
    ]
    results = {"replay": {"status": "success", "detail": "ok", "duration_sec": 5.0}}
    args = _Args()
    md = generate_summary_md(cal, results, steps, args)
    assert "# Calibration Workflow Summary" in md
    assert "## Parameters" in md
    assert "## Step Status" in md
    assert "## Commands Run" in md
    assert "| Signal Replay | success | 5.0s | ok |" in md
    assert "## Next Steps" in md
    print("PASS test_generate_summary_md_minimal")


def test_generate_summary_md_with_failures():
    cal = Path("/tmp/cal7b/fail-date")
    cal.mkdir(parents=True, exist_ok=True)
    steps = [
        {"id": "replay", "label": "Replay", "cmd": ["python", "replay.py"]},
        {"id": "dashboard", "label": "Dashboard", "cmd": ["python", "dash.py"]},
    ]
    results = {
        "replay": {"status": "failed", "detail": "exit 1 | error", "duration_sec": 12.0},
        "dashboard": {"status": "skipped-dependency", "detail": "dependency failed: replay"},
    }
    args = _Args()
    md = generate_summary_md(cal, results, steps, args)
    assert "## Failures" in md
    assert "replay" in md
    assert "exit 1" in md
    print("PASS test_generate_summary_md_with_failures")


def test_generate_summary_md_with_dashboard_data():
    cal = Path("/tmp/cal7b/dash-date")
    cal.mkdir(parents=True, exist_ok=True)
    dash = cal / "backtest-dashboard.json"
    dash.write_text(json.dumps({
        "replay": {"signals": 72, "hold_ratio": 0.67},
        "simulation": {"simulated_trades": 9, "win_rate": 0.89, "total_pnl_pct": 0.30,
                       "avg_pnl_pct": 0.033, "avg_hold_candles": 115.0},
        "warnings": ["warn1", "warn2"],
    }), encoding="utf-8")

    steps = [{"id": "replay", "label": "Replay", "cmd": ["python", "replay.py"]}]
    results = {"replay": {"status": "success", "detail": "ok", "duration_sec": 1.0}}
    args = _Args()
    md = generate_summary_md(cal, results, steps, args)
    assert "## Key Metrics" in md
    assert "72" in md
    assert "67%" in md
    assert "Warnings: 2" in md
    dash.unlink()
    print("PASS test_generate_summary_md_with_dashboard_data")


def test_generate_summary_md_with_recommendations_data():
    cal = Path("/tmp/cal7b/recs-date")
    cal.mkdir(parents=True, exist_ok=True)
    recs = cal / "parameter-recommendations.json"
    recs.write_text(json.dumps({
        "summary": {"total": 5, "high": 2, "medium": 2, "low": 1},
        "recommendations": [
            {"id": "R001", "priority": "high", "category": "data_quality",
             "finding": "Sample size too small"},
            {"id": "R003", "priority": "medium", "category": "exits",
             "finding": "Stale positions"},
        ],
    }), encoding="utf-8")

    steps = [{"id": "recs", "label": "Recs", "cmd": ["python", "recs.py"]}]
    results = {"recs": {"status": "success", "detail": "ok", "duration_sec": 1.0}}
    args = _Args()
    md = generate_summary_md(cal, results, steps, args)
    assert "## Top Recommendations" in md
    assert "5 total" in md
    assert "High: 2" in md
    assert "Sample size too small" in md
    assert "### High Priority" in md
    assert "### Medium Priority" in md
    recs.unlink()
    print("PASS test_generate_summary_md_with_recommendations_data")


def test_generate_summary_md_parameters_printed():
    cal = Path("/tmp/cal7b/params")
    cal.mkdir(parents=True, exist_ok=True)
    steps = [{"id": "replay", "label": "Replay", "cmd": ["python", "replay.py"]}]
    results = {"replay": {"status": "success", "detail": "ok", "duration_sec": 1.0}}
    from datetime import date
    args = _Args(symbols=["BTCUSDT", "ETHUSDT"], days=14, window=80, step=12,
                 sweep_days=3, use_sl_tp=True, baseline_only=True,
                 end_date=date(2024, 12, 31))
    md = generate_summary_md(cal, results, steps, args)
    assert "BTCUSDT, ETHUSDT" in md
    assert "14\n" in md or "Days: 14" in md
    assert "Sweep days: 3" in md
    assert "Window: 80" in md
    assert "Step: 12" in md
    assert "End date: 2024-12-31" in md
    assert "SL/TP: true" in md
    assert "Baseline only: true" in md
    print("PASS test_generate_summary_md_parameters_printed")


# ---------------------------------------------------------------------------
# Integration / main
# ---------------------------------------------------------------------------

def test_main_dry_run():
    """Test --dry-run exits 0 and prints expected content."""
    import subprocess
    result = subprocess.run(
        [PYTHON, str(project_root / "scripts/run_calibration_workflow.py"),
         "--symbols", "BTCUSDT", "ETHUSDT",
         "--days", "7", "--window", "40", "--step", "12",
         "--output-date", "dry-run-test",
         "--dry-run"],
        capture_output=True, text=True, timeout=30,
        cwd=str(project_root),
    )
    assert result.returncode == 0
    combined = result.stdout + result.stderr
    assert "DRY-RUN" in combined
    assert "dry-run-test" in combined
    print("PASS test_main_dry_run")


def test_main_all_skipped():
    """Test that skipping all steps succeeds."""
    import subprocess
    result = subprocess.run(
        [PYTHON, str(project_root / "scripts/run_calibration_workflow.py"),
         "--symbols", "BTCUSDT",
         "--days", "7", "--window", "40", "--step", "12",
         "--output-date", "all-skip",
         "--skip-replay", "--skip-replay-sweep", "--skip-simulation",
         "--skip-parameter-sweep", "--skip-dashboard", "--skip-recommendations"],
        capture_output=True, text=True, timeout=30,
        cwd=str(project_root),
    )
    assert result.returncode == 0
    combined = result.stdout + result.stderr
    assert "SKIP" in combined
    assert "Workflow Complete" in combined
    cal_dir = project_root / "reports/calibration/all-skip"
    assert (cal_dir / "workflow-summary.md").exists()
    print("PASS test_main_all_skipped")


def test_main_validates_conflicting_sl_tp():
    """Test that --use-sl-tp + --no-sl-tp exits 2."""
    import subprocess
    result = subprocess.run(
        [PYTHON, str(project_root / "scripts/run_calibration_workflow.py"),
         "--symbols", "BTCUSDT",
         "--use-sl-tp", "--no-sl-tp"],
        capture_output=True, text=True, timeout=30,
        cwd=str(project_root),
    )
    assert result.returncode == 2
    print("PASS test_main_validates_conflicting_sl_tp")


def test_main_validates_empty_symbols():
    """Test that no symbols exits 2."""
    import subprocess
    result = subprocess.run(
        [PYTHON, str(project_root / "scripts/run_calibration_workflow.py"),
         "--symbols"],
        capture_output=True, text=True, timeout=30,
        cwd=str(project_root),
    )
    assert result.returncode == 2
    print("PASS test_main_validates_empty_symbols")


# ---------------------------------------------------------------------------
# today_str / timestamp
# ---------------------------------------------------------------------------

def test_today_str_format():
    ts = today_str()
    assert len(ts) == 10
    assert ts.count("-") == 2
    print("PASS test_today_str_format")


def test_timestamp_format():
    ts = timestamp()
    assert "T" in ts
    assert len(ts) > 19
    print("PASS test_timestamp_format")


def run_all():
    with tempfile.TemporaryDirectory() as tmp:
        cal_base = Path(tmp) / "reports/calibration"
        cal_base.mkdir(parents=True, exist_ok=True)

        tests = [
            test_build_steps_default,
            test_build_steps_sl_tp_flag,
            test_build_steps_no_sl_tp_flag,
            test_build_steps_baseline_only,
            test_build_steps_skip_flags,
            test_build_steps_output_paths_are_dated,
            test_build_steps_symbols_in_cmd,
            test_build_steps_depends_set,
            test_build_steps_end_date_passthrough,
            test_build_steps_sweep_days_override,
            test_dependency_failed_statuses,
            test_load_json_safe_missing,
            test_load_json_safe_valid,
            test_generate_summary_md_minimal,
            test_generate_summary_md_with_failures,
            test_generate_summary_md_with_dashboard_data,
            test_generate_summary_md_with_recommendations_data,
            test_generate_summary_md_parameters_printed,
            test_main_dry_run,
            test_main_all_skipped,
            test_main_validates_conflicting_sl_tp,
            test_main_validates_empty_symbols,
            test_today_str_format,
            test_timestamp_format,
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

        if failures:
            print(f"\n{failures} test(s) failed")
            sys.exit(1)
        print(f"\nAll {len(tests)} tests passed")


if __name__ == "__main__":
    run_all()

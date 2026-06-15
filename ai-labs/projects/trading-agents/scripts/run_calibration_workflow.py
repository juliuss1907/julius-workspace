#!/usr/bin/env python3
"""
Calibration Workflow Orchestrator — Phase 7B.

Runs the full backtest-to-recommendations pipeline in sequence and
produces a dated calibration folder with all artifacts and a summary.

Does NOT auto-apply config. Every step is a subprocess invocation of
an existing script. Failed steps are recorded but do not halt the
workflow (unless a downstream step depends on the output).

Output structure:
  reports/calibration/YYYY-MM-DD/
    replay_signals.jsonl
    simulated_trades.jsonl
    simulation_summary.json
    parameter_sweep_report.json
    parameter_sweep_report.md
    replay_sweep_report.json
    replay_sweep_report.md
    backtest-dashboard.json
    backtest-dashboard.md
    parameter-recommendations.json
    parameter-recommendations.md
    workflow-summary.md
    artifacts/
      replay_sweep_variants/

Usage:
  ./venv/bin/python scripts/run_calibration_workflow.py \
    --symbols BTCUSDT ETHUSDT SOLUSDT \
    --days 30 --window 120 --step 24 --use-sl-tp
"""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, date
from pathlib import Path


def _parse_end_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"--end-date must be YYYY-MM-DD: {e}")

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


PYTHON = sys.executable


def today_str() -> str:
    return date.today().isoformat()


def timestamp() -> str:
    return datetime.now().isoformat()


STEP_DEFS = [
    {
        "id": "replay",
        "label": "Signal Replay",
        "skip_flag": "skip_replay",
        "depends_on": [],
    },
    {
        "id": "replay-sweep",
        "label": "Replay Parameter Sweep",
        "skip_flag": "skip_replay_sweep",
        "depends_on": [],
    },
    {
        "id": "simulation",
        "label": "Trade Simulation",
        "skip_flag": "skip_simulation",
        "depends_on": ["replay"],
    },
    {
        "id": "parameter-sweep",
        "label": "Parameter Sweep",
        "skip_flag": "skip_parameter_sweep",
        "depends_on": ["replay"],
    },
    {
        "id": "dashboard",
        "label": "Backtest Dashboard",
        "skip_flag": "skip_dashboard",
        "depends_on": ["replay", "simulation"],
    },
    {
        "id": "recommendations",
        "label": "Parameter Recommendations",
        "skip_flag": "skip_recommendations",
        "depends_on": ["dashboard"],
    },
]


def _flag_str(value):
    return "true" if value else "false"


def _args_to_cmd(args: list):
    return [str(a) for a in args]


def build_steps(args, cal_dir: Path, artifacts_dir: Path) -> list:
    """Build the list of step dictionaries with commands."""
    steps = []

    days = args.days
    window = args.window
    step_c = args.step
    sweep_days = args.sweep_days or days
    symbols = args.symbols

    replay_jsonl = cal_dir / "replay_signals.jsonl"
    simulated_jsonl = cal_dir / "simulated_trades.jsonl"
    sim_summary_json = cal_dir / "simulation_summary.json"
    param_sweep_json = cal_dir / "parameter_sweep_report.json"
    param_sweep_md = cal_dir / "parameter_sweep_report.md"
    replay_sweep_json = cal_dir / "replay_sweep_report.json"
    replay_sweep_md = cal_dir / "replay_sweep_report.md"
    dashboard_json = cal_dir / "backtest-dashboard.json"
    dashboard_md = cal_dir / "backtest-dashboard.md"
    recs_json = cal_dir / "parameter-recommendations.json"
    recs_md = cal_dir / "parameter-recommendations.md"

    for step_def in STEP_DEFS:
        sid = step_def["id"]
        label = step_def["label"]
        skip = getattr(args, step_def["skip_flag"], False)
        depends = step_def["depends_on"]

        if skip:
            steps.append({"id": sid, "label": label, "skip": True, "reason": "user skipped", "cmd": []})
            continue

        if sid == "replay":
            cmd = [PYTHON, str(project_root / "scripts/replay_signals.py"),
                   "--symbols"] + list(symbols) + [
                   "--days", str(days),
                   "--window", str(window),
                   "--step", str(step_c),
                   "--output", str(replay_jsonl),
                   ]
            if args.end_date:
                cmd.extend(["--end-date", args.end_date.isoformat()])
            steps.append({"id": sid, "label": label, "cmd": cmd, "outputs": [replay_jsonl],
                          "depends": depends, "skip": False})

        elif sid == "replay-sweep":
            cmd = [PYTHON, str(project_root / "scripts/replay_parameter_sweep.py"),
                   "--symbols"] + list(symbols) + [
                   "--days", str(sweep_days),
                   "--window", str(window),
                   "--step", str(step_c),
                   "--output-dir", str(artifacts_dir / "replay_sweep_variants"),
                   "--json-out", str(replay_sweep_json),
                   "--md-out", str(replay_sweep_md),
                   ]
            if args.baseline_only:
                cmd.append("--baseline-only")
            steps.append({"id": sid, "label": label, "cmd": cmd,
                          "outputs": [replay_sweep_json, replay_sweep_md, artifacts_dir / "replay_sweep_variants"],
                          "depends": depends, "skip": False})

        elif sid == "simulation":
            cmd = [PYTHON, str(project_root / "scripts/simulate_trades.py"),
                   "--input", str(replay_jsonl),
                   "--output", str(simulated_jsonl),
                   "--summary", str(sim_summary_json),
                   ]
            if args.use_sl_tp:
                cmd.append("--use-sl-tp")
            elif args.no_sl_tp:
                cmd.append("--no-sl-tp")
            steps.append({"id": sid, "label": label, "cmd": cmd,
                          "outputs": [simulated_jsonl, sim_summary_json],
                          "depends": depends, "skip": False})

        elif sid == "parameter-sweep":
            cmd = [PYTHON, str(project_root / "scripts/parameter_sweep.py"),
                   "--input", str(replay_jsonl),
                   "--json-out", str(param_sweep_json),
                   "--md-out", str(param_sweep_md),
                   ]
            steps.append({"id": sid, "label": label, "cmd": cmd,
                          "outputs": [param_sweep_json, param_sweep_md],
                          "depends": depends, "skip": False})

        elif sid == "dashboard":
            cmd = [PYTHON, str(project_root / "scripts/generate_backtest_dashboard.py"),
                   "--replay-input", str(replay_jsonl),
                   "--sim-summary", str(sim_summary_json),
                   "--trades-input", str(simulated_jsonl),
                   "--sweep-report", str(param_sweep_json),
                   "--replay-sweep-report", str(replay_sweep_json),
                   "--md-out", str(dashboard_md),
                   "--json-out", str(dashboard_json),
                   ]
            steps.append({"id": sid, "label": label, "cmd": cmd,
                          "outputs": [dashboard_json, dashboard_md],
                          "depends": depends, "skip": False})

        elif sid == "recommendations":
            config_path = str(args.config or (project_root / "config/default_params.yaml"))
            cmd = [PYTHON, str(project_root / "scripts/generate_parameter_recommendations.py"),
                   "--dashboard", str(dashboard_json),
                   "--sweep", str(param_sweep_json),
                   "--replay-sweep", str(replay_sweep_json),
                   "--config", config_path,
                   "--md-out", str(recs_md),
                   "--json-out", str(recs_json),
                   ]
            steps.append({"id": sid, "label": label, "cmd": cmd,
                          "outputs": [recs_json, recs_md],
                          "depends": depends, "skip": False})

    return steps


def _dependency_failed(dep_id: str, step_results: dict) -> bool:
    result = step_results.get(dep_id)
    if not result:
        return True
    return result.get("status") in ("failed", "skipped-dependency")


def _load_json_safe(path: Path):
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def generate_summary_md(cal_dir: Path, step_results: dict, steps: list, args) -> str:
    """Build the workflow-summary.md content."""
    lines = []
    lines.append("# Calibration Workflow Summary")
    lines.append("")
    lines.append(f"**Date:** {cal_dir.name}")
    lines.append(f"**Generated at:** {timestamp()}")
    lines.append("")
    lines.append("## Parameters")
    lines.append("")
    lines.append(f"- Symbols: {', '.join(args.symbols)}")
    lines.append(f"- Days: {args.days}")
    lines.append(f"- Sweep days: {args.sweep_days or args.days}")
    lines.append(f"- Window: {args.window}")
    lines.append(f"- Step: {args.step}")
    lines.append(f"- End date: {args.end_date.isoformat() if args.end_date else 'today'}")
    lines.append(f"- SL/TP: {_flag_str(args.use_sl_tp)}")
    lines.append(f"- Baseline only: {_flag_str(args.baseline_only)}")
    lines.append("")

    lines.append("## Step Status")
    lines.append("")
    lines.append("| Step | Status | Duration | Details |")
    lines.append("|------|--------|----------|---------|")
    for step in steps:
        sid = step["id"]
        label = step["label"]
        result = step_results.get(sid, {})
        status = result.get("status", "unknown")
        dur = result.get("duration_sec", 0) or 0
        detail = result.get("detail", "")
        if len(detail) > 60:
            detail = detail[:57] + "..."
        lines.append(f"| {label} | {status} | {dur:.1f}s | {detail} |")
    lines.append("")

    lines.append("## Commands Run")
    lines.append("")
    lines.append("```bash")
    for step in steps:
        if step.get("cmd"):
            lines.append(" ".join(str(a) for a in step["cmd"]))
    lines.append("```")
    lines.append("")

    dashboard_json = _load_json_safe(cal_dir / "backtest-dashboard.json")
    if dashboard_json:
        sim = dashboard_json.get("simulation") or {}
        rep = dashboard_json.get("replay") or {}
        lines.append("## Key Metrics")
        lines.append("")
        lines.append(f"- Replay signals: {rep.get('signals', 0)}")
        lines.append(f"- HOLD ratio: {rep.get('hold_ratio', 0)*100:.0f}%")
        lines.append(f"- Simulated trades: {sim.get('simulated_trades', 0)}")
        trades = sim.get("simulated_trades", 0)
        if trades > 0:
            lines.append(f"- Win rate: {sim.get('win_rate', 0)*100:.1f}%")
            lines.append(f"- Total PnL: {sim.get('total_pnl_pct', 0):+.2f}%")
            lines.append(f"- Avg PnL: {sim.get('avg_pnl_pct', 0):+.2f}%")
            lines.append(f"- Avg hold candles: {sim.get('avg_hold_candles', 0):.1f}")
        warnings = dashboard_json.get("warnings", [])
        if warnings:
            lines.append(f"- Warnings: {len(warnings)}")
        lines.append("")

    recs_json = _load_json_safe(cal_dir / "parameter-recommendations.json")
    if recs_json:
        recs = recs_json.get("recommendations") or []
        summ = recs_json.get("summary") or {}
        lines.append("## Top Recommendations")
        lines.append("")
        lines.append(f"- {summ.get('total', len(recs))} total")
        lines.append(f"  - High: {summ.get('high', 0)}")
        lines.append(f"  - Medium: {summ.get('medium', 0)}")
        lines.append(f"  - Low: {summ.get('low', 0)}")
        lines.append("")

        high_recs = [r for r in recs if r.get("priority") == "high"]
        if high_recs:
            lines.append("### High Priority")
            lines.append("")
            for r in high_recs:
                lines.append(f"- **{r.get('id')}** ({r.get('category')}): {r.get('finding')}")
            lines.append("")

        med_recs = [r for r in recs if r.get("priority") == "medium"]
        if med_recs:
            lines.append("### Medium Priority")
            lines.append("")
            for r in med_recs:
                lines.append(f"- **{r.get('id')}** ({r.get('category')}): {r.get('finding')}")
            lines.append("")

    any_failure = any(
        r.get("status") in ("failed", "skipped-dependency")
        for r in step_results.values()
    )
    if any_failure:
        lines.append("## Failures")
        lines.append("")
        for sid, r in step_results.items():
            if r.get("status") in ("failed", "skipped-dependency"):
                lines.append(f"- **{sid}**: {r.get('detail', 'unknown error')}")
        lines.append("")

    lines.append("## Next Steps")
    lines.append("")
    lines.append("1. Review the workflow summary above.")
    lines.append("2. Open `backtest-dashboard.md` for full diagnostics.")
    lines.append("3. Open `parameter-recommendations.md` for tuning suggestions.")
    lines.append("4. Make deliberate config edits — do NOT auto-apply.")
    lines.append("5. Re-run this workflow after config changes to verify impact.")
    lines.append("")

    return "\n".join(lines)


def run_workflow(args) -> int:
    cal_date = args.output_date or today_str()
    cal_dir = project_root / "reports/calibration" / cal_date
    artifacts_dir = cal_dir / "artifacts"
    cal_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    steps = build_steps(args, cal_dir, artifacts_dir)

    if args.dry_run:
        print(f"[DRY-RUN] Calibration date: {cal_date}")
        print(f"[DRY-RUN] Output: {cal_dir}")
        print()
        for step in steps:
            sid = step["id"]
            label = step["label"]
            if step.get("skip"):
                print(f"[SKIP] {label} — {step.get('reason', '')}")
            else:
                cmd_str = " ".join(str(a) for a in step["cmd"])
                print(f"[DRY-RUN] {label}:")
                print(f"  {cmd_str}")
        print()
        print(f"[DRY-RUN] Workflow would output {len(steps)} steps to {cal_dir}")
        return 0

    step_results = {}
    step_summaries = []

    for step in steps:
        sid = step["id"]
        label = step["label"]

        if step.get("skip"):
            step_results[sid] = {"status": "skipped", "detail": step.get("reason", "user skipped")}
            step_summaries.append(f"[SKIP] {label} — {step.get('reason', '')}")
            print(f"[SKIP] {label} — {step.get('reason', '')}")
            continue

        deps = step.get("depends", [])
        if deps:
            failed_deps = [d for d in deps if _dependency_failed(d, step_results)]
            if failed_deps:
                detail = f"dependency failed: {', '.join(failed_deps)}"
                step_results[sid] = {"status": "skipped-dependency", "detail": detail}
                step_summaries.append(f"[SKIP-DEP] {label} — {detail}")
                print(f"[SKIP-DEP] {label} — {detail}")
                continue

        cmd = step["cmd"]
        cmd_str = " ".join(str(a) for a in cmd)
        print(f"\n{'='*60}")
        print(f"[RUN] {label} ({sid})")
        print(f"  CMD: {cmd_str}")
        print(f"{'='*60}")

        t0 = time.monotonic()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=args.timeout or None,
                cwd=str(project_root),
            )
        except subprocess.TimeoutExpired:
            detail = "timeout"
            step_results[sid] = {"status": "failed", "detail": detail, "duration_sec": args.timeout}
            step_summaries.append(f"[FAIL] {label} — {detail}")
            print(f"[FAIL] {label} — {detail}")
            continue
        except Exception as e:
            detail = f"exception: {e}"
            step_results[sid] = {"status": "failed", "detail": detail}
            step_summaries.append(f"[FAIL] {label} — {detail}")
            print(f"[FAIL] {label} — {detail}")
            continue

        elapsed = time.monotonic() - t0

        out_preview = (result.stdout or "").strip()[-200:]
        err_preview = (result.stderr or "").strip()[-200:]

        if result.returncode == 0:
            detail = f"ok (exit 0)"
            step_results[sid] = {
                "status": "success",
                "detail": detail,
                "duration_sec": round(elapsed, 2),
                "stdout_tail": out_preview,
            }
            step_summaries.append(f"[OK] {label} — {detail} in {elapsed:.1f}s")
            print(f"[OK] {label} — {detail} in {elapsed:.1f}s")
        else:
            detail = f"exit {result.returncode}"
            if err_preview:
                detail += f" | {err_preview[-100:]}"
            step_results[sid] = {
                "status": "failed",
                "detail": detail,
                "duration_sec": round(elapsed, 2),
                "stderr_tail": err_preview,
            }
            step_summaries.append(f"[FAIL] {label} — {detail}")
            print(f"[FAIL] {label} — {detail}")
            if err_preview:
                print(f"  stderr tail: {err_preview}")

    print(f"\n{'='*60}")
    print("--- Workflow Complete ---")
    for s in step_summaries:
        print(s)

    summary_md = generate_summary_md(cal_dir, step_results, steps, args)
    summary_path = cal_dir / "workflow-summary.md"
    summary_path.write_text(summary_md, encoding="utf-8")
    print(f"\nWrote workflow summary to {summary_path}")

    any_failed = any(
        r.get("status") == "failed"
        for r in step_results.values()
    )
    return 1 if any_failed else 0


def main():
    parser = argparse.ArgumentParser(
        description="Run full calibration workflow — replay, sweep, simulate, dashboard, recommend"
    )
    parser.add_argument("--symbols", nargs="+", default=["BTCUSDT", "ETHUSDT", "SOLUSDT"])
    parser.add_argument("--days", type=int, default=30, help="Days of historical replay data")
    parser.add_argument("--sweep-days", type=int, default=None,
                        help="Days for replay sweep (default: same as --days)")
    parser.add_argument("--window", type=int, default=120, help="Candle window size")
    parser.add_argument("--step", type=int, default=24, help="Step candles (24 = ~24h)")
    parser.add_argument("--use-sl-tp", action="store_true", help="Enable SL/TP-aware exits")
    parser.add_argument("--no-sl-tp", action="store_true", help="Disable SL/TP-aware exits")
    parser.add_argument("--baseline-only", action="store_true",
                        help="Only run baseline replay sweep variant")
    parser.add_argument("--config", default=None, help="Path to default_params.yaml")
    parser.add_argument("--output-date", default=None,
                        help="Calibration date label (default: today)")
    parser.add_argument(
        "--end-date",
        type=_parse_end_date,
        default=None,
        help="End date for historical replay window (YYYY-MM-DD). Passed through to replay_signals.py.",
    )
    parser.add_argument("--timeout", type=int, default=None,
                        help="Timeout per step in seconds")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print planned commands without running")

    skip_group = parser.add_argument_group("skip flags")
    skip_group.add_argument("--skip-replay", action="store_true")
    skip_group.add_argument("--skip-replay-sweep", action="store_true")
    skip_group.add_argument("--skip-simulation", action="store_true")
    skip_group.add_argument("--skip-parameter-sweep", action="store_true")
    skip_group.add_argument("--skip-dashboard", action="store_true")
    skip_group.add_argument("--skip-recommendations", action="store_true")

    args = parser.parse_args()

    if args.use_sl_tp and args.no_sl_tp:
        print("Error: cannot set both --use-sl-tp and --no-sl-tp")
        sys.exit(2)

    if not args.symbols:
        print("Error: at least one symbol required")
        sys.exit(2)

    return run_workflow(args)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Manual read-only monitoring cadence runner.

Dry-run by default. Actual replay/monitoring execution requires --run.
This wrapper uses existing project scripts and does not import runtime trading,
dataflow, state, or agent modules at import time.
"""
import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
DEFAULT_BASELINE_INPUTS = [
    Path("logs/replay_signals-batch3f-2026-06-28.jsonl"),
    Path("logs/replay_signals-batch3g-2026-06-28.jsonl"),
]


@dataclass(frozen=True)
class CadencePaths:
    raw_replay_log: Path
    fresh_markdown: Path
    fresh_json: Path
    combined_markdown: Path
    combined_json: Path

    def outputs(self) -> List[Path]:
        return [self.raw_replay_log, self.fresh_markdown, self.fresh_json, self.combined_markdown, self.combined_json]

    def committable_reports(self) -> List[Path]:
        return [self.fresh_markdown, self.fresh_json, self.combined_markdown, self.combined_json]


def build_paths(date_tag: str) -> CadencePaths:
    return CadencePaths(
        raw_replay_log=Path(f"logs/replay_signals-batch3r-{date_tag}-core.jsonl"),
        fresh_markdown=Path(f"volatility-skip-monitoring-cadence-batch3r-{date_tag}.md"),
        fresh_json=Path(f"volatility-skip-monitoring-cadence-batch3r-{date_tag}.json"),
        combined_markdown=Path(f"volatility-skip-monitoring-combined-batch3r-{date_tag}.md"),
        combined_json=Path(f"volatility-skip-monitoring-combined-batch3r-{date_tag}.json"),
    )


def build_commands(args, paths: CadencePaths) -> Dict[str, List[str]]:
    python = args.python
    symbols = list(args.symbols)
    baseline_inputs = [str(path) for path in DEFAULT_BASELINE_INPUTS]
    return {
        "readiness": [python, "scripts/check_replay_dependency_readiness.py", "--json"],
        "replay": [python, "scripts/replay_signals.py", "--symbols", *symbols, "--days", str(args.days), "--window", str(args.window), "--step", str(args.step), "--output", str(paths.raw_replay_log)],
        "fresh_monitoring": [python, "scripts/run_volatility_skip_monitoring.py", "--inputs", str(paths.raw_replay_log), "--output", str(paths.fresh_markdown), "--json-output", str(paths.fresh_json)],
        "combined_monitoring": [python, "scripts/run_volatility_skip_monitoring.py", "--inputs", *baseline_inputs, str(paths.raw_replay_log), "--output", str(paths.combined_markdown), "--json-output", str(paths.combined_json)],
    }


def ensure_outputs_do_not_exist(paths: CadencePaths, overwrite: bool) -> None:
    if overwrite:
        return
    existing = [str(path) for path in paths.outputs() if path.exists()]
    if existing:
        raise FileExistsError("Refusing to overwrite existing cadence artifacts: " + ", ".join(existing))


def run_command(command: List[str]) -> int:
    print("$ " + " ".join(command))
    completed = subprocess.run(command, cwd=str(PROJECT_ROOT))
    return completed.returncode


def render_plan(args, paths: CadencePaths, commands: Dict[str, List[str]]) -> str:
    lines = [
        "Batch 3R manual read-only monitoring cadence",
        f"mode: {'RUN' if args.run else 'DRY-RUN'}",
        f"date_tag: {args.date_tag}",
        f"symbols: {' '.join(args.symbols)}",
        f"raw_replay_log: {paths.raw_replay_log}  # local-only, do not commit",
        "committable_reports:",
    ]
    lines.extend(f"  - {path}" for path in paths.committable_reports())
    lines.append("commands:")
    for name, command in commands.items():
        lines.append(f"  [{name}] " + " ".join(command))
    lines.append("scheduler_enabled: false")
    lines.append("live_trading_authorized: false")
    lines.append("order_placement_authorized: false")
    return "\n".join(lines) + "\n"


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Manual read-only replay plus volatility-skip monitoring cadence")
    parser.add_argument("--run", action="store_true", help="Actually execute replay and monitoring commands. Default is dry-run only.")
    parser.add_argument("--date-tag", default="manual", help="Date/run tag used in output filenames")
    parser.add_argument("--symbols", nargs="+", default=DEFAULT_SYMBOLS, help="Symbols for fresh replay collection")
    parser.add_argument("--days", type=int, default=14, help="Days of historical candles to replay")
    parser.add_argument("--window", type=int, default=200, help="Replay candle window size")
    parser.add_argument("--step", type=int, default=4, help="Replay candle step size")
    parser.add_argument("--python", default="venv/bin/python", help="Python interpreter for replay/monitoring scripts")
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting generated raw replay/report artifacts")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    paths = build_paths(args.date_tag)
    commands = build_commands(args, paths)
    print(render_plan(args, paths, commands), end="")
    if not args.run:
        print("DRY-RUN only. Re-run with --run to execute. Raw replay logs must not be committed.")
        return 0
    try:
        ensure_outputs_do_not_exist(paths, args.overwrite)
    except FileExistsError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for name in ("readiness", "replay", "fresh_monitoring", "combined_monitoring"):
        rc = run_command(commands[name])
        if rc != 0:
            print(f"ERROR: cadence step failed: {name} rc={rc}", file=sys.stderr)
            return rc
        if name == "replay" and not paths.raw_replay_log.exists():
            print(f"ERROR: replay step did not create {paths.raw_replay_log}", file=sys.stderr)
            return 3
    print("Cadence complete. Commit monitoring reports only; do not commit raw replay log:")
    print(f"  {paths.raw_replay_log}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

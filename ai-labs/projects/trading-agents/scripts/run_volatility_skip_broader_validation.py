#!/usr/bin/env python3
"""
Batch 3J broader replay validation for volatility-skip calibration.

Offline/replay-only. No live trading, no order placement, no runtime config
mutation, and no StrategySignal-to-order mapping.
"""
import argparse
import copy
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from statistics import mean
from typing import Dict, List, Sequence

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.evaluate_strategy_vs_trader import evaluate_strategy_vs_trader, load_replay_records, write_json, write_text  # noqa: E402
from scripts.run_volatility_skip_calibration import VARIANTS, rebuild_replay_records  # noqa: E402

DATE_TAG = "2026-06-29"
DEFAULT_VARIANTS = ("variant-d", "variant-b")
DEFAULT_INPUTS = (
    Path("logs/replay_signals-batch3f-2026-06-28.jsonl"),
    Path("logs/replay_signals-batch3g-2026-06-28.jsonl"),
)
CORE_RATE_KEYS = (
    "attribution_coverage_rate",
    "alignment_rate",
    "conflict_rate",
    "neutral_or_observational_rate",
    "directional_strategy_coverage_rate",
    "skip_during_trader_action_rate",
    "volatility_skip_direct_block_rate",
)


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _safe_name(path: Path) -> str:
    stem = path.name[:-6] if path.name.endswith(".jsonl") else path.name
    return "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in stem.lower()).strip("-") or "window"


def discover_default_inputs() -> List[Path]:
    """Return existing non-variant replay windows for broader validation."""
    return [path for path in DEFAULT_INPUTS if path.exists()]


def window_metadata(path: Path, records: List[Dict]) -> Dict:
    symbols = sorted({str(row.get("symbol")) for row in records if isinstance(row, dict) and row.get("symbol")})
    regimes = Counter()
    timeframes = Counter()
    for row in records:
        if not isinstance(row, dict):
            continue
        signal = row.get("strategy_signal")
        if isinstance(signal, dict):
            attribution = signal.get("attribution")
            if isinstance(attribution, dict):
                regime = attribution.get("regime") or attribution.get("market_regime")
                if regime:
                    regimes[str(regime)] += 1
        snapshot = row.get("market_snapshot")
        if isinstance(snapshot, dict):
            timeframes[str(snapshot.get("timeframe") or "unknown")] += 1
    return {
        "window_id": _safe_name(path),
        "source": str(path),
        "record_count": len(records),
        "symbols": symbols,
        "market_regime_counts": dict(sorted(regimes.items())),
        "timeframe_counts": dict(sorted(timeframes.items())),
    }


def load_windows(paths: Sequence[Path]) -> List[Dict]:
    windows = []
    for path in paths:
        records = load_replay_records(path)
        windows.append({"metadata": window_metadata(path, records), "records": records})
    return windows


def _status_map(evaluation: Dict) -> Dict[str, str]:
    return {key: value.get("status") for key, value in evaluation.get("gate_status", {}).items() if isinstance(value, dict)}


def _summary(evaluation: Dict) -> Dict:
    rates = evaluation.get("rates", {})
    counts = evaluation.get("counts", {})
    matrix = counts.get("action_matrix", {})
    actions = counts.get("strategy_action", {})
    return {
        "dataset": copy.deepcopy(evaluation.get("dataset", {})),
        "rates": {key: rates.get(key, 0.0) for key in CORE_RATE_KEYS},
        "action_matrix": {
            "BUY|skip": matrix.get("BUY|skip", 0),
            "SELL|skip": matrix.get("SELL|skip", 0),
            "BUY|long": matrix.get("BUY|long", 0),
            "SELL|short": matrix.get("SELL|short", 0),
            "BUY|short": matrix.get("BUY|short", 0),
            "SELL|long": matrix.get("SELL|long", 0),
            "HOLD|skip": matrix.get("HOLD|skip", 0),
            "HOLD|hold": matrix.get("HOLD|hold", 0),
        },
        "strategy_action": {
            "long": actions.get("long", 0),
            "short": actions.get("short", 0),
            "hold": actions.get("hold", 0),
            "skip": actions.get("skip", 0),
        },
        "strategy_id": copy.deepcopy(counts.get("strategy_id", {})),
        "strategy_family": copy.deepcopy(counts.get("strategy_family", {})),
        "market_regime": copy.deepcopy(counts.get("market_regime", {})),
        "gate_status": _status_map(evaluation),
    }


def _evaluate_candidate(records: List[Dict], candidate: str) -> Dict:
    if candidate == "baseline":
        candidate_records = records
    else:
        if candidate not in VARIANTS:
            raise ValueError(f"Unknown variant: {candidate}")
        candidate_records = rebuild_replay_records(records, VARIANTS[candidate]["strategy_config"], source=f"batch3j:{candidate}")
    return _summary(evaluate_strategy_vs_trader(candidate_records))


def evaluate_windows(windows: List[Dict], variants: Sequence[str]) -> List[Dict]:
    candidates = ["baseline"] + list(variants)
    results = []
    for window in windows:
        row = {"window": window["metadata"], "candidates": {}}
        for candidate in candidates:
            row["candidates"][candidate] = _evaluate_candidate(window["records"], candidate)
        results.append(row)
    return results


def aggregate_results(results: List[Dict], candidates: Sequence[str]) -> Dict:
    aggregate = {}
    for candidate in candidates:
        total_records = sum(row["candidates"][candidate]["dataset"].get("total_records", 0) for row in results)
        aggregate[candidate] = {"windows": len(results), "total_records": total_records, "rates": {}, "gate_status_counts": {}}
        for key in CORE_RATE_KEYS:
            values = [row["candidates"][candidate]["rates"].get(key, 0.0) for row in results]
            aggregate[candidate]["rates"][key] = {
                "mean": mean(values) if values else 0.0,
                "min": min(values) if values else 0.0,
                "max": max(values) if values else 0.0,
                "range": (max(values) - min(values)) if values else 0.0,
            }
        statuses = Counter()
        for row in results:
            for gate, status in row["candidates"][candidate].get("gate_status", {}).items():
                statuses[f"{gate}:{status}"] += 1
        aggregate[candidate]["gate_status_counts"] = dict(sorted(statuses.items()))
    return aggregate


def build_flags(results: List[Dict], variants: Sequence[str]) -> List[Dict]:
    flags = []
    for row in results:
        window_id = row["window"]["window_id"]
        baseline_rates = row["candidates"]["baseline"]["rates"]
        for variant in variants:
            summary = row["candidates"][variant]
            rates = summary["rates"]
            matrix = summary["action_matrix"]
            if rates.get("conflict_rate", 0.0) > baseline_rates.get("conflict_rate", 0.0):
                flags.append({"severity": "regression", "window_id": window_id, "candidate": variant, "metric": "conflict_rate", "message": "Conflict rate increased versus baseline."})
            if rates.get("attribution_coverage_rate", 0.0) < baseline_rates.get("attribution_coverage_rate", 0.0):
                flags.append({"severity": "regression", "window_id": window_id, "candidate": variant, "metric": "attribution_coverage_rate", "message": "Attribution coverage degraded versus baseline."})
            if rates.get("directional_strategy_coverage_rate", 0.0) < baseline_rates.get("directional_strategy_coverage_rate", 0.0):
                flags.append({"severity": "watch", "window_id": window_id, "candidate": variant, "metric": "directional_strategy_coverage_rate", "message": "Directional strategy coverage decreased versus baseline."})
            if baseline_rates.get("volatility_skip_direct_block_rate", 0.0) > 0.0 and rates.get("volatility_skip_direct_block_rate", 0.0) == 0.0:
                flags.append({"severity": "watch", "window_id": window_id, "candidate": variant, "metric": "volatility_skip_direct_block_rate", "message": "Volatility-skip direct block rate dropped to 0.0%; confirm de-overblocking rather than over-relaxation."})
            if matrix.get("BUY|short", 0) or matrix.get("SELL|long", 0):
                flags.append({"severity": "regression", "window_id": window_id, "candidate": variant, "metric": "action_matrix", "message": "Hard directional conflict pair appeared in action matrix."})
    return flags


def _candidate_has_regression(flags: List[Dict], candidate: str) -> bool:
    return any(flag.get("candidate") == candidate and flag.get("severity") == "regression" for flag in flags)


def _mean_delta(aggregate: Dict, candidate: str, key: str) -> float:
    return aggregate[candidate]["rates"][key]["mean"] - aggregate["baseline"]["rates"][key]["mean"]


def make_recommendation(results: List[Dict], aggregate: Dict, flags: List[Dict], variants: Sequence[str]) -> Dict:
    windows = len(results)
    total_records = sum(row["window"].get("record_count", 0) for row in results)
    if "variant-d" in variants and not _candidate_has_regression(flags, "variant-d"):
        primary = "variant-d"
    elif "variant-b" in variants and not _candidate_has_regression(flags, "variant-b"):
        primary = "variant-b"
    else:
        primary = None
    if primary == "variant-d" and windows >= 2 and total_records >= 100:
        confidence = "medium"
        outcome = "Variant D remains the safer primary candidate for another review step."
    elif primary:
        confidence = "low"
        outcome = f"{primary} has no hard regression, but replay coverage remains limited."
    else:
        confidence = "low"
        outcome = "No candidate is ready; collect more replay data or design a narrower Variant E."
    zero_watch = any(flag.get("metric") == "volatility_skip_direct_block_rate" for flag in flags)
    next_step = "Batch 3K — targeted review of zero volatility-skip block behavior before runtime/default changes" if zero_watch else "Batch 3K — approval-gated implementation design if Julius wants runtime calibration"
    return {
        "outcome": outcome,
        "primary_candidate": primary,
        "secondary_candidate": "variant-b" if primary == "variant-d" and "variant-b" in variants else None,
        "confidence": confidence,
        "reason": (
            f"Validated {len(variants)} replay-only variants across {windows} windows / {total_records} records. "
            f"Variant D directional mean delta={_mean_delta(aggregate, 'variant-d', 'directional_strategy_coverage_rate') if 'variant-d' in variants else 0.0:.4f}; "
            f"Variant D skip-during-action mean delta={_mean_delta(aggregate, 'variant-d', 'skip_during_trader_action_rate') if 'variant-d' in variants else 0.0:.4f}."
        ),
        "next_step": next_step,
        "production_change_authorized": False,
        "implementation_authorized": False,
        "requires_approval_before_runtime_change": True,
    }


def build_report(windows: List[Dict], variants: Sequence[str]) -> Dict:
    results = evaluate_windows(windows, variants)
    candidates = ["baseline"] + list(variants)
    aggregate = aggregate_results(results, candidates)
    flags = build_flags(results, variants)
    recommendation = make_recommendation(results, aggregate, flags, variants)
    return {
        "batch": "3J",
        "mode": "offline_replay_only",
        "production_change_authorized": False,
        "implementation_authorized": False,
        "requires_approval_before_runtime_change": True,
        "candidates": candidates,
        "windows": [row["metadata"] for row in windows],
        "results": results,
        "aggregate": aggregate,
        "regression_flags": flags,
        "recommendation": recommendation,
        "scope_boundary": "No live trading, order placement, StrategySignal-to-order mapping, production config/default changes, or runtime semantic changes.",
    }


def _agg_cell(aggregate: Dict, candidate: str, key: str) -> str:
    row = aggregate[candidate]["rates"][key]
    return f"| {candidate} | {key} | {_pct(row['mean'])} | {_pct(row['min'])} | {_pct(row['max'])} | {_pct(row['range'])} |"


def render_markdown_report(report: Dict) -> str:
    rec = report["recommendation"]
    lines = [
        "# Batch 3J — Broader Replay Validation for Volatility-Skip Calibration",
        "",
        "## Executive Summary",
        "",
        f"- Mode: {report['mode']}",
        f"- Windows evaluated: {len(report['windows'])}",
        f"- Candidates: {', '.join(report['candidates'])}",
        f"- Production change authorized: {str(report['production_change_authorized']).lower()}",
        f"- Implementation authorized: {str(report['implementation_authorized']).lower()}",
        f"- Requires approval before runtime change: {str(report['requires_approval_before_runtime_change']).lower()}",
        f"- Recommendation: {rec['outcome']}",
        "",
        "## Scope Boundary",
        "",
        report["scope_boundary"],
        "",
        "## Replay Windows",
        "",
        "| Window | Source | Records | Symbols | Regimes |",
        "|---|---|---:|---|---|",
    ]
    for window in report["windows"]:
        regimes = ", ".join(f"{k}:{v}" for k, v in window.get("market_regime_counts", {}).items()) or "unknown"
        symbols = ", ".join(window.get("symbols", [])) or "unknown"
        lines.append(f"| {window['window_id']} | {window['source']} | {window['record_count']} | {symbols} | {regimes} |")
    lines.extend(["", "## Aggregate Core Metrics", "", "| Candidate | Metric | Mean | Min | Max | Range |", "|---|---|---:|---:|---:|---:|"])
    for candidate in report["candidates"]:
        for key in CORE_RATE_KEYS:
            lines.append(_agg_cell(report["aggregate"], candidate, key))
    lines.extend(["", "## Per-Window Candidate Comparison", "", "| Window | Candidate | Records | Align | Conflict | Directional | Skip During Action | Vol-Skip Block | BUY/skip | SELL/skip | BUY/long | SELL/short |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"])
    for row in report["results"]:
        for candidate in report["candidates"]:
            summary = row["candidates"][candidate]
            rates = summary["rates"]
            matrix = summary["action_matrix"]
            lines.append(
                f"| {row['window']['window_id']} | {candidate} | {summary['dataset'].get('total_records', 0)} | {_pct(rates['alignment_rate'])} | {_pct(rates['conflict_rate'])} | {_pct(rates['directional_strategy_coverage_rate'])} | {_pct(rates['skip_during_trader_action_rate'])} | {_pct(rates['volatility_skip_direct_block_rate'])} | {matrix['BUY|skip']} | {matrix['SELL|skip']} | {matrix['BUY|long']} | {matrix['SELL|short']} |"
            )
    lines.extend(["", "## Regression / Watch Flags", "", "| Severity | Window | Candidate | Metric | Message |", "|---|---|---|---|---|"])
    if report["regression_flags"]:
        for flag in report["regression_flags"]:
            lines.append(f"| {flag['severity']} | {flag['window_id']} | {flag['candidate']} | {flag['metric']} | {flag['message']} |")
    else:
        lines.append("| none | all | all | n/a | No regression/watch flags generated. |")
    lines.extend([
        "", "## Variant Interpretation", "",
        "- Variant D is treated as the safer primary candidate because it changes fewer assumptions than Variant B.",
        "- Variant B remains an aggressive stress-test candidate because it allows volatile breakout replay behavior.",
        "- A 0.0% volatility-skip direct block rate is not automatically good; it requires follow-up review for over-relaxation.",
        "- These metrics remain observational and do not authorize production/default threshold changes.",
        "", "## Recommendation", "",
        f"- Outcome: {rec['outcome']}",
        f"- Primary candidate: {rec['primary_candidate']}",
        f"- Secondary candidate: {rec['secondary_candidate']}",
        f"- Confidence: {rec['confidence']}",
        f"- Reason: {rec['reason']}",
        f"- Next step: {rec['next_step']}",
        "", "## Decision Block", "", "~~~text", "Batch 3J Decision:",
        f"- Production change authorized: {str(rec['production_change_authorized']).lower()}",
        "- Runtime/default config change: not performed",
        f"- Primary candidate: {rec['primary_candidate']}",
        f"- Secondary candidate: {rec['secondary_candidate']}",
        f"- Confidence: {rec['confidence']}",
        f"- Reason: {rec['reason']}",
        f"- Next batch: {rec['next_step']}",
        "~~~", "",
    ])
    return "\n".join(lines)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Run Batch 3J broader replay validation for volatility-skip calibration")
    parser.add_argument("--inputs", nargs="+", type=Path, default=None, help="Replay JSONL windows to evaluate")
    parser.add_argument("--variants", nargs="+", default=list(DEFAULT_VARIANTS), choices=sorted(VARIANTS), help="Replay-only variants to compare")
    parser.add_argument("--output", type=Path, default=Path(f"volatility-skip-broader-validation-batch3j-{DATE_TAG}.md"))
    parser.add_argument("--json-output", type=Path, default=Path(f"volatility-skip-broader-validation-batch3j-{DATE_TAG}.json"))
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting Batch 3J report artifacts")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        inputs = args.inputs if args.inputs is not None else discover_default_inputs()
        if not inputs:
            raise FileNotFoundError("No replay input windows found; pass --inputs explicitly.")
        for path in inputs:
            if not path.exists():
                raise FileNotFoundError(f"Replay input not found: {path}")
        if not args.overwrite:
            for path in (args.output, args.json_output):
                if path.exists():
                    raise FileExistsError(f"Refusing to overwrite existing artifact: {path}")
        report = build_report(load_windows(inputs), args.variants)
        write_text(args.output, render_markdown_report(report))
        write_json(args.json_output, report)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Wrote broader validation markdown: {args.output}")
    print(f"Wrote broader validation JSON: {args.json_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Batch 3O post-implementation volatility-skip monitoring runner.

Offline/replay-only monitoring for the approved variant-d default config. This
script rebuilds StrategySignal attribution from replay artifacts using the
current default strategy_layer config, evaluates Batch 4B metrics, and emits
pass/watch/fail monitoring alerts.

It does not fetch market data, read .env, run live/paper trading loops, place
orders, or map StrategySignal into executable actions.
"""
import argparse
import copy
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.evaluate_strategy_vs_trader import evaluate_strategy_vs_trader, load_replay_records, write_json, write_text  # noqa: E402
from strategies.attribution import build_strategy_signal  # noqa: E402
from utils.config_loader import Config  # noqa: E402

DATE_TAG = "2026-07-01"
DEFAULT_INPUTS = (
    Path("logs/replay_signals-batch3f-2026-06-28.jsonl"),
    Path("logs/replay_signals-batch3g-2026-06-28.jsonl"),
)
EXPECTED_VARIANT_D = {
    "regime_strategy_order.volatile": ["volatility_skip", "trend_following", "breakout"],
    "volatility_skip.volatile_confidence_floor": 0.75,
    "volatility_skip.high_atr_pct": 0.10,
    "trend_following.allow_volatile_trend_up": True,
    "trend_following.allow_volatile_trend_down": True,
    "trend_following.min_regime_confidence": 0.50,
    "selection.min_action_confidence": 0.50,
    "breakout.allow_volatile": False,
}


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _safe_name(path: Path) -> str:
    stem = path.name[:-6] if path.name.endswith(".jsonl") else path.name
    return "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in stem.lower()).strip("-") or "window"


def discover_default_inputs() -> List[Path]:
    """Return existing non-variant replay windows for monitoring."""
    return [path for path in DEFAULT_INPUTS if path.exists()]


def get_nested(data: Dict, dotted: str):
    cur = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def load_strategy_layer_config() -> Dict:
    """Load current default strategy_layer config without runtime loops."""
    default_config = Config().load_default_params() or {}
    strategy_config = default_config.get("strategy_layer", {}) or {}
    if not isinstance(strategy_config, dict):
        return {}
    return strategy_config


def verify_variant_d_config(strategy_config: Dict) -> Dict:
    """Verify current config still matches approved Batch 3M variant-d surface."""
    checks = {}
    for key, expected in EXPECTED_VARIANT_D.items():
        actual = get_nested(strategy_config, key)
        checks[key] = {"expected": expected, "actual": actual, "matches": actual == expected}
    return {
        "matches_variant_d": all(row["matches"] for row in checks.values()),
        "breakout_allow_volatile_default": get_nested(strategy_config, "breakout.allow_volatile"),
        "checks": checks,
    }


def _extract_technical_analysis(record: Dict) -> Dict:
    analysts = record.get("analysts")
    if not isinstance(analysts, dict):
        return {}
    technical = analysts.get("technical")
    if not isinstance(technical, dict):
        return {}
    analysis = technical.get("analysis")
    return analysis if isinstance(analysis, dict) else {}


def rebuild_records_with_current_config(records: Sequence[Dict], strategy_config: Dict) -> List[Dict]:
    """Rebuild StrategySignal in replay records using current default config."""
    rebuilt = []
    for record in records:
        next_record = copy.deepcopy(record)
        signal = build_strategy_signal(
            technical_analysis=_extract_technical_analysis(next_record),
            strategy_config=strategy_config,
            source="batch3o:current-default-monitoring",
        )
        attribution = signal.get("attribution", {}) or {}
        attribution["monitoring"] = {"batch": "3O", "current_default_config": True}
        signal["attribution"] = attribution
        next_record["strategy_signal"] = signal
        rebuilt.append(next_record)
    return rebuilt


def _is_original_volatile(signal: Dict) -> bool:
    attribution = signal.get("attribution") if isinstance(signal, dict) else None
    if not isinstance(attribution, dict):
        return False
    return attribution.get("original_regime") == "volatile" or attribution.get("regime") == "volatile" or attribution.get("market_regime") == "volatile"


def monitoring_counts(records: Sequence[Dict]) -> Dict:
    volatile_trend = 0
    volatile_breakout = 0
    fallback_or_missing = 0
    by_strategy = Counter()
    by_action = Counter()
    for record in records:
        signal = record.get("strategy_signal") if isinstance(record, dict) else None
        if not isinstance(signal, dict) or not signal:
            fallback_or_missing += 1
            continue
        strategy_id = str(signal.get("strategy_id") or "unknown")
        family = str(signal.get("family") or "unknown")
        action = str(signal.get("action") or "unknown")
        by_strategy[strategy_id] += 1
        by_action[action] += 1
        if strategy_id == "registry" or family == "registry":
            fallback_or_missing += 1
        if family == "trend_following" and _is_original_volatile(signal):
            volatile_trend += 1
        if family == "breakout" and _is_original_volatile(signal):
            volatile_breakout += 1
    return {
        "volatile_trend_following_selected_count": volatile_trend,
        "volatile_breakout_selected_count": volatile_breakout,
        "fallback_or_missing_state_count": fallback_or_missing,
        "strategy_id_distribution": dict(sorted(by_strategy.items())),
        "strategy_action_distribution": dict(sorted(by_action.items())),
    }


def evaluate_window(path: Path, strategy_config: Dict) -> Dict:
    original_records = load_replay_records(path)
    rebuilt_records = rebuild_records_with_current_config(original_records, strategy_config)
    evaluation = evaluate_strategy_vs_trader(rebuilt_records)
    counts = monitoring_counts(rebuilt_records)
    action_matrix = evaluation.get("counts", {}).get("action_matrix", {})
    hard_conflict_count = action_matrix.get("BUY|short", 0) + action_matrix.get("SELL|long", 0)
    return {
        "window_id": _safe_name(path),
        "source": str(path),
        "record_count": len(rebuilt_records),
        "evaluation": evaluation,
        "monitoring_counts": {**counts, "hard_conflict_count": hard_conflict_count},
    }



def candidate_level_counts(record: Dict) -> Dict:
    """Return additive Batch 3W candidate-level counts from strategy attribution."""
    counts = {
        "volatility_skip_evaluated_count": 0,
        "volatility_skip_selected_hold_count": 0,
        "volatility_skip_evaluated_not_selected_count": 0,
        "volatility_skip_action_override_count": 0,
        "volatility_skip_threshold_failed_count": 0,
        "volatility_skip_confidence_floor_failed_count": 0,
    }
    strategy = record.get("strategy_signal") or {}
    attribution = strategy.get("attribution") or {}
    evaluated = attribution.get("evaluated") or []
    if not isinstance(evaluated, list):
        return counts
    for candidate in evaluated:
        if not isinstance(candidate, dict):
            continue
        family = str(candidate.get("family") or "").replace("-", "_")
        strategy_id = str(candidate.get("strategy_id") or "").replace("-", "_")
        if family != "volatility_skip" and strategy_id != "volatility_skip":
            continue
        counts["volatility_skip_evaluated_count"] += 1
        selected = candidate.get("selected") is True
        action = candidate.get("action")
        if selected and action == "hold":
            counts["volatility_skip_selected_hold_count"] += 1
        if not selected:
            counts["volatility_skip_evaluated_not_selected_count"] += 1
        if candidate.get("rejection_reason") == "hold_candidate_overridden_by_action_candidate":
            counts["volatility_skip_action_override_count"] += 1
        observed = candidate.get("observed") or {}
        thresholds = candidate.get("thresholds") or {}
        atr_pct = observed.get("atr_pct")
        high_atr_pct = thresholds.get("high_atr_pct")
        if isinstance(atr_pct, (int, float)) and isinstance(high_atr_pct, (int, float)) and atr_pct < high_atr_pct:
            counts["volatility_skip_threshold_failed_count"] += 1
        regime_confidence = observed.get("regime_confidence")
        confidence_floor = thresholds.get("volatile_confidence_floor")
        if isinstance(regime_confidence, (int, float)) and isinstance(confidence_floor, (int, float)) and regime_confidence < confidence_floor:
            counts["volatility_skip_confidence_floor_failed_count"] += 1
    return counts

def aggregate_windows(per_window: Sequence[Dict]) -> Dict:
    total_records = sum(row.get("record_count", 0) for row in per_window)
    hard_conflicts = sum(row["monitoring_counts"].get("hard_conflict_count", 0) for row in per_window)
    volatile_trend = sum(row["monitoring_counts"].get("volatile_trend_following_selected_count", 0) for row in per_window)
    volatile_breakout = sum(row["monitoring_counts"].get("volatile_breakout_selected_count", 0) for row in per_window)
    fallback_or_missing = sum(row["monitoring_counts"].get("fallback_or_missing_state_count", 0) for row in per_window)
    weighted = {}
    rate_keys = [
        "attribution_coverage_rate",
        "alignment_rate",
        "conflict_rate",
        "directional_strategy_coverage_rate",
        "skip_during_trader_action_rate",
        "volatility_skip_direct_block_rate",
    ]
    for key in rate_keys:
        numerator = 0.0
        for row in per_window:
            records = row.get("record_count", 0)
            rate = row.get("evaluation", {}).get("rates", {}).get(key, 0.0)
            numerator += records * rate
        weighted[key] = (numerator / total_records) if total_records else 0.0
    return {
        "windows": len(per_window),
        "total_records": total_records,
        "hard_conflict_count": hard_conflicts,
        "volatile_trend_following_selected_count": volatile_trend,
        "volatile_breakout_selected_count": volatile_breakout,
        "fallback_or_missing_state_count": fallback_or_missing,
        "rates_weighted_by_records": weighted,
    }


def build_alerts(config_check: Dict, aggregate: Dict) -> List[Dict]:
    alerts = []
    total = aggregate.get("total_records", 0) or 0
    rates = aggregate.get("rates_weighted_by_records", {})
    def add(level, metric, message):
        alerts.append({"level": level, "metric": metric, "message": message})

    if not config_check.get("matches_variant_d"):
        add("fail", "current_config_matches_variant_d", "Current strategy_layer config no longer matches approved variant-d values.")
    if config_check.get("breakout_allow_volatile_default") is not False:
        add("fail", "breakout_allow_volatile_default", "breakout.allow_volatile must remain false for variant-d default config.")
    if aggregate.get("hard_conflict_count", 0) > 0:
        add("fail", "hard_conflict_count", "Hard BUY|short or SELL|long conflict detected.")
    if aggregate.get("volatile_breakout_selected_count", 0) > 0:
        add("fail", "volatile_breakout_selected_count", "Volatile breakout was selected; this should remain disabled by default.")
    if rates.get("attribution_coverage_rate", 0.0) < 0.95:
        add("fail", "attribution_coverage_rate", "Attribution coverage dropped below 95%.")

    if total < 100:
        add("watch", "sample_size", "Replay sample remains small; collect broader data before higher confidence decisions.")
    if total and rates.get("volatility_skip_direct_block_rate", 0.0) == 0.0:
        add("watch", "volatility_skip_direct_block_rate", "Volatility-skip direct block rate is 0.0%; continue watching for over-relaxation.")
    if rates.get("directional_strategy_coverage_rate", 0.0) >= 0.20:
        add("watch", "directional_strategy_coverage_rate", "Directional strategy coverage is high relative to prior sparse baseline.")
    if total and aggregate.get("volatile_trend_following_selected_count", 0) / total >= 0.20:
        add("watch", "volatile_trend_following_selected_count", "Volatile trend-following selection share is high; review future samples.")
    if aggregate.get("fallback_or_missing_state_count", 0) > 0:
        add("watch", "fallback_or_missing_state_count", "Fallback or missing-state records were observed.")
    return alerts


def status_from_alerts(alerts: Sequence[Dict]) -> str:
    if any(alert.get("level") == "fail" for alert in alerts):
        return "fail"
    if any(alert.get("level") == "watch" for alert in alerts):
        return "watch"
    return "pass"


def build_report(inputs: Sequence[Path]) -> Dict:
    strategy_config = load_strategy_layer_config()
    config_check = verify_variant_d_config(strategy_config)
    per_window = [evaluate_window(path, strategy_config) for path in inputs]
    aggregate = aggregate_windows(per_window)
    alerts = build_alerts(config_check, aggregate)
    status = status_from_alerts(alerts)
    recommendation = {
        "outcome": (
            "Monitoring pass; keep variant-d default config." if status == "pass" else
            "Monitoring watch; keep variant-d but collect broader replay data before further runtime expansion." if status == "watch" else
            "Monitoring fail; stop and ask Julius whether to rollback Batch 3M."
        ),
        "next_batch": (
            "Batch 3P — monitoring automation schedule or broader replay collection." if status == "pass" else
            "Batch 3P — collect broader replay dataset and review watch alerts." if status == "watch" else
            "Rollback/escalation decision before further changes."
        ),
    }
    return {
        "batch": "3O",
        "mode": "post_implementation_monitoring",
        "runtime_default_config_change_performed": False,
        "monitoring_inputs": [str(path) for path in inputs],
        "current_config": config_check,
        "metrics": {"aggregate": aggregate, "per_window": per_window},
        "alerts": alerts,
        "status": status,
        "recommendation": recommendation,
        "scope_boundary": "Monitoring only: no live trading, order placement, StrategySignal-to-order mapping, or runtime/default config changes.",
    }


def render_markdown(report: Dict) -> str:
    aggregate = report["metrics"]["aggregate"]
    rates = aggregate["rates_weighted_by_records"]
    lines = [
        "# Batch 3O — Volatility-Skip Post-Implementation Monitoring",
        "",
        "## Executive Summary",
        "",
        f"- Mode: {report['mode']}",
        f"- Status: {report['status']}",
        f"- Runtime/default config change performed in Batch 3O: {str(report['runtime_default_config_change_performed']).lower()}",
        f"- Monitoring inputs: {', '.join(report['monitoring_inputs'])}",
        f"- Recommendation: {report['recommendation']['outcome']}",
        "",
        "## Current Config Verification",
        "",
        "| Key | Expected | Actual | Matches |",
        "|---|---|---|---|",
    ]
    for key, row in report["current_config"]["checks"].items():
        lines.append(f"| {key} | {row['expected']} | {row['actual']} | {str(row['matches']).lower()} |")
    lines.extend([
        "",
        "## Aggregate Monitoring Metrics",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| total_records | {aggregate['total_records']} |",
        f"| hard_conflict_count | {aggregate['hard_conflict_count']} |",
        f"| volatile_trend_following_selected_count | {aggregate['volatile_trend_following_selected_count']} |",
        f"| volatile_breakout_selected_count | {aggregate['volatile_breakout_selected_count']} |",
        f"| fallback_or_missing_state_count | {aggregate['fallback_or_missing_state_count']} |",
        f"| attribution_coverage_rate | {_pct(rates['attribution_coverage_rate'])} |",
        f"| directional_strategy_coverage_rate | {_pct(rates['directional_strategy_coverage_rate'])} |",
        f"| skip_during_trader_action_rate | {_pct(rates['skip_during_trader_action_rate'])} |",
        f"| volatility_skip_direct_block_rate | {_pct(rates['volatility_skip_direct_block_rate'])} |",
        "",
        "## Alerts",
        "",
        "| Level | Metric | Message |",
        "|---|---|---|",
    ])
    if report["alerts"]:
        for alert in report["alerts"]:
            lines.append(f"| {alert['level']} | {alert['metric']} | {alert['message']} |")
    else:
        lines.append("| pass | none | No monitoring alerts. |")
    lines.extend([
        "",
        "## Per-Window Summary",
        "",
        "| Window | Records | Hard conflicts | Volatile trend-following | Volatile breakout | Vol-skip block rate | Directional rate |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report["metrics"]["per_window"]:
        r = row["evaluation"]["rates"]
        c = row["monitoring_counts"]
        lines.append(
            f"| {row['window_id']} | {row['record_count']} | {c['hard_conflict_count']} | "
            f"{c['volatile_trend_following_selected_count']} | {c['volatile_breakout_selected_count']} | "
            f"{_pct(r['volatility_skip_direct_block_rate'])} | {_pct(r['directional_strategy_coverage_rate'])} |"
        )
    lines.extend([
        "",
        "## Boundary Confirmation",
        "",
        "- No runtime/default config changes were made by Batch 3O.",
        "- No live trading, order placement, or StrategySignal-to-order mapping was introduced.",
        "- Raw replay logs remain local/ignored and were not committed.",
        "",
        "## Recommendation",
        "",
        f"- Outcome: {report['recommendation']['outcome']}",
        f"- Next batch: {report['recommendation']['next_batch']}",
        "",
        "## Decision Block",
        "",
        "~~~text",
        "Batch 3O Decision:",
        f"- Runtime/default config change performed in Batch 3O: {str(report['runtime_default_config_change_performed']).lower()}",
        f"- Current config matches variant-d: {str(report['current_config']['matches_variant_d']).lower()}",
        f"- Volatile breakout selected count: {aggregate['volatile_breakout_selected_count']}",
        f"- Hard conflict count: {aggregate['hard_conflict_count']}",
        f"- Monitoring status: {report['status']}",
        f"- Recommendation: {report['recommendation']['outcome']}",
        f"- Next batch: {report['recommendation']['next_batch']}",
        "~~~",
        "",
    ])
    return "\n".join(lines)


def write_jsonl(path: Path, rows: Iterable[Dict]) -> None:
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Run Batch 3O volatility-skip post-implementation monitoring")
    parser.add_argument("--inputs", nargs="+", type=Path, default=None, help="Replay JSONL windows to monitor")
    parser.add_argument("--output", type=Path, default=Path(f"volatility-skip-monitoring-batch3o-{DATE_TAG}.md"))
    parser.add_argument("--json-output", type=Path, default=Path(f"volatility-skip-monitoring-batch3o-{DATE_TAG}.json"))
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting Batch 3O monitoring reports")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        inputs = args.inputs if args.inputs is not None else discover_default_inputs()
        if not inputs:
            raise FileNotFoundError("No replay inputs found; pass --inputs explicitly.")
        for path in inputs:
            if not path.exists():
                raise FileNotFoundError(f"Replay input not found: {path}")
        if not args.overwrite:
            for path in (args.output, args.json_output):
                if path.exists():
                    raise FileExistsError(f"Refusing to overwrite existing artifact: {path}")
        report = build_report(inputs)
        write_text(args.output, render_markdown(report))
        write_json(args.json_output, report)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Wrote monitoring markdown: {args.output}")
    print(f"Wrote monitoring JSON: {args.json_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

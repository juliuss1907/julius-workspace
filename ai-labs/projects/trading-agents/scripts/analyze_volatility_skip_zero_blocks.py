#!/usr/bin/env python3
"""
Batch 3K targeted zero-block review for volatility-skip calibration.

Offline/replay-only analyzer. It explains baseline volatility-skip direct blocks
under replay-only calibration variants. It does not fetch live data, place
orders, mutate production config, or map StrategySignal into executable actions.
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

from scripts.evaluate_strategy_vs_trader import extract_trader_action, is_volatility_skip_block, load_replay_records, write_json, write_text  # noqa: E402
from scripts.run_volatility_skip_calibration import VARIANTS, rebuild_replay_records  # noqa: E402

DATE_TAG = "2026-06-30"
DEFAULT_VARIANTS = ("variant-d", "variant-b")
DEFAULT_INPUTS = (
    Path("logs/replay_signals-batch3f-2026-06-28.jsonl"),
    Path("logs/replay_signals-batch3g-2026-06-28.jsonl"),
)
CONFIDENCE_BUCKETS = ("<0.50", "0.50-0.75", "0.75-0.95", ">=0.95", "unknown")
ATR_BUCKETS = ("<8%", "8-10%", "10-12%", ">=12%", "unknown")


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _safe_name(path: Path) -> str:
    stem = path.name[:-6] if path.name.endswith(".jsonl") else path.name
    return "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in stem.lower()).strip("-") or "window"


def discover_default_inputs() -> List[Path]:
    """Return existing Batch 3K default replay windows."""
    return [path for path in DEFAULT_INPUTS if path.exists()]


def _extract_technical_analysis(record: Dict) -> Dict:
    analysts = record.get("analysts")
    if not isinstance(analysts, dict):
        return {}
    technical = analysts.get("technical")
    if not isinstance(technical, dict):
        return {}
    analysis = technical.get("analysis")
    return analysis if isinstance(analysis, dict) else {}


def extract_states(record: Dict) -> Dict:
    """Extract technical_state and market_state from a replay record."""
    analysis = _extract_technical_analysis(record)
    technical_state = analysis.get("technical_state") if isinstance(analysis, dict) else None
    market_state = analysis.get("market_state") if isinstance(analysis, dict) else None
    return {
        "technical_state": technical_state if isinstance(technical_state, dict) else {},
        "market_state": market_state if isinstance(market_state, dict) else {},
        "missing_state": not isinstance(technical_state, dict) or not isinstance(market_state, dict),
    }


def safe_float(value, default=None):
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def atr_pct(technical_state: Dict):
    close = safe_float(technical_state.get("close"))
    atr = safe_float(technical_state.get("atr"))
    if close is None or atr is None or close <= 0:
        return None
    return atr / close


def confidence_bucket(confidence) -> str:
    value = safe_float(confidence)
    if value is None:
        return "unknown"
    if value < 0.50:
        return "<0.50"
    if value < 0.75:
        return "0.50-0.75"
    if value < 0.95:
        return "0.75-0.95"
    return ">=0.95"


def atr_bucket(value) -> str:
    if value is None:
        return "unknown"
    if value < 0.08:
        return "<8%"
    if value < 0.10:
        return "8-10%"
    if value < 0.12:
        return "10-12%"
    return ">=12%"


def _variant_config(candidate: str) -> Dict:
    if candidate not in VARIANTS:
        raise ValueError(f"Unknown variant: {candidate}")
    return VARIANTS[candidate]["strategy_config"]


def rebuild_candidate_signal(record: Dict, candidate: str) -> Dict:
    """Rebuild a single candidate signal using replay-only variant config."""
    rebuilt = rebuild_replay_records([record], _variant_config(candidate), source=f"batch3k:{candidate}")
    if not rebuilt:
        return {}
    signal = rebuilt[0].get("strategy_signal")
    return signal if isinstance(signal, dict) else {}


def classify_unblock_reasons(record: Dict, candidate: str, candidate_signal: Dict) -> List[str]:
    """Classify why a candidate no longer direct-blocks a baseline skip."""
    states = extract_states(record)
    technical_state = states["technical_state"]
    market_state = states["market_state"]
    config = _variant_config(candidate)
    vol_config = config.get("volatility_skip", {}) if isinstance(config.get("volatility_skip"), dict) else {}
    trend_config = config.get("trend_following", {}) if isinstance(config.get("trend_following"), dict) else {}
    breakout_config = config.get("breakout", {}) if isinstance(config.get("breakout"), dict) else {}
    selection_config = config.get("selection", {}) if isinstance(config.get("selection"), dict) else {}

    reasons = []
    if states["missing_state"] or not candidate_signal:
        reasons.append("fallback_or_missing_state")
        return reasons

    if is_volatility_skip_block(candidate_signal):
        return ["still_blocked"]

    regime = str(market_state.get("regime") or "")
    confidence = safe_float(market_state.get("confidence"), 0.0)
    floor = safe_float(vol_config.get("volatile_confidence_floor"), 0.0)
    if regime == "volatile" and confidence is not None and floor is not None and confidence < floor:
        reasons.append("volatile_confidence_below_floor")

    value = atr_pct(technical_state)
    threshold = safe_float(vol_config.get("high_atr_pct"), 0.08)
    if value is not None and threshold is not None and value < threshold:
        reasons.append("atr_below_candidate_threshold")

    strategy_id = str(candidate_signal.get("strategy_id") or "")
    family = str(candidate_signal.get("family") or "")
    if family == "trend_following" or strategy_id == "trend-following":
        if regime == "volatile" and (trend_config.get("allow_volatile_trend_up") or trend_config.get("allow_volatile_trend_down")):
            reasons.append("trend_following_allowed_volatile")
    if family == "breakout" or strategy_id == "breakout":
        if regime == "volatile" and breakout_config.get("allow_volatile"):
            reasons.append("breakout_allowed_volatile")

    min_action_confidence = safe_float(selection_config.get("min_action_confidence"))
    signal_confidence = safe_float(candidate_signal.get("confidence"))
    if min_action_confidence is not None and signal_confidence is not None and signal_confidence < 0.55 and signal_confidence >= min_action_confidence:
        reasons.append("lower_action_confidence_floor")

    if not reasons:
        reasons.append("other")
    return sorted(set(reasons))


def is_baseline_direct_block(record: Dict) -> bool:
    signal = record.get("strategy_signal")
    return isinstance(signal, dict) and is_volatility_skip_block(signal)


def analyze_record(record: Dict, *, window_id: str, record_index: int, variants: Sequence[str]) -> Dict:
    states = extract_states(record)
    technical_state = states["technical_state"]
    market_state = states["market_state"]
    baseline_signal = copy.deepcopy(record.get("strategy_signal") if isinstance(record.get("strategy_signal"), dict) else {})
    atr_value = atr_pct(technical_state)
    case = {
        "window_id": window_id,
        "record_index": record_index,
        "symbol": str(record.get("symbol") or "unknown"),
        "trader_action": extract_trader_action(record),
        "baseline": {
            "strategy_id": baseline_signal.get("strategy_id"),
            "family": baseline_signal.get("family"),
            "action": baseline_signal.get("action"),
            "confidence": baseline_signal.get("confidence"),
            "no_trade_reason": baseline_signal.get("no_trade_reason"),
        },
        "state": {
            "missing_state": states["missing_state"],
            "regime": market_state.get("regime"),
            "market_confidence": market_state.get("confidence"),
            "confidence_bucket": confidence_bucket(market_state.get("confidence")),
            "trend_direction": market_state.get("trend_direction"),
            "trend_strength": market_state.get("trend_strength"),
            "adx": market_state.get("adx"),
            "atr": technical_state.get("atr"),
            "close": technical_state.get("close"),
            "atr_pct": atr_value,
            "atr_bucket": atr_bucket(atr_value),
            "breakout_up_20": technical_state.get("breakout_up_20"),
            "breakout_down_20": technical_state.get("breakout_down_20"),
            "macd_crossing_up": technical_state.get("macd_crossing_up"),
            "macd_crossing_down": technical_state.get("macd_crossing_down"),
            "rsi": technical_state.get("rsi"),
        },
        "candidates": {},
    }
    for candidate in variants:
        signal = rebuild_candidate_signal(record, candidate)
        reasons = classify_unblock_reasons(record, candidate, signal)
        case["candidates"][candidate] = {
            "strategy_id": signal.get("strategy_id"),
            "family": signal.get("family"),
            "action": signal.get("action"),
            "confidence": signal.get("confidence"),
            "no_trade_reason": signal.get("no_trade_reason"),
            "direct_block": is_volatility_skip_block(signal),
            "unblock_reasons": reasons,
        }
    return case


def load_cases(input_paths: Sequence[Path], variants: Sequence[str]) -> Dict:
    windows = []
    cases = []
    for path in input_paths:
        records = load_replay_records(path)
        window_id = _safe_name(path)
        block_count = 0
        for idx, record in enumerate(records):
            if is_baseline_direct_block(record):
                block_count += 1
                cases.append(analyze_record(record, window_id=window_id, record_index=idx, variants=variants))
        windows.append({
            "window_id": window_id,
            "source": str(path),
            "total_records": len(records),
            "baseline_direct_blocks": block_count,
        })
    return {"windows": windows, "cases": cases}


def _counter_to_dict(counter: Counter) -> Dict:
    return dict(sorted(counter.items(), key=lambda kv: (-kv[1], kv[0])))


def _numeric_summary(values: List[float]) -> Dict:
    cleaned = [v for v in values if isinstance(v, (int, float))]
    if not cleaned:
        return {"count": 0, "min": None, "max": None, "mean": None}
    return {"count": len(cleaned), "min": min(cleaned), "max": max(cleaned), "mean": mean(cleaned)}


def aggregate_cases(cases: List[Dict], variants: Sequence[str]) -> Dict:
    by_window = Counter(case["window_id"] for case in cases)
    by_symbol = Counter(case["symbol"] for case in cases)
    by_trader_action = Counter(case["trader_action"] or "missing" for case in cases)
    by_regime = Counter(str(case["state"].get("regime") or "unknown") for case in cases)
    confidence_buckets = Counter(case["state"].get("confidence_bucket") or "unknown" for case in cases)
    atr_buckets = Counter(case["state"].get("atr_bucket") or "unknown" for case in cases)
    confidences = [safe_float(case["state"].get("market_confidence")) for case in cases]
    atr_values = [case["state"].get("atr_pct") for case in cases]

    candidate_summary = {}
    for candidate in variants:
        reason_counts = Counter()
        selected_strategy = Counter()
        selected_action = Counter()
        direct_blocks = 0
        hard_conflicts = 0
        for case in cases:
            cand = case["candidates"][candidate]
            for reason in cand.get("unblock_reasons", []):
                reason_counts[reason] += 1
            selected_strategy[str(cand.get("strategy_id") or "unknown")] += 1
            selected_action[str(cand.get("action") or "unknown")] += 1
            if cand.get("direct_block"):
                direct_blocks += 1
            trader_action = case.get("trader_action")
            action = str(cand.get("action") or "").lower()
            if (trader_action, action) in {("BUY", "short"), ("SELL", "long")}:
                hard_conflicts += 1
        total = len(cases)
        candidate_summary[candidate] = {
            "direct_blocks": direct_blocks,
            "direct_block_rate_on_baseline_block_subset": (direct_blocks / total) if total else 0.0,
            "hard_conflicts": hard_conflicts,
            "hard_conflict_rate_on_baseline_block_subset": (hard_conflicts / total) if total else 0.0,
            "selected_strategy": _counter_to_dict(selected_strategy),
            "selected_action": _counter_to_dict(selected_action),
            "reason_counts": _counter_to_dict(reason_counts),
        }

    return {
        "total_baseline_direct_blocks": len(cases),
        "by_window": _counter_to_dict(by_window),
        "by_symbol": _counter_to_dict(by_symbol),
        "by_trader_action": _counter_to_dict(by_trader_action),
        "by_market_regime": _counter_to_dict(by_regime),
        "confidence_buckets": {bucket: confidence_buckets.get(bucket, 0) for bucket in CONFIDENCE_BUCKETS},
        "atr_pct_buckets": {bucket: atr_buckets.get(bucket, 0) for bucket in ATR_BUCKETS},
        "market_confidence": _numeric_summary([v for v in confidences if v is not None]),
        "atr_pct": _numeric_summary([v for v in atr_values if v is not None]),
        "candidates": candidate_summary,
    }


def make_recommendation(aggregate: Dict, variants: Sequence[str]) -> Dict:
    total = aggregate.get("total_baseline_direct_blocks", 0)
    cand = aggregate.get("candidates", {})
    d = cand.get("variant-d", {})
    b = cand.get("variant-b", {})
    d_reasons = d.get("reason_counts", {})
    b_reasons = b.get("reason_counts", {})
    d_conflicts = d.get("hard_conflicts", 0)
    d_direct = d.get("direct_blocks", 0)
    dominant_d = sorted(d_reasons.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
    dominant_b = sorted(b_reasons.items(), key=lambda kv: (-kv[1], kv[0]))[:3]

    if total == 0:
        primary = None
        confidence = "low"
        outcome = "No baseline direct volatility-skip blocks were found; collect more replay data."
        next_step = "Collect additional replay windows before calibration decisions"
    elif d_conflicts == 0 and d_direct == 0 and d_reasons.get("volatile_confidence_below_floor", 0) >= max(1, int(total * 0.8)):
        primary = "variant-d"
        confidence = "medium"
        outcome = "Variant D zero-block behavior is mostly explained by the replay-only volatile confidence floor."
        next_step = "Batch 3L — approval-gated implementation design or Variant E review, depending on Julius preference"
    elif d_conflicts == 0:
        primary = "variant-d"
        confidence = "low"
        outcome = "Variant D has no hard conflicts, but zero-block behavior is not dominated by one safe explanation."
        next_step = "Batch 3L — design a narrower Variant E or collect broader replay data"
    else:
        primary = None
        confidence = "low"
        outcome = "Variant D is not ready because hard conflicts appeared on the baseline-blocked subset."
        next_step = "Reject/defer calibration or design a narrower Variant E"

    return {
        "outcome": outcome,
        "primary_candidate": primary,
        "secondary_candidate": "variant-b" if primary == "variant-d" and "variant-b" in variants else None,
        "zero_block_explanation": {
            "variant-d_top_reasons": dominant_d,
            "variant-b_top_reasons": dominant_b,
        },
        "confidence": confidence,
        "next_step": next_step,
        "production_change_authorized": False,
        "implementation_authorized": False,
        "runtime_default_config_change_performed": False,
        "requires_approval_before_runtime_change": True,
    }


def build_report(input_paths: Sequence[Path], variants: Sequence[str]) -> Dict:
    loaded = load_cases(input_paths, variants)
    aggregate = aggregate_cases(loaded["cases"], variants)
    recommendation = make_recommendation(aggregate, variants)
    return {
        "batch": "3K",
        "mode": "offline_replay_only",
        "production_change_authorized": False,
        "implementation_authorized": False,
        "runtime_default_config_change_performed": False,
        "requires_approval_before_runtime_change": True,
        "variants": list(variants),
        "windows": loaded["windows"],
        "aggregate": aggregate,
        "cases": loaded["cases"],
        "recommendation": recommendation,
        "scope_boundary": "No live trading, order placement, StrategySignal-to-order mapping, production config/default changes, or runtime semantic changes.",
    }


def _table_from_counts(title: str, counts: Dict) -> List[str]:
    lines = [f"| {title} | Count |", "|---|---:|"]
    if not counts:
        return lines + ["| _none_ | 0 |"]
    for key, value in counts.items():
        lines.append(f"| {key} | {value} |")
    return lines


def render_markdown_report(report: Dict) -> str:
    aggregate = report["aggregate"]
    rec = report["recommendation"]
    lines = [
        "# Batch 3K — Zero Volatility-Skip Block Review",
        "",
        "## Executive Summary",
        "",
        f"- Mode: {report['mode']}",
        f"- Windows evaluated: {len(report['windows'])}",
        f"- Baseline direct volatility-skip blocks reviewed: {aggregate['total_baseline_direct_blocks']}",
        f"- Variants: {', '.join(report['variants'])}",
        f"- Production change authorized: {str(report['production_change_authorized']).lower()}",
        f"- Implementation authorized: {str(report['implementation_authorized']).lower()}",
        f"- Runtime/default config change performed: {str(report['runtime_default_config_change_performed']).lower()}",
        f"- Recommendation: {rec['outcome']}",
        "",
        "## Scope Boundary",
        "",
        report["scope_boundary"],
        "",
        "## Replay Windows",
        "",
        "| Window | Source | Total records | Baseline direct blocks |",
        "|---|---|---:|---:|",
    ]
    for window in report["windows"]:
        lines.append(f"| {window['window_id']} | {window['source']} | {window['total_records']} | {window['baseline_direct_blocks']} |")

    lines.extend(["", "## Baseline Block Subset Distribution", ""])
    for title, counts in [
        ("Window", aggregate["by_window"]),
        ("Symbol", aggregate["by_symbol"]),
        ("Trader Action", aggregate["by_trader_action"]),
        ("Market Regime", aggregate["by_market_regime"]),
        ("Confidence Bucket", aggregate["confidence_buckets"]),
        ("ATR/Close Bucket", aggregate["atr_pct_buckets"]),
    ]:
        lines.extend(_table_from_counts(title, counts))
        lines.append("")

    conf = aggregate["market_confidence"]
    atr = aggregate["atr_pct"]
    lines.extend([
        "## Numeric State Summary",
        "",
        "| Metric | Count | Min | Mean | Max |",
        "|---|---:|---:|---:|---:|",
        f"| Market confidence | {conf['count']} | {conf['min']} | {conf['mean']} | {conf['max']} |",
        f"| ATR/close | {atr['count']} | {atr['min']} | {atr['mean']} | {atr['max']} |",
        "",
        "## Candidate Behavior on Baseline-Blocked Subset",
        "",
        "| Candidate | Direct blocks | Direct block rate | Hard conflicts | Hard conflict rate | Selected strategies | Selected actions |",
        "|---|---:|---:|---:|---:|---|---|",
    ])
    for candidate, summary in aggregate["candidates"].items():
        strategies = ", ".join(f"{k}:{v}" for k, v in summary["selected_strategy"].items()) or "none"
        actions = ", ".join(f"{k}:{v}" for k, v in summary["selected_action"].items()) or "none"
        lines.append(
            f"| {candidate} | {summary['direct_blocks']} | {_pct(summary['direct_block_rate_on_baseline_block_subset'])} | "
            f"{summary['hard_conflicts']} | {_pct(summary['hard_conflict_rate_on_baseline_block_subset'])} | {strategies} | {actions} |"
        )

    lines.extend(["", "## Candidate Reason Categories", ""])
    for candidate, summary in aggregate["candidates"].items():
        lines.extend([f"### {candidate}", ""])
        lines.extend(_table_from_counts("Reason", summary["reason_counts"]))
        lines.append("")

    lines.extend([
        "## Interpretation",
        "",
        "- A zero direct-block rate is acceptable only if explained by safe replay-only filters rather than unrestricted volatile entries.",
        "- Variant D is safer than Variant B because it does not allow volatile breakout behavior.",
        "- Variant B remains useful as a stress-test, not as a default production candidate.",
        "- This review remains observational and does not authorize runtime/default calibration changes.",
        "",
        "## Recommendation",
        "",
        f"- Outcome: {rec['outcome']}",
        f"- Primary candidate: {rec['primary_candidate']}",
        f"- Secondary candidate: {rec['secondary_candidate']}",
        f"- Zero-block explanation: {rec['zero_block_explanation']}",
        f"- Confidence: {rec['confidence']}",
        f"- Next step: {rec['next_step']}",
        "",
        "## Decision Block",
        "",
        "~~~text",
        "Batch 3K Decision:",
        f"- Production change authorized: {str(rec['production_change_authorized']).lower()}",
        "- Runtime/default config change: not performed",
        f"- Primary candidate: {rec['primary_candidate']}",
        f"- Secondary candidate: {rec['secondary_candidate']}",
        f"- Zero-block explanation: {rec['zero_block_explanation']}",
        f"- Confidence: {rec['confidence']}",
        f"- Next batch: {rec['next_step']}",
        "~~~",
        "",
    ])
    return "\n".join(lines)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Run Batch 3K zero volatility-skip block review")
    parser.add_argument("--inputs", nargs="+", type=Path, default=None, help="Replay JSONL windows to evaluate")
    parser.add_argument("--variants", nargs="+", default=list(DEFAULT_VARIANTS), choices=sorted(VARIANTS), help="Replay-only variants to diagnose")
    parser.add_argument("--output", type=Path, default=Path(f"volatility-skip-zero-block-review-batch3k-{DATE_TAG}.md"))
    parser.add_argument("--json-output", type=Path, default=Path(f"volatility-skip-zero-block-review-batch3k-{DATE_TAG}.json"))
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting Batch 3K report artifacts")
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
        report = build_report(inputs, args.variants)
        write_text(args.output, render_markdown_report(report))
        write_json(args.json_output, report)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Wrote zero-block review markdown: {args.output}")
    print(f"Wrote zero-block review JSON: {args.json_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

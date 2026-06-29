#!/usr/bin/env python3
"""
Replay-only volatility-skip calibration review helper.

Reads an existing replay JSONL artifact, rebuilds top-level StrategySignal
attribution with explicit in-memory calibration variants, evaluates each
variant with the Batch 4B evaluator, and writes flat comparison reports.

This tool is offline/replay-only. It does not fetch live data, does not import
runtime/execution/order modules, does not modify config files, and does not map
strategy actions into executable TraderAgent actions.
"""
import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Dict, Iterable, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.evaluate_strategy_vs_trader import (  # noqa: E402
    evaluate_strategy_vs_trader,
    load_replay_records,
    render_markdown_evaluation,
    write_json,
    write_text,
)
from strategies.attribution import build_strategy_signal  # noqa: E402

DATE_TAG = "2026-06-29"
DEFAULT_INPUT = Path("logs/replay_signals-batch3g-2026-06-28.jsonl")
DEFAULT_BASELINE_JSON = Path("strategy-vs-traderagent-evaluation-batch4b-2026-06-29.json")

BASE_ORDER = {
    "trend_up": ["volatility_skip", "trend_following", "breakout"],
    "trend_down": ["volatility_skip", "trend_following", "breakout"],
    "ranging": ["volatility_skip", "breakout"],
    "volatile": ["volatility_skip", "trend_following", "breakout"],
}

VARIANTS: Dict[str, Dict] = {
    "variant-a": {
        "description": "Mild volatility relaxation: only hard-skip volatile regimes at higher regime confidence; keep conservative ATR guard.",
        "strategy_config": {
            "calibration": {"replay_only": True, "variant": "variant-a"},
            "regime_strategy_order": BASE_ORDER,
            "volatility_skip": {
                "calibration": {"replay_only": True},
                "volatile_confidence_floor": 0.75,
                "high_atr_pct": 0.10,
            },
            "trend_following": {
                "allow_volatile_trend_up": True,
                "allow_volatile_trend_down": True,
            },
            "selection": {"min_action_confidence": 0.55},
        },
    },
    "variant-b": {
        "description": "Moderate relaxation stress test: materially higher volatile confidence and ATR floors, with breakout allowed in volatile replay only.",
        "strategy_config": {
            "calibration": {"replay_only": True, "variant": "variant-b"},
            "regime_strategy_order": BASE_ORDER,
            "volatility_skip": {
                "calibration": {"replay_only": True},
                "volatile_confidence_floor": 0.95,
                "high_atr_pct": 0.12,
            },
            "trend_following": {
                "allow_volatile_trend_up": True,
                "allow_volatile_trend_down": True,
            },
            "breakout": {"allow_volatile": True},
            "selection": {"min_action_confidence": 0.55},
        },
    },
    "variant-c": {
        "description": "Trend-down short exception: allow only volatile downtrends through trend-following after volatility guard relaxation.",
        "strategy_config": {
            "calibration": {"replay_only": True, "variant": "variant-c"},
            "regime_strategy_order": BASE_ORDER,
            "volatility_skip": {
                "calibration": {"replay_only": True},
                "volatile_confidence_floor": 0.75,
                "high_atr_pct": 0.20,
            },
            "trend_following": {"allow_volatile_trend_down": True},
            "selection": {"min_action_confidence": 0.55},
        },
    },
    "variant-d": {
        "description": "Trend-following confidence floor review: lower replay-only trend/action floors without changing production defaults.",
        "strategy_config": {
            "calibration": {"replay_only": True, "variant": "variant-d"},
            "regime_strategy_order": BASE_ORDER,
            "volatility_skip": {
                "calibration": {"replay_only": True},
                "volatile_confidence_floor": 0.75,
                "high_atr_pct": 0.10,
            },
            "trend_following": {
                "allow_volatile_trend_up": True,
                "allow_volatile_trend_down": True,
                "min_regime_confidence": 0.50,
            },
            "selection": {"min_action_confidence": 0.50},
        },
    },
}


def load_json(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_technical_analysis(record: Dict) -> Dict:
    analysts = record.get("analysts")
    if not isinstance(analysts, dict):
        return {}
    technical = analysts.get("technical")
    if not isinstance(technical, dict):
        return {}
    analysis = technical.get("analysis")
    return analysis if isinstance(analysis, dict) else {}


def rebuild_replay_records(records: List[Dict], strategy_config: Dict, *, source: str) -> List[Dict]:
    """Return replay records with strategy_signal rebuilt under variant config."""
    rebuilt = []
    for record in records:
        next_record = copy.deepcopy(record)
        signal = build_strategy_signal(
            technical_analysis=_extract_technical_analysis(next_record),
            strategy_config=strategy_config,
            source=source,
        )
        attribution = signal.get("attribution", {}) or {}
        attribution["calibration"] = {
            "batch": "3H",
            "replay_only": True,
            "variant": source,
        }
        signal["attribution"] = attribution
        next_record["strategy_signal"] = signal
        rebuilt.append(next_record)
    return rebuilt


def write_jsonl(path: Path, records: Iterable[Dict], *, overwrite: bool = False) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, sort_keys=True) + chr(10))


def evaluate_records(records: List[Dict], md_path: Path, json_path: Path, *, overwrite: bool = False) -> Dict:
    if not overwrite:
        for path in (md_path, json_path):
            if path.exists():
                raise FileExistsError(f"Refusing to overwrite existing artifact: {path}")
    evaluation = evaluate_strategy_vs_trader(records)
    write_text(md_path, render_markdown_evaluation(evaluation))
    write_json(json_path, evaluation)
    return evaluation


def _count_share(evaluation: Dict, section: str, key: str) -> Dict:
    total = evaluation.get("dataset", {}).get("total_records", 0) or 0
    count = evaluation.get("counts", {}).get(section, {}).get(key, 0)
    return {"count": count, "share": (count / total) if total else 0.0}


def _core_rates(evaluation: Dict) -> Dict:
    rates = evaluation.get("rates", {})
    keys = [
        "attribution_coverage_rate",
        "alignment_rate",
        "conflict_rate",
        "neutral_or_observational_rate",
        "directional_strategy_coverage_rate",
        "skip_during_trader_action_rate",
        "volatility_skip_direct_block_rate",
    ]
    return {key: rates.get(key, 0.0) for key in keys}


def _summary(evaluation: Dict) -> Dict:
    counts = evaluation.get("counts", {})
    action_matrix = counts.get("action_matrix", {})
    strategy_action = counts.get("strategy_action", {})
    return {
        "total_records": evaluation.get("dataset", {}).get("total_records", 0),
        "rates": _core_rates(evaluation),
        "strategy_selection": {
            "volatility-skip": _count_share(evaluation, "strategy_id", "volatility-skip"),
            "trend-following": _count_share(evaluation, "strategy_id", "trend-following"),
            "breakout": _count_share(evaluation, "strategy_id", "breakout"),
        },
        "actions": {
            "long": strategy_action.get("long", 0),
            "short": strategy_action.get("short", 0),
            "skip": strategy_action.get("skip", 0),
            "hold": strategy_action.get("hold", 0),
        },
        "matrix": {
            "BUY|skip": action_matrix.get("BUY|skip", 0),
            "SELL|skip": action_matrix.get("SELL|skip", 0),
            "BUY|long": action_matrix.get("BUY|long", 0),
            "SELL|short": action_matrix.get("SELL|short", 0),
            "BUY|short": action_matrix.get("BUY|short", 0),
            "SELL|long": action_matrix.get("SELL|long", 0),
        },
        "gate_status": {
            key: value.get("status")
            for key, value in evaluation.get("gate_status", {}).items()
            if isinstance(value, dict)
        },
    }


def _deltas(baseline: Dict, variant: Dict) -> Dict:
    base_rates = baseline["rates"]
    variant_rates = variant["rates"]
    return {key: variant_rates.get(key, 0.0) - base_rates.get(key, 0.0) for key in base_rates}


def _is_promising(baseline: Dict, variant: Dict) -> bool:
    rates = variant["rates"]
    base = baseline["rates"]
    matrix = variant["matrix"]
    return (
        rates.get("attribution_coverage_rate") == 1.0
        and rates.get("conflict_rate", 0.0) == 0.0
        and rates.get("volatility_skip_direct_block_rate", 1.0) < base.get("volatility_skip_direct_block_rate", 0.0)
        and rates.get("directional_strategy_coverage_rate", 0.0) > base.get("directional_strategy_coverage_rate", 0.0)
        and rates.get("skip_during_trader_action_rate", 1.0) < base.get("skip_during_trader_action_rate", 0.0)
        and matrix.get("BUY|short", 0) == 0
        and matrix.get("SELL|long", 0) == 0
    )


def compare_evaluations(baseline_evaluation: Dict, variant_evaluations: Dict[str, Dict]) -> Dict:
    """Compare Batch 3H variants against the Batch 3G/4B baseline."""
    baseline = _summary(baseline_evaluation)
    variants = {}
    for label, evaluation in sorted(variant_evaluations.items()):
        summary = _summary(evaluation)
        variants[label] = {
            "description": VARIANTS.get(label, {}).get("description", "custom variant"),
            "summary": summary,
            "deltas": _deltas(baseline, summary),
            "promising": _is_promising(baseline, summary),
        }

    promising = [label for label, row in variants.items() if row["promising"]]
    if promising:
        recommendation = {
            "outcome": "Outcome A — Calibration looks promising",
            "next_step": "Batch 3I — Replay-Only Calibration Implementation Proposal",
            "reason": f"Promising variants: {', '.join(promising)}.",
        }
    else:
        recommendation = {
            "outcome": "Outcome C — Need more data or safer variants",
            "next_step": "Broader multi-period replay dataset or narrower calibration hypotheses before implementation.",
            "reason": "No variant satisfied all acceptance criteria against the Batch 3G/4B baseline.",
        }

    return {
        "mode": "offline_replay_only",
        "baseline": baseline,
        "variants": variants,
        "recommendation": recommendation,
        "scope_boundary": "production/runtime thresholds were not changed; StrategySignal remains observational-only.",
    }


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def render_markdown_comparison(comparison: Dict) -> str:
    baseline = comparison["baseline"]
    variants = comparison["variants"]
    rec = comparison["recommendation"]
    metric_keys = [
        "attribution_coverage_rate",
        "alignment_rate",
        "conflict_rate",
        "neutral_or_observational_rate",
        "directional_strategy_coverage_rate",
        "skip_during_trader_action_rate",
        "volatility_skip_direct_block_rate",
    ]

    lines = [
        "# Volatility-Skip Calibration Review",
        "",
        "## Baseline",
        "",
        f"- Total records: {baseline['total_records']}",
        "- Source: Batch 3G replay + Batch 4B evaluator",
        "- Scope: offline replay-only; production/runtime thresholds were not changed.",
        "",
        "| Metric | Baseline |",
        "|---|---:|",
    ]
    for key in metric_keys:
        lines.append(f"| {key} | {_pct(baseline['rates'].get(key, 0.0))} |")

    lines.extend([
        "",
        "## Variant Comparison",
        "",
        "| Variant | Directional | Δ Directional | Skip During Action | Δ Skip During Action | Vol-Skip Block | Δ Vol-Skip Block | Conflict |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for label, row in variants.items():
        rates = row["summary"]["rates"]
        deltas = row["deltas"]
        lines.append(
            f"| {label} | {_pct(rates['directional_strategy_coverage_rate'])} | "
            f"{_pct(deltas['directional_strategy_coverage_rate'])} | "
            f"{_pct(rates['skip_during_trader_action_rate'])} | "
            f"{_pct(deltas['skip_during_trader_action_rate'])} | "
            f"{_pct(rates['volatility_skip_direct_block_rate'])} | "
            f"{_pct(deltas['volatility_skip_direct_block_rate'])} | "
            f"{_pct(rates['conflict_rate'])} |"
        )

    lines.extend([
        "",
        "## Acceptance Review",
        "",
        "| Variant | Promising | BUY|skip | SELL|skip | BUY|long | SELL|short | BUY|short | SELL|long |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ])
    for label, row in variants.items():
        matrix = row["summary"]["matrix"]
        lines.append(
            f"| {label} | {'yes' if row['promising'] else 'no'} | "
            f"{matrix['BUY|skip']} | {matrix['SELL|skip']} | "
            f"{matrix['BUY|long']} | {matrix['SELL|short']} | "
            f"{matrix['BUY|short']} | {matrix['SELL|long']} |"
        )

    lines.extend([
        "",
        "## Variant Notes",
        "",
    ])
    for label, row in variants.items():
        lines.extend([
            f"### {label}",
            "",
            f"- Description: {row['description']}",
            f"- Gate status: {row['summary']['gate_status']}",
            "",
        ])

    lines.extend([
        "## Recommendation",
        "",
        f"- Outcome: {rec['outcome']}",
        f"- Next step: {rec['next_step']}",
        f"- Reason: {rec['reason']}",
        "- Boundary: production/runtime thresholds were not changed; no live trading or execution mapping was introduced.",
        "",
    ])
    return chr(10).join(lines)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Run replay-only volatility-skip calibration review")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Baseline replay JSONL input")
    parser.add_argument("--baseline-json", type=Path, default=DEFAULT_BASELINE_JSON, help="Baseline Batch 4B evaluation JSON")
    parser.add_argument("--variants", nargs="+", default=sorted(VARIANTS), choices=sorted(VARIANTS), help="Variants to run")
    parser.add_argument("--review-output", type=Path, default=Path(f"volatility-skip-calibration-review-batch3h-{DATE_TAG}.md"))
    parser.add_argument("--json-output", type=Path, default=Path(f"volatility-skip-calibration-review-batch3h-{DATE_TAG}.json"))
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting Batch 3H artifacts")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        baseline_records = load_replay_records(args.input)
        if args.baseline_json.exists():
            baseline_eval = load_json(args.baseline_json)
        else:
            baseline_eval = evaluate_strategy_vs_trader(baseline_records)

        variant_evals = {}
        for label in args.variants:
            variant = VARIANTS[label]
            records = rebuild_replay_records(
                baseline_records,
                variant["strategy_config"],
                source=f"batch3h:{label}",
            )
            replay_path = Path(f"logs/replay_signals-batch3h-{label}-{DATE_TAG}.jsonl")
            md_path = Path(f"strategy-vs-traderagent-evaluation-batch3h-{label}-{DATE_TAG}.md")
            json_path = Path(f"strategy-vs-traderagent-evaluation-batch3h-{label}-{DATE_TAG}.json")
            write_jsonl(replay_path, records, overwrite=args.overwrite)
            variant_evals[label] = evaluate_records(records, md_path, json_path, overwrite=args.overwrite)
            print(f"Wrote {label}: {replay_path}, {md_path}, {json_path}")

        comparison = compare_evaluations(baseline_eval, variant_evals)
        if not args.overwrite:
            for path in (args.review_output, args.json_output):
                if path.exists():
                    raise FileExistsError(f"Refusing to overwrite existing artifact: {path}")
        write_text(args.review_output, render_markdown_comparison(comparison))
        write_json(args.json_output, comparison)
        print(f"Wrote review markdown: {args.review_output}")
        print(f"Wrote review JSON: {args.json_output}")
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

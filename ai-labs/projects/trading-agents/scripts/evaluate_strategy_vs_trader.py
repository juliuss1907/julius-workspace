#!/usr/bin/env python3
"""
Offline Strategy-vs-TraderAgent evaluator.

Reads replay JSONL artifacts and computes Batch 4A evaluation metrics for
observational StrategySignal outputs versus TraderAgent final actions. This is
reporting-only tooling: it does not import runtime, dataflow, order, notifier,
risk, position, trading, or execution modules, and it never maps strategy
signals into executable trade actions.
"""
import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Dict, List


DEFAULT_INPUT = Path("logs/replay_signals-batch3g-2026-06-28.jsonl")


def load_replay_records(path: Path) -> List[Dict]:
    """Load replay JSONL records, skipping blank lines."""
    records = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Replay input not found: {path}") from exc

    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            record = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {path} at line {line_no}: {exc}") from exc
        if not isinstance(record, dict):
            raise ValueError(f"Invalid replay record in {path} at line {line_no}: expected object")
        records.append(record)
    return records


def extract_trader_action(record: Dict) -> str:
    """Extract TraderAgent final action from known replay record shapes."""
    final_signal = record.get("final_signal")
    if not isinstance(final_signal, dict):
        return ""

    analysis = final_signal.get("analysis")
    if isinstance(analysis, dict):
        trader = analysis.get("trader")
        if isinstance(trader, dict):
            action = trader.get("action")
            if action:
                return str(action).upper()

    metadata = final_signal.get("metadata")
    if isinstance(metadata, dict):
        action = metadata.get("final_action")
        if action:
            return str(action).upper()

    return ""


def extract_strategy_signal(record: Dict) -> Dict:
    """Return top-level strategy_signal when present and non-empty."""
    strategy_signal = record.get("strategy_signal")
    if isinstance(strategy_signal, dict) and strategy_signal:
        return strategy_signal
    return {}


def extract_strategy_action(record: Dict) -> str:
    """Extract strategy action from replay record."""
    strategy_signal = extract_strategy_signal(record)
    action = strategy_signal.get("action")
    return str(action).lower() if action else ""


def extract_strategy_family(strategy_signal: Dict) -> str:
    """Extract strategy family with a stable unknown fallback."""
    if not isinstance(strategy_signal, dict) or not strategy_signal:
        return "unknown"
    return str(strategy_signal.get("family") or "unknown")


def extract_market_regime(strategy_signal: Dict) -> str:
    """Extract market regime from StrategySignal attribution."""
    if not isinstance(strategy_signal, dict) or not strategy_signal:
        return "unknown"
    attribution = strategy_signal.get("attribution")
    if not isinstance(attribution, dict):
        return "unknown"
    return str(attribution.get("regime") or attribution.get("market_regime") or "unknown")


def is_volatility_skip_block(strategy_signal: Dict) -> bool:
    """Return True when volatility-skip directly blocks with a skip action."""
    if not isinstance(strategy_signal, dict) or not strategy_signal:
        return False
    strategy_id = str(strategy_signal.get("strategy_id") or "")
    action = str(strategy_signal.get("action") or "").lower()
    return strategy_id == "volatility-skip" and action == "skip"


def classify_alignment(trader_action: str, strategy_action: str) -> str:
    """Classify TraderAgent-vs-StrategySignal relationship for reporting only."""
    trader = (trader_action or "").upper()
    strategy = (strategy_action or "").lower()

    if not trader or not strategy:
        return "missing"
    if (trader, strategy) in {("BUY", "long"), ("SELL", "short"), ("HOLD", "hold")}:
        return "aligned"
    if (trader, strategy) in {("BUY", "short"), ("SELL", "long")}:
        return "conflicted"
    return "neutral_or_observational"


def safe_rate(numerator: int, denominator: int) -> float:
    """Return numerator / denominator, or 0.0 when denominator is zero."""
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def _market_timeframe(record: Dict) -> str:
    snapshot = record.get("market_snapshot")
    if not isinstance(snapshot, dict):
        return "unknown"
    return str(snapshot.get("timeframe") or "unknown")


def _status(status: str, message: str) -> Dict:
    return {"status": status, "message": message}


def _gate_status(total_records: int, records_with_strategy_signal: int, conflict_count: int,
                 directional_count: int, skip_during_action: int) -> Dict:
    attribution_rate = safe_rate(records_with_strategy_signal, total_records)
    directional_rate = safe_rate(directional_count, total_records)
    skip_rate = safe_rate(skip_during_action, total_records)

    return {
        "attribution_ready": _status(
            "pass" if total_records > 0 and attribution_rate == 1.0 else "warn",
            "All replay records include top-level strategy_signal."
            if total_records > 0 and attribution_rate == 1.0
            else "Some replay records lack top-level strategy_signal; review data quality first.",
        ),
        "conflict_review_ready": _status(
            "pass" if conflict_count == 0 else "warn",
            "No hard BUY|short or SELL|long conflicts detected."
            if conflict_count == 0
            else "Hard directional conflicts detected; review before any influence policy.",
        ),
        "directional_sample_insufficient": _status(
            "warn" if directional_count < 30 or directional_rate < 0.20 else "pass",
            "Directional strategy sample is still sparse; collect more replay evidence before policy changes."
            if directional_count < 30 or directional_rate < 0.20
            else "Directional strategy sample is large enough for first-pass review.",
        ),
        "skip_calibration_needed": _status(
            "warn" if skip_rate >= 0.25 else "pass",
            "TraderAgent often acts while StrategySignal skips; calibration review is needed before tuning."
            if skip_rate >= 0.25
            else "Skip-during-action rate is below first-review warning threshold.",
        ),
        "execution_not_authorized": _status(
            "blocked",
            "Evaluation tooling does not authorize live trading, order routing, or strategy-to-execution mapping.",
        ),
    }


def evaluate_strategy_vs_trader(records: List[Dict]) -> Dict:
    """Compute Batch 4A Strategy-vs-TraderAgent evaluation metrics."""
    by_symbol = Counter()
    by_timeframe = Counter()
    strategy_id = Counter()
    strategy_action = Counter()
    strategy_family = Counter()
    market_regime = Counter()
    action_alignment = Counter({
        "aligned": 0,
        "conflicted": 0,
        "neutral_or_observational": 0,
        "missing": 0,
    })
    action_matrix = Counter()

    records_with_strategy_signal = 0
    directional_strategy_signals = 0
    skip_during_trader_action = 0
    volatility_skip_direct_blocks = 0

    for record in records:
        if not isinstance(record, dict):
            continue
        by_symbol[str(record.get("symbol") or "unknown")] += 1
        by_timeframe[_market_timeframe(record)] += 1

        trader_action = extract_trader_action(record)
        strategy_signal = extract_strategy_signal(record)
        strategy = str(strategy_signal.get("action") or "").lower() if strategy_signal else ""

        label = classify_alignment(trader_action, strategy)
        action_alignment[label] += 1
        action_matrix[f"{trader_action or 'missing'}|{strategy or 'missing'}"] += 1

        if not strategy_signal:
            continue

        records_with_strategy_signal += 1
        strategy_id[str(strategy_signal.get("strategy_id") or "unknown")] += 1
        family = extract_strategy_family(strategy_signal)
        strategy_family[family] += 1
        strategy_action[strategy or "unknown"] += 1
        market_regime[extract_market_regime(strategy_signal)] += 1

        if strategy in {"long", "short"}:
            directional_strategy_signals += 1
        if trader_action in {"BUY", "SELL"} and strategy == "skip":
            skip_during_trader_action += 1
        if is_volatility_skip_block(strategy_signal):
            volatility_skip_direct_blocks += 1

    total_records = len(records)
    strategy_family_share = {
        family: safe_rate(count, total_records)
        for family, count in sorted(strategy_family.items())
    }
    counts = {
        "by_symbol": dict(sorted(by_symbol.items())),
        "by_timeframe": dict(sorted(by_timeframe.items())),
        "strategy_id": dict(sorted(strategy_id.items())),
        "strategy_action": dict(sorted(strategy_action.items())),
        "strategy_family": dict(sorted(strategy_family.items())),
        "market_regime": dict(sorted(market_regime.items())),
        "action_alignment": dict(action_alignment),
        "action_matrix": dict(sorted(action_matrix.items())),
        "directional_strategy_signals": directional_strategy_signals,
        "skip_during_trader_action": skip_during_trader_action,
        "volatility_skip_direct_blocks": volatility_skip_direct_blocks,
    }
    rates = {
        "attribution_coverage_rate": safe_rate(records_with_strategy_signal, total_records),
        "alignment_rate": safe_rate(action_alignment["aligned"], total_records),
        "conflict_rate": safe_rate(action_alignment["conflicted"], total_records),
        "neutral_or_observational_rate": safe_rate(action_alignment["neutral_or_observational"], total_records),
        "missing_rate": safe_rate(action_alignment["missing"], total_records),
        "directional_strategy_coverage_rate": safe_rate(directional_strategy_signals, total_records),
        "skip_during_trader_action_rate": safe_rate(skip_during_trader_action, total_records),
        "volatility_skip_direct_block_rate": safe_rate(volatility_skip_direct_blocks, total_records),
        "strategy_family_share": strategy_family_share,
    }

    return {
        "dataset": {
            "total_records": total_records,
            "records_with_strategy_signal": records_with_strategy_signal,
            "records_missing_strategy_signal": total_records - records_with_strategy_signal,
        },
        "metrics": {
            "attribution_coverage": {"numerator": records_with_strategy_signal, "denominator": total_records, "rate": rates["attribution_coverage_rate"]},
            "alignment": {"numerator": action_alignment["aligned"], "denominator": total_records, "rate": rates["alignment_rate"]},
            "conflict": {"numerator": action_alignment["conflicted"], "denominator": total_records, "rate": rates["conflict_rate"]},
            "neutral_or_observational": {"numerator": action_alignment["neutral_or_observational"], "denominator": total_records, "rate": rates["neutral_or_observational_rate"]},
            "directional_strategy_coverage": {"numerator": directional_strategy_signals, "denominator": total_records, "rate": rates["directional_strategy_coverage_rate"]},
            "skip_during_trader_action": {"numerator": skip_during_trader_action, "denominator": total_records, "rate": rates["skip_during_trader_action_rate"]},
            "volatility_skip_direct_block": {"numerator": volatility_skip_direct_blocks, "denominator": total_records, "rate": rates["volatility_skip_direct_block_rate"]},
        },
        "counts": counts,
        "rates": rates,
        "action_matrix": counts["action_matrix"],
        "gate_status": _gate_status(total_records, records_with_strategy_signal, action_alignment["conflicted"], directional_strategy_signals, skip_during_trader_action),
        "recommendation": {
            "next_batch": "Batch 3H — Volatility-Skip Calibration Review",
            "reason": "Use repeatable Batch 4B metrics to compare replay-only calibration variants against the Batch 3G baseline before any threshold tuning.",
        },
    }


def _pct(rate: float) -> str:
    return f"{rate * 100:.1f}%"


def _table(title_left: str, rows: Dict[str, int]) -> List[str]:
    lines = [f"| {title_left} | Count |", "|---|---:|"]
    if not rows:
        return lines + ["| _none_ | 0 |"]
    for key, count in sorted(rows.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| {key} | {count} |")
    return lines


def _metric_row(name: str, metric: Dict) -> str:
    return f"| {name} | {metric['numerator']}/{metric['denominator']} ({_pct(metric['rate'])}) |"


def render_markdown_evaluation(evaluation: Dict) -> str:
    """Render a flat human-reviewable Markdown evaluation report."""
    dataset = evaluation["dataset"]
    metrics = evaluation["metrics"]
    counts = evaluation["counts"]
    rates = evaluation["rates"]
    gates = evaluation["gate_status"]
    recommendation = evaluation["recommendation"]

    lines = [
        "# Strategy vs TraderAgent Evaluation",
        "",
        "## Dataset",
        "",
        f"- Total records: {dataset['total_records']}",
        f"- Records with strategy_signal: {dataset['records_with_strategy_signal']}",
        f"- Records missing strategy_signal: {dataset['records_missing_strategy_signal']}",
        "- Evaluation mode: offline / replay-only",
        "- StrategySignal remains observational-only; this report does not authorize execution.",
        "",
        "## Core Metrics",
        "",
        "| Metric | Value |",
        "|---|---:|",
        _metric_row("Attribution coverage", metrics["attribution_coverage"]),
        _metric_row("Alignment rate", metrics["alignment"]),
        _metric_row("Conflict rate", metrics["conflict"]),
        _metric_row("Neutral / observational rate", metrics["neutral_or_observational"]),
        _metric_row("Directional strategy coverage", metrics["directional_strategy_coverage"]),
        _metric_row("Skip during TraderAgent action", metrics["skip_during_trader_action"]),
        _metric_row("Volatility-skip direct block", metrics["volatility_skip_direct_block"]),
        "",
        "## Strategy Distribution",
        "",
    ]
    lines.extend(_table("Strategy ID", counts["strategy_id"]))
    lines.extend(["", "### Strategy Action", ""])
    lines.extend(_table("Strategy Action", counts["strategy_action"]))
    lines.extend(["", "### Strategy Family", ""])
    lines.extend(_table("Strategy Family", counts["strategy_family"]))
    lines.extend(["", "### Strategy Family Share", "", "| Strategy Family | Share |", "|---|---:|"])
    for family, share in sorted(rates["strategy_family_share"].items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| {family} | {_pct(share)} |")
    if not rates["strategy_family_share"]:
        lines.append("| _none_ | 0.0% |")
    lines.extend(["", "### Market Regime", ""])
    lines.extend(_table("Market Regime", counts["market_regime"]))
    lines.extend(["", "## Action Matrix", "", "| Trader Action + Strategy Action | Count |", "|---|---:|"])
    for key, count in sorted(counts["action_matrix"].items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| {key} | {count} |")
    if not counts["action_matrix"]:
        lines.append("| _none_ | 0 |")
    lines.extend(["", "## Gate Status", "", "| Gate | Status | Message |", "|---|---|---|"])
    for gate, info in gates.items():
        lines.append(f"| {gate} | {info['status']} | {info['message']} |")
    lines.extend([
        "",
        "## Interpretation",
        "",
        "- This evaluator is repeatable offline tooling for replay attribution artifacts.",
        "- Aligned pairs are BUY|long, SELL|short, and HOLD|hold.",
        "- Conflicted pairs are BUY|short and SELL|long.",
        "- Neutral/observational pairs are review signals, not execution instructions.",
        "- StrategySignal remains observational-only and must not be mapped into orders.",
        "",
        "## Next Recommendation",
        "",
        f"- Recommended next batch: {recommendation['next_batch']}",
        f"- Reason: {recommendation['reason']}",
        "",
    ])
    return "\n".join(lines)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, evaluation: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evaluation, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Evaluate StrategySignal attribution against TraderAgent final actions.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input replay JSONL path")
    parser.add_argument("--output", type=Path, default=Path(f"strategy-vs-traderagent-evaluation-{date.today().isoformat()}.md"), help="Flat markdown output path")
    parser.add_argument("--json-output", type=Path, default=None, help="JSON evaluation output path")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        records = load_replay_records(args.input)
        evaluation = evaluate_strategy_vs_trader(records)
        write_text(args.output, render_markdown_evaluation(evaluation))
        if args.json_output is not None:
            write_json(args.json_output, evaluation)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Wrote evaluation markdown: {args.output}")
    if args.json_output is not None:
        print(f"Wrote evaluation JSON: {args.json_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

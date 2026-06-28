#!/usr/bin/env python3
"""
Offline replay attribution analyzer.

Reads replay JSONL artifacts produced by scripts/replay_signals.py and
summarizes observational StrategySignal behavior against TraderAgent final
actions. This script is intentionally lightweight and execution-free: it does
not import dataflows, state, trading, Telegram, order, notifier, or runtime
modules.
"""
import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional


DEFAULT_INPUT = Path("logs/replay_signals.jsonl")


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
    """Extract TraderAgent final action from known JSONL shapes."""
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


def extract_strategy_action(record: Dict) -> str:
    """Extract strategy_signal.action or return empty string."""
    strategy_signal = record.get("strategy_signal")
    if not isinstance(strategy_signal, dict):
        return ""
    action = strategy_signal.get("action")
    return str(action).lower() if action else ""


def classify_alignment(trader_action: str, strategy_action: str) -> str:
    """Classify TraderAgent-vs-StrategySignal relationship for reporting only.

    This is not an execution mapping. It only labels historical replay records
    so humans can review where the observational strategy layer agreed,
    disagreed, or stayed neutral relative to TraderAgent output.
    """
    trader = (trader_action or "").upper()
    strategy = (strategy_action or "").lower()

    if not trader or not strategy:
        return "missing"

    if (trader, strategy) in {("BUY", "long"), ("SELL", "short"), ("HOLD", "hold")}:
        return "aligned"

    if (trader, strategy) in {("BUY", "short"), ("SELL", "long")}:
        return "conflicted"

    return "neutral_or_observational"


def _market_timeframe(record: Dict) -> str:
    snapshot = record.get("market_snapshot")
    if not isinstance(snapshot, dict):
        return "unknown"
    return str(snapshot.get("timeframe") or "unknown")


def _market_regime(strategy_signal: Dict) -> str:
    attribution = strategy_signal.get("attribution")
    if not isinstance(attribution, dict):
        return "unknown"
    return str(attribution.get("regime") or attribution.get("market_regime") or "unknown")


def _is_volatility_skip_block(strategy_signal: Dict) -> bool:
    strategy_id = str(strategy_signal.get("strategy_id") or "")
    action = str(strategy_signal.get("action") or "")
    if strategy_id == "volatility-skip" and action == "skip":
        return True

    attribution = strategy_signal.get("attribution")
    if not isinstance(attribution, dict):
        return False
    evaluated = attribution.get("evaluated")
    if not isinstance(evaluated, list):
        return False

    for item in evaluated:
        if not isinstance(item, dict):
            continue
        if item.get("strategy_id") == "volatility-skip" and item.get("action") == "skip":
            return True
    return False


def _example(record: Dict, trader_action: str, strategy_signal: Optional[Dict]) -> Dict:
    strategy_signal = strategy_signal if isinstance(strategy_signal, dict) else {}
    return {
        "timestamp": record.get("timestamp"),
        "symbol": record.get("symbol", "unknown"),
        "timeframe": _market_timeframe(record),
        "trader_action": trader_action or "missing",
        "strategy_id": strategy_signal.get("strategy_id", "missing"),
        "strategy_action": strategy_signal.get("action", "missing"),
        "strategy_confidence": strategy_signal.get("confidence"),
        "no_trade_reason": strategy_signal.get("no_trade_reason"),
    }


def _append_example(bucket: List[Dict], example: Dict, max_examples: int) -> None:
    if len(bucket) < max_examples:
        bucket.append(example)


def summarize_strategy_attribution(records: List[Dict], *, max_examples: int = 5) -> Dict:
    """Return JSON-serializable replay attribution summary."""
    by_symbol = Counter()
    by_timeframe = Counter()
    by_strategy_id = Counter()
    by_strategy_action = Counter()
    by_strategy_family = Counter()
    by_market_regime = Counter()
    alignment_matrix = Counter()
    action_alignment = Counter({
        "aligned": 0,
        "conflicted": 0,
        "neutral_or_observational": 0,
        "missing": 0,
    })

    records_with_strategy_signal = 0
    volatility_skip_blocks = 0
    examples = {
        "conflicts": [],
        "volatility_skips": [],
        "missing_strategy_signal": [],
    }

    for record in records:
        if not isinstance(record, dict):
            continue
        symbol = str(record.get("symbol") or "unknown")
        by_symbol[symbol] += 1
        by_timeframe[_market_timeframe(record)] += 1

        trader_action = extract_trader_action(record)
        strategy_signal = record.get("strategy_signal")
        if not isinstance(strategy_signal, dict) or not strategy_signal:
            label = classify_alignment(trader_action, "")
            action_alignment[label] += 1
            _append_example(
                examples["missing_strategy_signal"],
                _example(record, trader_action, None),
                max_examples,
            )
            continue

        records_with_strategy_signal += 1
        strategy_action = extract_strategy_action(record)
        strategy_id = str(strategy_signal.get("strategy_id") or "unknown")
        family = str(strategy_signal.get("family") or "unknown")
        regime = _market_regime(strategy_signal)

        by_strategy_id[strategy_id] += 1
        by_strategy_action[strategy_action or "unknown"] += 1
        by_strategy_family[family] += 1
        by_market_regime[regime] += 1

        matrix_key = f"{trader_action or 'missing'}|{strategy_action or 'missing'}"
        alignment_matrix[matrix_key] += 1
        label = classify_alignment(trader_action, strategy_action)
        action_alignment[label] += 1

        example = _example(record, trader_action, strategy_signal)
        if label == "conflicted":
            _append_example(examples["conflicts"], example, max_examples)

        if _is_volatility_skip_block(strategy_signal):
            volatility_skip_blocks += 1
            _append_example(examples["volatility_skips"], example, max_examples)

    total_records = len(records)
    return {
        "total_records": total_records,
        "records_with_strategy_signal": records_with_strategy_signal,
        "records_missing_strategy_signal": total_records - records_with_strategy_signal,
        "by_symbol": dict(sorted(by_symbol.items())),
        "by_timeframe": dict(sorted(by_timeframe.items())),
        "by_strategy_id": dict(sorted(by_strategy_id.items())),
        "by_strategy_action": dict(sorted(by_strategy_action.items())),
        "by_strategy_family": dict(sorted(by_strategy_family.items())),
        "by_market_regime": dict(sorted(by_market_regime.items())),
        "volatility_skip_blocks": volatility_skip_blocks,
        "action_alignment": dict(action_alignment),
        "alignment_matrix": dict(sorted(alignment_matrix.items())),
        "examples": examples,
    }


def _table(title_left: str, rows: Dict[str, int]) -> List[str]:
    lines = [f"| {title_left} | Count |", "|---|---:|"]
    if not rows:
        lines.append("| _none_ | 0 |")
        return lines
    for key, count in sorted(rows.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| {key} | {count} |")
    return lines


def _render_examples(examples: List[Dict]) -> List[str]:
    if not examples:
        return ["- None"]
    lines = []
    for item in examples:
        lines.append(
            "- "
            f"{item.get('symbol')} {item.get('timeframe')} "
            f"Trader={item.get('trader_action')} "
            f"Strategy={item.get('strategy_id')}:{item.get('strategy_action')} "
            f"Confidence={item.get('strategy_confidence')} "
            f"Reason={item.get('no_trade_reason') or 'n/a'}"
        )
    return lines


def render_markdown_summary(summary: Dict) -> str:
    """Render flat markdown report for review."""
    lines = [
        "# Replay Attribution Summary",
        "",
        "## Overview",
        f"- Total records: {summary.get('total_records', 0)}",
        f"- Records with strategy_signal: {summary.get('records_with_strategy_signal', 0)}",
        f"- Records missing strategy_signal: {summary.get('records_missing_strategy_signal', 0)}",
        "",
        "## Strategy Decisions",
    ]
    lines.extend(_table("Strategy ID", summary.get("by_strategy_id", {})))
    lines.append("")
    lines.extend(_table("Strategy Action", summary.get("by_strategy_action", {})))
    lines.append("")
    lines.extend(_table("Strategy Family", summary.get("by_strategy_family", {})))
    lines.extend([
        "",
        "## Symbols and Timeframes",
    ])
    lines.extend(_table("Symbol", summary.get("by_symbol", {})))
    lines.append("")
    lines.extend(_table("Timeframe", summary.get("by_timeframe", {})))
    lines.extend([
        "",
        "## Market Regimes",
    ])
    lines.extend(_table("Regime", summary.get("by_market_regime", {})))
    lines.extend([
        "",
        "## Trader vs Strategy Comparison",
    ])
    lines.extend(_table("Trader Action + Strategy Action", summary.get("alignment_matrix", {})))
    lines.append("")
    lines.extend(_table("Alignment Label", summary.get("action_alignment", {})))
    lines.extend([
        "",
        "## Volatility Skip Blocks",
        f"- Count: {summary.get('volatility_skip_blocks', 0)}",
        "",
        "## Examples for Review",
        "### Conflicts",
    ])
    lines.extend(_render_examples(summary.get("examples", {}).get("conflicts", [])))
    lines.extend([
        "",
        "### Volatility Skips",
    ])
    lines.extend(_render_examples(summary.get("examples", {}).get("volatility_skips", [])))
    lines.extend([
        "",
        "### Missing Strategy Signal",
    ])
    lines.extend(_render_examples(summary.get("examples", {}).get("missing_strategy_signal", [])))
    lines.extend([
        "",
        "## Notes",
        "- StrategySignal is observational-only.",
        "- This report does not change TraderAgent actions, sizing, risk, or execution.",
        "- No PnL/backtest metrics are included in Batch 3D.",
        "",
    ])
    return "\n".join(lines)


def write_text(path: Path, text: str) -> None:
    """Create parent directory if needed and write UTF-8 text."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json_summary(summary: Dict, path: Path) -> None:
    """Write summary as pretty JSON."""
    write_text(path, json.dumps(summary, ensure_ascii=True, indent=2, sort_keys=True) + "\n")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Analyze observational StrategySignal attribution in replay JSONL artifacts."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input replay JSONL path")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(f"replay-attribution-summary-{date.today().isoformat()}.md"),
        help="Flat markdown output path",
    )
    parser.add_argument("--json-output", type=Path, default=None, help="Optional JSON summary output path")
    parser.add_argument("--max-examples", type=int, default=5, help="Maximum examples per review bucket")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    records = load_replay_records(args.input)
    summary = summarize_strategy_attribution(records, max_examples=max(0, args.max_examples))
    markdown = render_markdown_summary(summary)
    write_text(args.output, markdown)
    if args.json_output:
        write_json_summary(summary, args.json_output)
    print(f"Wrote replay attribution summary: {args.output}")
    if args.json_output:
        print(f"Wrote replay attribution JSON: {args.json_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

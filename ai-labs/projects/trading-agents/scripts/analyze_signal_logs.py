#!/usr/bin/env python3
"""Analyze structured signal JSONL logs including position event analytics."""
import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def load_records(path: Path):
    if not path.exists():
        return []

    records = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Skipping malformed line {line_no}: {e}")
    return records


def pct(value: int, total: int) -> str:
    if total == 0:
        return "0.0%"
    return f"{(value / total) * 100:.1f}%"


def avg(values):
    values = [v for v in values if isinstance(v, (int, float))]
    return sum(values) / len(values) if values else 0.0


def print_counter(title: str, counter: Counter, total: int, limit: int = 20):
    print(f"\n{title}")
    if not counter:
        print("  none")
        return
    for key, count in counter.most_common(limit):
        print(f"  {key}: {count} ({pct(count, total)})")


def analyze(records):
    total = len(records)
    print("Signal Log Analysis")
    print("=" * 80)
    print(f"Total records: {total}")

    if not records:
        return

    symbol_counts = Counter()
    action_counts = Counter()
    direction_counts = Counter()
    execution_counts = Counter()
    hold_reasons = Counter()
    research_consensus = Counter()
    research_winners = Counter()
    risk_status = Counter()
    risk_levels = Counter()
    risk_reasons = Counter()
    risk_multipliers = []
    position_actions = Counter()
    position_reasons = Counter()
    position_confidences = []
    missing_analysts = Counter()
    agent_direction_counts = defaultdict(Counter)
    agent_confidences = defaultdict(list)
    agent_scores = defaultdict(list)
    disagreement_counts = Counter()

    # --- Phase 5D: position event accumulators ---
    position_execution_details = Counter()
    position_close_reasons = Counter()
    position_action_by_symbol = defaultdict(Counter)
    position_action_by_side = defaultdict(Counter)
    # action_by_direction: key = (position_side, final_direction) -> Counter of actions
    action_by_direction = defaultdict(Counter)
    close_fractions = []
    close_reduce_outcomes = {"close_recommended": 0, "close_executed": 0, "close_failed": 0,
                             "reduce_recommended": 0, "reduce_executed": 0, "reduce_failed": 0}

    for record in records:
        symbol = record.get("symbol", "unknown")
        symbol_counts[symbol] += 1
        exec_status = record.get("execution_status", "unknown")
        execution_counts[exec_status] += 1
        position_execution_details[exec_status] += 1

        final = record.get("final_signal") or {}
        final_analysis = final.get("analysis") or {}
        trader = final_analysis.get("trader") or {}
        action = trader.get("action") or final.get("metadata", {}).get("final_action") or "unknown"
        direction = final.get("direction", "unknown")
        action_counts[action] += 1
        direction_counts[direction] += 1

        hold_reason = trader.get("hold_reason") or final.get("metadata", {}).get("hold_reason")
        if hold_reason:
            hold_reasons[hold_reason] += 1

        debate = record.get("research_debate") or {}
        if debate:
            research_consensus[debate.get("consensus", "unknown")] += 1
            research_winners[debate.get("winner", "unknown")] += 1

        risk = record.get("risk_decision") or {}
        if risk:
            approved = risk.get("approved")
            risk_status["approved" if approved else "rejected"] += 1
            risk_levels[risk.get("risk_level", "unknown")] += 1
            reason = risk.get("reason")
            if reason:
                risk_reasons[reason] += 1
            multiplier = risk.get("position_size_multiplier")
            if isinstance(multiplier, (int, float)):
                risk_multipliers.append(multiplier)
        else:
            risk_status["not_evaluated"] += 1

        position = record.get("position_decision") or {}
        if position:
            pos_action = position.get("action", "unknown")
            position_actions[pos_action] += 1
            pos_reason = position.get("reason")
            if pos_reason:
                position_reasons[pos_reason] += 1
            confidence = position.get("confidence")
            if isinstance(confidence, (int, float)):
                position_confidences.append(confidence)

            # Phase 5D per-record position analytics
            position_action_by_symbol[symbol][pos_action] += 1

            pos_side = (position.get("position") or {}).get("side", "unknown")
            position_action_by_side[pos_side][pos_action] += 1

            action_by_direction[(pos_side, direction)][pos_action] += 1

            close_reason_str = position.get("close_reason", "unknown")
            if close_reason_str and pos_action in ("close_position", "reduce_position"):
                position_close_reasons[close_reason_str] += 1

            fraction = position.get("close_fraction")
            if isinstance(fraction, (int, float)):
                close_fractions.append(fraction)

            # Close/reduce success rate tracking
            if pos_action == "close_position":
                close_reduce_outcomes["close_recommended"] += 1
                if exec_status == "position_closed":
                    close_reduce_outcomes["close_executed"] += 1
                elif exec_status == "position_close_failed":
                    close_reduce_outcomes["close_failed"] += 1
            elif pos_action == "reduce_position":
                close_reduce_outcomes["reduce_recommended"] += 1
                if exec_status == "position_reduced":
                    close_reduce_outcomes["reduce_executed"] += 1
                elif exec_status == "position_reduce_failed":
                    close_reduce_outcomes["reduce_failed"] += 1

        for name in record.get("missing_analysts", []):
            missing_analysts[name] += 1

        analysts = record.get("analysts") or {}
        directions = []
        for name, signal in analysts.items():
            direction = signal.get("direction", "unknown")
            directions.append(direction)
            agent_direction_counts[name][direction] += 1
            agent_confidences[name].append(signal.get("confidence"))
            agent_scores[name].append(signal.get("sub_score"))

        non_neutral = {d for d in directions if d in ("bullish", "bearish")}
        if len(non_neutral) > 1:
            disagreement_counts["bullish_vs_bearish"] += 1
        elif "bullish" in non_neutral:
            disagreement_counts["bullish_only"] += 1
        elif "bearish" in non_neutral:
            disagreement_counts["bearish_only"] += 1
        else:
            disagreement_counts["all_neutral_or_missing"] += 1

    # =========================================================================
    # Core Signal Analysis (unchanged)
    # =========================================================================
    print_counter("Symbols", symbol_counts, total)
    print_counter("Final Actions", action_counts, total)
    print_counter("Final Directions", direction_counts, total)
    print_counter("Execution Status", execution_counts, total)
    print_counter("Hold Reasons", hold_reasons, total)
    print_counter("Research Consensus", research_consensus, total)
    print_counter("Research Winners", research_winners, total)
    print_counter("Risk Status", risk_status, total)
    print_counter("Risk Levels", risk_levels, total)
    print_counter("Risk Reasons", risk_reasons, total)
    if risk_multipliers:
        print(f"\nRisk Multiplier Average\n  {avg(risk_multipliers):.3f}")
    print_counter("Position Actions", position_actions, total)
    print_counter("Position Reasons", position_reasons, total)
    if position_confidences:
        print(f"\nPosition Decision Confidence Average\n  {avg(position_confidences):.3f}")
    print_counter("Analyst Disagreement", disagreement_counts, total)
    print_counter("Missing Analysts", missing_analysts, total)

    print("\nAgent Summary")
    for name in sorted(agent_direction_counts.keys()):
        dirs = ", ".join(f"{k}:{v}" for k, v in agent_direction_counts[name].most_common())
        print(
            f"  {name}: directions[{dirs}] "
            f"avg_score={avg(agent_scores[name]):.3f} avg_conf={avg(agent_confidences[name]):.3f}"
        )

    # =========================================================================
    # Phase 5D: Position Event Analytics
    # =========================================================================
    print(f"\n{'=' * 80}")
    print("Position Event Analytics (Phase 5D)")
    print("=" * 80)

    # --- Position Execution Breakdown ---
    all_position_exec_states = [
        "position_hold",
        "position_close_recommended", "position_closed", "position_close_failed",
        "position_reduce_recommended", "position_reduced", "position_reduce_failed",
        "position_reverse_recommended",
        "position_reversed",
        "position_reversed_close_only",
        "position_reverse_close_failed",
        "position_reverse_open_failed",
    ]
    position_total = sum(position_execution_details.get(s, 0) for s in all_position_exec_states + ["hold", "not_evaluated", "executed"])
    if position_total > 0:
        print(f"\nPosition Execution Details ({position_total} records with position or hold)")
        for s in all_position_exec_states:
            count = position_execution_details.get(s, 0)
            if count:
                print(f"  {s}: {count}")
    else:
        print("\nPosition Execution Details\n  no position-related records yet")

    # --- Position Close Reasons ---
    print_counter("Position Close/Reduce Reasons", position_close_reasons, sum(position_close_reasons.values()))

    # --- Position Actions By Symbol ---
    if position_action_by_symbol:
        print("\nPosition Actions By Symbol")
        for sym in sorted(position_action_by_symbol.keys()):
            actions_str = ", ".join(f"{k}={v}" for k, v in position_action_by_symbol[sym].most_common())
            print(f"  {sym}: {actions_str}")
    else:
        print("\nPosition Actions By Symbol\n  none")

    # --- Position Actions By Side ---
    if position_action_by_side:
        print("\nPosition Actions By Position Side")
        for side in sorted(position_action_by_side.keys()):
            actions_str = ", ".join(f"{k}={v}" for k, v in position_action_by_side[side].most_common())
            print(f"  {side}: {actions_str}")
    else:
        print("\nPosition Actions By Position Side\n  none")

    # --- Position Action vs Final Direction ---
    if action_by_direction:
        print("\nPosition Action vs Final Direction")
        for (pos_side, final_dir), action_counter in sorted(action_by_direction.items()):
            actions_str = ", ".join(f"{k}={v}" for k, v in action_counter.most_common())
            print(f"  {pos_side} pos + {final_dir} final: {actions_str}")
    else:
        print("\nPosition Action vs Final Direction\n  none")

    # --- Position Reduce Details ---
    if close_fractions:
        print(f"\nPosition Close/Reduce Fractions\n  avg_close_fraction={avg(close_fractions):.3f} count={len(close_fractions)}")

    # --- Close/Reduce Success Rate ---
    cr = close_reduce_outcomes
    has_close = cr["close_recommended"] > 0
    has_reduce = cr["reduce_recommended"] > 0
    if has_close or has_reduce:
        print("\nPosition Execution Success Rate")
        if has_close:
            print(f"  close: {cr['close_executed']}/{cr['close_recommended']} recommended executed"
                  f"{f' ({cr['close_failed']} failed)' if cr['close_failed'] else ''}")
        if has_reduce:
            print(f"  reduce: {cr['reduce_executed']}/{cr['reduce_recommended']} recommended executed"
                  f"{f' ({cr['reduce_failed']} failed)' if cr['reduce_failed'] else ''}")


def main():
    parser = argparse.ArgumentParser(description="Analyze trading signal JSONL logs")
    parser.add_argument(
        "--path",
        default=str(project_root / "logs" / "signals.jsonl"),
        help="Path to signals.jsonl",
    )
    args = parser.parse_args()

    path = Path(args.path)
    records = load_records(path)
    analyze(records)


if __name__ == "__main__":
    main()

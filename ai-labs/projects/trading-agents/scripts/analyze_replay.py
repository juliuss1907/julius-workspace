#!/usr/bin/env python3
"""Analyze replay signal logs from Phase 6A."""
import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def pct(value: int, total: int) -> str:
    if total == 0:
        return "0.0%"
    return f"{(value / total) * 100:.1f}%"


def avg(values):
    values = [v for v in values if isinstance(v, (int, float))]
    return sum(values) / len(values) if values else 0.0


def load(path: Path):
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Skipping line {line_no}: {e}")
    return records


def print_bar(title: str, counter: Counter, total: int, limit: int = 20):
    print(f"\n{title}")
    if not counter:
        print("  none")
        return
    for key, count in counter.most_common(limit):
        print(f"  {key}: {count} ({pct(count, total)})")


def analyze(records):
    total = len(records)
    print("=" * 72)
    print(f"Replay Analysis — {total} windows")
    print("=" * 72)

    if not records:
        print("No records found.")
        return

    symbol = Counter()
    action = Counter()
    direction = Counter()
    hold_reasons = Counter()
    consensus = Counter()
    tech_dir = Counter()
    deriv_dir = Counter()
    tech_vs_final = Counter()
    scores = defaultdict(list)
    confidences = defaultdict(list)
    disagreement = Counter()
    hourly_buckets = defaultdict(lambda: {"total": 0, "non_hold": 0})

    for record in records:
        symbol[record.get("symbol", "?")] += 1

        final = record.get("final_signal") or {}
        fd = final.get("direction", "unknown")
        direction[fd] += 1
        action[final.get("analysis", {}).get("trader", {}).get("action", "unknown")] += 1

        hr = final.get("analysis", {}).get("trader", {}).get("hold_reason")
        if fd == "neutral" and hr:
            hold_reasons[hr] += 1

        debate = record.get("research_debate") or {}
        if debate:
            consensus[debate.get("consensus", "unknown")] += 1

        analysts = record.get("analysts") or {}
        tech = analysts.get("technical") or {}
        deriv = analysts.get("derivatives") or {}
        tech_dir[tech.get("direction", "FAIL")] += 1
        deriv_dir[deriv.get("direction", "FAIL")] += 1

        if tech and fd != "FAIL":
            tvf = f"tech_{tech.get('direction','?')}→final_{fd}"
            tech_vs_final[tvf] += 1

        for name, signal in analysts.items():
            if signal:
                scores[name].append(signal.get("sub_score", 0))
                confidences[name].append(signal.get("confidence", 0))

        non_neutral = set()
        for name in ("technical", "derivatives"):
            sig = analysts.get(name) or {}
            d = sig.get("direction")
            if d in ("bullish", "bearish"):
                non_neutral.add(d)
            elif sig and d != "FAIL":
                non_neutral.add("neutral_deriv")

        if len(non_neutral) > 1:
            disagreement["conflicting"] += 1
        elif "bullish" in non_neutral:
            disagreement["bullish_only"] += 1
        elif "bearish" in non_neutral:
            disagreement["bearish_only"] += 1
        else:
            disagreement["all_neutral"] += 1

    print(f"\nAction Distribution ({total} total)")
    for k, v in sorted(action.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v} ({pct(v, total)})")

    print(f"\nFinal Direction")
    for k, v in sorted(direction.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v} ({pct(v, total)})")

    print_bar("Hold Reasons", hold_reasons, direction.get("neutral", 0))

    print(f"\nConfidence Stats")
    for name in sorted(confidences.keys()):
        vals = confidences[name]
        print(f"  {name}: n={len(vals)} avg={avg(vals):.3f} min={min(vals):.3f} max={max(vals):.3f}")

    print_bar("Research Consensus", consensus, total)

    print("\nTechnical Direction")
    for k, v in tech_dir.most_common():
        print(f"  {k}: {v} ({pct(v, total)})")

    print(f"\nDerivatives Direction")
    for k, v in deriv_dir.most_common():
        print(f"  {k}: {v} ({pct(v, total)})")

    print(f"\nTechnical → Final Alignment")
    for k, v in sorted(tech_vs_final.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v} ({pct(v, total)})")

    print_bar("Analyst Disagreement", disagreement, total)

    print("\nConfidence Distribution (Final Signal)")
    buckets = Counter()
    for c in confidences.get("TraderAgent", []):
        bucket = int(c * 10) / 10
        buckets[f"{bucket:.1f}-{bucket + 0.1:.1f}"] += 1
    for k, v in sorted(buckets.items()):
        bar = "#" * v
        print(f"  {k}: {v:4d} {bar}")


def main():
    parser = argparse.ArgumentParser(description="Analyze replay signal logs")
    parser.add_argument("--path", default="logs/replay_signals.jsonl", help="Path to replay JSONL")
    args = parser.parse_args()
    path = Path(project_root) / args.path if not Path(args.path).is_absolute() else Path(args.path)
    records = load(path)
    analyze(records)


if __name__ == "__main__":
    main()

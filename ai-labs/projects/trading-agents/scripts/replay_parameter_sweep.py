#!/usr/bin/env python3
"""
Replay + Parameter Sweep — Phase 6E.

Runs replay agent stack across multiple named config variants, feeds each
variant's replay output through the trade simulator, and produces a
ranking report.

Named variants (avoiding full cartesian explosion):

  baseline                 - current default_params
  tech_heavy               - higher technical weight
  deriv_heavy              - higher derivatives weight
  lower_thresholds         - more aggressive BUY/SELL
  higher_thresholds        - more conservative BUY/SELL
  more_aggressive          - lower hold cap
  more_conservative        - higher hold cap

Output:
  logs/replay_sweep_report.json
  logs/replay_sweep_report.md
  logs/replay_sweep_variants/  (per-variant replay JSONL + trades JSONL)
"""
import argparse
import asyncio
import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils import config as cfg

from scripts.simulate_trades import simulate


VARIANTS = {
    "baseline": {},
    "tech_heavy": {
        "analyst_weights": {
            "full": {
                "technical": 0.80,
                "news": 0.02,
                "fundamentals": 0.03,
                "sentiment": 0.02,
                "derivatives": 0.13,
            }
        }
    },
    "deriv_heavy": {
        "analyst_weights": {
            "full": {
                "technical": 0.65,
                "news": 0.02,
                "fundamentals": 0.03,
                "sentiment": 0.02,
                "derivatives": 0.28,
            }
        }
    },
    "lower_thresholds": {
        "analyst_weights": {
            "direction_thresholds": {
                "bullish_above": 0.54,
                "bearish_below": 0.46,
                "hold_confidence_cap": 0.55,
            }
        }
    },
    "higher_thresholds": {
        "analyst_weights": {
            "direction_thresholds": {
                "bullish_above": 0.62,
                "bearish_below": 0.38,
                "hold_confidence_cap": 0.55,
            }
        }
    },
    "more_aggressive": {
        "analyst_weights": {
            "direction_thresholds": {
                "bullish_above": 0.55,
                "bearish_below": 0.45,
                "hold_confidence_cap": 0.50,
            }
        }
    },
    "more_conservative": {
        "analyst_weights": {
            "direction_thresholds": {
                "bullish_above": 0.60,
                "bearish_below": 0.40,
                "hold_confidence_cap": 0.60,
            }
        }
    },
}


def deep_merge(base: dict, override: dict) -> dict:
    """Deep merge override into base (returns new dict)."""
    result = dict(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def score_variant(summary: dict) -> float:
    trades = summary.get("simulated_trades", 0)
    total_pnl = summary.get("total_pnl_pct", 0.0)
    avg_pnl = summary.get("avg_pnl_pct", 0.0)
    win_rate = summary.get("win_rate", 0.0)

    penalty = 0.0
    if trades < 3:
        penalty = 0.5
    elif trades < 5:
        penalty = 0.25

    return round(
        total_pnl
        + avg_pnl * 2
        + win_rate * 5
        - penalty,
        4,
    )


async def run_replay_variant(
    variant_name: str,
    config_override: dict,
    base_config: dict,
    symbols: list,
    days: int,
    window: int,
    step: int,
    output_jsonl: Path,
) -> dict:
    """Run replay for a single variant. Returns count summary."""
    from scripts.replay_signals import SignalReplay

    merged_config = deep_merge(base_config, config_override)
    replay = SignalReplay(
        symbols=symbols,
        days=days,
        window_size=window,
        step_candles=step,
        output_path=str(output_jsonl),
        config_override=merged_config,
    )
    await replay.run()
    return {"variant": variant_name, "replay_path": str(output_jsonl)}


def load_records(path: Path):
    records = []
    if not path.exists():
        return records
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return records


def summarize_simulation(trades: list, stats: dict) -> dict:
    total = stats["simulated_trades"]
    return {
        "trades": total,
        "wins": stats["wins"],
        "losses": stats["losses"],
        "breakeven": stats["breakeven"],
        "win_rate": round(stats["wins"] / max(total, 1), 4),
        "total_pnl_pct": round(sum(stats["pnl_pcts"]), 4),
        "avg_pnl_pct": round(sum(stats["pnl_pcts"]) / max(total, 1), 4),
        "max_pnl_pct": round(max(stats["pnl_pcts"]), 4) if stats["pnl_pcts"] else 0.0,
        "min_pnl_pct": round(min(stats["pnl_pcts"]), 4) if stats["pnl_pcts"] else 0.0,
        "avg_hold_candles": round(sum(stats["hold_durations"]) / max(total, 1), 1) if stats["hold_durations"] else 0.0,
        "exit_reasons": dict(stats["exit_reasons"].most_common()),
    }


def summarize_replay(records: list) -> dict:
    from collections import Counter
    by_action = Counter()
    by_direction = Counter()
    confidences = []
    for rec in records:
        final = rec.get("final_signal") or {}
        action = (final.get("analysis") or {}).get("trader", {}).get("action", "HOLD")
        by_action[action] += 1
        by_direction[final.get("direction", "unknown")] += 1
        conf = final.get("confidence", 0)
        if conf is not None:
            confidences.append(conf)
    total = len(records)
    return {
        "signals": total,
        "by_action": dict(by_action.most_common()),
        "by_direction": dict(by_direction.most_common()),
        "hold_ratio": round(by_action.get("HOLD", 0) / max(total, 1), 4),
        "avg_confidence": round(sum(confidences) / max(len(confidences), 1), 4) if confidences else 0.0,
    }


async def run_sweep(
    base_config: dict,
    symbols: list,
    days: int,
    window: int,
    step: int,
    output_dir: Path,
) -> list:
    """Run all variants, simulate each, return ranked rows."""
    rows = []

    for variant_name, config_override in VARIANTS.items():
        print(f"\n--- Variant: {variant_name} ---")
        variant_dir = output_dir / variant_name
        variant_dir.mkdir(parents=True, exist_ok=True)
        replay_path = variant_dir / "replay.jsonl"
        trades_path = variant_dir / "trades.jsonl"
        summary_path = variant_dir / "summary.json"

        try:
            await run_replay_variant(
                variant_name, config_override, base_config,
                symbols, days, window, step, replay_path,
            )
        except Exception as e:
            print(f"  replay failed: {e}")
            rows.append({
                "variant": variant_name,
                "error": str(e),
                "score": -999.0,
            })
            continue

        records = load_records(replay_path)
        replay_summary = summarize_replay(records)

        try:
            trades, stats = simulate(
                records,
                base_config,
                output_path=str(trades_path),
                summary_path=str(summary_path),
            )
        except Exception as e:
            print(f"  simulation failed: {e}")
            rows.append({
                "variant": variant_name,
                "replay": replay_summary,
                "error": str(e),
                "score": -999.0,
            })
            continue

        sim_summary = summarize_simulation(trades, stats)
        score = score_variant(sim_summary)
        rows.append({
            "variant": variant_name,
            "replay": replay_summary,
            "simulation": sim_summary,
            "score": score,
        })
        print(f"  signals={replay_summary['signals']} trades={sim_summary['trades']} "
              f"win_rate={sim_summary['win_rate']*100:.1f}% "
              f"total_pnl={sim_summary['total_pnl_pct']:+.2f}% score={score:+.3f}")

    rows.sort(key=lambda r: r.get("score", -999.0), reverse=True)
    for i, row in enumerate(rows, 1):
        row["rank"] = i
    return rows


def write_json_report(rows: list, output_dir: Path, json_path: str):
    data = {
        "generated_at": datetime.now().isoformat(),
        "variants": list(VARIANTS.keys()),
        "results": rows,
    }
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    with Path(json_path).open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=True)


def write_md_report(rows: list, md_path: str):
    lines = []
    lines.append("# Replay Parameter Sweep Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().isoformat()}")
    lines.append(f"**Variants:** {', '.join(VARIANTS.keys())}")
    lines.append("")
    lines.append("## Ranking")
    lines.append("")
    lines.append("| Rank | Variant | Signals | HOLD% | Trades | Win Rate | Total PnL% | Avg PnL% | Score |")
    lines.append("|------|---------|---------|-------|--------|----------|------------|----------|-------|")
    for r in rows:
        rep = r.get("replay", {})
        sim = r.get("simulation", {})
        lines.append(
            f"| {r['rank']} | {r['variant']} | {rep.get('signals', '-')} | "
            f"{rep.get('hold_ratio', 0)*100:.0f}% | {sim.get('trades', '-')} | "
            f"{sim.get('win_rate', 0)*100:.1f}% | {sim.get('total_pnl_pct', 0):+.2f}% | "
            f"{sim.get('avg_pnl_pct', 0):+.2f}% | {r.get('score', 0):+.3f} |"
        )
    lines.append("")

    if rows:
        best = rows[0]
        lines.append("## Best Variant")
        lines.append("")
        lines.append(f"- **variant:** {best['variant']}")
        lines.append(f"- **score:** {best.get('score', 0):+.3f}")
        sim = best.get("simulation", {})
        if sim:
            lines.append(f"- **trades:** {sim.get('trades', 0)}")
            lines.append(f"- **win_rate:** {sim.get('win_rate', 0)*100:.1f}%")
            lines.append(f"- **total_pnl_pct:** {sim.get('total_pnl_pct', 0):+.2f}%")
        lines.append("")
        lines.append("> Do NOT auto-apply. Review sample size, HOLD ratio, and whether one-sided bias dominates before changing default config.")

    Path(md_path).parent.mkdir(parents=True, exist_ok=True)
    with Path(md_path).open("w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def print_report(rows: list):
    print(f"\n{'=' * 80}")
    print("Replay Parameter Sweep Report")
    print(f"{'=' * 80}")
    print(f"{'Rank':<4} {'Variant':<22} {'Signals':<7} {'HOLD%':<5} {'Trades':<6} {'WinR%':<6} {'Total':<8} {'Avg':<8} {'Score':<8}")
    print("-" * 80)
    for r in rows:
        rep = r.get("replay", {})
        sim = r.get("simulation", {})
        print(
            f"{r['rank']:<4} {r['variant']:<22} {rep.get('signals', '-'):<7} "
            f"{rep.get('hold_ratio', 0)*100:<5.0f} {sim.get('trades', '-'):<6} "
            f"{sim.get('win_rate', 0)*100:<6.1f} {sim.get('total_pnl_pct', 0):<+8.2f} "
            f"{sim.get('avg_pnl_pct', 0):<+8.2f} {r.get('score', 0):<+8.3f}"
        )


def main():
    parser = argparse.ArgumentParser(description="Replay + parameter sweep")
    parser.add_argument("--symbols", nargs="+", default=["BTCUSDT", "ETHUSDT", "SOLUSDT"])
    parser.add_argument("--days", type=int, default=7, help="Days of historical data per variant")
    parser.add_argument("--window", type=int, default=200)
    parser.add_argument("--step", type=int, default=4)
    parser.add_argument("--variants", nargs="+", default=None, help="Subset of variants to run (default: all)")
    parser.add_argument("--output-dir", default="logs/replay_sweep_variants")
    parser.add_argument("--json-out", default="logs/replay_sweep_report.json")
    parser.add_argument("--md-out", default="logs/replay_sweep_report.md")
    parser.add_argument("--baseline-only", action="store_true", help="Only run baseline variant (smoke test)")
    args = parser.parse_args()

    base_config = cfg.load_default_params()
    output_dir = Path(args.output_dir)

    variants_to_run = dict(VARIANTS)
    if args.variants:
        variants_to_run = {k: VARIANTS[k] for k in args.variants if k in VARIANTS}
        if not variants_to_run:
            print(f"No valid variants specified. Available: {list(VARIANTS.keys())}")
            sys.exit(1)
    if args.baseline_only:
        variants_to_run = {"baseline": {}}
    # Monkey-patch VARIANTS dict for the rest of the script
    VARIANTS.clear()
    VARIANTS.update(variants_to_run)

    print(f"Running {len(variants_to_run)} variants: {list(variants_to_run.keys())}")
    print(f"Symbols: {args.symbols}, days={args.days}, window={args.window}, step={args.step}")
    print(f"Output: {output_dir}")

    rows = asyncio.run(run_sweep(
        base_config, args.symbols, args.days, args.window, args.step, output_dir,
    ))
    write_json_report(rows, output_dir, args.json_out)
    write_md_report(rows, args.md_out)
    print_report(rows)
    print(f"\nWrote JSON report to {args.json_out}")
    print(f"Wrote Markdown report to {args.md_out}")
    print(f"Per-variant artifacts in {output_dir}/")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Parameter Sweep — Phase 6D.

Runs the trade simulator across multiple parameter combinations and produces
a ranking report (JSON + Markdown).

Sweep dimensions:
  - min_confidence
  - fee_pct
  - slippage_pct

Output:
  logs/parameter_sweep_report.json
  logs/parameter_sweep_report.md
"""
import argparse
import json
import sys
from datetime import datetime
from itertools import product
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils import config as cfg

from scripts.simulate_trades import load_records, simulate


def generate_sweep_configs(sweep_cfg: dict, base_config: dict) -> list:
    """Generate all parameter combinations to evaluate."""
    min_conf_values = sweep_cfg.get("min_confidence_values", [0.55])
    fee_values = sweep_cfg.get("fee_pct_values", [0.001])
    slip_values = sweep_cfg.get("slippage_pct_values", [0.0005])

    configs = []
    for mc, fee, slip in product(min_conf_values, fee_values, slip_values):
        cfg_copy = {**base_config}
        cfg_copy["simulation"] = {
            **base_config.get("simulation", {}),
            "min_confidence": mc,
            "fee_pct": fee,
            "slippage_pct": slip,
        }
        configs.append({
            "config": cfg_copy,
            "min_confidence": mc,
            "fee_pct": fee,
            "slippage_pct": slip,
        })
    return configs


def score_result(summary: dict, sweep_cfg: dict) -> float:
    """Compute a numeric score to rank configs.

    Components:
      - total_pnl_pct
      - avg_pnl_pct * 2
      - win_rate * 5
      - penalty for low trade count
    """
    trades = summary.get("simulated_trades", 0)
    total_pnl = summary.get("total_pnl_pct", 0.0)
    avg_pnl = summary.get("avg_pnl_pct", 0.0)
    win_rate = summary.get("win_rate", 0.0)

    min_trades_no_penalty = sweep_cfg.get("min_trades_no_penalty", 5)
    min_trades_mild_penalty = sweep_cfg.get("min_trades_mild_penalty", 3)

    penalty = 0.0
    if trades < min_trades_mild_penalty:
        penalty = 0.5
    elif trades < min_trades_no_penalty:
        penalty = 0.25

    return round(
        total_pnl
        + avg_pnl * 2
        + win_rate * 5
        - penalty,
        4,
    )


def run_sweep(records: list, sweep_cfg: dict, base_config: dict) -> list:
    """Run simulator over all parameter combos and return ranked results."""
    configs = generate_sweep_configs(sweep_cfg, base_config)
    rows = []

    for combo in configs:
        try:
            trades, stats = simulate(
                records,
                combo["config"],
                output_path=str(Path("/dev/null")),
                summary_path=str(Path("/dev/null")),
            )
        except Exception as e:
            rows.append({
                "min_confidence": combo["min_confidence"],
                "fee_pct": combo["fee_pct"],
                "slippage_pct": combo["slippage_pct"],
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0,
                "total_pnl_pct": 0.0,
                "avg_pnl_pct": 0.0,
                "max_pnl_pct": 0.0,
                "min_pnl_pct": 0.0,
                "avg_hold_candles": 0.0,
                "score": -999.0,
                "error": str(e),
            })
            continue

        total_pnl = sum(stats["pnl_pcts"])
        avg_pnl = (total_pnl / max(stats["simulated_trades"], 1)) if stats["simulated_trades"] > 0 else 0.0
        wins = stats["wins"]
        losses = stats["losses"]
        win_rate = round(wins / max(stats["simulated_trades"], 1), 4)
        avg_hold = round(sum(stats["hold_durations"]) / max(stats["simulated_trades"], 1), 1) if stats["hold_durations"] else 0.0

        summary_dict = {
            "simulated_trades": stats["simulated_trades"],
            "total_pnl_pct": total_pnl,
            "avg_pnl_pct": avg_pnl,
            "win_rate": win_rate,
        }
        score = score_result(summary_dict, sweep_cfg)

        rows.append({
            "min_confidence": combo["min_confidence"],
            "fee_pct": combo["fee_pct"],
            "slippage_pct": combo["slippage_pct"],
            "trades": stats["simulated_trades"],
            "wins": wins,
            "losses": losses,
            "win_rate": win_rate,
            "total_pnl_pct": round(total_pnl, 4),
            "avg_pnl_pct": round(avg_pnl, 4),
            "max_pnl_pct": round(max(stats["pnl_pcts"]), 4) if stats["pnl_pcts"] else 0.0,
            "min_pnl_pct": round(min(stats["pnl_pcts"]), 4) if stats["pnl_pcts"] else 0.0,
            "avg_hold_candles": avg_hold,
            "score": score,
        })

    rows.sort(key=lambda r: r["score"], reverse=True)
    for i, row in enumerate(rows, 1):
        row["rank"] = i
    return rows


def write_json_report(rows: list, sweep_cfg: dict, source: str, path: str):
    data = {
        "generated_at": datetime.now().isoformat(),
        "source_replay": source,
        "sweep_config": {
            "min_confidence_values": sweep_cfg.get("min_confidence_values"),
            "fee_pct_values": sweep_cfg.get("fee_pct_values"),
            "slippage_pct_values": sweep_cfg.get("slippage_pct_values"),
            "min_trades_no_penalty": sweep_cfg.get("min_trades_no_penalty"),
            "min_trades_mild_penalty": sweep_cfg.get("min_trades_mild_penalty"),
        },
        "combinations_run": len(rows),
        "results": rows,
    }
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=True)


def write_md_report(rows: list, source: str, path: str):
    lines = []
    lines.append("# Parameter Sweep Report")
    lines.append("")
    lines.append(f"**Source replay:** `{source}`")
    lines.append(f"**Generated:** {datetime.now().isoformat()}")
    lines.append(f"**Combinations:** {len(rows)}")
    lines.append("")
    lines.append("## Ranking")
    lines.append("")
    lines.append("| Rank | Min Conf | Fee | Slip | Trades | W/L | Win Rate | Total PnL% | Avg PnL% | Max PnL% | Min PnL% | Avg Hold | Score |")
    lines.append("|------|----------|-----|------|--------|-----|----------|------------|----------|----------|----------|----------|-------|")
    for r in rows:
        lines.append(
            f"| {r['rank']} | {r['min_confidence']:.2f} | {r['fee_pct']:.4f} | {r['slippage_pct']:.4f} | "
            f"{r['trades']} | {r['wins']}W/{r['losses']}L | {r['win_rate']*100:.1f}% | "
            f"{r['total_pnl_pct']:+.2f}% | {r['avg_pnl_pct']:+.2f}% | {r['max_pnl_pct']:+.2f}% | {r['min_pnl_pct']:+.2f}% | "
            f"{r['avg_hold_candles']:.1f} | {r['score']:+.3f} |"
        )
    lines.append("")

    if rows:
        top = rows[0]
        lines.append("## Best Config")
        lines.append("")
        lines.append(f"- **min_confidence:** {top['min_confidence']}")
        lines.append(f"- **fee_pct:** {top['fee_pct']}")
        lines.append(f"- **slippage_pct:** {top['slippage_pct']}")
        lines.append(f"- **trades:** {top['trades']}")
        lines.append(f"- **win_rate:** {top['win_rate']*100:.1f}%")
        lines.append(f"- **total_pnl_pct:** {top['total_pnl_pct']:+.2f}%")
        lines.append(f"- **avg_pnl_pct:** {top['avg_pnl_pct']:+.2f}%")
        lines.append(f"- **score:** {top['score']:+.3f}")
        lines.append("")
        lines.append("> Do NOT auto-apply. Review the trade sample size and the trade count vs score penalty before changing config.")

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def print_report(rows: list, source: str):
    print(f"\n{'=' * 80}")
    print(f"Parameter Sweep Report — {source}")
    print(f"{'=' * 80}")
    print(f"Combinations: {len(rows)}\n")
    print(f"{'Rank':<4} {'MinConf':<8} {'Fee':<6} {'Slip':<6} {'Trades':<6} {'WinRate':<7} {'TotalPnl':<9} {'AvgPnl':<8} {'Score':<7}")
    print("-" * 80)
    for r in rows:
        print(
            f"{r['rank']:<4} {r['min_confidence']:<8.2f} {r['fee_pct']:<6.4f} {r['slippage_pct']:<6.4f} "
            f"{r['trades']:<6} {r['win_rate']*100:<7.1f} {r['total_pnl_pct']:<+9.2f} "
            f"{r['avg_pnl_pct']:<+8.2f} {r['score']:<+7.3f}"
        )
    if rows:
        top = rows[0]
        print(f"\nBest: min_conf={top['min_confidence']} trades={top['trades']} "
              f"win_rate={top['win_rate']*100:.1f}% total_pnl={top['total_pnl_pct']:+.2f}% score={top['score']:+.3f}")


def main():
    parser = argparse.ArgumentParser(description="Parameter sweep for trade simulation")
    parser.add_argument("--input", default="logs/replay_signals.jsonl", help="Path to replay JSONL")
    parser.add_argument("--json-out", default="logs/parameter_sweep_report.json", help="JSON report path")
    parser.add_argument("--md-out", default="logs/parameter_sweep_report.md", help="Markdown report path")
    parser.add_argument("--min-confidence", type=float, nargs="+", default=None,
                        help="Override min_confidence values to sweep")
    parser.add_argument("--fee", type=float, nargs="+", default=None,
                        help="Override fee_pct values to sweep")
    parser.add_argument("--slippage", type=float, nargs="+", default=None,
                        help="Override slippage_pct values to sweep")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        sys.exit(1)

    records = load_records(input_path)
    print(f"Loaded {len(records)} signal records from {input_path}")

    base_config = cfg.load_default_params()
    sweep_cfg = dict(base_config.get("parameter_sweep", {}))

    if args.min_confidence is not None:
        sweep_cfg["min_confidence_values"] = args.min_confidence
    if args.fee is not None:
        sweep_cfg["fee_pct_values"] = args.fee
    if args.slippage is not None:
        sweep_cfg["slippage_pct_values"] = args.slippage

    rows = run_sweep(records, sweep_cfg, base_config)
    write_json_report(rows, sweep_cfg, str(input_path), args.json_out)
    write_md_report(rows, str(input_path), args.md_out)
    print_report(rows, str(input_path))
    print(f"\nWrote JSON report to {args.json_out}")
    print(f"Wrote Markdown report to {args.md_out}")


if __name__ == "__main__":
    main()

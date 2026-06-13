#!/usr/bin/env python3
"""Backtest Report Dashboard — Phase 6G.

Aggregates replay, simulation, parameter sweep, and replay sweep outputs
into a single human-readable Markdown + JSON dashboard.

Inputs (auto-discovered, all optional):
  logs/replay_signals.jsonl
  logs/simulation_summary.json
  logs/simulated_trades.jsonl
  logs/parameter_sweep_report.json
  logs/replay_sweep_report.json

Outputs:
  reports/backtest-dashboard.md
  reports/backtest-dashboard.json
"""
import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


DEFAULT_CONFIG = {
    "min_trade_sample_warning": 10,
    "high_hold_ratio_warning": 0.85,
    "side_bias_warning_pct": 0.80,
    "max_avg_hold_candles_warning": 72,
}


def load_json(path: Path):
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def load_jsonl(path: Path):
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


def summarize_replay(records):
    if not records:
        return {"signals": 0, "by_action": {}, "by_direction": {}, "hold_ratio": 0.0, "avg_confidence": 0.0}
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


def summarize_trades(trades):
    if not trades:
        return {"count": 0, "by_symbol": {}, "by_side": {}, "by_exit_reason": {}}
    by_symbol = Counter()
    by_side = Counter()
    by_exit_reason = Counter()
    for t in trades:
        by_symbol[t.get("symbol", "unknown")] += 1
        by_side[t.get("side", "unknown")] += 1
        by_exit_reason[t.get("exit_reason", "unknown")] += 1
    return {
        "count": len(trades),
        "by_symbol": dict(by_symbol.most_common()),
        "by_side": dict(by_side.most_common()),
        "by_exit_reason": dict(by_exit_reason.most_common()),
    }


def generate_warnings(replay_summary, sim_summary, trades_summary, cfg):
    warnings = []

    trades = sim_summary.get("simulated_trades", 0)
    if trades < cfg["min_trade_sample_warning"]:
        warnings.append(
            f"⚠️ Sample size small: only {trades} simulated trades (warn threshold: {cfg['min_trade_sample_warning']}). "
            f"Calibration conclusions are unreliable."
        )

    hold_ratio = replay_summary.get("hold_ratio", 0.0)
    if hold_ratio > cfg["high_hold_ratio_warning"]:
        warnings.append(
            f"⚠️ HOLD ratio too high: {hold_ratio*100:.0f}% of signals are HOLD "
            f"(warn threshold: {cfg['high_hold_ratio_warning']*100:.0f}%). "
            f"Strategy is too conservative."
        )

    total_pnl = sim_summary.get("total_pnl_pct", 0.0)
    if trades > 0 and total_pnl < 0:
        warnings.append(
            f"⚠️ Negative expectancy: total PnL {total_pnl:+.2f}% across {trades} trades."
        )

    by_side = trades_summary.get("by_side", {})
    if by_side:
        total_side_trades = sum(by_side.values())
        for side, count in by_side.items():
            pct = count / max(total_side_trades, 1)
            if pct > cfg["side_bias_warning_pct"]:
                warnings.append(
                    f"⚠️ Side bias: {pct*100:.0f}% of trades are {side}. "
                    f"Strategy may be overfit to one direction."
                )

    avg_hold = sim_summary.get("avg_hold_candles", 0.0)
    if avg_hold > cfg["max_avg_hold_candles_warning"]:
        warnings.append(
            f"⚠️ Stale positions: avg hold {avg_hold:.0f} candles "
            f"(warn threshold: {cfg['max_avg_hold_candles_warning']}). "
            f"Trades may not be exiting in time."
        )

    exit_reasons = trades_summary.get("by_exit_reason", {})
    sl_count = exit_reasons.get("stop_loss", 0)
    tp_count = exit_reasons.get("take_profit", 0)
    if sl_count > 0 and tp_count > 0 and sl_count > tp_count * 1.5:
        warnings.append(
            f"⚠️ SL/TP imbalance: stop_loss exits ({sl_count}) >> take_profit exits ({tp_count}). "
            f"Risk/reward or SL/TP calibration may need review."
        )

    return warnings


def render_markdown(dashboard, cfg):
    lines = []
    lines.append("# Backtest Report Dashboard")
    lines.append("")
    lines.append(f"**Generated:** {dashboard['generated_at']}")
    lines.append("")

    lines.append("## Executive Summary")
    lines.append("")
    rep = dashboard["replay"]
    sim = dashboard["simulation"]
    summary_lines = [
        f"- Replay signals: {rep.get('signals', 0)}",
        f"- HOLD ratio: {rep.get('hold_ratio', 0)*100:.0f}%",
        f"- Simulated trades: {sim.get('simulated_trades', 0)}",
        f"- Win rate: {sim.get('win_rate', 0)*100:.1f}%",
        f"- Total PnL: {sim.get('total_pnl_pct', 0):+.2f}%",
        f"- Avg PnL: {sim.get('avg_pnl_pct', 0):+.2f}%",
        f"- Avg hold candles: {sim.get('avg_hold_candles', 0):.1f}",
    ]
    if sim.get("avg_mae_pct") is not None:
        summary_lines.append(f"- Avg MAE: {sim['avg_mae_pct']*100:.2f}%")
        summary_lines.append(f"- Avg MFE: {sim['avg_mfe_pct']*100:.2f}%")
    if dashboard.get("replay_sweep_best"):
        best = dashboard["replay_sweep_best"]
        summary_lines.append(
            f"- Best replay variant: {best.get('variant', '?')} (score {best.get('score', 0):+.3f})"
        )
    if dashboard.get("sweep_best"):
        b = dashboard["sweep_best"]
        summary_lines.append(
            f"- Best simulation config: min_conf={b.get('min_confidence', '?')} (score {b.get('score', 0):+.3f})"
        )
    lines.extend(summary_lines)
    lines.append("")

    lines.append("## Diagnostics / Warnings")
    lines.append("")
    if dashboard["warnings"]:
        for w in dashboard["warnings"]:
            lines.append(f"- {w}")
    else:
        lines.append("- No warnings.")
    lines.append("")

    lines.append("## Signal Distribution")
    lines.append("")
    lines.append(f"- Total signals: {rep.get('signals', 0)}")
    by_action = rep.get("by_action", {})
    if by_action:
        lines.append("- By action:")
        for k, v in by_action.items():
            pct = v / max(rep.get("signals", 1), 1) * 100
            lines.append(f"  - {k}: {v} ({pct:.1f}%)")
    by_direction = rep.get("by_direction", {})
    if by_direction:
        lines.append("- By direction:")
        for k, v in by_direction.items():
            lines.append(f"  - {k}: {v}")
    lines.append(f"- Avg confidence: {rep.get('avg_confidence', 0):.3f}")
    lines.append("")

    lines.append("## Simulation Performance")
    lines.append("")
    lines.append(f"- Trades: {sim.get('simulated_trades', 0)}")
    if sim.get("simulated_trades", 0) > 0:
        wr = sim.get("win_rate", 0) * 100
        lines.append(f"- Win/Loss/BE: {sim.get('wins', 0)}W / {sim.get('losses', 0)}L / {sim.get('breakeven', 0)}BE ({wr:.1f}%)")
    lines.append(f"- Total PnL%: {sim.get('total_pnl_pct', 0):+.2f}%")
    lines.append(f"- Avg PnL%: {sim.get('avg_pnl_pct', 0):+.2f}%")
    lines.append(f"- Max PnL%: {sim.get('max_pnl_pct', 0):+.2f}%")
    lines.append(f"- Min PnL%: {sim.get('min_pnl_pct', 0):+.2f}%")
    lines.append(f"- Avg hold candles: {sim.get('avg_hold_candles', 0):.1f}")
    exit_reasons = sim.get("exit_reasons", {})
    if exit_reasons:
        lines.append("- Exit reasons:")
        for k, v in exit_reasons.items():
            lines.append(f"  - {k}: {v}")
    lines.append("")

    trades_summary = dashboard["trades"]
    if trades_summary.get("by_symbol"):
        lines.append("## Symbol Breakdown")
        lines.append("")
        lines.append("| Symbol | Trades | % |")
        lines.append("|--------|--------|---|")
        for sym, count in trades_summary["by_symbol"].items():
            pct = count / max(trades_summary["count"], 1) * 100
            lines.append(f"| {sym} | {count} | {pct:.0f}% |")
        lines.append("")

    if trades_summary.get("by_side"):
        lines.append("## Side Bias")
        lines.append("")
        lines.append("| Side | Trades | % |")
        lines.append("|------|--------|---|")
        for side, count in trades_summary["by_side"].items():
            pct = count / max(trades_summary["count"], 1) * 100
            lines.append(f"| {side} | {count} | {pct:.0f}% |")
        lines.append("")

    if dashboard.get("sweep_top"):
        lines.append("## Parameter Sweep Top 3")
        lines.append("")
        lines.append("| Rank | Min Conf | Trades | Win Rate | Total PnL% | Score |")
        lines.append("|------|----------|--------|----------|-----------|-------|")
        for r in dashboard["sweep_top"]:
            lines.append(
                f"| {r['rank']} | {r['min_confidence']:.2f} | {r['trades']} | "
                f"{r['win_rate']*100:.1f}% | {r['total_pnl_pct']:+.2f}% | {r['score']:+.3f} |"
            )
        lines.append("")

    if dashboard.get("replay_sweep_top"):
        lines.append("## Replay Sweep Top Variants")
        lines.append("")
        lines.append("| Rank | Variant | HOLD% | Trades | Win Rate | Total PnL% | Score |")
        lines.append("|------|---------|-------|--------|----------|-----------|-------|")
        for r in dashboard["replay_sweep_top"]:
            rep_r = r.get("replay", {})
            sim_r = r.get("simulation", {})
            lines.append(
                f"| {r['rank']} | {r['variant']} | {rep_r.get('hold_ratio', 0)*100:.0f}% | "
                f"{sim_r.get('trades', '-')} | {sim_r.get('win_rate', 0)*100:.1f}% | "
                f"{sim_r.get('total_pnl_pct', 0):+.2f}% | {r.get('score', 0):+.3f} |"
            )
        lines.append("")

    lines.append("## Recommendations")
    lines.append("")
    recs = dashboard.get("recommendations", [])
    if recs:
        for r in recs:
            lines.append(f"- {r}")
    else:
        lines.append("- No recommendations generated.")
    lines.append("")
    lines.append("> This report is informational only. It does NOT auto-apply config changes.")
    lines.append("")
    return "\n".join(lines)


def generate_recommendations(dashboard):
    recs = []
    sim = dashboard["simulation"]
    rep = dashboard["replay"]
    trades_summary = dashboard["trades"]
    warnings = dashboard["warnings"]

    if sim.get("simulated_trades", 0) < 10:
        recs.append(
            "Sample size is too small. Run replay on 30-90 days before drawing conclusions about config."
        )

    if rep.get("hold_ratio", 0) > 0.85:
        recs.append(
            "HOLD ratio is very high. Consider if thresholds/weights are too conservative before re-running."
        )

    by_side = trades_summary.get("by_side", {})
    if by_side:
        total = sum(by_side.values())
        for side, count in by_side.items():
            if total > 0 and count / total > 0.85:
                recs.append(
                    f"Strategy is {side}-heavy. Investigate whether opposing side is being suppressed."
                )
                break

    if sim.get("total_pnl_pct", 0) < 0 and sim.get("simulated_trades", 0) >= 10:
        recs.append(
            "Total PnL is negative. Consider running replay sweep to find a better variant before changing live config."
        )

    if not dashboard.get("sweep_top"):
        recs.append(
            "No parameter sweep data available. Run `parameter_sweep.py` for a fuller picture."
        )

    if not dashboard.get("replay_sweep_top"):
        recs.append(
            "No replay sweep data available. Run `replay_parameter_sweep.py` to compare variants."
        )

    if not warnings and sim.get("simulated_trades", 0) >= 10 and sim.get("total_pnl_pct", 0) > 0:
        recs.append("No major issues detected. Continue with current config and collect more data.")

    return recs


def build_dashboard(replay_records, sim_summary, trades_records,
                    sweep_report, replay_sweep_report, cfg):
    rep = summarize_replay(replay_records)
    trades_summary = summarize_trades(trades_records)

    sweep_top = []
    sweep_best = None
    if sweep_report and sweep_report.get("results"):
        sweep_top = sweep_report["results"][:3]
        sweep_best = sweep_top[0] if sweep_top else None

    replay_sweep_top = []
    replay_sweep_best = None
    if replay_sweep_report and replay_sweep_report.get("results"):
        replay_sweep_top = [r for r in replay_sweep_report["results"] if "error" not in r][:3]
        replay_sweep_best = replay_sweep_top[0] if replay_sweep_top else None

    dashboard = {
        "generated_at": datetime.now().isoformat(),
        "replay": rep,
        "simulation": sim_summary or {},
        "trades": trades_summary,
        "warnings": [],
        "recommendations": [],
        "sweep_top": sweep_top,
        "sweep_best": sweep_best,
        "replay_sweep_top": replay_sweep_top,
        "replay_sweep_best": replay_sweep_best,
    }
    dashboard["warnings"] = generate_warnings(rep, sim_summary or {}, trades_summary, cfg)
    dashboard["recommendations"] = generate_recommendations(dashboard)
    return dashboard


def main():
    parser = argparse.ArgumentParser(description="Generate backtest dashboard")
    parser.add_argument("--replay-input", default="logs/replay_signals.jsonl")
    parser.add_argument("--sim-summary", default="logs/simulation_summary.json")
    parser.add_argument("--trades-input", default="logs/simulated_trades.jsonl")
    parser.add_argument("--sweep-report", default="logs/parameter_sweep_report.json")
    parser.add_argument("--replay-sweep-report", default="logs/replay_sweep_report.json")
    parser.add_argument("--md-out", default="reports/backtest-dashboard.md")
    parser.add_argument("--json-out", default="reports/backtest-dashboard.json")
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent

    def resolve(p):
        path = Path(p)
        if not path.is_absolute():
            path = project_root / path
        return path

    replay_records = load_jsonl(resolve(args.replay_input))
    sim_summary = load_json(resolve(args.sim_summary))
    trades_records = load_jsonl(resolve(args.trades_input))
    sweep_report = load_json(resolve(args.sweep_report))
    replay_sweep_report = load_json(resolve(args.replay_sweep_report))

    print(f"Loaded {len(replay_records)} replay signals")
    if sim_summary:
        print(f"Loaded simulation summary: {sim_summary.get('simulated_trades', 0)} trades")
    if trades_records:
        print(f"Loaded {len(trades_records)} simulated trades")
    if sweep_report:
        print(f"Loaded parameter sweep: {len(sweep_report.get('results', []))} configs")
    if replay_sweep_report:
        print(f"Loaded replay sweep: {len(replay_sweep_report.get('results', []))} variants")

    dashboard = build_dashboard(
        replay_records, sim_summary, trades_records,
        sweep_report, replay_sweep_report, DEFAULT_CONFIG,
    )

    md_path = resolve(args.md_out)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_markdown(dashboard, DEFAULT_CONFIG), encoding="utf-8")
    print(f"Wrote Markdown to {md_path}")

    json_path = resolve(args.json_out)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(dashboard, f, indent=2, ensure_ascii=True)
    print(f"Wrote JSON to {json_path}")


if __name__ == "__main__":
    main()

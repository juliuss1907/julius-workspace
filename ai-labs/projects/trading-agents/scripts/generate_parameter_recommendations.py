#!/usr/bin/env python3
"""Adaptive Parameter Recommendations — Phase 7A.

Consumes the backtest dashboard, parameter sweep, and replay sweep outputs
and produces structured, human-readable parameter recommendations.

IMPORTANT:
  - Recommendations are advisory only. They do NOT auto-apply any config.
  - The script reads `config/default_params.yaml` only to surface current
    values and the canonical `config_path` strings to use in a manual edit.
  - Every recommendation is tagged `apply_status: manual_review_required`.

Inputs (auto-resolved relative to project root, all optional):
  reports/backtest-dashboard.json
  logs/parameter_sweep_report.json
  logs/replay_sweep_report.json
  config/default_params.yaml

Outputs:
  reports/parameter-recommendations.md
  reports/parameter-recommendations.json

Recommendation record:
  {
    "id": "R001",
    "priority": "high|medium|low",
    "category": "data_quality|thresholds|exits|side_bias|risk|workflow",
    "finding": "...",
    "evidence": "...",
    "recommendation": "...",
    "config_path": "risk_manager.min_signal_confidence" | null,
    "current_value": ...,
    "suggested_value": ...,
    "apply_status": "manual_review_required",
  }
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}
APPLY_STATUS = "manual_review_required"

DEFAULT_RULES = {
    "min_trade_sample": 10,
    "side_bias_pct": 0.80,
    "stale_hold_candles": 72,
    "stale_hold_min_trades": 3,
    "sweep_tie_pct": 0.05,
    "negative_pnl_min_trades": 5,
    "high_win_rate": 0.80,
    "high_win_rate_min_trades": 5,
}


def load_json(path: Path):
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def load_yaml(path: Path):
    if not path.exists():
        return None
    try:
        import yaml
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def get_config_value(cfg: dict, dotted_path: str):
    if not cfg:
        return None
    cur = cfg
    for part in dotted_path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def _trades_by_side(trades_summary: dict) -> dict:
    return (trades_summary or {}).get("by_side", {}) or {}


def _dominant_side(trades_summary: dict):
    by_side = _trades_by_side(trades_summary)
    if not by_side:
        return None, 0, 0
    total = sum(by_side.values())
    top = max(by_side.items(), key=lambda kv: kv[1])
    return top[0], top[1], total


def _pct(value, total):
    if total <= 0:
        return 0.0
    return value / total


def _new_id(seq: list) -> str:
    n = len(seq) + 1
    return f"R{n:03d}"


def generate_recommendations(
    dashboard: dict,
    sweep_report: dict,
    replay_sweep_report: dict,
    default_config: dict,
    rules: dict,
) -> list:
    """Build list of recommendation records."""
    recs = []

    sim = (dashboard or {}).get("simulation") or {}
    replay = (dashboard or {}).get("replay") or {}
    trades_summary = (dashboard or {}).get("trades") or {}
    warnings = (dashboard or {}).get("warnings") or []
    trades = sim.get("simulated_trades", 0) or 0
    total_pnl = sim.get("total_pnl_pct", 0.0) or 0.0
    win_rate = sim.get("win_rate", 0.0) or 0.0
    avg_hold = sim.get("avg_hold_candles", 0.0) or 0.0

    min_trade_sample = rules["min_trade_sample"]
    side_bias_pct = rules["side_bias_pct"]
    stale_hold_candles = rules["stale_hold_candles"]
    stale_hold_min_trades = rules["stale_hold_min_trades"]
    sweep_tie_pct = rules["sweep_tie_pct"]
    negative_pnl_min_trades = rules["negative_pnl_min_trades"]
    high_win_rate = rules["high_win_rate"]
    high_win_rate_min_trades = rules["high_win_rate_min_trades"]

    current_min_conf = get_config_value(
        default_config, "simulation.min_confidence"
    )

    dashboard_present = bool(dashboard) and bool(dashboard.get("simulation"))

    if dashboard_present and trades < min_trade_sample:
        recs.append({
            "id": _new_id(recs),
            "priority": "high",
            "category": "data_quality",
            "finding": (
                f"Sample size too small: only {trades} simulated trades in the backtest. "
                f"Calibration conclusions are unreliable below {min_trade_sample} trades."
            ),
            "evidence": f"simulation.simulated_trades={trades}",
            "recommendation": (
                "Do not apply config changes yet. Run replay on 30-90 days "
                "of OHLCV before re-running the parameter sweep."
            ),
            "config_path": None,
            "current_value": None,
            "suggested_value": None,
            "apply_status": APPLY_STATUS,
        })

    side, side_count, side_total = _dominant_side(trades_summary)
    if side and side_total >= 5 and _pct(side_count, side_total) > side_bias_pct:
        recs.append({
            "id": _new_id(recs),
            "priority": "high",
            "category": "side_bias",
            "finding": (
                f"{_pct(side_count, side_total)*100:.0f}% of simulated trades "
                f"are {side}. Strategy is heavily one-sided."
            ),
            "evidence": (
                f"trades.by_side={trades_summary.get('by_side', {})}, "
                f"replay.by_direction={replay.get('by_direction', {})}"
            ),
            "recommendation": (
                "Investigate whether the opposite side is being suppressed by "
                "thresholds, weights, or funding/derivatives gates before changing "
                "live config. Check technical/news/derivatives analyst weights."
            ),
            "config_path": "analyst_weights.full.derivatives",
            "current_value": get_config_value(
                default_config, "analyst_weights.full.derivatives"
            ),
            "suggested_value": "review only — do not change without root-cause analysis",
            "apply_status": APPLY_STATUS,
        })

    if trades >= stale_hold_min_trades and avg_hold > stale_hold_candles:
        recs.append({
            "id": _new_id(recs),
            "priority": "medium",
            "category": "exits",
            "finding": (
                f"Average hold {avg_hold:.0f} candles exceeds the {stale_hold_candles}-candle "
                f"warning threshold. Positions are not exiting in time."
            ),
            "evidence": (
                f"simulation.avg_hold_candles={avg_hold}, "
                f"exit_reasons={sim.get('exit_reasons', {})}"
            ),
            "recommendation": (
                "Review SL/TP and max-hold logic. Consider lowering "
                "`simulation.max_hold_candles` or enabling "
                "`simulation.use_sl_tp` if not already on."
            ),
            "config_path": "simulation.max_hold_candles",
            "current_value": get_config_value(
                default_config, "simulation.max_hold_candles"
            ),
            "suggested_value": "review; typical target 24-48 for 1h timeframe",
            "apply_status": APPLY_STATUS,
        })

    if trades >= negative_pnl_min_trades and total_pnl < 0:
        recs.append({
            "id": _new_id(recs),
            "priority": "high",
            "category": "thresholds",
            "finding": (
                f"Total PnL {total_pnl:+.2f}% across {trades} simulated trades. "
                f"Negative expectancy at current config."
            ),
            "evidence": (
                f"simulation.total_pnl_pct={total_pnl}, "
                f"simulation.win_rate={win_rate*100:.1f}%, trades={trades}"
            ),
            "recommendation": (
                "Do not change live config on a single negative run. "
                "Run `replay_parameter_sweep.py` to compare variants and "
                "look for consistent losers across the top 3 before tuning."
            ),
            "config_path": None,
            "current_value": None,
            "suggested_value": None,
            "apply_status": APPLY_STATUS,
        })

    if (
        trades >= high_win_rate_min_trades
        and win_rate >= high_win_rate
        and trades < min_trade_sample
    ):
        recs.append({
            "id": _new_id(recs),
            "priority": "medium",
            "category": "data_quality",
            "finding": (
                f"Win rate {win_rate*100:.1f}% looks strong, but the sample "
                f"({trades} trades) is too small to trust."
            ),
            "evidence": f"simulation.win_rate={win_rate}, trades={trades}",
            "recommendation": (
                "Treat high win rate as noise until at least "
                f"{min_trade_sample} trades are collected."
            ),
            "config_path": None,
            "current_value": None,
            "suggested_value": None,
            "apply_status": APPLY_STATUS,
        })

    sweep_results = (sweep_report or {}).get("results") or []
    if sweep_results:
        best = sweep_results[0]
        best_score = best.get("score", 0.0)
        tie_window = best_score * sweep_tie_pct
        tied = [
            r for r in sweep_results
            if abs(r.get("score", 0.0) - best_score) <= tie_window
        ]
        unique_min_conf = {round(r.get("min_confidence", 0.0), 4) for r in tied}
        if len(tied) >= 3 and len(unique_min_conf) >= 3:
            recs.append({
                "id": _new_id(recs),
                "priority": "low",
                "category": "data_quality",
                "finding": (
                    f"Top {len(tied)} parameter sweep configs are within "
                    f"{sweep_tie_pct*100:.0f}% of each other on score "
                    f"({best_score:+.3f}). Sweep is not differentiating."
                ),
                "evidence": (
                    f"sweep_top_scores={[r.get('score') for r in tied]}, "
                    f"min_confidences={sorted(unique_min_conf)}"
                ),
                "recommendation": (
                    "Widen the sweep grid (e.g. include fee_pct, slippage_pct, "
                    "or stop_loss_pct) before trusting ranking."
                ),
                "config_path": "parameter_sweep.min_confidence_values",
                "current_value": get_config_value(
                    default_config, "parameter_sweep.min_confidence_values"
                ),
                "suggested_value": "widen grid",
                "apply_status": APPLY_STATUS,
            })

        if best.get("trades", 0) < min_trade_sample:
            recs.append({
                "id": _new_id(recs),
                "priority": "medium",
                "category": "data_quality",
                "finding": (
                    f"Best sweep config only produced {best.get('trades', 0)} "
                    f"trades — ranking is unreliable."
                ),
                "evidence": (
                    f"sweep_best.trades={best.get('trades')}, "
                    f"sweep_best.min_confidence={best.get('min_confidence')}"
                ),
                "recommendation": (
                    "Lower `simulation.min_confidence` temporarily for the sweep, "
                    "or collect more replay data, before changing live config."
                ),
                "config_path": "simulation.min_confidence",
                "current_value": current_min_conf,
                "suggested_value": (
                    f"keep current {current_min_conf} for live; "
                    "sweep with a lower value for exploration"
                ),
                "apply_status": APPLY_STATUS,
            })

    replay_results = (replay_sweep_report or {}).get("results") or []
    valid_replay_results = [r for r in replay_results if "error" not in r]
    if valid_replay_results:
        best = valid_replay_results[0]
        if best.get("simulation", {}).get("total_pnl_pct", 0.0) < 0:
            recs.append({
                "id": _new_id(recs),
                "priority": "high",
                "category": "thresholds",
                "finding": (
                    f"Best replay variant `{best.get('variant')}` has negative "
                    f"total PnL ({best.get('simulation', {}).get('total_pnl_pct', 0):+.2f}%) "
                    f"despite the highest score."
                ),
                "evidence": (
                    f"replay_sweep_best={best.get('variant')}, "
                    f"pnl={best.get('simulation', {}).get('total_pnl_pct')}, "
                    f"trades={best.get('simulation', {}).get('trades')}, "
                    f"score={best.get('score')}"
                ),
                "recommendation": (
                    "Do NOT apply this variant. The score is dominated by "
                    "win_rate/avg_pnl on a tiny sample. Keep current live config "
                    "and increase sample size first."
                ),
                "config_path": None,
                "current_value": None,
                "suggested_value": None,
                "apply_status": APPLY_STATUS,
            })

    for w in warnings:
        text = w.lower()
        if "negative" in text and not any(
            r["category"] == "thresholds" for r in recs
        ):
            recs.append({
                "id": _new_id(recs),
                "priority": "medium",
                "category": "workflow",
                "finding": "Backtest dashboard flagged negative expectancy.",
                "evidence": w,
                "recommendation": (
                    "Cross-check with `analyze_positions.py` for live PnL and "
                    "make sure any tuning is hypothesis-driven."
                ),
                "config_path": None,
                "current_value": None,
                "suggested_value": None,
                "apply_status": APPLY_STATUS,
            })
        if "imbalance" in text:
            recs.append({
                "id": _new_id(recs),
                "priority": "medium",
                "category": "exits",
                "finding": "Stop-loss exits are dominating take-profit exits.",
                "evidence": w,
                "recommendation": (
                    "Review `stop_loss.atr_multiplier` and "
                    "`take_profit.risk_reward_ratio`. Consider lowering SL "
                    "tightness or widening TP."
                ),
                "config_path": "stop_loss.atr_multiplier",
                "current_value": get_config_value(
                    default_config, "stop_loss.atr_multiplier"
                ),
                "suggested_value": "review only",
                "apply_status": APPLY_STATUS,
            })
            break

    if not recs:
        recs.append({
            "id": _new_id(recs),
            "priority": "low",
            "category": "workflow",
            "finding": "No parameter issues detected by current rules.",
            "evidence": "All rule preconditions were unmet or false.",
            "recommendation": (
                "Continue collecting data with the current config. Re-run this "
                "script after each weekly backtest to confirm stability."
            ),
            "config_path": None,
            "current_value": None,
            "suggested_value": None,
            "apply_status": APPLY_STATUS,
        })

    return recs


def sort_recommendations(recs: list) -> list:
    """Sort by priority desc, then by id."""
    return sorted(
        recs,
        key=lambda r: (-PRIORITY_RANK.get(r.get("priority", "low"), 0), r.get("id", "")),
    )


def render_markdown(recs: list, dashboard: dict, rules: dict) -> str:
    lines = []
    lines.append("# Adaptive Parameter Recommendations")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().isoformat()}")
    sim = (dashboard or {}).get("simulation") or {}
    lines.append(
        f"**Trades analyzed:** {sim.get('simulated_trades', 0)} "
        f"(win rate {sim.get('win_rate', 0)*100:.1f}%, "
        f"PnL {sim.get('total_pnl_pct', 0):+.2f}%)"
    )
    lines.append("")
    lines.append("> This report is advisory only. It does NOT auto-apply any config change.")
    lines.append("> Every recommendation requires manual review and a deliberate edit.")
    lines.append("")

    counts = {"high": 0, "medium": 0, "low": 0}
    for r in recs:
        counts[r.get("priority", "low")] = counts.get(r.get("priority", "low"), 0) + 1

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- High: {counts['high']}")
    lines.append(f"- Medium: {counts['medium']}")
    lines.append(f"- Low: {counts['low']}")
    lines.append(f"- Total: {len(recs)}")
    lines.append("")
    lines.append("## Recommendations")
    lines.append("")
    lines.append("| # | Priority | Category | Finding | Config | Suggested |")
    lines.append("|---|----------|----------|---------|--------|-----------|")
    for r in recs:
        finding = r.get("finding", "").replace("|", "\\|")
        cfg_path = r.get("config_path") or "—"
        suggested = str(r.get("suggested_value") or "—").replace("|", "\\|")
        if len(suggested) > 60:
            suggested = suggested[:57] + "..."
        lines.append(
            f"| {r.get('id')} | {r.get('priority')} | {r.get('category')} | "
            f"{finding} | `{cfg_path}` | {suggested} |"
        )
    lines.append("")

    for r in recs:
        lines.append(f"### {r.get('id')} — {r.get('priority').upper()} — {r.get('category')}")
        lines.append("")
        lines.append(f"**Finding:** {r.get('finding')}")
        lines.append("")
        lines.append(f"**Evidence:** {r.get('evidence')}")
        lines.append("")
        lines.append(f"**Recommendation:** {r.get('recommendation')}")
        lines.append("")
        lines.append(f"**Config path:** `{r.get('config_path') or '—'}`")
        lines.append(f"**Current value:** `{r.get('current_value')}`")
        lines.append(f"**Suggested value:** `{r.get('suggested_value')}`")
        lines.append(f"**Apply status:** `{r.get('apply_status')}`")
        lines.append("")

    return "\n".join(lines)


def build_report(
    dashboard: dict,
    sweep_report: dict,
    replay_sweep_report: dict,
    default_config: dict,
    rules: dict,
) -> dict:
    recs = generate_recommendations(
        dashboard, sweep_report, replay_sweep_report, default_config, rules,
    )
    recs = sort_recommendations(recs)
    counts = {"high": 0, "medium": 0, "low": 0}
    for r in recs:
        counts[r.get("priority", "low")] = counts.get(r.get("priority", "low"), 0) + 1
    return {
        "generated_at": datetime.now().isoformat(),
        "rules": rules,
        "summary": {
            "total": len(recs),
            "high": counts["high"],
            "medium": counts["medium"],
            "low": counts["low"],
        },
        "trades_analyzed": (dashboard or {}).get("simulation", {}).get("simulated_trades", 0),
        "recommendations": recs,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate adaptive parameter recommendations")
    parser.add_argument("--dashboard", default="reports/backtest-dashboard.json")
    parser.add_argument("--sweep", default="logs/parameter_sweep_report.json")
    parser.add_argument("--replay-sweep", default="logs/replay_sweep_report.json")
    parser.add_argument("--config", default="config/default_params.yaml")
    parser.add_argument("--md-out", default="reports/parameter-recommendations.md")
    parser.add_argument("--json-out", default="reports/parameter-recommendations.json")
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent

    def resolve(p):
        path = Path(p)
        if not path.is_absolute():
            path = project_root / path
        return path

    dashboard = load_json(resolve(args.dashboard)) or {}
    sweep_report = load_json(resolve(args.sweep)) or {}
    replay_sweep_report = load_json(resolve(args.replay_sweep)) or {}
    default_config = load_yaml(resolve(args.config)) or {}

    sim = dashboard.get("simulation") or {}
    print(f"Trades analyzed: {sim.get('simulated_trades', 0)}")
    print(f"Win rate: {sim.get('win_rate', 0)*100:.1f}%")
    print(f"Total PnL: {sim.get('total_pnl_pct', 0):+.2f}%")
    if sweep_report.get("results"):
        print(f"Parameter sweep configs: {len(sweep_report['results'])}")
    if replay_sweep_report.get("results"):
        valid = [r for r in replay_sweep_report["results"] if "error" not in r]
        print(f"Replay sweep variants: {len(valid)} valid")

    report = build_report(
        dashboard, sweep_report, replay_sweep_report, default_config, DEFAULT_RULES,
    )

    md_path = resolve(args.md_out)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_markdown(report["recommendations"], dashboard, DEFAULT_RULES), encoding="utf-8")
    print(f"Wrote Markdown to {md_path}")

    json_path = resolve(args.json_out)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=True)
    print(f"Wrote JSON to {json_path}")
    print(
        f"Summary: high={report['summary']['high']} "
        f"medium={report['summary']['medium']} "
        f"low={report['summary']['low']}"
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Dynamic Watchlist Updater — Phase 8B.

Reads the latest screening report (Phase 8A) and produces a proposal
for a dynamic watchlist. Always marks the result as
`manual_review_required` and `enabled_for_runtime: false`.

This script does NOT:
  - Mutate `config/default_params.yaml` runtime watchlist
  - Auto-promote any symbol to live runtime
  - Place orders

It only writes:
  watchlist/dynamic-watchlist.json
  watchlist/dynamic-watchlist.md

Usage:
  ./venv/bin/python scripts/update_dynamic_watchlist.py
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils import config as cfg_loader
from utils import get_logger


logger = get_logger(__name__)


RATING_RANK = {
    "strong_candidate": 4,
    "candidate": 3,
    "watch_only": 2,
    "avoid": 1,
}


def _load_json(path: Path):
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"  ! failed to load {path}: {e}")
        return None


def _resolve(path_str: str, base: Path) -> Path:
    p = Path(path_str)
    if not p.is_absolute():
        p = base / p
    return p


def _relative_or_absolute(path: Path, base: Path) -> str:
    """Return a path string; relative if under base, else absolute."""
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def _load_screening(report_path: Path) -> dict:
    return _load_json(report_path) or {}


def _normalize_candidates(screening: dict) -> list:
    """Extract normalized candidate list from screening report."""
    cands = screening.get("candidates") or []
    normalized = []
    for c in cands:
        normalized.append({
            "symbol": c.get("symbol", ""),
            "rank": c.get("rank", 0),
            "score": float(c.get("score", 0.0) or 0.0),
            "rating": c.get("rating", "avoid"),
            "recommended_action": c.get("recommended_action", "skip"),
            "liquidity_score": c.get("liquidity_score", 0.0),
            "volatility_score": c.get("volatility_score", 0.0),
            "technical_score": c.get("technical_score", 0.0),
            "news_score": c.get("news_score", 50.0),
            "risk_score": c.get("risk_score", 100.0),
            "reasons": c.get("reasons", []) or [],
            "warnings": c.get("warnings", []) or [],
        })
    return normalized


def _filter_candidates(
    candidates: list,
    rules: dict,
    base_symbols: list,
    allowed_symbols: list,
) -> tuple:
    """Apply selection rules. Returns (selected, excluded_with_reasons)."""
    min_score = rules.get("min_score", 60)
    min_rating = rules.get("min_rating", "candidate")
    exclude_avoid = rules.get("exclude_avoid_rating", True)
    preserve_base = rules.get("preserve_base_watchlist", True)
    max_symbols = rules.get("max_symbols", 6)
    min_rating_rank = RATING_RANK.get(min_rating, 0)

    allowed_set = set(allowed_symbols) if allowed_symbols else None
    base_set = set(base_symbols) if base_symbols else set()

    pool = list(candidates)
    pool.sort(key=lambda c: (c.get("rank", 9999), -c.get("score", 0.0)))

    selected = []
    excluded = []
    selected_set = set()

    def _add(symbol, cand):
        if symbol in selected_set:
            return
        selected.append({
            "symbol": symbol,
            "score": cand.get("score", 0.0),
            "rating": cand.get("rating", "avoid"),
            "rank": cand.get("rank", 0),
            "recommended_action": cand.get("recommended_action", "skip"),
            "reasons": cand.get("reasons", []) or [],
            "warnings": cand.get("warnings", []) or [],
            "from_base": symbol in base_set,
        })
        selected_set.add(symbol)

    by_symbol = {c["symbol"]: c for c in pool if c.get("symbol")}

    if preserve_base:
        for sym in base_symbols:
            if sym in by_symbol:
                _add(sym, by_symbol[sym])
            else:
                _add(sym, {
                    "symbol": sym,
                    "score": 0.0,
                    "rating": "base_preserved",
                    "rank": 0,
                    "recommended_action": "preserve",
                    "reasons": ["base_watchlist"],
                    "warnings": [],
                })

    for cand in pool:
        sym = cand.get("symbol", "")
        if not sym or sym in selected_set:
            continue
        if allowed_set is not None and sym not in allowed_set:
            excluded.append({"symbol": sym, "reason": "not_in_allowlist"})
            continue
        if exclude_avoid and cand.get("rating") == "avoid":
            excluded.append({"symbol": sym, "reason": "rating_is_avoid"})
            continue
        if cand.get("score", 0.0) < min_score:
            excluded.append({"symbol": sym, "reason": f"score_below_{min_score}"})
            continue
        if RATING_RANK.get(cand.get("rating", "avoid"), 0) < min_rating_rank:
            excluded.append({"symbol": sym, "reason": f"rating_below_{min_rating}"})
            continue
        if len(selected) >= max_symbols:
            excluded.append({"symbol": sym, "reason": "max_symbols_reached"})
            continue
        _add(sym, cand)

    for cand in pool:
        sym = cand.get("symbol", "")
        if not sym or sym in selected_set:
            continue
        already_excluded = any(e["symbol"] == sym for e in excluded)
        if not already_excluded:
            excluded.append({"symbol": sym, "reason": "not_selected"})

    return selected, excluded


def _build_proposal(
    screening: dict,
    selected: list,
    excluded: list,
    rules: dict,
    base_symbols: list,
    source_report: str,
) -> dict:
    now = datetime.now().isoformat()
    return {
        "generated_at": now,
        "source_report": source_report,
        "status": "manual_review_required",
        "enabled_for_runtime": False,
        "enabled_for_runtime_reason": (
            "set enabled_for_runtime: true and config "
            "dynamic_watchlist.enabled: true only after manual review"
        ),
        "base_symbols": base_symbols,
        "selected_symbols": [s["symbol"] for s in selected],
        "selection": selected,
        "excluded": excluded,
        "selection_rules": rules,
        "source_metrics": {
            "symbols_scanned": screening.get("symbols_scanned", 0),
            "min_score_threshold": screening.get("min_score", rules.get("min_score", 60)),
            "top_n": screening.get("top_n", 0),
        },
    }


def _render_markdown(proposal: dict) -> str:
    lines = []
    lines.append("# Dynamic Watchlist Proposal")
    lines.append("")
    lines.append(f"**Generated:** {proposal['generated_at']}")
    lines.append(f"**Source:** `{proposal['source_report']}`")
    lines.append(f"**Status:** `{proposal['status']}`")
    lines.append(f"**Enabled for runtime:** `{proposal['enabled_for_runtime']}`")
    lines.append("")
    lines.append("> This is a PROPOSAL. It is NOT active for runtime.")
    lines.append("> Set `enabled_for_runtime: true` and config `dynamic_watchlist.enabled: true`")
    lines.append("> only after manual review of the selection below.")
    lines.append("")

    lines.append("## Selected Symbols")
    lines.append("")
    if not proposal["selected_symbols"]:
        lines.append("- (none)")
    else:
        for s in proposal["selection"]:
            tag = " (base)" if s.get("from_base") else ""
            lines.append(
                f"- {s['symbol']}{tag} — score {s.get('score', 0):.1f}, "
                f"rating {s.get('rating', '?')}"
            )
    lines.append("")

    rules = proposal["selection_rules"]
    lines.append("## Selection Rules")
    lines.append("")
    lines.append(f"- max_symbols: {rules.get('max_symbols', 6)}")
    lines.append(f"- min_score: {rules.get('min_score', 60)}")
    lines.append(f"- min_rating: {rules.get('min_rating', 'candidate')}")
    lines.append(f"- preserve_base_watchlist: {rules.get('preserve_base_watchlist', True)}")
    lines.append(f"- exclude_avoid_rating: {rules.get('exclude_avoid_rating', True)}")
    lines.append(f"- require_manual_approval: {rules.get('require_manual_approval', True)}")
    lines.append("")

    lines.append("## Excluded Symbols")
    lines.append("")
    if not proposal["excluded"]:
        lines.append("- (none)")
    else:
        for e in proposal["excluded"]:
            lines.append(f"- {e['symbol']}: {e['reason']}")
    lines.append("")

    metrics = proposal.get("source_metrics", {})
    if metrics:
        lines.append("## Source Screening Metrics")
        lines.append("")
        lines.append(f"- Symbols scanned: {metrics.get('symbols_scanned', 0)}")
        lines.append(f"- Screening min score: {metrics.get('min_score_threshold', '?')}")
        lines.append("")

    lines.append("## Manual Review Checklist")
    lines.append("")
    lines.append("- [ ] Read the screening report")
    lines.append("- [ ] Check each selected symbol's score and rating")
    lines.append("- [ ] Confirm allowlist is still appropriate")
    lines.append("- [ ] Confirm base watchlist is still appropriate")
    lines.append("- [ ] Update `watchlist/dynamic-watchlist.json` with `enabled_for_runtime: true`")
    lines.append("- [ ] Set config `dynamic_watchlist.enabled: true`")
    lines.append("- [ ] Re-run `scripts/run_paper_trading.py` and monitor first cycle")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Build dynamic watchlist proposal from screening report"
    )
    parser.add_argument("--source", default=None,
                        help="Path to screening JSON (default from config)")
    parser.add_argument("--output-json", default=None)
    parser.add_argument("--output-md", default=None)
    parser.add_argument("--max-symbols", type=int, default=None)
    parser.add_argument("--min-score", type=float, default=None)
    parser.add_argument("--min-rating", default=None,
                        help="strong_candidate | candidate | watch_only")
    parser.add_argument("--preserve-base", dest="preserve_base", action="store_true",
                        default=None)
    parser.add_argument("--no-preserve-base", dest="preserve_base", action="store_false")
    parser.add_argument("--allowed-symbols", nargs="+", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    default_config = cfg_loader.load_default_params()
    dw_cfg = dict(default_config.get("dynamic_watchlist", {}) or {})

    source_str = args.source or dw_cfg.get("source_report", "reports/screening/latest-screening.json")
    out_json_str = args.output_json or dw_cfg.get("output_json", "watchlist/dynamic-watchlist.json")
    out_md_str = args.output_md or dw_cfg.get("output_md", "watchlist/dynamic-watchlist.md")

    source_path = _resolve(source_str, project_root)
    out_json = _resolve(out_json_str, project_root)
    out_md = _resolve(out_md_str, project_root)

    if not source_path.exists():
        print(f"Error: screening report not found at {source_path}")
        print("Run `scripts/run_screening.py` first.")
        return 2

    screening = _load_screening(source_path)
    candidates = _normalize_candidates(screening)

    if not candidates:
        print(f"Error: screening report has no candidates")
        return 2

    rules = {
        "max_symbols": args.max_symbols if args.max_symbols is not None else dw_cfg.get("max_symbols", 6),
        "min_score": args.min_score if args.min_score is not None else dw_cfg.get("min_score", 60),
        "min_rating": args.min_rating if args.min_rating is not None else dw_cfg.get("min_rating", "candidate"),
        "preserve_base_watchlist": (
            args.preserve_base
            if args.preserve_base is not None
            else dw_cfg.get("preserve_base_watchlist", True)
        ),
        "exclude_avoid_rating": dw_cfg.get("exclude_avoid_rating", True),
        "require_manual_approval": dw_cfg.get("require_manual_approval", True),
    }
    base_symbols = dw_cfg.get("base_symbols", []) or []
    allowed_symbols = args.allowed_symbols or dw_cfg.get("allowed_symbols", []) or []

    selected, excluded = _filter_candidates(
        candidates, rules, base_symbols, allowed_symbols,
    )

    proposal = _build_proposal(
        screening=screening,
        selected=selected,
        excluded=excluded,
        rules=rules,
        base_symbols=base_symbols,
        source_report=_relative_or_absolute(source_path, project_root),
    )

    print(f"Loaded {len(candidates)} candidates from {source_path}")
    print(f"Selected {len(proposal['selected_symbols'])}: {proposal['selected_symbols']}")
    print(f"Excluded {len(excluded)}")
    print(f"Status: {proposal['status']}")
    print(f"Enabled for runtime: {proposal['enabled_for_runtime']}")

    if args.dry_run:
        print("\n[DRY-RUN] would write:")
        print(f"  {out_json}")
        print(f"  {out_md}")
        return 0

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(proposal, f, indent=2, ensure_ascii=True)
    out_md.write_text(_render_markdown(proposal), encoding="utf-8")
    print(f"\nWrote {out_json}")
    print(f"Wrote {out_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

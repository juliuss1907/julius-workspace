#!/usr/bin/env python3
"""
Screening Runner — Phase 8A CLI.

Fetches OHLCV for a list of candidate symbols, runs the ScreeningAgent,
and produces a ranked candidate list (JSON + Markdown).

This script does NOT:
  - Mutate the live watchlist
  - Place orders
  - Modify any config

It only writes:
  reports/screening/latest-screening.json
  reports/screening/latest-screening.md
  reports/screening/<date>-screening.json
  reports/screening/<date>-screening.md

Usage:
  ./venv/bin/python scripts/run_screening.py \
    --symbols BTCUSDT ETHUSDT SOLUSDT BNBUSDT HYPEUSDT ZECUSDT
"""
import argparse
import asyncio
import json
import sys
from datetime import datetime, date
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils import config as cfg_loader
from utils import get_logger
from agents.screening_agent import ScreeningAgent, CandidateMetrics
from dataflows.data_manager import DataManager
from dataflows.binance_client import BinanceClient


logger = get_logger(__name__)


def _screening_config() -> dict:
    default_config = cfg_loader.load_default_params()
    return default_config.get("screening", {}) or {}


def _synthetic_ohlcv(symbol: str, last_close: float, n: int = 100) -> list:
    """Build a flat synthetic OHLCV series. Used for offline / fail-safe runs."""
    candles = []
    import math
    for i in range(n):
        t = i - n + 1
        noise = math.sin(i / 7.0) * 0.005
        close = last_close * (1.0 + noise + i * 0.0002)
        candles.append({
            "timestamp": int(datetime.now().timestamp()) + t * 3600,
            "open": close * 0.999,
            "high": close * 1.005,
            "low": close * 0.995,
            "close": close,
            "volume": 1000.0,
            "quote_volume": 1000.0 * close,
            "trades": 100,
        })
    return candles


def _synthetic_ticker(symbol: str, last_close: float) -> dict:
    """Build a minimal synthetic ticker."""
    return {
        "symbol": symbol,
        "last_price": last_close,
        "quote_volume": 50_000_000 if "BTC" in symbol else 20_000_000,
        "price_change_pct": 1.0,
    }


async def _fetch_symbol_data(
    binance: BinanceClient, symbol: str, limit: int
) -> tuple:
    """Return (ohlcv_list, ticker_dict). May return empty on failure."""
    ohlcv = []
    ticker = None
    try:
        ohlcv = await binance.fetch_ohlcv(symbol, "1h", limit=limit)
    except Exception as e:
        print(f"  ! {symbol}: OHLCV fetch failed: {e}")
    try:
        ticker = await binance.fetch_ticker(symbol)
    except Exception as e:
        print(f"  ! {symbol}: ticker fetch failed: {e}")
    return ohlcv, ticker


async def _gather_ohlcv(symbols: list, limit: int) -> tuple:
    """Fetch OHLCV + ticker for all symbols. Returns (ohlcv_map, ticker_map, errors)."""
    binance = BinanceClient(environment="production")
    ohlcv_map = {}
    ticker_map = {}
    errors = {}

    try:
        for sym in symbols:
            ohlcv, ticker = await _fetch_symbol_data(binance, sym, limit)
            ohlcv_map[sym] = ohlcv
            if ticker:
                ticker_map[sym] = ticker
            if not ohlcv:
                errors[sym] = "no_ohlcv"
    finally:
        await binance.close()

    return ohlcv_map, ticker_map, errors


def _build_synthetic_dataset(symbols: list) -> tuple:
    """Build a fully synthetic dataset for offline / dry-run screening."""
    ohlcv_map = {}
    ticker_map = {}
    fake_prices = {
        "BTCUSDT": 65000.0,
        "ETHUSDT": 3500.0,
        "SOLUSDT": 150.0,
        "BNBUSDT": 600.0,
        "HYPEUSDT": 25.0,
        "ZECUSDT": 30.0,
        "XRPUSDT": 0.55,
        "ADAUSDT": 0.45,
        "AVAXUSDT": 35.0,
        "DOGEUSDT": 0.15,
        "LINKUSDT": 18.0,
        "SUIUSDT": 1.5,
        "APTUSDT": 9.0,
    }
    for sym in symbols:
        price = fake_prices.get(sym, 100.0)
        ohlcv_map[sym] = _synthetic_ohlcv(sym, price, n=120)
        ticker_map[sym] = _synthetic_ticker(sym, price)
    return ohlcv_map, ticker_map


def _render_markdown(report: dict, top_n: int) -> str:
    lines = []
    lines.append("# Screening Report")
    lines.append("")
    lines.append(f"**Generated:** {report['generated_at']}")
    lines.append(f"**Symbols scanned:** {len(report['candidates'])}")
    lines.append("")
    lines.append("> Advisory only. Does NOT auto-apply any config or watchlist change.")
    lines.append("")

    counts = {"strong_candidate": 0, "candidate": 0, "watch_only": 0, "avoid": 0}
    for c in report["candidates"]:
        counts[c["rating"]] = counts.get(c["rating"], 0) + 1

    lines.append("## Distribution")
    lines.append("")
    lines.append(f"- strong_candidate: {counts.get('strong_candidate', 0)}")
    lines.append(f"- candidate: {counts.get('candidate', 0)}")
    lines.append(f"- watch_only: {counts.get('watch_only', 0)}")
    lines.append(f"- avoid: {counts.get('avoid', 0)}")
    lines.append("")

    top = report["candidates"][:top_n]
    if not top:
        lines.append("No candidates to display.")
        return "\n".join(lines)

    lines.append(f"## Top {len(top)} Candidates")
    lines.append("")
    lines.append("| # | Symbol | Score | Rating | Liq | Vol | Tech | News | Risk | Action |")
    lines.append("|---|--------|------:|--------|----:|----:|-----:|-----:|-----:|--------|")
    for c in top:
        lines.append(
            f"| {c['rank']} | {c['symbol']} | {c['score']:.1f} | {c['rating']} | "
            f"{c['liquidity_score']:.0f} | {c['volatility_score']:.0f} | "
            f"{c['technical_score']:.0f} | {c['news_score']:.0f} | {c['risk_score']:.0f} | "
            f"{c['recommended_action']} |"
        )
    lines.append("")

    lines.append("## Detail")
    lines.append("")
    for c in top:
        lines.append(f"### {c['rank']}. {c['symbol']} — {c['rating']} (score {c['score']})")
        lines.append("")
        if c["reasons"]:
            lines.append("**Reasons:**")
            for r in c["reasons"]:
                lines.append(f"- + {r}")
        if c["warnings"]:
            lines.append("**Warnings:**")
            for w in c["warnings"]:
                lines.append(f"- ! {w}")
        if not c["reasons"] and not c["warnings"]:
            lines.append("No notable reasons or warnings.")
        lines.append("")

    if report.get("errors"):
        lines.append("## Fetch Errors")
        lines.append("")
        for sym, err in report["errors"].items():
            lines.append(f"- {sym}: {err}")
        lines.append("")

    return "\n".join(lines)


async def main_async(args):
    screening_cfg = _screening_config()
    default_symbols = screening_cfg.get("default_symbols", [])
    top_n = args.top or screening_cfg.get("top_n", 5)
    min_score = args.min_score if args.min_score is not None else screening_cfg.get("min_score", 60)

    symbols = args.symbols or default_symbols
    if not symbols:
        print("Error: no symbols provided and config has no defaults")
        return 2

    print(f"Screening {len(symbols)} symbols: {symbols}")
    print(f"Top N: {top_n}, min score: {min_score}")

    ohlcv_map = {}
    ticker_map = {}
    fetch_errors = {}

    if args.offline or args.dry_run:
        print("[OFFLINE] using synthetic OHLCV")
        ohlcv_map, ticker_map = _build_synthetic_dataset(symbols)
    else:
        try:
            ohlcv_map, ticker_map, fetch_errors = await _gather_ohlcv(
                symbols, limit=args.limit
            )
        except Exception as e:
            print(f"OHLCV fetch crashed: {e}")
            print("Falling back to synthetic dataset.")
            ohlcv_map, ticker_map = _build_synthetic_dataset(symbols)
            fetch_errors = {s: "fallback_synthetic" for s in symbols}

        for sym, ohlcv in ohlcv_map.items():
            if not ohlcv:
                if sym not in fetch_errors:
                    fetch_errors[sym] = "empty_ohlcv"
                # Synthesise so the symbol still appears in the report
                ohlcv_map[sym] = _synthetic_ohlcv(sym, 100.0, n=120)
                ticker_map[sym] = _synthetic_ticker(sym, 100.0)

    open_positions = []
    if not args.exclude_open_positions:
        try:
            data_manager = DataManager()
            await data_manager.initialize()
            from state import db
            try:
                open_positions = await db.get_open_positions() or []
            finally:
                await data_manager.close()
        except Exception as e:
            print(f"  ! open positions fetch failed: {e}")
            open_positions = []

    agent = ScreeningAgent(screening_cfg)
    candidates = agent.screen(
        symbols=symbols,
        ohlcv_map=ohlcv_map,
        ticker_map=ticker_map,
        news_scores={},
        open_positions=open_positions,
    )

    above = [c for c in candidates if c.score >= min_score]
    top_picks = candidates[:top_n]

    if args.dry_run:
        print("\n[DRY-RUN] would write:")
        print(f"  {args.output_json}")
        print(f"  {args.output_md}")
        print(f"\nTop {len(top_picks)} candidates:")
        for c in top_picks:
            print(f"  {c.rank}. {c.symbol} score={c.score} rating={c.rating}")
        return 0

    report = {
        "generated_at": datetime.now().isoformat(),
        "symbols_scanned": len(candidates),
        "min_score": min_score,
        "top_n": top_n,
        "candidates": [c.to_dict() for c in candidates],
        "above_min_score": [c.to_dict() for c in above],
        "top_picks": [c.to_dict() for c in top_picks],
        "errors": fetch_errors,
        "config": {
            "weights": agent.weights,
            "liquidity_thresholds": agent.liquidity_thresholds,
            "volatility_cfg": agent.volatility_cfg,
            "rating_thresholds": agent.ratings_cfg,
        },
    }

    out_json = project_root / args.output_json
    out_md = project_root / args.output_md
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    with out_json.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=True)
    out_md.write_text(_render_markdown(report, top_n), encoding="utf-8")

    dated_json = out_json.parent / f"{date.today().isoformat()}-screening.json"
    dated_md = out_md.parent / f"{date.today().isoformat()}-screening.md"
    with dated_json.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=True)
    dated_md.write_text(_render_markdown(report, top_n), encoding="utf-8")

    print(f"\nWrote {out_json}")
    print(f"Wrote {out_md}")
    print(f"Wrote {dated_json}")
    print(f"Wrote {dated_md}")
    print(f"\nTop {len(top_picks)}:")
    for c in top_picks:
        print(f"  {c.rank}. {c.symbol} score={c.score} rating={c.rating} action={c.recommended_action}")
    print(f"\nAbove min_score: {len(above)}/{len(candidates)}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Screen and rank candidate symbols")
    parser.add_argument("--symbols", nargs="+", default=None)
    parser.add_argument("--top", type=int, default=None, help="Top N to surface")
    parser.add_argument("--min-score", type=float, default=None)
    parser.add_argument("--limit", type=int, default=200, help="Candle limit per symbol")
    parser.add_argument("--exclude-open-positions", action="store_true")
    parser.add_argument("--offline", action="store_true", help="Use synthetic OHLCV")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--output-json", default="reports/screening/latest-screening.json")
    parser.add_argument("--output-md", default="reports/screening/latest-screening.md")
    args = parser.parse_args()
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    sys.exit(main())

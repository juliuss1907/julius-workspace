#!/usr/bin/env python3
"""
Manual trade report generator.

Consumes shared analysis orchestration for each symbol, converts
results to human-centric ManualTradeReportItem objects, and renders
one flat markdown report.

Does NOT start Telegram, paper-trading runtime, or any execution stack.

All heavy imports (dotenv, utils, orchestration, policies) are deferred
until after argparse so that --help works without the analysis stack.
"""
import argparse
import asyncio
import json
import sys
from datetime import date
from pathlib import Path
from typing import List

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def _parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Generate manual trade report")
    parser.add_argument("--symbols", nargs="*",
                        help="Symbols to analyze (e.g. BTCUSDT ETHUSDT). Default: config watchlist.")
    parser.add_argument("--output", default=None,
                        help="Output file path. Default: reports/manual-trade-report-YYYY-MM-DD.md")
    parser.add_argument("--mode", default="full", choices=("full", "quick"),
                        help="Analysis mode (default: full)")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON instead of markdown")
    return parser.parse_args(argv)


def _lazy_dotenv():
    try:
        from dotenv import load_dotenv
        load_dotenv(project_root / ".env")
    except ImportError:
        pass


def _write_output(path: Path, content: str) -> None:
    """Write content to path, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _default_output_path(today: str | None = None) -> Path:
    """Return the default flat manual-report artifact path."""
    day = today or date.today().isoformat()
    return project_root / "reports" / f"manual-trade-report-{day}.md"


async def _analyze_symbols(
    symbols: List[str],
    mode: str,
    *,
    analyze_symbol_fn=None,
    final_analysis_to_report_item_fn=None,
    manual_item_cls=None,
    logger=None,
    data_manager=None,
) -> list:
    """Analyze a batch of symbols, continuing past individual failures.

    On failure, appends a ManualTradeReportItem with setup_quality='avoid',
    thesis='Analysis unavailable: ...', and risk_notes with exception type+message.
    """
    owns_default_analyzer = analyze_symbol_fn is None
    if analyze_symbol_fn is None:
        from orchestration import analyze_symbol as analyze_symbol_fn
    if final_analysis_to_report_item_fn is None:
        from policies.manual_report import final_analysis_to_report_item as final_analysis_to_report_item_fn
    if manual_item_cls is None:
        from policies.manual_report import ManualTradeReportItem as manual_item_cls
    if logger is None:
        from utils import get_logger
        logger = get_logger(__name__)

    shared_dm = data_manager
    if shared_dm is None and owns_default_analyzer:
        from dataflows import data_manager as shared_dm

    if shared_dm is not None:
        await shared_dm.initialize()

    items = []
    try:
        for symbol in symbols:
            try:
                if shared_dm is not None:
                    bundle = await analyze_symbol_fn(symbol, mode=mode, _data_manager=shared_dm)
                else:
                    bundle = await analyze_symbol_fn(symbol, mode=mode)
                item = final_analysis_to_report_item_fn(bundle.final)
                items.append(item)
                logger.info(
                    f"{symbol}: {item.direction_label} Q={item.setup_quality} "
                    f"C={item.confidence:.2f}"
                )
            except Exception as e:
                logger.warning(f"{symbol}: analysis failed — {type(e).__name__}: {e}")
                items.append(manual_item_cls(
                    symbol=symbol,
                    direction="neutral",
                    confidence=0.0,
                    setup_quality="avoid",
                    thesis=f"Analysis unavailable: {e}",
                    risk_notes=[f"Orchestration error: {type(e).__name__}: {e}"],
                ))
    finally:
        if shared_dm is not None:
            await shared_dm.close()

    return items


async def _run(args):
    _lazy_dotenv()

    from utils import config as cfg_loader, get_logger
    from policies.manual_report import render_markdown_report

    logger = get_logger(__name__)

    if args.symbols:
        symbols = [s.upper() for s in args.symbols]
    else:
        cfg = cfg_loader.load_default_params()
        symbols = cfg.get("watchlist") or ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

    logger.info(f"Analyzing {len(symbols)} symbols in {args.mode} mode: {symbols}")

    items = await _analyze_symbols(symbols, mode=args.mode)

    if args.json:
        payload = [item.to_dict() for item in items]
        print(json.dumps(payload, indent=2, default=str))
        return

    report_md = render_markdown_report(items, mode=args.mode)

    if args.output:
        out_path = Path(args.output)
    else:
        out_path = _default_output_path()

    _write_output(out_path, report_md)
    logger.info(f"Report written to {out_path}")


if __name__ == "__main__":
    args = _parse_args()
    asyncio.run(_run(args))

#!/usr/bin/env python3
"""Thin read-only single-symbol analysis CLI.

The default path is a lightweight client over ``orchestration.analyze_symbol``:
parse args, run the shared analysis core, and print the normalized
``FinalAnalysis`` JSON. Demo execution/risk inspection is available only via
an explicit flag and is imported lazily so ``--help`` and module import stay
cheap and free of execution-runtime dependencies.
"""
import argparse
import asyncio
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def _build_parser() -> argparse.ArgumentParser:
    """Build CLI parser without importing project runtime dependencies."""
    parser = argparse.ArgumentParser(
        description="Run shared orchestration analysis for one symbol and print JSON.",
    )
    parser.add_argument("symbol", nargs="?", default="HYPEUSDT")
    parser.add_argument("--timeframe", default="1h", help="OHLCV timeframe to analyze")
    parser.add_argument("--mode", default="full", help="Analysis mode passed to orchestration")
    parser.add_argument(
        "--include-demo-decision",
        action="store_true",
        help=(
            "Also evaluate demo PositionManager/RiskManager policy. "
            "This intentionally loads execution-adjacent runtime modules."
        ),
    )
    return parser


def _analysis_payload(bundle) -> Dict[str, Any]:
    """Serialize the shared FinalAnalysis contract for CLI JSON output."""
    analysis = bundle.final
    return {
        "symbol": analysis.symbol,
        "timeframe": analysis.timeframe,
        "price": analysis.price,
        "timestamp": analysis.timestamp,
        "analysts": {
            name: asdict(sig)
            for name, sig in analysis.analyst_signals.items()
        },
        "draft_signal": asdict(analysis.draft_signal),
        "final": asdict(analysis.final_signal),
        "direction": analysis.direction,
        "confidence": analysis.confidence,
        "final_action": analysis.action,
        "hold_reason": analysis.hold_reason,
        "research_debate": analysis.research_debate,
        "market_snapshot": analysis.market_snapshot,
        "risk_notes": analysis.risk_notes,
        "metadata": analysis.metadata,
    }


async def _demo_policy_payload(bundle) -> Dict[str, Any]:
    """Evaluate optional demo policy details behind an explicit CLI flag."""
    from dotenv import load_dotenv

    load_dotenv(project_root / ".env")

    from agents import PositionManager, RiskManager
    from policies.demo_execution import build_demo_execution_decision
    from state import PortfolioContextBuilder, db

    risk = RiskManager()
    position_manager = PositionManager()
    portfolio_builder = PortfolioContextBuilder()

    await risk.initialize()
    await position_manager.initialize()

    try:
        analysis = bundle.final
        symbol = analysis.symbol
        open_positions = await db.get_open_positions()
        portfolio_stats = await db.get_portfolio_stats()
        decision = await build_demo_execution_decision(
            bundle=bundle,
            risk_manager=risk,
            position_manager=position_manager,
            portfolio_context_builder=portfolio_builder,
            open_positions=open_positions,
            portfolio_stats=portfolio_stats,
            current_prices={symbol: analysis.price},
            execution_mode="readonly_inspection",
        )
        return {
            "demo_decision": asdict(decision),
            "open_positions": [
                p for p in open_positions if p.get("symbol") == symbol
            ],
        }
    finally:
        await risk.close()
        await position_manager.close()


async def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)
    symbol = args.symbol.upper()

    # Import only after argparse so --help remains lightweight.
    from dotenv import load_dotenv

    load_dotenv(project_root / ".env")

    from orchestration.analysis_runner import analyze_symbol

    bundle = await analyze_symbol(symbol, timeframe=args.timeframe, mode=args.mode)
    payload = _analysis_payload(bundle)

    if args.include_demo_decision:
        payload.update(await _demo_policy_payload(bundle))

    print(json.dumps(payload, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())

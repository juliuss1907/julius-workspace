#!/usr/bin/env python3
"""Synthetic tests for portfolio exposure context and risk gating."""
import asyncio
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.base_agent import AgentResult, SignalDirection
from agents.risk_manager import RiskManager
from state.portfolio_context import PortfolioContextBuilder
from utils import setup_logging


setup_logging("INFO")


def make_signal(name: str, direction: SignalDirection, score: float, confidence: float, funding_avg=0.0001):
    analysis = {"indicators": {"atr": 100.0}}
    if name == "DerivativesAnalyst":
        analysis["funding"] = {"average": funding_avg}
    return AgentResult(
        agent_name=name,
        symbol="BTCUSDT",
        timestamp=datetime.now(),
        direction=direction,
        sub_score=score,
        confidence=confidence,
        analysis=analysis,
        reasoning=f"synthetic {name} {direction.value}",
        metadata={},
    )


async def main():
    config_override = {
        "demo_trading": {"auto_execute": {"min_confidence": 0.60}},
        "risk_manager": {
            "min_signal_confidence": 0.60,
            "total_exposure_warning_pct": 0.70,
            "max_total_exposure_pct": 0.80,
            "correlated_exposure_warning_pct": 0.40,
            "max_correlated_exposure_pct": 0.50,
            "portfolio_exposure_warning_multiplier": 0.70,
            "correlated_exposure_warning_multiplier": 0.80,
            "correlated_groups": {"majors": ["BTC", "ETH", "SOL"]},
        },
    }
    builder = PortfolioContextBuilder(config_override)

    positions = [
        {"symbol": "ETHUSDT", "side": "LONG", "market_type": "spot", "entry_price": 3000, "quantity": 1.0, "leverage": 1},
        {"symbol": "SOLUSDT", "side": "LONG", "market_type": "futures", "entry_price": 150, "quantity": 10.0, "leverage": 2},
    ]
    context = builder.build(
        open_positions=positions,
        portfolio_stats={"total_balance": 10000.0},
        current_prices={"ETHUSDT": 3100.0, "SOLUSDT": 160.0},
    )
    assert context["open_positions_count"] == 2
    assert round(context["total_exposure_pct"], 2) == 0.63
    assert round(context["correlated_exposure_pct"]["majors"], 2) == 0.63

    final_bull = make_signal("TraderAgent", SignalDirection.BULLISH, 0.68, 0.75)
    analyst_signals = {
        "technical": make_signal("TechnicalAnalyst", SignalDirection.BULLISH, 0.66, 0.80),
        "derivatives": make_signal("DerivativesAnalyst", SignalDirection.NEUTRAL, 0.52, 0.70),
    }
    risk = RiskManager(config_override)

    correlated_block = await risk.evaluate(
        symbol="BTCUSDT",
        final_signal=final_bull,
        analyst_signals=analyst_signals,
        market_snapshot={"last_close": 10000.0, "atr": 100.0},
        open_positions=positions,
        portfolio_stats={"total_balance": 10000.0},
        portfolio_context=context,
    )
    assert correlated_block["approved"] is False
    assert "correlated exposure too high" in correlated_block["reason"]

    warning_context = builder.build(
        open_positions=[
            {"symbol": "XRPUSDT", "side": "LONG", "market_type": "spot", "entry_price": 1, "quantity": 3600, "leverage": 1},
            {"symbol": "ETHUSDT", "side": "SHORT", "market_type": "spot", "entry_price": 2000, "quantity": 1.8, "leverage": 1},
        ],
        portfolio_stats={"total_balance": 10000.0},
    )
    total_warning = await risk.evaluate(
        symbol="BTCUSDT",
        final_signal=final_bull,
        analyst_signals=analyst_signals,
        market_snapshot={"last_close": 10000.0, "atr": 100.0},
        open_positions=[],
        portfolio_stats={"total_balance": 10000.0},
        portfolio_context=warning_context,
    )
    assert total_warning["approved"] is True
    assert total_warning["risk_level"] in ("medium", "high")
    assert total_warning["position_size_multiplier"] == 0.70

    print("Portfolio context synthetic tests passed")
    print(f"correlated_block_reason={correlated_block['reason']}")
    print(f"warning_multiplier={total_warning['position_size_multiplier']:.2f}")


if __name__ == "__main__":
    asyncio.run(main())

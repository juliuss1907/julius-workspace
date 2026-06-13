#!/usr/bin/env python3
"""Synthetic tests for RiskManager."""
import asyncio
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.base_agent import AgentResult, SignalDirection
from agents.risk_manager import RiskManager
from utils import setup_logging


setup_logging("INFO")


def make_signal(name: str, direction: SignalDirection, score: float, confidence: float, funding_avg=None, atr=100.0):
    analysis = {"indicators": {"atr": atr}}
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
    risk = RiskManager({
        "demo_trading": {"auto_execute": {"min_confidence": 0.60}},
        "risk_management": {"max_open_positions": 2},
        "risk_manager": {
            "max_open_positions": 2,
            "technical_conflict_multiplier": 0.40,
            "analyst_conflict_step": 0.10,
            "analyst_conflict_floor": 0.60,
        },
        "futures": {"max_acceptable_funding": 0.001, "funding_warning_threshold": 0.0005},
    })

    final_bull = make_signal("TraderAgent", SignalDirection.BULLISH, 0.68, 0.75)
    signals_bull = {
        "technical": make_signal("TechnicalAnalyst", SignalDirection.BULLISH, 0.66, 0.80),
        "derivatives": make_signal("DerivativesAnalyst", SignalDirection.NEUTRAL, 0.52, 0.70, funding_avg=0.0001),
    }

    approved = await risk.evaluate(
        "BTCUSDT",
        final_bull,
        signals_bull,
        market_snapshot={"last_close": 10000, "atr": 100},
        open_positions=[],
    )
    print("approved", approved)
    assert approved["approved"] is True
    assert approved["risk_level"] == "low"

    neutral = await risk.evaluate(
        "BTCUSDT",
        make_signal("TraderAgent", SignalDirection.NEUTRAL, 0.50, 0.55),
        signals_bull,
        market_snapshot={"last_close": 10000, "atr": 100},
        open_positions=[],
    )
    assert neutral["approved"] is False
    assert neutral["risk_level"] == "blocked"

    duplicate = await risk.evaluate(
        "BTCUSDT",
        final_bull,
        signals_bull,
        market_snapshot={"last_close": 10000, "atr": 100},
        open_positions=[{"symbol": "BTCUSDT"}],
    )
    assert duplicate["approved"] is False
    assert "pyramiding disabled" in duplicate["reason"]

    crowded = dict(signals_bull)
    crowded["derivatives"] = make_signal("DerivativesAnalyst", SignalDirection.BEARISH, 0.30, 0.80, funding_avg=0.002)
    funding_block = await risk.evaluate(
        "BTCUSDT",
        final_bull,
        crowded,
        market_snapshot={"last_close": 10000, "atr": 100},
        open_positions=[],
    )
    assert funding_block["approved"] is False
    assert "funding" in funding_block["reason"]

    conflict = dict(signals_bull)
    conflict["technical"] = make_signal("TechnicalAnalyst", SignalDirection.BEARISH, 0.30, 0.80)
    reduced = await risk.evaluate(
        "BTCUSDT",
        final_bull,
        conflict,
        market_snapshot={"last_close": 10000, "atr": 100},
        open_positions=[],
    )
    assert reduced["approved"] is True
    assert reduced["risk_level"] in ("medium", "high")
    assert reduced["position_size_multiplier"] < 1.0
    assert reduced["position_size_multiplier"] == 0.40

    print("RiskManager synthetic tests passed")


if __name__ == "__main__":
    asyncio.run(main())

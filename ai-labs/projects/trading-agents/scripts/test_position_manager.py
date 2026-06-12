#!/usr/bin/env python3
"""Synthetic tests for PositionManager."""
import asyncio
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.base_agent import AgentResult, SignalDirection
from agents.position_manager import PositionManager
from utils import setup_logging


setup_logging("INFO")


def signal(name: str, direction: SignalDirection, confidence: float):
    score = {SignalDirection.BULLISH: 0.68, SignalDirection.BEARISH: 0.32, SignalDirection.NEUTRAL: 0.50}[direction]
    return AgentResult(
        agent_name=name,
        symbol="BTCUSDT",
        timestamp=datetime.now(),
        direction=direction,
        sub_score=score,
        confidence=confidence,
        analysis={"indicators": {"atr": 100.0}},
        reasoning=f"synthetic {direction.value}",
        metadata={},
    )


async def main():
    manager = PositionManager({"position_manager": {"reverse_enabled": False}})
    long_pos = {"trade_id": "long1", "symbol": "BTCUSDT", "side": "LONG", "entry_price": 10000, "quantity": 0.1, "market_type": "spot"}
    short_pos = {"trade_id": "short1", "symbol": "BTCUSDT", "side": "SHORT", "entry_price": 10000, "quantity": 0.1, "market_type": "futures"}

    no_pos = await manager.evaluate("BTCUSDT", signal("TraderAgent", SignalDirection.BULLISH, 0.75), {}, open_positions=[])
    assert no_pos["action"] == "no_position"

    hold_long = await manager.evaluate("BTCUSDT", signal("TraderAgent", SignalDirection.BULLISH, 0.75), {}, open_positions=[long_pos])
    assert hold_long["action"] == "hold_position"

    weak_opp = await manager.evaluate("BTCUSDT", signal("TraderAgent", SignalDirection.BEARISH, 0.55), {}, open_positions=[long_pos])
    assert weak_opp["action"] == "hold_position"

    reduce = await manager.evaluate("BTCUSDT", signal("TraderAgent", SignalDirection.BEARISH, 0.65), {}, open_positions=[long_pos])
    assert reduce["action"] == "reduce_position"
    assert reduce["close_fraction"] == 0.5

    close = await manager.evaluate(
        "BTCUSDT",
        signal("TraderAgent", SignalDirection.BEARISH, 0.75),
        {"technical": signal("TechnicalAnalyst", SignalDirection.BEARISH, 0.80)},
        open_positions=[long_pos],
    )
    assert close["action"] == "close_position"

    close_short = await manager.evaluate(
        "BTCUSDT",
        signal("TraderAgent", SignalDirection.BULLISH, 0.75),
        {"technical": signal("TechnicalAnalyst", SignalDirection.BULLISH, 0.80)},
        open_positions=[short_pos],
    )
    assert close_short["action"] == "close_position"

    profit_reduce = await manager.evaluate(
        "BTCUSDT",
        signal("TraderAgent", SignalDirection.NEUTRAL, 0.55),
        {},
        open_positions=[long_pos],
        market_snapshot={"last_close": 10600},
    )
    assert profit_reduce["action"] == "reduce_position"

    loss_close = await manager.evaluate(
        "BTCUSDT",
        signal("TraderAgent", SignalDirection.BEARISH, 0.65),
        {},
        open_positions=[long_pos],
        market_snapshot={"last_close": 9500},
    )
    assert loss_close["action"] == "close_position"

    reverse_disabled = await manager.evaluate(
        "BTCUSDT",
        signal("TraderAgent", SignalDirection.BEARISH, 0.85),
        {"technical": signal("TechnicalAnalyst", SignalDirection.BEARISH, 0.85)},
        risk_decision={"approved": True},
        open_positions=[long_pos],
    )
    assert reverse_disabled["action"] == "close_position"
    assert reverse_disabled["reverse_allowed"] is False

    reverse_manager = PositionManager({"position_manager": {"reverse_enabled": True}})
    reverse_enabled = await reverse_manager.evaluate(
        "BTCUSDT",
        signal("TraderAgent", SignalDirection.BEARISH, 0.85),
        {"technical": signal("TechnicalAnalyst", SignalDirection.BEARISH, 0.85)},
        risk_decision={"approved": False},
        open_positions=[long_pos],
    )
    assert reverse_enabled["action"] == "reverse_position"
    assert reverse_enabled["reverse_allowed"] is True

    print("PositionManager synthetic tests passed")


if __name__ == "__main__":
    asyncio.run(main())

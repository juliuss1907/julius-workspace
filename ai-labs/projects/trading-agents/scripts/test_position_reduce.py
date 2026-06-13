#!/usr/bin/env python3
"""Dry-run synthetic tests for partial reduce, close reason mapping, and execution status."""
import asyncio
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import state.database as db_module
from agents.base_agent import AgentResult, SignalDirection
from agents.position_manager import PositionManager
from trading.base_trader import CloseReason, MarketType, TradeResult, TradeSide
from trading.order_manager import OrderManager
from utils import setup_logging


setup_logging("INFO")


def make_signal(name: str, direction: SignalDirection, confidence: float):
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


class FakeTrader:
    def __init__(self, market_type: MarketType):
        self.market_type = market_type
        self.last_close = None

    async def get_balance(self) -> float:
        return 5000.0

    async def close_position(self, trade_id, reason=CloseReason.MANUAL, close_price=None, close_quantity=None):
        self.last_close = {"trade_id": trade_id, "reason": reason, "close_quantity": close_quantity}
        return type("FakeClosed", (), {
            "trade_id": trade_id,
            "symbol": "BTCUSDT",
            "side": TradeSide.LONG,
            "market_type": self.market_type,
            "entry_price": 10000,
            "exit_price": 10050,
            "quantity": close_quantity or 0.1,
            "leverage": 1.0,
            "pnl": 5.0,
            "pnl_pct": 0.5,
            "fees": 0.5,
            "close_reason": reason,
            "opened_at": datetime.now(),
            "closed_at": datetime.now(),
            "duration_seconds": 0,
        })


class FakeOrderManager(OrderManager):
    def __init__(self):
        self.spot_trader = FakeTrader(MarketType.SPOT)
        self.futures_trader = FakeTrader(MarketType.FUTURES)
        self.config = {}
        self.market_selection = {}
        self.futures_allowed_coins = ["BTC", "ETH", "SOL"]
        self.futures_on_downtrend = True
        self.risk_per_trade = 0.03
        self.max_position_size = 0.30
        self.max_open_positions = 5
        self.min_confidence = 0.60
        self.max_trades_per_day = 10
        self._initialized = True
        self._fake_positions = []

    async def get_all_positions(self):
        return self._fake_positions


async def make_positions(positions):
    async def _inner(symbol=None):
        if symbol:
            return [p for p in positions if p["symbol"] == symbol]
        return positions
    return _inner


async def main():
    pos_large = {
        "trade_id": "reduce_large",
        "symbol": "BTCUSDT",
        "side": "LONG",
        "market_type": "spot",
        "entry_price": 10000,
        "quantity": 1.0,
        "leverage": 1,
    }
    pos_small = {
        "trade_id": "reduce_small",
        "symbol": "BTCUSDT",
        "side": "LONG",
        "market_type": "spot",
        "entry_price": 10000,
        "quantity": 0.0001,
        "leverage": 1,
    }

    original_get_open = db_module.db.get_open_positions
    async def fake_get_open_positions(symbol=None):
        return [p for p in [pos_large, pos_small] if not symbol or p["symbol"] == symbol]
    db_module.db.get_open_positions = fake_get_open_positions

    try:
        om = FakeOrderManager()

        big_reduced = await om.reduce_position("reduce_large", 0.5, reason=CloseReason.RISK_REDUCTION)
        assert big_reduced is True
        assert om.spot_trader.last_close["close_quantity"] == 0.5

        tiny = await om.reduce_position("reduce_small", 0.5, reason=CloseReason.PROFIT_PROTECTION)
        assert tiny is True

        pm = PositionManager({"position_manager": {}})
        technical = make_signal("TechnicalAnalyst", SignalDirection.BEARISH, 0.80)

        profit_reduce = await pm.evaluate(
            "BTCUSDT",
            make_signal("TraderAgent", SignalDirection.NEUTRAL, 0.55),
            {},
            open_positions=[pos_large],
            market_snapshot={"last_close": 10600},
        )
        assert profit_reduce["action"] == "reduce_position"
        assert profit_reduce["close_reason"] == "profit_protection"

        signal_close = await pm.evaluate(
            "BTCUSDT",
            make_signal("TraderAgent", SignalDirection.BEARISH, 0.75),
            {"technical": technical},
            open_positions=[pos_large],
        )
        assert signal_close["action"] == "close_position"
        assert signal_close["close_reason"] == "signal_reversal"

        loss_close = await pm.evaluate(
            "BTCUSDT",
            make_signal("TraderAgent", SignalDirection.BEARISH, 0.65),
            {},
            open_positions=[pos_large],
            market_snapshot={"last_close": 9500},
        )
        assert loss_close["action"] == "close_position"
        assert loss_close["close_reason"] == "loss_control"

        risk_reduce = await pm.evaluate(
            "BTCUSDT",
            make_signal("TraderAgent", SignalDirection.BEARISH, 0.65),
            {},
            open_positions=[pos_large],
        )
        assert risk_reduce["action"] == "reduce_position"
        assert risk_reduce["close_reason"] == "risk_reduction"

        print("Partial reduce and close reason synthetic tests passed")
        print(f"reduce_fraction=0.5 close_quantity={om.spot_trader.last_close['close_quantity']}")
        print(f"profit_reduce_reason={profit_reduce['close_reason']}")
        print(f"signal_close_reason={signal_close['close_reason']}")
        print(f"loss_close_reason={loss_close['close_reason']}")
        print(f"risk_reduce_reason={risk_reduce['close_reason']}")
    finally:
        db_module.db.get_open_positions = original_get_open


if __name__ == "__main__":
    asyncio.run(main())

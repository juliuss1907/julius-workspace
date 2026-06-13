#!/usr/bin/env python3
"""Dry-run Phase 4B validation for the RiskManager execution gate."""
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import trading.order_manager as order_manager_module
from agents.base_agent import AgentResult, SignalDirection
from agents.risk_manager import RiskManager
from state.signal_recorder import SignalRecorder
from trading.base_trader import MarketType, TradeResult, TradeSide
from trading.order_manager import OrderManager
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


class FakeTrader:
    def __init__(self, market_type: MarketType):
        self.market_type = market_type
        self.last_order = None

    async def get_balance(self) -> float:
        return 10000.0

    async def place_trade(self, symbol, side, quantity, price=None, stop_loss=None, take_profit=None, signal_data=None):
        self.last_order = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "signal_data": signal_data or {},
        }
        return TradeResult(
            success=True,
            trade_id="dry_run_phase4b",
            symbol=symbol,
            side=side,
            market_type=self.market_type,
            entry_price=price,
            quantity=quantity,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )

    async def close(self):
        pass


class DryRunOrderManager(OrderManager):
    def __init__(self):
        self.config = {"auto_execute": {"min_confidence": 0.60}}
        self.spot_trader = FakeTrader(MarketType.SPOT)
        self.futures_trader = FakeTrader(MarketType.FUTURES)
        self.market_selection = {}
        self.futures_allowed_coins = ["BTC", "ETH", "SOL"]
        self.futures_on_downtrend = True
        self.risk_per_trade = 0.03
        self.max_position_size = 0.30
        self.max_open_positions = 5
        self.min_confidence = 0.60
        self.max_trades_per_day = 10
        self._initialized = True


async def no_open_positions():
    return []


async def main():
    original_get_open_positions = order_manager_module.db.get_open_positions
    order_manager_module.db.get_open_positions = no_open_positions

    try:
        risk = RiskManager({
            "demo_trading": {"auto_execute": {"min_confidence": 0.60}},
            "risk_management": {"max_open_positions": 5},
            "futures": {"max_acceptable_funding": 0.001, "funding_warning_threshold": 0.0005},
        })

        final_bull = make_signal("TraderAgent", SignalDirection.BULLISH, 0.68, 0.75)
        analyst_signals = {
            "technical": make_signal("TechnicalAnalyst", SignalDirection.BEARISH, 0.34, 0.80),
            "news": make_signal("NewsAnalyst", SignalDirection.BULLISH, 0.64, 0.70),
            "sentiment": make_signal("SentimentAnalyst", SignalDirection.BULLISH, 0.66, 0.80),
            "fundamentals": make_signal("FundamentalsAnalyst", SignalDirection.BULLISH, 0.67, 0.80),
            "derivatives": make_signal("DerivativesAnalyst", SignalDirection.NEUTRAL, 0.52, 0.70, funding_avg=0.0001),
        }

        risk_decision = await risk.evaluate(
            symbol="BTCUSDT",
            final_signal=final_bull,
            analyst_signals=analyst_signals,
            research_debate={"consensus": "balanced"},
            market_snapshot={"last_close": 10000.0, "atr": 100.0},
            open_positions=[],
            portfolio_stats={"open_positions": 0},
        )
        assert risk_decision["approved"] is True
        assert 0 < risk_decision["position_size_multiplier"] < 1.0

        order_manager = DryRunOrderManager()
        trade_result = await order_manager.execute_signal(
            final_bull,
            current_price=10000.0,
            atr=100.0,
            risk_decision=risk_decision,
        )
        assert trade_result and trade_result.success
        assert trade_result.quantity < 0.30
        assert order_manager.spot_trader.last_order["signal_data"]["risk_multiplier"] == risk_decision["position_size_multiplier"]
        assert order_manager.spot_trader.last_order["signal_data"]["risk_level"] == risk_decision["risk_level"]

        rejected = await risk.evaluate(
            symbol="BTCUSDT",
            final_signal=final_bull,
            analyst_signals=analyst_signals,
            research_debate={"consensus": "balanced"},
            market_snapshot={"last_close": 10000.0, "atr": 100.0},
            open_positions=[{"symbol": "BTCUSDT"}],
            portfolio_stats={"open_positions": 1},
        )
        assert rejected["approved"] is False
        assert rejected["position_size_multiplier"] == 0.0

        log_path = Path("/tmp/opencode/phase4b_risk_gate_signals.jsonl")
        recorder = SignalRecorder(log_path=log_path)
        record = recorder.record_signal(
            symbol="BTCUSDT",
            analyst_signals=analyst_signals,
            draft_signal=final_bull,
            final_signal=final_bull,
            research_debate={"consensus": "balanced"},
            market_snapshot={"last_close": 10000.0, "atr": 100.0},
            risk_decision=rejected,
            execution_status="risk_rejected",
        )
        assert record["execution_status"] == "risk_rejected"
        assert record["risk_decision"]["approved"] is False

        last_record = json.loads(log_path.read_text(encoding="utf-8").splitlines()[-1])
        assert last_record["execution_status"] == "risk_rejected"
        assert last_record["risk_decision"]["risk_level"] == "blocked"

        print("Phase 4B risk gate dry-run validation passed")
        print(f"approved_multiplier={risk_decision['position_size_multiplier']:.3f}")
        print(f"dry_run_quantity={trade_result.quantity:.6f}")
        print(f"rejection_reason={rejected['reason']}")
    finally:
        order_manager_module.db.get_open_positions = original_get_open_positions


if __name__ == "__main__":
    asyncio.run(main())

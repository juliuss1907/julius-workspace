#!/usr/bin/env python3
"""Test Phase 5B.4: Guarded Reverse Flow policy and execution statuses.

Mirrors the logic of TradingSystem._execute_guarded_reverse in run_paper_trading.py
without spinning up the full trading system.
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils import setup_logging

setup_logging("INFO")


class FakeOrderManager:
    def __init__(self, close_returns=True, open_returns=True):
        self.close_returns = close_returns
        self.open_returns = open_returns
        self.closed_ids = []
        self.executed_signals = []
        self.open_positions = []
        self.portfolio_stats = {}

    async def close_position(self, trade_id, reason=None):
        self.closed_ids.append(trade_id)
        if self.close_returns:
            self.open_positions = [p for p in self.open_positions if p.get("trade_id") != trade_id]
            return True
        return False

    async def execute_signal(self, signal, current_price, atr, risk_decision=None):
        result = type("R", (), {
            "success": self.open_returns,
            "trade_id": f"reverse_{len(self.executed_signals)+1}",
            "symbol": signal.symbol,
            "side": signal.direction,
            "market_type": type("M", (), {"value": "spot"})(),
            "entry_price": current_price,
            "quantity": 0.1,
            "leverage": 1.0,
            "stop_loss": None,
            "take_profit": None,
            "order_id": None,
            "error_message": None,
        })()
        if result.success:
            self.executed_signals.append(signal)
        return result

    async def get_all_positions(self):
        return list(self.open_positions)

    async def get_portfolio_stats(self):
        return dict(self.portfolio_stats)


class FakeRiskManager:
    def __init__(self, approved=True, reason="risk checks passed"):
        self.approved = approved
        self.reason = reason
        self.evaluate_calls = 0

    async def evaluate(self, **kwargs):
        self.evaluate_calls += 1
        return {
            "approved": self.approved,
            "risk_level": "low" if self.approved else "blocked",
            "reason": self.reason,
            "position_size_multiplier": 1.0 if self.approved else 0.0,
        }


class FakePortfolioContextBuilder:
    def __init__(self, ctx=None):
        self.ctx = ctx or {}

    def build(self, **kwargs):
        return self.ctx


class FakeDataManager:
    def __init__(self, ticker_price=100.0):
        self.ticker_price = ticker_price

    async def get_ticker(self, symbol):
        return {"price": self.ticker_price, "symbol": symbol}


class FakeSignal:
    def __init__(self, symbol, direction, confidence=0.85):
        self.symbol = symbol
        self.direction = direction
        self.confidence = confidence
        self.analysis = {"indicators": {"atr": 100.0}}
        self.sub_score = 0.7
        self.metadata = {}


class FakeNotifier:
    def __init__(self):
        self.calls = []

    async def notify_trade_opened(self, result):
        self.calls.append(("trade_opened", result.trade_id))

    async def notify_position_event(self, **kwargs):
        self.calls.append(("position_event", kwargs))


async def _guarded_reverse(
    reverse_enabled: bool,
    mode: str,
    min_conf: float,
    rerun_risk: bool,
    final_signal,
    position_decision: dict,
    order_manager,
    risk_manager,
    portfolio_context_builder,
    notifier,
    data_manager,
    close_reason,
):
    """Mirror of TradingSystem._execute_guarded_reverse."""
    if not reverse_enabled or mode != "execute_all":
        return ("position_reverse_recommended", None, None)
    if final_signal.confidence < min_conf:
        return ("position_reversed_close_only", None, None)
    trade_id = position_decision.get("position", {}).get("trade_id")
    if not trade_id:
        return ("position_reverse_close_failed", None, None)
    closed = await order_manager.close_position(trade_id, reason=close_reason)
    if not closed:
        return ("position_reverse_close_failed", None, None)
    if not rerun_risk:
        return ("position_reversed_close_only", None, None)
    open_positions = await order_manager.get_all_positions()
    portfolio_stats = await order_manager.get_portfolio_stats()
    portfolio_context = portfolio_context_builder.build(
        open_positions=open_positions,
        portfolio_stats=portfolio_stats,
        current_prices={final_signal.symbol: 100.0},
    )
    risk_decision = await risk_manager.evaluate(
        symbol=final_signal.symbol,
        final_signal=final_signal,
        analyst_signals={},
        research_debate={},
        market_snapshot={"last_close": 100.0, "atr": 100.0},
        open_positions=open_positions,
        portfolio_stats=portfolio_stats,
        portfolio_context=portfolio_context,
    )
    if not risk_decision["approved"]:
        return ("position_reversed_close_only", None, risk_decision)
    ticker = await data_manager.get_ticker(final_signal.symbol)
    if not ticker:
        return ("position_reverse_open_failed", None, risk_decision)
    result = await order_manager.execute_signal(
        final_signal, ticker["price"], 100.0, risk_decision=risk_decision,
    )
    if result and result.success:
        await notifier.notify_trade_opened(result)
        return ("position_reversed", result, risk_decision)
    return ("position_reverse_open_failed", result, risk_decision)


async def main():
    # ── 1. reverse disabled -> recommended only ──────────────────────────
    om = FakeOrderManager()
    rm = FakeRiskManager()
    pcb = FakePortfolioContextBuilder()
    nm = FakeNotifier()
    dm = FakeDataManager()
    sig = FakeSignal("BTCUSDT", "bearish", 0.85)
    pos = {"position": {"trade_id": "old_btc_long", "side": "LONG"}}

    status, trade, risk = await _guarded_reverse(
        reverse_enabled=False, mode="execute_all", min_conf=0.80,
        rerun_risk=True, final_signal=sig, position_decision=pos,
        order_manager=om, risk_manager=rm, portfolio_context_builder=pcb,
        notifier=nm, data_manager=dm, close_reason=None,
    )
    assert status == "position_reverse_recommended"
    assert trade is None and risk is None
    assert len(om.closed_ids) == 0
    assert rm.evaluate_calls == 0
    print("PASS reverse_disabled_recommended")

    # ── 2. mode not execute_all -> recommended only ──────────────────────
    om = FakeOrderManager()
    rm = FakeRiskManager()
    pcb = FakePortfolioContextBuilder()
    nm = FakeNotifier()
    dm = FakeDataManager()
    status, trade, risk = await _guarded_reverse(
        reverse_enabled=True, mode="execute_close_only", min_conf=0.80,
        rerun_risk=True, final_signal=sig, position_decision=pos,
        order_manager=om, risk_manager=rm, portfolio_context_builder=pcb,
        notifier=nm, data_manager=dm, close_reason=None,
    )
    assert status == "position_reverse_recommended"
    assert len(om.closed_ids) == 0
    print("PASS mode_not_execute_all_recommended")

    # ── 3. confidence below threshold -> close-only ─────────────────────
    om = FakeOrderManager(close_returns=True)
    rm = FakeRiskManager()
    pcb = FakePortfolioContextBuilder()
    nm = FakeNotifier()
    dm = FakeDataManager()
    sig_low = FakeSignal("BTCUSDT", "bearish", 0.65)
    status, trade, risk = await _guarded_reverse(
        reverse_enabled=True, mode="execute_all", min_conf=0.80,
        rerun_risk=True, final_signal=sig_low, position_decision=pos,
        order_manager=om, risk_manager=rm, portfolio_context_builder=pcb,
        notifier=nm, data_manager=dm, close_reason=None,
    )
    assert status == "position_reversed_close_only"
    assert len(om.closed_ids) == 0
    assert rm.evaluate_calls == 0
    print("PASS low_confidence_close_only")

    # ── 4. close fails -> reverse_close_failed ──────────────────────────
    om = FakeOrderManager(close_returns=False)
    rm = FakeRiskManager()
    pcb = FakePortfolioContextBuilder()
    nm = FakeNotifier()
    dm = FakeDataManager()
    status, trade, risk = await _guarded_reverse(
        reverse_enabled=True, mode="execute_all", min_conf=0.80,
        rerun_risk=True, final_signal=sig, position_decision=pos,
        order_manager=om, risk_manager=rm, portfolio_context_builder=pcb,
        notifier=nm, data_manager=dm, close_reason=None,
    )
    assert status == "position_reverse_close_failed"
    assert len(om.closed_ids) == 1
    assert rm.evaluate_calls == 0
    assert len(om.executed_signals) == 0
    print("PASS close_fail_no_reverse")

    # ── 5. close ok + risk rejects -> close-only ─────────────────────────
    om = FakeOrderManager(close_returns=True)
    rm = FakeRiskManager(approved=False, reason="exposure too high")
    pcb = FakePortfolioContextBuilder()
    nm = FakeNotifier()
    dm = FakeDataManager()
    status, trade, risk = await _guarded_reverse(
        reverse_enabled=True, mode="execute_all", min_conf=0.80,
        rerun_risk=True, final_signal=sig, position_decision=pos,
        order_manager=om, risk_manager=rm, portfolio_context_builder=pcb,
        notifier=nm, data_manager=dm, close_reason=None,
    )
    assert status == "position_reversed_close_only"
    assert len(om.closed_ids) == 1
    assert rm.evaluate_calls == 1
    assert len(om.executed_signals) == 0
    assert risk["approved"] is False
    print("PASS risk_reject_close_only")

    # ── 6. close ok + risk approve + open ok -> reversed ─────────────────
    om = FakeOrderManager(close_returns=True, open_returns=True)
    rm = FakeRiskManager(approved=True)
    pcb = FakePortfolioContextBuilder()
    nm = FakeNotifier()
    dm = FakeDataManager()
    status, trade, risk = await _guarded_reverse(
        reverse_enabled=True, mode="execute_all", min_conf=0.80,
        rerun_risk=True, final_signal=sig, position_decision=pos,
        order_manager=om, risk_manager=rm, portfolio_context_builder=pcb,
        notifier=nm, data_manager=dm, close_reason=None,
    )
    assert status == "position_reversed"
    assert trade is not None and trade.success is True
    assert len(om.closed_ids) == 1
    assert rm.evaluate_calls == 1
    assert len(om.executed_signals) == 1
    assert len(nm.calls) == 1
    assert nm.calls[0][0] == "trade_opened"
    print("PASS full_reverse_success")

    # ── 7. close ok + risk approve + open fail -> open_failed ───────────
    om = FakeOrderManager(close_returns=True, open_returns=False)
    rm = FakeRiskManager(approved=True)
    pcb = FakePortfolioContextBuilder()
    nm = FakeNotifier()
    dm = FakeDataManager()
    status, trade, risk = await _guarded_reverse(
        reverse_enabled=True, mode="execute_all", min_conf=0.80,
        rerun_risk=True, final_signal=sig, position_decision=pos,
        order_manager=om, risk_manager=rm, portfolio_context_builder=pcb,
        notifier=nm, data_manager=dm, close_reason=None,
    )
    assert status == "position_reverse_open_failed"
    assert trade is not None and trade.success is False
    assert len(om.closed_ids) == 1
    assert len(om.executed_signals) == 0
    print("PASS open_fail_after_close")

    # ── 8. no trade_id -> close_failed ───────────────────────────────────
    om = FakeOrderManager()
    rm = FakeRiskManager()
    pcb = FakePortfolioContextBuilder()
    nm = FakeNotifier()
    dm = FakeDataManager()
    status, trade, risk = await _guarded_reverse(
        reverse_enabled=True, mode="execute_all", min_conf=0.80,
        rerun_risk=True, final_signal=sig, position_decision={"position": {}},
        order_manager=om, risk_manager=rm, portfolio_context_builder=pcb,
        notifier=nm, data_manager=dm, close_reason=None,
    )
    assert status == "position_reverse_close_failed"
    assert len(om.closed_ids) == 0
    print("PASS missing_trade_id")

    # ── 9. rerun_risk disabled -> close only, no risk call ──────────────
    om = FakeOrderManager(close_returns=True)
    rm = FakeRiskManager()
    pcb = FakePortfolioContextBuilder()
    nm = FakeNotifier()
    dm = FakeDataManager()
    status, trade, risk = await _guarded_reverse(
        reverse_enabled=True, mode="execute_all", min_conf=0.80,
        rerun_risk=False, final_signal=sig, position_decision=pos,
        order_manager=om, risk_manager=rm, portfolio_context_builder=pcb,
        notifier=nm, data_manager=dm, close_reason=None,
    )
    assert status == "position_reversed_close_only"
    assert len(om.closed_ids) == 1
    assert rm.evaluate_calls == 0
    assert len(om.executed_signals) == 0
    print("PASS no_rerun_close_only")

    # ── 10. ticker unavailable -> open_failed ───────────────────────────
    om = FakeOrderManager(close_returns=True)
    rm = FakeRiskManager(approved=True)
    pcb = FakePortfolioContextBuilder()
    nm = FakeNotifier()

    class NoTickerDM:
        async def get_ticker(self, symbol):
            return None

    status, trade, risk = await _guarded_reverse(
        reverse_enabled=True, mode="execute_all", min_conf=0.80,
        rerun_risk=True, final_signal=sig, position_decision=pos,
        order_manager=om, risk_manager=rm, portfolio_context_builder=pcb,
        notifier=nm, data_manager=NoTickerDM(), close_reason=None,
    )
    assert status == "position_reverse_open_failed"
    assert len(om.executed_signals) == 0
    print("PASS no_ticker_open_failed")

    print("\nAll Phase 5B.4 guarded reverse flow tests passed.")


if __name__ == "__main__":
    asyncio.run(main())

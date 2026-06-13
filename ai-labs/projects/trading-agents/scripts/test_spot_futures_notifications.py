#!/usr/bin/env python3
"""Tests for spot vs futures notification wording and field propagation."""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from trading.trade_notifier import TradeNotifier
from utils import setup_logging
import state.database as db_module

setup_logging("INFO")


class FakeBot:
    def __init__(self):
        self.sent = []

    async def send_message(self, chat_id, text, parse_mode=None):
        self.sent.append({"chat_id": chat_id, "text": text, "parse_mode": parse_mode})
        return None


class FakeDB:
    def __init__(self):
        self.logged = []

    async def log_notification(self, **kwargs):
        self.logged.append(kwargs)


def make_notifier():
    config = {
        "telegram": {
            "enabled": True,
            "chat_id": 12345,
            "bot_token": "x",
        },
        "position_events": {
            "enabled": True,
            "notify_closed": True,
            "notify_reduced": True,
            "notify_failures": True,
            "notify_recommendations": True,
        },
    }
    notifier = TradeNotifier.__new__(TradeNotifier)
    notifier.config = config
    notifier.bot = FakeBot()
    notifier._db = FakeDB()
    notifier.chat_id = 12345
    notifier.session = None
    notifier.enabled = True

    async def fake_send(message):
        notifier.bot.sent.append({"chat_id": notifier.chat_id, "text": message, "parse_mode": "HTML"})
        return True

    notifier._send_message = fake_send  # type: ignore[assignment]
    return notifier


async def assert_title(notifier, kwargs, expected_title_substring, label):
    notifier.bot.sent.clear()
    notifier._db.logged.clear()
    await notifier.notify_position_event(**kwargs)
    assert notifier.bot.sent, f"no message sent for {label}"
    text = notifier.bot.sent[0]["text"]
    assert expected_title_substring in text, f"[{label}] expected '{expected_title_substring}' in:\n{text}"
    print(f"PASS {label}")


async def main():
    original_log = db_module.db.log_notification
    db_module.db.log_notification = FakeDB().log_notification
    try:
        await _run_tests()
    finally:
        db_module.db.log_notification = original_log


async def _run_tests():
    # ── 1. spot close uses SPOT SELL EXECUTED ─────────────────────────────
    notifier = make_notifier()
    await assert_title(
        notifier,
        {
            "symbol": "ETHUSDT",
            "action": "close_position",
            "reason": "opposite signal confirmed by position checks",
            "close_reason": "signal_reversal",
            "final_direction": "bearish",
            "final_confidence": 0.72,
            "execution_status": "position_closed",
            "mode": "execute_close_only",
            "market_type": "spot",
            "position_side": "LONG",
            "requested_qty": 0.89,
            "executed_qty": 0.889,
            "trade_id": "ETHUSDT_LONG_1780884139073",
        },
        "SPOT SELL EXECUTED",
        "spot_close_title",
    )

    # ── 2. spot close failed uses SPOT SELL FAILED ───────────────────────
    notifier = make_notifier()
    await assert_title(
        notifier,
        {
            "symbol": "ETHUSDT",
            "action": "close_position",
            "reason": "opposite signal",
            "close_reason": "signal_reversal",
            "final_direction": "bearish",
            "final_confidence": 0.72,
            "execution_status": "position_close_failed",
            "mode": "execute_close_only",
            "market_type": "spot",
            "position_side": "LONG",
            "requested_qty": 0.89,
            "executed_qty": 0.0,
            "trade_id": "ETHUSDT_LONG_1780884139073",
        },
        "SPOT SELL FAILED",
        "spot_close_failed_title",
    )

    # ── 3. futures close uses FUTURES POSITION CLOSED ─────────────────────
    notifier = make_notifier()
    await assert_title(
        notifier,
        {
            "symbol": "BTCUSDT",
            "action": "close_position",
            "reason": "stop loss hit",
            "close_reason": "loss_control",
            "final_direction": "bearish",
            "final_confidence": 0.80,
            "execution_status": "position_closed",
            "mode": "execute_close_only",
            "market_type": "futures",
            "position_side": "SHORT",
            "requested_qty": 0.024,
            "executed_qty": 0.024,
            "trade_id": "BTCUSDT_SHORT_1780576065100",
        },
        "FUTURES POSITION CLOSED",
        "futures_close_title",
    )

    # ── 4. futures close failed uses FUTURES CLOSE FAILED ────────────────
    notifier = make_notifier()
    await assert_title(
        notifier,
        {
            "symbol": "BTCUSDT",
            "action": "close_position",
            "reason": "opposite signal",
            "close_reason": "signal_reversal",
            "final_direction": "bearish",
            "final_confidence": 0.80,
            "execution_status": "position_close_failed",
            "mode": "execute_close_only",
            "market_type": "futures",
            "position_side": "LONG",
            "requested_qty": 0.024,
            "executed_qty": 0.0,
            "trade_id": "BTCUSDT_LONG_x",
        },
        "FUTURES CLOSE FAILED",
        "futures_close_failed_title",
    )

    # ── 5. spot message includes Market + Qty adjusted note ──────────────
    notifier = make_notifier()
    notifier.bot.sent.clear()
    notifier._db.logged.clear()
    await notifier.notify_position_event(
        symbol="ETHUSDT",
        action="close_position",
        reason="opposite signal confirmed by position checks",
        close_reason="signal_reversal",
        final_direction="bearish",
        final_confidence=0.72,
        execution_status="position_closed",
        mode="execute_close_only",
        market_type="spot",
        position_side="LONG",
        requested_qty=0.89,
        executed_qty=0.889,
        trade_id="ETHUSDT_LONG_1780884139073",
    )
    text = notifier.bot.sent[0]["text"]
    assert "<b>Market:</b> Spot" in text, f"missing Market in:\n{text}"
    assert "requested=0.890000" in text, f"missing requested qty in:\n{text}"
    assert "executed=0.889000" in text, f"missing executed qty in:\n{text}"
    assert "adjusted to free balance" in text, f"missing adjusted note in:\n{text}"
    assert "<b>Trade ID:</b> ETHUSDT_LONG_1780884139073" in text, f"missing trade id in:\n{text}"
    print("PASS spot_message_fields_adjusted_qty")

    # ── 6. futures message includes Market + Position Side ───────────────
    notifier = make_notifier()
    notifier.bot.sent.clear()
    notifier._db.logged.clear()
    await notifier.notify_position_event(
        symbol="BTCUSDT",
        action="close_position",
        reason="stop loss",
        close_reason="loss_control",
        final_direction="bullish",
        final_confidence=0.80,
        execution_status="position_closed",
        mode="execute_close_only",
        market_type="futures",
        position_side="SHORT",
        requested_qty=0.024,
        executed_qty=0.024,
        trade_id="BTCUSDT_SHORT_x",
    )
    text = notifier.bot.sent[0]["text"]
    assert "<b>Market:</b> Futures" in text, f"missing Market in:\n{text}"
    assert "<b>Position Side:</b> SHORT" in text, f"missing Position Side in:\n{text}"
    assert "CLOSE leveraged position" in text, f"missing action label in:\n{text}"
    print("PASS futures_message_fields_with_position_side")

    # ── 7. no market_type => generic wording (back-compat) ──────────────
    notifier = make_notifier()
    await assert_title(
        notifier,
        {
            "symbol": "BTCUSDT",
            "action": "close_position",
            "reason": "test",
            "execution_status": "position_closed",
        },
        "POSITION CLOSED",
        "generic_close_title",
    )

    # ── 8. spot close (no qty) does not print Qty line ──────────────────
    notifier = make_notifier()
    notifier.bot.sent.clear()
    notifier._db.logged.clear()
    await notifier.notify_position_event(
        symbol="ETHUSDT",
        action="close_position",
        reason="opposite signal",
        close_reason="signal_reversal",
        final_direction="bearish",
        final_confidence=0.72,
        execution_status="position_close_failed",
        mode="execute_close_only",
        market_type="spot",
        position_side="LONG",
        trade_id="ETHUSDT_LONG_x",
    )
    text = notifier.bot.sent[0]["text"]
    assert "<b>Market:</b> Spot" in text
    assert "<b>Qty:</b>" not in text, f"unexpected Qty line in failure notification:\n{text}"
    print("PASS spot_no_qty_line_on_failure")

    print("\nAll spot vs futures notification tests passed")


if __name__ == "__main__":
    asyncio.run(main())

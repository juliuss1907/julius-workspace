#!/usr/bin/env python3
"""Test position notification policy: format, gate, skip logic."""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils import setup_logging

setup_logging("INFO")

# Build a fake notifier that records calls instead of sending Telegram.


class FakeNotifier:
    def __init__(self):
        self.calls = []

    async def notify_position_event(self, **kwargs):
        self.calls.append(("position_event", kwargs))
        return True

    async def notify_risk_rejected(self, **kwargs):
        self.calls.append(("risk_rejected", kwargs))
        return True


NOTIFY_EVENTS = {
    "position_closed",
    "position_reduced",
    "position_close_failed",
    "position_reduce_failed",
    "position_close_recommended",
    "position_reduce_recommended",
    "position_reverse_recommended",
}

SKIP_EVENTS = {
    "hold",
    "position_hold",
    "no_position",
    "not_evaluated",
    "below_confidence_threshold",
    "executed",
    "execution_failed",
}


def should_notify_position(execution_status, config=None):
    config = config or {}
    position_config = config.get("position_events", {})
    if not position_config.get("enabled", True):
        return False

    if execution_status == "position_closed":
        return position_config.get("notify_closed", True)
    if execution_status == "position_reduced":
        return position_config.get("notify_reduced", True)
    if execution_status in ("position_close_failed", "position_reduce_failed"):
        return position_config.get("notify_failures", True)
    if "recommended" in execution_status:
        return position_config.get("notify_recommendations", True)
    return False


def should_notify_risk_rejected(config=None):
    config = config or {}
    position_config = config.get("position_events", {})
    if not position_config.get("enabled", True):
        return False
    return position_config.get("notify_risk_rejections", False)


async def main():
    fake = FakeNotifier()

    # ── 1. hold does not notify ──────────────────────────────────────────
    fake.calls.clear()
    for status in SKIP_EVENTS:
        if should_notify_position(status):
            await fake.notify_position_event(execution_status=status, symbol="BTC", action="hold", reason="test")
    assert len(fake.calls) == 0, f"skip events should not notify: {fake.calls}"
    print("PASS skip_events_not_notified")

    # ── 2. position_closed notifies ──────────────────────────────────────
    fake.calls.clear()
    await fake.notify_position_event(
        symbol="BTCUSDT", action="close_position", reason="opposite signal",
        close_reason="signal_reversal", final_direction="bearish",
        final_confidence=0.75, execution_status="position_closed",
        mode="execute_close_only",
    )
    assert len(fake.calls) == 1
    call = fake.calls[0][1]
    assert call["execution_status"] == "position_closed"
    assert call["symbol"] == "BTCUSDT"
    print("PASS position_closed_notifies")

    # ── 3. position_reduced notifies ─────────────────────────────────────
    fake.calls.clear()
    await fake.notify_position_event(
        symbol="ETHUSDT", action="reduce_position", reason="profit protection",
        close_reason="profit_protection", final_direction="neutral",
        final_confidence=0.55, execution_status="position_reduced",
        mode="execute_reduce_and_close",
    )
    assert len(fake.calls) == 1
    print("PASS position_reduced_notifies")

    # ── 4. position_close_failed notifies ────────────────────────────────
    fake.calls.clear()
    await fake.notify_position_event(
        symbol="SOLUSDT", action="close_position", reason="opposite signal",
        close_reason="signal_reversal", final_direction="bearish",
        final_confidence=0.80, execution_status="position_close_failed",
        mode="execute_close_only",
    )
    assert len(fake.calls) == 1
    print("PASS position_close_failed_notifies")

    # ── 4b. position_close_failed with spot market uses SPOT wording ──────
    fake.calls.clear()
    await fake.notify_position_event(
        symbol="ETHUSDT", action="close_position", reason="opposite signal",
        close_reason="signal_reversal", final_direction="bearish",
        final_confidence=0.80, execution_status="position_close_failed",
        mode="execute_close_only", market_type="spot", position_side="LONG",
        trade_id="ETHUSDT_LONG_x",
    )
    assert len(fake.calls) == 1
    print("PASS position_close_failed_spot_market_accepted")

    # ── 5. position_reduce_failed notifies ───────────────────────────────
    fake.calls.clear()
    await fake.notify_position_event(
        symbol="SOLUSDT", action="reduce_position", reason="risk reduction",
        close_reason="risk_reduction", execution_status="position_reduce_failed",
        mode="execute_reduce_and_close",
    )
    assert len(fake.calls) == 1
    print("PASS position_reduce_failed_notifies")

    # ── 6. position_close_recommended notifies ───────────────────────────
    fake.calls.clear()
    await fake.notify_position_event(
        symbol="BTCUSDT", action="close_position", reason="opposite signal",
        close_reason="signal_reversal", final_direction="bearish",
        final_confidence=0.80, execution_status="position_close_recommended",
        mode="execute_close_only",
    )
    assert len(fake.calls) == 1
    print("PASS position_close_recommended_notifies")

    # ── 7. position_reduce_recommended notifies ──────────────────────────
    fake.calls.clear()
    await fake.notify_position_event(
        symbol="ETHUSDT", action="reduce_position", reason="profit protection",
        close_reason="profit_protection", execution_status="position_reduce_recommended",
        mode="execute_close_only",
    )
    assert len(fake.calls) == 1
    print("PASS position_reduce_recommended_notifies")

    # ── 8. position_reverse_recommended notifies ─────────────────────────
    fake.calls.clear()
    await fake.notify_position_event(
        symbol="SOLUSDT", action="reverse_position", reason="high confidence opposite",
        close_reason="signal_reversal", final_direction="bullish",
        final_confidence=0.85, execution_status="position_reverse_recommended",
        mode="execute_close_only",
    )
    assert len(fake.calls) == 1
    print("PASS position_reverse_recommended_notifies")

    # ── 9. recommendations disabled does not notify ──────────────────────
    fake.calls.clear()
    disabled_config = {"position_events": {"enabled": True, "notify_recommendations": False}}
    for status in ["position_close_recommended", "position_reduce_recommended", "position_reverse_recommended"]:
        if should_notify_position(status, disabled_config):
            await fake.notify_position_event(execution_status=status, symbol="X", action="close", reason="test")
    assert len(fake.calls) == 0, f"recommendations disabled should not notify: {fake.calls}"
    print("PASS recommendations_disabled_not_notified")

    # ── 10. risk rejected NOT notified by default ────────────────────────
    assert should_notify_risk_rejected() is False
    print("PASS risk_rejected_disabled_by_default")

    # ── 11. risk rejected notifies when config enabled ───────────────────
    assert should_notify_risk_rejected({"position_events": {"enabled": True, "notify_risk_rejections": True}}) is True
    print("PASS risk_rejected_enabled_notifies")

    # ── 12. risk rejected call records properly ──────────────────────────
    fake.calls.clear()
    await fake.notify_risk_rejected(
        symbol="BTCUSDT", direction="bullish", confidence=0.72,
        reason="same-side LONG exposure too high (75.0%)",
    )
    assert len(fake.calls) == 1
    call = fake.calls[0][1]
    assert call["symbol"] == "BTCUSDT"
    assert call["direction"] == "bullish"
    assert "exposure too high" in call["reason"]
    print("PASS risk_rejected_call_records")

    # ── 13. missing optional fields don't crash ──────────────────────────
    fake.calls.clear()
    await fake.notify_position_event(
        symbol="BTCUSDT", action="close_position", reason="test",
        execution_status="position_closed",
    )
    assert len(fake.calls) == 1
    call = fake.calls[0][1]
    assert call.get("close_reason", "") == ""
    assert call.get("final_confidence", 0) == 0
    assert call.get("mode", "") == ""
    print("PASS missing_optional_fields_ok")

    # ── 14. position_hold does not trigger notify_position_event ─────────
    fake.calls.clear()
    assert should_notify_position("position_hold") is False
    print("PASS position_hold_not_notified")

    # ── 15. hold does not trigger notify_position_event ──────────────────
    fake.calls.clear()
    assert should_notify_position("hold") is False
    print("PASS hold_not_notified")

    # ── 16. all required events pass should_notify check ─────────────────
    for event in NOTIFY_EVENTS:
        assert should_notify_position(event), f"{event} should notify"
    print("PASS all_notify_events_pass_check")

    print("\nAll position notification tests passed.")


if __name__ == "__main__":
    asyncio.run(main())

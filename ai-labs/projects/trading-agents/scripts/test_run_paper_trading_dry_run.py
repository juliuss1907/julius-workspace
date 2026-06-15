#!/usr/bin/env python3
"""Runtime dry-run safety tests for scripts/run_paper_trading.py.

These tests import the real runtime script under the project venv and verify
that ``TradingSystem(dry_run=True)`` does not start Telegram, reconcile,
mutate positions, or write production state.  They intentionally use the real
 TradingSystem class with spies/monkeypatches rather than reimplementing logic.
"""
import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from scripts.run_paper_trading import (
    TradingSystem,
    _DryRunNotifier,
    _DryRunTelegramBot,
)


ERRORS = []


def assert_true(cond, msg=""):
    if not cond:
        ERRORS.append(msg or "assertion failed")


def assert_eq(a, b, msg=""):
    if a != b:
        ERRORS.append(msg or f"expected {b!r}, got {a!r}")


def _fake_final_signal():
    direction = MagicMock()
    direction.value = "bullish"
    return SimpleNamespace(
        direction=direction,
        confidence=0.95,
        analysis={"indicators": {"atr": 100.0}},
    )


def test_trading_system_accepts_dry_run_flag():
    system = TradingSystem(dry_run=True)
    assert_true(system.dry_run is True, "dry_run flag not stored on TradingSystem")
    assert_true(
        isinstance(system.telegram_bot, _DryRunTelegramBot),
        "dry_run did not use null Telegram bot",
    )
    assert_true(
        isinstance(system.notifier, _DryRunNotifier),
        "dry_run did not use null notifier",
    )


def test_dry_run_uses_dry_run_execution_mode():
    system = TradingSystem(dry_run=True)
    assert_eq(system.position_execution_mode, "dry_run")


def test_dry_run_disables_reconciliation():
    system = TradingSystem(dry_run=True)
    assert_true(system.recon_enabled is False, "dry_run did not force recon_enabled=False")
    assert_true(system.reconciler is None, "dry_run instantiated reconciler")


def test_dry_run_telegram_bot_start_stop_are_noops():
    async def _run():
        bot = _DryRunTelegramBot()
        await bot.start()
        assert_true(bot.is_paused is False, "dry-run bot is_paused mutated")
        await bot.stop()

    asyncio.run(_run())


def test_dry_run_notifier_methods_are_noops():
    async def _run():
        notifier = _DryRunNotifier()
        await notifier.notify_risk_rejected(symbol="BTCUSDT")
        await notifier.notify_trade_opened(trade_result=None)
        await notifier.notify_position_event(symbol="BTCUSDT", action="close_position")
        await notifier.notify_error("err", "ctx")
        await notifier.send_daily_summary(stats={})
        await notifier._send_message("msg")
        await notifier.close()

    asyncio.run(_run())


def test_dry_run_record_signal_does_not_call_signal_recorder():
    system = TradingSystem(dry_run=True)
    with patch("scripts.run_paper_trading.signal_recorder") as mock_recorder:
        system._record_signal(
            symbol="BTCUSDT",
            execution_status="dry_run_entry_recommended",
            position_decision={"action": "open_long"},
            risk_decision={"approved": True, "reason": "ok"},
        )
    assert_true(
        not mock_recorder.record_signal.called,
        "dry_run _record_signal called signal_recorder.record_signal",
    )


def test_normal_record_signal_calls_signal_recorder():
    system = TradingSystem(dry_run=False)
    with patch("scripts.run_paper_trading.signal_recorder") as mock_recorder:
        system._record_signal(
            symbol="BTCUSDT",
            execution_status="hold",
        )
    assert_true(
        mock_recorder.record_signal.called,
        "normal _record_signal did not call signal_recorder.record_signal",
    )


def test_dry_run_position_action_close_does_not_close():
    async def _run():
        system = TradingSystem(dry_run=True)
        system.order_manager.close_position = AsyncMock()
        system.order_manager.close_position_group = AsyncMock()
        system.notifier.notify_position_event = AsyncMock()

        decision = SimpleNamespace(
            action="close_position",
            position_decision={
                "position": {"trade_id": "t1", "quantity": 1.0},
                "close_reason": "signal_reversal",
            },
            market_snapshot={"last_close": 70000.0},
            final_signal=_fake_final_signal(),
            analyst_signals={},
            draft_signal=None,
            research_debate=None,
        )
        await system._execute_position_action("BTCUSDT", decision)

        assert_true(
            not system.order_manager.close_position.called,
            "dry_run close_position was called",
        )
        assert_true(
            not system.order_manager.close_position_group.called,
            "dry_run close_position_group was called",
        )
        assert_true(
            system.notifier.notify_position_event.called,
            "dry_run did not notify position event",
        )

    asyncio.run(_run())


def test_dry_run_position_action_reduce_does_not_reduce():
    async def _run():
        system = TradingSystem(dry_run=True)
        system.order_manager.reduce_position = AsyncMock()
        system.notifier.notify_position_event = AsyncMock()

        decision = SimpleNamespace(
            action="reduce_position",
            position_decision={
                "position": {"trade_id": "t1"},
                "close_fraction": 0.5,
                "close_reason": "risk_reduction",
            },
            market_snapshot={"last_close": 70000.0},
            final_signal=_fake_final_signal(),
            analyst_signals={},
            draft_signal=None,
            research_debate=None,
        )
        await system._execute_position_action("BTCUSDT", decision)

        assert_true(
            not system.order_manager.reduce_position.called,
            "dry_run reduce_position was called",
        )

    asyncio.run(_run())


def test_dry_run_position_action_reverse_does_not_close_or_execute():
    async def _run():
        system = TradingSystem(dry_run=True)
        system.order_manager.close_position = AsyncMock()
        system.order_manager.execute_signal = AsyncMock()
        system.order_manager.get_all_positions = AsyncMock(return_value=[])
        system.order_manager.get_portfolio_stats = AsyncMock(return_value={})
        system.risk_manager.evaluate = AsyncMock(return_value={"approved": True, "reason": "ok"})
        system.notifier.notify_position_event = AsyncMock()

        fake_plan = SimpleNamespace(
            should_close=True,
            should_rerun_risk=True,
            should_open_reverse=True,
            trade_id="t1",
            pre_close_status=None,
            post_close_status=None,
            reason="full reverse requested",
        )

        with patch("scripts.run_paper_trading.plan_guarded_reverse", return_value=fake_plan):
            decision = SimpleNamespace(
                action="reverse_position",
                position_decision={"position": {"trade_id": "t1"}},
                market_snapshot={"last_close": 70000.0},
                final_signal=_fake_final_signal(),
                analyst_signals={},
                draft_signal=None,
                research_debate=None,
            )
            await system._execute_position_action("BTCUSDT", decision)

        assert_true(
            not system.order_manager.close_position.called,
            "dry_run reverse close_position was called",
        )
        assert_true(
            not system.order_manager.execute_signal.called,
            "dry_run reverse execute_signal was called",
        )

    asyncio.run(_run())


def test_dry_run_guarded_reverse_does_not_close_or_open():
    async def _run():
        system = TradingSystem(dry_run=True)
        system.order_manager.close_position = AsyncMock()
        system.order_manager.execute_signal = AsyncMock()
        system.order_manager.get_all_positions = AsyncMock(return_value=[])
        system.order_manager.get_portfolio_stats = AsyncMock(return_value={})
        system.risk_manager.evaluate = AsyncMock(return_value={"approved": True, "reason": "ok"})

        fake_plan = SimpleNamespace(
            should_close=True,
            should_rerun_risk=True,
            should_open_reverse=True,
            trade_id="t1",
            pre_close_status=None,
            post_close_status=None,
            reason="full reverse requested",
        )

        with patch("scripts.run_paper_trading.plan_guarded_reverse", return_value=fake_plan):
            status, result, risk_decision = await system._execute_guarded_reverse(
                symbol="BTCUSDT",
                final_signal=_fake_final_signal(),
                position_decision={"position": {"trade_id": "t1"}},
                close_reason=MagicMock(),
                base_market_snapshot={"last_close": 70000.0},
                draft_signal=None,
                analyst_signals={},
                research_debate=None,
            )

        assert_true(
            status.startswith("dry_run"),
            f"dry_run guarded reverse status was {status!r}",
        )
        assert_true(
            not system.order_manager.close_position.called,
            "dry_run guarded reverse close_position was called",
        )
        assert_true(
            not system.order_manager.execute_signal.called,
            "dry_run guarded reverse execute_signal was called",
        )

    asyncio.run(_run())


def test_dry_run_run_cycle_skips_snapshot_and_monitor():
    async def _run():
        system = TradingSystem(dry_run=True)
        system.watchlist = []  # avoid heavy analysis in unit test
        system.monitor_positions = AsyncMock()
        system.order_manager.get_portfolio_stats = AsyncMock(return_value={
            "spot_balance": 1000.0,
            "futures_balance": 500.0,
        })
        system.runtime_health.record_cycle = MagicMock()

        with patch("scripts.run_paper_trading.db.save_portfolio_snapshot") as mock_save:
            await system.run_cycle()

        assert_true(
            not system.monitor_positions.called,
            "dry_run run_cycle called monitor_positions",
        )
        assert_true(
            not mock_save.called,
            "dry_run run_cycle saved portfolio snapshot",
        )
        assert_true(
            not system.runtime_health.record_cycle.called,
            "dry_run run_cycle recorded runtime health",
        )

    asyncio.run(_run())


def test_dry_run_run_single_cycle_skips_health_and_lock():
    async def _run():
        system = TradingSystem(dry_run=True)
        system.initialize = AsyncMock()
        system.shutdown = AsyncMock()
        system.run_cycle = AsyncMock()
        system.runtime_health.mark_running = MagicMock()
        system.runtime_health.mark_stopped = MagicMock()

        await system.run_single_cycle()

        assert_true(
            not system.runtime_health.mark_running.called,
            "dry_run run_single_cycle marked health running",
        )
        assert_true(
            not system.runtime_health.mark_stopped.called,
            "dry_run run_single_cycle marked health stopped",
        )
        assert_true(system.run_cycle.called, "dry_run run_single_cycle did not run cycle")

    asyncio.run(_run())


def run_tests():
    tests = [
        ("trading_system_accepts_dry_run_flag", test_trading_system_accepts_dry_run_flag),
        ("dry_run_uses_dry_run_execution_mode", test_dry_run_uses_dry_run_execution_mode),
        ("dry_run_disables_reconciliation", test_dry_run_disables_reconciliation),
        ("dry_run_telegram_bot_start_stop_are_noops", test_dry_run_telegram_bot_start_stop_are_noops),
        ("dry_run_notifier_methods_are_noops", test_dry_run_notifier_methods_are_noops),
        ("dry_run_record_signal_does_not_call_signal_recorder", test_dry_run_record_signal_does_not_call_signal_recorder),
        ("normal_record_signal_calls_signal_recorder", test_normal_record_signal_calls_signal_recorder),
        ("dry_run_position_action_close_does_not_close", test_dry_run_position_action_close_does_not_close),
        ("dry_run_position_action_reduce_does_not_reduce", test_dry_run_position_action_reduce_does_not_reduce),
        ("dry_run_position_action_reverse_does_not_close_or_execute", test_dry_run_position_action_reverse_does_not_close_or_execute),
        ("dry_run_guarded_reverse_does_not_close_or_open", test_dry_run_guarded_reverse_does_not_close_or_open),
        ("dry_run_run_cycle_skips_snapshot_and_monitor", test_dry_run_run_cycle_skips_snapshot_and_monitor),
        ("dry_run_run_single_cycle_skips_health_and_lock", test_dry_run_run_single_cycle_skips_health_and_lock),
    ]

    all_errors = []
    passed = 0
    for name, fn in tests:
        ERRORS.clear()
        try:
            fn()
            if ERRORS:
                for err in ERRORS:
                    all_errors.append(f"{name}: {err}")
                    print(f"FAIL {name}: {err}")
            else:
                print(f"PASS {name}")
                passed += 1
        except Exception as exc:
            all_errors.append(f"{name}: {exc}")
            print(f"FAIL {name}: {exc}")

    if all_errors:
        print(f"\n{len(all_errors)} FAILURES:")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print(f"\nAll {passed} dry-run tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_tests())

#!/usr/bin/env python3
"""
Main Trading Loop - Paper Trading

Consumes shared analysis orchestration (orchestration.analyze_symbol)
and layers on demo-policy decisions via RiskManager/PositionManager/OrderManager.
"""
import asyncio
import argparse
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def _build_parser() -> argparse.ArgumentParser:
    """Build parser before heavy runtime imports so --help stays usable."""
    parser = argparse.ArgumentParser(description='Trading System')
    parser.add_argument('--single-cycle', action='store_true',
                       help='Run single cycle and exit')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without Telegram startup/messages, position mutations, or production state writes',
    )
    return parser


if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
    _build_parser().parse_args()
    sys.exit(0)

from dotenv import load_dotenv
load_dotenv()

from utils import setup_logging, get_logger, config
from utils.watchlist import load_runtime_watchlist
from utils.process_lock import ProcessLock, LockHeldError
from dataflows import data_manager
from agents import RiskManager, PositionManager
from trading import OrderManager, PositionMonitor, TradeNotifier
from trading.base_trader import CloseReason
from telegram_bot import TradingTelegramBot
from state import PortfolioContextBuilder, signal_recorder, db
from state.runtime_health import RuntimeHealth
from state.reconciliation import FuturesReconciler
from state.entry_guard import EntryGuard
from orchestration import analyze_symbol
from policies.demo_execution import build_demo_execution_decision
from policies.reverse_planner import plan_guarded_reverse


setup_logging("INFO")
logger = get_logger(__name__)


class _DryRunTelegramBot:
    """Null Telegram bot used in dry-run mode."""

    is_paused = False

    async def start(self):
        logger.info("DRY-RUN: skipped Telegram bot start")

    async def stop(self):
        logger.info("DRY-RUN: skipped Telegram bot stop")


class _DryRunNotifier:
    """Null notifier used in dry-run mode."""

    async def notify_risk_rejected(self, *args, **kwargs):
        logger.info("DRY-RUN: risk rejected notification suppressed")

    async def notify_trade_opened(self, *args, **kwargs):
        logger.info("DRY-RUN: trade opened notification suppressed")

    async def notify_trade_closed(self, *args, **kwargs):
        logger.info("DRY-RUN: trade closed notification suppressed")

    async def notify_position_event(self, *args, **kwargs):
        logger.info("DRY-RUN: position event notification suppressed")

    async def notify_error(self, *args, **kwargs):
        logger.info("DRY-RUN: error notification suppressed")

    async def send_daily_summary(self, *args, **kwargs):
        logger.info("DRY-RUN: daily summary suppressed")

    async def _send_message(self, *args, **kwargs):
        logger.info("DRY-RUN: message suppressed")

    async def close(self):
        pass


class TradingSystem:
    """Main trading system orchestrator"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.running = False
        # Execution-side components (analysts are created per-cycle by
        # the shared orchestration layer).
        self.risk_manager = RiskManager()
        self.position_manager = PositionManager()
        self.portfolio_context_builder = PortfolioContextBuilder()
        if self.dry_run:
            self.notifier = _DryRunNotifier()
            logger.info("DRY-RUN mode enabled: Telegram bot and notifier are no-ops")
        else:
            self.notifier = TradeNotifier()
        self.order_manager = OrderManager(notifier=self.notifier)
        self.position_monitor = PositionMonitor()
        if self.dry_run:
            self.telegram_bot = _DryRunTelegramBot()
        else:
            self.telegram_bot = TradingTelegramBot(self.order_manager, self.position_monitor)

        # Load config
        default_config = config.load_default_params()
        demo_config = default_config.get('demo_trading', {})
        self.check_interval = demo_config.get('auto_execute', {}).get('check_interval_seconds', 3600)
        pm_config = default_config.get('position_manager', {})
        self.position_execution_mode = pm_config.get('execution_mode', 'execute_close_only')
        if self.dry_run:
            self.position_execution_mode = "dry_run"
            logger.info("DRY-RUN: overriding position_execution_mode to 'dry_run'")
        self.reverse_enabled = pm_config.get('reverse_enabled', False)
        reverse_flow_config = pm_config.get('reverse_flow', {})
        self.min_confidence_to_open_reverse = reverse_flow_config.get('min_confidence_to_open_reverse', 0.80)
        self.rerun_risk_after_close = reverse_flow_config.get('rerun_risk_after_close', True)

        # Watchlist
        self.watchlist = load_runtime_watchlist(default_config, project_root=project_root, logger=logger)

        # Trade watchlist (subset of watchlist allowed for auto entries)
        self.trade_watchlist = list(default_config.get('trade_watchlist') or self.watchlist)

        # Entry guard (Phase 10C) — permanent policy for new entries.
        entry_guard_config = pm_config.get('entry_guard', {})
        self.entry_guard = EntryGuard(
            config=entry_guard_config,
            trade_watchlist=self.trade_watchlist,
        )
        # Attach to OrderManager (replace the placeholder we built above)
        self.order_manager._entry_guard = self.entry_guard
        if self.entry_guard.enabled:
            logger.info(
                f"Entry guard: enabled (trade_watchlist={self.trade_watchlist}, "
                f"cooldown={entry_guard_config.get('same_symbol_side_cooldown_hours', 24)}h)"
            )
        else:
            logger.info("Entry guard: disabled")

        # Reconciliation (Phase 10C)
        recon_config = default_config.get('runtime', {}).get('reconciliation', {})
        self.recon_enabled = bool(recon_config.get('enabled', False)) and not self.dry_run
        self.recon_config = recon_config
        self.reconciler: Optional[FuturesReconciler] = None
        if self.dry_run:
            logger.info("DRY-RUN: reconciliation disabled")
        elif self.recon_enabled:
            try:
                from dataflows.binance_futures_client import BinanceFuturesClient
                client = BinanceFuturesClient(
                    api_key=os.getenv('BINANCE_FUTURES_TESTNET_API_KEY'),
                    api_secret=os.getenv('BINANCE_FUTURES_TESTNET_SECRET'),
                    environment='testnet',
                )
                self.reconciler = FuturesReconciler(
                    client=client,
                    db=db,
                    qty_tolerance_pct=float(recon_config.get('qty_tolerance_pct', 0.5)),
                    price_tolerance_pct=float(recon_config.get('price_tolerance_pct', 0.5)),
                    auto_sync_orphans=bool(recon_config.get('auto_sync_orphans', True)),
                    auto_close_db_missing=bool(recon_config.get('auto_close_db_missing', True)),
                    auto_fix_qty_mismatch=bool(recon_config.get('auto_fix_qty_mismatch', False)),
                )
                logger.info("Reconciliation: enabled")
            except Exception as e:
                logger.warning(f"Reconciliation init failed, disabling: {e}")
                self.reconciler = None
        else:
            logger.info("Reconciliation: disabled (set runtime.reconciliation.enabled=true to enable)")

        # Runtime lock + health (Phase 9A.1)
        runtime_cfg = default_config.get("runtime", {}) or {}
        self.lock_path = runtime_cfg.get("lock_file", "logs/run_paper_trading.lock")
        self.health_path = runtime_cfg.get("health_file", "logs/runtime_health.json")
        self.process_lock = ProcessLock(path=self.lock_path, name="trading-runtime")
        self.runtime_health = RuntimeHealth(path=self.health_path, name="trading-runtime")

    def _record_signal(self, **kwargs):
        """Record a signal.  In dry-run mode, log a summary instead of writing production state."""
        if self.dry_run:
            symbol = kwargs.get("symbol", "?")
            status = kwargs.get("execution_status", "?")
            position_decision = kwargs.get("position_decision") or {}
            risk_decision = kwargs.get("risk_decision") or {}
            logger.info(
                "DRY-RUN decision summary: symbol=%s status=%s position_action=%s risk_approved=%s reason=%s",
                symbol,
                status,
                position_decision.get("action") or position_decision.get("recommended_action"),
                risk_decision.get("approved") if isinstance(risk_decision, dict) else None,
                position_decision.get("reason") or (
                    risk_decision.get("reason") if isinstance(risk_decision, dict) else None
                ),
            )
            return
        signal_recorder.record_signal(**kwargs)

    async def initialize(self):
        """Initialize all components"""
        logger.info("Initializing trading system...")

        await data_manager.initialize()
        await self.risk_manager.initialize()
        await self.position_manager.initialize()
        await self.order_manager.initialize()
        await self.position_monitor.initialize()
        await self.telegram_bot.start()

        logger.info("✓ Trading system initialized")

    async def shutdown(self):
        """Shutdown all components"""
        logger.info("Shutting down trading system...")

        await self.telegram_bot.stop()
        await self.risk_manager.close()
        await self.position_manager.close()
        await self.order_manager.close()
        await self.position_monitor.close()
        await self.notifier.close()
        await data_manager.close()

        logger.info("✓ Trading system shutdown")

    async def analyze_and_trade(self, symbol: str):
        """Analyze symbol via shared orchestration, then execute via demo policy."""
        try:
            if self.telegram_bot.is_paused:
                logger.info(f"Trading paused, skipping analysis for {symbol}")
                return

            # ── shared analysis (orchestration) ──────────────────────
            try:
                bundle = await analyze_symbol(symbol, _data_manager=data_manager)
            except RuntimeError as e:
                logger.error(f"Analysis failed for {symbol}: {e}")
                return

            analysis = bundle.final
            final_signal = bundle.raw_final
            analyst_signals = bundle.raw_signals
            draft_signal = bundle.raw_draft
            research_debate = analysis.research_debate

            # ── logging ─────────────────────────────────────────────
            ta = analysis.analyst_signals
            trader_analysis = final_signal.analysis.get("trader", {})
            final_action = analysis.action
            hold_reason = analysis.hold_reason
            research_consensus = research_debate.get("consensus") if research_debate else None
            research_adjustment = research_debate.get("confidence_adjustment", 0.0) if research_debate else 0.0
            research_winner = research_debate.get("winner") if research_debate else None

            logger.info(
                f"{symbol}: Tech={ta['technical'].direction} S:{ta['technical'].score:.3f} C:{ta['technical'].confidence:.3f} | "
                f"News={ta['news'].direction} S:{ta['news'].score:.3f} C:{ta['news'].confidence:.3f} | "
                f"Sent={ta['sentiment'].direction} S:{ta['sentiment'].score:.3f} C:{ta['sentiment'].confidence:.3f} | "
                f"Fund={ta['fundamentals'].direction} S:{ta['fundamentals'].score:.3f} C:{ta['fundamentals'].confidence:.3f} | "
                f"Deriv={ta['derivatives'].direction} S:{ta['derivatives'].score:.3f} C:{ta['derivatives'].confidence:.3f} | "
                f"Final={analysis.direction} Action={final_action} S:{analysis.final_signal.score:.3f} C:{analysis.confidence:.3f}"
            )
            if research_consensus:
                logger.info(
                    f"{symbol}: Research={research_consensus} Adj:{research_adjustment:+.2f} "
                    f"Winner:{research_winner}"
                )
            if hold_reason:
                logger.info(f"{symbol}: HOLD reason: {hold_reason}")

            # ── demo policy evaluation ──────────────────────────────
            open_positions = await self.order_manager.get_all_positions()
            portfolio_stats = await self.order_manager.get_portfolio_stats()

            decision = await build_demo_execution_decision(
                bundle=bundle,
                risk_manager=self.risk_manager,
                position_manager=self.position_manager,
                portfolio_context_builder=self.portfolio_context_builder,
                open_positions=open_positions,
                portfolio_stats=portfolio_stats,
                current_prices={symbol: analysis.market_snapshot.get("last_close")},
                execution_mode=self.position_execution_mode,
            )

            market_snapshot = dict(analysis.market_snapshot)

            # ── route by decision ───────────────────────────────────

            # Position actions: close / reduce / reverse existing positions
            if decision.action in ("close_position", "reduce_position", "reverse_position"):
                await self._execute_position_action(symbol, decision)
                return

            # Skip / hold: neutral signal, explicit position hold, risk rejection, or blocked
            if not decision.approved:
                is_risk_rejection = bool(
                    decision.risk_decision
                    and decision.action != "hold"
                    and not decision.risk_decision.get("approved", False)
                )
                if is_risk_rejection:
                    await self.notifier.notify_risk_rejected(
                        symbol=symbol,
                        direction=final_signal.direction.value,
                        confidence=final_signal.confidence,
                        reason=decision.reason,
                    )
                self._record_signal(
                    symbol=symbol,
                    analyst_signals=analyst_signals,
                    draft_signal=draft_signal,
                    final_signal=final_signal,
                    research_debate=research_debate,
                    market_snapshot=market_snapshot,
                    position_decision=decision.position_decision,
                    risk_decision=decision.risk_decision,
                    execution_status="risk_rejected" if is_risk_rejection else "hold",
                )
                return

            # Open / new entry — gate by execution mode
            if self.position_execution_mode == "execute_close_only":
                logger.info(f"{symbol}: New entry blocked by execution_mode=execute_close_only")
                self._record_signal(
                    symbol=symbol,
                    analyst_signals=analyst_signals,
                    draft_signal=draft_signal,
                    final_signal=final_signal,
                    research_debate=research_debate,
                    market_snapshot=market_snapshot,
                    position_decision=decision.position_decision,
                    risk_decision=decision.risk_decision,
                    execution_status="entry_blocked_close_only",
                )
                return
            if self.dry_run or self.position_execution_mode == "dry_run":
                logger.info(f"{symbol}: New entry in dry_run mode, recording signal only")
                self._record_signal(
                    symbol=symbol,
                    analyst_signals=analyst_signals,
                    draft_signal=draft_signal,
                    final_signal=final_signal,
                    research_debate=research_debate,
                    market_snapshot=market_snapshot,
                    position_decision=decision.position_decision,
                    risk_decision=decision.risk_decision,
                    execution_status="dry_run_entry_recommended",
                )
                return

            # Execute new trade
            if final_signal.confidence >= self.order_manager.min_confidence:
                ticker = await data_manager.get_ticker(symbol)
                if not ticker:
                    logger.error(f"Could not get ticker for {symbol}")
                    return
                current_price = ticker["price"]
                atr = final_signal.analysis.get("indicators", {}).get("atr", 0)
                result = await self.order_manager.execute_signal(
                    final_signal, current_price, atr,
                    risk_decision=decision.risk_decision,
                )
                self._record_signal(
                    symbol=symbol,
                    analyst_signals=analyst_signals,
                    draft_signal=draft_signal,
                    final_signal=final_signal,
                    research_debate=research_debate,
                    market_snapshot={
                        **market_snapshot,
                        "ticker": ticker,
                        "atr": atr,
                    },
                    position_decision=decision.position_decision,
                    risk_decision=decision.risk_decision,
                    trade_result=result,
                    execution_status="executed" if result and result.success else "execution_failed",
                )
                if result and result.success:
                    await self.notifier.notify_trade_opened(result)
                    logger.info(f"✓ Trade executed: {result.trade_id}")
            else:
                logger.info(
                    f"{symbol}: Final confidence {final_signal.confidence:.3f} below "
                    f"threshold {self.order_manager.min_confidence:.3f}, skipping"
                )
                self._record_signal(
                    symbol=symbol,
                    analyst_signals=analyst_signals,
                    draft_signal=draft_signal,
                    final_signal=final_signal,
                    research_debate=research_debate,
                    market_snapshot=market_snapshot,
                    position_decision=decision.position_decision,
                    risk_decision=decision.risk_decision,
                    execution_status="below_confidence_threshold",
                )

        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}", exc_info=True)
            await self.notifier.notify_error(str(e), f"Analyzing {symbol}")

    async def _execute_position_action(self, symbol: str, decision):
        """Execute a position action (close / reduce / reverse) from a policy decision."""
        position_decision = decision.position_decision or {}
        position_action = decision.action
        base_market_snapshot = decision.market_snapshot
        final_signal = decision.final_signal
        analyst_signals = decision.analyst_signals
        draft_signal = decision.draft_signal
        research_debate = decision.research_debate

        logger.info(f"{symbol}: Position action={position_action} reason={position_decision.get('reason')}")
        execution_status = "position_hold"
        close_reason_str = position_decision.get("close_reason", "manual")
        close_reason_map = {
            "signal_reversal": CloseReason.SIGNAL_REVERSAL,
            "risk_reduction": CloseReason.RISK_REDUCTION,
            "loss_control": CloseReason.LOSS_CONTROL,
            "profit_protection": CloseReason.PROFIT_PROTECTION,
        }
        close_reason = close_reason_map.get(close_reason_str, CloseReason.MANUAL)
        reverse_risk_decision = None
        reverse_trade_result = None

        if position_action == "close_position":
            if self.dry_run or self.position_execution_mode == "dry_run":
                execution_status = "dry_run_position_close_recommended"
            else:
                position = position_decision.get("position", {})
                trade_id = position.get("trade_id")
                group_id = position.get("position_group_id")
                if group_id:
                    closed = await self.order_manager.close_position_group(group_id, reason=close_reason)
                else:
                    closed = await self.order_manager.close_position(trade_id, reason=close_reason) if trade_id else False
                execution_status = "position_closed" if closed else "position_close_failed"
        elif position_action == "reduce_position":
            if self.dry_run:
                execution_status = "dry_run_position_reduce_recommended"
            else:
                allowed = self.position_execution_mode in ("execute_reduce_and_close", "execute_all")
                if not allowed:
                    execution_status = "position_reduce_recommended"
                else:
                    trade_id = position_decision.get("position", {}).get("trade_id")
                    fraction = position_decision.get("close_fraction", 0.5)
                    reduced = await self.order_manager.reduce_position(trade_id, fraction=fraction, reason=close_reason) if trade_id else False
                    execution_status = "position_reduced" if reduced else "position_reduce_failed"
        elif position_action == "reverse_position":
            if self.dry_run:
                logger.info(f"{symbol}: reverse action blocked in dry-run")
                execution_status = "dry_run_position_reverse_recommended"
            else:
                execution_status, reverse_trade_result, reverse_risk_decision = await self._execute_guarded_reverse(
                    symbol=symbol,
                    final_signal=final_signal,
                    position_decision=position_decision,
                    close_reason=close_reason,
                    base_market_snapshot=base_market_snapshot,
                    draft_signal=draft_signal,
                    analyst_signals=analyst_signals,
                    research_debate=research_debate,
                )

        notify_market_type = position_decision.get("position", {}).get("market_type", "") or ""
        notify_position_side = position_decision.get("position", {}).get("side", "") or ""
        notify_trade_id = position_decision.get("position", {}).get("trade_id", "") or ""
        notify_requested_qty = 0.0
        notify_executed_qty = 0.0
        if position_action == "close_position":
            qty = position_decision.get("position", {}).get("quantity", 0.0)
            fraction = position_decision.get("close_fraction", 1.0)
            notify_requested_qty = fraction * qty
            notify_executed_qty = notify_requested_qty

        await self.notifier.notify_position_event(
            symbol=symbol,
            action=position_action,
            reason=position_decision.get("reason", ""),
            close_reason=close_reason_str,
            final_direction=final_signal.direction.value,
            final_confidence=final_signal.confidence,
            execution_status=execution_status,
            mode=self.position_execution_mode,
            market_type=notify_market_type,
            position_side=notify_position_side,
            requested_qty=notify_requested_qty,
            executed_qty=notify_executed_qty,
            trade_id=notify_trade_id,
        )

        self._record_signal(
            symbol=symbol,
            analyst_signals=analyst_signals,
            draft_signal=draft_signal,
            final_signal=final_signal,
            research_debate=research_debate,
            market_snapshot={**base_market_snapshot},
            position_decision=position_decision,
            risk_decision=reverse_risk_decision if position_action == "reverse_position" else None,
            trade_result=reverse_trade_result if position_action == "reverse_position" else None,
            execution_status=execution_status,
        )

    async def _execute_guarded_reverse(
        self,
        symbol: str,
        final_signal,
        position_decision: dict,
        close_reason,
        base_market_snapshot: dict,
        draft_signal,
        analyst_signals: dict,
        research_debate: dict,
    ):
        """Phase 5B.4: Guarded reverse flow.

        Uses plan_guarded_reverse() from policies.reverse_planner for
        pure policy decisions.  All side effects stay in this method.

        Returns: (execution_status, trade_result_or_None, risk_decision_or_None)
        """
        if self.dry_run:
            logger.info(f"{symbol}: guarded reverse blocked in dry-run")
            return ("dry_run_position_reverse_recommended", None, None)

        plan = plan_guarded_reverse(
            reverse_enabled=self.reverse_enabled,
            execution_mode=self.position_execution_mode,
            final_confidence=final_signal.confidence,
            min_confidence_to_open_reverse=self.min_confidence_to_open_reverse,
            position_decision=position_decision,
            rerun_risk_after_close=self.rerun_risk_after_close,
        )

        if not plan.should_close:
            return ("position_reverse_recommended", None, None)

        if not plan.should_open_reverse:
            logger.info(f"{symbol}: reverse {plan.reason}")
            closed = await self.order_manager.close_position(
                plan.trade_id, reason=close_reason,
            )
            if not closed:
                return ("position_reverse_close_failed", None, None)
            return ("position_reversed_close_only", None, None)

        # ── full reverse flow ───────────────────────────────────────
        closed = await self.order_manager.close_position(
            plan.trade_id, reason=close_reason,
        )
        if not closed:
            return ("position_reverse_close_failed", None, None)

        open_positions = await self.order_manager.get_all_positions()
        portfolio_stats = await self.order_manager.get_portfolio_stats()
        portfolio_context = self.portfolio_context_builder.build(
            open_positions=open_positions,
            portfolio_stats=portfolio_stats,
            current_prices={symbol: base_market_snapshot.get("last_close")},
        )
        risk_decision = await self.risk_manager.evaluate(
            symbol=symbol,
            final_signal=final_signal,
            analyst_signals=analyst_signals,
            research_debate=research_debate,
            market_snapshot=base_market_snapshot,
            open_positions=open_positions,
            portfolio_stats=portfolio_stats,
            portfolio_context=portfolio_context,
        )
        if not risk_decision["approved"]:
            logger.info(
                f"{symbol}: reverse blocked by risk after close: {risk_decision['reason']}"
            )
            return ("position_reversed_close_only", None, risk_decision)

        ticker = await data_manager.get_ticker(symbol)
        if not ticker:
            return ("position_reverse_open_failed", None, risk_decision)

        current_price = ticker["price"]
        atr = final_signal.analysis.get("indicators", {}).get("atr", 0)
        result = await self.order_manager.execute_signal(
            final_signal, current_price, atr, risk_decision=risk_decision,
        )
        if result and result.success:
            await self.notifier.notify_trade_opened(result)
            return ("position_reversed", result, risk_decision)
        return ("position_reverse_open_failed", result, risk_decision)

    async def monitor_positions(self):
        """Monitor open positions for SL/TP triggers"""
        try:
            closed_positions = await self.position_monitor.check_positions()

            for pos in closed_positions:
                logger.info(f"Position closed: {pos['trade_id']} | PnL: ${pos['pnl']:.2f} ({pos['pnl_pct']:.2f}%)")

                # Send notification
                from trading.base_trader import ClosedPosition, TradeSide, MarketType, CloseReason
                closed = ClosedPosition(
                    trade_id=pos['trade_id'],
                    symbol=pos['symbol'],
                    side=TradeSide(pos['side']),
                    market_type=MarketType(pos['market_type']),
                    entry_price=pos['entry_price'],
                    exit_price=pos['exit_price'],
                    quantity=pos['quantity'],
                    leverage=pos['leverage'],
                    pnl=pos['pnl'],
                    pnl_pct=pos['pnl_pct'],
                    fees=pos.get('fees', 0),
                    close_reason=CloseReason(pos['close_reason']),
                    opened_at=datetime.now(),  # TODO: get from DB
                    closed_at=datetime.now(),
                    duration_seconds=0  # TODO: calculate from DB
                )

                await self.notifier.notify_trade_closed(closed)

        except Exception as e:
            logger.error(f"Error monitoring positions: {e}", exc_info=True)
            await self.notifier.notify_error(str(e), "Monitoring positions")

    async def send_daily_summary(self):
        """Send daily portfolio summary"""
        try:
            stats = await self.order_manager.get_portfolio_stats()
            await self.notifier.send_daily_summary(stats)
            logger.info("✓ Daily summary sent")
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}", exc_info=True)

    async def run_cycle(self):
        """Run one trading cycle"""
        logger.info(f"\n{'='*80}")
        logger.info(f"Trading cycle started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'='*80}\n")

        t0 = time.monotonic()
        cycle_status = "success"
        symbols_processed = 0
        cycle_error = None

        try:
            # Phase 10C: reconcile Binance vs DB before doing anything else
            if self.reconciler and self.recon_config.get('run_before_cycle', True):
                try:
                    await self._run_reconciliation_once()
                except Exception as e:
                    logger.warning(f"Reconciliation (before cycle) failed: {e}")

            if self.dry_run:
                logger.info("DRY-RUN: skipped position monitoring")
            else:
                # Always monitor existing positions (even when paused)
                await self.monitor_positions()

            # Only analyze and trade if not paused
            if not self.telegram_bot.is_paused:
                # Analyze each coin in watchlist
                for symbol in self.watchlist:
                    await self.analyze_and_trade(symbol)
                    symbols_processed += 1
            else:
                logger.info("⚠️ Trading is paused, skipping analysis")

            # Save portfolio snapshot
            if self.dry_run:
                logger.info("DRY-RUN: skipped portfolio snapshot save")
            else:
                try:
                    stats = await self.order_manager.get_portfolio_stats()
                    from state import db
                    await db.save_portfolio_snapshot(
                        spot_balance=stats['spot_balance'],
                        futures_balance=stats['futures_balance']
                    )
                except Exception as e:
                    logger.error(f"Error saving portfolio snapshot: {e}")
        except Exception as e:
            cycle_status = "failed"
            cycle_error = str(e)
            logger.error(f"Trading cycle failed: {e}", exc_info=True)

        duration = time.monotonic() - t0
        if self.dry_run:
            logger.info("DRY-RUN: skipped runtime health record_cycle")
        else:
            try:
                self.runtime_health.record_cycle(
                    status=cycle_status,
                    duration_sec=duration,
                    symbols_processed=symbols_processed,
                    error=cycle_error,
                )
            except Exception as e:
                logger.warning(f"Failed to record runtime health: {e}")

        logger.info(f"\n{'='*80}")
        logger.info(f"Trading cycle completed")
        logger.info(f"{'='*80}\n")

    async def _run_reconciliation_once(self):
        """Run a single reconciliation pass and notify on warnings."""
        if not self.reconciler:
            return
        result = await self.reconciler.reconcile_once()
        if not self.recon_config.get('notify_mismatches', True):
            return
        threshold = self.recon_config.get('notify_threshold_severity', 'warning')
        sev_rank = {'info': 0, 'warning': 1, 'high': 2}
        threshold_rank = sev_rank.get(threshold, 1)
        warn_events = [
            e for e in result.events
            if sev_rank.get(e.severity, 0) >= threshold_rank
            and e.event_type != 'ok'
        ]
        if not warn_events:
            return
        # Build a single notification summarizing the diffs
        lines = [f"⚠️ <b>Reconciliation Alert ({len(warn_events)})</b>\n"]
        for ev in warn_events[:10]:  # cap
            lines.append(
                f"  - [{ev.severity}] {ev.event_type} "
                f"{ev.symbol} {ev.side or '-'} "
                f"db_trade_id={ev.db_trade_id or '-'} "
                f"action={ev.action_taken}"
            )
        if len(warn_events) > 10:
            lines.append(f"  ... and {len(warn_events) - 10} more")
        msg = "\n".join(lines)
        try:
            await self.notifier._send_message(msg)
        except Exception as e:
            logger.warning(f"Failed to send reconciliation alert: {e}")

    async def run(self):
        """Main trading loop"""
        self.running = True

        if not self.dry_run:
            try:
                self.runtime_health.mark_running(
                    watchlist=self.watchlist, mode="continuous",
                )
            except Exception as e:
                logger.warning(f"Failed to mark runtime health: {e}")
        else:
            logger.info("DRY-RUN: skipped runtime health mark_running")

        # Initialize
        await self.initialize()

        # Send startup message
        await self.notifier._send_message(
            "🚀 <b>Trading System Started</b>\n\n"
            f"Watchlist: {', '.join(self.watchlist)}\n"
            f"Check interval: {self.check_interval}s\n"
            f"Min confidence: {self.order_manager.min_confidence}\n\n"
            "📱 <b>Telegram Bot Active</b>\n"
            "Commands: /help /status /positions /trades /pnl /close /pause /resume"
        )

        # Send initial daily summary
        await self.send_daily_summary()

        # Main loop
        cycle_count = 0
        while self.running:
            try:
                await self.run_cycle()
                cycle_count += 1

                # Send daily summary every 24 cycles (assuming 1h interval)
                if cycle_count % 24 == 0:
                    await self.send_daily_summary()

                # Wait for next cycle
                logger.info(f"Waiting {self.check_interval}s for next cycle...")
                await asyncio.sleep(self.check_interval)

            except asyncio.CancelledError:
                logger.info("Trading loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in trading loop: {e}", exc_info=True)
                await self.notifier.notify_error(str(e), "Trading loop")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

        # Shutdown
        await self.shutdown()

        # Send shutdown message
        if not self.dry_run:
            await self.notifier._send_message("🛑 <b>Trading System Stopped</b>")

        if not self.dry_run:
            try:
                self.runtime_health.mark_stopped(reason="continuous_loop_exit")
            except Exception as e:
                logger.warning(f"Failed to mark runtime health stopped: {e}")
        else:
            logger.info("DRY-RUN: skipped runtime health mark_stopped")

    def stop(self):
        """Stop the trading system"""
        logger.info("Stop signal received")
        self.running = False

    async def run_single_cycle(self):
        """Run a single trading cycle and exit"""
        logger.info("Running single trading cycle...")

        if not self.dry_run:
            try:
                self.runtime_health.mark_running(
                    watchlist=self.watchlist, mode="single_cycle",
                )
            except Exception as e:
                logger.warning(f"Failed to mark runtime health: {e}")
        else:
            logger.info("DRY-RUN: skipped runtime health mark_running")

        await self.initialize()

        try:
            await self.run_cycle()
            logger.info("✓ Single cycle completed")
        finally:
            await self.shutdown()
            if not self.dry_run:
                try:
                    self.runtime_health.mark_stopped(reason="single_cycle_complete")
                except Exception as e:
                    logger.warning(f"Failed to mark runtime health stopped: {e}")
            else:
                logger.info("DRY-RUN: skipped runtime health mark_stopped")


async def main():
    """Main entry point"""
    parser = _build_parser()
    args = parser.parse_args()

    system = TradingSystem(dry_run=args.dry_run)

    # Acquire process lock (Phase 9A.1) — skipped in dry-run mode
    if not args.dry_run:
        try:
            system.process_lock.acquire()
        except LockHeldError as e:
            holder = e.holder or {}
            logger.error(
                f"Runtime lock active: PID {holder.get('pid')} already running "
                f"(started={holder.get('started_at')}). Refusing to start duplicate process."
            )
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to acquire runtime lock: {e}")
            sys.exit(1)
    else:
        logger.info("DRY-RUN: skipped process lock acquire")

    # Setup signal handlers
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}")
        system.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    exit_code = 0
    try:
        if args.single_cycle:
            await system.run_single_cycle()
        else:
            await system.run()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        exit_code = 1
    finally:
        if not args.dry_run:
            try:
                system.process_lock.release()
            except Exception as e:
                logger.warning(f"Failed to release runtime lock: {e}")
        else:
            logger.info("DRY-RUN: skipped process lock release")

    if exit_code:
        sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())

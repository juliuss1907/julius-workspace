"""
Trading Telegram Bot
Interactive commands for monitoring and controlling the trading system
"""
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import Conflict
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from utils import get_logger, config
from state import db
from trading import OrderManager, PositionMonitor
from trading.base_trader import TradeSide, MarketType, CloseReason


logger = get_logger(__name__)


class TradingTelegramBot:
    """Telegram bot for trading system interaction"""
    
    def __init__(self, order_manager: OrderManager, position_monitor: PositionMonitor):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.order_manager = order_manager
        self.position_monitor = position_monitor
        
        # Trading control
        self.is_paused = False
        self._started = False
        
        # Build application
        self.app = Application.builder().token(self.bot_token).build()
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all command handlers"""
        # Basic commands
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("help", self.cmd_help))
        
        # Status commands
        self.app.add_handler(CommandHandler("status", self.cmd_status))
        self.app.add_handler(CommandHandler("positions", self.cmd_positions))
        self.app.add_handler(CommandHandler("trades", self.cmd_trades))
        self.app.add_handler(CommandHandler("pnl", self.cmd_pnl))
        
        # Trading commands
        self.app.add_handler(CommandHandler("close", self.cmd_close))
        self.app.add_handler(CommandHandler("pause", self.cmd_pause))
        self.app.add_handler(CommandHandler("resume", self.cmd_resume))
        
        # Config commands
        self.app.add_handler(CommandHandler("config", self.cmd_config))
        
        # Callback handler for inline keyboards
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_msg = """
🤖 <b>Trading Agent Bot</b>

Welcome to the Trading Agent monitoring system!

Use /help to see all available commands.

Current status: {'🟢 Running' if not self.is_paused else '🔴 Paused'}
        """
        await update.message.reply_text(welcome_msg, parse_mode='HTML')
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_msg = """
📋 <b>Available Commands</b>

<b>Basic:</b>
/start - Welcome message
/help - Show this help

<b>Status:</b>
/status - Portfolio overview
/positions - Open positions
/trades - Recent trades (last 10)
/pnl - PnL breakdown

<b>Trading:</b>
/close &lt;trade_id&gt; - Close a position
/pause - Pause trading
/resume - Resume trading

<b>Config:</b>
/config - Show current config
        """
        await update.message.reply_text(help_msg, parse_mode='HTML')
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        try:
            stats = await self.order_manager.get_portfolio_stats()
            
            # Calculate total PnL percentage
            initial_balance = 10000  # $10k initial
            total_balance = stats['total_balance']
            total_pnl = total_balance - initial_balance
            total_pnl_pct = (total_pnl / initial_balance) * 100
            
            # Determine emoji based on PnL
            pnl_emoji = "🟢" if total_pnl >= 0 else "🔴"
            
            status_msg = f"""
📊 <b>Portfolio Status</b>

<b>Balance:</b>
  • Spot: ${stats['spot_balance']:,.2f}
  • Futures: ${stats['futures_balance']:,.2f}
  • Total: ${total_balance:,.2f}

<b>Positions:</b>
  • Open: {stats['open_positions']}
  • Total Trades: {stats['total_trades']}

<b>Performance:</b>
  {pnl_emoji} Total PnL: ${total_pnl:+,.2f} ({total_pnl_pct:+.2f}%)
  • Avg PnL/Trade: {stats['avg_pnl_pct']:+.2f}%

<b>System:</b>
  • Status: {'🟢 Running' if not self.is_paused else '🔴 Paused'}
            """
            
            await update.message.reply_text(status_msg, parse_mode='HTML')
        
        except Exception as e:
            logger.error(f"Error in /status command: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def cmd_positions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /positions command"""
        try:
            positions = await self.order_manager.get_all_positions()
            
            if not positions:
                await update.message.reply_text("📭 No open positions")
                return
            
            # Build positions message
            positions_msg = f"📈 <b>Open Positions ({len(positions)})</b>\n\n"
            
            for pos in positions:
                # Calculate current PnL (simplified)
                entry_price = pos['entry_price']
                quantity = pos['quantity']
                side = pos['side']
                leverage = pos.get('leverage', 1.0)
                
                # Get current price (simplified - would need to fetch from API)
                # For now, just show entry info
                emoji = "🟢" if side == "LONG" else "🔴"
                market_emoji = "📊" if pos['market_type'] == "spot" else "⚡"
                
                positions_msg += f"""
{emoji} <b>{pos['symbol']}</b> {market_emoji}
  • Side: {side}
  • Entry: ${entry_price:,.2f}
  • Qty: {quantity:.6f}
  • Leverage: {leverage:.1f}x
  • SL: ${pos.get('stop_loss', 0):,.2f}
  • TP: ${pos.get('take_profit', 0):,.2f}
  • Trade ID: <code>{pos['trade_id']}</code>

                """
            
            # Split into chunks if too long (Telegram limit: 4096 chars)
            if len(positions_msg) > 4000:
                # Send in chunks
                chunks = [positions_msg[i:i+4000] for i in range(0, len(positions_msg), 4000)]
                for chunk in chunks:
                    await update.message.reply_text(chunk, parse_mode='HTML')
            else:
                await update.message.reply_text(positions_msg, parse_mode='HTML')
        
        except Exception as e:
            logger.error(f"Error in /positions command: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def cmd_trades(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /trades command"""
        try:
            # Get last 10 trades
            trades = await db.get_paper_trades(limit=10)
            
            if not trades:
                await update.message.reply_text("📭 No trades yet")
                return
            
            trades_msg = f"📜 <b>Recent Trades (Last {len(trades)})</b>\n\n"
            
            for trade in trades:
                # Determine emoji based on PnL
                pnl = trade['pnl']
                pnl_emoji = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
                
                # Calculate duration
                duration_seconds = trade['duration_seconds']
                if duration_seconds < 3600:
                    duration = f"{duration_seconds // 60}m"
                elif duration_seconds < 86400:
                    duration = f"{duration_seconds // 3600}h"
                else:
                    duration = f"{duration_seconds // 86400}d"
                
                trades_msg += f"""
{pnl_emoji} <b>{trade['symbol']}</b>
  • Side: {trade['side']}
  • Entry: ${trade['entry_price']:,.2f}
  • Exit: ${trade['exit_price']:,.2f}
  • PnL: ${pnl:+,.2f} ({trade['pnl_pct']:+.2f}%)
  • Duration: {duration}
  • Reason: {trade['close_reason']}
  • Date: {trade['closed_at']}

                """
            
            await update.message.reply_text(trades_msg, parse_mode='HTML')
        
        except Exception as e:
            logger.error(f"Error in /trades command: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def cmd_pnl(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pnl command"""
        try:
            stats = await db.get_portfolio_stats()
            
            # Calculate metrics
            total_trades = stats['total_trades']
            total_pnl = stats['total_pnl']
            avg_pnl_pct = stats['avg_pnl_pct']
            
            # Get win/loss count (need to query separately)
            # For now, just show basic stats
            pnl_emoji = "🟢" if total_pnl >= 0 else "🔴"
            
            pnl_msg = f"""
💰 <b>PnL Breakdown</b>

<b>Overall:</b>
  {pnl_emoji} Total PnL: ${total_pnl:+,.2f}
  • Avg PnL/Trade: {avg_pnl_pct:+.2f}%
  • Total Trades: {total_trades}

<b>Open Positions:</b>
  • Count: {stats['open_positions_count']}

<b>Balance:</b>
  • Spot: ${stats['spot_balance']:,.2f}
  • Futures: ${stats['futures_balance']:,.2f}
  • Total: ${stats['total_balance']:,.2f}
            """
            
            await update.message.reply_text(pnl_msg, parse_mode='HTML')
        
        except Exception as e:
            logger.error(f"Error in /pnl command: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def cmd_close(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /close command"""
        try:
            # Get trade_id from args
            if not context.args:
                await update.message.reply_text(
                    "❌ Usage: /close <trade_id>\n\n"
                    "Use /positions to see trade IDs"
                )
                return
            
            trade_id = context.args[0]
            
            # Close position
            success = await self.order_manager.close_position(trade_id, CloseReason.MANUAL)
            
            if success:
                await update.message.reply_text(
                    f"✅ Position closed successfully\n"
                    f"Trade ID: <code>{trade_id}</code>",
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text(
                    f"❌ Failed to close position\n"
                    f"Trade ID: <code>{trade_id}</code>\n\n"
                    f"Position may not exist or already closed",
                    parse_mode='HTML'
                )
        
        except Exception as e:
            logger.error(f"Error in /close command: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def cmd_pause(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pause command"""
        if self.is_paused:
            await update.message.reply_text("⚠️ Trading is already paused")
            return
        
        self.is_paused = True
        await update.message.reply_text(
            "🔴 <b>Trading Paused</b>\n\n"
            "The system will stop opening new positions.\n"
            "Existing positions will still be monitored.\n\n"
            "Use /resume to continue trading.",
            parse_mode='HTML'
        )
        logger.info("Trading paused via Telegram command")
    
    async def cmd_resume(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /resume command"""
        if not self.is_paused:
            await update.message.reply_text("⚠️ Trading is already running")
            return
        
        self.is_paused = False
        await update.message.reply_text(
            "🟢 <b>Trading Resumed</b>\n\n"
            "The system will continue normal operations.",
            parse_mode='HTML'
        )
        logger.info("Trading resumed via Telegram command")
    
    async def cmd_config(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /config command"""
        try:
            default_config = config.load_default_params()
            demo_config = default_config.get('demo_trading', {})
            auto_execute = demo_config.get('auto_execute', {})
            
            config_msg = f"""
⚙️ <b>Current Configuration</b>

<b>Trading:</b>
  • Min Confidence: {auto_execute.get('min_confidence', 0.70):.2f}
  • Max Trades/Day: {auto_execute.get('max_trades_per_day', 10)}
  • Check Interval: {auto_execute.get('check_interval_seconds', 3600)}s

<b>Risk Management:</b>
  • Risk/Trade: {default_config.get('risk_management', {}).get('risk_per_trade', 0.03) * 100:.1f}%
  • Max Position Size: {default_config.get('risk_management', {}).get('max_position_size', 0.30) * 100:.0f}%
  • Max Open Positions: {default_config.get('risk_management', {}).get('max_open_positions', 5)}

<b>Stop Loss:</b>
  • Method: {default_config.get('stop_loss', {}).get('method', 'atr')}
  • ATR Multiplier: {default_config.get('stop_loss', {}).get('atr_multiplier', 2.0)}

<b>Take Profit:</b>
  • Risk/Reward: 1:{default_config.get('take_profit', {}).get('risk_reward_ratio', 2.0)}
  • Trailing Stop: {'✅' if default_config.get('take_profit', {}).get('trailing_stop', {}).get('enabled', True) else '❌'}

<b>System:</b>
  • Status: {'🟢 Running' if not self.is_paused else '🔴 Paused'}
            """
            
            await update.message.reply_text(config_msg, parse_mode='HTML')
        
        except Exception as e:
            logger.error(f"Error in /config command: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks"""
        query = update.callback_query
        await query.answer()
        
        # Handle different callback actions
        data = query.data
        
        if data == "refresh_status":
            # Refresh status
            await query.edit_message_text("Refreshing...")
            # Would need to re-fetch and update message
        elif data.startswith("close_"):
            # Close position
            trade_id = data.replace("close_", "")
            success = await self.order_manager.close_position(trade_id, CloseReason.MANUAL)
            if success:
                await query.edit_message_text(f"✅ Position closed: {trade_id}")
            else:
                await query.edit_message_text(f"❌ Failed to close: {trade_id}")
    
    async def send_message(self, text: str, parse_mode: str = 'HTML'):
        """Send a message to the configured chat"""
        try:
            await self.app.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=parse_mode
            )
            return True
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    async def start(self):
        """Start the bot"""
        logger.info("Starting Telegram bot...")
        try:
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling(drop_pending_updates=True)
            self._started = True
            logger.info("Telegram bot started")
        except Conflict as e:
            logger.warning(f"Telegram polling conflict detected, disabling bot polling: {e}")
            try:
                await self.app.stop()
            except Exception:
                pass
            try:
                await self.app.shutdown()
            except Exception:
                pass
            self._started = False
        except Exception:
            try:
                await self.app.shutdown()
            except Exception:
                pass
            raise

    async def stop(self):
        """Stop the bot"""
        logger.info("Stopping Telegram bot...")
        if not self._started:
            logger.info("Telegram bot was not polling")
            return
        await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown()
        self._started = False
        logger.info("Telegram bot stopped")

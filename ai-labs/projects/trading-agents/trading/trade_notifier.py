"""
Trade Notifier - Send trade notifications via Telegram
"""
import os
import aiohttp
from typing import Dict, Optional
from datetime import datetime
from utils import get_logger, config
from state import db
from .base_trader import TradeResult, ClosedPosition


logger = get_logger(__name__)


class TradeNotifier:
    """Send trade notifications via Telegram"""
    
    def __init__(self, config_override: Optional[Dict] = None):
        # Load config
        default_config = config.load_default_params()
        demo_config = default_config.get('demo_trading', {})
        self.config = {**demo_config.get('notify', {}), **(config_override or {})}
        notification_config = default_config.get("notifications", {})
        self.config = {**notification_config, **self.config}
        
        # Telegram settings
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        self.enabled = self.config.get('enabled', True)
        self.session = None
        
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram credentials not configured, notifications disabled")
            self.enabled = False
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _send_message(self, message: str) -> bool:
        """Send message via Telegram"""
        if not self.enabled:
            return False
        
        try:
            session = await self._get_session()
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            async with session.post(url, json=payload, timeout=10) as resp:
                if resp.status == 200:
                    return True
                else:
                    error = await resp.text()
                    logger.error(f"Telegram API error {resp.status}: {error}")
                    return False
        
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    async def notify_trade_opened(self, trade: TradeResult) -> bool:
        """Send notification when trade is opened"""
        if not self.config.get('on_trade_open', True):
            return False
        
        emoji = "🟢" if trade.side.value == "LONG" else "🔴"
        
        message = f"""
{emoji} <b>Trade Opened</b>

<b>Symbol:</b> {trade.symbol}
<b>Side:</b> {trade.side.value}
<b>Market:</b> {trade.market_type.value.upper()}
<b>Entry Price:</b> ${trade.entry_price:,.2f}
<b>Quantity:</b> {trade.quantity:.6f}
<b>Leverage:</b> {trade.leverage:.1f}x
"""
        
        if trade.stop_loss:
            message += f"<b>Stop Loss:</b> ${trade.stop_loss:,.2f}\n"
        if trade.take_profit:
            message += f"<b>Take Profit:</b> ${trade.take_profit:,.2f}\n"
        
        message += f"\n<b>Trade ID:</b> <code>{trade.trade_id}</code>"
        
        success = await self._send_message(message)
        
        # Log to database
        await db.log_notification(
            trade_id=trade.trade_id,
            notification_type='trade_opened',
            message=message,
            success=success
        )
        
        return success
    
    async def notify_trade_closed(self, closed: ClosedPosition) -> bool:
        """Send notification when trade is closed"""
        if not self.config.get('on_trade_close', True):
            return False
        
        # Determine emoji based on PnL
        if closed.pnl > 0:
            emoji = "💰"
            pnl_emoji = "🟢"
        elif closed.pnl < 0:
            emoji = "💸"
            pnl_emoji = "🔴"
        else:
            emoji = "⚪"
            pnl_emoji = "⚪"
        
        # Close reason emoji
        reason_emoji = {
            'sl_hit': '🛑',
            'tp_hit': '🎯',
            'trailing_stop': '📉',
            'manual': '✋',
            'timeout': '⏰'
        }.get(closed.close_reason.value, '❓')
        
        message = f"""
{emoji} <b>Trade Closed</b>

<b>Symbol:</b> {closed.symbol}
<b>Side:</b> {closed.side.value}
<b>Market:</b> {closed.market_type.value.upper()}

<b>Entry:</b> ${closed.entry_price:,.2f}
<b>Exit:</b> ${closed.exit_price:,.2f}
<b>Leverage:</b> {closed.leverage:.1f}x

{pnl_emoji} <b>PnL:</b> ${closed.pnl:+,.2f} ({closed.pnl_pct:+.2f}%)
<b>Fees:</b> ${closed.fees:.2f}

{reason_emoji} <b>Reason:</b> {closed.close_reason.value}
<b>Duration:</b> {self._format_duration(closed.duration_seconds)}

<b>Trade ID:</b> <code>{closed.trade_id}</code>
"""
        
        success = await self._send_message(message)
        
        # Log to database
        await db.log_notification(
            trade_id=closed.trade_id,
            notification_type='trade_closed',
            message=message,
            success=success
        )
        
        return success
    
    async def notify_sl_tp_hit(self, trade_id: str, symbol: str, reason: str, pnl: float) -> bool:
        """Send notification when SL/TP is hit"""
        if not self.config.get('on_sl_tp_hit', True):
            return False
        
        if reason == 'tp_hit':
            emoji = "🎯"
            title = "Take Profit Hit!"
        elif reason == 'sl_hit':
            emoji = "🛑"
            title = "Stop Loss Hit!"
        else:
            emoji = "📉"
            title = "Trailing Stop Hit!"
        
        pnl_emoji = "🟢" if pnl > 0 else "🔴"
        
        message = f"""
{emoji} <b>{title}</b>

<b>Symbol:</b> {symbol}
{pnl_emoji} <b>PnL:</b> ${pnl:+,.2f}

<b>Trade ID:</b> <code>{trade_id}</code>
"""
        
        success = await self._send_message(message)
        
        # Log to database
        await db.log_notification(
            trade_id=trade_id,
            notification_type='sl_tp_hit',
            message=message,
            success=success
        )
        
        return success
    
    async def send_daily_summary(self, stats: Dict) -> bool:
        """Send daily portfolio summary"""
        if not self.config.get('daily_summary', True):
            return False
        
        total_pnl = stats.get('total_pnl', 0)
        if total_pnl > 0:
            emoji = "📈"
        elif total_pnl < 0:
            emoji = "📉"
        else:
            emoji = "➡️"
        
        message = f"""
{emoji} <b>Daily Summary</b>

<b>Total Balance:</b> ${stats.get('total_balance', 0):,.2f}
  • Spot: ${stats.get('spot_balance', 0):,.2f}
  • Futures: ${stats.get('futures_balance', 0):,.2f}

<b>Open Positions:</b> {stats.get('open_positions', 0)}
<b>Total Trades:</b> {stats.get('total_trades', 0)}

<b>Total PnL:</b> ${stats.get('total_pnl', 0):+,.2f}
<b>Avg PnL %:</b> {stats.get('avg_pnl_pct', 0):+.2f}%
"""
        
        success = await self._send_message(message)
        
        # Log to database
        await db.log_notification(
            trade_id='daily_summary',
            notification_type='daily_summary',
            message=message,
            success=success
        )
        
        return success
    
    async def notify_error(self, error: str, context: str = "") -> bool:
        """Send error notification"""
        if not self.config.get('on_error', True):
            return False
        
        message = f"""
⚠️ <b>Error Alert</b>

<b>Error:</b> {error}
"""
        
        if context:
            message += f"<b>Context:</b> {context}\n"
        
        message += f"\n<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        success = await self._send_message(message)
        
        # Log to database
        await db.log_notification(
            trade_id='error',
            notification_type='error',
            message=message,
            success=success
        )
        
        return success

    async def notify_position_event(
        self,
        symbol: str,
        action: str,
        reason: str,
        close_reason: str = "",
        final_direction: str = "",
        final_confidence: float = 0.0,
        execution_status: str = "",
        mode: str = "",
        market_type: str = "",
        position_side: str = "",
        requested_qty: float = 0.0,
        executed_qty: float = 0.0,
        trade_id: str = "",
    ) -> bool:
        """Send notification for position events: closed, reduced, recommended, failed."""
        position_config = self.config.get("position_events", {})
        if not position_config.get("enabled", True):
            return False

        if execution_status == "position_closed":
            if not position_config.get("notify_closed", True):
                return False
        elif execution_status == "position_reduced":
            if not position_config.get("notify_reduced", True):
                return False
        elif execution_status in ("position_close_failed", "position_reduce_failed"):
            if not position_config.get("notify_failures", True):
                return False
        elif "recommended" in execution_status or "reversed" in execution_status:
            if not position_config.get("notify_recommendations", True):
                return False
        else:
            return False

        is_spot = (market_type or "").lower() == "spot"
        is_futures = (market_type or "").lower() == "futures"
        market_label = "Spot" if is_spot else ("Futures" if is_futures else (market_type.upper() if market_type else ""))

        spot_titles = {
            "position_closed": "SPOT SELL EXECUTED",
            "position_reduced": "SPOT SELL EXECUTED (PARTIAL)",
            "position_close_failed": "SPOT SELL FAILED",
            "position_reduce_failed": "SPOT SELL FAILED",
            "position_close_recommended": "SPOT SELL RECOMMENDED",
            "position_reduce_recommended": "SPOT SELL RECOMMENDED",
            "position_reverse_recommended": "SPOT REVERSE RECOMMENDED",
            "position_reversed": "SPOT REVERSE EXECUTED",
            "position_reversed_close_only": "SPOT REVERSE CLOSE-ONLY",
            "position_reverse_close_failed": "SPOT REVERSE CLOSE FAILED",
            "position_reverse_open_failed": "SPOT REVERSE OPEN FAILED",
        }
        futures_titles = {
            "position_closed": "FUTURES POSITION CLOSED",
            "position_reduced": "FUTURES POSITION REDUCED",
            "position_close_failed": "FUTURES CLOSE FAILED",
            "position_reduce_failed": "FUTURES REDUCE FAILED",
            "position_close_recommended": "FUTURES CLOSE RECOMMENDED",
            "position_reduce_recommended": "FUTURES REDUCE RECOMMENDED",
            "position_reverse_recommended": "FUTURES REVERSE RECOMMENDED",
            "position_reversed": "FUTURES POSITION REVERSED",
            "position_reversed_close_only": "FUTURES REVERSE CLOSE-ONLY",
            "position_reverse_close_failed": "FUTURES REVERSE CLOSE FAILED",
            "position_reverse_open_failed": "FUTURES REVERSE OPEN FAILED",
        }
        generic_titles = {
            "position_closed": "POSITION CLOSED",
            "position_reduced": "POSITION REDUCED",
            "position_close_failed": "CLOSE FAILED",
            "position_reduce_failed": "REDUCE FAILED",
            "position_close_recommended": "CLOSE RECOMMENDED",
            "position_reduce_recommended": "REDUCE RECOMMENDED",
            "position_reverse_recommended": "REVERSE RECOMMENDED",
            "position_reversed": "POSITION REVERSED",
            "position_reversed_close_only": "REVERSE CLOSE-ONLY",
            "position_reverse_close_failed": "REVERSE CLOSE FAILED",
            "position_reverse_open_failed": "REVERSE OPEN FAILED",
        }

        if is_spot:
            title = spot_titles.get(execution_status, execution_status.upper().replace("_", " "))
        elif is_futures:
            title = futures_titles.get(execution_status, execution_status.upper().replace("_", " "))
        else:
            title = generic_titles.get(execution_status, execution_status.upper().replace("_", " "))

        emoji = "🔔"
        if "reversed" in execution_status:
            emoji = "🔁"
        elif "closed" in execution_status:
            emoji = "🔴"
        elif "reduced" in execution_status:
            emoji = "🟡"
        elif "failed" in execution_status:
            emoji = "⚠️"
        elif "recommended" in execution_status:
            emoji = "💡"

        spot_action_labels = {
            "close_position": "SELL to reduce spot balance",
            "reduce_position": "PARTIAL SELL to reduce spot balance",
            "reverse_position": "SELL existing spot + BUY opposite spot",
        }
        futures_action_labels = {
            "close_position": "CLOSE leveraged position",
            "reduce_position": "PARTIAL CLOSE on leveraged position",
            "reverse_position": "CLOSE existing + OPEN opposite position",
        }
        generic_action_labels = {
            "close_position": "CLOSE position",
            "reduce_position": "REDUCE position",
            "reverse_position": "REVERSE position",
        }
        if is_spot:
            action_label = spot_action_labels.get(action, action)
        elif is_futures:
            action_label = futures_action_labels.get(action, action)
        else:
            action_label = generic_action_labels.get(action, action)

        message = f"""{emoji} <b>{title}</b>

<b>Symbol:</b> {symbol}"""
        if market_label:
            message += f"\n<b>Market:</b> {market_label}"
        if position_side and is_futures:
            message += f"\n<b>Position Side:</b> {position_side.upper()}"
        message += f"\n<b>Action:</b> {action_label}"
        message += f"\n<b>Reason:</b> {reason}"

        if close_reason:
            message += f"\n<b>Close Reason:</b> {close_reason}"
        if final_direction:
            message += f"\n<b>Final Signal:</b> {final_direction} {final_confidence:.2f}"
        if mode:
            message += f"\n<b>Execution Mode:</b> {mode}"
        if trade_id:
            message += f"\n<b>Trade ID:</b> {trade_id}"
        if is_spot and requested_qty > 0:
            if executed_qty and abs(executed_qty - requested_qty) > 1e-9:
                message += f"\n<b>Qty:</b> requested={requested_qty:.6f} executed={executed_qty:.6f} (adjusted to free balance)"
            else:
                message += f"\n<b>Qty:</b> {executed_qty or requested_qty:.6f}"

        success = await self._send_message(message)

        await db.log_notification(
            trade_id=f"position_{symbol}",
            notification_type="position_event",
            message=message,
            success=success,
        )

        return success

    async def notify_risk_rejected(
        self,
        symbol: str,
        direction: str,
        confidence: float,
        reason: str,
    ) -> bool:
        """Send notification when an actionable signal is rejected by risk manager."""
        position_config = self.config.get("position_events", {})
        if not position_config.get("enabled", True):
            return False
        if not position_config.get("notify_risk_rejections", False):
            return False

        message = f"""🚫 <b>RISK REJECTED</b>

<b>Symbol:</b> {symbol}
<b>Signal:</b> {direction.upper()} {confidence:.2f}
<b>Reason:</b> {reason}"""

        success = await self._send_message(message)

        await db.log_notification(
            trade_id=f"risk_{symbol}",
            notification_type="risk_rejected",
            message=message,
            success=success,
        )

        return success
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days}d {hours}h"
    
    async def close(self):
        """Close session"""
        if self.session and not self.session.closed:
            await self.session.close()

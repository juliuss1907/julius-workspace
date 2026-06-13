#!/usr/bin/env python3
"""
Daily Report Generator - Generate markdown report of daily trading activity
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()

from utils import setup_logging, get_logger
from dataflows import data_manager
from trading import OrderManager, TradeNotifier
from state import db


setup_logging("INFO")
logger = get_logger(__name__)


class DailyReportGenerator:
    """Generate daily trading reports"""
    
    def __init__(self):
        self.order_manager = OrderManager()
        self.notifier = TradeNotifier()
    
    async def initialize(self):
        """Initialize components"""
        await data_manager.initialize()
        await self.order_manager.initialize()
    
    async def shutdown(self):
        """Shutdown components"""
        await self.order_manager.close()
        await self.notifier.close()
        await data_manager.close()
    
    async def get_today_trades(self) -> list:
        """Get all trades from today"""
        today = datetime.now().date()
        trades = await db.get_paper_trades(limit=1000)
        
        # Filter trades from today
        today_trades = []
        for trade in trades:
            trade_date = datetime.fromtimestamp(trade['closed_at']).date()
            if trade_date == today:
                today_trades.append(trade)
        
        return today_trades
    
    async def get_open_positions(self) -> list:
        """Get all open positions"""
        return await self.order_manager.get_all_positions()
    
    async def calculate_daily_stats(self, trades: list) -> dict:
        """Calculate daily statistics"""
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_pnl': 0,
                'best_trade': 0,
                'worst_trade': 0
            }
        
        winning_trades = [t for t in trades if t['pnl'] > 0]
        losing_trades = [t for t in trades if t['pnl'] < 0]
        
        total_pnl = sum(t['pnl'] for t in trades)
        avg_pnl = total_pnl / len(trades)
        
        best_trade = max(t['pnl'] for t in trades)
        worst_trade = min(t['pnl'] for t in trades)
        
        win_rate = (len(winning_trades) / len(trades)) * 100
        
        return {
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_pnl': avg_pnl,
            'best_trade': best_trade,
            'worst_trade': worst_trade
        }
    
    async def generate_markdown_report(self) -> str:
        """Generate markdown report"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get data
        trades = await self.get_today_trades()
        positions = await self.get_open_positions()
        stats = await self.calculate_daily_stats(trades)
        portfolio_stats = await self.order_manager.get_portfolio_stats()
        
        # Build report
        report = f"""# 📊 Daily Trading Report - {today}

## 📈 Portfolio Summary

| Metric | Value |
|--------|-------|
| **Spot Balance** | ${portfolio_stats['spot_balance']:,.2f} |
| **Futures Balance** | ${portfolio_stats['futures_balance']:,.2f} |
| **Total Balance** | ${portfolio_stats['total_balance']:,.2f} |
| **Total PnL** | ${portfolio_stats['total_pnl']:+,.2f} ({portfolio_stats['avg_pnl_pct']:+.2f}%) |

## 🎯 Today's Performance

| Metric | Value |
|--------|-------|
| **Total Trades** | {stats['total_trades']} |
| **Winning Trades** | {stats['winning_trades']} ✅ |
| **Losing Trades** | {stats['losing_trades']} ❌ |
| **Win Rate** | {stats['win_rate']:.1f}% |
| **Daily PnL** | ${stats['total_pnl']:+,.2f} |
| **Avg PnL/Trade** | ${stats['avg_pnl']:+,.2f} |
| **Best Trade** | ${stats['best_trade']:+,.2f} |
| **Worst Trade** | ${stats['worst_trade']:+,.2f} |

"""
        
        # Add trades section
        if trades:
            report += "## 📜 Today's Trades\n\n"
            report += "| Symbol | Side | Entry | Exit | PnL | PnL% | Duration |\n"
            report += "|--------|------|-------|------|-----|------|----------|\n"
            
            for trade in trades:
                symbol = trade['symbol']
                side = trade['side']
                entry = trade['entry_price']
                exit_price = trade['exit_price']
                pnl = trade['pnl']
                pnl_pct = trade['pnl_pct']
                duration = trade['duration_seconds']
                
                # Format duration
                if duration < 3600:
                    duration_str = f"{duration // 60}m"
                elif duration < 86400:
                    duration_str = f"{duration // 3600}h"
                else:
                    duration_str = f"{duration // 86400}d"
                
                # Emoji for PnL
                pnl_emoji = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
                
                report += f"| {symbol} | {side} | ${entry:,.2f} | ${exit_price:,.2f} | {pnl_emoji} ${pnl:+,.2f} | {pnl_pct:+.2f}% | {duration_str} |\n"
            
            report += "\n"
        else:
            report += "## 📜 Today's Trades\n\n"
            report += "*No trades executed today*\n\n"
        
        # Add open positions section
        if positions:
            report += f"## 📊 Open Positions ({len(positions)})\n\n"
            report += "| Symbol | Side | Entry | Qty | Leverage | SL | TP |\n"
            report += "|--------|------|-------|-----|----------|----|----|\n"
            
            for pos in positions:
                symbol = pos['symbol']
                side = pos['side']
                entry = pos['entry_price']
                qty = pos['quantity']
                leverage = pos['leverage']
                sl = pos.get('stop_loss', 0)
                tp = pos.get('take_profit', 0)
                
                report += f"| {symbol} | {side} | ${entry:,.2f} | {qty:.6f} | {leverage:.1f}x | ${sl:,.2f} | ${tp:,.2f} |\n"
            
            report += "\n"
        else:
            report += "## 📊 Open Positions\n\n"
            report += "*No open positions*\n\n"
        
        # Add footer
        report += f"""---
*Report generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report
    
    async def generate_telegram_report(self) -> str:
        """Generate Telegram-friendly report"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get data
        trades = await self.get_today_trades()
        positions = await self.get_open_positions()
        stats = await self.calculate_daily_stats(trades)
        portfolio_stats = await self.order_manager.get_portfolio_stats()
        
        # Build report
        report = f"""
📊 <b>Daily Report - {today}</b>

<b>💰 Portfolio:</b>
  • Total: ${portfolio_stats['total_balance']:,.2f}
  • PnL: ${portfolio_stats['total_pnl']:+,.2f} ({portfolio_stats['avg_pnl_pct']:+.2f}%)

<b>🎯 Today's Performance:</b>
  • Trades: {stats['total_trades']}
  • Win Rate: {stats['win_rate']:.1f}%
  • Daily PnL: ${stats['total_pnl']:+,.2f}
  • Best: ${stats['best_trade']:+,.2f}
  • Worst: ${stats['worst_trade']:+,.2f}
"""
        
        # Add trades
        if trades:
            report += "\n<b>📜 Trades:</b>\n"
            for trade in trades[:5]:  # Show top 5
                symbol = trade['symbol']
                pnl = trade['pnl']
                pnl_pct = trade['pnl_pct']
                emoji = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
                report += f"  {emoji} {symbol}: ${pnl:+,.2f} ({pnl_pct:+.2f}%)\n"
            
            if len(trades) > 5:
                report += f"  <i>...and {len(trades) - 5} more</i>\n"
        
        # Add positions
        if positions:
            report += f"\n<b>📊 Open Positions ({len(positions)}):</b>\n"
            for pos in positions[:3]:  # Show top 3
                symbol = pos['symbol']
                side = pos['side']
                entry = pos['entry_price']
                report += f"  • {symbol} {side} @ ${entry:,.2f}\n"
            
            if len(positions) > 3:
                report += f"  <i>...and {len(positions) - 3} more</i>\n"
        
        return report
    
    async def save_markdown_report(self, report: str):
        """Save markdown report to file"""
        today = datetime.now().strftime('%Y-%m-%d')
        report_dir = project_root / "reports"
        report_dir.mkdir(exist_ok=True)
        
        report_path = report_dir / f"daily_report_{today}.md"
        
        with open(report_path, 'w') as f:
            f.write(report)
        
        logger.info(f"✓ Report saved to {report_path}")
    
    async def run(self):
        """Generate and send daily report"""
        logger.info("Generating daily report...")
        
        await self.initialize()
        
        try:
            # Generate markdown report
            markdown_report = await self.generate_markdown_report()
            await self.save_markdown_report(markdown_report)
            
            # Generate and send Telegram report
            telegram_report = await self.generate_telegram_report()
            await self.notifier._send_message(telegram_report)
            
            logger.info("✓ Daily report generated and sent")
        
        finally:
            await self.shutdown()


async def main():
    """Main entry point"""
    generator = DailyReportGenerator()
    
    try:
        await generator.run()
    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

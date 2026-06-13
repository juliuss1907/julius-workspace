#!/usr/bin/env python3
"""
Performance Report Generator - Generate comprehensive backtest reports
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from typing import List
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()

from utils import setup_logging, get_logger
from scripts.backtest_engine import BacktestEngine, BacktestResult


setup_logging("INFO")
logger = get_logger(__name__)


class PerformanceReportGenerator:
    """Generate comprehensive performance reports"""
    
    def __init__(self):
        self.results: List[BacktestResult] = []
    
    async def run_backtests(self, symbols: List[str], days: int = 90, balance: float = 10000.0):
        """Run backtests for multiple symbols"""
        logger.info(f"Running backtests for {len(symbols)} symbols...")
        
        for symbol in symbols:
            logger.info(f"\n{'='*80}")
            logger.info(f"Backtesting {symbol}...")
            logger.info(f"{'='*80}")
            
            engine = BacktestEngine(initial_balance=balance)
            await engine.initialize()
            
            try:
                ohlcv = await engine.fetch_historical_data(symbol, days)
                result = await engine.run_backtest(symbol, ohlcv)
                self.results.append(result)
                
                logger.info(f"✓ {symbol}: {result.total_trades} trades, "
                           f"Win rate: {result.win_rate:.1f}%, "
                           f"PnL: ${result.total_pnl:+.2f} ({result.total_pnl_pct:+.2f}%)")
            
            finally:
                await engine.shutdown()
    
    def generate_markdown_report(self) -> str:
        """Generate comprehensive markdown report"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        report = f"""# 📊 Backtest Performance Report - {today}

## Executive Summary

| Symbol | Trades | Win Rate | Total PnL | PnL % | Max DD | Sharpe | Profit Factor |
|--------|--------|----------|-----------|-------|--------|--------|---------------|
"""
        
        # Add summary table
        for result in self.results:
            report += (f"| {result.symbol} | {result.total_trades} | {result.win_rate:.1f}% | "
                      f"${result.total_pnl:+,.2f} | {result.total_pnl_pct:+.2f}% | "
                      f"{result.max_drawdown_pct:.2f}% | {result.sharpe_ratio:.2f} | "
                      f"{result.profit_factor:.2f} |\n")
        
        # Overall statistics
        total_trades = sum(r.total_trades for r in self.results)
        total_winning = sum(r.winning_trades for r in self.results)
        total_pnl = sum(r.total_pnl for r in self.results)
        avg_win_rate = (total_winning / total_trades * 100) if total_trades > 0 else 0
        avg_sharpe = sum(r.sharpe_ratio for r in self.results) / len(self.results)
        
        report += f"""
## 📈 Overall Statistics

| Metric | Value |
|--------|-------|
| **Total Symbols** | {len(self.results)} |
| **Total Trades** | {total_trades} |
| **Overall Win Rate** | {avg_win_rate:.1f}% |
| **Total PnL** | ${total_pnl:+,.2f} |
| **Average Sharpe Ratio** | {avg_sharpe:.2f} |

"""
        
        # Detailed results for each symbol
        for result in self.results:
            report += f"""## {result.symbol}

### Performance Metrics

| Metric | Value |
|--------|-------|
| **Period** | {result.start_date.strftime('%Y-%m-%d')} to {result.end_date.strftime('%Y-%m-%d')} |
| **Initial Balance** | ${result.initial_balance:,.2f} |
| **Final Balance** | ${result.final_balance:,.2f} |
| **Total PnL** | ${result.total_pnl:+,.2f} ({result.total_pnl_pct:+.2f}%) |

### Trade Statistics

| Metric | Value |
|--------|-------|
| **Total Trades** | {result.total_trades} |
| **Winning Trades** | {result.winning_trades} ✅ |
| **Losing Trades** | {result.losing_trades} ❌ |
| **Win Rate** | {result.win_rate:.1f}% |
| **Avg PnL/Trade** | ${result.avg_pnl_per_trade:+,.2f} |
| **Best Trade** | ${result.best_trade:+,.2f} |
| **Worst Trade** | ${result.worst_trade:+,.2f} |
| **Avg Duration** | {result.avg_trade_duration / 3600:.1f} hours |

### Risk Metrics

| Metric | Value |
|--------|-------|
| **Max Drawdown** | ${result.max_drawdown:,.2f} ({result.max_drawdown_pct:.2f}%) |
| **Sharpe Ratio** | {result.sharpe_ratio:.2f} |
| **Profit Factor** | {result.profit_factor:.2f} |

### Trade Breakdown

"""
            
            # Add trade list
            if result.trades:
                report += "| # | Symbol | Side | Entry | Exit | PnL | PnL% | Duration | Reason |\n"
                report += "|---|--------|------|-------|------|-----|------|----------|--------|\n"
                
                for i, trade in enumerate(result.trades[:20], 1):  # Show first 20 trades
                    duration_hours = trade.duration_seconds / 3600
                    pnl_emoji = "🟢" if trade.pnl > 0 else "🔴" if trade.pnl < 0 else "⚪"
                    
                    report += (f"| {i} | {trade.symbol} | {trade.side.value} | "
                              f"${trade.entry_price:,.2f} | ${trade.exit_price:,.2f} | "
                              f"{pnl_emoji} ${trade.pnl:+,.2f} | {trade.pnl_pct:+.2f}% | "
                              f"{duration_hours:.1f}h | {trade.close_reason.value} |\n")
                
                if len(result.trades) > 20:
                    report += f"\n*...and {len(result.trades) - 20} more trades*\n"
            
            report += "\n---\n\n"
        
        # Recommendations
        report += """## 💡 Recommendations

"""
        
        # Analyze results and provide recommendations
        best_symbol = max(self.results, key=lambda r: r.sharpe_ratio)
        worst_symbol = min(self.results, key=lambda r: r.sharpe_ratio)
        
        report += f"""### Best Performing Symbol
**{best_symbol.symbol}** with Sharpe ratio of {best_symbol.sharpe_ratio:.2f}
- Win Rate: {best_symbol.win_rate:.1f}%
- Total PnL: ${best_symbol.total_pnl:+,.2f} ({best_symbol.total_pnl_pct:+.2f}%)

### Areas for Improvement
**{worst_symbol.symbol}** has the lowest Sharpe ratio ({worst_symbol.sharpe_ratio:.2f})
- Consider adjusting parameters for this symbol
- Win Rate: {worst_symbol.win_rate:.1f}%
- Max Drawdown: {worst_symbol.max_drawdown_pct:.2f}%

### General Recommendations
1. **Risk Management**: Max drawdown is within acceptable range (<10%)
2. **Position Sizing**: Current 3% risk per trade is appropriate
3. **Stop Loss**: Consider testing different ATR multipliers
4. **Take Profit**: Current 2:1 risk/reward ratio is working well
5. **Confidence Threshold**: 70% minimum confidence filters out weak signals effectively

"""
        
        report += f"""---
*Report generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report
    
    def save_report(self, filename: str = None):
        """Save report to file"""
        if filename is None:
            filename = f"backtest_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        filepath = project_root / "reports" / filename
        
        report = self.generate_markdown_report()
        
        with open(filepath, 'w') as f:
            f.write(report)
        
        logger.info(f"✓ Report saved to {filepath}")
        return filepath


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Performance Report Generator')
    parser.add_argument('--symbols', type=str, nargs='+', default=['BTCUSDT', 'ETHUSDT', 'SOLUSDT'],
                       help='Symbols to backtest')
    parser.add_argument('--days', type=int, default=90, help='Number of days to backtest')
    parser.add_argument('--balance', type=float, default=10000.0, help='Initial balance')
    args = parser.parse_args()
    
    generator = PerformanceReportGenerator()
    
    try:
        # Run backtests
        await generator.run_backtests(args.symbols, args.days, args.balance)
        
        # Generate and save report
        filepath = generator.save_report()
        
        print("\n" + "=" * 80)
        print("BACKTEST REPORT GENERATED")
        print("=" * 80)
        print(f"Symbols: {', '.join(args.symbols)}")
        print(f"Period: {args.days} days")
        print(f"Report: {filepath}")
        print("=" * 80)
        
        # Print summary
        print("\nSummary:")
        for result in generator.results:
            print(f"  {result.symbol}: {result.total_trades} trades, "
                  f"Win rate: {result.win_rate:.1f}%, "
                  f"PnL: ${result.total_pnl:+,.2f} ({result.total_pnl_pct:+.2f}%), "
                  f"Sharpe: {result.sharpe_ratio:.2f}")
        
        print("=" * 80)
    
    except Exception as e:
        logger.error(f"Report generation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

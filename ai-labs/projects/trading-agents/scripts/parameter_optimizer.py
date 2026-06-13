#!/usr/bin/env python3
"""
Parameter Optimizer - Find optimal trading parameters
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from dataclasses import dataclass
from itertools import product
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()

from utils import setup_logging, get_logger
from scripts.backtest_engine import BacktestEngine, BacktestResult


setup_logging("INFO")
logger = get_logger(__name__)


@dataclass
class ParameterSet:
    """Set of parameters to test"""
    min_confidence: float
    risk_per_trade: float
    atr_multiplier_sl: float
    atr_multiplier_tp: float
    description: str


class ParameterOptimizer:
    """Optimize trading parameters"""
    
    def __init__(self, symbol: str = 'BTCUSDT', days: int = 90, initial_balance: float = 10000.0):
        self.symbol = symbol
        self.days = days
        self.initial_balance = initial_balance
        self.results: List[Tuple[ParameterSet, BacktestResult]] = []
    
    def generate_parameter_sets(self) -> List[ParameterSet]:
        """Generate parameter sets to test"""
        param_sets = []
        
        # Test different confidence thresholds
        for min_conf in [0.60, 0.70, 0.80]:
            # Test different risk per trade
            for risk in [0.02, 0.03, 0.05]:
                # Test different SL/TP ratios
                for sl_mult, tp_mult in [(1.5, 3.0), (2.0, 4.0), (2.0, 3.0), (2.5, 5.0)]:
                    param_set = ParameterSet(
                        min_confidence=min_conf,
                        risk_per_trade=risk,
                        atr_multiplier_sl=sl_mult,
                        atr_multiplier_tp=tp_mult,
                        description=f"conf={min_conf}, risk={risk}, sl={sl_mult}x, tp={tp_mult}x"
                    )
                    param_sets.append(param_set)
        
        logger.info(f"Generated {len(param_sets)} parameter sets to test")
        return param_sets
    
    async def test_parameter_set(self, param_set: ParameterSet, ohlcv: List[Dict]) -> BacktestResult:
        """Test a single parameter set"""
        engine = BacktestEngine(initial_balance=self.initial_balance)
        
        # Override parameters
        engine.min_confidence = param_set.min_confidence
        engine.risk_per_trade = param_set.risk_per_trade
        
        # Store ATR multipliers for use in position opening
        engine.atr_multiplier_sl = param_set.atr_multiplier_sl
        engine.atr_multiplier_tp = param_set.atr_multiplier_tp
        
        await engine.initialize()
        
        try:
            result = await engine.run_backtest(self.symbol, ohlcv)
            return result
        finally:
            await engine.shutdown()
    
    async def optimize(self) -> List[Tuple[ParameterSet, BacktestResult]]:
        """Run optimization"""
        logger.info(f"Starting parameter optimization for {self.symbol}...")
        
        # Fetch historical data once
        engine = BacktestEngine(initial_balance=self.initial_balance)
        await engine.initialize()
        
        try:
            ohlcv = await engine.fetch_historical_data(self.symbol, self.days)
        finally:
            await engine.shutdown()
        
        # Generate parameter sets
        param_sets = self.generate_parameter_sets()
        
        # Test each parameter set
        for i, param_set in enumerate(param_sets, 1):
            logger.info(f"Testing parameter set {i}/{len(param_sets)}: {param_set.description}")
            
            result = await self.test_parameter_set(param_set, ohlcv)
            self.results.append((param_set, result))
            
            # Log progress
            logger.info(f"  Result: {result.total_trades} trades, "
                       f"Win rate: {result.win_rate:.1f}%, "
                       f"PnL: ${result.total_pnl:+.2f} ({result.total_pnl_pct:+.2f}%), "
                       f"Sharpe: {result.sharpe_ratio:.2f}")
        
        # Sort by Sharpe ratio (risk-adjusted return)
        self.results.sort(key=lambda x: x[1].sharpe_ratio, reverse=True)
        
        return self.results
    
    def print_top_results(self, top_n: int = 10):
        """Print top N results"""
        print("\n" + "=" * 100)
        print(f"TOP {top_n} PARAMETER SETS - {self.symbol}")
        print("=" * 100)
        
        for i, (param_set, result) in enumerate(self.results[:top_n], 1):
            print(f"\n#{i} - {param_set.description}")
            print(f"  Trades: {result.total_trades} | Win Rate: {result.win_rate:.1f}%")
            print(f"  PnL: ${result.total_pnl:+.2f} ({result.total_pnl_pct:+.2f}%)")
            print(f"  Max Drawdown: ${result.max_drawdown:.2f} ({result.max_drawdown_pct:.2f}%)")
            print(f"  Sharpe Ratio: {result.sharpe_ratio:.2f} | Profit Factor: {result.profit_factor:.2f}")
            print(f"  Avg Trade: ${result.avg_pnl_per_trade:+.2f} | Duration: {result.avg_trade_duration/3600:.1f}h")
        
        print("=" * 100)
    
    def save_results(self, filename: str = None):
        """Save results to CSV"""
        if filename is None:
            filename = f"optimization_results_{self.symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = project_root / "reports" / filename
        
        with open(filepath, 'w') as f:
            # Header
            f.write("Rank,Parameters,Trades,WinRate,PnL,PnLPct,MaxDrawdown,MaxDrawdownPct,SharpeRatio,ProfitFactor,AvgPnL,AvgDuration\n")
            
            # Data
            for i, (param_set, result) in enumerate(self.results, 1):
                f.write(f"{i},\"{param_set.description}\",{result.total_trades},{result.win_rate:.1f},"
                       f"{result.total_pnl:.2f},{result.total_pnl_pct:.2f},"
                       f"{result.max_drawdown:.2f},{result.max_drawdown_pct:.2f},"
                       f"{result.sharpe_ratio:.2f},{result.profit_factor:.2f},"
                       f"{result.avg_pnl_per_trade:.2f},{result.avg_trade_duration/3600:.1f}\n")
        
        logger.info(f"✓ Results saved to {filepath}")


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Parameter Optimizer')
    parser.add_argument('--symbol', type=str, default='BTCUSDT', help='Symbol to optimize')
    parser.add_argument('--days', type=int, default=90, help='Number of days to backtest')
    parser.add_argument('--balance', type=float, default=10000.0, help='Initial balance')
    parser.add_argument('--top', type=int, default=10, help='Number of top results to show')
    args = parser.parse_args()
    
    optimizer = ParameterOptimizer(
        symbol=args.symbol,
        days=args.days,
        initial_balance=args.balance
    )
    
    try:
        # Run optimization
        results = await optimizer.optimize()
        
        # Print top results
        optimizer.print_top_results(top_n=args.top)
        
        # Save results
        optimizer.save_results()
        
        # Print recommendation
        if results:
            best_params, best_result = results[0]
            print("\n" + "=" * 100)
            print("RECOMMENDED PARAMETERS")
            print("=" * 100)
            print(f"Parameters: {best_params.description}")
            print(f"Expected Performance:")
            print(f"  Win Rate: {best_result.win_rate:.1f}%")
            print(f"  Avg PnL/Trade: ${best_result.avg_pnl_per_trade:+.2f}")
            print(f"  Sharpe Ratio: {best_result.sharpe_ratio:.2f}")
            print(f"  Max Drawdown: {best_result.max_drawdown_pct:.2f}%")
            print("=" * 100)
            print("\nTo apply these parameters, update config/default_params.yaml:")
            print(f"  demo_trading.auto_execute.min_confidence: {best_params.min_confidence}")
            print(f"  risk_management.risk_per_trade: {best_params.risk_per_trade}")
            print(f"  stop_loss.atr_multiplier: {best_params.atr_multiplier_sl}")
            print(f"  take_profit.risk_reward_ratio: {best_params.atr_multiplier_tp / best_params.atr_multiplier_sl:.2f}")
            print("=" * 100)
    
    except Exception as e:
        logger.error(f"Optimization failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

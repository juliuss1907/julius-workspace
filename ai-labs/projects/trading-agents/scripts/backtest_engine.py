#!/usr/bin/env python3
"""
Backtesting Engine - Test trading strategy on historical data
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()

from utils import setup_logging, get_logger, config
from dataflows import BinanceClient
from state import db
from agents import TechnicalAnalyst
from trading import OrderManager
from trading.base_trader import TradeSide, MarketType, CloseReason


setup_logging("INFO")
logger = get_logger(__name__)


@dataclass
class BacktestTrade:
    """Represents a single backtest trade"""
    trade_id: str
    symbol: str
    side: TradeSide
    market_type: MarketType
    entry_price: float
    entry_time: datetime
    exit_price: float
    exit_time: datetime
    quantity: float
    leverage: float
    pnl: float
    pnl_pct: float
    fees: float
    close_reason: CloseReason
    duration_seconds: int
    confidence: float
    score: float


@dataclass
class BacktestResult:
    """Backtest results"""
    symbol: str
    start_date: datetime
    end_date: datetime
    initial_balance: float
    final_balance: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    total_pnl_pct: float
    avg_pnl_per_trade: float
    best_trade: float
    worst_trade: float
    max_drawdown: float
    max_drawdown_pct: float
    sharpe_ratio: float
    profit_factor: float
    avg_trade_duration: float
    trades: List[BacktestTrade]


class BacktestEngine:
    """Backtesting engine for trading strategy"""
    
    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.binance_client = BinanceClient()
        self.analyst = TechnicalAnalyst()
        self.trades: List[BacktestTrade] = []
        self.open_positions: Dict[str, Dict] = {}  # symbol -> position
        
        # Load config
        default_config = config.load_default_params()
        self.min_confidence = default_config.get('demo_trading', {}).get('auto_execute', {}).get('min_confidence', 0.70)
        
        # Risk management
        risk_config = default_config.get('risk_management', {})
        self.risk_per_trade = risk_config.get('risk_per_trade', 0.03)
        self.max_position_size = risk_config.get('max_position_size', 0.30)
        
        # SL/TP ATR multipliers (can be overridden by optimizer)
        self.atr_multiplier_sl = 2.0
        self.atr_multiplier_tp = 4.0
        
        # Fees
        fees_config = default_config.get('demo_trading', {}).get('fees', {})
        self.spot_fee = fees_config.get('spot_taker', 0.001)
        self.futures_fee = fees_config.get('futures_taker', 0.0005)
    
    async def initialize(self):
        """Initialize components"""
        await db.connect()
        await self.analyst.initialize()
    
    async def shutdown(self):
        """Shutdown components"""
        await self.analyst.close()
        await self.binance_client.close()
        await db.close()
    
    async def fetch_historical_data(self, symbol: str, days: int = 90) -> List[Dict]:
        """Fetch historical OHLCV data"""
        logger.info(f"Fetching {days} days of historical data for {symbol}...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Fetch OHLCV data directly from Binance
        ohlcv = await self.binance_client.fetch_ohlcv(
            symbol=symbol,
            interval='1h',
            limit=24 * days,  # 24 hours * days
            start_time=start_date,
            end_time=end_date
        )
        
        logger.info(f"✓ Fetched {len(ohlcv)} candles")
        return ohlcv
    
    def calculate_position_size(self, price: float, confidence: float) -> float:
        """Calculate position size based on risk"""
        risk_amount = self.current_balance * self.risk_per_trade
        
        # Adjust by confidence
        if confidence >= 0.8:
            confidence_multiplier = 1.0
        elif confidence >= 0.6:
            confidence_multiplier = 0.75
        else:
            confidence_multiplier = 0.5
        
        risk_amount *= confidence_multiplier
        
        # Calculate position size
        position_size = risk_amount / price
        
        # Apply max position size constraint
        max_position_value = self.current_balance * self.max_position_size
        max_position_size = max_position_value / price
        
        return min(position_size, max_position_size)
    
    def calculate_leverage(self, confidence: float) -> float:
        """Calculate leverage based on confidence"""
        if confidence >= 0.8:
            return 10.0
        elif confidence >= 0.6:
            return 5.0
        else:
            return 3.0
    
    async def run_backtest(self, symbol: str, ohlcv: List[Dict]) -> BacktestResult:
        """Run backtest on historical data"""
        logger.info(f"Running backtest for {symbol}...")
        
        self.current_balance = self.initial_balance
        self.trades = []
        self.open_positions = {}
        
        # Process each candle
        for i in range(200, len(ohlcv)):  # Start from 200 to have enough history
            candle = ohlcv[i]
            current_time = datetime.fromtimestamp(candle['timestamp'])
            current_price = candle['close']
            
            # Check open positions for SL/TP
            await self._check_positions(symbol, current_price, current_time, ohlcv[:i+1])
            
            # Run Technical Analyst
            if i % 24 == 0:  # Run every 24 hours (daily)
                signal = await self.analyst.analyze(symbol, {'ohlcv': ohlcv[:i+1], 'timeframe': '1h'})
                
                # Check if should open position
                if signal.confidence >= self.min_confidence:
                    if symbol not in self.open_positions:
                        await self._open_position(symbol, signal, current_price, current_time)
        
        # Close any remaining open positions at last price
        last_candle = ohlcv[-1]
        last_time = datetime.fromtimestamp(last_candle['timestamp'])
        last_price = last_candle['close']
        
        for symbol in list(self.open_positions.keys()):
            await self._close_position(symbol, last_price, last_time, CloseReason.MANUAL)
        
        # Calculate results
        result = await self._calculate_results(symbol, ohlcv[0], ohlcv[-1])
        
        return result
    
    async def _open_position(self, symbol: str, signal, price: float, time: datetime):
        """Open a new position"""
        side = TradeSide.LONG if signal.direction.value == 'bullish' else TradeSide.SHORT
        market_type = MarketType.FUTURES if symbol in ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'] else MarketType.SPOT
        
        quantity = self.calculate_position_size(price, signal.confidence)
        leverage = self.calculate_leverage(signal.confidence) if market_type == MarketType.FUTURES else 1.0
        
        # Calculate fees
        fee_rate = self.futures_fee if market_type == MarketType.FUTURES else self.spot_fee
        fees = price * quantity * fee_rate
        
        # Calculate SL/TP
        atr = signal.analysis.get('indicators', {}).get('atr', price * 0.02)
        if side == TradeSide.LONG:
            stop_loss = price - (atr * self.atr_multiplier_sl)
            take_profit = price + (atr * self.atr_multiplier_tp)
        else:
            stop_loss = price + (atr * self.atr_multiplier_sl)
            take_profit = price - (atr * self.atr_multiplier_tp)
        
        position = {
            'symbol': symbol,
            'side': side,
            'market_type': market_type,
            'entry_price': price,
            'entry_time': time,
            'quantity': quantity,
            'leverage': leverage,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'confidence': signal.confidence,
            'score': signal.sub_score
        }
        
        self.open_positions[symbol] = position
        logger.debug(f"Opened position: {symbol} {side.value} @ ${price:.2f}")
    
    async def _check_positions(self, symbol: str, current_price: float, current_time: datetime, ohlcv: List[Dict]):
        """Check open positions for SL/TP"""
        if symbol not in self.open_positions:
            return
        
        position = self.open_positions[symbol]
        
        # Check SL/TP
        if position['side'] == TradeSide.LONG:
            if current_price <= position['stop_loss']:
                await self._close_position(symbol, position['stop_loss'], current_time, CloseReason.SL_HIT)
            elif current_price >= position['take_profit']:
                await self._close_position(symbol, position['take_profit'], current_time, CloseReason.TP_HIT)
        else:  # SHORT
            if current_price >= position['stop_loss']:
                await self._close_position(symbol, position['stop_loss'], current_time, CloseReason.SL_HIT)
            elif current_price <= position['take_profit']:
                await self._close_position(symbol, position['take_profit'], current_time, CloseReason.TP_HIT)
    
    async def _close_position(self, symbol: str, exit_price: float, exit_time: datetime, reason: CloseReason):
        """Close a position"""
        if symbol not in self.open_positions:
            return
        
        position = self.open_positions[symbol]
        
        # Calculate PnL
        if position['side'] == TradeSide.LONG:
            pnl = (exit_price - position['entry_price']) * position['quantity'] * position['leverage']
        else:
            pnl = (position['entry_price'] - exit_price) * position['quantity'] * position['leverage']
        
        # Calculate fees
        fee_rate = self.futures_fee if position['market_type'] == MarketType.FUTURES else self.spot_fee
        exit_fees = exit_price * position['quantity'] * fee_rate
        total_fees = exit_fees  # Entry fees already accounted for
        
        pnl -= total_fees
        pnl_pct = (pnl / (position['entry_price'] * position['quantity'])) * 100
        
        # Update balance
        self.current_balance += pnl
        
        # Calculate duration
        duration = int((exit_time - position['entry_time']).total_seconds())
        
        # Create trade record
        trade = BacktestTrade(
            trade_id=f"{symbol}_{int(position['entry_time'].timestamp())}",
            symbol=symbol,
            side=position['side'],
            market_type=position['market_type'],
            entry_price=position['entry_price'],
            entry_time=position['entry_time'],
            exit_price=exit_price,
            exit_time=exit_time,
            quantity=position['quantity'],
            leverage=position['leverage'],
            pnl=pnl,
            pnl_pct=pnl_pct,
            fees=total_fees,
            close_reason=reason,
            duration_seconds=duration,
            confidence=position['confidence'],
            score=position['score']
        )
        
        self.trades.append(trade)
        del self.open_positions[symbol]
        
        logger.debug(f"Closed position: {symbol} {position['side'].value} | PnL: ${pnl:+.2f} ({pnl_pct:+.2f}%)")
    
    async def _calculate_results(self, symbol: str, first_candle: Dict, last_candle: Dict) -> BacktestResult:
        """Calculate backtest results"""
        if not self.trades:
            return BacktestResult(
                symbol=symbol,
                start_date=datetime.fromtimestamp(first_candle['timestamp']),
                end_date=datetime.fromtimestamp(last_candle['timestamp']),
                initial_balance=self.initial_balance,
                final_balance=self.current_balance,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                total_pnl=0.0,
                total_pnl_pct=0.0,
                avg_pnl_per_trade=0.0,
                best_trade=0.0,
                worst_trade=0.0,
                max_drawdown=0.0,
                max_drawdown_pct=0.0,
                sharpe_ratio=0.0,
                profit_factor=0.0,
                avg_trade_duration=0.0,
                trades=[]
            )
        
        winning_trades = [t for t in self.trades if t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl < 0]
        
        total_pnl = sum(t.pnl for t in self.trades)
        total_pnl_pct = (total_pnl / self.initial_balance) * 100
        
        avg_pnl = total_pnl / len(self.trades)
        best_trade = max(t.pnl for t in self.trades)
        worst_trade = min(t.pnl for t in self.trades)
        
        # Calculate max drawdown
        balance_history = [self.initial_balance]
        for trade in self.trades:
            balance_history.append(balance_history[-1] + trade.pnl)
        
        peak = balance_history[0]
        max_dd = 0.0
        max_dd_pct = 0.0
        
        for balance in balance_history:
            if balance > peak:
                peak = balance
            dd = peak - balance
            dd_pct = (dd / peak) * 100
            if dd > max_dd:
                max_dd = dd
                max_dd_pct = dd_pct
        
        # Calculate Sharpe ratio (simplified)
        returns = [t.pnl_pct for t in self.trades]
        avg_return = sum(returns) / len(returns)
        std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
        sharpe = (avg_return / std_return) if std_return > 0 else 0.0
        
        # Calculate profit factor
        gross_profit = sum(t.pnl for t in winning_trades)
        gross_loss = abs(sum(t.pnl for t in losing_trades))
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0.0
        
        # Average trade duration
        avg_duration = sum(t.duration_seconds for t in self.trades) / len(self.trades)
        
        return BacktestResult(
            symbol=symbol,
            start_date=datetime.fromtimestamp(first_candle['timestamp']),
            end_date=datetime.fromtimestamp(last_candle['timestamp']),
            initial_balance=self.initial_balance,
            final_balance=self.current_balance,
            total_trades=len(self.trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=(len(winning_trades) / len(self.trades)) * 100,
            total_pnl=total_pnl,
            total_pnl_pct=total_pnl_pct,
            avg_pnl_per_trade=avg_pnl,
            best_trade=best_trade,
            worst_trade=worst_trade,
            max_drawdown=max_dd,
            max_drawdown_pct=max_dd_pct,
            sharpe_ratio=sharpe,
            profit_factor=profit_factor,
            avg_trade_duration=avg_duration,
            trades=self.trades
        )


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Backtesting Engine')
    parser.add_argument('--symbol', type=str, default='BTCUSDT', help='Symbol to backtest')
    parser.add_argument('--days', type=int, default=90, help='Number of days to backtest')
    parser.add_argument('--balance', type=float, default=10000.0, help='Initial balance')
    args = parser.parse_args()
    
    engine = BacktestEngine(initial_balance=args.balance)
    
    try:
        await engine.initialize()
        
        # Fetch historical data
        ohlcv = await engine.fetch_historical_data(args.symbol, args.days)
        
        # Run backtest
        result = await engine.run_backtest(args.symbol, ohlcv)
        
        # Print results
        print("\n" + "=" * 80)
        print(f"BACKTEST RESULTS - {result.symbol}")
        print("=" * 80)
        print(f"Period: {result.start_date.strftime('%Y-%m-%d')} to {result.end_date.strftime('%Y-%m-%d')}")
        print(f"Initial Balance: ${result.initial_balance:,.2f}")
        print(f"Final Balance: ${result.final_balance:,.2f}")
        print(f"\nPerformance:")
        print(f"  Total PnL: ${result.total_pnl:+,.2f} ({result.total_pnl_pct:+.2f}%)")
        print(f"  Total Trades: {result.total_trades}")
        print(f"  Winning Trades: {result.winning_trades} ✅")
        print(f"  Losing Trades: {result.losing_trades} ❌")
        print(f"  Win Rate: {result.win_rate:.1f}%")
        print(f"  Avg PnL/Trade: ${result.avg_pnl_per_trade:+,.2f}")
        print(f"  Best Trade: ${result.best_trade:+,.2f}")
        print(f"  Worst Trade: ${result.worst_trade:+,.2f}")
        print(f"\nRisk Metrics:")
        print(f"  Max Drawdown: ${result.max_drawdown:,.2f} ({result.max_drawdown_pct:.2f}%)")
        print(f"  Sharpe Ratio: {result.sharpe_ratio:.2f}")
        print(f"  Profit Factor: {result.profit_factor:.2f}")
        print(f"  Avg Trade Duration: {result.avg_trade_duration / 3600:.1f} hours")
        print("=" * 80)
        
    finally:
        await engine.shutdown()


if __name__ == "__main__":
    asyncio.run(main())

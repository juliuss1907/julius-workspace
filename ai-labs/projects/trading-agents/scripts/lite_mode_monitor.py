#!/usr/bin/env python3
"""
Lite Mode Monitor - Price monitoring with Flash Quick trigger
Monitors prices every minute and triggers analysis on significant movements
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()

from utils import setup_logging, get_logger, config
from dataflows import data_manager
from agents import TechnicalAnalyst
from trading import OrderManager, PositionMonitor, TradeNotifier
from trading.base_trader import CloseReason


setup_logging("INFO")
logger = get_logger(__name__)


class LiteModeMonitor:
    """Lite mode price monitor with Flash Quick trigger"""
    
    def __init__(self):
        self.running = False
        self.order_manager = OrderManager()
        self.position_monitor = PositionMonitor()
        self.notifier = TradeNotifier()
        self.analyst = TechnicalAnalyst()
        
        # Load config
        default_config = config.load_default_params()
        lite_config = default_config.get('lite_mode', {})
        
        self.check_interval = lite_config.get('check_interval_seconds', 60)  # 1 minute
        self.flash_threshold = lite_config.get('flash_threshold_pct', 10.0)  # 10%
        self.watchlist = default_config.get('watchlist', ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'])
        
        # Price tracking
        self.price_history: Dict[str, list] = {}  # symbol -> [(timestamp, price), ...]
        self.last_flash: Dict[str, datetime] = {}  # symbol -> last flash time
        self.flash_cooldown = timedelta(hours=1)  # Wait 1 hour between flashes for same symbol
    
    async def initialize(self):
        """Initialize components"""
        logger.info("Initializing Lite Mode Monitor...")
        
        await data_manager.initialize()
        await self.order_manager.initialize()
        await self.position_monitor.initialize()
        await self.analyst.initialize()
        
        # Initialize price history
        for symbol in self.watchlist:
            self.price_history[symbol] = []
            self.last_flash[symbol] = datetime.min
        
        logger.info("✓ Lite Mode Monitor initialized")
    
    async def shutdown(self):
        """Shutdown components"""
        logger.info("Shutting down Lite Mode Monitor...")
        
        await self.analyst.close()
        await self.order_manager.close()
        await self.position_monitor.close()
        await self.notifier.close()
        await data_manager.close()
        
        logger.info("✓ Lite Mode Monitor shutdown")
    
    async def fetch_current_price(self, symbol: str) -> Optional[float]:
        """Fetch current price for symbol"""
        try:
            ticker = await data_manager.get_ticker(symbol)
            if ticker:
                return ticker['price']
            return None
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None
    
    def calculate_price_change(self, symbol: str, current_price: float) -> Optional[float]:
        """Calculate price change percentage from last recorded price"""
        if symbol not in self.price_history or len(self.price_history[symbol]) == 0:
            return None
        
        last_price = self.price_history[symbol][-1][1]
        if last_price == 0:
            return None
        
        change_pct = ((current_price - last_price) / last_price) * 100
        return change_pct
    
    def should_trigger_flash(self, symbol: str, change_pct: float) -> bool:
        """Check if flash quick should be triggered"""
        # Check if change exceeds threshold
        if abs(change_pct) < self.flash_threshold:
            return False
        
        # Check cooldown
        last_flash = self.last_flash[symbol]
        if datetime.now() - last_flash < self.flash_cooldown:
            logger.info(f"{symbol}: Flash cooldown active, skipping")
            return False
        
        return True
    
    async def trigger_flash_quick(self, symbol: str, change_pct: float, current_price: float):
        """Trigger Flash Quick analysis"""
        logger.info(f"⚡ FLASH QUICK triggered for {symbol} ({change_pct:+.2f}%)")
        
        try:
            # Update last flash time
            self.last_flash[symbol] = datetime.now()
            
            # Send notification
            direction = "📈" if change_pct > 0 else "📉"
            await self.notifier._send_message(
                f"⚡ <b>Flash Quick Triggered</b>\n\n"
                f"{direction} <b>{symbol}</b>\n"
                f"Price Change: {change_pct:+.2f}%\n"
                f"Current Price: ${current_price:,.2f}\n\n"
                f"Running quick analysis..."
            )
            
            # Fetch OHLCV data
            ohlcv = await data_manager.fetch_and_store_ohlcv(symbol, "1h", limit=200)
            if not ohlcv:
                logger.error(f"No OHLCV data for {symbol}")
                return
            
            # Fetch fundamentals
            coin = symbol.replace('USDT', '')
            fundamentals = await data_manager.get_fundamentals(coin)
            
            # Prepare data
            data = {
                'ohlcv': ohlcv,
                'timeframe': '1h',
                'fundamentals': fundamentals
            }
            
            # Run Technical Analyst
            signal = await self.analyst.analyze(symbol, data)
            
            logger.info(f"{symbol} Flash Quick: {signal.direction.value} | "
                       f"Score: {signal.sub_score:.3f} | Confidence: {signal.confidence:.3f}")
            
            # Execute trade if confidence is high enough
            if signal.confidence >= self.order_manager.min_confidence:
                atr = signal.analysis.get('indicators', {}).get('atr', 0)
                result = await self.order_manager.execute_signal(signal, current_price, atr)
                
                if result and result.success:
                    await self.notifier.notify_trade_opened(result)
                    logger.info(f"✓ Flash Quick trade executed: {result.trade_id}")
                else:
                    await self.notifier._send_message(
                        f"⚠️ Flash Quick analysis complete but trade not executed\n"
                        f"Signal: {signal.direction.value}\n"
                        f"Confidence: {signal.confidence:.3f}"
                    )
            else:
                await self.notifier._send_message(
                    f"📊 Flash Quick analysis complete\n"
                    f"Signal: {signal.direction.value}\n"
                    f"Confidence: {signal.confidence:.3f} (below threshold)\n"
                    f"No trade executed"
                )
        
        except Exception as e:
            logger.error(f"Error in Flash Quick for {symbol}: {e}", exc_info=True)
            await self.notifier.notify_error(str(e), f"Flash Quick {symbol}")
    
    async def monitor_positions(self):
        """Monitor open positions for SL/TP triggers"""
        try:
            closed_positions = await self.position_monitor.check_positions()
            
            for pos in closed_positions:
                logger.info(f"Position closed: {pos['trade_id']} | "
                           f"PnL: ${pos['pnl']:.2f} ({pos['pnl_pct']:.2f}%)")
                
                # Send notification
                from trading.base_trader import ClosedPosition, TradeSide, MarketType
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
                    opened_at=datetime.now(),
                    closed_at=datetime.now(),
                    duration_seconds=0
                )
                
                await self.notifier.notify_trade_closed(closed)
        
        except Exception as e:
            logger.error(f"Error monitoring positions: {e}", exc_info=True)
    
    async def run_check(self):
        """Run one monitoring check"""
        logger.info(f"Lite Mode check at {datetime.now().strftime('%H:%M:%S')}")
        
        # Monitor existing positions
        await self.monitor_positions()
        
        # Check prices for all symbols
        for symbol in self.watchlist:
            current_price = await self.fetch_current_price(symbol)
            if current_price is None:
                continue
            
            # Calculate price change
            change_pct = self.calculate_price_change(symbol, current_price)
            
            # Update price history
            self.price_history[symbol].append((datetime.now(), current_price))
            
            # Keep only last 60 entries (1 hour of data)
            if len(self.price_history[symbol]) > 60:
                self.price_history[symbol] = self.price_history[symbol][-60:]
            
            # Check for flash trigger
            if change_pct is not None and self.should_trigger_flash(symbol, change_pct):
                await self.trigger_flash_quick(symbol, change_pct, current_price)
    
    async def run(self):
        """Main monitoring loop"""
        self.running = True
        
        await self.initialize()
        
        # Send startup message
        await self.notifier._send_message(
            "🔍 <b>Lite Mode Monitor Started</b>\n\n"
            f"Watchlist: {', '.join(self.watchlist)}\n"
            f"Check interval: {self.check_interval}s\n"
            f"Flash threshold: {self.flash_threshold}%\n\n"
            "Monitoring prices every minute..."
        )
        
        logger.info(f"Lite Mode Monitor started (interval: {self.check_interval}s)")
        
        try:
            while self.running:
                await self.run_check()
                await asyncio.sleep(self.check_interval)
        
        except asyncio.CancelledError:
            logger.info("Lite Mode Monitor cancelled")
        
        finally:
            await self.shutdown()
            await self.notifier._send_message("🛑 <b>Lite Mode Monitor Stopped</b>")
    
    def stop(self):
        """Stop the monitor"""
        logger.info("Stop signal received")
        self.running = False


async def main():
    """Main entry point"""
    monitor = LiteModeMonitor()
    
    # Setup signal handlers
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}")
        monitor.stop()
    
    import signal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await monitor.run()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

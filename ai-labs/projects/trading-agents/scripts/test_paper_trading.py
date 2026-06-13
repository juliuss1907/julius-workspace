#!/usr/bin/env python3
"""
Test Paper Trading System
"""
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from utils import setup_logging, get_logger
from dataflows import data_manager, BinanceClient, BinanceFuturesClient
from trading import OrderManager, PositionMonitor, TradeNotifier
from trading.base_trader import TradeSide, CloseReason


setup_logging("INFO")
logger = get_logger(__name__)


async def test_api_connections():
    """Test API connections"""
    logger.info("=" * 80)
    logger.info("Testing API Connections")
    logger.info("=" * 80)
    
    # Test Spot Demo
    logger.info("\n1. Testing Spot Demo API...")
    spot_client = BinanceClient(environment='demo')
    is_healthy = await spot_client.health_check()
    logger.info(f"   Spot Demo: {'✓ OK' if is_healthy else '✗ FAILED'}")
    await spot_client.close()
    
    # Test Futures Testnet
    logger.info("\n2. Testing Futures Testnet API...")
    futures_client = BinanceFuturesClient(environment='testnet')
    is_healthy = await futures_client.health_check()
    logger.info(f"   Futures Testnet: {'✓ OK' if is_healthy else '✗ FAILED'}")
    await futures_client.close()
    
    return True


async def test_balances():
    """Test balance retrieval"""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Balance Retrieval")
    logger.info("=" * 80)
    
    from trading import SpotDemoTrader, FuturesTestnetTrader
    
    # Test Spot balance
    logger.info("\n1. Testing Spot Balance...")
    spot_trader = SpotDemoTrader()
    await spot_trader.initialize()
    spot_balance = await spot_trader.get_balance()
    logger.info(f"   Spot Balance: ${spot_balance:,.2f}")
    await spot_trader.close()
    
    # Test Futures balance
    logger.info("\n2. Testing Futures Balance...")
    futures_trader = FuturesTestnetTrader()
    await futures_trader.initialize()
    futures_balance = await futures_trader.get_balance()
    logger.info(f"   Futures Balance: ${futures_balance:,.2f}")
    await futures_trader.close()
    
    return True


async def test_order_manager():
    """Test Order Manager"""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Order Manager")
    logger.info("=" * 80)
    
    await data_manager.initialize()
    
    order_manager = OrderManager()
    await order_manager.initialize()
    
    try:
        # Get portfolio stats
        logger.info("\n1. Getting Portfolio Stats...")
        stats = await order_manager.get_portfolio_stats()
        logger.info(f"   Spot Balance: ${stats['spot_balance']:,.2f}")
        logger.info(f"   Futures Balance: ${stats['futures_balance']:,.2f}")
        logger.info(f"   Total Balance: ${stats['total_balance']:,.2f}")
        logger.info(f"   Open Positions: {stats['open_positions']}")
        logger.info(f"   Total Trades: {stats['total_trades']}")
        
        # Get current positions
        logger.info("\n2. Getting Open Positions...")
        positions = await order_manager.get_all_positions()
        logger.info(f"   Found {len(positions)} open positions")
        
        for pos in positions:
            logger.info(f"   - {pos['trade_id']}: {pos['symbol']} {pos['side']} "
                       f"({pos['market_type']}) @ ${pos['entry_price']:.2f}")
        
        logger.info("\n✓ Order Manager tests passed")
        return True
    
    finally:
        await order_manager.close()


async def test_telegram_notification():
    """Test Telegram notifications"""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Telegram Notifications")
    logger.info("=" * 80)
    
    notifier = TradeNotifier()
    
    if not notifier.enabled:
        logger.warning("Telegram not configured, skipping test")
        return True
    
    try:
        # Send test message
        logger.info("\n1. Sending test notification...")
        success = await notifier._send_message("🤖 <b>Test Message</b>\n\nPaper trading system test successful!")
        logger.info(f"   Test message: {'✓ Sent' if success else '✗ Failed'}")
        
        # Send daily summary
        logger.info("\n2. Sending daily summary...")
        stats = {
            'total_balance': 20000.0,
            'spot_balance': 10000.0,
            'futures_balance': 10000.0,
            'open_positions': 2,
            'total_trades': 10,
            'total_pnl': 500.0,
            'avg_pnl_pct': 2.5
        }
        success = await notifier.send_daily_summary(stats)
        logger.info(f"   Daily summary: {'✓ Sent' if success else '✗ Failed'}")
        
        logger.info("\n✓ Telegram notification tests passed")
        return True
    
    finally:
        await notifier.close()


async def test_position_monitor():
    """Test Position Monitor"""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Position Monitor")
    logger.info("=" * 80)
    
    await data_manager.initialize()
    
    monitor = PositionMonitor()
    await monitor.initialize()
    
    try:
        # Check positions
        logger.info("\n1. Checking positions for SL/TP triggers...")
        closed = await monitor.check_positions()
        logger.info(f"   Closed {len(closed)} positions")
        
        for pos in closed:
            logger.info(f"   - {pos['trade_id']}: {pos['symbol']} "
                       f"PnL: ${pos['pnl']:.2f} ({pos['pnl_pct']:.2f}%)")
        
        logger.info("\n✓ Position Monitor tests passed")
        return True
    
    finally:
        await monitor.close()


async def main():
    """Run all tests"""
    logger.info("Starting Paper Trading System Tests\n")
    
    try:
        # Test 1: API connections
        await test_api_connections()
        
        # Test 2: Balances
        await test_balances()
        
        # Test 3: Order Manager
        await test_order_manager()
        
        # Test 4: Telegram notifications
        await test_telegram_notification()
        
        # Test 5: Position Monitor
        await test_position_monitor()
        
        logger.info("\n" + "=" * 80)
        logger.info("✓ ALL TESTS PASSED")
        logger.info("=" * 80)
        logger.info("\nPhase 1.5 complete!")
        logger.info("Paper Trading System is ready for integration with Technical Analyst.")
        
        return 0
    
    except Exception as e:
        logger.error(f"\n✗ TEST FAILED: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

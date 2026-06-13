"""
Futures Testnet Trader - Paper trading with Binance Futures Testnet
"""
import os
from typing import Dict, Optional, List
from datetime import datetime
from utils import get_logger, config
from dataflows import BinanceFuturesClient
from state import db
from .base_trader import BaseTrader, TradeResult, TradeSide, MarketType, CloseReason, ClosedPosition


logger = get_logger(__name__)


class FuturesTestnetTrader(BaseTrader):
    """Futures Testnet trader"""
    
    def __init__(self, config_override: Optional[Dict] = None):
        super().__init__("FuturesTestnetTrader", config_override)
        
        # Load config
        default_config = config.load_default_params()
        demo_config = default_config.get('demo_trading', {})
        self.config = {**demo_config, **(config_override or {})}
        
        # Initialize client
        self.client = BinanceFuturesClient(
            api_key=os.getenv('BINANCE_FUTURES_TESTNET_API_KEY'),
            api_secret=os.getenv('BINANCE_FUTURES_TESTNET_SECRET'),
            environment='testnet'
        )
        
        # Fees
        self.maker_fee = self.config.get('fees', {}).get('futures_maker', 0.0002)
        self.taker_fee = self.config.get('fees', {}).get('futures_taker', 0.0005)
        
        # Leverage settings
        self.leverage_by_confidence = self.config.get('market_selection', {}).get('leverage_by_confidence', {
            'high': 10,
            'medium': 5,
            'low': 3
        })
        
        self.max_leverage = self.config.get('market_selection', {}).get('max_futures_leverage', 10)
    
    async def initialize(self):
        """Initialize the trader"""
        if self._initialized:
            return
        
        # Check API connection
        is_healthy = await self.client.health_check()
        if not is_healthy:
            logger.error("Futures Testnet API is not accessible")
            raise Exception("Futures Testnet API health check failed")
        
        # Get initial balance
        balance = await self.get_balance()
        logger.info(f"FuturesTestnetTrader initialized - Balance: ${balance:.2f}")
        
        self._initialized = True
    
    async def get_balance(self) -> float:
        """Get USDT balance"""
        return await self.client.get_balance('USDT')
    
    def _calculate_leverage(self, confidence: float) -> int:
        """Calculate leverage based on confidence"""
        if confidence >= 0.8:
            return self.leverage_by_confidence['high']
        elif confidence >= 0.6:
            return self.leverage_by_confidence['medium']
        else:
            return self.leverage_by_confidence['low']
    
    async def _setup_symbol(self, symbol: str, leverage: int):
        """Setup symbol with leverage and margin type"""
        # Set margin type to ISOLATED (ignore error if already set)
        try:
            await self.client.set_margin_type(symbol, 'ISOLATED')
        except Exception as e:
            # Ignore "No need to change margin type" error
            if "No need to change margin type" not in str(e):
                logger.warning(f"Error setting margin type: {e}")
        
        # Set leverage
        await self.client.set_leverage(symbol, leverage)
    
    async def place_trade(
        self,
        symbol: str,
        side: TradeSide,
        quantity: float,
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        signal_data: Optional[Dict] = None
    ) -> TradeResult:
        """Place a futures trade"""
        if not self._initialized:
            await self.initialize()
        
        # Generate trade ID
        trade_id = self._generate_trade_id(symbol, side)
        
        # Get confidence from signal data
        confidence = signal_data.get('confidence', 0.5) if signal_data else 0.5
        leverage = self._calculate_leverage(confidence)
        leverage = min(leverage, self.max_leverage)
        
        try:
            # Setup symbol
            await self._setup_symbol(symbol, leverage)
            
            # Determine order side
            order_side = 'BUY' if side == TradeSide.LONG else 'SELL'
            # Use BOTH for one-way position mode (default on Binance)
            position_side = 'BOTH'
            
            # Place market order
            order = await self.client.place_order(
                symbol=symbol,
                side=order_side,
                order_type='MARKET',
                quantity=quantity,
                position_side=position_side
            )
            
            if 'error' in order:
                logger.error(f"Failed to place futures order: {order['error']}")
                return TradeResult(
                    success=False,
                    trade_id=trade_id,
                    symbol=symbol,
                    side=side,
                    market_type=MarketType.FUTURES,
                    entry_price=0,
                    quantity=0,
                    error_message=order['error']
                )
            
            # Get entry price
            # For market orders, avgPrice might be 0 or empty initially
            avg_price = order.get('avgPrice')
            if avg_price and float(avg_price) > 0:
                entry_price = float(avg_price)
            elif price:
                # Use the price parameter passed to the function
                entry_price = float(price)
            else:
                # Fallback: query order status to get actual fill price
                order_id = order.get('orderId')
                if order_id:
                    order_status = await self.client.get_order(symbol, order_id)
                    avg_price = order_status.get('avgPrice')
                    entry_price = float(avg_price) if avg_price and float(avg_price) > 0 else 0
                else:
                    entry_price = 0
            
            order_id = str(order.get('orderId', ''))
            
            # Calculate fees
            fees = entry_price * quantity * self.taker_fee
            
            # Save position to database
            position_data = {
                'trade_id': trade_id,
                'symbol': symbol,
                'side': side.value,
                'market_type': MarketType.FUTURES.value,
                'entry_price': entry_price,
                'quantity': quantity,
                'leverage': leverage,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'signal_data': signal_data or {},
                'order_id': order_id,
                'position_group_id': (signal_data or {}).get('position_group_id') or trade_id,
                'entry_kind': (signal_data or {}).get('entry_kind', 'base'),
                'dca_index': (signal_data or {}).get('dca_index', 0),
            }
            
            await db.insert_paper_position(position_data)
            
            logger.info(f"Futures trade opened: {trade_id} - {side.value} {quantity} {symbol} @ ${entry_price:.2f} (Leverage: {leverage}x)")
            
            return TradeResult(
                success=True,
                trade_id=trade_id,
                symbol=symbol,
                side=side,
                market_type=MarketType.FUTURES,
                entry_price=entry_price,
                quantity=quantity,
                leverage=leverage,
                stop_loss=stop_loss,
                take_profit=take_profit,
                order_id=order_id
            )
        
        except Exception as e:
            logger.error(f"Error placing futures trade: {e}", exc_info=True)
            return TradeResult(
                success=False,
                trade_id=trade_id,
                symbol=symbol,
                side=side,
                market_type=MarketType.FUTURES,
                entry_price=0,
                quantity=0,
                error_message=str(e)
            )
    
    async def close_position(
        self,
        trade_id: str,
        close_price: Optional[float] = None,
        reason: CloseReason = CloseReason.MANUAL,
        close_quantity: Optional[float] = None,
    ) -> Optional[ClosedPosition]:
        """Close a futures position (partial if close_quantity provided and less than full)"""
        if not self._initialized:
            await self.initialize()
        
        # Get position from database
        positions = await db.get_open_positions()
        position = next((p for p in positions if p['trade_id'] == trade_id), None)
        
        if not position:
            logger.error(f"Position not found: {trade_id}")
            return None

        full_quantity = position['quantity']
        partial = close_quantity is not None and close_quantity < full_quantity
        exec_quantity = close_quantity if partial else full_quantity

        try:
            # Determine close order side
            if position['side'] == 'LONG':
                order_side = 'SELL'
            else:
                order_side = 'BUY'
            
            # Place close order (use BOTH for one-way mode)
            order = await self.client.place_order(
                symbol=position['symbol'],
                side=order_side,
                order_type='MARKET',
                quantity=exec_quantity,
                position_side='BOTH',
                reduce_only=True
            )
            
            if 'error' in order:
                logger.error(f"Failed to close futures position: {order['error']}")
                return None

            # Get exit price (avgPrice may be 0/empty on market orders; fall back to order status)
            raw_avg = order.get('avgPrice')
            if raw_avg and float(raw_avg) > 0:
                exit_price = float(raw_avg)
            else:
                order_id = order.get('orderId')
                if order_id:
                    try:
                        order_status = await self.client.get_order(position['symbol'], int(order_id))
                        status_avg = order_status.get('avgPrice')
                        if status_avg and float(status_avg) > 0:
                            exit_price = float(status_avg)
                        else:
                            exit_price = float(close_price or 0)
                    except Exception as e:
                        logger.warning(f"Failed to fetch close order status for {trade_id}: {e}")
                        exit_price = float(close_price or 0)
                else:
                    exit_price = float(close_price or 0)
            
            # Calculate PnL
            entry_price = position['entry_price']
            leverage = position['leverage']
            
            if position['side'] == 'LONG':
                gross_pnl = (exit_price - entry_price) * exec_quantity
            else:
                gross_pnl = (entry_price - exit_price) * exec_quantity
            
            # Apply leverage
            leveraged_pnl = gross_pnl * leverage
            
            # Calculate fees
            fees = (entry_price * exec_quantity * self.taker_fee) + (exit_price * exec_quantity * self.taker_fee)
            net_pnl = leveraged_pnl - fees
            pnl_pct = (net_pnl / (entry_price * exec_quantity)) * 100 if exec_quantity > 0 else 0.0
            
            if partial:
                remaining = full_quantity - exec_quantity
                effective_reason = CloseReason.PARTIAL_REDUCE
                await db.update_position_quantity(trade_id, remaining)
                await db.insert_partial_reduce(
                    trade_id=trade_id,
                    symbol=position['symbol'],
                    side=TradeSide(position['side']),
                    market_type=MarketType.FUTURES,
                    entry_price=entry_price,
                    exit_price=exit_price,
                    reduced_quantity=exec_quantity,
                    remaining_quantity=remaining,
                    pnl=net_pnl,
                    pnl_pct=pnl_pct,
                    fees=fees,
                    close_reason=effective_reason.value,
                    original_close_reason=reason.value,
                )
            else:
                effective_reason = reason
                await db.close_paper_position(
                    trade_id=trade_id,
                    close_price=exit_price,
                    pnl=net_pnl,
                    pnl_pct=pnl_pct,
                    close_reason=effective_reason.value,
                    fees=fees,
                )
            
            # Create closed position object
            closed_position = ClosedPosition(
                trade_id=trade_id,
                symbol=position['symbol'],
                side=TradeSide(position['side']),
                market_type=MarketType.FUTURES,
                entry_price=entry_price,
                exit_price=exit_price,
                quantity=exec_quantity,
                leverage=leverage,
                pnl=net_pnl,
                pnl_pct=pnl_pct,
                fees=fees,
                close_reason=effective_reason,
                opened_at=datetime.fromtimestamp(position['opened_at']),
                closed_at=datetime.now(),
                duration_seconds=int(datetime.now().timestamp() - position['opened_at'])
            )
            
            logger.info(f"Futures position closed: {trade_id} - PnL: ${net_pnl:.2f} ({pnl_pct:.2f}%)")
            
            return closed_position
        
        except Exception as e:
            logger.error(f"Error closing futures position: {e}", exc_info=True)
            return None
    
    async def get_positions(self) -> List[Dict]:
        """Get all open futures positions"""
        positions = await db.get_open_positions()
        return [p for p in positions if p['market_type'] == MarketType.FUTURES.value]
    
    async def close(self):
        """Close client session"""
        await self.client.close()

"""
Spot Demo Trader - Paper trading with Binance Spot Demo Mode
"""
import os
import math
from typing import Dict, Optional, List
from datetime import datetime
from utils import get_logger, config
from dataflows import BinanceClient
from state import db
from .base_trader import BaseTrader, TradeResult, TradeSide, MarketType, CloseReason, ClosedPosition


logger = get_logger(__name__)


class SpotDemoTrader(BaseTrader):
    """Spot Demo Mode trader"""
    
    def __init__(self, config_override: Optional[Dict] = None):
        super().__init__("SpotDemoTrader", config_override)
        
        # Load config
        default_config = config.load_default_params()
        demo_config = default_config.get('demo_trading', {})
        self.config = {**demo_config, **(config_override or {})}
        
        # Initialize client
        self.client = BinanceClient(
            api_key=os.getenv('BINANCE_DEMO_API_KEY'),
            api_secret=os.getenv('BINANCE_DEMO_SECRET'),
            environment='demo'
        )
        
        # Fees
        self.maker_fee = self.config.get('fees', {}).get('spot_maker', 0.001)
        self.taker_fee = self.config.get('fees', {}).get('spot_taker', 0.001)
    
    async def initialize(self):
        """Initialize the trader"""
        if self._initialized:
            return
        
        # Check API connection
        is_healthy = await self.client.health_check()
        if not is_healthy:
            logger.error("Spot Demo API is not accessible")
            raise Exception("Spot Demo API health check failed")
        
        # Get initial balance
        balance = await self.get_balance()
        logger.info(f"SpotDemoTrader initialized - Balance: ${balance:.2f}")
        
        self._initialized = True
    
    async def get_balance(self) -> float:
        """Get USDT balance"""
        return await self.client.get_balance('USDT')

    def _extract_base_asset(self, symbol: str) -> str:
        """Extract base asset from a USDT spot pair."""
        if symbol.endswith('USDT'):
            return symbol[:-4]
        return symbol

    def _floor_quantity(self, quantity: float, asset: str) -> float:
        """Round down to Binance-style quantity precision for common assets."""
        precision_map = {
            'BTC': 3, 'ETH': 3, 'SOL': 1, 'BNB': 2, 'XRP': 1, 'ADA': 1, 'DOGE': 0,
        }
        precision = precision_map.get(asset, 2)
        factor = 10 ** precision
        return math.floor(quantity * factor) / factor
    
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
        """
        Place a spot trade
        
        Note: Spot only supports LONG (buy low, sell high)
        """
        if not self._initialized:
            await self.initialize()
        
        if side == TradeSide.SHORT:
            logger.warning("Spot trading does not support SHORT positions")
            return TradeResult(
                success=False,
                trade_id="",
                symbol=symbol,
                side=side,
                market_type=MarketType.SPOT,
                entry_price=0,
                quantity=0,
                error_message="Spot trading does not support SHORT positions"
            )
        
        # Generate trade ID
        trade_id = self._generate_trade_id(symbol, side)
        
        try:
            # Place market order
            order = await self.client.place_order(
                symbol=symbol,
                side='BUY',
                order_type='MARKET',
                quantity=quantity
            )
            
            if 'error' in order:
                logger.error(f"Failed to place order: {order['error']}")
                return TradeResult(
                    success=False,
                    trade_id=trade_id,
                    symbol=symbol,
                    side=side,
                    market_type=MarketType.SPOT,
                    entry_price=0,
                    quantity=0,
                    error_message=order['error']
                )
            
            # Get entry price
            entry_price = float(order.get('fills', [{}])[0].get('price', price or 0))
            order_id = str(order.get('orderId', ''))
            
            # Calculate fees
            fees = entry_price * quantity * self.taker_fee
            
            # Save position to database
            position_data = {
                'trade_id': trade_id,
                'symbol': symbol,
                'side': side.value,
                'market_type': MarketType.SPOT.value,
                'entry_price': entry_price,
                'quantity': quantity,
                'leverage': 1.0,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'signal_data': signal_data or {},
                'order_id': order_id,
                'position_group_id': (signal_data or {}).get('position_group_id') or trade_id,
                'entry_kind': (signal_data or {}).get('entry_kind', 'base'),
                'dca_index': (signal_data or {}).get('dca_index', 0),
            }
            
            await db.insert_paper_position(position_data)
            
            logger.info(f"Spot trade opened: {trade_id} - BUY {quantity} {symbol} @ ${entry_price:.2f}")
            
            return TradeResult(
                success=True,
                trade_id=trade_id,
                symbol=symbol,
                side=side,
                market_type=MarketType.SPOT,
                entry_price=entry_price,
                quantity=quantity,
                leverage=1.0,
                stop_loss=stop_loss,
                take_profit=take_profit,
                order_id=order_id
            )
        
        except Exception as e:
            logger.error(f"Error placing spot trade: {e}", exc_info=True)
            return TradeResult(
                success=False,
                trade_id=trade_id,
                symbol=symbol,
                side=side,
                market_type=MarketType.SPOT,
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
        """Close a spot position (partial if close_quantity provided and less than full)"""
        if not self._initialized:
            await self.initialize()
        
        # Get position from database
        positions = await db.get_open_positions()
        position = next((p for p in positions if p['trade_id'] == trade_id), None)
        
        if not position:
            logger.error(f"Position not found: {trade_id}")
            return None

        full_quantity = position['quantity']
        requested_partial = close_quantity is not None and close_quantity < full_quantity
        requested_quantity = close_quantity if requested_partial else full_quantity
        base_asset = self._extract_base_asset(position['symbol'])
        free_balance = await self.client.get_balance(base_asset)
        exec_quantity = min(requested_quantity, free_balance)
        exec_quantity = self._floor_quantity(exec_quantity, base_asset)

        if exec_quantity <= 0:
            logger.error(
                f"Insufficient {base_asset} balance to close position: "
                f"trade_id={trade_id} requested={requested_quantity:.8f} free={free_balance:.8f}"
            )
            return None

        if exec_quantity < requested_quantity:
            logger.warning(
                f"Adjusted close quantity for {trade_id}: requested={requested_quantity:.8f} "
                f"free_{base_asset}={free_balance:.8f} selling={exec_quantity:.8f}"
            )

        partial = requested_partial

        try:
            # Place sell order
            order = await self.client.place_order(
                symbol=position['symbol'],
                side='SELL',
                order_type='MARKET',
                quantity=exec_quantity
            )
            
            if 'error' in order:
                logger.error(f"Failed to close position: {order['error']}")
                return None
            
            # Get exit price
            exit_price = float(order.get('fills', [{}])[0].get('price', close_price or 0))
            
            # Calculate PnL
            entry_price = position['entry_price']
            gross_pnl = (exit_price - entry_price) * exec_quantity
            fees = (entry_price * exec_quantity * self.taker_fee) + (exit_price * exec_quantity * self.taker_fee)
            net_pnl = gross_pnl - fees
            pnl_pct = (net_pnl / (entry_price * exec_quantity)) * 100 if exec_quantity > 0 else 0.0
            
            if partial:
                remaining = full_quantity - exec_quantity
                effective_reason = CloseReason.PARTIAL_REDUCE
                await db.update_position_quantity(trade_id, remaining)
                await db.insert_partial_reduce(
                    trade_id=trade_id,
                    symbol=position['symbol'],
                    side=TradeSide(position['side']),
                    market_type=MarketType.SPOT,
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
                market_type=MarketType.SPOT,
                entry_price=entry_price,
                exit_price=exit_price,
                quantity=exec_quantity,
                leverage=1.0,
                pnl=net_pnl,
                pnl_pct=pnl_pct,
                fees=fees,
                close_reason=effective_reason,
                opened_at=datetime.fromtimestamp(position['opened_at']),
                closed_at=datetime.now(),
                duration_seconds=int(datetime.now().timestamp() - position['opened_at'])
            )
            
            logger.info(f"Spot position closed: {trade_id} - PnL: ${net_pnl:.2f} ({pnl_pct:.2f}%)")
            
            return closed_position
        
        except Exception as e:
            logger.error(f"Error closing spot position: {e}", exc_info=True)
            return None
    
    async def get_positions(self) -> List[Dict]:
        """Get all open spot positions"""
        positions = await db.get_open_positions()
        return [p for p in positions if p['market_type'] == MarketType.SPOT.value]
    
    async def close(self):
        """Close client session"""
        await self.client.close()

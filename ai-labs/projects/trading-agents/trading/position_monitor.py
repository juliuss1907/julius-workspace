"""
Position Monitor - Monitor open positions for SL/TP triggers
"""
from typing import Dict, Optional, List
from datetime import datetime
from utils import get_logger, config
from dataflows import data_manager
from state import db
from .base_trader import CloseReason, MarketType
from .spot_demo_trader import SpotDemoTrader
from .futures_testnet_trader import FuturesTestnetTrader


logger = get_logger(__name__)


class PositionMonitor:
    """Monitor open positions for SL/TP triggers"""
    
    def __init__(self, config_override: Optional[Dict] = None):
        # Load config
        default_config = config.load_default_params()
        self.config = default_config.get('take_profit', {})
        
        # Trailing stop settings
        trailing_config = self.config.get('trailing_stop', {})
        self.trailing_enabled = trailing_config.get('enabled', True)
        self.trailing_activation_pct = trailing_config.get('activation_pct', 0.03)
        self.trailing_pct = trailing_config.get('trail_pct', 0.015)
        
        # Initialize traders
        self.spot_trader = SpotDemoTrader()
        self.futures_trader = FuturesTestnetTrader()
        
        self._initialized = False
    
    async def initialize(self):
        """Initialize position monitor"""
        if self._initialized:
            return
        
        await self.spot_trader.initialize()
        await self.futures_trader.initialize()
        
        logger.info("PositionMonitor initialized")
        self._initialized = True
    
    async def check_positions(self) -> List[Dict]:
        """
        Check all open positions for SL/TP triggers
        
        Returns:
            List of closed positions
        """
        if not self._initialized:
            await self.initialize()
        
        positions = await db.get_open_positions()
        closed_positions = []
        closed_groups = set()

        for position in positions:
            group_id = position.get('position_group_id')
            if group_id and group_id in closed_groups:
                continue
            # Get current price
            ticker = await data_manager.get_ticker(position['symbol'])
            if not ticker:
                logger.warning(f"Could not get ticker for {position['symbol']}")
                continue
            
            current_price = ticker['price']
            
            # Check SL/TP
            close_reason = self._check_sl_tp(position, current_price)
            
            if close_reason:
                # DCA group behavior: one triggered leg closes the whole group.
                legs_to_close = [position]
                if group_id:
                    legs_to_close = [p for p in positions if p.get('position_group_id') == group_id]
                    closed_groups.add(group_id)

                for leg in legs_to_close:
                    closed = await self._close_leg(leg, current_price, close_reason)
                    if closed:
                        closed_positions.append({
                            'trade_id': closed.trade_id,
                            'symbol': closed.symbol,
                            'side': closed.side.value,
                            'market_type': closed.market_type.value,
                            'entry_price': closed.entry_price,
                            'exit_price': closed.exit_price,
                            'pnl': closed.pnl,
                            'pnl_pct': closed.pnl_pct,
                            'close_reason': closed.close_reason.value
                        })
            
            # Update trailing stop if enabled
            elif self.trailing_enabled:
                await self._update_trailing_stop(position, current_price)
        
        return closed_positions

    async def _close_leg(self, position: Dict, current_price: float, close_reason: CloseReason):
        if position['market_type'] == MarketType.FUTURES.value:
            return await self.futures_trader.close_position(
                position['trade_id'], close_price=current_price, reason=close_reason,
            )
        return await self.spot_trader.close_position(
            position['trade_id'], close_price=current_price, reason=close_reason,
        )
    
    def _check_sl_tp(self, position: Dict, current_price: float) -> Optional[CloseReason]:
        """
        Check if SL or TP is hit
        
        Returns:
            CloseReason if triggered, None otherwise
        """
        side = position['side']
        stop_loss = position.get('stop_loss')
        take_profit = position.get('take_profit')
        trailing_stop = position.get('trailing_stop')
        
        if side == 'LONG':
            # Check stop loss
            if stop_loss and current_price <= stop_loss:
                logger.info(f"SL hit for {position['trade_id']}: ${current_price:.2f} <= ${stop_loss:.2f}")
                return CloseReason.SL_HIT
            
            # Check trailing stop
            if trailing_stop and current_price <= trailing_stop:
                logger.info(f"Trailing stop hit for {position['trade_id']}: ${current_price:.2f} <= ${trailing_stop:.2f}")
                return CloseReason.TRAILING_STOP
            
            # Check take profit
            if take_profit and current_price >= take_profit:
                logger.info(f"TP hit for {position['trade_id']}: ${current_price:.2f} >= ${take_profit:.2f}")
                return CloseReason.TP_HIT
        
        else:  # SHORT
            # Check stop loss
            if stop_loss and current_price >= stop_loss:
                logger.info(f"SL hit for {position['trade_id']}: ${current_price:.2f} >= ${stop_loss:.2f}")
                return CloseReason.SL_HIT
            
            # Check trailing stop
            if trailing_stop and current_price >= trailing_stop:
                logger.info(f"Trailing stop hit for {position['trade_id']}: ${current_price:.2f} >= ${trailing_stop:.2f}")
                return CloseReason.TRAILING_STOP
            
            # Check take profit
            if take_profit and current_price <= take_profit:
                logger.info(f"TP hit for {position['trade_id']}: ${current_price:.2f} <= ${take_profit:.2f}")
                return CloseReason.TP_HIT
        
        return None
    
    async def _update_trailing_stop(self, position: Dict, current_price: float):
        """Update trailing stop for profitable positions"""
        side = position['side']
        entry_price = position['entry_price']
        trailing_stop = position.get('trailing_stop')
        trailing_activated = position.get('trailing_activated', 0)
        
        if side == 'LONG':
            # Calculate profit percentage
            profit_pct = (current_price - entry_price) / entry_price
            
            # Check if trailing should be activated
            if not trailing_activated and profit_pct >= self.trailing_activation_pct:
                # Activate trailing stop
                new_trailing_stop = current_price * (1 - self.trailing_pct)
                await db.update_position_trailing_stop(
                    position['trade_id'],
                    new_trailing_stop,
                    activated=True
                )
                logger.info(f"Trailing stop activated for {position['trade_id']}: ${new_trailing_stop:.2f}")
            
            # Update trailing stop if price moved up
            elif trailing_activated and trailing_stop:
                new_trailing_stop = current_price * (1 - self.trailing_pct)
                if new_trailing_stop > trailing_stop:
                    await db.update_position_trailing_stop(
                        position['trade_id'],
                        new_trailing_stop,
                        activated=True
                    )
                    logger.debug(f"Trailing stop updated for {position['trade_id']}: ${new_trailing_stop:.2f}")
        
        else:  # SHORT
            # Calculate profit percentage
            profit_pct = (entry_price - current_price) / entry_price
            
            # Check if trailing should be activated
            if not trailing_activated and profit_pct >= self.trailing_activation_pct:
                # Activate trailing stop
                new_trailing_stop = current_price * (1 + self.trailing_pct)
                await db.update_position_trailing_stop(
                    position['trade_id'],
                    new_trailing_stop,
                    activated=True
                )
                logger.info(f"Trailing stop activated for {position['trade_id']}: ${new_trailing_stop:.2f}")
            
            # Update trailing stop if price moved down
            elif trailing_activated and trailing_stop:
                new_trailing_stop = current_price * (1 + self.trailing_pct)
                if new_trailing_stop < trailing_stop:
                    await db.update_position_trailing_stop(
                        position['trade_id'],
                        new_trailing_stop,
                        activated=True
                    )
                    logger.debug(f"Trailing stop updated for {position['trade_id']}: ${new_trailing_stop:.2f}")
    
    async def close(self):
        """Close all traders"""
        await self.spot_trader.close()
        await self.futures_trader.close()

"""
Order Manager - Coordinates trading across spot and futures
"""
import time
from typing import Dict, Optional, List
from datetime import datetime
from utils import get_logger, config
from agents.base_agent import AgentResult, SignalDirection
from state import db
from .base_trader import TradeResult, TradeSide, MarketType, CloseReason, ClosedPosition
from .spot_demo_trader import SpotDemoTrader
from .futures_testnet_trader import FuturesTestnetTrader


logger = get_logger(__name__)


class OrderManager:
    """Coordinates trading across spot and futures markets"""

    def __init__(
        self,
        config_override: Optional[Dict] = None,
        notifier: Optional[object] = None,
        entry_guard: Optional[object] = None,
    ):
        # Optional notifier for manual close position_event messages.
        # If not provided, the caller can still call notify_position_event
        # separately. The OrderManager only emits position_event when a
        # notifier is injected, to keep this class loosely coupled.
        self._notifier = notifier
        # Optional entry guard for permanent policy enforcement.
        self._entry_guard = entry_guard

        # Load config
        default_config = config.load_default_params()
        demo_config = default_config.get('demo_trading', {})
        self.config = {**demo_config, **(config_override or {})}
        
        # Initialize traders
        self.spot_trader = SpotDemoTrader()
        self.futures_trader = FuturesTestnetTrader()
        
        # Market selection settings
        self.market_selection = self.config.get('market_selection', {})
        self.futures_allowed_coins = self.market_selection.get('futures_allowed_coins', ['BTC', 'ETH', 'SOL'])
        self.futures_on_downtrend = self.market_selection.get('futures_on_downtrend', True)
        
        # Risk management
        risk_config = default_config.get('risk_management', {})
        self.risk_per_trade = risk_config.get('risk_per_trade', 0.03)
        self.max_position_size = risk_config.get('max_position_size', 0.30)
        self.max_open_positions = risk_config.get('max_open_positions', 5)
        
        # Auto-execute settings
        auto_execute = self.config.get('auto_execute', {})
        self.min_confidence = auto_execute.get('min_confidence', 0.70)
        self.max_trades_per_day = auto_execute.get('max_trades_per_day', 10)
        
        self._initialized = False
    
    async def initialize(self):
        """Initialize order manager"""
        if self._initialized:
            return
        
        await self.spot_trader.initialize()
        await self.futures_trader.initialize()
        
        logger.info("OrderManager initialized")
        self._initialized = True
    
    def _extract_coin_from_symbol(self, symbol: str) -> str:
        """Extract coin name from symbol (e.g., BTCUSDT -> BTC)"""
        if symbol.endswith('USDT'):
            return symbol[:-4]
        return symbol
    
    def _round_quantity(self, quantity: float, symbol: str, market_type: str) -> float:
        """
        Round quantity to correct precision for the symbol
        
        Args:
            quantity: Raw quantity
            symbol: Trading pair (e.g., BTCUSDT)
            market_type: 'spot' or 'futures'
        
        Returns:
            Rounded quantity
        """
        # Precision rules for common symbols
        # Spot: stepSize determines precision
        # Futures: stepSize determines precision
        
        coin = self._extract_coin_from_symbol(symbol)
        
        # Common precision rules
        precision_map = {
            'BTC': 3,   # 0.001
            'ETH': 3,   # 0.001
            'SOL': 1,   # 0.1
            'BNB': 2,   # 0.01
            'XRP': 1,   # 0.1
            'ADA': 1,   # 0.1
            'DOGE': 0,  # 1
        }
        
        precision = precision_map.get(coin, 2)  # Default 2 decimals
        
        # Round to precision
        rounded = round(quantity, precision)
        
        # Ensure minimum quantity (at least 0.001 for most coins)
        min_qty = 10 ** (-precision)
        if rounded < min_qty:
            rounded = min_qty
        
        return rounded
    
    def _should_use_futures(self, symbol: str, signal: AgentResult) -> bool:
        """
        Determine if should use futures for this trade
        
        Rules:
        - Use futures for: downtrend, or coins with low volatility + large cap (BTC, ETH, SOL)
        - Use spot for: uptrend with smaller coins
        """
        coin = self._extract_coin_from_symbol(symbol)
        
        # Check if coin is allowed for futures
        if coin not in self.futures_allowed_coins:
            return False
        
        # Check if signal is bearish (downtrend)
        if signal.direction == SignalDirection.BEARISH and self.futures_on_downtrend:
            return True
        
        # Check regime
        regime = signal.metadata.get('regime', '')
        if regime == 'trend_down' and self.futures_on_downtrend:
            return True
        
        # For large cap coins in ranging market, can use futures for both directions
        if coin in ['BTC', 'ETH', 'SOL'] and regime in ['ranging', 'trend_up']:
            return True
        
        return False
    
    def _calculate_position_size(
        self,
        balance: float,
        price: float,
        atr: float,
        confidence: float,
        stop_loss_distance_pct: float
    ) -> float:
        """
        Calculate position size based on risk parameters
        
        Formula:
        position_size = (balance * risk_per_trade) / (stop_loss_distance * price)
        
        Adjusted by confidence level
        """
        # Base risk amount
        risk_amount = balance * self.risk_per_trade
        
        # Adjust by confidence
        if confidence >= 0.8:
            confidence_multiplier = 1.0
        elif confidence >= 0.6:
            confidence_multiplier = 0.75
        else:
            confidence_multiplier = 0.5
        
        risk_amount *= confidence_multiplier
        
        # Calculate position size
        if stop_loss_distance_pct > 0:
            position_size = risk_amount / (stop_loss_distance_pct * price)
        else:
            # Fallback: use ATR-based calculation
            atr_multiplier = 2.0
            stop_distance = atr * atr_multiplier
            position_size = risk_amount / stop_distance
        
        # Apply max position size constraint
        max_position_value = balance * self.max_position_size
        max_position_size = max_position_value / price
        
        position_size = min(position_size, max_position_size)
        
        return position_size
    
    async def execute_signal(
        self,
        signal: AgentResult,
        current_price: float,
        atr: float,
        risk_decision: Optional[Dict] = None,
    ) -> Optional[TradeResult]:
        """
        Execute trade based on signal

        Args:
            signal: AgentResult from Technical Analyst
            current_price: Current market price
            atr: Average True Range for position sizing
            risk_decision: Optional RiskManager approval with sizing hints

        Returns:
            TradeResult if trade was executed, None otherwise
        """
        if not self._initialized:
            await self.initialize()

        # Check confidence threshold
        if signal.confidence < self.min_confidence:
            logger.info(f"Signal confidence {signal.confidence:.2f} below threshold {self.min_confidence}")
            return None
        
        # Check if signal is actionable
        if signal.direction == SignalDirection.NEUTRAL:
            logger.info(f"Signal is neutral, skipping")
            return None
        
        # Check max open positions
        open_positions = await db.get_open_positions()
        if len(open_positions) >= self.max_open_positions:
            logger.warning(f"Max open positions reached ({self.max_open_positions})")
            return None
        
        # Check if already have position for this symbol.
        # Without EntryGuard, keep the old conservative behavior.
        # With EntryGuard, same-side entries may be DCA-approved; opposite
        # side has already been blocked by EntryGuard before this point.
        symbol = signal.symbol
        existing_position = next((p for p in open_positions if p['symbol'] == symbol), None)
        if existing_position and self._entry_guard is None:
            logger.info(f"Already have open position for {symbol}")
            return None
        
        # Determine market type
        use_futures = self._should_use_futures(symbol, signal)
        
        # Get balance
        if use_futures:
            balance = await self.futures_trader.get_balance()
            trader = self.futures_trader
        else:
            balance = await self.spot_trader.get_balance()
            trader = self.spot_trader
        
        if balance <= 0:
            logger.error("Insufficient balance")
            return None
        
        # Calculate stop loss distance
        stop_loss_pct = 0.02  # Default 2%
        if signal.analysis.get('indicators', {}).get('atr'):
            atr_value = signal.analysis['indicators']['atr']
            stop_loss_pct = (atr_value * 2) / current_price  # 2x ATR
        
        # Calculate position size
        position_size = self._calculate_position_size(
            balance=balance,
            price=current_price,
            atr=atr,
            confidence=signal.confidence,
            stop_loss_distance_pct=stop_loss_pct
        )
        risk_multiplier = 1.0
        if risk_decision:
            risk_multiplier = max(0.0, min(1.0, risk_decision.get('position_size_multiplier', 1.0)))
            position_size *= risk_multiplier
        
        # Round quantity to correct precision
        market_type = 'futures' if use_futures else 'spot'
        position_size = self._round_quantity(position_size, symbol, market_type)
        
        # Calculate SL/TP
        if signal.direction == SignalDirection.BULLISH:
            side = TradeSide.LONG
            stop_loss = current_price * (1 - stop_loss_pct)
            take_profit = current_price * (1 + stop_loss_pct * 2)  # 2:1 R/R
        else:  # BEARISH
            side = TradeSide.SHORT
            stop_loss = current_price * (1 + stop_loss_pct)
            take_profit = current_price * (1 - stop_loss_pct * 2)

        entry_guard_decision = None
        if self._entry_guard is not None:
            try:
                async def _get_open_positions(sym: str):
                    return await self._open_positions_for_guard(sym)

                portfolio_value = 0.0
                try:
                    stats = await self.get_portfolio_stats()
                    portfolio_value = float(stats.get('total_balance') or 0.0)
                except Exception as e:
                    logger.warning(f"Entry guard portfolio value unavailable: {e}")

                proposed_notional = current_price * position_size
                proposed_leverage = 1.0
                if use_futures:
                    proposed_leverage = min(
                        float(self.futures_trader._calculate_leverage(signal.confidence)),
                        float(self.futures_trader.max_leverage),
                    )

                entry_guard_decision = await self._entry_guard.check(
                    symbol=symbol,
                    side=side.value,
                    current_price=current_price,
                    confidence=signal.confidence,
                    get_open_positions=_get_open_positions,
                    proposed_notional=proposed_notional,
                    portfolio_value=portfolio_value,
                    leverage=proposed_leverage,
                )
                if not entry_guard_decision.allowed:
                    logger.info(
                        f"Entry guard blocked {symbol} {side.value}: {entry_guard_decision.reason} "
                        f"({entry_guard_decision.details})"
                    )
                    if self._entry_guard.notify_on_block and self._notifier is not None:
                        try:
                            await self._notifier._send_message(
                                f"🛡️ <b>Entry Blocked</b>\n"
                                f"<b>Symbol:</b> {symbol}\n"
                                f"<b>Side:</b> {side.value}\n"
                                f"<b>Reason:</b> {entry_guard_decision.reason}\n"
                                f"<b>Details:</b> {entry_guard_decision.details}"
                            )
                        except Exception as e:
                            logger.warning(f"notify_on_block failed: {e}")
                    return None
            except Exception as e:
                logger.error(f"Entry guard check failed (continuing without guard): {e}")
        
        # Prepare signal data
        signal_data = {
            'confidence': signal.confidence,
            'score': signal.sub_score,
            'direction': signal.direction.value,
            'reasoning': signal.reasoning,
            'regime': signal.metadata.get('regime', 'unknown'),
            'risk_level': risk_decision.get('risk_level') if risk_decision else None,
            'risk_multiplier': risk_multiplier,
            'risk_reason': risk_decision.get('reason') if risk_decision else None,
        }
        if entry_guard_decision:
            signal_data['entry_guard'] = entry_guard_decision.to_dict()
            signal_data['position_group_id'] = entry_guard_decision.details.get('position_group_id')
            signal_data['entry_kind'] = entry_guard_decision.details.get('entry_kind', 'base')
            signal_data['dca_index'] = entry_guard_decision.details.get('dca_index', 0)
        
        # Execute trade
        result = await trader.place_trade(
            symbol=symbol,
            side=side,
            quantity=position_size,
            price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            signal_data=signal_data
        )
        
        if result.success:
            logger.info(f"Trade executed: {result.trade_id} - {side.value} {position_size:.6f} {symbol} @ ${current_price:.2f}")
        else:
            logger.error(f"Trade execution failed: {result.error_message}")
        
        return result
    
    async def close_position(self, trade_id: str, reason: CloseReason = CloseReason.MANUAL) -> bool:
        """Close a position by trade ID and emit position_event notification.

        Returns True if Binance-side close succeeded, False otherwise.
        Notification policy:
          - success: position_closed (spot: SPOT SELL EXECUTED,
                     futures: FUTURES POSITION CLOSED)
          - failure: position_close_failed (spot: SPOT SELL FAILED,
                     futures: FUTURES CLOSE FAILED)
        Notifications are only emitted if a notifier was injected.
        """
        if not self._initialized:
            await self.initialize()

        # Find position
        positions = await db.get_open_positions()
        position = next((p for p in positions if p['trade_id'] == trade_id), None)

        if not position:
            logger.error(f"Position not found: {trade_id}")
            await self._notify_close_event(
                symbol=trade_id.split("_")[0] if "_" in trade_id else trade_id,
                side="",
                market_type="",
                action="close_position",
                reason="position_not_found",
                close_reason=reason.value,
                execution_status="position_close_failed",
                requested_qty=0.0,
                executed_qty=0.0,
                trade_id=trade_id,
            )
            return False

        market_type = position.get('market_type', '')
        symbol = position.get('symbol', '')
        side = position.get('side', '')
        full_qty = float(position.get('quantity', 0.0))
        is_futures = market_type == MarketType.FUTURES.value
        is_spot = market_type == MarketType.SPOT.value

        # Use appropriate trader
        closed: Optional[ClosedPosition] = None
        if is_futures:
            closed = await self.futures_trader.close_position(trade_id, reason=reason)
        elif is_spot:
            closed = await self.spot_trader.close_position(trade_id, reason=reason)
        else:
            logger.error(f"Unknown market_type '{market_type}' for {trade_id}")
            return False

        success = closed is not None
        await self._notify_close_event(
            symbol=symbol,
            side=side,
            market_type=market_type,
            action="close_position",
            reason=reason.value,
            close_reason=reason.value,
            execution_status="position_closed" if success else "position_close_failed",
            requested_qty=full_qty,
            executed_qty=(closed.quantity if success else 0.0),
            trade_id=trade_id,
            closed=closed,
            success=success,
        )
        return success

    async def _notify_close_event(
        self,
        symbol: str,
        side: str,
        market_type: str,
        action: str,
        reason: str,
        close_reason: str,
        execution_status: str,
        requested_qty: float,
        executed_qty: float,
        trade_id: str,
        closed: Optional[ClosedPosition] = None,
        success: Optional[bool] = None,
    ) -> None:
        """Best-effort emit of position_event after a manual close.

        Silently no-ops if no notifier was injected. Failures are logged
        and never block the close flow.
        """
        if self._notifier is None:
            return
        if success is None:
            success = execution_status.endswith("closed") or execution_status == "position_closed"
        try:
            await self._notifier.notify_position_event(
                symbol=symbol,
                action=action,
                reason=reason,
                close_reason=close_reason,
                final_direction="N/A",
                final_confidence=0.0,
                execution_status=execution_status,
                mode="manual_close",
                market_type=market_type,
                position_side=side if market_type == MarketType.FUTURES.value else "",
                requested_qty=requested_qty,
                executed_qty=executed_qty,
                trade_id=trade_id,
            )
        except Exception as e:
            logger.warning(f"close_position notify failed for {trade_id}: {e}")

    async def close_position_group(
        self,
        position_group_id: str,
        reason: CloseReason = CloseReason.MANUAL,
    ) -> bool:
        """Close every open leg in a DCA group, one DB leg at a time.

        Option 1 (DB-first): each leg is closed via close_position(trade_id),
        preserving per-leg accounting and auditability. If any leg fails,
        remaining failures are left open and a warning is emitted.
        """
        if not position_group_id:
            logger.error("close_position_group requires position_group_id")
            return False
        if not self._initialized:
            await self.initialize()

        legs = await self._open_group_positions(position_group_id)
        if not legs:
            logger.warning(f"No open legs found for group {position_group_id}")
            return False

        ok_all = True
        failed = []
        for leg in legs:
            trade_id = leg.get('trade_id')
            ok = await self.close_position(trade_id, reason=reason) if trade_id else False
            if not ok:
                ok_all = False
                failed.append(trade_id)

        if not ok_all:
            logger.error(
                f"GROUP CLOSE PARTIAL FAILURE group={position_group_id} failed={failed}"
            )
            if self._notifier is not None:
                try:
                    await self._notifier._send_message(
                        f"⚠️ <b>GROUP CLOSE PARTIAL FAILURE</b>\n"
                        f"<b>Group:</b> {position_group_id}\n"
                        f"<b>Failed legs:</b> {failed}"
                    )
                except Exception as e:
                    logger.warning(f"group close failure notify failed: {e}")
        return ok_all

    async def reduce_position(self, trade_id: str, fraction: float, reason: CloseReason = CloseReason.RISK_REDUCTION) -> bool:
        """Partially reduce a position by the given fraction (0 < fraction < 1)"""
        if not self._initialized:
            await self.initialize()

        if fraction <= 0 or fraction >= 1:
            logger.warning(f"Reduce fraction must be in (0, 1), got {fraction:.2f}")
            return False

        positions = await db.get_open_positions()
        position = next((p for p in positions if p['trade_id'] == trade_id), None)

        if not position:
            logger.error(f"Position not found: {trade_id}")
            return False

        full_quantity = position['quantity']
        reduce_quantity = full_quantity * fraction
        remaining = full_quantity - reduce_quantity

        coin = self._extract_coin_from_symbol(position['symbol'])
        min_qty = 10.0 ** -self._precision_for_coin(coin)

        if remaining < min_qty:
            logger.info(f"Remaining quantity ({remaining:.6f}) below min, closing full position instead")
            if position['market_type'] == MarketType.FUTURES.value:
                closed = await self.futures_trader.close_position(trade_id, reason=reason)
            else:
                closed = await self.spot_trader.close_position(trade_id, reason=reason)
            return closed is not None

        if position['market_type'] == MarketType.FUTURES.value:
            closed = await self.futures_trader.close_position(trade_id, reason=reason, close_quantity=reduce_quantity)
        else:
            closed = await self.spot_trader.close_position(trade_id, reason=reason, close_quantity=reduce_quantity)

        return closed is not None

    def _precision_for_coin(self, coin: str) -> int:
        precision_map = {
            'BTC': 3, 'ETH': 3, 'SOL': 1, 'BNB': 2, 'XRP': 1, 'ADA': 1, 'DOGE': 0,
        }
        return precision_map.get(coin, 2)

    async def _open_positions_for_guard(self, symbol: str) -> List[Dict]:
        """Return all open positions for symbol.

        Used by EntryGuard for opposite-side blocking and DCA checks.
        """
        try:
            async with db._conn.execute(
                """
                SELECT trade_id, symbol, side, market_type, status,
                       entry_price, quantity
                FROM paper_positions
                WHERE symbol = ? AND status = 'open'
                ORDER BY opened_at ASC
                """,
                (symbol,),
            ) as cur:
                rows = await cur.fetchall()
            cols = [c[0] for c in cur.description]
            return [dict(zip(cols, r)) for r in rows]
        except Exception as e:
            logger.warning(f"_open_positions_for_guard failed: {e}")
            return []

    async def _open_group_positions(self, position_group_id: str) -> List[Dict]:
        """Return all open legs for a position group."""
        try:
            async with db._conn.execute(
                """
                SELECT trade_id, symbol, side, market_type, status,
                       entry_price, quantity, position_group_id, entry_kind, dca_index
                FROM paper_positions
                WHERE position_group_id = ? AND status = 'open'
                ORDER BY dca_index ASC, opened_at ASC
                """,
                (position_group_id,),
            ) as cur:
                rows = await cur.fetchall()
            cols = [c[0] for c in cur.description]
            return [dict(zip(cols, r)) for r in rows]
        except Exception as e:
            logger.warning(f"_open_group_positions failed: {e}")
            return []

    async def get_all_positions(self) -> List[Dict]:
        """Get all open positions"""
        return await db.get_open_positions()
    
    async def get_portfolio_stats(self) -> Dict:
        """Get portfolio statistics"""
        spot_balance = await self.spot_trader.get_balance()
        futures_balance = await self.futures_trader.get_balance()
        
        stats = await db.get_portfolio_stats()
        
        return {
            'spot_balance': spot_balance,
            'futures_balance': futures_balance,
            'total_balance': spot_balance + futures_balance,
            'open_positions': stats['open_positions_count'],
            'total_trades': stats['total_trades'],
            'total_pnl': stats['total_pnl'],
            'avg_pnl_pct': stats['avg_pnl_pct']
        }
    
    async def close(self):
        """Close all traders"""
        await self.spot_trader.close()
        await self.futures_trader.close()

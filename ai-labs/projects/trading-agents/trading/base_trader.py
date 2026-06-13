"""
Base Trader - Abstract base class for paper trading
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TradeSide(Enum):
    """Trade side"""
    LONG = "LONG"
    SHORT = "SHORT"


class MarketType(Enum):
    """Market type"""
    SPOT = "spot"
    FUTURES = "futures"


class CloseReason(Enum):
    """Reason for closing position"""
    SL_HIT = "sl_hit"
    TP_HIT = "tp_hit"
    TRAILING_STOP = "trailing_stop"
    MANUAL = "manual"
    TIMEOUT = "timeout"
    ERROR = "error"
    SIGNAL_REVERSAL = "signal_reversal"
    RISK_REDUCTION = "risk_reduction"
    LOSS_CONTROL = "loss_control"
    PROFIT_PROTECTION = "profit_protection"
    PARTIAL_REDUCE = "partial_reduce"


@dataclass
class TradeResult:
    """Result of a trade operation"""
    success: bool
    trade_id: str
    symbol: str
    side: TradeSide
    market_type: MarketType
    entry_price: float
    quantity: float
    leverage: float = 1.0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    order_id: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'success': self.success,
            'trade_id': self.trade_id,
            'symbol': self.symbol,
            'side': self.side.value,
            'market_type': self.market_type.value,
            'entry_price': self.entry_price,
            'quantity': self.quantity,
            'leverage': self.leverage,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'order_id': self.order_id,
            'error_message': self.error_message,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class ClosedPosition:
    """Represents a closed position"""
    trade_id: str
    symbol: str
    side: TradeSide
    market_type: MarketType
    entry_price: float
    exit_price: float
    quantity: float
    leverage: float
    pnl: float
    pnl_pct: float
    fees: float
    close_reason: CloseReason
    opened_at: datetime
    closed_at: datetime
    duration_seconds: int


class BaseTrader(ABC):
    """Abstract base class for traders"""
    
    def __init__(self, name: str, config: Optional[Dict] = None):
        self.name = name
        self.config = config or {}
        self._initialized = False
    
    @abstractmethod
    async def initialize(self):
        """Initialize the trader"""
        pass
    
    @abstractmethod
    async def get_balance(self) -> float:
        """Get available balance"""
        pass
    
    @abstractmethod
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
        Place a trade
        
        Args:
            symbol: Trading pair
            side: LONG or SHORT
            quantity: Trade quantity
            price: Entry price (for limit orders)
            stop_loss: Stop loss price
            take_profit: Take profit price
            signal_data: Signal data that triggered this trade
        
        Returns:
            TradeResult
        """
        pass
    
    @abstractmethod
    async def close_position(
        self,
        trade_id: str,
        close_price: Optional[float] = None,
        reason: CloseReason = CloseReason.MANUAL
    ) -> Optional[ClosedPosition]:
        """
        Close a position
        
        Args:
            trade_id: Trade ID to close
            close_price: Close price (for limit orders)
            reason: Reason for closing
        
        Returns:
            ClosedPosition if successful, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_positions(self) -> List[Dict]:
        """Get all open positions"""
        pass
    
    async def close(self):
        """Clean up resources"""
        pass
    
    def _generate_trade_id(self, symbol: str, side: TradeSide) -> str:
        """Generate unique trade ID"""
        timestamp = int(datetime.now().timestamp() * 1000)
        return f"{symbol}_{side.value}_{timestamp}"

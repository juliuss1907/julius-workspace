"""
Pure strategy-layer contracts.

This module defines the dataclasses and enums used by the strategy layer.
It is intentionally stdlib-only and must not import execution, runtime,
order, position, or notification modules.
"""
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional


class StrategyAction(str, Enum):
    """Discrete actions a strategy signal may request."""
    LONG = "long"
    SHORT = "short"
    HOLD = "hold"
    SKIP = "skip"
    EXIT = "exit"
    REDUCE = "reduce"


class StrategyFamily(str, Enum):
    """Strategy family identifiers.

    mean_reversion is reserved as a Phase 2 placeholder; no active
    implementation should live in this milestone.
    """
    TREND_FOLLOWING = "trend_following"
    BREAKOUT = "breakout"
    VOLATILITY_SKIP = "volatility_skip"
    MEAN_REVERSION = "mean_reversion"  # Phase 2 placeholder only


@dataclass
class TechnicalState:
    """Normalized technical indicator snapshot used by strategy policies."""
    close: Optional[float] = None
    rsi: Optional[float] = None
    macd_histogram: Optional[float] = None
    macd_crossing_up: bool = False
    macd_crossing_down: bool = False
    bb_position: Optional[float] = None
    atr: Optional[float] = None
    ema_20: Optional[float] = None
    ema_50: Optional[float] = None
    ema_200: Optional[float] = None
    volume: Optional[float] = None
    obv: Optional[float] = None
    obv_prev: Optional[float] = None
    recent_high_20: Optional[float] = None
    recent_low_20: Optional[float] = None
    breakout_up_20: bool = False
    breakout_down_20: bool = False
    scores: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class MarketState:
    """Normalized market-regime snapshot used by strategy policies."""
    regime: str = "ranging"
    confidence: float = 0.5
    trend_direction: str = "neutral"
    trend_strength: float = 0.0
    adx: float = 0.0
    bb_width: Optional[float] = None
    reason: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class StrategySignal:
    """Output of a single strategy policy evaluation.

    Pure data object — no execution concerns. The downstream policy layer
    (demo execution / manual report) decides what to do with the signal.
    """
    strategy_id: str
    family: str
    action: str
    confidence: float
    setup: str = ""
    trigger: str = ""
    invalidation: str = ""
    sizing_hint: str = ""
    exit_plan: str = ""
    no_trade_reason: Optional[str] = None
    risk_notes: List[str] = field(default_factory=list)
    attribution: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)

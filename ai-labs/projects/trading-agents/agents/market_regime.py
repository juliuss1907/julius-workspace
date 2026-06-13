"""
Market Regime Detection
"""
from typing import Dict, List
from enum import Enum
from agents.indicators import Indicators
from utils import get_logger


logger = get_logger(__name__)


class MarketRegime(Enum):
    """Market regime types"""
    TREND_UP = "trend_up"
    TREND_DOWN = "trend_down"
    RANGING = "ranging"
    VOLATILE = "volatile"


class MarketRegimeDetector:
    """Detects current market regime"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # Thresholds
        self.adx_trend_threshold = self.config.get("adx_trend_threshold", 25)
        self.adx_strong_trend = self.config.get("adx_strong_trend", 50)
        self.bb_width_volatile = self.config.get("bb_width_volatile", 0.10)
        self.bb_width_ranging = self.config.get("bb_width_ranging", 0.04)
    
    def detect(
        self,
        closes: List[float],
        highs: List[float],
        lows: List[float],
        volumes: List[float]
    ) -> Dict:
        """
        Detect market regime
        
        Args:
            closes: Close prices
            highs: High prices
            lows: Low prices
            volumes: Volume data
        
        Returns:
            Dict with regime info:
            - regime: MarketRegime enum
            - confidence: 0.0-1.0
            - adx: ADX value
            - bb_width: Bollinger Band width
            - trend_strength: Trend strength indicator
        """
        if len(closes) < 50:
            return {
                "regime": MarketRegime.RANGING,
                "confidence": 0.3,
                "adx": 0,
                "bb_width": 0,
                "trend_strength": 0,
                "reason": "Insufficient data"
            }
        
        # Calculate indicators
        adx = self._calculate_adx(highs, lows, closes, period=14)
        bb_upper, bb_middle, bb_lower = Indicators.bollinger_bands(closes, period=20)
        
        # Get latest values
        latest_adx = adx[-1] if adx and not self._is_nan(adx[-1]) else 0
        latest_bb_upper = bb_upper[-1] if bb_upper and not self._is_nan(bb_upper[-1]) else closes[-1]
        latest_bb_lower = bb_lower[-1] if bb_lower and not self._is_nan(bb_lower[-1]) else closes[-1]
        latest_bb_middle = bb_middle[-1] if bb_middle and not self._is_nan(bb_middle[-1]) else closes[-1]
        latest_close = closes[-1]
        
        # Calculate BB width
        if latest_bb_middle > 0:
            bb_width = (latest_bb_upper - latest_bb_lower) / latest_bb_middle
        else:
            bb_width = 0
        
        # Determine trend direction (using EMA slope)
        ema_short = Indicators.ema(closes, 20)
        ema_long = Indicators.ema(closes, 50)
        
        latest_ema_short = ema_short[-1] if ema_short and not self._is_nan(ema_short[-1]) else latest_close
        latest_ema_long = ema_long[-1] if ema_long and not self._is_nan(ema_long[-1]) else latest_close
        
        # Trend direction
        if latest_ema_short > latest_ema_long * 1.01:
            trend_up = True
        elif latest_ema_short < latest_ema_long * 0.99:
            trend_up = False
        else:
            trend_up = None  # No clear trend
        
        # Determine regime
        regime, confidence, reason = self._classify_regime(
            latest_adx, bb_width, trend_up, latest_close, latest_bb_middle
        )
        
        # Trend strength (0-100)
        trend_strength = min(100, latest_adx * 2)
        
        return {
            "regime": regime,
            "confidence": confidence,
            "adx": latest_adx,
            "bb_width": bb_width,
            "trend_strength": trend_strength,
            "trend_direction": "up" if trend_up else ("down" if trend_up is False else "neutral"),
            "reason": reason
        }
    
    def _classify_regime(
        self,
        adx: float,
        bb_width: float,
        trend_up: bool,
        price: float,
        bb_middle: float
    ) -> tuple:
        """
        Classify market regime based on indicators
        
        Returns:
            Tuple of (MarketRegime, confidence, reason)
        """
        # High volatility (wide Bollinger Bands)
        if bb_width >= self.bb_width_volatile:
            return (
                MarketRegime.VOLATILE,
                min(0.9, 0.5 + (bb_width - self.bb_width_volatile) * 5),
                f"High volatility (BB width: {bb_width:.2%})"
            )
        
        # Strong trend (high ADX)
        if adx >= self.adx_trend_threshold:
            if trend_up is True:
                confidence = min(0.95, 0.6 + (adx - self.adx_trend_threshold) / 100)
                return (
                    MarketRegime.TREND_UP,
                    confidence,
                    f"Strong uptrend (ADX: {adx:.1f})"
                )
            elif trend_up is False:
                confidence = min(0.95, 0.6 + (adx - self.adx_trend_threshold) / 100)
                return (
                    MarketRegime.TREND_DOWN,
                    confidence,
                    f"Strong downtrend (ADX: {adx:.1f})"
                )
            else:
                # ADX high but no clear direction - volatile
                return (
                    MarketRegime.VOLATILE,
                    0.6,
                    f"High ADX but unclear direction (ADX: {adx:.1f})"
                )
        
        # Narrow Bollinger Bands - ranging
        if bb_width <= self.bb_width_ranging:
            confidence = min(0.9, 0.6 + (self.bb_width_ranging - bb_width) * 10)
            return (
                MarketRegime.RANGING,
                confidence,
                f"Narrow Bollinger Bands (width: {bb_width:.2%})"
            )
        
        # Default: ranging with moderate confidence
        return (
            MarketRegime.RANGING,
            0.5,
            f"No clear regime (ADX: {adx:.1f}, BB width: {bb_width:.2%})"
        )
    
    def _calculate_adx(
        self,
        highs: List[float],
        lows: List[float],
        closes: List[float],
        period: int = 14
    ) -> List[float]:
        """
        Calculate Average Directional Index (ADX)
        
        Simplified implementation
        """
        if len(closes) < period * 2:
            return [float('nan')] * len(closes)
        
        # Calculate +DM and -DM
        plus_dm = [0.0]
        minus_dm = [0.0]
        
        for i in range(1, len(closes)):
            high_diff = highs[i] - highs[i-1]
            low_diff = lows[i-1] - lows[i]
            
            if high_diff > low_diff and high_diff > 0:
                plus_dm.append(high_diff)
            else:
                plus_dm.append(0.0)
            
            if low_diff > high_diff and low_diff > 0:
                minus_dm.append(low_diff)
            else:
                minus_dm.append(0.0)
        
        # Calculate TR
        tr = [0.0]
        for i in range(1, len(closes)):
            high_low = highs[i] - lows[i]
            high_close = abs(highs[i] - closes[i-1])
            low_close = abs(lows[i] - closes[i-1])
            tr.append(max(high_low, high_close, low_close))
        
        # Smooth with Wilder's method
        atr = self._wilder_smooth(tr, period)
        plus_dm_smooth = self._wilder_smooth(plus_dm, period)
        minus_dm_smooth = self._wilder_smooth(minus_dm, period)
        
        # Calculate +DI and -DI
        plus_di = []
        minus_di = []
        
        for i in range(len(atr)):
            if atr[i] > 0:
                plus_di.append((plus_dm_smooth[i] / atr[i]) * 100)
                minus_di.append((minus_dm_smooth[i] / atr[i]) * 100)
            else:
                plus_di.append(0.0)
                minus_di.append(0.0)
        
        # Calculate DX
        dx = []
        for i in range(len(plus_di)):
            di_sum = plus_di[i] + minus_di[i]
            if di_sum > 0:
                dx.append((abs(plus_di[i] - minus_di[i]) / di_sum) * 100)
            else:
                dx.append(0.0)
        
        # ADX is smoothed DX
        adx = self._wilder_smooth(dx, period)
        
        return adx
    
    def _wilder_smooth(self, data: List[float], period: int) -> List[float]:
        """Wilder's smoothing method"""
        if len(data) < period:
            return [0.0] * len(data)
        
        result = [0.0] * (period - 1)
        
        # First value is simple average
        first_val = sum(data[1:period+1]) / period
        result.append(first_val)
        
        # Rest is smoothed: previous - (previous / period) + current
        for i in range(period + 1, len(data)):
            smoothed = result[-1] - (result[-1] / period) + data[i]
            result.append(smoothed)
        
        return result
    
    def _is_nan(self, value: float) -> bool:
        """Check if value is NaN"""
        return value != value  # NaN != NaN

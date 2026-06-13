"""
Technical Indicators
"""
import numpy as np
from typing import List, Dict, Tuple
from utils import get_logger


logger = get_logger(__name__)


class Indicators:
    """Technical indicators calculator"""
    
    @staticmethod
    def sma(data: List[float], period: int) -> List[float]:
        """
        Simple Moving Average
        
        Args:
            data: Price data
            period: SMA period
        
        Returns:
            SMA values (same length as input, NaN for first period-1 values)
        """
        if len(data) < period:
            return [float('nan')] * len(data)
        
        result = [float('nan')] * (period - 1)
        
        for i in range(period - 1, len(data)):
            window = data[i - period + 1:i + 1]
            result.append(sum(window) / period)
        
        return result
    
    @staticmethod
    def ema(data: List[float], period: int) -> List[float]:
        """
        Exponential Moving Average
        
        Args:
            data: Price data
            period: EMA period
        
        Returns:
            EMA values
        """
        if len(data) < period:
            return [float('nan')] * len(data)
        
        multiplier = 2 / (period + 1)
        result = [float('nan')] * (period - 1)
        
        # First EMA is SMA
        first_sma = sum(data[:period]) / period
        result.append(first_sma)
        
        # Calculate rest
        for i in range(period, len(data)):
            ema = (data[i] - result[-1]) * multiplier + result[-1]
            result.append(ema)
        
        return result
    
    @staticmethod
    def rsi(data: List[float], period: int = 14) -> List[float]:
        """
        Relative Strength Index
        
        Args:
            data: Price data (closes)
            period: RSI period (default: 14)
        
        Returns:
            RSI values (0-100)
        """
        if len(data) < period + 1:
            return [float('nan')] * len(data)
        
        # Calculate price changes
        deltas = [data[i] - data[i-1] for i in range(1, len(data))]
        
        # Separate gains and losses
        gains = [max(d, 0) for d in deltas]
        losses = [abs(min(d, 0)) for d in deltas]
        
        # Initial average gain/loss
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        result = [float('nan')] * period
        
        # First RSI
        if avg_loss == 0:
            rs = 100
        else:
            rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        result.append(rsi)
        
        # Rest of RSI values
        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
            if avg_loss == 0:
                rs = 100
            else:
                rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            result.append(rsi)
        
        return result
    
    @staticmethod
    def macd(
        data: List[float],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Tuple[List[float], List[float], List[float]]:
        """
        MACD (Moving Average Convergence Divergence)
        
        Args:
            data: Price data (closes)
            fast_period: Fast EMA period (default: 12)
            slow_period: Slow EMA period (default: 26)
            signal_period: Signal line period (default: 9)
        
        Returns:
            Tuple of (macd_line, signal_line, histogram)
        """
        fast_ema = Indicators.ema(data, fast_period)
        slow_ema = Indicators.ema(data, slow_period)
        
        # MACD line = Fast EMA - Slow EMA
        macd_line = [
            f - s if not (np.isnan(f) or np.isnan(s)) else float('nan')
            for f, s in zip(fast_ema, slow_ema)
        ]
        
        # Signal line = EMA of MACD line
        valid_macd = [m for m in macd_line if not np.isnan(m)]
        if len(valid_macd) < signal_period:
            signal_line = [float('nan')] * len(macd_line)
            histogram = [float('nan')] * len(macd_line)
            return macd_line, signal_line, histogram
        
        signal_ema = Indicators.ema(valid_macd, signal_period)
        
        # Pad signal line with NaN
        signal_line = [float('nan')] * (len(macd_line) - len(signal_ema)) + signal_ema
        
        # Histogram = MACD - Signal
        histogram = [
            m - s if not (np.isnan(m) or np.isnan(s)) else float('nan')
            for m, s in zip(macd_line, signal_line)
        ]
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def bollinger_bands(
        data: List[float],
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[List[float], List[float], List[float]]:
        """
        Bollinger Bands
        
        Args:
            data: Price data (closes)
            period: SMA period (default: 20)
            std_dev: Standard deviation multiplier (default: 2.0)
        
        Returns:
            Tuple of (upper_band, middle_band, lower_band)
        """
        if len(data) < period:
            return (
                [float('nan')] * len(data),
                [float('nan')] * len(data),
                [float('nan')] * len(data)
            )
        
        middle = Indicators.sma(data, period)
        upper = [float('nan')] * len(data)
        lower = [float('nan')] * len(data)
        
        for i in range(period - 1, len(data)):
            window = data[i - period + 1:i + 1]
            mean = middle[i]
            variance = sum((x - mean) ** 2 for x in window) / period
            std = variance ** 0.5
            
            upper[i] = mean + (std_dev * std)
            lower[i] = mean - (std_dev * std)
        
        return upper, middle, lower
    
    @staticmethod
    def atr(
        highs: List[float],
        lows: List[float],
        closes: List[float],
        period: int = 14
    ) -> List[float]:
        """
        Average True Range (ATR)
        
        Args:
            highs: High prices
            lows: Low prices
            closes: Close prices
            period: ATR period (default: 14)
        
        Returns:
            ATR values
        """
        if len(closes) < period + 1:
            return [float('nan')] * len(closes)
        
        # Calculate True Range
        tr = [float('nan')]  # First value is NaN
        
        for i in range(1, len(closes)):
            high_low = highs[i] - lows[i]
            high_close = abs(highs[i] - closes[i-1])
            low_close = abs(lows[i] - closes[i-1])
            true_range = max(high_low, high_close, low_close)
            tr.append(true_range)
        
        # Calculate ATR
        result = [float('nan')] * period
        
        # First ATR is simple average
        first_atr = sum(tr[1:period+1]) / period
        result.append(first_atr)
        
        # Rest is smoothed
        for i in range(period + 1, len(closes)):
            atr = (result[-1] * (period - 1) + tr[i]) / period
            result.append(atr)
        
        return result
    
    @staticmethod
    def obv(closes: List[float], volumes: List[float]) -> List[float]:
        """
        On-Balance Volume (OBV)
        
        Args:
            closes: Close prices
            volumes: Volume data
        
        Returns:
            OBV values
        """
        if len(closes) < 2:
            return [0.0] * len(closes)
        
        result = [0.0]
        
        for i in range(1, len(closes)):
            if closes[i] > closes[i-1]:
                # Price up, add volume
                obv = result[-1] + volumes[i]
            elif closes[i] < closes[i-1]:
                # Price down, subtract volume
                obv = result[-1] - volumes[i]
            else:
                # Price unchanged
                obv = result[-1]
            result.append(obv)
        
        return result
    
    @staticmethod
    def stochastic(
        highs: List[float],
        lows: List[float],
        closes: List[float],
        k_period: int = 14,
        d_period: int = 3
    ) -> Tuple[List[float], List[float]]:
        """
        Stochastic Oscillator (%K and %D)
        
        Args:
            highs: High prices
            lows: Low prices
            closes: Close prices
            k_period: %K period (default: 14)
            d_period: %D period (default: 3)
        
        Returns:
            Tuple of (%K, %D)
        """
        if len(closes) < k_period:
            return (
                [float('nan')] * len(closes),
                [float('nan')] * len(closes)
            )
        
        k_values = [float('nan')] * (k_period - 1)
        
        for i in range(k_period - 1, len(closes)):
            window_highs = highs[i - k_period + 1:i + 1]
            window_lows = lows[i - k_period + 1:i + 1]
            
            highest_high = max(window_highs)
            lowest_low = min(window_lows)
            
            if highest_high == lowest_low:
                k = 50.0
            else:
                k = ((closes[i] - lowest_low) / (highest_high - lowest_low)) * 100
            
            k_values.append(k)
        
        # %D is SMA of %K
        valid_k = [k for k in k_values if not np.isnan(k)]
        if len(valid_k) < d_period:
            d_values = [float('nan')] * len(k_values)
        else:
            d_sma = Indicators.sma(valid_k, d_period)
            d_values = [float('nan')] * (len(k_values) - len(d_sma)) + d_sma
        
        return k_values, d_values

"""
Technical Analyst Agent
"""
from datetime import datetime
from typing import Dict, List, Optional
from agents.base_agent import BaseAgent, AgentResult, SignalDirection
from agents.indicators import Indicators
from agents.market_regime import MarketRegimeDetector, MarketRegime
from strategies.contracts import MarketState, TechnicalState
from utils import get_logger, config


logger = get_logger(__name__)


class TechnicalAnalyst(BaseAgent):
    """
    Technical Analyst Agent
    
    Analyzes price action, indicators, and market regime to generate
    trading signals with sub-scores.
    """
    
    def __init__(self, config_override: Optional[Dict] = None):
        super().__init__("TechnicalAnalyst", config_override)

        # Load config with canonical technical_indicators mapping + legacy fallback
        default_config = config.load_default_params()
        self.config = self._load_indicator_config(default_config, config_override)

        # Initialize components
        self.regime_detector = MarketRegimeDetector(self.config.get("regime", {}))

        # Indicator parameters
        self.rsi_period = self.config.get("rsi_period", 14)
        self.macd_fast = self.config.get("macd_fast", 12)
        self.macd_slow = self.config.get("macd_slow", 26)
        self.macd_signal = self.config.get("macd_signal", 9)
        self.bb_period = self.config.get("bb_period", 20)
        self.bb_std = self.config.get("bb_std", 2.0)
        self.atr_period = self.config.get("atr_period", 14)

        # Scoring weights
        self.weights = self.config.get("weights", {
            "trend": 0.30,
            "momentum": 0.25,
            "volatility": 0.20,
            "volume": 0.15,
            "regime": 0.10
        })

        # Thresholds
        self.rsi_overbought = self.config.get("rsi_overbought", 70)
        self.rsi_oversold = self.config.get("rsi_oversold", 30)
        self.rsi_strong_overbought = self.config.get("rsi_strong_overbought", 80)
        self.rsi_strong_oversold = self.config.get("rsi_strong_oversold", 20)

    @staticmethod
    def _load_indicator_config(
        default_config: Dict,
        config_override: Optional[Dict] = None,
    ) -> Dict:
        """Map canonical `technical_indicators` config + legacy overrides.

        Precedence (highest to lowest):
        1. explicit config_override
        2. legacy `technical_analysis` block
        3. canonical `technical_indicators` block
        4. hard-coded defaults
        """
        legacy = default_config.get("technical_analysis", {})
        canonical = default_config.get("technical_indicators", {})

        mapped = {
            "rsi_period": canonical.get("rsi", {}).get("period", 14),
            "rsi_oversold": canonical.get("rsi", {}).get("oversold", 30),
            "rsi_overbought": canonical.get("rsi", {}).get("overbought", 70),
            "macd_fast": canonical.get("macd", {}).get("fast", 12),
            "macd_slow": canonical.get("macd", {}).get("slow", 26),
            "macd_signal": canonical.get("macd", {}).get("signal", 9),
            "bb_period": canonical.get("bollinger_bands", {}).get("period", 20),
            "bb_std": canonical.get("bollinger_bands", {}).get("std_dev", 2.0),
            "atr_period": canonical.get("atr", {}).get("period", 14),
        }

        return {**mapped, **legacy, **(config_override or {})}
    
    async def initialize(self):
        """Initialize the agent"""
        if self._initialized:
            return
        
        logger.info("TechnicalAnalyst initialized")
        self._initialized = True
    
    async def analyze(self, symbol: str, data: Dict) -> AgentResult:
        """
        Perform technical analysis
        
        Args:
            symbol: Trading pair symbol
            data: Dict containing:
                - ohlcv: List of OHLCV candles
                - timeframe: Timeframe string
                - fundamentals: Optional fundamental data
        
        Returns:
            AgentResult with analysis
        """
        if not self._initialized:
            await self.initialize()
        
        ohlcv = data.get("ohlcv", [])
        timeframe = data.get("timeframe", "1h")
        
        if len(ohlcv) < 50:
            logger.warning(f"{symbol}: Insufficient data ({len(ohlcv)} candles)")
            return self._create_neutral_result(symbol, "Insufficient data")
        
        # Extract price data
        closes = [c["close"] for c in ohlcv]
        highs = [c["high"] for c in ohlcv]
        lows = [c["low"] for c in ohlcv]
        volumes = [c["volume"] for c in ohlcv]
        
        # Calculate all indicators
        indicators = self._calculate_indicators(closes, highs, lows, volumes)
        
        # Detect market regime
        regime_data = self.regime_detector.detect(closes, highs, lows, volumes)
        
        # Calculate sub-scores
        scores = self._calculate_scores(indicators, regime_data, closes, volumes)

        # Calculate overall sub-score
        sub_score = self._calculate_overall_score(scores)

        # Determine direction
        direction = self._determine_direction(sub_score)

        # Generate reasoning
        reasoning = self._generate_reasoning(scores, regime_data, indicators)

        # Build normalized strategy-layer state snapshots
        technical_state = self._build_technical_state(indicators, scores)
        market_state = self._build_market_state(regime_data)

        # Build analysis dict
        analysis = {
            "indicators": indicators,
            "regime": {
                "type": regime_data["regime"].value,
                "confidence": regime_data["confidence"],
                "adx": regime_data["adx"],
                "trend_strength": regime_data["trend_strength"],
                "reason": regime_data["reason"]
            },
            "scores": scores,
            "technical_state": technical_state.to_dict(),
            "market_state": market_state.to_dict(),
            "timeframe": timeframe,
            "candles_analyzed": len(ohlcv)
        }
        
        # Calculate confidence based on data quality and regime clarity
        confidence = self._calculate_confidence(scores, regime_data, len(ohlcv))
        
        return AgentResult(
            agent_name=self.name,
            symbol=symbol,
            timestamp=datetime.now(),
            direction=direction,
            sub_score=sub_score,
            confidence=confidence,
            analysis=analysis,
            reasoning=reasoning,
            metadata={
                "timeframe": timeframe,
                "regime": regime_data["regime"].value
            }
        )
    
    def _calculate_indicators(
        self,
        closes: List[float],
        highs: List[float],
        lows: List[float],
        volumes: List[float]
    ) -> Dict:
        """Calculate all technical indicators"""
        
        # RSI
        rsi = Indicators.rsi(closes, self.rsi_period)
        
        # MACD
        macd_line, signal_line, histogram = Indicators.macd(
            closes, self.macd_fast, self.macd_slow, self.macd_signal
        )
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = Indicators.bollinger_bands(
            closes, self.bb_period, self.bb_std
        )
        
        # ATR
        atr = Indicators.atr(highs, lows, closes, self.atr_period)
        
        # OBV
        obv = Indicators.obv(closes, volumes)
        
        # EMAs
        ema_20 = Indicators.ema(closes, 20)
        ema_50 = Indicators.ema(closes, 50)
        ema_200 = Indicators.ema(closes, 200) if len(closes) >= 200 else None
        
        # Get latest values
        latest = {
            "rsi": rsi[-1] if rsi else None,
            "macd_line": macd_line[-1] if macd_line else None,
            "macd_signal": signal_line[-1] if signal_line else None,
            "macd_histogram": histogram[-1] if histogram else None,
            "bb_upper": bb_upper[-1] if bb_upper else None,
            "bb_middle": bb_middle[-1] if bb_middle else None,
            "bb_lower": bb_lower[-1] if bb_lower else None,
            "atr": atr[-1] if atr else None,
            "obv": obv[-1] if obv else None,
            "obv_prev": obv[-2] if len(obv) >= 2 else None,
            "ema_20": ema_20[-1] if ema_20 else None,
            "ema_50": ema_50[-1] if ema_50 else None,
            "ema_200": ema_200[-1] if ema_200 else None,
            "close": closes[-1],
            "volume": volumes[-1]
        }
        
        # Calculate BB position (0-1, where 0 is lower band, 1 is upper band)
        if latest["bb_upper"] and latest["bb_lower"] and latest["bb_upper"] != latest["bb_lower"]:
            latest["bb_position"] = (latest["close"] - latest["bb_lower"]) / (latest["bb_upper"] - latest["bb_lower"])
        else:
            latest["bb_position"] = 0.5
        
        # Calculate MACD crossover
        if len(histogram) >= 2 and histogram[-1] is not None and histogram[-2] is not None:
            latest["macd_crossing_up"] = histogram[-2] < 0 and histogram[-1] > 0
            latest["macd_crossing_down"] = histogram[-2] > 0 and histogram[-1] < 0
        else:
            latest["macd_crossing_up"] = False
            latest["macd_crossing_down"] = False

        # Donchian-style 20-candle breakout helpers.
        # Use previous 20 candles, excluding the current candle, so the
        # breakout trigger is not self-referential.
        if len(highs) >= 21 and len(lows) >= 21:
            recent_high_20 = max(highs[-21:-1])
            recent_low_20 = min(lows[-21:-1])
            latest["recent_high_20"] = recent_high_20
            latest["recent_low_20"] = recent_low_20
            latest["breakout_up_20"] = closes[-1] > recent_high_20
            latest["breakout_down_20"] = closes[-1] < recent_low_20
        else:
            latest["recent_high_20"] = None
            latest["recent_low_20"] = None
            latest["breakout_up_20"] = False
            latest["breakout_down_20"] = False

        return latest
    
    def _calculate_scores(
        self,
        indicators: Dict,
        regime_data: Dict,
        closes: List[float],
        volumes: List[float]
    ) -> Dict:
        """Calculate sub-scores for each component"""
        
        scores = {}
        
        # Trend score (EMA alignment)
        scores["trend"] = self._score_trend(indicators)
        
        # Momentum score (RSI + MACD)
        scores["momentum"] = self._score_momentum(indicators)
        
        # Volatility score (BB position)
        scores["volatility"] = self._score_volatility(indicators, regime_data)
        
        # Volume score (OBV trend)
        scores["volume"] = self._score_volume(indicators, volumes)
        
        # Regime score (regime clarity)
        scores["regime"] = self._score_regime(regime_data)
        
        return scores
    
    def _score_trend(self, indicators: Dict) -> float:
        """Score trend strength and direction (0-1)"""
        score = 0.5  # Neutral baseline
        
        close = indicators["close"]
        ema_20 = indicators["ema_20"]
        ema_50 = indicators["ema_50"]
        ema_200 = indicators["ema_200"]
        
        if not all([ema_20, ema_50]):
            return score
        
        # EMA 20 vs EMA 50
        if ema_20 > ema_50 * 1.02:
            score += 0.2
        elif ema_20 < ema_50 * 0.98:
            score -= 0.2
        
        # Price vs EMAs
        if close > ema_20 > ema_50:
            score += 0.2
        elif close < ema_20 < ema_50:
            score -= 0.2
        
        # EMA 200 if available
        if ema_200:
            if close > ema_200:
                score += 0.1
            elif close < ema_200:
                score -= 0.1
        
        return self._clamp_score(score)
    
    def _score_momentum(self, indicators: Dict) -> float:
        """Score momentum (RSI + MACD) (0-1)"""
        score = 0.5
        
        rsi = indicators["rsi"]
        macd_hist = indicators["macd_histogram"]
        
        # RSI scoring
        if rsi is not None:
            if rsi >= self.rsi_strong_overbought:
                score -= 0.3  # Very overbought
            elif rsi >= self.rsi_overbought:
                score -= 0.15
            elif rsi <= self.rsi_strong_oversold:
                score += 0.3  # Very oversold
            elif rsi <= self.rsi_oversold:
                score += 0.15
            elif 45 <= rsi <= 55:
                pass  # Neutral
            elif rsi > 55:
                score += 0.1
            elif rsi < 45:
                score -= 0.1
        
        # MACD scoring
        if macd_hist is not None:
            if indicators["macd_crossing_up"]:
                score += 0.2
            elif indicators["macd_crossing_down"]:
                score -= 0.2
            elif macd_hist > 0:
                score += 0.1
            elif macd_hist < 0:
                score -= 0.1
        
        return self._clamp_score(score)
    
    def _score_volatility(self, indicators: Dict, regime_data: Dict) -> float:
        """Score volatility position (0-1)"""
        bb_position = indicators["bb_position"]
        regime = regime_data["regime"]
        
        # In trending regime, being near middle is good
        if regime in [MarketRegime.TREND_UP, MarketRegime.TREND_DOWN]:
            # Prefer pullbacks to middle
            if 0.4 <= bb_position <= 0.6:
                return 0.7
            else:
                return 0.5
        
        # In ranging regime, extremes are opportunities
        if regime == MarketRegime.RANGING:
            if bb_position <= 0.2:
                return 0.8  # Near lower band, potential bounce
            elif bb_position >= 0.8:
                return 0.2  # Near upper band, potential reversal
            else:
                return 0.5
        
        # Volatile regime
        if regime == MarketRegime.VOLATILE:
            return 0.4  # Lower confidence
        
        return 0.5
    
    def _score_volume(self, indicators: Dict, volumes: List[float]) -> float:
        """Score volume confirmation (0-1)"""
        score = 0.5
        
        obv = indicators["obv"]
        obv_prev = indicators["obv_prev"]
        
        if obv is not None and obv_prev is not None:
            # OBV trending up
            if obv > obv_prev:
                score += 0.2
            elif obv < obv_prev:
                score -= 0.2
        
        # Volume vs average
        if len(volumes) >= 20:
            avg_volume = sum(volumes[-20:]) / 20
            current_volume = volumes[-1]
            
            if current_volume > avg_volume * 1.5:
                score += 0.1  # High volume
            elif current_volume < avg_volume * 0.5:
                score -= 0.1  # Low volume
        
        return self._clamp_score(score)
    
    def _score_regime(self, regime_data: Dict) -> float:
        """Score regime clarity (0-1)"""
        # Higher confidence = better score
        return regime_data["confidence"]
    
    def _calculate_overall_score(self, scores: Dict) -> float:
        """Calculate weighted overall score"""
        total = 0.0
        
        for component, weight in self.weights.items():
            if component in scores:
                total += scores[component] * weight
        
        return self._clamp_score(total)
    
    def _calculate_confidence(
        self,
        scores: Dict,
        regime_data: Dict,
        num_candles: int
    ) -> float:
        """Calculate overall confidence in the analysis"""
        confidence = 0.5
        
        # More data = higher confidence
        if num_candles >= 200:
            confidence += 0.15
        elif num_candles >= 100:
            confidence += 0.10
        elif num_candles >= 50:
            confidence += 0.05
        
        # Clear regime = higher confidence
        confidence += (regime_data["confidence"] - 0.5) * 0.3
        
        # High ADX = clearer trend
        if regime_data["adx"] >= 50:
            confidence += 0.1
        elif regime_data["adx"] >= 25:
            confidence += 0.05
        
        # Score alignment (all components agree)
        score_values = list(scores.values())
        if score_values:
            avg_score = sum(score_values) / len(score_values)
            variance = sum((s - avg_score) ** 2 for s in score_values) / len(score_values)
            
            if variance < 0.05:
                confidence += 0.1  # All components agree
            elif variance > 0.15:
                confidence -= 0.1  # Components disagree
        
        return self._clamp_score(confidence)
    
    def _generate_reasoning(
        self,
        scores: Dict,
        regime_data: Dict,
        indicators: Dict
    ) -> str:
        """Generate human-readable reasoning"""
        parts = []
        
        # Regime
        regime = regime_data["regime"]
        if regime == MarketRegime.TREND_UP:
            parts.append(f"Strong uptrend (ADX: {regime_data['adx']:.1f})")
        elif regime == MarketRegime.TREND_DOWN:
            parts.append(f"Strong downtrend (ADX: {regime_data['adx']:.1f})")
        elif regime == MarketRegime.RANGING:
            parts.append("Ranging market")
        else:
            parts.append("Volatile market")
        
        # RSI
        rsi = indicators["rsi"]
        if rsi is not None:
            if rsi >= self.rsi_overbought:
                parts.append(f"RSI overbought ({rsi:.1f})")
            elif rsi <= self.rsi_oversold:
                parts.append(f"RSI oversold ({rsi:.1f})")
            else:
                parts.append(f"RSI neutral ({rsi:.1f})")
        
        # MACD
        if indicators["macd_crossing_up"]:
            parts.append("MACD bullish crossover")
        elif indicators["macd_crossing_down"]:
            parts.append("MACD bearish crossover")
        
        # BB position
        bb_pos = indicators["bb_position"]
        if bb_pos <= 0.2:
            parts.append("Price near lower Bollinger Band")
        elif bb_pos >= 0.8:
            parts.append("Price near upper Bollinger Band")
        
        return "; ".join(parts)
    
    def _build_technical_state(self, indicators: Dict, scores: Dict) -> TechnicalState:
        """Build a normalized TechnicalState from raw indicators and scores."""
        return TechnicalState(
            close=indicators.get("close"),
            rsi=indicators.get("rsi"),
            macd_histogram=indicators.get("macd_histogram"),
            macd_crossing_up=bool(indicators.get("macd_crossing_up", False)),
            macd_crossing_down=bool(indicators.get("macd_crossing_down", False)),
            bb_position=indicators.get("bb_position"),
            atr=indicators.get("atr"),
            ema_20=indicators.get("ema_20"),
            ema_50=indicators.get("ema_50"),
            ema_200=indicators.get("ema_200"),
            volume=indicators.get("volume"),
            obv=indicators.get("obv"),
            obv_prev=indicators.get("obv_prev"),
            recent_high_20=indicators.get("recent_high_20"),
            recent_low_20=indicators.get("recent_low_20"),
            breakout_up_20=bool(indicators.get("breakout_up_20", False)),
            breakout_down_20=bool(indicators.get("breakout_down_20", False)),
            scores=dict(scores or {}),
        )

    def _build_market_state(self, regime_data: Dict) -> MarketState:
        """Build a normalized MarketState from raw regime data."""
        regime = regime_data.get("regime")
        return MarketState(
            regime=regime.value if hasattr(regime, "value") else str(regime),
            confidence=float(regime_data.get("confidence", 0.0)),
            trend_direction=regime_data.get("trend_direction", "neutral"),
            trend_strength=float(regime_data.get("trend_strength", 0.0)),
            adx=float(regime_data.get("adx", 0.0)),
            bb_width=regime_data.get("bb_width"),
            reason=regime_data.get("reason", ""),
        )

    def _create_neutral_result(self, symbol: str, reason: str) -> AgentResult:
        """Create a neutral result when analysis cannot be performed"""
        return AgentResult(
            agent_name=self.name,
            symbol=symbol,
            timestamp=datetime.now(),
            direction=SignalDirection.NEUTRAL,
            sub_score=0.5,
            confidence=0.3,
            analysis={"error": reason},
            reasoning=reason,
            metadata={"error": True}
        )

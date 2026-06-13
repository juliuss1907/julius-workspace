"""
Sentiment Analyst Agent
Analyzes market sentiment from Fear & Greed Index and Polymarket
"""
from datetime import datetime
from typing import Dict, Optional
from agents.base_agent import BaseAgent, AgentResult, SignalDirection
from agents.sentiment_scorer import SentimentScorer
from dataflows import FearGreedClient, PolymarketClient
from utils import get_logger, config

logger = get_logger(__name__)


class SentimentAnalyst(BaseAgent):
    """
    Sentiment Analyst Agent
    
    Combines macro sentiment (Fear & Greed) with prediction market odds
    to generate contrarian trading signals.
    """

    def __init__(self, config_override: Optional[Dict] = None):
        super().__init__("SentimentAnalyst", config_override)
        default_config = config.load_default_params()
        self.config = {**default_config.get("sentiment_analysis", {}), **(config_override or {})}

        self.fg_client = FearGreedClient()
        self.pm_client = PolymarketClient()
        self.scorer = SentimentScorer()

    async def initialize(self):
        if self._initialized:
            return
        logger.info("SentimentAnalyst initialized")
        self._initialized = True

    async def analyze(self, symbol: str, data: Dict) -> AgentResult:
        """
        Analyze market sentiment
        
        Args:
            symbol: Trading pair symbol (e.g., BTCUSDT)
            data: Dict with optional:
                - coin: Coin name (e.g., BTC)
        
        Returns:
            AgentResult with sentiment analysis
        """
        if not self._initialized:
            await self.initialize()

        coin = data.get("coin", symbol.replace("USDT", ""))

        try:
            # Fetch data from both sources in parallel
            import asyncio
            fg_task = self.fg_client.fetch_current()
            pm_task = self.pm_client.fetch_crypto_markets(limit=5)
            fg_data, polymarkets = await asyncio.gather(fg_task, pm_task, return_exceptions=True)

            if isinstance(fg_data, Exception):
                logger.warning(f"FearGreed fetch failed: {fg_data}")
                fg_data = None
            if isinstance(polymarkets, Exception):
                logger.warning(f"Polymarket fetch failed: {polymarkets}")
                polymarkets = []

        except Exception as e:
            logger.error(f"Failed to fetch sentiment data: {e}")
            fg_data, polymarkets = None, []

        # Score and combine
        result = self.scorer.combine(fg_data, polymarkets)

        # Determine signal direction
        direction = self._determine_direction(result['score'])
        sub_score = result['score']
        confidence = result['confidence']

        # Build reasoning
        parts = []
        fg = result['fear_greed']
        pm = result['polymarket']

        if fg['confidence'] > 0:
            parts.append(f"Fear&Greed: {fg['raw_value']} ({fg['classification']})")
            if fg['contrarian']:
                parts.append("→ contrarian signal active")

        if pm['confidence'] > 0:
            parts.append(f"Polymarket: {pm['markets']} markets, avg odds {pm.get('avg_odds', 0.5):.2f}")

        reasoning = "; ".join(parts)

        # Build analysis detail
        analysis = {
            'fear_greed': {
                'value': fg.get('raw_value'),
                'classification': fg.get('classification'),
                'score': fg.get('score'),
                'contrarian': fg.get('contrarian')
            },
            'polymarket': {
                'markets_count': pm.get('markets'),
                'avg_odds': pm.get('avg_odds'),
                'score': pm.get('score'),
                'sentiment': pm.get('sentiment')
            },
            'overall': {
                'score': result['score'],
                'direction': result['direction'],
                'confidence': result['confidence']
            }
        }

        return AgentResult(
            agent_name=self.name,
            symbol=symbol,
            timestamp=datetime.now(),
            direction=direction,
            sub_score=sub_score,
            confidence=confidence,
            analysis=analysis,
            reasoning=reasoning,
            metadata={'sources': 'fear_greed+polymarket'}
        )

    async def close(self):
        await self.fg_client.close()
        await self.pm_client.close()

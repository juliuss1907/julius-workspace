"""
Sentiment Scorer
Combines Fear & Greed + Polymarket data into sentiment scores
"""
from typing import Dict, Optional
from utils import get_logger

logger = get_logger(__name__)


class SentimentScorer:
    """Score sentiment from Fear & Greed Index and Polymarket"""

    def score_fear_greed(self, fg_data: Optional[Dict]) -> Dict:
        """
        Convert Fear & Greed value to sentiment score (0-1)
        Uses contrarian logic: extreme fear → bullish, extreme greed → bearish
        """
        if not fg_data:
            return {'score': 0.5, 'sentiment': 'neutral', 'confidence': 0.0}

        value = fg_data.get('value', 50)

        if value <= 25:
            score, sentiment, contrarian = 0.80, 'bullish', True
        elif value <= 45:
            score, sentiment, contrarian = 0.65, 'bullish', False
        elif value <= 55:
            score, sentiment, contrarian = 0.50, 'neutral', False
        elif value <= 75:
            score, sentiment, contrarian = 0.35, 'bearish', False
        else:
            score, sentiment, contrarian = 0.20, 'bearish', True

        return {
            'score': score,
            'sentiment': sentiment,
            'confidence': 0.85,  # Fear & Greed is reliable
            'contrarian': contrarian,
            'raw_value': value,
            'classification': fg_data.get('classification', 'unknown')
        }

    def score_polymarket(self, markets: list) -> Dict:
        """
        Score from Polymarket prediction markets
        Higher odds = more bullish expectation
        """
        if not markets:
            return {'score': 0.5, 'sentiment': 'neutral', 'confidence': 0.0, 'markets': 0}

        scores = []
        total_weight = 0.0
        total_odds = []

        for market in markets:
            prices = self._parse_prices(market.get('outcome_prices', []))
            if not prices:
                continue

            dominant_odds = max(prices)
            volume = market.get('volume', 0)
            total_odds.append(dominant_odds)

            # Convert odds to score
            if dominant_odds >= 0.7:
                ms = 0.65 + (dominant_odds - 0.7) * 0.5
            elif dominant_odds <= 0.3:
                ms = 0.35 - (0.3 - dominant_odds) * 0.5
            else:
                ms = 0.5

            ms = max(0.0, min(1.0, ms))

            # Weight by volume
            weight = min(1.0, volume / 50000) if volume else 0.2
            scores.append(ms * weight)
            total_weight += weight

        if total_weight > 0:
            avg_score = sum(scores) / total_weight
        else:
            avg_score = 0.5

        if total_odds:
            sentiment = 'bullish' if avg_score >= 0.6 else ('bearish' if avg_score <= 0.4 else 'neutral')
            confidence = min(0.8, total_weight / len(markets))
        else:
            sentiment = 'neutral'
            confidence = 0.0

        return {
            'score': round(avg_score, 3),
            'sentiment': sentiment,
            'confidence': confidence,
            'markets': len(markets),
            'avg_odds': round(sum(total_odds) / len(total_odds), 3) if total_odds else 0.5
        }

    def _parse_prices(self, raw_prices) -> list:
        """Parse Polymarket outcomePrices which may be JSON string or list"""
        import json
        # Polymarket returns outcomePrices as JSON string like '["0.65","0.35"]'
        if isinstance(raw_prices, str):
            try:
                raw_prices = json.loads(raw_prices)
            except json.JSONDecodeError:
                return []
        prices = []
        for p in raw_prices:
            try:
                val = float(p)
                if val == val:
                    prices.append(val)
            except (ValueError, TypeError):
                pass
        return prices

    def combine(
        self,
        fg_data: Optional[Dict],
        polymarkets: list,
        fg_weight: float = 0.5,
        pm_weight: float = 0.5
    ) -> Dict:
        """Combine Fear & Greed + Polymarket into overall sentiment score"""
        fg = self.score_fear_greed(fg_data)
        pm = self.score_polymarket(polymarkets)

        # Weighted average (skip sources with 0 confidence)
        total_weight = 0.0
        weighted_score = 0.0

        if fg['confidence'] > 0:
            weighted_score += fg['score'] * fg_weight
            total_weight += fg_weight

        if pm['confidence'] > 0:
            weighted_score += pm['score'] * pm_weight
            total_weight += pm_weight

        if total_weight > 0:
            final_score = weighted_score / total_weight
        else:
            final_score = 0.5

        # Determine direction
        if final_score >= 0.6:
            direction = 'bullish'
        elif final_score <= 0.4:
            direction = 'bearish'
        else:
            direction = 'neutral'

        # Confidence: higher when both sources agree
        both_active = (fg['confidence'] > 0) and (pm['confidence'] > 0)
        if both_active:
            agreement = 1.0 - abs(fg['score'] - pm['score'])
            confidence = 0.6 + agreement * 0.3
        elif fg['confidence'] > 0:
            confidence = min(0.7, fg['confidence'] * 0.7)
        elif pm['confidence'] > 0:
            confidence = min(0.5, pm['confidence'] * 0.5)
        else:
            confidence = 0.3

        return {
            'score': round(final_score, 3),
            'direction': direction,
            'confidence': round(confidence, 3),
            'fear_greed': fg,
            'polymarket': pm,
            'contrarian': fg.get('contrarian', False)
        }

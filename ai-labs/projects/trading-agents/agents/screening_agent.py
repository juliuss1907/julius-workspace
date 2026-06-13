"""
Screening Agent — Phase 8A.

Scans a candidate universe, scores each symbol on liquidity / volatility /
technical / news / risk, and produces a ranked candidate list.

IMPORTANT:
  - This agent does NOT trade.
  - It does NOT mutate the live watchlist.
  - It produces an advisory report only.
  - Dynamic watchlist promotion is Phase 8B.

Inputs (per symbol):
  - ohlcv: list of dicts with keys {open, high, low, close, volume, quote_volume}
  - ticker: dict with optional 24h quote_volume, price change pct, etc.
  - news_score: 0-100 (50 = neutral). Optional; defaults to 50.
  - open_positions: list of dicts (for risk penalty). Optional.

Output: CandidateMetrics per symbol.
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional


DEFAULT_WEIGHTS = {
    "liquidity": 0.25,
    "volatility": 0.20,
    "technical": 0.25,
    "news": 0.15,
    "risk": 0.15,
}

DEFAULT_LIQUIDITY_THRESHOLDS = {
    "excellent": 100_000_000,
    "good": 50_000_000,
    "fair": 10_000_000,
    "low": 1_000_000,
}

DEFAULT_VOLATILITY = {
    "ideal_min": 0.010,
    "ideal_max": 0.050,
    "block_threshold": 0.10,
}

DEFAULT_RATINGS = {
    "strong_candidate": 75,
    "candidate": 60,
    "watch_only": 45,
}


@dataclass
class CandidateMetrics:
    symbol: str
    score: float = 0.0
    rating: str = "avoid"
    liquidity_score: float = 0.0
    volatility_score: float = 0.0
    technical_score: float = 0.0
    news_score: float = 50.0
    risk_score: float = 100.0
    rank: int = 0
    reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommended_action: str = "skip"
    raw_metrics: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


def _ema(values: List[float], period: int) -> Optional[float]:
    if len(values) < period:
        return None
    k = 2.0 / (period + 1)
    ema = sum(values[:period]) / period
    for v in values[period:]:
        ema = v * k + ema * (1 - k)
    return ema


def _rsi(closes: List[float], period: int = 14) -> Optional[float]:
    if len(closes) < period + 1:
        return None
    gains = []
    losses = []
    for i in range(1, len(closes)):
        delta = closes[i] - closes[i - 1]
        if delta >= 0:
            gains.append(delta)
            losses.append(0.0)
        else:
            gains.append(0.0)
            losses.append(-delta)
    if len(gains) < period:
        return None
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1 + rs))


def _atr_pct(candles: List[Dict], period: int = 14) -> Optional[float]:
    if len(candles) < period + 1:
        return None
    trs = []
    for i in range(1, len(candles)):
        h = candles[i]["high"]
        l = candles[i]["low"]
        c_prev = candles[i - 1]["close"]
        tr = max(h - l, abs(h - c_prev), abs(l - c_prev))
        trs.append(tr)
    if len(trs) < period:
        return None
    atr = sum(trs[:period]) / period
    last_close = candles[-1]["close"]
    if last_close <= 0:
        return None
    return atr / last_close


def score_liquidity(quote_volume_24h: Optional[float], thresholds: Dict) -> float:
    """Convert 24h quote volume to a 0-100 score."""
    if quote_volume_24h is None or quote_volume_24h <= 0:
        return 0.0
    if quote_volume_24h >= thresholds.get("excellent", 100_000_000):
        return 100.0
    if quote_volume_24h >= thresholds.get("good", 50_000_000):
        return 80.0
    if quote_volume_24h >= thresholds.get("fair", 10_000_000):
        return 60.0
    if quote_volume_24h >= thresholds.get("low", 1_000_000):
        return 40.0
    return 20.0


def score_volatility(atr_pct_value: Optional[float], vconf: Dict) -> float:
    """Convert ATR/price to a 0-100 score. Prefer moderate volatility."""
    if atr_pct_value is None or atr_pct_value < 0:
        return 0.0
    ideal_min = vconf.get("ideal_min", 0.010)
    ideal_max = vconf.get("ideal_max", 0.050)
    block = vconf.get("block_threshold", 0.10)

    if atr_pct_value >= block:
        return 5.0
    if atr_pct_value >= ideal_max:
        # Ramp down as we approach block
        span = block - ideal_max
        if span <= 0:
            return 50.0
        return max(20.0, 60.0 * (1 - (atr_pct_value - ideal_max) / span))
    if atr_pct_value >= ideal_min:
        return 100.0
    # Below ideal — too quiet
    if atr_pct_value <= 0:
        return 0.0
    return max(10.0, 100.0 * (atr_pct_value / ideal_min))


def score_technical(ohlcv: List[Dict]) -> float:
    """Compute a 0-100 technical score from EMA trend, RSI, and momentum."""
    if len(ohlcv) < 50:
        return 0.0
    closes = [c["close"] for c in ohlcv]

    ema_fast = _ema(closes, 20)
    ema_slow = _ema(closes, 50)
    rsi = _rsi(closes, 14)

    score = 50.0

    if ema_fast is not None and ema_slow is not None:
        if ema_fast > ema_slow * 1.005:
            score += 15
        elif ema_fast > ema_slow:
            score += 8
        elif ema_fast < ema_slow * 0.995:
            score -= 15
        else:
            score -= 8

    if rsi is not None:
        if 45 <= rsi <= 65:
            score += 12
        elif 35 <= rsi <= 75:
            score += 5
        elif rsi > 80 or rsi < 20:
            score -= 12
        elif rsi > 70 or rsi < 30:
            score -= 5

    if len(closes) >= 20:
        last_5_pct = (closes[-1] - closes[-5]) / closes[-5] if closes[-5] else 0
        if last_5_pct > 0.05:
            score += 8
        elif last_5_pct < -0.05:
            score -= 8

    return max(0.0, min(100.0, score))


def score_risk(warnings: List[str]) -> float:
    """Convert warnings into a 0-100 risk score (higher = safer)."""
    return max(0.0, 100.0 - len(warnings) * 25.0)


def rating_from_score(score: float, thresholds: Dict) -> str:
    if score >= thresholds.get("strong_candidate", 75):
        return "strong_candidate"
    if score >= thresholds.get("candidate", 60):
        return "candidate"
    if score >= thresholds.get("watch_only", 45):
        return "watch_only"
    return "avoid"


def recommended_action_for(rating: str) -> str:
    if rating == "strong_candidate":
        return "consider_watchlist"
    if rating == "candidate":
        return "consider_watchlist"
    if rating == "watch_only":
        return "monitor_only"
    return "skip"


def _compute_quote_volume_24h(ohlcv: List[Dict]) -> Optional[float]:
    """Best-effort estimate of 24h quote volume from recent candles."""
    if not ohlcv:
        return None
    last = ohlcv[-1]
    if "quote_volume" in last and last["quote_volume"]:
        return float(last["quote_volume"])
    if "volume" in last and last["volume"]:
        return float(last["volume"]) * float(last["close"])
    return None


class ScreeningAgent:
    """Scores and ranks a candidate universe for screening."""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.weights = {
            **DEFAULT_WEIGHTS,
            **self.config.get("weights", {}),
        }
        self.liquidity_thresholds = {
            **DEFAULT_LIQUIDITY_THRESHOLDS,
            **self.config.get("liquidity_thresholds", {}),
        }
        self.volatility_cfg = {
            **DEFAULT_VOLATILITY,
            **self.config.get("volatility", {}),
        }
        self.ratings_cfg = {
            **DEFAULT_RATINGS,
            **self.config.get("rating_thresholds", {}),
        }
        self.min_candles = self.config.get("min_candles_required", 50)

    def score_candidate(
        self,
        symbol: str,
        ohlcv: Optional[List[Dict]] = None,
        ticker: Optional[Dict] = None,
        news_score: float = 50.0,
        open_positions: Optional[List[Dict]] = None,
    ) -> CandidateMetrics:
        warnings: List[str] = []
        reasons: List[str] = []
        ohlcv = ohlcv or []
        open_positions = open_positions or []

        c = CandidateMetrics(symbol=symbol, news_score=max(0.0, min(100.0, news_score)))

        if len(ohlcv) < self.min_candles:
            warnings.append(
                f"insufficient_data: only {len(ohlcv)} candles (< {self.min_candles})"
            )
            c.warnings = warnings
            c.risk_score = score_risk(warnings)
            c.recommended_action = "skip"
            c.raw_metrics = {
                "candles": len(ohlcv),
                "min_required": self.min_candles,
            }
            return c

        last_close = ohlcv[-1]["close"]

        quote_vol_24h = None
        if ticker and "quote_volume" in ticker:
            quote_vol_24h = ticker["quote_volume"]
        if quote_vol_24h is None:
            quote_vol_24h = _compute_quote_volume_24h(ohlcv)
        c.liquidity_score = score_liquidity(quote_vol_24h, self.liquidity_thresholds)

        atr_pct = _atr_pct(ohlcv, 14)
        if atr_pct is not None and atr_pct >= self.volatility_cfg.get("block_threshold", 0.10):
            warnings.append(f"extreme_volatility: ATR/price {atr_pct*100:.1f}%")
        c.volatility_score = score_volatility(atr_pct, self.volatility_cfg)
        c.raw_metrics["atr_pct"] = round(atr_pct, 6) if atr_pct is not None else None
        c.raw_metrics["last_close"] = last_close
        c.raw_metrics["quote_volume_24h"] = quote_vol_24h

        if quote_vol_24h is not None and quote_vol_24h < self.liquidity_thresholds.get("low", 1_000_000):
            warnings.append("low_liquidity: 24h quote volume below threshold")

        c.technical_score = score_technical(ohlcv)
        if c.technical_score >= 70:
            reasons.append("strong technical setup")
        elif c.technical_score <= 30:
            warnings.append("weak technical setup")

        for pos in open_positions:
            if pos.get("symbol") == symbol:
                warnings.append("open_position_already_exists")
                break

        c.risk_score = score_risk(warnings)
        c.warnings = warnings
        c.reasons = reasons

        total = (
            c.liquidity_score * self.weights["liquidity"]
            + c.volatility_score * self.weights["volatility"]
            + c.technical_score * self.weights["technical"]
            + c.news_score * self.weights["news"]
            + c.risk_score * self.weights["risk"]
        )
        c.score = round(max(0.0, min(100.0, total)), 2)
        c.rating = rating_from_score(c.score, self.ratings_cfg)
        c.recommended_action = recommended_action_for(c.rating)

        return c

    def rank_candidates(
        self, candidates: List[CandidateMetrics]
    ) -> List[CandidateMetrics]:
        ordered = sorted(candidates, key=lambda x: x.score, reverse=True)
        for i, c in enumerate(ordered, 1):
            c.rank = i
        return ordered

    def screen(
        self,
        symbols: List[str],
        ohlcv_map: Dict[str, List[Dict]],
        ticker_map: Optional[Dict[str, Dict]] = None,
        news_scores: Optional[Dict[str, float]] = None,
        open_positions: Optional[List[Dict]] = None,
    ) -> List[CandidateMetrics]:
        ticker_map = ticker_map or {}
        news_scores = news_scores or {}
        candidates = []
        for sym in symbols:
            cand = self.score_candidate(
                symbol=sym,
                ohlcv=ohlcv_map.get(sym, []),
                ticker=ticker_map.get(sym),
                news_score=news_scores.get(sym, 50.0),
                open_positions=open_positions,
            )
            candidates.append(cand)
        return self.rank_candidates(candidates)

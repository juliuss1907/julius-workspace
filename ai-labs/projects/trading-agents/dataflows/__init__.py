"""
Data Flows Package
"""
from .base import DataSource
from .binance_client import BinanceClient
from .binance_futures_client import BinanceFuturesClient
from .binance_derivatives_client import BinanceDerivativesClient
from .hyperliquid_client import HyperliquidClient
from .lighter_client import LighterClient
from .coingecko_client import CoinGeckoClient
from .telegram_scraper import TelegramScraper
from .rss_fetcher import RSSFetcher
from .fear_greed_client import FearGreedClient
from .reddit_client import RedditClient
from .polymarket_client import PolymarketClient
from .retry import retry_with_backoff, CircuitBreaker
from .parallel_fetcher import ParallelFetcher
from .cache import cache, Cache
from .data_manager import DataManager, data_manager

__all__ = [
    "DataSource",
    "BinanceClient",
    "BinanceFuturesClient",
    "BinanceDerivativesClient",
    "HyperliquidClient",
    "LighterClient",
    "CoinGeckoClient",
    "TelegramScraper",
    "RSSFetcher",
    "FearGreedClient",
    "RedditClient",
    "PolymarketClient",
    "retry_with_backoff",
    "CircuitBreaker",
    "ParallelFetcher",
    "cache",
    "Cache",
    "DataManager",
    "data_manager"
]

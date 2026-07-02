"""
Data Flows Package

Only the stdlib-only DataSource base class is eagerly loaded. Concrete clients
and scrapers are lazy-loaded so optional dependencies (for example telethon or
feedparser) are not required by unrelated read-only tooling such as replay CLI
help/readiness checks.
"""
from .base import DataSource


_LAZY = {
    "BinanceClient": ".binance_client",
    "BinanceFuturesClient": ".binance_futures_client",
    "BinanceDerivativesClient": ".binance_derivatives_client",
    "HyperliquidClient": ".hyperliquid_client",
    "LighterClient": ".lighter_client",
    "CoinGeckoClient": ".coingecko_client",
    "TelegramScraper": ".telegram_scraper",
    "RSSFetcher": ".rss_fetcher",
    "FearGreedClient": ".fear_greed_client",
    "RedditClient": ".reddit_client",
    "PolymarketClient": ".polymarket_client",
    "retry_with_backoff": ".retry",
    "CircuitBreaker": ".retry",
    "ParallelFetcher": ".parallel_fetcher",
    "cache": ".cache",
    "Cache": ".cache",
    "DataManager": ".data_manager",
    "data_manager": ".data_manager",
}


def __getattr__(name):
    dotpath = _LAZY.get(name)
    if dotpath is not None:
        module = __import__(f"dataflows{dotpath}", fromlist=[name])
        value = getattr(module, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


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
    "data_manager",
]

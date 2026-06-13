"""
Data Manager - Orchestrates fetching and storage
"""
import os
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from utils import get_logger
from dataflows.binance_client import BinanceClient
from dataflows.binance_futures_client import BinanceFuturesClient
from dataflows.coingecko_client import CoinGeckoClient
from dataflows.parallel_fetcher import ParallelFetcher
from dataflows.cache import cache
from state import db


logger = get_logger(__name__)


class DataManager:
    """Manages data fetching, caching, and storage"""

    def __init__(self):
        self.binance = BinanceClient()
        self.binance_futures = BinanceFuturesClient(
            api_key=os.getenv("BINANCE_FUTURES_TESTNET_API_KEY"),
            api_secret=os.getenv("BINANCE_FUTURES_TESTNET_SECRET"),
            environment="testnet",
        )
        self.coingecko = CoinGeckoClient(api_key=os.getenv("COINGECKO_API_KEY"))
        self.fetcher = ParallelFetcher()
        self.fetcher.register_source("binance", self.binance)
        self.fetcher.register_source("coingecko", self.coingecko)
        self._initialized = False
    
    async def initialize(self):
        """Initialize database connection"""
        if not self._initialized:
            await db.connect()
            self._initialized = True
            logger.info("DataManager initialized")
    
    async def close(self):
        """Close all connections and mark the manager reusable."""
        await self.binance.close()
        await self.binance_futures.close()
        await self.coingecko.close()
        await db.close()
        self._initialized = False
        logger.info("DataManager closed")
    
    # =========================================================================
    # OHLCV Operations
    # =========================================================================
    
    async def fetch_and_store_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 500,
        force_fetch: bool = False
    ) -> List[Dict]:
        """
        Fetch OHLCV and store in database
        
        Args:
            symbol: Trading pair
            timeframe: Timeframe
            limit: Number of candles to fetch
            force_fetch: Bypass cache and fetch fresh data
        
        Returns:
            List of candles
        """
        if not self._initialized:
            await self.initialize()
        
        # Check what we already have in DB
        latest_ts = await db.get_latest_ohlcv_timestamp(symbol, timeframe)
        
        if latest_ts and not force_fetch:
            # Calculate how many new candles we need
            current_time = int(datetime.now().timestamp())
            
            # Timeframe to seconds mapping
            tf_seconds = {
                '1m': 60, '3m': 180, '5m': 300, '15m': 900, '30m': 1800,
                '1h': 3600, '2h': 7200, '4h': 14400, '6h': 21600, '12h': 43200,
                '1d': 86400, '1w': 604800
            }
            
            interval_seconds = tf_seconds.get(timeframe, 3600)
            candles_behind = (current_time - latest_ts) // interval_seconds
            
            if candles_behind < 2:
                # We're up to date, return from DB
                logger.debug(f"{symbol} {timeframe} is up to date, using DB")
                return await db.get_ohlcv(symbol, timeframe, limit)
            
            # Fetch only missing candles
            fetch_limit = min(int(candles_behind) + 10, 1000)
            logger.info(f"{symbol} {timeframe} behind by {candles_behind} candles, fetching {fetch_limit}")
        else:
            # No data in DB, fetch full history
            fetch_limit = limit
            logger.info(f"No local data for {symbol} {timeframe}, fetching {fetch_limit} candles")
        
        # Fetch from exchange (spot first, then futures fallback)
        candles = await self.binance.fetch_ohlcv(symbol, timeframe, fetch_limit)
        if not candles:
            logger.info(f"{symbol} {timeframe} not on spot, trying Binance Futures")
            try:
                candles = await self.binance_futures.fetch_ohlcv(
                    symbol, timeframe, fetch_limit
                )
            except Exception as e:
                logger.warning(f"Futures OHLCV fetch failed for {symbol}: {e}")

        if candles:
            # Store in database
            await db.insert_ohlcv(symbol, timeframe, candles)

        # Return from DB (ensures consistency)
        return await db.get_ohlcv(symbol, timeframe, limit)
    
    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 500,
        use_cache: bool = True
    ) -> List[Dict]:
        """
        Get OHLCV data (from cache/DB or fetch if needed)
        
        Args:
            symbol: Trading pair
            timeframe: Timeframe
            limit: Number of candles
            use_cache: Whether to use cache layer
        
        Returns:
            List of candles
        """
        if not self._initialized:
            await self.initialize()
        
        cache_key = f"ohlcv:{symbol}:{timeframe}:{limit}"
        
        if use_cache:
            # Check cache first (TTL: 1 minute for 1m/5m, 5 minutes for 1h+)
            cache_ttl = 60 if timeframe in ['1m', '5m'] else 300
            
            cached = await cache.get(cache_key, max_age_seconds=cache_ttl)
            if cached:
                logger.debug(f"OHLCV cache hit: {symbol} {timeframe}")
                return cached
        
        # Fetch and store
        candles = await self.fetch_and_store_ohlcv(symbol, timeframe, limit)
        
        # Update cache
        if use_cache and candles:
            cache_ttl = 60 if timeframe in ['1m', '5m'] else 300
            await cache.set(cache_key, candles, ttl_seconds=cache_ttl)
        
        return candles
    
    # =========================================================================
    # Ticker Operations
    # =========================================================================
    
    async def fetch_and_store_ticker(self, symbol: str) -> Optional[Dict]:
        """Fetch current ticker and store in DB"""
        if not self._initialized:
            await self.initialize()

        ticker = await self.binance.fetch_ticker(symbol)
        if not ticker:
            logger.info(f"{symbol} ticker not on spot, trying Binance Futures")
            try:
                ticker = await self.binance_futures.fetch_ticker(symbol)
            except Exception as e:
                logger.warning(f"Futures ticker fetch failed for {symbol}: {e}")

        if ticker:
            await db.insert_ticker(ticker)

        return ticker
    
    async def get_ticker(self, symbol: str, use_cache: bool = True) -> Optional[Dict]:
        """
        Get current ticker (cached with 5s TTL)
        
        Args:
            symbol: Trading pair
            use_cache: Whether to use cache
        
        Returns:
            Ticker dict
        """
        if not self._initialized:
            await self.initialize()
        
        cache_key = f"ticker:{symbol}"
        
        if use_cache:
            cached = await cache.get(cache_key, max_age_seconds=5)
            if cached:
                return cached
        
        # Fetch fresh
        ticker = await self.fetch_and_store_ticker(symbol)
        
        if use_cache and ticker:
            await cache.set(cache_key, ticker, ttl_seconds=5)
        
        return ticker
    
    # =========================================================================
    # Multi-Coin Batch Operations
    # =========================================================================
    
    async def fetch_watchlist_tickers(self, coins: List[str]) -> Dict[str, Dict]:
        """
        Fetch tickers for multiple coins in parallel
        
        Args:
            coins: List of coin symbols
        
        Returns:
            Dict mapping coin to ticker data
        """
        if not self._initialized:
            await self.initialize()
        
        tasks = []
        for coin in coins:
            tasks.append(self.get_ticker(coin))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        ticker_map = {}
        for coin, result in zip(coins, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to fetch ticker for {coin}: {result}")
                ticker_map[coin] = None
            else:
                ticker_map[coin] = result
        
        return ticker_map
    
    async def fetch_watchlist_ohlcv(
        self,
        coins: List[str],
        timeframe: str = "1h",
        limit: int = 100
    ) -> Dict[str, List[Dict]]:
        """
        Fetch OHLCV for multiple coins in parallel
        
        Args:
            coins: List of coin symbols
            timeframe: Timeframe
            limit: Number of candles per coin
        
        Returns:
            Dict mapping coin to OHLCV data
        """
        if not self._initialized:
            await self.initialize()
        
        tasks = []
        for coin in coins:
            tasks.append(self.get_ohlcv(coin, timeframe, limit))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        ohlcv_map = {}
        for coin, result in zip(coins, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to fetch OHLCV for {coin}: {result}")
                ohlcv_map[coin] = []
            else:
                ohlcv_map[coin] = result
        
        return ohlcv_map
    
    # =========================================================================
    # Fundamentals Operations (CoinGecko)
    # =========================================================================
    
    async def get_fundamentals(self, symbol: str, use_cache: bool = True) -> Optional[Dict]:
        """
        Get fundamental data for a coin (market cap, supply, etc.)
        
        Args:
            symbol: Coin symbol
            use_cache: Whether to use cache (15 min TTL)
        
        Returns:
            Fundamentals dict from CoinGecko
        """
        if not self._initialized:
            await self.initialize()
        
        cache_key = f"fundamentals:{symbol}"
        
        if use_cache:
            # Cache for 15 minutes (fundamentals don't change often)
            cached = await cache.get(cache_key, max_age_seconds=900)
            if cached:
                logger.debug(f"Fundamentals cache hit: {symbol}")
                return cached
        
        # Fetch from CoinGecko
        fundamentals = await self.coingecko.fetch_coin_data(symbol)
        
        if use_cache and fundamentals:
            await cache.set(cache_key, fundamentals, ttl_seconds=900)
        
        return fundamentals
    
    async def get_simple_prices(
        self,
        symbols: List[str],
        use_cache: bool = True
    ) -> Dict[str, Dict]:
        """
        Get simple price data for multiple coins (fast, rate-limit friendly)
        
        Args:
            symbols: List of coin symbols
            use_cache: Whether to use cache (5 min TTL)
        
        Returns:
            Dict mapping symbols to price data
        """
        if not self._initialized:
            await self.initialize()
        
        cache_key = f"simple_prices:{'_'.join(sorted(symbols))}"
        
        if use_cache:
            cached = await cache.get(cache_key, max_age_seconds=300)
            if cached:
                return cached
        
        # Fetch from CoinGecko
        prices = await self.coingecko.fetch_simple_price(symbols)
        
        if use_cache and prices:
            await cache.set(cache_key, prices, ttl_seconds=300)
        
        return prices


# Global data manager instance
data_manager = DataManager()

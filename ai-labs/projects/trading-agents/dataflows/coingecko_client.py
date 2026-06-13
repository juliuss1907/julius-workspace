"""
CoinGecko API Client
For market data, fundamentals, and market cap info
"""
import aiohttp
from typing import Dict, Optional, List
from utils import get_logger
from .base import DataSource


logger = get_logger(__name__)


class CoinGeckoClient(DataSource):
    """CoinGecko API client for market fundamentals"""
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    # Symbol to CoinGecko ID mapping (most common ones)
    SYMBOL_TO_ID = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "BNB": "binancecoin",
        "XRP": "ripple",
        "ADA": "cardano",
        "AVAX": "avalanche-2",
        "DOT": "polkadot",
        "MATIC": "matic-network",
        "LINK": "chainlink",
        "UNI": "uniswap",
        "ATOM": "cosmos",
        "LTC": "litecoin",
        "BCH": "bitcoin-cash",
        "NEAR": "near",
        "APT": "aptos",
        "ARB": "arbitrum",
        "OP": "optimism",
        "SUI": "sui",
        "INJ": "injective-protocol",
        "TIA": "celestia",
        "SEI": "sei-network",
        "PEPE": "pepe",
        "WIF": "dogwifcoin",
        "BONK": "bonk"
    }
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("coingecko")
        self.api_key = api_key
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            headers = {}
            if self.api_key:
                headers["x-cg-demo-api-key"] = self.api_key
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    def _get_coin_id(self, symbol: str) -> str:
        """Convert symbol to CoinGecko ID"""
        symbol = symbol.upper().replace("USDT", "").replace("USD", "")
        return self.SYMBOL_TO_ID.get(symbol, symbol.lower())
    
    async def health_check(self) -> bool:
        """Check CoinGecko API status"""
        try:
            session = await self._get_session()
            async with session.get(f"{self.BASE_URL}/ping", timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("gecko_says") == "(V3) To the Moon!"
                return False
        except Exception as e:
            logger.error(f"CoinGecko health check failed: {e}")
            return False
    
    async def fetch_coin_data(self, symbol: str) -> Optional[Dict]:
        """
        Fetch comprehensive coin data
        
        Args:
            symbol: Coin symbol (BTC, ETH, etc.)
        
        Returns:
            Dict with market data, fundamentals, etc.
        """
        try:
            coin_id = self._get_coin_id(symbol)
            session = await self._get_session()
            
            url = f"{self.BASE_URL}/coins/{coin_id}"
            params = {
                "localization": "false",
                "tickers": "false",
                "market_data": "true",
                "community_data": "false",
                "developer_data": "false",
                "sparkline": "false"
            }
            
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    # Extract relevant data
                    market_data = data.get("market_data", {})
                    
                    result = {
                        "symbol": symbol,
                        "coingecko_id": coin_id,
                        "name": data.get("name"),
                        
                        # Price
                        "price_usd": market_data.get("current_price", {}).get("usd"),
                        
                        # Market Cap
                        "market_cap": market_data.get("market_cap", {}).get("usd"),
                        "market_cap_rank": market_data.get("market_cap_rank"),
                        
                        # Fully Diluted Valuation
                        "fdv": market_data.get("fully_diluted_valuation", {}).get("usd"),
                        
                        # Supply
                        "circulating_supply": market_data.get("circulating_supply"),
                        "total_supply": market_data.get("total_supply"),
                        "max_supply": market_data.get("max_supply"),
                        
                        # Volume
                        "volume_24h": market_data.get("total_volume", {}).get("usd"),
                        
                        # Price Changes
                        "price_change_24h_pct": market_data.get("price_change_percentage_24h"),
                        "price_change_7d_pct": market_data.get("price_change_percentage_7d"),
                        "price_change_30d_pct": market_data.get("price_change_percentage_30d"),
                        
                        # ATH/ATL
                        "ath": market_data.get("ath", {}).get("usd"),
                        "ath_change_pct": market_data.get("ath_change_percentage", {}).get("usd"),
                        "ath_date": market_data.get("ath_date", {}).get("usd"),
                        
                        "atl": market_data.get("atl", {}).get("usd"),
                        "atl_change_pct": market_data.get("atl_change_percentage", {}).get("usd"),
                        "atl_date": market_data.get("atl_date", {}).get("usd"),
                        
                        # Categories
                        "categories": data.get("categories", []),
                        
                        # Links
                        "homepage": data.get("links", {}).get("homepage", [None])[0],
                        "whitepaper": data.get("links", {}).get("whitepaper"),
                        
                        # Timestamp
                        "last_updated": data.get("last_updated")
                    }
                    
                    self.record_success()
                    logger.info(f"Fetched CoinGecko data for {symbol}")
                    return result
                
                elif resp.status == 429:
                    logger.warning("CoinGecko rate limit hit")
                    self.record_error()
                    return None
                else:
                    error_text = await resp.text()
                    logger.error(f"CoinGecko API error {resp.status}: {error_text}")
                    self.record_error()
                    return None
        
        except Exception as e:
            logger.error(f"Error fetching CoinGecko data: {e}")
            self.record_error()
            return None
    
    async def fetch_simple_price(
        self,
        symbols: List[str],
        vs_currency: str = "usd",
        include_market_cap: bool = True,
        include_24h_vol: bool = True,
        include_24h_change: bool = True
    ) -> Dict[str, Dict]:
        """
        Fetch simple prices for multiple coins (faster, rate-limit friendly)
        
        Args:
            symbols: List of coin symbols
            vs_currency: Quote currency (usd, btc, eth)
            include_market_cap: Include market cap
            include_24h_vol: Include 24h volume
            include_24h_change: Include 24h price change
        
        Returns:
            Dict mapping symbols to price data
        """
        try:
            # Convert symbols to IDs
            coin_ids = [self._get_coin_id(s) for s in symbols]
            
            session = await self._get_session()
            
            url = f"{self.BASE_URL}/simple/price"
            params = {
                "ids": ",".join(coin_ids),
                "vs_currencies": vs_currency,
                "include_market_cap": str(include_market_cap).lower(),
                "include_24hr_vol": str(include_24h_vol).lower(),
                "include_24hr_change": str(include_24h_change).lower()
            }
            
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    # Convert back to symbol keys
                    result = {}
                    for symbol, coin_id in zip(symbols, coin_ids):
                        if coin_id in data:
                            coin_data = data[coin_id]
                            result[symbol] = {
                                "price": coin_data.get(vs_currency),
                                "market_cap": coin_data.get(f"{vs_currency}_market_cap"),
                                "volume_24h": coin_data.get(f"{vs_currency}_24h_vol"),
                                "price_change_24h_pct": coin_data.get(f"{vs_currency}_24h_change")
                            }
                    
                    self.record_success()
                    logger.info(f"Fetched simple prices for {len(result)} coins")
                    return result
                
                else:
                    logger.error(f"CoinGecko simple price error {resp.status}")
                    self.record_error()
                    return {}
        
        except Exception as e:
            logger.error(f"Error fetching simple prices: {e}")
            self.record_error()
            return {}
    
    async def search_coin(self, query: str) -> Optional[Dict]:
        """
        Search for a coin by name or symbol
        
        Args:
            query: Search query
        
        Returns:
            Best match coin info
        """
        try:
            session = await self._get_session()
            
            url = f"{self.BASE_URL}/search"
            params = {"query": query}
            
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    coins = data.get("coins", [])
                    
                    if coins:
                        # Return first match
                        best_match = coins[0]
                        return {
                            "id": best_match.get("id"),
                            "symbol": best_match.get("symbol"),
                            "name": best_match.get("name"),
                            "market_cap_rank": best_match.get("market_cap_rank")
                        }
                    
                    return None
                else:
                    logger.error(f"CoinGecko search error {resp.status}")
                    return None
        
        except Exception as e:
            logger.error(f"Error searching coin: {e}")
            return None
    
    async def close(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def fetch(self, *args, **kwargs):
        """Generic fetch (not implemented for base)"""
        raise NotImplementedError("Use specific fetch methods")

"""
Binance REST API Client
Supports multiple environments: production, demo (spot), testnet (futures)
"""
import asyncio
import aiohttp
import hashlib
import hmac
import time
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urlencode
from utils import get_logger
from .base import DataSource


logger = get_logger(__name__)


class BinanceClient(DataSource):
    """Binance REST API client for market data and trading"""
    
    ENVIRONMENTS = {
        'production': {
            'rest_url': 'https://api.binance.com',
            'ws_url': 'wss://stream.binance.com:9443/ws'
        },
        'demo': {
            'rest_url': 'https://demo-api.binance.com',
            'ws_url': 'wss://demo-stream.binance.com:9443/ws'
        },
        'testnet': {
            'rest_url': 'https://testnet.binance.vision',
            'ws_url': 'wss://testnet.binance.vision/ws'
        }
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        environment: str = 'production'
    ):
        super().__init__("binance")
        self.api_key = api_key
        self.api_secret = api_secret
        self.environment = environment
        
        if environment not in self.ENVIRONMENTS:
            raise ValueError(f"Invalid environment: {environment}. Must be one of {list(self.ENVIRONMENTS.keys())}")
        
        self.base_url = self.ENVIRONMENTS[environment]['rest_url']
        self.session = None
        
        logger.info(f"BinanceClient initialized with environment: {environment}")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    def _generate_signature(self, query_string: str) -> str:
        """Generate HMAC SHA256 signature"""
        if not self.api_secret:
            raise ValueError("API secret is required for signed requests")
        
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _get_headers(self, signed: bool = False) -> Dict:
        """Get request headers"""
        headers = {
            'Content-Type': 'application/json'
        }
        
        if self.api_key:
            headers['X-MBX-APIKEY'] = self.api_key
        
        return headers
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        signed: bool = False,
        timeout: int = 10
    ) -> Dict:
        """Make HTTP request to Binance API"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}{endpoint}"
            
            if params is None:
                params = {}
            
            if signed:
                params['timestamp'] = int(time.time() * 1000)
                params['recvWindow'] = 5000
                query_string = urlencode(params)
                params['signature'] = self._generate_signature(query_string)
            
            headers = self._get_headers(signed=signed)
            
            async with session.request(
                method,
                url,
                params=params,
                headers=headers,
                timeout=timeout
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.record_success()
                    return data
                else:
                    error_text = await resp.text()
                    logger.error(f"Binance API error {resp.status}: {error_text}")
                    self.record_error()
                    return {'error': error_text, 'status': resp.status}
        
        except Exception as e:
            logger.error(f"Binance API request error: {e}")
            self.record_error()
            return {'error': str(e)}
    
    async def health_check(self) -> bool:
        """Check Binance API status"""
        try:
            result = await self._request('GET', '/api/v3/ping', timeout=5)
            return 'error' not in result
        except Exception as e:
            logger.error(f"Binance health check failed: {e}")
            return False
    
    # =========================================================================
    # Market Data Methods
    # =========================================================================
    
    async def fetch_ohlcv(
        self,
        symbol: str,
        interval: str = "1h",
        limit: int = 500,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict]:
        """Fetch OHLCV candlestick data"""
        try:
            if not symbol.endswith("USDT"):
                symbol = f"{symbol}USDT"
            
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": min(limit, 1000)
            }
            
            if start_time:
                params["startTime"] = int(start_time.timestamp() * 1000)
            if end_time:
                params["endTime"] = int(end_time.timestamp() * 1000)
            
            data = await self._request('GET', '/api/v3/klines', params=params)
            
            if 'error' in data:
                return []
            
            candles = []
            for candle in data:
                candles.append({
                    "timestamp": candle[0] // 1000,
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": float(candle[5]),
                    "close_time": candle[6] // 1000,
                    "quote_volume": float(candle[7]),
                    "trades": int(candle[8])
                })
            
            logger.info(f"Fetched {len(candles)} candles for {symbol} {interval}")
            return candles
        
        except Exception as e:
            logger.error(f"Error fetching OHLCV from Binance: {e}")
            self.record_error()
            return []
    
    async def fetch_ticker(self, symbol: str) -> Optional[Dict]:
        """Fetch current ticker price"""
        try:
            if not symbol.endswith("USDT"):
                symbol = f"{symbol}USDT"
            
            data = await self._request('GET', '/api/v3/ticker/24hr', params={"symbol": symbol})
            
            if 'error' in data:
                return None
            
            ticker = {
                "symbol": symbol,
                "price": float(data["lastPrice"]),
                "volume_24h": float(data["volume"]),
                "quote_volume_24h": float(data["quoteVolume"]),
                "price_change_24h_pct": float(data["priceChangePercent"]),
                "high_24h": float(data["highPrice"]),
                "low_24h": float(data["lowPrice"]),
                "trades_24h": int(data["count"]),
                "timestamp": int(data["closeTime"]) // 1000
            }
            
            return ticker
        
        except Exception as e:
            logger.error(f"Error fetching ticker from Binance: {e}")
            self.record_error()
            return None
    
    async def fetch_orderbook(self, symbol: str, limit: int = 100) -> Optional[Dict]:
        """Fetch order book depth"""
        try:
            if not symbol.endswith("USDT"):
                symbol = f"{symbol}USDT"
            
            data = await self._request('GET', '/api/v3/depth', params={"symbol": symbol, "limit": limit})
            
            if 'error' in data:
                return None
            
            orderbook = {
                "symbol": symbol,
                "bids": [[float(p), float(q)] for p, q in data["bids"]],
                "asks": [[float(p), float(q)] for p, q in data["asks"]],
                "timestamp": data["lastUpdateId"]
            }
            
            if orderbook["bids"] and orderbook["asks"]:
                best_bid = orderbook["bids"][0][0]
                best_ask = orderbook["asks"][0][0]
                orderbook["mid_price"] = (best_bid + best_ask) / 2
                orderbook["spread"] = best_ask - best_bid
                orderbook["spread_pct"] = (orderbook["spread"] / orderbook["mid_price"]) * 100
            
            return orderbook
        
        except Exception as e:
            logger.error(f"Error fetching orderbook from Binance: {e}")
            self.record_error()
            return None
    
    # =========================================================================
    # Account Methods (Signed)
    # =========================================================================
    
    async def get_account_info(self) -> Dict:
        """Get account information"""
        return await self._request('GET', '/api/v3/account', signed=True)
    
    async def get_balance(self, asset: str = "USDT") -> float:
        """Get balance for specific asset"""
        account = await self.get_account_info()
        
        if 'error' in account:
            return 0.0
        
        for balance in account.get('balances', []):
            if balance['asset'] == asset:
                return float(balance['free'])
        
        return 0.0
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get open orders"""
        params = {}
        if symbol:
            if not symbol.endswith("USDT"):
                symbol = f"{symbol}USDT"
            params['symbol'] = symbol
        
        return await self._request('GET', '/api/v3/openOrders', params=params, signed=True)
    
    # =========================================================================
    # Order Methods (Signed)
    # =========================================================================
    
    async def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: str = "GTC"
    ) -> Dict:
        """
        Place an order
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: BUY or SELL
            order_type: MARKET, LIMIT, STOP_LOSS_LIMIT, TAKE_PROFIT_LIMIT
            quantity: Order quantity
            price: Limit price (required for LIMIT orders)
            stop_price: Stop price (required for STOP_LOSS/TAKE_PROFIT orders)
            time_in_force: GTC, IOC, FOK
        
        Returns:
            Order response
        """
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        params = {
            'symbol': symbol,
            'side': side.upper(),
            'type': order_type.upper(),
            'quantity': quantity
        }
        
        if order_type.upper() in ['LIMIT', 'STOP_LOSS_LIMIT', 'TAKE_PROFIT_LIMIT']:
            params['price'] = price
            params['timeInForce'] = time_in_force
        
        if order_type.upper() in ['STOP_LOSS_LIMIT', 'STOP_LOSS', 'TAKE_PROFIT_LIMIT', 'TAKE_PROFIT']:
            params['stopPrice'] = stop_price
        
        return await self._request('POST', '/api/v3/order', params=params, signed=True)
    
    async def cancel_order(self, symbol: str, order_id: int) -> Dict:
        """Cancel an order"""
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        
        return await self._request('DELETE', '/api/v3/order', params=params, signed=True)
    
    async def get_order(self, symbol: str, order_id: int) -> Dict:
        """Get order status"""
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        
        return await self._request('GET', '/api/v3/order', params=params, signed=True)
    
    async def close(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def fetch(self, *args, **kwargs):
        """Generic fetch (not implemented for base)"""
        raise NotImplementedError("Use specific fetch methods")

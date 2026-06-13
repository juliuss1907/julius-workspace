"""
Binance Futures REST API Client (Testnet)
"""
import aiohttp
import hashlib
import hmac
import time
from typing import List, Dict, Optional
from urllib.parse import urlencode
from utils import get_logger
from .base import DataSource


logger = get_logger(__name__)


class BinanceFuturesClient(DataSource):
    """Binance Futures REST API client for futures trading"""
    
    ENVIRONMENTS = {
        'production': {
            'rest_url': 'https://fapi.binance.com',
            'ws_url': 'wss://fstream.binance.com/ws'
        },
        'testnet': {
            'rest_url': 'https://testnet.binancefuture.com',
            'ws_url': 'wss://fstream.binancefuture.com/ws'
        }
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        environment: str = 'testnet'
    ):
        super().__init__("binance_futures")
        self.api_key = api_key
        self.api_secret = api_secret
        self.environment = environment
        
        if environment not in self.ENVIRONMENTS:
            raise ValueError(f"Invalid environment: {environment}. Must be one of {list(self.ENVIRONMENTS.keys())}")
        
        self.base_url = self.ENVIRONMENTS[environment]['rest_url']
        self.session = None
        
        logger.info(f"BinanceFuturesClient initialized with environment: {environment}")
    
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
    
    def _get_headers(self) -> Dict:
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
        """Make HTTP request to Binance Futures API"""
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
            
            headers = self._get_headers()
            
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
                    # Check for ignorable errors (e.g., "No need to change margin type")
                    if resp.status == 400 and '-4046' in error_text:
                        logger.debug(f"Binance Futures API info {resp.status}: {error_text}")
                    else:
                        logger.error(f"Binance Futures API error {resp.status}: {error_text}")
                    self.record_error()
                    return {'error': error_text, 'status': resp.status}
        
        except Exception as e:
            logger.error(f"Binance Futures API request error: {e}")
            self.record_error()
            return {'error': str(e)}
    
    async def health_check(self) -> bool:
        """Check Binance Futures API status"""
        try:
            result = await self._request('GET', '/fapi/v1/ping', timeout=5)
            return 'error' not in result
        except Exception as e:
            logger.error(f"Binance Futures health check failed: {e}")
            return False
    
    # =========================================================================
    # Account Methods (Signed)
    # =========================================================================
    
    async def get_account_info(self) -> Dict:
        """Get futures account information"""
        return await self._request('GET', '/fapi/v2/account', signed=True)
    
    async def get_balance(self, asset: str = "USDT") -> float:
        """Get balance for specific asset"""
        account = await self.get_account_info()
        
        if 'error' in account:
            return 0.0
        
        for balance in account.get('assets', []):
            if balance['asset'] == asset:
                return float(balance['walletBalance'])
        
        return 0.0
    
    async def get_positions(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get open positions"""
        params = {}
        if symbol:
            if not symbol.endswith("USDT"):
                symbol = f"{symbol}USDT"
            params['symbol'] = symbol
        
        data = await self._request('GET', '/fapi/v2/positionRisk', params=params, signed=True)
        
        if 'error' in data:
            return []
        
        positions = []
        for pos in data:
            if float(pos['positionAmt']) != 0:
                positions.append({
                    'symbol': pos['symbol'],
                    'side': 'LONG' if float(pos['positionAmt']) > 0 else 'SHORT',
                    'amount': abs(float(pos['positionAmt'])),
                    'entry_price': float(pos['entryPrice']),
                    'mark_price': float(pos['markPrice']),
                    'unrealized_pnl': float(pos['unRealizedProfit']),
                    'leverage': float(pos['leverage']),
                    'margin_type': pos['marginType'],
                    'liquidation_price': float(pos['liquidationPrice']) if pos['liquidationPrice'] else None
                })
        
        return positions
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get open orders"""
        params = {}
        if symbol:
            if not symbol.endswith("USDT"):
                symbol = f"{symbol}USDT"
            params['symbol'] = symbol
        
        return await self._request('GET', '/fapi/v1/openOrders', params=params, signed=True)
    
    # =========================================================================
    # Leverage & Margin Methods (Signed)
    # =========================================================================
    
    async def set_leverage(self, symbol: str, leverage: int) -> Dict:
        """Set leverage for a symbol"""
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        params = {
            'symbol': symbol,
            'leverage': leverage
        }
        
        return await self._request('POST', '/fapi/v1/leverage', params=params, signed=True)
    
    async def set_margin_type(self, symbol: str, margin_type: str = "ISOLATED") -> Dict:
        """Set margin type (ISOLATED or CROSSED)"""
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        params = {
            'symbol': symbol,
            'marginType': margin_type.upper()
        }
        
        return await self._request('POST', '/fapi/v1/marginType', params=params, signed=True)
    
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
        position_side: str = "BOTH",
        time_in_force: str = "GTC",
        reduce_only: bool = False
    ) -> Dict:
        """
        Place a futures order
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: BUY or SELL
            order_type: MARKET, LIMIT, STOP, TAKE_PROFIT, etc.
            quantity: Order quantity
            price: Limit price (required for LIMIT orders)
            stop_price: Stop price (required for STOP/TAKE_PROFIT orders)
            position_side: LONG, SHORT, or BOTH (for one-way mode)
            time_in_force: GTC, IOC, FOK
            reduce_only: True if this order only reduces position
        
        Returns:
            Order response
        """
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        params = {
            'symbol': symbol,
            'side': side.upper(),
            'type': order_type.upper(),
            'quantity': quantity,
            'positionSide': position_side.upper()
        }
        
        if reduce_only:
            params['reduceOnly'] = 'true'
        
        if order_type.upper() in ['LIMIT']:
            params['price'] = price
            params['timeInForce'] = time_in_force
        
        if order_type.upper() in ['STOP', 'TAKE_PROFIT']:
            params['stopPrice'] = stop_price
            if price:
                params['price'] = price
                params['timeInForce'] = time_in_force
        
        return await self._request('POST', '/fapi/v1/order', params=params, signed=True)
    
    async def cancel_order(self, symbol: str, order_id: int) -> Dict:
        """Cancel an order"""
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        
        return await self._request('DELETE', '/fapi/v1/order', params=params, signed=True)
    
    async def get_order(self, symbol: str, order_id: int) -> Dict:
        """Get order status"""
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"

        params = {
            'symbol': symbol,
            'orderId': order_id
        }

        return await self._request('GET', '/fapi/v1/order', params=params, signed=True)

    async def get_all_orders(
        self,
        symbol: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 50,
    ) -> List[Dict]:
        """List futures orders for a symbol within a time window.

        Uses /fapi/v1/allOrders which returns historical orders for the
        account (signed endpoint, requires API key+secret).
        """
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        params = {"symbol": symbol, "limit": min(max(limit, 1), 1000)}
        if start_time is not None:
            params["startTime"] = int(start_time)
        if end_time is not None:
            params["endTime"] = int(end_time)
        data = await self._request('GET', '/fapi/v1/allOrders', params=params, signed=True)
        if isinstance(data, dict) and 'error' in data:
            return []
        if not isinstance(data, list):
            return []
        return data

    async def get_user_trades(
        self,
        symbol: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 50,
    ) -> List[Dict]:
        """List futures account trades (fills) for a symbol within a time window.

        Uses /fapi/v1/userTrades which returns the executed trades
        (fills), each with executedQty, executedPrice, commission, etc.
        """
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        params = {"symbol": symbol, "limit": min(max(limit, 1), 1000)}
        if start_time is not None:
            params["startTime"] = int(start_time)
        if end_time is not None:
            params["endTime"] = int(end_time)
        data = await self._request('GET', '/fapi/v1/userTrades', params=params, signed=True)
        if isinstance(data, dict) and 'error' in data:
            return []
        if not isinstance(data, list):
            return []
        return data
    
    # =========================================================================
    # Market Data Methods
    # =========================================================================
    
    async def fetch_ticker(self, symbol: str) -> Optional[Dict]:
        """Fetch current ticker price"""
        try:
            if not symbol.endswith("USDT"):
                symbol = f"{symbol}USDT"

            data = await self._request('GET', '/fapi/v1/ticker/24hr', params={"symbol": symbol})

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
                "timestamp": int(data["closeTime"]) // 1000
            }

            return ticker

        except Exception as e:
            logger.error(f"Error fetching ticker from Binance Futures: {e}")
            self.record_error()
            return None

    async def fetch_ohlcv(
        self,
        symbol: str,
        interval: str = "1h",
        limit: int = 500,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> List[Dict]:
        """Fetch OHLCV candlestick data from Binance Futures (public)."""
        try:
            if not symbol.endswith("USDT"):
                symbol = f"{symbol}USDT"

            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": min(limit, 1500),
            }
            if start_time is not None:
                params["startTime"] = int(start_time)
            if end_time is not None:
                params["endTime"] = int(end_time)

            data = await self._request('GET', '/fapi/v1/klines', params=params)
            if isinstance(data, dict) and 'error' in data:
                return []

            candles = []
            for c in data:
                candles.append({
                    "timestamp": int(c[0]) // 1000,
                    "open": float(c[1]),
                    "high": float(c[2]),
                    "low": float(c[3]),
                    "close": float(c[4]),
                    "volume": float(c[5]),
                    "close_time": int(c[6]) // 1000,
                    "quote_volume": float(c[7]),
                    "trades": int(c[8]),
                })
            return candles
        except Exception as e:
            logger.error(f"Error fetching OHLCV from Binance Futures: {e}")
            self.record_error()
            return []
    
    async def close(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def fetch(self, *args, **kwargs):
        """Generic fetch (not implemented for base)"""
        raise NotImplementedError("Use specific fetch methods")

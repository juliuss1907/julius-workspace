"""
Parallel Data Fetcher
Fetch data from multiple sources concurrently
"""
import asyncio
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from utils import get_logger
from .retry import retry_with_backoff


logger = get_logger(__name__)


class ParallelFetcher:
    """Orchestrate parallel data fetching from multiple sources"""
    
    def __init__(self):
        self.sources = {}
    
    def register_source(self, name: str, source: Any):
        """Register a data source"""
        self.sources[name] = source
        logger.info(f"Registered data source: {name}")
    
    async def fetch_parallel(
        self,
        tasks: List[Dict[str, Any]],
        required_sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Fetch data from multiple sources in parallel
        
        Args:
            tasks: List of task dicts with 'source', 'method', 'args', 'kwargs'
            required_sources: List of source names that MUST succeed
        
        Returns:
            Dict mapping source names to results (or Exception if failed)
        
        Example:
            tasks = [
                {
                    'source': 'binance',
                    'method': 'fetch_ticker',
                    'args': ['BTC'],
                    'kwargs': {}
                },
                {
                    'source': 'geckoterminal',
                    'method': 'fetch_price',
                    'args': ['BTC'],
                    'kwargs': {}
                }
            ]
            results = await fetcher.fetch_parallel(tasks, required_sources=['binance'])
        """
        # Create async tasks
        async_tasks = []
        task_names = []
        
        for task_spec in tasks:
            source_name = task_spec['source']
            method_name = task_spec['method']
            args = task_spec.get('args', [])
            kwargs = task_spec.get('kwargs', {})
            
            if source_name not in self.sources:
                logger.warning(f"Source {source_name} not registered, skipping")
                continue
            
            source = self.sources[source_name]
            method = getattr(source, method_name, None)
            
            if method is None:
                logger.warning(f"Method {method_name} not found on {source_name}, skipping")
                continue
            
            # Wrap in retry logic
            async_task = retry_with_backoff(
                method,
                *args,
                retries=3,
                backoff_base=2.0,
                timeout=10,
                **kwargs
            )
            
            async_tasks.append(async_task)
            task_names.append(source_name)
        
        # Execute all tasks concurrently
        logger.info(f"Fetching from {len(async_tasks)} sources in parallel...")
        results = await asyncio.gather(*async_tasks, return_exceptions=True)
        
        # Build result dict
        result_dict = {}
        for name, result in zip(task_names, results):
            if isinstance(result, Exception):
                logger.error(f"Source {name} failed: {result}")
                result_dict[name] = None
            else:
                result_dict[name] = result
                logger.debug(f"Source {name} succeeded")
        
        # Check required sources
        if required_sources:
            missing = []
            for req_source in required_sources:
                if req_source not in result_dict or result_dict[req_source] is None:
                    missing.append(req_source)
            
            if missing:
                raise Exception(f"Required sources failed: {missing}")
        
        # Count successes
        success_count = sum(1 for v in result_dict.values() if v is not None)
        logger.info(f"Parallel fetch completed: {success_count}/{len(result_dict)} sources succeeded")
        
        return result_dict
    
    async def fetch_ohlcv_multi_source(
        self,
        coin: str,
        interval: str = "1h",
        limit: int = 500
    ) -> Dict[str, List[Dict]]:
        """
        Fetch OHLCV from multiple sources
        
        Returns:
            Dict mapping source name to OHLCV data
        """
        tasks = []
        
        # Binance
        if 'binance' in self.sources:
            tasks.append({
                'source': 'binance',
                'method': 'fetch_ohlcv',
                'args': [coin, interval, limit],
                'kwargs': {}
            })
        
        # Add more sources here when implemented
        # if 'geckoterminal' in self.sources: ...
        
        return await self.fetch_parallel(tasks, required_sources=['binance'])
    
    async def fetch_ticker_multi_source(
        self,
        coin: str
    ) -> Dict[str, Dict]:
        """
        Fetch current ticker from multiple sources
        
        Returns:
            Dict mapping source name to ticker data
        """
        tasks = []
        
        if 'binance' in self.sources:
            tasks.append({
                'source': 'binance',
                'method': 'fetch_ticker',
                'args': [coin],
                'kwargs': {}
            })
        
        return await self.fetch_parallel(tasks)
    
    async def fetch_orderbook_multi_source(
        self,
        coin: str,
        limit: int = 100
    ) -> Dict[str, Dict]:
        """
        Fetch order book from multiple sources
        
        Returns:
            Dict mapping source name to orderbook data
        """
        tasks = []
        
        if 'binance' in self.sources:
            tasks.append({
                'source': 'binance',
                'method': 'fetch_orderbook',
                'args': [coin],
                'kwargs': {'limit': limit}
            })
        
        return await self.fetch_parallel(tasks)
    
    async def close_all(self):
        """Close all data sources"""
        for name, source in self.sources.items():
            if hasattr(source, 'close'):
                await source.close()
                logger.info(f"Closed data source: {name}")

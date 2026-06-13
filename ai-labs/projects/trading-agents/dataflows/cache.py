"""
Cache Layer with TTL
"""
import json
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional
from utils import get_logger


logger = get_logger(__name__)


class Cache:
    """Simple file-based cache with TTL"""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._memory_cache = {}  # In-memory cache for speed
    
    def _get_cache_key(self, key: str) -> str:
        """Generate safe filename from cache key"""
        return key.replace("/", "_").replace(":", "_")
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path"""
        safe_key = self._get_cache_key(key)
        return self.cache_dir / f"{safe_key}.json"
    
    async def get(self, key: str, max_age_seconds: Optional[int] = None) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            max_age_seconds: Max age in seconds (None = use TTL from cached data)
        
        Returns:
            Cached value or None if expired/missing
        """
        # Check memory cache first
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            if self._is_valid(entry, max_age_seconds):
                logger.debug(f"Cache HIT (memory): {key}")
                return entry["data"]
        
        # Check file cache
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            logger.debug(f"Cache MISS: {key}")
            return None
        
        try:
            with open(cache_path) as f:
                entry = json.load(f)
            
            # Validate expiry
            if self._is_valid(entry, max_age_seconds):
                # Update memory cache
                self._memory_cache[key] = entry
                logger.debug(f"Cache HIT (file): {key}")
                return entry["data"]
            else:
                logger.debug(f"Cache EXPIRED: {key}")
                # Delete expired cache
                cache_path.unlink()
                return None
        
        except Exception as e:
            logger.error(f"Error reading cache {key}: {e}")
            return None
    
    async def set(
        self,
        key: str,
        data: Any,
        ttl_seconds: int = 300
    ):
        """
        Set value in cache with TTL
        
        Args:
            key: Cache key
            data: Data to cache (must be JSON serializable)
            ttl_seconds: Time to live in seconds
        """
        expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
        
        entry = {
            "data": data,
            "cached_at": datetime.now().isoformat(),
            "expires_at": expires_at.isoformat(),
            "ttl_seconds": ttl_seconds
        }
        
        # Save to memory
        self._memory_cache[key] = entry
        
        # Save to file
        try:
            cache_path = self._get_cache_path(key)
            with open(cache_path, "w") as f:
                json.dump(entry, f, indent=2)
            
            logger.debug(f"Cache SET: {key} (TTL: {ttl_seconds}s)")
        
        except Exception as e:
            logger.error(f"Error writing cache {key}: {e}")
    
    def _is_valid(self, entry: dict, max_age_seconds: Optional[int] = None) -> bool:
        """Check if cache entry is still valid"""
        expires_at = datetime.fromisoformat(entry["expires_at"])
        
        if max_age_seconds is not None:
            # Override TTL with max_age
            cached_at = datetime.fromisoformat(entry["cached_at"])
            age = (datetime.now() - cached_at).total_seconds()
            return age < max_age_seconds
        else:
            # Use original TTL
            return datetime.now() < expires_at
    
    async def delete(self, key: str):
        """Delete cache entry"""
        # Delete from memory
        if key in self._memory_cache:
            del self._memory_cache[key]
        
        # Delete file
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()
            logger.debug(f"Cache DELETED: {key}")
    
    async def clear_expired(self):
        """Clear all expired cache entries"""
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file) as f:
                    entry = json.load(f)
                
                if not self._is_valid(entry):
                    cache_file.unlink()
                    count += 1
            
            except Exception as e:
                logger.error(f"Error checking cache file {cache_file}: {e}")
        
        if count > 0:
            logger.info(f"Cleared {count} expired cache entries")
        
        # Clear memory cache
        expired_keys = [
            key for key, entry in self._memory_cache.items()
            if not self._is_valid(entry)
        ]
        for key in expired_keys:
            del self._memory_cache[key]
    
    async def get_with_fallback(
        self,
        key: str,
        fetch_func,
        ttl_seconds: int = 300,
        max_age_seconds: Optional[int] = None
    ) -> Any:
        """
        Get from cache, or fetch and cache if miss
        
        Args:
            key: Cache key
            fetch_func: Async function to fetch data if cache miss
            ttl_seconds: TTL for newly cached data
            max_age_seconds: Max acceptable age for cached data
        
        Returns:
            Data from cache or fresh fetch
        """
        # Try cache first
        cached = await self.get(key, max_age_seconds)
        if cached is not None:
            return cached
        
        # Cache miss - fetch fresh data
        logger.debug(f"Cache miss, fetching fresh: {key}")
        data = await fetch_func()
        
        if data is not None:
            await self.set(key, data, ttl_seconds)
        
        return data


# Global cache instance
cache = Cache()

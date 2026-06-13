"""
Retry Logic with Exponential Backoff
"""
import asyncio
from typing import Callable, Any, Optional
from utils import get_logger


logger = get_logger(__name__)


async def retry_with_backoff(
    func: Callable,
    *args,
    retries: int = 3,
    backoff_base: float = 2.0,
    timeout: Optional[float] = None,
    **kwargs
) -> Any:
    """
    Retry a function with exponential backoff
    
    Args:
        func: Async function to retry
        retries: Number of retry attempts
        backoff_base: Base for exponential backoff (2 = 2s, 4s, 8s)
        timeout: Optional timeout per attempt
        *args, **kwargs: Arguments for func
    
    Returns:
        Result from func
    
    Raises:
        Last exception if all retries fail
    """
    last_exception = None
    
    for attempt in range(retries):
        try:
            # Apply timeout if specified
            if timeout:
                result = await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
            else:
                result = await func(*args, **kwargs)
            
            # Success
            if attempt > 0:
                logger.info(f"{func.__name__} succeeded on attempt {attempt + 1}")
            return result
        
        except asyncio.TimeoutError as e:
            last_exception = e
            logger.warning(f"{func.__name__} timeout on attempt {attempt + 1}/{retries}")
        
        except Exception as e:
            last_exception = e
            logger.warning(f"{func.__name__} failed attempt {attempt + 1}/{retries}: {e}")
        
        # Don't sleep after last attempt
        if attempt < retries - 1:
            wait_time = backoff_base ** attempt
            logger.info(f"Retrying {func.__name__} in {wait_time}s...")
            await asyncio.sleep(wait_time)
    
    # All retries failed
    logger.error(f"{func.__name__} failed after {retries} attempts")
    raise last_exception


class CircuitBreaker:
    """Circuit breaker pattern for API calls"""
    
    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 900):
        """
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout_seconds: How long to keep circuit open (15 min default)
        """
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.opened_at = None
        self.last_failure_time = None
    
    def is_open(self) -> bool:
        """Check if circuit is open (blocking calls)"""
        if self.opened_at is None:
            return False
        
        # Check if timeout has passed
        import time
        if time.time() - self.opened_at > self.timeout_seconds:
            # Reset circuit
            logger.info(f"Circuit breaker reset after {self.timeout_seconds}s timeout")
            self.reset()
            return False
        
        return True
    
    def record_success(self):
        """Record successful call"""
        self.failure_count = 0
        self.last_failure_time = None
    
    def record_failure(self):
        """Record failed call"""
        import time
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.opened_at = time.time()
            logger.error(
                f"Circuit breaker OPENED after {self.failure_count} failures. "
                f"Will retry in {self.timeout_seconds}s"
            )
    
    def reset(self):
        """Reset circuit breaker"""
        self.failure_count = 0
        self.opened_at = None
        self.last_failure_time = None

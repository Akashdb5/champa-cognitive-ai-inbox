"""
Retry logic with exponential backoff for platform API calls
Validates: Requirements 16.1
"""
import asyncio
import logging
from functools import wraps
from typing import Callable, TypeVar, Any, Optional, Type, Tuple
import time

logger = logging.getLogger(__name__)

T = TypeVar('T')


def calculate_exponential_backoff(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0
) -> float:
    """
    Calculate exponential backoff delay
    
    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential calculation
    
    Returns:
        float: Delay in seconds
    """
    delay = base_delay * (exponential_base ** attempt)
    return min(delay, max_delay)


def retry_with_exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int, float], None]] = None
):
    """
    Decorator for retrying functions with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential calculation
        exceptions: Tuple of exception types to catch and retry
        on_retry: Optional callback function called on each retry
    
    Returns:
        Decorated function
    
    Example:
        @retry_with_exponential_backoff(max_retries=3, base_delay=1.0)
        async def fetch_data():
            # API call that might fail
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        delay = calculate_exponential_backoff(
                            attempt,
                            base_delay,
                            max_delay,
                            exponential_base
                        )
                        
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {delay:.2f} seconds..."
                        )
                        
                        if on_retry:
                            on_retry(e, attempt + 1, delay)
                        
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts failed for {func.__name__}: {str(e)}"
                        )
            
            # If we get here, all retries failed
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        delay = calculate_exponential_backoff(
                            attempt,
                            base_delay,
                            max_delay,
                            exponential_base
                        )
                        
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {delay:.2f} seconds..."
                        )
                        
                        if on_retry:
                            on_retry(e, attempt + 1, delay)
                        
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts failed for {func.__name__}: {str(e)}"
                        )
            
            # If we get here, all retries failed
            raise last_exception
        
        # Return appropriate wrapper based on whether function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class RetryableError(Exception):
    """Base exception for errors that should trigger retries"""
    pass


class PlatformAPIError(RetryableError):
    """Exception for platform API errors that should be retried"""
    pass


class NetworkError(RetryableError):
    """Exception for network errors that should be retried"""
    pass


class RateLimitError(RetryableError):
    """Exception for rate limit errors that should be retried"""
    pass

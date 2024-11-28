import asyncio
import logging
from functools import wraps
from typing import Callable, TypeVar, Any

T = TypeVar('T')

def async_retry(
    retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Async retry decorator with exponential backoff
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            retry_count = 0
            current_delay = delay
            
            while retry_count < retries:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    retry_count += 1
                    if retry_count == retries:
                        raise e
                    
                    logging.warning(
                        f"Retry {retry_count}/{retries} for {func.__name__} "
                        f"after error: {str(e)}"
                    )
                    
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator 
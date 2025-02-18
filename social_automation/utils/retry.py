import asyncio
from functools import wraps
import logging
import time

logger = logging.getLogger(__name__)

def async_retry(
    retries=3,
    delay=1,
    backoff=2,
    exceptions=(Exception,)
):
    """Retry decorator for async functions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retry_count = 0
            current_delay = delay
            
            while retry_count < retries:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    retry_count += 1
                    
                    if retry_count == retries:
                        logger.error(
                            f"Max retries ({retries}) reached for {func.__name__}"
                        )
                        raise
                        
                    logger.warning(
                        f"Attempt {retry_count} failed for {func.__name__}: {str(e)}"
                        f"\nRetrying in {current_delay} seconds..."
                    )
                    
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
                    
        return wrapper
    return decorator

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold=5,
        reset_timeout=60,
        half_open_timeout=30
    ):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.half_open_timeout = half_open_timeout
        self.failures = {}
        self.state = 'closed'
        self.last_failure_time = 0
        
    def can_execute(self):
        """Check if execution is allowed"""
        if self.state == 'open':
            if time.time() - self.last_failure_time >= self.reset_timeout:
                self.state = 'half-open'
                return True
            return False
            
        return True
        
    def record_failure(self):
        """Record a failure"""
        current_time = time.time()
        self.failures = {
            t for t in self.failures 
            if current_time - t <= self.reset_timeout
        }
        
        self.failures.add(current_time)
        self.last_failure_time = current_time
        
        if len(self.failures) >= self.failure_threshold:
            self.state = 'open'
            logger.warning("Circuit breaker opened")
            
    def record_success(self):
        """Record a success"""
        if self.state == 'half-open':
            self.state = 'closed'
            self.failures.clear()
            logger.info("Circuit breaker closed") 
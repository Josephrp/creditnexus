"""
Rate limiter utility for external API calls.

This module provides rate limiting functionality to prevent hitting external API
rate limits (e.g., Companies House API, SEC API, etc.).
"""

import logging
import time
from typing import Dict, Optional
from threading import Lock
from collections import deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RateLimiter:
    """Thread-safe rate limiter for API calls.
    
    Implements token bucket algorithm with sliding window to respect
    external API rate limits.
    """
    
    def __init__(
        self,
        max_requests: int,
        time_window_seconds: int,
        name: Optional[str] = None
    ):
        """Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in time window
            time_window_seconds: Time window in seconds (e.g., 60 for per-minute)
            name: Optional name for logging
        """
        self.max_requests = max_requests
        self.time_window_seconds = time_window_seconds
        self.name = name or "RateLimiter"
        
        # Thread-safe request tracking
        self._lock = Lock()
        self._request_times: deque = deque()
    
    def acquire(self, timeout: Optional[float] = None) -> bool:
        """Acquire permission to make a request.
        
        Args:
            timeout: Maximum time to wait (None for no wait)
            
        Returns:
            True if permission granted, False if timeout
        """
        with self._lock:
            now = time.time()
            
            # Remove old requests outside the time window
            cutoff = now - self.time_window_seconds
            while self._request_times and self._request_times[0] < cutoff:
                self._request_times.popleft()
            
            # Check if we can make a request
            if len(self._request_times) < self.max_requests:
                self._request_times.append(now)
                return True
            
            # Need to wait
            if timeout is None:
                return False
            
            # Calculate wait time
            oldest_request = self._request_times[0]
            wait_time = (oldest_request + self.time_window_seconds) - now
            
            if wait_time > timeout:
                return False
            
            # Wait and retry
            time.sleep(wait_time)
            
            # Remove the oldest request and add new one
            self._request_times.popleft()
            self._request_times.append(time.time())
            return True
    
    def wait_if_needed(self) -> None:
        """Wait if necessary to respect rate limit.
        
        This is a blocking call that will wait until a request can be made.
        """
        while not self.acquire(timeout=300):  # Max 5 minute wait
            logger.warning(
                f"{self.name}: Rate limit reached, waiting..."
            )
    
    def get_wait_time(self) -> float:
        """Get time to wait before next request can be made.
        
        Returns:
            Seconds to wait (0 if no wait needed)
        """
        with self._lock:
            now = time.time()
            cutoff = now - self.time_window_seconds
            
            # Remove old requests
            while self._request_times and self._request_times[0] < cutoff:
                self._request_times.popleft()
            
            if len(self._request_times) < self.max_requests:
                return 0.0
            
            # Calculate wait time
            oldest_request = self._request_times[0]
            wait_time = (oldest_request + self.time_window_seconds) - now
            return max(0.0, wait_time)
    
    def reset(self) -> None:
        """Reset rate limiter (clear all request history)."""
        with self._lock:
            self._request_times.clear()


class APIRateLimitManager:
    """Manager for multiple rate limiters (one per API)."""
    
    _limiters: Dict[str, RateLimiter] = {}
    _lock = Lock()
    
    @classmethod
    def get_limiter(
        cls,
        api_name: str,
        max_requests: int,
        time_window_seconds: int
    ) -> RateLimiter:
        """Get or create rate limiter for an API.
        
        Args:
            api_name: Name of the API (e.g., "companies_house")
            max_requests: Maximum requests per time window
            time_window_seconds: Time window in seconds
            
        Returns:
            RateLimiter instance
        """
        with cls._lock:
            if api_name not in cls._limiters:
                cls._limiters[api_name] = RateLimiter(
                    max_requests=max_requests,
                    time_window_seconds=time_window_seconds,
                    name=api_name
                )
            return cls._limiters[api_name]
    
    @classmethod
    def reset_limiter(cls, api_name: str) -> None:
        """Reset rate limiter for an API.
        
        Args:
            api_name: Name of the API
        """
        with cls._lock:
            if api_name in cls._limiters:
                cls._limiters[api_name].reset()


# Pre-configured rate limiters for known APIs
# Companies House API: 600 requests per 5 minutes (per API key)
COMPANIES_HOUSE_LIMITER = APIRateLimitManager.get_limiter(
    api_name="companies_house",
    max_requests=600,
    time_window_seconds=300  # 5 minutes
)

# SEC EDGAR API: 10 requests per second
SEC_EDGAR_LIMITER = APIRateLimitManager.get_limiter(
    api_name="sec_edgar",
    max_requests=10,
    time_window_seconds=1
)

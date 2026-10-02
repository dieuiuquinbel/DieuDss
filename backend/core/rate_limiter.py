"""
NutriDSS - Lightweight Sliding Window Rate Limiter
Prevents resource exhaustion on intensive ML and Optimization endpoints.
"""

import time
from collections import defaultdict
from typing import Dict, List
from fastapi import Request, HTTPException, status
from backend.core.config import settings

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60.0
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def check(self, request: Request, custom_limit: int = None):
        """
        Check if client IP has exceeded the allowed rate limit.
        """
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        limit = custom_limit or self.requests_per_minute
        
        # Purge timestamps outside sliding window
        window_start = now - self.window_seconds
        timestamps = [t for t in self.requests[client_ip] if t > window_start]
        
        if len(timestamps) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Quá nhiều yêu cầu. Giới hạn tối đa {limit} yêu cầu/phút. Vui lòng thử lại sau.",
                headers={"Retry-After": "60"}
            )
        
        timestamps.append(now)
        self.requests[client_ip] = timestamps

limiter = RateLimiter(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)

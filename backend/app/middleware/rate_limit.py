"""
Rate Limiting Middleware for FastAPI.
Uses in-memory storage for MVP (replace with Redis for production).
"""
from fastapi import Request, HTTPException, status
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple
import asyncio
import jwt

from ..config import settings
from ..errors import ErrorCode


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        # Format: {client_ip: [(timestamp, count), ...]}
        self._requests: Dict[str, list] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def is_rate_limited(
        self, 
        key: str, 
        max_requests: int, 
        window_seconds: int
    ) -> Tuple[bool, int]:
        """
        Check if the key has exceeded the rate limit.
        Returns (is_limited, remaining_requests).
        """
        async with self._lock:
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=window_seconds)
            
            # Clean old entries
            self._requests[key] = [
                ts for ts in self._requests[key] 
                if ts > window_start
            ]
            
            current_count = len(self._requests[key])
            remaining = max(0, max_requests - current_count)
            
            if current_count >= max_requests:
                return True, 0
            
            # Record this request
            self._requests[key].append(now)
            return False, remaining - 1

    async def reset(self) -> None:
        """Reset in-memory counters (primarily for tests)."""
        async with self._lock:
            self._requests.clear()

# Global rate limiter instance
rate_limiter = RateLimiter()


# Rate limit configurations per endpoint pattern
RATE_LIMITS = {
    "/api/auth/login": {"max_requests": 10, "window_seconds": 60},     # 10 req/min
    "/api/auth/signup": {"max_requests": 5, "window_seconds": 60},     # 5 req/min
    "/api/auth/": {"max_requests": 20, "window_seconds": 60},          # 20 req/min default
    "/api/jobs/upload": {"max_requests": 5, "window_seconds": 3600},   # 5 uploads/hour
    "/api/agents": {"max_requests": 30, "window_seconds": 3600},       # 30 req/hour
}


def get_rate_limit_config(path: str) -> dict | None:
    """Get rate limit config for a given path."""
    for pattern, config in RATE_LIMITS.items():
        if path.startswith(pattern):
            return config
    return None


async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware.
    Applies rate limits based on client IP and endpoint.
    """
    if not settings.rate_limit_enabled:
        return await call_next(request)
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    path = request.url.path
    user_key = None

    # Try to identify user from JWT (if present)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "").strip()
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
            user_id = payload.get("sub")
            if user_id:
                user_key = f"user:{user_id}"
        except Exception:
            user_key = None
    
    # Check if this path has rate limiting
    config = get_rate_limit_config(path)
    
    if config:
        # Create a unique key per user (if available) or IP
        identity = user_key or f"ip:{client_ip}"
        key = f"{identity}:{path}"
        
        is_limited, remaining = await rate_limiter.is_rate_limited(
            key, 
            config["max_requests"], 
            config["window_seconds"]
        )
        
        if is_limited:
            retry_after = config["window_seconds"]
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error_code": ErrorCode.RATE_LIMITED.value,
                    "message": f"Rate limit exceeded. Try again in {retry_after} seconds.",
                    "metadata": {"retry_after": retry_after, "limit": config["max_requests"]},
                },
                headers={"Retry-After": str(retry_after)},
            )
    
    response = await call_next(request)
    
    # Add rate limit headers if applicable
    if config:
        response.headers["X-RateLimit-Limit"] = str(config["max_requests"])
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(config["window_seconds"])
    
    return response

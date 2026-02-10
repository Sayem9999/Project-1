"""
Redis Memory Store - Short-term run memory for session state and recent context.
Uses TTL-based expiration for automatic cleanup.
"""
import os
import json
import structlog
from typing import Optional, Any, Dict, List
from datetime import timedelta

logger = structlog.get_logger()

# Redis client (lazy import to handle missing dependency)
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None


class RedisMemoryStore:
    """
    Short-term memory store using Redis.
    Stores session state, recent context, and temporary data with TTL.
    """
    
    DEFAULT_TTL = timedelta(hours=24)
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL") or "redis://localhost:6379/0"
        self._client: Optional[Any] = None
    
    async def _get_client(self):
        """Lazy initialize Redis client."""
        if not REDIS_AVAILABLE:
            logger.warning("redis_not_available", message="Redis package not installed")
            return None
        
        if self._client is None:
            try:
                self._client = redis.from_url(self.redis_url, decode_responses=True)
                await self._client.ping()
                logger.info("redis_connected", url=self.redis_url)
            except Exception as e:
                logger.error("redis_connection_failed", error=str(e))
                self._client = None
        
        return self._client
    
    async def set_session(
        self, 
        user_id: int, 
        session_id: str, 
        data: Dict[str, Any],
        ttl: Optional[timedelta] = None
    ) -> bool:
        """Store session data with TTL."""
        client = await self._get_client()
        if not client:
            return False
        
        key = f"session:{user_id}:{session_id}"
        ttl = ttl or self.DEFAULT_TTL
        
        try:
            await client.setex(key, int(ttl.total_seconds()), json.dumps(data))
            logger.debug("session_stored", user_id=user_id, session_id=session_id)
            return True
        except Exception as e:
            logger.error("session_store_failed", error=str(e))
            return False
    
    async def get_session(self, user_id: int, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data."""
        client = await self._get_client()
        if not client:
            return None
        
        key = f"session:{user_id}:{session_id}"
        
        try:
            data = await client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error("session_get_failed", error=str(e))
            return None
    
    async def add_recent_context(
        self, 
        user_id: int, 
        context_type: str, 
        content: str,
        max_items: int = 10
    ) -> bool:
        """Add to recent context list (FIFO queue)."""
        client = await self._get_client()
        if not client:
            return False
        
        key = f"context:{user_id}:{context_type}"
        
        try:
            await client.lpush(key, content)
            await client.ltrim(key, 0, max_items - 1)
            await client.expire(key, int(self.DEFAULT_TTL.total_seconds()))
            return True
        except Exception as e:
            logger.error("context_add_failed", error=str(e))
            return False
    
    async def get_recent_context(
        self, 
        user_id: int, 
        context_type: str,
        count: int = 5
    ) -> List[str]:
        """Get recent context items."""
        client = await self._get_client()
        if not client:
            return []
        
        key = f"context:{user_id}:{context_type}"
        
        try:
            return await client.lrange(key, 0, count - 1)
        except Exception as e:
            logger.error("context_get_failed", error=str(e))
            return []
    
    async def cache_response(
        self, 
        prompt_hash: str, 
        response: Dict[str, Any],
        ttl: timedelta = timedelta(hours=1)
    ) -> bool:
        """Cache agent response by prompt hash."""
        client = await self._get_client()
        if not client:
            return False
        
        key = f"cache:{prompt_hash}"
        
        try:
            await client.setex(key, int(ttl.total_seconds()), json.dumps(response))
            logger.debug("response_cached", hash=prompt_hash[:16])
            return True
        except Exception as e:
            logger.error("cache_store_failed", error=str(e))
            return False
    
    async def get_cached_response(self, prompt_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached response by prompt hash."""
        client = await self._get_client()
        if not client:
            return None
        
        key = f"cache:{prompt_hash}"
        
        try:
            data = await client.get(key)
            if data:
                logger.debug("cache_hit", hash=prompt_hash[:16])
                return json.loads(data)
            return None
        except Exception as e:
            logger.error("cache_get_failed", error=str(e))
            return None
    
    async def close(self):
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None


# Global instance
redis_store = RedisMemoryStore()

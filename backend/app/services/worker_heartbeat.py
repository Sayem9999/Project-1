import time
import os
import redis
from ..config import settings
import structlog

logger = structlog.get_logger()

def update_worker_heartbeat():
    """
    Update a heartbeat timestamp in Redis to signal that the local worker is alive.
    Should be called periodically from the celery worker.
    """
    if not settings.redis_url:
        return
        
    try:
        # Using synchronous redis client as this is called from Celery worker threads/signals
        r = redis.from_url(settings.redis_url, socket_timeout=2)
        r.set("worker:heartbeat:local", int(time.time()))
        # Also set a TTL so if the worker crashes, the key eventually disappears
        r.expire("worker:heartbeat:local", 60) 
    except Exception as e:
        logger.warning("worker_heartbeat_failed", error=str(e))

def get_worker_status() -> dict:
    """
    Check the current heartbeat status.
    """
    if not settings.redis_url:
        return {"status": "unknown", "last_heartbeat": 0}
        
    try:
        r = redis.from_url(settings.redis_url, decode_responses=True, socket_timeout=2)
        last_beat = r.get("worker:heartbeat:local")
        if not last_beat:
            return {"status": "offline", "last_heartbeat": 0}
            
        diff = int(time.time()) - int(last_beat)
        if diff < 45: # Tolerant threshold
            return {"status": "online", "last_heartbeat": int(last_beat)}
        else:
            return {"status": "stale", "last_heartbeat": int(last_beat)}
    except Exception:
        return {"status": "error", "last_heartbeat": 0}

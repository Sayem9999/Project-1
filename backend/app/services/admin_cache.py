import asyncio
import time
from datetime import datetime, timedelta
from typing import Any, Dict
import structlog
from sqlalchemy import select, func
from ..db import SessionLocal
from ..models import User, Job
from ..services.storage_service import storage_service

logger = structlog.get_logger()

# Global in-memory cache
_ADMIN_STATS = {}
_ADMIN_HEALTH = {}
_LAST_REFRESH = 0

async def refresh_admin_data():
    """Background task to refresh admin stats and health."""
    global _ADMIN_STATS, _ADMIN_HEALTH, _LAST_REFRESH
    
    while True:
        try:
            logger.info("admin_cache_refresh_start")
            start_time = time.perf_counter()
            
            # Parallelize Data Fetching
            # 1. DB Stats (Critical)
            async def fetch_db_wrapper():
                try:
                    stats = await asyncio.wait_for(fetch_db_stats(), timeout=5.0)
                    _ADMIN_STATS.update(stats)
                except Exception as e:
                    logger.warning("admin_cache_db_refresh_slow", error=str(e))

            # 2. Storage Stats (Non-Critical, run every 5 mins or if missing)
            async def fetch_storage_wrapper():
                # Only run if cache is empty or stale (> 5 mins)
                last_storage = _ADMIN_STATS.get("storage", {}).get("_updated", 0)
                if time.time() - last_storage < 300:
                    return

                try:
                    usage = await asyncio.wait_for(
                        asyncio.to_thread(storage_service.get_storage_usage),
                        timeout=15.0 # Give it more time since it's parallel
                    )
                    usage["_updated"] = time.time()
                    _ADMIN_STATS["storage"] = usage
                except Exception as e:
                    logger.warning("admin_cache_storage_refresh_slow", error=str(e))

            # 3. Health Diagnostics (Non-Critical)
            async def fetch_health_wrapper():
                try:
                    # External checks (Parallel with strict timeout)
                    from .integration_health import get_integration_health
                    # Only import if needed to avoid circular deps
                    from ..routers.jobs import get_celery_dispatch_diagnostics
                    
                    celery_res, integrations_res = await asyncio.wait_for(
                        asyncio.gather(
                            asyncio.to_thread(get_celery_dispatch_diagnostics, timeout=2.0),
                            asyncio.to_thread(get_integration_health, run_probe=False),
                            return_exceptions=True,
                        ),
                        timeout=5.0,
                    )
                    
                    health = {"timestamp": datetime.utcnow().isoformat()}
                    health["redis"] = celery_res if not isinstance(celery_res, Exception) else {"configured": True, "reachable": False, "error": str(celery_res)}
                    health["integrations"] = integrations_res if not isinstance(integrations_res, Exception) else {"error": str(integrations_res)}
                    
                    # DB health is internal
                    health["db"] = {"reachable": True}
                    health["llm"] = health.get("integrations", {}).get("llm", {}) 
                    
                    global _ADMIN_HEALTH
                    _ADMIN_HEALTH = health
                except Exception as e:
                    logger.warning("admin_cache_health_refresh_slow", error=str(e))

            # Execute all in parallel
            await asyncio.gather(
                fetch_db_wrapper(),
                fetch_storage_wrapper(),
                fetch_health_wrapper(),
                return_exceptions=True
            )

            _LAST_REFRESH = time.time()
            
            duration = time.perf_counter() - start_time
            logger.info("admin_cache_refresh_complete", duration_ms=round(duration*1000, 2))
            
        except Exception as e:
            logger.error("admin_cache_refresh_failed", error=str(e))
            
        # Refresh every 10 seconds (faster UI updates, since storage is decoupled)
        await asyncio.sleep(10)

def get_cached_stats() -> Dict[str, Any]:
    return _ADMIN_STATS

def get_cached_health() -> Dict[str, Any]:
    return _ADMIN_HEALTH

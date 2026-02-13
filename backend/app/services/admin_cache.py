import asyncio
import time
from datetime import datetime, timedelta
from typing import Any, Dict
import structlog
from sqlalchemy import select, func
from ..db import SessionLocal
from ..models import User, Job
from ..services.storage_service import storage_service
from .integration_health import get_integration_health
from ..routers.jobs import get_celery_dispatch_diagnostics

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
            start_time = time.perf_counter()
            
            # 1. DB Stats (Strict timeout to prevent deadlock)
            try:
                # Use wait_for on a local async function to avoid compatibility issues with asyncio.timeout
                async def fetch_db_stats():
                    async with SessionLocal() as session:
                        u_count = (await session.execute(select(func.count(User.id)))).scalar() or 0
                        j_count = (await session.execute(select(func.count(Job.id)))).scalar() or 0
                        
                        one_day_ago = datetime.utcnow() - timedelta(days=1)
                        recent = (await session.execute(
                            select(func.count(Job.id)).where(Job.created_at >= one_day_ago)
                        )).scalar() or 0
                        active = (await session.execute(
                            select(func.count(func.distinct(Job.user_id))).where(Job.created_at >= one_day_ago)
                        )).scalar() or 0

                        start_date = datetime.utcnow().date() - timedelta(days=6)
                        by_day = await session.execute(
                            select(func.date(Job.created_at), func.count(Job.id))
                            .where(Job.created_at >= start_date)
                            .group_by(func.date(Job.created_at))
                            .order_by(func.date(Job.created_at))
                        )
                        return {
                            "users": {"total": u_count, "active_24h": active},
                            "jobs": {"total": j_count, "recent_24h": recent},
                            "trends": {
                                "jobs_by_day": [{"date": str(row[0]), "count": row[1]} for row in by_day.all()],
                            }
                        }

                _ADMIN_STATS.update(await asyncio.wait_for(fetch_db_stats(), timeout=5.0))
            except (asyncio.TimeoutError, Exception) as e:
                logger.warning("admin_cache_db_refresh_slow", error=str(e))

            # 2. Storage Stats (Timeout for sync boto3 call)
            try:
                _ADMIN_STATS["storage"] = await asyncio.wait_for(
                    asyncio.to_thread(storage_service.get_storage_usage),
                    timeout=5.0
                )
            except (asyncio.TimeoutError, Exception) as e:
                logger.warning("admin_cache_storage_refresh_slow", error=str(e))

            # 3. Health Diagnostics
            health = {"timestamp": datetime.utcnow().isoformat()}
            
            # External checks (Parallel with strict timeout)
            try:
                celery_task = asyncio.to_thread(get_celery_dispatch_diagnostics, timeout=2.0)
                integrations_task = asyncio.to_thread(get_integration_health, run_probe=False)
                
                # integrations_res might be a dict or a timeout error
                health["redis"] = celery_res if not isinstance(celery_res, Exception) else {"configured": True, "reachable": False, "error": "timeout"}
                health["integrations"] = integrations_res if not isinstance(integrations_res, Exception) else {"error": "timeout"}
            except (asyncio.TimeoutError, Exception) as e:
                logger.warning("admin_cache_health_refresh_slow", error=str(e))
                health["error"] = "diagnostic_timeout"
            
            # DB health is internal and should be reported even if external checks time out
            health["db"] = {"reachable": True}
            
            _ADMIN_HEALTH = health
            _LAST_REFRESH = time.time()
            
            duration = time.perf_counter() - start_time
            logger.info("admin_cache_refresh_complete", duration_ms=round(duration*1000, 2))
            
        except Exception as e:
            logger.error("admin_cache_refresh_failed", error=str(e))
            
        # Refresh every 30 seconds
        await asyncio.sleep(30)

def get_cached_stats() -> Dict[str, Any]:
    return _ADMIN_STATS

def get_cached_health() -> Dict[str, Any]:
    return _ADMIN_HEALTH

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
            
            # 1. DB Stats
            async with SessionLocal() as session:
                user_count = (await session.execute(select(func.count(User.id)))).scalar() or 0
                job_count = (await session.execute(select(func.count(Job.id)))).scalar() or 0
                
                one_day_ago = datetime.utcnow() - timedelta(days=1)
                recent_jobs = (await session.execute(
                    select(func.count(Job.id)).where(Job.created_at >= one_day_ago)
                )).scalar() or 0
                active_users = (await session.execute(
                    select(func.count(func.distinct(Job.user_id))).where(Job.created_at >= one_day_ago)
                )).scalar() or 0

                start_date = datetime.utcnow().date() - timedelta(days=6)
                jobs_by_day = await session.execute(
                    select(func.date(Job.created_at), func.count(Job.id))
                    .where(Job.created_at >= start_date)
                    .group_by(func.date(Job.created_at))
                    .order_by(func.date(Job.created_at))
                )
                
                _ADMIN_STATS = {
                    "users": {"total": user_count, "active_24h": active_users},
                    "jobs": {"total": job_count, "recent_24h": recent_jobs},
                    "trends": {
                        "jobs_by_day": [{"date": str(row[0]), "count": row[1]} for row in jobs_by_day.all()],
                    }
                }

            # 2. Storage Stats (Async to thread as it's sync Boto3)
            _ADMIN_STATS["storage"] = await asyncio.to_thread(storage_service.get_storage_usage)

            # 3. Health Diagnostics
            health = {"timestamp": datetime.utcnow().isoformat()}
            
            # External checks (Parallel)
            celery_task = asyncio.to_thread(get_celery_dispatch_diagnostics, timeout=1.5)
            integrations_task = asyncio.to_thread(get_integration_health, run_probe=False)
            
            celery_res, integrations_res = await asyncio.gather(
                celery_task, integrations_task, return_exceptions=True
            )
            
            health["celery"] = celery_res if not isinstance(celery_res, Exception) else {"error": "timeout"}
            health["integrations"] = integrations_res if not isinstance(integrations_res, Exception) else {"error": "timeout"}
            health["db"] = {"reachable": True} # If we reached here, DB worked
            
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

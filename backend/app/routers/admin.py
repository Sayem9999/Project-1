from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from pathlib import Path
import time
import asyncio

from ..db import get_session
from ..deps import get_current_user
from ..models import User, Job, CreditLedger
from ..schemas import AdminUserResponse, CreditLedgerResponse
from ..services.storage_service import storage_service
from ..services.llm_health import get_llm_health_summary
from ..services.integration_health import get_integration_health
from ..config import settings
from .jobs import enqueue_job, get_celery_dispatch_diagnostics
from ..tasks.cleanup import get_cleanup_status

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users", response_model=list[AdminUserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    result = await session.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return [
        AdminUserResponse(
            id=user.id,
            email=user.email,
            full_name=user.name,
            avatar_url=user.avatar_url,
            credits=user.credits or 0,
            monthly_credits=user.monthly_credits,
            last_credit_reset=user.last_credit_reset,
            is_admin=bool(user.is_admin),
            oauth_provider=user.oauth_provider,
            created_at=user.created_at
        )
        for user in users
    ]

@router.patch("/users/{user_id}/credits")
async def update_user_credits(
    user_id: int,
    credits: int,
    reason: str = "manual_set",
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin permissions required")
        
    user = await session.get(User, user_id)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    
    previous = user.credits or 0
    user.credits = credits
    delta = user.credits - previous
    session.add(user)
    if delta != 0:
        entry = CreditLedger(
            user_id=user.id,
            delta=delta,
            balance_after=user.credits,
            reason=reason,
            source="admin",
            created_by=current_user.id,
        )
        session.add(entry)
    await session.commit()
    return {"status": "ok", "new_credits": user.credits}


@router.patch("/users/{user_id}/credits/add")
async def add_user_credits(
    user_id: int,
    delta: int,
    reason: str = "manual_adjustment",
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin permissions required")
        
    user = await session.get(User, user_id)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    
    current = user.credits or 0
    new_value = max(0, current + delta)
    actual_delta = new_value - current
    user.credits = new_value
    session.add(user)
    if actual_delta != 0:
        entry = CreditLedger(
            user_id=user.id,
            delta=actual_delta,
            balance_after=user.credits,
            reason=reason,
            source="admin",
            created_by=current_user.id,
        )
        session.add(entry)
    await session.commit()
    return {"status": "ok", "new_credits": user.credits}


@router.get("/credits/ledger", response_model=list[CreditLedgerResponse])
async def list_credit_ledger(
    user_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin permissions required")

    from sqlalchemy.orm import aliased
    created_by = aliased(User)
    stmt = (
        select(CreditLedger, User.email, created_by.email)
        .join(User, CreditLedger.user_id == User.id)
        .outerjoin(created_by, CreditLedger.created_by == created_by.id)
        .order_by(CreditLedger.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    if user_id is not None:
        stmt = stmt.where(CreditLedger.user_id == user_id)

    result = await session.execute(stmt)
    rows = result.all()
    return [
        CreditLedgerResponse(
            id=entry.id,
            user_id=entry.user_id,
            user_email=user_email,
            delta=entry.delta,
            balance_after=entry.balance_after,
            reason=entry.reason,
            source=entry.source,
            job_id=entry.job_id,
            created_by=entry.created_by,
            created_by_email=created_by_email,
            created_at=entry.created_at,
        )
        for entry, user_email, created_by_email in rows
    ]

@router.get("/jobs")
async def list_all_jobs(
    skip: int = 0,
    limit: int = 50,
    user_id: int | None = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin permissions required")
        
    stmt = select(Job).order_by(Job.created_at.desc()).offset(skip).limit(limit)
    if user_id is not None:
        stmt = stmt.where(Job.user_id == user_id)
    result = await session.execute(stmt)
    jobs = result.scalars().all()
    return jobs


@router.get("/users/{user_id}/jobs")
async def list_user_jobs(
    user_id: int,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin permissions required")
    result = await session.execute(
        select(Job)
        .where(Job.user_id == user_id)
        .order_by(Job.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.post("/jobs/{job_id}/cancel")
async def admin_cancel_job(
    job_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin permissions required")
    job = await session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status == "complete":
        raise HTTPException(status_code=400, detail="Completed jobs cannot be canceled.")
    job.cancel_requested = True
    job.status = "failed"
    job.progress_message = "Canceled by admin."
    session.add(job)
    await session.commit()
    return {"status": "ok", "job_id": job.id}


@router.post("/jobs/{job_id}/retry")
async def admin_retry_job(
    job_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin permissions required")
    job = await session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status not in ["failed"]:
        raise HTTPException(status_code=400, detail="Only failed jobs can be retried.")
    if settings.credits_enabled:
        # Lock user row for update
        result = await session.execute(select(User).where(User.id == job.user_id).with_for_update())
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        cost = job.credits_cost or (2 if (job.tier or "standard") == "pro" else 1)
        if (user.credits or 0) < cost:
            raise HTTPException(status_code=403, detail="User has insufficient credits.")
        user.credits = (user.credits or 0) - cost
        session.add(user)
        session.add(
            CreditLedger(
                user_id=user.id,
                job_id=job.id,
                delta=-cost,
                balance_after=user.credits or 0,
                reason=f"{job.tier}_job_retry",
                source="job",
                created_by=current_user.id,
            )
        )
    job.cancel_requested = False
    job.status = "processing"
    job.progress_message = "Retrying pipeline..."
    job.output_path = None
    job.thumbnail_path = None
    session.add(job)
    await session.commit()
    await enqueue_job(
        job,
        job.pacing or "medium",
        job.mood or "professional",
        job.ratio or "16:9",
        job.tier or "standard",
        job.platform or "youtube",
        job.brand_safety or "standard",
    )
    return {"status": "ok", "job_id": job.id}


@router.post("/jobs/{job_id}/force-retry")
async def admin_force_retry_job(
    job_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin permissions required")
    job = await session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status == "complete":
        raise HTTPException(status_code=400, detail="Completed jobs cannot be retried.")
    if job.source_path and not str(job.source_path).startswith("http"):
        if not Path(job.source_path).exists():
            raise HTTPException(status_code=400, detail="Source file is no longer available.")

    job.cancel_requested = False
    job.status = "processing"
    job.progress_message = "Force retry by admin."
    job.output_path = None
    job.thumbnail_path = None
    session.add(job)
    await session.commit()
    await enqueue_job(
        job,
        job.pacing or "medium",
        job.mood or "professional",
        job.ratio or "16:9",
        job.tier or "standard",
        job.platform or "youtube",
        job.brand_safety or "standard",
    )
    return {"status": "ok", "job_id": job.id, "forced": True}

# --- Admin Dashboard Caching ---
_STATS_CACHE = None
_STATS_CACHE_TIME = 0.0
_HEALTH_CACHE = None
_HEALTH_CACHE_TIME = 0.0

@router.get("/stats")
async def get_admin_stats(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin permissions required")

    # 1-minute global cache for stats to prevent rapid-fire DB pressure
    global _STATS_CACHE, _STATS_CACHE_TIME
    now = time.time()
    if _STATS_CACHE and (now - _STATS_CACHE_TIME < 60):
        return _STATS_CACHE

    try:
        # Wrap the whole stats collection in a 10s timeout to prevent API hangs
        async def fetch_stats():
            # Total counts are fast with indices
            user_count = (await session.execute(select(func.count(User.id)))).scalar() or 0
            job_count = (await session.execute(select(func.count(Job.id)))).scalar() or 0
            
            one_day_ago = datetime.utcnow() - timedelta(days=1)
            recent_jobs = (await session.execute(
                select(func.count(Job.id)).where(Job.created_at >= one_day_ago)
            )).scalar() or 0
            active_users = (await session.execute(
                select(func.count(func.distinct(Job.user_id))).where(Job.created_at >= one_day_ago)
            )).scalar() or 0

            # Trend data (last 7 days)
            start_date = datetime.utcnow().date() - timedelta(days=6)
            
            jobs_by_day = await session.execute(
                select(func.date(Job.created_at), func.count(Job.id))
                .where(Job.created_at >= start_date)
                .group_by(func.date(Job.created_at))
                .order_by(func.date(Job.created_at))
            )
            
            # Storage is cached inside storage_service, so this should be fast
            storage_stats = await asyncio.to_thread(storage_service.get_storage_usage)
            
            return {
                "users": {"total": user_count, "active_24h": active_users},
                "jobs": {"total": job_count, "recent_24h": recent_jobs},
                "storage": storage_stats,
                "trends": {
                    "jobs_by_day": [{"date": str(row[0]), "count": row[1]} for row in jobs_by_day.all()],
                }
            }

        stats = await asyncio.wait_for(fetch_stats(), timeout=10.0)
        _STATS_CACHE = stats
        _STATS_CACHE_TIME = now
        return stats
        
    except asyncio.TimeoutError:
        # If DB is truly locked or slow, return cached or partial data
        if _STATS_CACHE: return _STATS_CACHE
        return {"error": "Stats timeout", "status": "degraded"}
    except Exception as e:
        print(f"[Admin] Stats Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stats")


@router.get("/health")
async def get_admin_health(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin permissions required")

    # 30-second global cache for health status
    global _HEALTH_CACHE, _HEALTH_CACHE_TIME
    now = time.time()
    if _HEALTH_CACHE and (now - _HEALTH_CACHE_TIME < 30):
        return _HEALTH_CACHE

    health: dict = {"timestamp": datetime.utcnow().isoformat()}

    async def check_health():
        # DB health (fail fast)
        try:
            await asyncio.wait_for(session.execute(select(1)), timeout=2.0)
            health["db"] = {"reachable": True}
        except:
            health["db"] = {"reachable": False}

        # Parallelize heavy external checks
        celery_task = asyncio.to_thread(get_celery_dispatch_diagnostics, timeout=1.0)
        storage_task = asyncio.to_thread(storage_service.get_storage_usage)
        integrations_task = asyncio.to_thread(get_integration_health, run_probe=False)
        
        celery_res, storage_res, integrations_res = await asyncio.gather(
            celery_task, storage_task, integrations_task, return_exceptions=True
        )

        health["celery"] = celery_res if not isinstance(celery_res, Exception) else {"error": "timeout"}
        health["storage"] = storage_res if not isinstance(storage_res, Exception) else {"error": "lookup failed"}
        health["integrations"] = integrations_res if not isinstance(integrations_res, Exception) else {"error": "lookup failed"}
        health["llm"] = get_llm_health_summary()
        health["cleanup"] = get_cleanup_status()
        return health

    try:
        results = await asyncio.wait_for(check_health(), timeout=12.0)
        _HEALTH_CACHE = results
        _HEALTH_CACHE_TIME = now
        return results
    except asyncio.TimeoutError:
        return {"status": "degraded", "error": "Health check timed out"}


@router.get("/integrations/health")
async def get_admin_integrations_health(
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin permissions required")
    return get_integration_health(run_probe=True)

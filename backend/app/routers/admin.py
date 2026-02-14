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
from ..services.cleanup_service import cleanup_service

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

from ..services.admin_cache import get_cached_stats, get_cached_health

@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin permissions required")

    return get_cached_stats()


@router.get("/health")
async def get_admin_health(
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin permissions required")

    return get_cached_health()


@router.get("/integrations/health")
async def get_admin_integrations_health(
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin permissions required")
    return get_integration_health(run_probe=True)


@router.get("/performance")
async def get_performance_analytics(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    # Simple aggregation of the last 100 jobs with performance_metrics
    stmt = (
        select(Job.performance_metrics)
        .where(Job.performance_metrics != None)
        .order_by(Job.created_at.desc())
        .limit(100)
    )
    result = await session.execute(stmt)
    metrics_list = result.scalars().all()
    
    if not metrics_list:
        return {"avg_latency_ms": 0, "total_jobs_tracked": 0, "phase_averages_ms": {}, "tier_distribution": {}}

    total_latency = 0
    phase_totals = {}
    phase_counts = {}

    for m in metrics_list:
        total_latency += m.get("total_duration_ms", 0)
        phases = m.get("phase_durations", {})
        for phase, dur in phases.items():
            phase_totals[phase] = phase_totals.get(phase, 0) + dur
            phase_counts[phase] = phase_counts.get(phase, 0) + 1

    avg_phases = {p: round(phase_totals[p] / phase_counts[p], 2) for p in phase_totals}
    
    # NEW: Tier Distribution
    tier_counts = {"pro": 0, "standard": 0}
    
    # We need to fetch the tiers for these jobs. 
    # Since we have the metrics, let's just count from the Job table for recent jobs as a proxy
    # or better, fetch jobs that have these metrics.
    stmt_tier = select(Job.tier, func.count(Job.id)).where(Job.performance_metrics != None).group_by(Job.tier)
    tier_res = await session.execute(stmt_tier)
    for t_name, t_count in tier_res.all():
        tier_counts[t_name] = t_count

    return {
        "avg_latency_ms": round(total_latency / len(metrics_list), 2),
        "total_jobs_tracked": len(metrics_list),
        "phase_averages_ms": avg_phases,
        "tier_distribution": tier_counts,
        "efficiency_score": 98.4 # Placeholder for future health score
    }


@router.post("/cleanup")
async def trigger_storage_cleanup(
    max_age_hours: int = 6,
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    freed = await cleanup_service.run_cleanup(max_age_hours=max_age_hours)
    return {"status": "ok", "bytes_freed": freed, "mb_freed": round(freed / (1024*1024), 2)}

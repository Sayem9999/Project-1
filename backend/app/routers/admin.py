from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import time

from ..db import get_session
from ..deps import get_current_user
from ..models import User, Job, CreditLedger
from ..schemas import AdminUserResponse, CreditLedgerResponse
from ..services.storage_service import storage_service
from ..services.llm_health import get_llm_health_summary
from ..config import settings

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
        from fastapi import HTTPException
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
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin permissions required")
        
    result = await session.execute(select(Job).order_by(Job.created_at.desc()).offset(skip).limit(limit))
    jobs = result.scalars().all()
    return jobs

@router.get("/stats")
async def get_admin_stats(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin permissions required")

    # Total Users
    user_count = (await session.execute(select(func.count(User.id)))).scalar() or 0
    
    # Total Jobs
    job_count = (await session.execute(select(func.count(Job.id)))).scalar() or 0
    
    # Jobs in last 24h
    one_day_ago = datetime.utcnow() - timedelta(days=1)
    recent_jobs = (await session.execute(
        select(func.count(Job.id)).where(Job.created_at >= one_day_ago)
    )).scalar() or 0
    
    # Storage Stats
    storage_stats = storage_service.get_storage_usage()
    
    return {
        "users": {
            "total": user_count
        },
        "jobs": {
            "total": job_count,
            "recent_24h": recent_jobs
        },
        "storage": storage_stats
    }


@router.get("/health")
async def get_admin_health(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin permissions required")

    health: dict = {}

    # DB health
    try:
        await session.execute(select(1))
        health["db"] = {"reachable": True}
    except Exception as e:
        health["db"] = {"reachable": False, "error": str(e)}

    # Redis health
    if settings.redis_url:
        try:
            import redis.asyncio as redis  # type: ignore
            start = time.perf_counter()
            client = redis.from_url(settings.redis_url, decode_responses=True)
            pong = await client.ping()
            await client.close()
            latency_ms = int((time.perf_counter() - start) * 1000)
            health["redis"] = {"configured": True, "reachable": bool(pong), "latency_ms": latency_ms}
        except Exception as e:
            health["redis"] = {"configured": True, "reachable": False, "error": str(e)}
    else:
        health["redis"] = {"configured": False, "reachable": False}

    # LLM health
    health["llm"] = get_llm_health_summary()

    # Storage
    health["storage"] = storage_service.get_storage_usage()

    return health

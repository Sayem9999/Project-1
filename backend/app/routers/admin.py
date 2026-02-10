from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from ..db import get_session
from ..deps import get_current_user
from ..models import User, Job
from ..schemas import AdminUserResponse
from ..services.storage_service import storage_service

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
    
    user.credits = credits
    await session.commit()
    return {"status": "ok", "new_credits": user.credits}

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

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from ..db import get_session
from ..deps import get_current_user
from ..models import User, Job
from ..services.storage_service import storage_service

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/stats")
async def get_admin_stats(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
):
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
    # Note: This might be slow if there are many files in S3 and we list them all.
    # In production, this should be cached or fetched from a separate metrics service.
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

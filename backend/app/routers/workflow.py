from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from ..models import Job
from ..schemas import N8NCallbackRequest

router = APIRouter(prefix="/workflow", tags=["workflow"])


@router.post("/n8n/callback/{job_id}")
async def n8n_callback(job_id: int, payload: N8NCallbackRequest, session: AsyncSession = Depends(get_session)):
    job = await session.scalar(select(Job).where(Job.id == job_id))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = payload.status
    job.progress_message = payload.progress_message
    if payload.output_path:
        job.output_path = payload.output_path
    await session.commit()
    return {"ok": True}

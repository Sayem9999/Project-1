from pathlib import Path
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from ..deps import get_current_user
from ..models import Job, User
from ..schemas import JobResponse
from ..services.storage import storage_service
from ..services.n8n_client import trigger_edit_workflow

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/upload", response_model=JobResponse)
async def upload_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    source_path = await storage_service.save_upload(file)
    job = Job(user_id=current_user.id, source_path=source_path)
    session.add(job)
    await session.commit()
    await session.refresh(job)
    await trigger_edit_workflow(job.id, job.source_path)
    return JobResponse.model_validate(job, from_attributes=True)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    job = await session.scalar(select(Job).where(Job.id == job_id, Job.user_id == current_user.id))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse.model_validate(job, from_attributes=True)


@router.get("/{job_id}/download")
async def download_output(job_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    job = await session.scalar(select(Job).where(Job.id == job_id, Job.user_id == current_user.id))
    if not job or not job.output_path:
        raise HTTPException(status_code=404, detail="Rendered file unavailable")
    file_path = Path(job.output_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Rendered file missing")
    return FileResponse(path=file_path, filename=file_path.name, media_type="video/mp4")

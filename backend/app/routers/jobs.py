from pathlib import Path
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from ..deps import get_current_user
from ..models import Job, User
from ..schemas import JobResponse
from ..services.storage import storage_service
from ..services.storage_service import storage_service as r2_storage


router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/upload", response_model=JobResponse)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    theme: str = Form("professional"),
    pacing: str = Form("medium"),
    mood: str = Form("professional"),
    ratio: str = Form("16:9"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # Check file size before accepting (100MB limit)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to start
    
    if file_size > 100 * 1024 * 1024:  # 100 MB
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 100MB.")
    
    source_path = await storage_service.save_upload(file)
    
    job = Job(user_id=current_user.id, source_path=source_path, theme=theme)
    session.add(job)
    await session.commit()
    await session.refresh(job)
    
    from ..services.workflow_engine import process_job
    background_tasks.add_task(process_job, job.id, job.source_path, pacing, mood, ratio)
    
    return JobResponse.model_validate(job, from_attributes=True)


@router.get("/storage/usage")
async def get_storage_usage(current_user: User = Depends(get_current_user)):
    """Get current R2 storage usage (admin info)."""
    return r2_storage.get_storage_usage()


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
    
    # If output_path is a URL (R2), redirect to it
    if job.output_path.startswith("http"):
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=job.output_path)
    
    # Local file
    file_path = Path(job.output_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Rendered file missing")
    return FileResponse(path=file_path, filename=file_path.name, media_type="video/mp4")

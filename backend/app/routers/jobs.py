import os
from pathlib import Path
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form, Request
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from ..errors import CreditError, NotFoundError
from ..config import settings
from ..deps import get_current_user
from ..models import Job, User, CreditLedger
from ..schemas import JobResponse, EditJobRequest
from ..services.storage import storage_service
from ..services.storage_service import storage_service as r2_storage


router = APIRouter(prefix="/jobs", tags=["jobs"])

# Check if Celery/Redis is available (handle empty or invalid URLs)
_REDIS_URL = os.getenv("REDIS_URL", "")
USE_CELERY = _REDIS_URL.startswith("redis://") or _REDIS_URL.startswith("rediss://")


@router.post("/upload", response_model=JobResponse)
async def upload_video(
    request: Request,
    file: UploadFile = File(...),
    theme: str = Form("professional"),
    pacing: str = Form("medium"),
    mood: str = Form("professional"),
    ratio: str = Form("16:9"),
    platform: str = Form("youtube"),
    tier: str = Form("pro"),
    brand_safety: str = Form("standard"),
    media_intelligence: str = Form(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Upload video and enqueue for processing."""
    # Check file size (100MB limit)
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > 100 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 100MB.")

    idempotency_key = request.headers.get("Idempotency-Key")
    if idempotency_key:
        existing = await session.scalar(
            select(Job).where(
                Job.user_id == current_user.id,
                Job.idempotency_key == idempotency_key
            )
        )
        if existing:
            return JobResponse.model_validate(existing, from_attributes=True)

    source_path = await storage_service.save_upload(file)

    # Parse media intelligence if provided
    parsed_intel = None
    if media_intelligence:
        try:
            import json
            parsed_intel = json.loads(media_intelligence)
        except:
            pass

    job = await create_job(
        session=session,
        current_user=current_user,
        source_path=source_path,
        theme=theme,
        tier=tier,
        pacing=pacing,
        mood=mood,
        ratio=ratio,
        platform=platform,
        brand_safety=brand_safety,
        idempotency_key=idempotency_key,
        media_intelligence=parsed_intel,
        start_immediately=False,
    )
    await session.refresh(job)
    
    return JobResponse.model_validate(job, from_attributes=True)


@router.get("", response_model=list[JobResponse])
async def list_jobs(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """List all jobs for current user."""
    result = await session.execute(
        select(Job).where(Job.user_id == current_user.id).order_by(Job.created_at.desc()).offset(skip).limit(limit)
    )
    jobs = result.scalars().all()
    return [JobResponse.model_validate(job, from_attributes=True) for job in jobs]


@router.get("/storage/usage")
async def get_storage_usage(current_user: User = Depends(get_current_user)):
    """Get current R2 storage usage."""
    return r2_storage.get_storage_usage()


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    job = await session.scalar(select(Job).where(Job.id == job_id, Job.user_id == current_user.id))
    if not job:
        raise NotFoundError("Job not found")
    return JobResponse.model_validate(job, from_attributes=True)


@router.post("/{job_id}/cancel")
async def cancel_job(job_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    job = await session.scalar(select(Job).where(Job.id == job_id, Job.user_id == current_user.id))
    if not job:
        raise NotFoundError("Job not found")
    if job.status in ["complete"]:
        raise HTTPException(status_code=400, detail="Completed jobs cannot be canceled.")
    job.cancel_requested = True
    job.status = "failed"
    job.progress_message = "Canceled by user."
    session.add(job)
    await session.commit()
    return {"status": "ok", "job_id": job.id}


@router.post("/{job_id}/retry")
async def retry_job(job_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    job = await session.scalar(select(Job).where(Job.id == job_id, Job.user_id == current_user.id))
    if not job:
        raise NotFoundError("Job not found")
    if job.status not in ["failed"]:
        raise HTTPException(status_code=400, detail="Only failed jobs can be retried.")

    if settings.credits_enabled:
        # Lock user row for update to prevent race conditions
        result = await session.execute(select(User).where(User.id == current_user.id).with_for_update())
        user_to_charge = result.scalar_one()
        
        cost = job.credits_cost or (2 if (job.tier or "standard") == "pro" else 1)
        if (user_to_charge.credits or 0) < cost:
            raise CreditError(f"Insufficient credits. {job.tier.title()} edit requires {cost} credits.")
        
        user_to_charge.credits = (user_to_charge.credits or 0) - cost
        session.add(user_to_charge)
        session.add(
            CreditLedger(
                user_id=user_to_charge.id,
                job_id=job.id,
                delta=-cost,
                balance_after=user_to_charge.credits or 0,
                reason=f"{job.tier}_job_retry",
                source="job",
            )
        )

    job.cancel_requested = False
    job.status = "processing"
    job.progress_message = "Retrying pipeline..."
    job.output_path = None
    job.thumbnail_path = None
    session.add(job)
    try:
        await enqueue_job(
            job,
            job.pacing or "medium",
            job.mood or "professional",
            job.ratio or "16:9",
            job.tier or "standard",
            job.platform or "youtube",
            job.brand_safety or "standard",
        )
    except HTTPException:
        await session.rollback()
        raise
    await session.commit()
    return {"status": "ok", "job_id": job.id}


@router.post("/{job_id}/start")
async def start_job(job_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    job = await session.scalar(select(Job).where(Job.id == job_id, Job.user_id == current_user.id))
    if not job:
        raise NotFoundError("Job not found")
    if job.status != "queued":
        raise HTTPException(status_code=400, detail="Job is already started.")
    if job.source_path and not str(job.source_path).startswith("http"):
        if not Path(job.source_path).exists():
            raise HTTPException(status_code=400, detail="Source file is no longer available.")

    # Charge credits on start
    if settings.credits_enabled:
        # Lock user row for update
        result = await session.execute(select(User).where(User.id == current_user.id).with_for_update())
        user_to_charge = result.scalar_one()

        cost = job.credits_cost or (2 if (job.tier or "standard") == "pro" else 1)
        if (user_to_charge.credits or 0) < cost:
            raise CreditError(f"Insufficient credits. {job.tier.title()} edit requires {cost} credits.")
        
        user_to_charge.credits = (user_to_charge.credits or 0) - cost
        session.add(user_to_charge)
        session.add(
            CreditLedger(
                user_id=user_to_charge.id,
                job_id=job.id,
                delta=-cost,
                balance_after=user_to_charge.credits or 0,
                reason=f"{job.tier}_job_start",
                source="job",
            )
        )

    job.status = "processing"
    job.progress_message = "Starting pipeline..."
    job.cancel_requested = False
    session.add(job)
    try:
        await enqueue_job(
            job,
            job.pacing or "medium",
            job.mood or "professional",
            job.ratio or "16:9",
            job.tier or "standard",
            job.platform or "youtube",
            job.brand_safety or "standard",
        )
    except HTTPException:
        await session.rollback()
        raise
    await session.commit()
    return {"status": "ok", "job_id": job.id}


@router.post("/{job_id}/edit", response_model=JobResponse)
async def edit_job(
    job_id: int,
    request: Request,
    payload: EditJobRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    job = await session.scalar(select(Job).where(Job.id == job_id, Job.user_id == current_user.id))
    if not job:
        raise NotFoundError("Job not found")

    source_path = job.source_path
    if source_path and not str(source_path).startswith("http"):
        if not Path(source_path).exists():
            raise HTTPException(status_code=400, detail="Source file is no longer available.")

    idempotency_key = request.headers.get("Idempotency-Key")
    if idempotency_key:
        existing = await session.scalar(
            select(Job).where(
                Job.user_id == current_user.id,
                Job.idempotency_key == idempotency_key
            )
        )
        if existing:
            return JobResponse.model_validate(existing, from_attributes=True)

    new_job = await create_job(
        session=session,
        current_user=current_user,
        source_path=source_path,
        theme=payload.theme,
        tier=payload.tier,
        pacing=payload.pacing,
        mood=payload.mood,
        ratio=payload.ratio,
        platform=payload.platform,
        brand_safety=payload.brand_safety,
        idempotency_key=idempotency_key,
        start_immediately=False,
    )
    await session.refresh(new_job)
    return JobResponse.model_validate(new_job, from_attributes=True)


@router.get("/{job_id}/download")
async def download_output(job_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    job = await session.scalar(select(Job).where(Job.id == job_id, Job.user_id == current_user.id))
    if not job or not job.output_path:
        raise NotFoundError("Rendered file unavailable")
    
    # R2 URL redirect
    if job.output_path.startswith("http"):
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=job.output_path)
    
    # Local file
    file_path = Path(job.output_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Rendered file missing")
    return FileResponse(path=file_path, filename=file_path.name, media_type="video/mp4")


async def enqueue_job(
    job: Job,
    pacing: str,
    mood: str,
    ratio: str,
    tier: str,
    platform: str,
    brand_safety: str,
) -> None:
    if settings.environment == "production" and not USE_CELERY:
        raise HTTPException(
            status_code=503,
            detail="Queue dispatch unavailable. Configure REDIS_URL and a running Celery worker.",
        )

    if USE_CELERY:
        try:
            from ..tasks.video_tasks import process_video_task
            process_video_task.delay(job.id, job.source_path, pacing, mood, ratio, tier, platform, brand_safety)
            return
        except Exception as e:
            if settings.environment == "production":
                raise HTTPException(
                    status_code=503,
                    detail="Queue dispatch failed. Check Redis connectivity and worker health.",
                ) from e
            print(f"[Job] Celery dispatch failed: {e}. Falling back to inline.")
    from ..services.workflow_engine import process_job
    import asyncio
    asyncio.create_task(process_job(job.id, job.source_path, pacing, mood, ratio, tier, platform, brand_safety))


async def create_job(
    session: AsyncSession,
    current_user: User,
    source_path: str,
    theme: str,
    tier: str,
    pacing: str,
    mood: str,
    ratio: str,
    platform: str,
    brand_safety: str,
    idempotency_key: str | None = None,
    media_intelligence: dict | None = None,
    start_immediately: bool = True,
) -> Job:
    COST_PER_JOB = 2 if tier == "pro" else 1
    job = Job(
        user_id=current_user.id,
        source_path=source_path,
        theme=theme,
        tier=tier,
        credits_cost=COST_PER_JOB,
        idempotency_key=idempotency_key,
        pacing=pacing,
        mood=mood,
        ratio=ratio,
        platform=platform,
        brand_safety=brand_safety,
        media_intelligence=media_intelligence,
        cancel_requested=False,
        progress_message="Starting pipeline..." if start_immediately else "Awaiting manual start.",
    )
    session.add(job)
    await session.flush()

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        if idempotency_key:
            existing = await session.scalar(
                select(Job).where(
                    Job.user_id == current_user.id,
                    Job.idempotency_key == idempotency_key
                )
            )
            if existing:
                return existing
        raise
    return job

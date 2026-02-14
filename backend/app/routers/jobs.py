import asyncio
import os
from pathlib import Path
from urllib.parse import urlparse
from typing import Any
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form, Request
import asyncio
import structlog
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import SessionLocal, get_session
from ..errors import CreditError, NotFoundError
from ..config import settings
from ..deps import get_current_user
from ..models import Job, User, CreditLedger
from ..schemas import JobResponse, EditJobRequest
from ..services.storage import storage_service
from ..services.storage_service import storage_service as r2_storage


router = APIRouter(prefix="/jobs", tags=["jobs"])
logger = structlog.get_logger()

# Check if Celery/Redis is available
_REDIS_URL = settings.redis_url or ""
USE_CELERY = _REDIS_URL.startswith("redis://") or _REDIS_URL.startswith("rediss://")
ALLOWED_TRANSITION_STYLES = {"cut", "dissolve", "wipe", "crossfade", "wipe_left", "wipe_right", "slide_left", "slide_right"}
ALLOWED_SPEED_PROFILES = {"slow", "balanced", "fast"}
ALLOWED_SUBTITLE_PRESETS = {"platform_default", "broadcast", "social"}
ALLOWED_COLOR_PROFILES = {"natural", "cinematic", "punchy"}


def _broker_fingerprint(redis_url: str) -> str:
    """Return a sanitized broker fingerprint without credentials."""
    url = (redis_url or "").strip().strip('"').strip("'")
    if not url:
        return "unset"
    parsed = urlparse(url)
    if not parsed.scheme:
        return "invalid"
    host = parsed.hostname or "unknown"
    port = parsed.port or 6379
    db_name = parsed.path.lstrip("/") or "0"
    return f"{parsed.scheme}://{host}:{port}/{db_name}"


def get_celery_dispatch_diagnostics(timeout: float = 1.5) -> dict[str, Any]:
    """Inspect current broker/worker visibility from the API process."""
    target_queue = (settings.celery_video_queue or "video").strip() or "video"
    diagnostics: dict[str, Any] = {
        "use_celery": USE_CELERY,
        "configured": USE_CELERY,
        "reachable": False,
        "broker": _broker_fingerprint(_REDIS_URL),
        "expected_queue": target_queue,
        "worker_count": 0,
        "workers": [],
        "queues": {},
        "error": None,
    }
    if not USE_CELERY:
        return diagnostics

    try:
        from ..celery_app import celery_app
        
        # Stricter timeout for control inspection to avoid blocking threads.
        # inspect().ping() and active_queues() are network-bound calls to other workers.
        inspect = celery_app.control.inspect(timeout=0.5)
        
        # Ping check
        try:
            ping = inspect.ping() or {}
        except Exception as e:
            logger.warning("celery_inspect_ping_failed", error=str(e))
            ping = {}

        # Queue check
        try:
            active_queues = inspect.active_queues() or {}
        except Exception as e:
            logger.warning("celery_inspect_queues_failed", error=str(e))
            active_queues = {}

        worker_names = sorted(set(list(ping.keys()) + list(active_queues.keys())))
        diagnostics["workers"] = worker_names
        diagnostics["worker_count"] = len(worker_names)
        diagnostics["reachable"] = len(worker_names) > 0
        diagnostics["queues"] = {
            worker: [q.get("name") for q in active_queues.get(worker, [])]
            for worker in worker_names
        }
    except Exception as exc:
        diagnostics["error"] = str(exc)
    return diagnostics


def _has_queue_consumer(diagnostics: dict[str, Any], queue_name: str) -> bool:
    """Return True if any discovered worker is subscribed to queue_name."""
    queues_by_worker = diagnostics.get("queues") or {}
    for queue_list in queues_by_worker.values():
        if isinstance(queue_list, list) and queue_name in queue_list:
            return True
    return False


async def _dispatch_job_background(
    job_id: int,
    pacing: str,
    mood: str,
    ratio: str,
    tier: str,
    platform: str,
    brand_safety: str,
) -> None:
    """Detach queue dispatch from request lifecycle so /start never hangs.

    This is intentionally defensive: any dispatch error is recorded on the job row
    so the UI/client can surface it, rather than timing out the HTTP request.
    """
    async with SessionLocal() as session:
        job = await session.get(Job, job_id)
        if not job:
            return
        try:
            await enqueue_job(
                job,
                pacing=pacing,
                mood=mood,
                ratio=ratio,
                tier=tier,
                platform=platform,
                brand_safety=brand_safety,
            )
        except HTTPException as exc:
            job.status = "failed"
            job.progress_message = f"Dispatch failed: {exc.detail}"
            session.add(job)
            await session.commit()
            logger.warning(
                "job_dispatch_failed_http",
                job_id=job_id,
                status_code=exc.status_code,
                detail=str(exc.detail),
            )
            return
        except Exception as exc:
            job.status = "failed"
            job.progress_message = "Dispatch failed due to unexpected error."
            session.add(job)
            await session.commit()
            logger.exception("job_dispatch_failed_unhandled", job_id=job_id, error=str(exc))
            return

        # Persist any progress_message changes made during enqueue_job().
        session.add(job)
        await session.commit()


def _parse_bounded_float(value: Any, default: float, minimum: float, maximum: float) -> float:
    try:
        parsed = float(value)
    except Exception:
        parsed = default
    return min(max(parsed, minimum), maximum)


def _normalize_post_settings(
    transition_style: Any,
    transition_duration: Any,
    speed_profile: Any,
    subtitle_preset: Any,
    color_profile: Any,
    skin_protect_strength: Any,
) -> dict[str, Any]:
    transition_style_norm = str(transition_style or "dissolve").lower()
    if transition_style_norm not in ALLOWED_TRANSITION_STYLES:
        transition_style_norm = "dissolve"

    speed_profile_norm = str(speed_profile or "balanced").lower()
    if speed_profile_norm not in ALLOWED_SPEED_PROFILES:
        speed_profile_norm = "balanced"

    subtitle_preset_norm = str(subtitle_preset or "platform_default").lower()
    if subtitle_preset_norm not in ALLOWED_SUBTITLE_PRESETS:
        subtitle_preset_norm = "platform_default"

    color_profile_norm = str(color_profile or "natural").lower()
    if color_profile_norm not in ALLOWED_COLOR_PROFILES:
        color_profile_norm = "natural"

    return {
        "transition_style": transition_style_norm,
        "transition_duration": _parse_bounded_float(transition_duration, 0.25, 0.1, 1.5),
        "speed_profile": speed_profile_norm,
        "subtitle_preset": subtitle_preset_norm,
        "color_profile": color_profile_norm,
        "skin_protect_strength": _parse_bounded_float(skin_protect_strength, 0.5, 0.0, 1.0),
    }


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
    transition_style: str = Form("dissolve"),
    transition_duration: float = Form(0.25),
    speed_profile: str = Form("balanced"),
    subtitle_preset: str = Form("platform_default"),
    color_profile: str = Form("natural"),
    skin_protect_strength: float = Form(0.5),
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
        post_settings=_normalize_post_settings(
            transition_style=transition_style,
            transition_duration=transition_duration,
            speed_profile=speed_profile,
            subtitle_preset=subtitle_preset,
            color_profile=color_profile,
            skin_protect_strength=skin_protect_strength,
        ),
        idempotency_key=idempotency_key,
        media_intelligence=parsed_intel,
        start_immediately=True,
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
    await session.commit()
    pacing = job.pacing or "medium"
    mood = job.mood or "professional"
    ratio = job.ratio or "16:9"
    tier = job.tier or "standard"
    platform = job.platform or "youtube"
    brand_safety = job.brand_safety or "standard"

    # Best-effort quick dispatch in-request (bounded). If dispatch is slow/unavailable,
    # fall back to detached dispatch so the HTTP request never hangs indefinitely.
    try:
        await asyncio.wait_for(
            enqueue_job(job, pacing, mood, ratio, tier, platform, brand_safety),
            timeout=2.5,
        )
        session.add(job)
        await session.commit()
    except asyncio.TimeoutError:
        logger.warning("job_dispatch_timeout_retry", job_id=job.id)
        asyncio.create_task(_dispatch_job_background(job.id, pacing, mood, ratio, tier, platform, brand_safety))
    except HTTPException as exc:
        job.status = "failed"
        job.progress_message = f"Dispatch failed: {exc.detail}"
        session.add(job)
        await session.commit()
    return {"status": "ok", "job_id": job.id}


@router.post("/{job_id}/start")
async def start_job(job_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    logger.info("start_job_called", job_id=job_id, user_id=current_user.id)
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
        logger.info("lock_user_acquired")
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
    job.progress_message = "Dispatching job to pipeline..."
    job.cancel_requested = False
    session.add(job)
    await session.commit()
    pacing = job.pacing or "medium"
    mood = job.mood or "professional"
    ratio = job.ratio or "16:9"
    tier = job.tier or "standard"
    platform = job.platform or "youtube"
    brand_safety = job.brand_safety or "standard"

    # Best-effort quick dispatch in-request (bounded). If dispatch is slow/unavailable,
    # fall back to detached dispatch so the HTTP request never hangs indefinitely.
    try:
        await asyncio.wait_for(
            enqueue_job(job, pacing, mood, ratio, tier, platform, brand_safety),
            timeout=2.5,
        )
        session.add(job)
        await session.commit()
    except asyncio.TimeoutError:
        logger.warning("job_dispatch_timeout_start", job_id=job.id)
        asyncio.create_task(_dispatch_job_background(job.id, pacing, mood, ratio, tier, platform, brand_safety))
    except HTTPException as exc:
        job.status = "failed"
        job.progress_message = f"Dispatch failed: {exc.detail}"
        session.add(job)
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
        post_settings=_normalize_post_settings(
            transition_style=payload.transition_style,
            transition_duration=payload.transition_duration,
            speed_profile=payload.speed_profile,
            subtitle_preset=payload.subtitle_preset,
            color_profile=payload.color_profile,
            skin_protect_strength=payload.skin_protect_strength,
        ),
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
    queue_name = (settings.celery_video_queue or "video").strip() or "video"
    health_queue_name = "video"
    if settings.environment == "production" and not USE_CELERY:
        raise HTTPException(
            status_code=503,
            detail="Queue dispatch unavailable. Configure REDIS_URL and a running Celery worker.",
        )

    if settings.environment == "production" and USE_CELERY:
        diagnostics = get_celery_dispatch_diagnostics()
        if diagnostics.get("worker_count", 0) < 1:
            raise HTTPException(
                status_code=503,
                detail="No active Celery worker reachable",
            )
        has_configured_queue = _has_queue_consumer(diagnostics, queue_name)
        has_default_video_queue = _has_queue_consumer(diagnostics, health_queue_name)
        if not (has_configured_queue or has_default_video_queue):
            raise HTTPException(
                status_code=503,
                detail=f"No active Celery worker subscribed to '{health_queue_name}' queue",
            )

    if USE_CELERY:
        try:
            from ..tasks.video_tasks import process_video_task
            
            # Using asyncio.to_thread to prevent blocking the event loop
            try:
                task = await asyncio.wait_for(
                    asyncio.to_thread(
                        process_video_task.apply_async,
                        args=[job.id, job.source_path, pacing, mood, ratio, tier, platform, brand_safety],
                        queue=queue_name,
                    ),
                    timeout=2.0,
                )
            except asyncio.TimeoutError as e:
                # In local/dev, fall back to in-process workflow rather than hanging the job forever.
                logger.warning(
                    "celery_dispatch_timeout",
                    job_id=job.id,
                    queue=queue_name,
                    broker=_broker_fingerprint(_REDIS_URL),
                )
                if settings.environment == "production":
                    raise HTTPException(
                        status_code=503,
                        detail="Queue dispatch timed out. Check broker connectivity/latency.",
                    ) from e
                # Fall through to workflow_engine fallback below.
                task = None
            
            short_id = task.id[:8] if task and task.id else "unknown"
            if task is not None:
                job.progress_message = f"Queued for worker pickup (task {short_id})."
                logger.info("job_enqueued", job_id=job.id, task_id=task.id, queue=queue_name)
                return
        except Exception as e:
            if settings.environment == "production":
                logger.error("celery_dispatch_failed_production", error=str(e), job_id=job.id)
                raise HTTPException(
                    status_code=503,
                    detail="Queue dispatch failed. Check Redis connectivity and worker health.",
                ) from e
            logger.warning("celery_dispatch_failed_fallback", error=str(e), job_id=job.id)
    from ..services.workflow_engine import process_job
    job.progress_message = "Starting local pipeline (Celery dispatch unavailable)."
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
    post_settings: dict | None = None,
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
        post_settings=post_settings or {},
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

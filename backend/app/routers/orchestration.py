from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import structlog
from typing import Dict, Any
import hmac
import hashlib
from datetime import datetime, timezone

from ..db import get_session
from ..models import Job, User, ProcessedWebhook
from ..deps import get_current_user
from ..services.workflow_engine import update_status
from ..config import settings
from fastapi import Request

router = APIRouter(prefix="/orchestration", tags=["orchestration"])
logger = structlog.get_logger()


def _resolve_orchestration_secret() -> str | None:
    return (settings.orchestration_webhook_secret or settings.n8n_webhook_secret or "").strip() or None


def _parse_timestamp(value: str) -> datetime:
    raw = (value or "").strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    parsed = datetime.fromisoformat(raw)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _verify_signature(secret: str, timestamp: str, body: bytes, signature: str) -> bool:
    message = timestamp.encode("utf-8") + b"." + body
    expected = "sha256=" + hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature or "")

@router.post("/start/{job_id}")
async def start_orchestrated_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Called by n8n to signal that it is ready to oversee this job.
    Essentially moves the job into an 'orchestrated' state.
    """
    job = await session.get(Job, job_id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")

    await update_status(job_id, "processing", "Handed over to n8n orchestration.")
    logger.info("job_orchestration_started", job_id=job_id)
    return {"status": "success", "message": "Job orchestration initiated"}

@router.get("/context/{job_id}")
async def get_job_context(
    job_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Returns media intelligence and metadata for n8n/OpenClaw to process.
    """
    job = await session.get(Job, job_id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job.id,
        "source_path": job.source_path,
        "media_intelligence": job.media_intelligence,
        "theme": job.theme,
        "pacing": job.pacing,
        "mood": job.mood,
        "tier": job.tier
    }

@router.get("/strategy/{job_id}")
async def get_editing_strategy(
    job_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Calls OpenClaw to generate an editing strategy (EDL + Mood) based on media intelligence.
    """
    job = await session.get(Job, job_id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")

    if not job.media_intelligence:
        raise HTTPException(status_code=400, detail="Media intelligence not yet generated for this job")

    from ..services.openclaw_service import openclaw_service
    
    user_requirements = {
        "pacing": job.pacing,
        "mood": job.mood,
        "ratio": job.ratio,
        "platform": job.platform
    }
    
    strategy = await openclaw_service.get_editing_strategy(
        job_id=job.id,
        media_intelligence=job.media_intelligence,
        user_requirements=user_requirements
    )
    
    return strategy

@router.post("/callback/{job_id}")
async def orchestration_callback(
    job_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session)
):
    """
    Receives editing strategy from n8n and triggers technical rendering.
    """
    secret = _resolve_orchestration_secret()
    if not secret:
        raise HTTPException(status_code=503, detail="Orchestration callback secret not configured")

    timestamp = request.headers.get("X-ProEdit-Timestamp")
    signature = request.headers.get("X-ProEdit-Signature")
    event_id = request.headers.get("X-ProEdit-Event-Id")
    if not timestamp or not signature or not event_id:
        raise HTTPException(status_code=401, detail="Missing orchestration signature headers")

    body = await request.body()
    if not _verify_signature(secret, timestamp, body, signature):
        raise HTTPException(status_code=401, detail="Invalid orchestration signature")

    try:
        ts = _parse_timestamp(timestamp)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid orchestration timestamp")

    now = datetime.now(timezone.utc)
    tolerance = max(30, int(settings.orchestration_webhook_tolerance_seconds))
    if abs((now - ts).total_seconds()) > tolerance:
        raise HTTPException(status_code=401, detail="Orchestration callback timestamp outside allowed window")

    session.add(ProcessedWebhook(id=event_id))
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        logger.warning("orchestration_callback_replay_blocked", job_id=job_id, event_id=event_id)
        return {"status": "duplicate", "message": "Callback already processed"}

    payload = await request.json()

    job = await session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status == "complete":
        return {"status": "ignored", "message": "Job already complete"}

    if payload.get("job_id") and int(payload["job_id"]) != job_id:
        raise HTTPException(status_code=400, detail="job_id mismatch in callback payload")

    if payload.get("user_id") and int(payload["user_id"]) != job.user_id:
        raise HTTPException(status_code=400, detail="user_id mismatch in callback payload")

    logger.info("orchestration_callback_received", job_id=job_id, payload=payload)
    
    cuts = payload.get("cuts", [])
    vf_filters = payload.get("vf_filters")
    af_filters = payload.get("af_filters")
    
    if not cuts:
        raise HTTPException(status_code=400, detail="No cuts provided in strategy")

    from ..services.workflow_engine import render_orchestrated_job
    
    # Trigger rendering as a background task
    background_tasks.add_task(
        render_orchestrated_job,
        job_id=job_id,
        cuts=cuts,
        vf_filters=vf_filters,
        af_filters=af_filters
    )
    
    return {"status": "success", "message": "Orchestration strategy received. Rendering started."}

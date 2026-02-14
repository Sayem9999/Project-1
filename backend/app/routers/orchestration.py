from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog
from typing import Dict, Any

from ..db import get_session
from ..models import Job, User
from ..deps import get_current_user
from ..services.workflow_engine import update_status
from ..config import settings

router = APIRouter(prefix="/orchestration", tags=["orchestration"])
logger = structlog.get_logger()

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
    payload: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Receives editing strategy from n8n and triggers technical rendering.
    """
    job = await session.get(Job, job_id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")

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

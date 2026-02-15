import asyncio
from collections import Counter
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..agents.architect_agent import architect_agent
from ..agents.maintenance_agent import maintenance_agent
from ..config import settings
from ..db import get_session
from ..deps import get_current_user
from ..models import AdminActionLog, Job, User
from ..services.autonomy_service import autonomy_service
from ..services.introspection import introspection_service

router = APIRouter(prefix="/maintenance", tags=["maintenance"])

_EXTERNAL_OUTAGE_MARKERS = (
    "provider",
    "timeout",
    "timed out",
    "rate limit",
    "quota",
    "unavailable",
    "connection",
    "gateway",
    "503",
    "gemini",
    "openai",
    "groq",
    "openrouter",
    "redis",
    "modal",
)


async def _log_admin_action(
    session: AsyncSession,
    current_user: User,
    action: str,
    target_type: str = "system",
    target_id: str | None = None,
    details: dict | None = None,
) -> None:
    session.add(
        AdminActionLog(
            admin_user_id=current_user.id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details or {},
        )
    )
    await session.commit()


def _coerce_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _extract_timeout_metrics(performance_metrics: Any) -> tuple[int, dict[str, int]]:
    metrics = performance_metrics if isinstance(performance_metrics, dict) else {}
    total = _coerce_int(metrics.get("stage_timeout_total"), 0)
    counts_raw = metrics.get("stage_timeout_counts")
    counts: dict[str, int] = {}
    if isinstance(counts_raw, dict):
        for stage, value in counts_raw.items():
            if not isinstance(stage, str):
                continue
            count = _coerce_int(value, 0)
            if count > 0:
                counts[stage] = count
    return total, counts


def _classify_failed_job(progress_message: str | None) -> str:
    msg = (progress_message or "").lower()
    if any(marker in msg for marker in _EXTERNAL_OUTAGE_MARKERS):
        return "external_dependency_outage"
    return "hard_failure"


@router.get("/graph")
async def get_system_graph(current_user: User = Depends(get_current_user)):
    """Get the current visualization graph of the codebase."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return await asyncio.to_thread(introspection_service.scan)


@router.get("/status")
async def get_maintenance_status(current_user: User = Depends(get_current_user)):
    """Get scan cache and self-heal status."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return introspection_service.get_health_status()


@router.get("/metrics")
async def get_live_metrics(current_user: User = Depends(get_current_user)):
    """Get real-time system metrics (CPU, RAM, Process stats)."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return await asyncio.to_thread(introspection_service.get_live_metrics)


@router.get("/reliability/timeout-summary")
async def get_timeout_reliability_summary(
    recent_jobs: int | None = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Summarize recent timeout reliability with threshold-based alerts for operators."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")

    window = max(1, min(recent_jobs or settings.reliability_recent_window_jobs, 200))
    rows = await session.execute(
        select(Job)
        .where(Job.status.in_(["complete", "failed"]))
        .order_by(Job.updated_at.desc(), Job.id.desc())
        .limit(window)
    )
    jobs = rows.scalars().all()

    stage_totals: Counter[str] = Counter()
    timeout_jobs = 0
    timeout_events = 0
    max_timeout_total = 0
    taxonomy = {
        "timeout_degraded_success": 0,
        "hard_failure": 0,
        "external_dependency_outage": 0,
    }

    for job in jobs:
        timeout_total, timeout_counts = _extract_timeout_metrics(job.performance_metrics)
        if timeout_total > 0:
            timeout_jobs += 1
            timeout_events += timeout_total
            max_timeout_total = max(max_timeout_total, timeout_total)
            stage_totals.update(timeout_counts)

        if job.status == "complete" and timeout_total > 0:
            taxonomy["timeout_degraded_success"] += 1
        elif job.status == "failed":
            classification = _classify_failed_job(job.progress_message)
            taxonomy[classification] += 1

    total_jobs = len(jobs)
    timeout_rate = round((timeout_jobs / total_jobs) if total_jobs else 0.0, 4)
    top_timeout_stages = [
        {"stage": stage, "timeout_count": count}
        for stage, count in stage_totals.most_common(5)
    ]

    alerts: list[dict[str, Any]] = []
    if max_timeout_total > settings.reliability_max_timeouts_per_job:
        alerts.append(
            {
                "type": "max_timeouts_per_job_exceeded",
                "severity": "high",
                "threshold": settings.reliability_max_timeouts_per_job,
                "actual": max_timeout_total,
            }
        )

    if timeout_rate > settings.reliability_timeout_rate_threshold:
        alerts.append(
            {
                "type": "timeout_rate_exceeded",
                "severity": "high",
                "threshold": settings.reliability_timeout_rate_threshold,
                "actual": timeout_rate,
            }
        )

    stage_spike_threshold = settings.reliability_stage_timeout_spike_threshold
    for stage, count in stage_totals.items():
        if count >= stage_spike_threshold:
            alerts.append(
                {
                    "type": "stage_timeout_spike",
                    "severity": "medium",
                    "stage": stage,
                    "threshold": stage_spike_threshold,
                    "actual": count,
                }
            )

    return {
        "as_of": datetime.utcnow().isoformat(),
        "window": {
            "requested_recent_jobs": recent_jobs,
            "effective_recent_jobs": window,
            "observed_jobs": total_jobs,
        },
        "thresholds": {
            "max_timeouts_per_job": settings.reliability_max_timeouts_per_job,
            "timeout_rate": settings.reliability_timeout_rate_threshold,
            "stage_timeout_spike": stage_spike_threshold,
        },
        "summary": {
            "timeout_jobs": timeout_jobs,
            "timeout_rate": timeout_rate,
            "timeout_events": timeout_events,
            "max_timeouts_in_single_job": max_timeout_total,
            "top_timeout_stages": top_timeout_stages,
            "taxonomy": taxonomy,
        },
        "alerts": alerts,
    }


@router.post("/architect")
async def ask_architect(payload: Dict[str, Any], current_user: User = Depends(get_current_user)):
    """Ask the System Architect a question about the codebase."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return await architect_agent.run(payload)


@router.post("/audit")
async def run_audit(current_user: User = Depends(get_current_user)):
    """Run an integrity audit and find gaps."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return await maintenance_agent.run({"task": "audit"})


@router.post("/refresh")
async def refresh_graph(current_user: User = Depends(get_current_user)):
    """Force-refresh the system graph cache."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return await asyncio.to_thread(introspection_service.scan, force=True)


@router.post("/heal")
async def trigger_healing(payload: Dict[str, Any], current_user: User = Depends(get_current_user)):
    """Trigger an autonomous repair of a specific error."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return await maintenance_agent.run({"task": "heal", "error_trace": payload.get("error_trace")})


@router.post("/self-heal")
async def trigger_self_heal(current_user: User = Depends(get_current_user)):
    """Run cache/data self-healing for maintenance graph."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return await asyncio.to_thread(introspection_service.self_heal)


@router.post("/populate")
async def trigger_population(payload: Dict[str, Any], current_user: User = Depends(get_current_user)):
    """Generate a scaffold plan for requested feature population."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return await maintenance_agent.run({"task": "populate", "feature_request": payload.get("feature_request")})


@router.post("/chaos")
async def trigger_chaos(duration: int = 60, current_user: User = Depends(get_current_user)):
    """Unleash the Chaos Monkey to stress test the system."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    from ..services.chaos import chaos_monkey

    asyncio.create_task(chaos_monkey.start_chaos_session(duration))
    return {"status": "chaos_unleashed", "duration": duration}


@router.get("/autonomy/status")
async def get_autonomy_status(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return autonomy_service.get_status()


@router.post("/autonomy/run")
async def run_autonomy_now(
    force_improve: bool = False,
    force_heal: bool = False,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    result = await autonomy_service.run_once(force_improve=force_improve, force_heal=force_heal)
    await _log_admin_action(
        session=session,
        current_user=current_user,
        action="autonomy.run",
        details={
            "force_heal": force_heal,
            "force_improve": force_improve,
            "result_summary": {
                "idle": result.get("idle"),
                "high_load": result.get("high_load"),
                "heal_ran": result.get("heal_ran"),
                "improve_ran": result.get("improve_ran"),
            },
        },
    )
    return result


@router.post("/autonomy/profile")
async def set_autonomy_profile(
    mode: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    try:
        status = autonomy_service.set_profile(mode)
        await _log_admin_action(
            session=session,
            current_user=current_user,
            action="autonomy.profile.set",
            details={"mode": mode, "profile_mode": status.get("profile_mode")},
        )
        return status
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

import asyncio
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from ..services.introspection import introspection_service
from ..services.autonomy_service import autonomy_service
from ..agents.maintenance_agent import maintenance_agent
from ..agents.architect_agent import architect_agent
from ..db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from ..deps import get_current_user
from ..models import User, AdminActionLog

router = APIRouter(prefix="/maintenance", tags=["maintenance"])


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

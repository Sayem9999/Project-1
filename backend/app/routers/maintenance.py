from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from ..services.introspection import introspection_service
from ..agents.maintenance_agent import maintenance_agent
from ..agents.architect_agent import architect_agent
from ..deps import get_current_user
from ..models import User

router = APIRouter(prefix="/maintenance", tags=["maintenance"])

@router.get("/graph")
async def get_system_graph(current_user: User = Depends(get_current_user)):
    """Get the current visualization graph of the codebase."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return introspection_service.scan()


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
    return introspection_service.get_live_metrics()

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
    return introspection_service.scan(force=True)

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
    return introspection_service.self_heal()


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
    import asyncio
    asyncio.create_task(chaos_monkey.start_chaos_session(duration))
    return {"status": "chaos_unleashed", "duration": duration}

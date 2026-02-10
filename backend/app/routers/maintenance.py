from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from ..services.introspection import introspection_service
from ..agents.maintenance_agent import maintenance_agent
from ..deps import get_current_user
from ..models import User

router = APIRouter(prefix="/maintenance", tags=["maintenance"])

@router.get("/graph")
async def get_system_graph(current_user: User = Depends(get_current_user)):
    """Get the current visualization graph of the codebase."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return introspection_service.scan()

@router.post("/audit")
async def run_audit(current_user: User = Depends(get_current_user)):
    """Run an integrity audit and find gaps."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return await maintenance_agent.run({"task": "audit"})

@router.post("/heal")
async def trigger_healing(payload: Dict[str, Any], current_user: User = Depends(get_current_user)):
    """Trigger an autonomous repair of a specific error."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return await maintenance_agent.run({"task": "heal", "error_trace": payload.get("error_trace")})

@router.post("/chaos")
async def trigger_chaos(duration: int = 60, current_user: User = Depends(get_current_user)):
    """Unleash the Chaos Monkey to stress test the system."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    from ..services.chaos import chaos_monkey
    import asyncio
    asyncio.create_task(chaos_monkey.start_chaos_session(duration))
    return {"status": "chaos_unleashed", "duration": duration}

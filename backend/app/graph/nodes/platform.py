"""
Platform Node - Adapt video specifications for target platforms.
"""
from typing import Dict, Any
from ..state import GraphState
from ...agents import platform_agent
import structlog

logger = structlog.get_logger(__name__)

async def platform_node(state: GraphState) -> GraphState:
    """
    Adapts the plan for specific platform requirements.
    """
    logger.info("platform_node_start", job_id=state.get("job_id"))
    
    # Extract platform from user request or default to tiktok
    platform = state.get("user_request", {}).get("platform", "tiktok")
    
    payload = {
        "job_id": state.get("job_id"),
        "platform": platform,
        "director_plan": state.get("director_plan", {}),
        "content_type": state.get("user_request", {}).get("content_type", "short-form"),
    }
    
    try:
        result = await platform_agent.run(payload, job_id=state.get("job_id"))
        return {"platform_result": result.model_dump()}
    except Exception as e:
        logger.error("platform_node_error", error=str(e))
        return {"errors": [f"Platform Agent failed: {str(e)}"]}

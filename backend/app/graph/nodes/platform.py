"""
Platform Node - Adapt video specifications for target platforms.
"""
from typing import Dict, Any
from ..state import GraphState
from ...agents import platform_agent
import structlog
from ._timeouts import run_with_stage_timeout

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
        result = await run_with_stage_timeout(
            platform_agent.run(payload, job_id=state.get("job_id")),
            stage="platform",
            job_id=state.get("job_id"),
        )
        return {"platform_result": result.model_dump()}
    except TimeoutError as e:
        logger.warning("platform_node_timeout", error=str(e), job_id=state.get("job_id"))
        return {"errors": [str(e)], "platform_result": {"warning": str(e), "platform": platform}}
    except Exception as e:
        logger.error("platform_node_error", error=str(e))
        return {"errors": [f"Platform Agent failed: {str(e)}"]}

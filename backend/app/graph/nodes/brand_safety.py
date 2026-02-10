"""
Brand Safety Node - Content moderation and policy checks.
"""
from typing import Dict, Any
from ..state import GraphState
from ...agents import brand_safety_agent
import structlog

logger = structlog.get_logger(__name__)

async def brand_safety_node(state: GraphState) -> GraphState:
    """
    Checks the plan and transcript for brand safety violations.
    """
    logger.info("brand_safety_node_start", job_id=state.get("job_id"))
    
    payload = {
        "job_id": state.get("job_id"),
        "transcript": state.get("keyframe_data", {}).get("transcript", ""),
        "visual_description": state.get("director_plan", {}).get("directors_vision", ""),
    }
    
    try:
        result = await brand_safety_agent.run(payload, job_id=state.get("job_id"))
        return {"brand_safety_result": result.model_dump()}
    except Exception as e:
        logger.error("brand_safety_node_error", error=str(e))
        return {"errors": [f"Brand Safety Agent failed: {str(e)}"]}

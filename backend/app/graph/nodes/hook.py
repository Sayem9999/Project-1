"""
Hook Node - Analyze first 3-5 seconds of video.
"""
from typing import Dict, Any
from ..state import GraphState
from ...agents import hook_agent
import structlog

logger = structlog.get_logger(__name__)

async def hook_node(state: GraphState) -> GraphState:
    """
    Analyzes the hook potential of the video.
    """
    logger.info("hook_node_start", job_id=state.get("job_id"))
    
    payload = {
        "job_id": state.get("job_id"),
        "director_plan": state.get("director_plan", {}),
        "keyframe_analysis": state.get("keyframe_data", {}),
    }
    
    try:
        result = await hook_agent.run(payload, job_id=state.get("job_id"))
        return {"hook_result": result.model_dump()}
    except Exception as e:
        logger.error("hook_node_error", error=str(e))
        return {
            "hook_result": {
                "attention_technique": "fallback",
                "opening_cuts": [],
                "hook_text": None,
                "retention_score": 5,
                "warning": f"Hook Agent unavailable: {str(e)}",
            }
        }

"""
Brand Safety Node - Content moderation and policy checks.
"""
from typing import Dict, Any
from ..state import GraphState
from ...agents import brand_safety_agent
import structlog
from ._timeouts import run_with_stage_timeout

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
        result = await run_with_stage_timeout(
            brand_safety_agent.run(payload, job_id=state.get("job_id")),
            stage="brand_safety",
            job_id=state.get("job_id"),
        )
        return {"brand_safety_result": result.model_dump()}
    except TimeoutError as e:
        logger.warning("brand_safety_node_timeout", error=str(e), job_id=state.get("job_id"))
        return {
            "brand_safety_result": {
                "is_safe": True,
                "violations": [],
                "risk_score": 0,
                "recommendations": ["Brand safety timed out; manual review recommended."],
                "warning": str(e),
            }
        }
    except Exception as e:
        logger.error("brand_safety_node_error", error=str(e))
        return {
            "brand_safety_result": {
                "is_safe": True,
                "violations": [],
                "risk_score": 0,
                "recommendations": ["Brand safety agent unavailable; manual review recommended."],
                "warning": f"Brand Safety Agent unavailable: {str(e)}",
            }
        }

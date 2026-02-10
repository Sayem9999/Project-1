"""
A/B Test Node - Generate variants for testing.
"""
from typing import Dict, Any
from ..state import GraphState
from ...agents import ab_test_agent
import structlog

logger = structlog.get_logger(__name__)

async def ab_test_node(state: GraphState) -> GraphState:
    """
    Generates A/B test variants for headings or hooks.
    """
    logger.info("ab_test_node_start", job_id=state.get("job_id"))
    
    payload = {
        "job_id": state.get("job_id"),
        "variant_type": "hook", # Default to hook for now
        "transcript_summary": state.get("keyframe_data", {}).get("summary", ""),
        "target_platform": state.get("user_request", {}).get("platform", "tiktok"),
        "content_type": state.get("user_request", {}).get("content_type", "short-form"),
    }
    
    try:
        result = await ab_test_agent.run(payload, job_id=state.get("job_id"))
        return {"ab_test_result": result.model_dump()}
    except Exception as e:
        logger.error("ab_test_node_error", error=str(e))
        # Non-fatal: return a placeholder instead of failing the full pipeline
        return {
            "ab_test_result": {
                "error": f"A/B Test Agent failed: {str(e)}"
            }
        }

import structlog
from typing import Dict, Any
from ..state import GraphState
from ...agents import scout_agent
from ...services.stock_scout_service import stock_scout_service

logger = structlog.get_logger()

async def scout_node(state: GraphState) -> Dict[str, Any]:
    """
    Scout Node: Finds real-world stock footage matching the director's vision.
    """
    job_id = state.get("job_id")
    logger.info("node_scout_start", job_id=job_id)
    
    plan = state.get("director_plan", {})
    
    try:
        # 1. Ask the AI Scout to generate search queries
        scout_resp = await scout_agent.run({"plan": plan, "job_id": job_id})
        scout_data = scout_resp.model_dump()
        
        # 2. Execute the actual search against Pexels/Pixabay
        queries = scout_data.get("search_queries", [])
        if queries:
            logger.info("scouting_stock_api", job_id=job_id, queries=queries)
            real_assets = await stock_scout_service.search(queries)
            # Add real results to the agent's logic
            scout_data["real_assets"] = real_assets
        
        return {
            "scout_result": scout_data
        }
    except Exception as e:
        logger.error("node_scout_failed", job_id=job_id, error=str(e))
        return {
            "errors": [f"Scout Agent failed: {str(e)}"]
        }

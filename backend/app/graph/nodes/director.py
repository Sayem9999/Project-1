from ..state import GraphState
from ...agents import director_agent
import json
from ._timeouts import run_with_stage_timeout

async def director_node(state: GraphState) -> GraphState:
    """
    Director Node: Plans the video strategy.
    """
    print("--- [Graph] Director Planning ---")
    
    payload = {
        "job_id": state.get("job_id"),
        "source_path": state["source_path"],
        "user_request": state["user_request"],
        "keyframe_analysis": state.get("keyframe_data", {})
    }
    
    try:
        plan = await run_with_stage_timeout(
            director_agent.run(payload),
            stage="director",
            job_id=state.get("job_id"),
        )
        # Convert to dict for state storage (or keep as model if state supports it)
        return {"director_plan": plan.model_dump()}
    except TimeoutError as e:
        print(f"Director Timeout: {e}")
        return {"errors": [str(e)], "director_plan": {}}
    except Exception as e:
        print(f"Director Error: {e}")
        return {"errors": [str(e)]}

from ..state import GraphState
from ...agents import director_agent
import json

async def director_node(state: GraphState) -> GraphState:
    """
    Director Node: Plans the video strategy.
    """
    print("--- [Graph] Director Planning ---")
    
    payload = {
        "source_path": state["source_path"],
        "user_request": state["user_request"],
        "keyframe_analysis": state.get("keyframe_data", {})
    }
    
    try:
        resp = await director_agent.run(payload)
        raw = resp.get("raw_response", "{}")
        clean = raw.replace("```json", "").replace("```", "").strip()
        plan = json.loads(clean)
        
        return {"director_plan": plan}
    except Exception as e:
        print(f"Director Error: {e}")
        return {"errors": [str(e)]}

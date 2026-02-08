from ..state import GraphState
from ...agents import cutter_agent
import json

async def cutter_node(state: GraphState) -> GraphState:
    """
    Cutter Node: Generates the EDL (Edit Decision List).
    """
    print("--- [Graph] Cutter Working ---")
    
    plan = state.get("director_plan")
    if not plan:
        return {"errors": ["No director plan found"]}
        
    try:
        resp = await cutter_agent.run({"plan": plan})
        raw = resp.get("raw_response", "{}")
        clean = raw.replace("```json", "").replace("```", "").strip()
        cuts_data = json.loads(clean)
        
        return {"cuts": cuts_data.get("cuts", [])}
    except Exception as e:
        print(f"Cutter Error: {e}")
        return {"errors": [str(e)]}

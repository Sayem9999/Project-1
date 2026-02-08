import asyncio
import json
from ..state import GraphState
from ...agents import color_agent, vfx_agent

async def visuals_node(state: GraphState) -> GraphState:
    """
    Visuals Node: Runs Color and VFX agents in parallel.
    """
    print("--- [Graph] Visuals Processing ---")
    
    plan = state.get("director_plan")
    mood = state.get("user_request", {}).get("mood", "professional")
    
    if not plan:
        return {"errors": ["Visuals node missing plan"]}

    # Run Color and VFX in parallel
    async def run_color():
        try:
            resp = await color_agent.run({"plan": plan, "mood": mood})
            return json.loads(resp.get("raw_response", "{}").replace("```json", "").replace("```", "").strip())
        except: return {}

    async def run_vfx():
        try:
            resp = await vfx_agent.run({"plan": plan, "mood": mood})
            return json.loads(resp.get("raw_response", "{}").replace("```json", "").replace("```", "").strip())
        except: return {}

    results = await asyncio.gather(run_color(), run_vfx())
    color_data, vfx_data = results
    
    # Merge effects
    effects = []
    if color_data.get("lut"): effects.append({"type": "lut", "value": color_data["lut"]})
    if vfx_data.get("effects"): effects.extend(vfx_data["effects"])
    
    return {"visual_effects": effects}

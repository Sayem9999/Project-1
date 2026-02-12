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
    
    # Handle color agent output
    if color_data.get("ffmpeg_color_filter"):
        effects.append({
            "type": "ffmpeg_filter", 
            "value": color_data["ffmpeg_color_filter"],
            "name": "color_grading"
        })
    if color_data.get("lut_recommendation"):
        effects.append({
            "type": "lut", 
            "value": color_data["lut_recommendation"]
        })
        
    # Handle VFX agent output
    if vfx_data.get("effects"):
        for effect in vfx_data["effects"]:
            effects.append({
                "type": "ffmpeg_filter",
                "value": effect.get("filter", ""),
                "name": effect.get("name", "vfx")
            })
    elif vfx_data.get("ffmpeg_filter"):
        effects.append({
            "type": "ffmpeg_filter",
            "value": vfx_data["ffmpeg_filter"],
            "name": "vfx_summary"
        })
    
    return {"visual_effects": effects}

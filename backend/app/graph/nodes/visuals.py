import asyncio
import json
from ..state import GraphState
from ...agents import color_agent, vfx_agent
from ...services.post_production_depth import build_color_pipeline_filters
from ._timeouts import run_with_stage_timeout

async def visuals_node(state: GraphState) -> GraphState:
    """
    Visuals Node: Runs Color and VFX agents in parallel.
    """
    print("--- [Graph] Visuals Processing ---")
    
    plan = state.get("director_plan")
    mood = state.get("user_request", {}).get("mood", "professional")
    
    if not plan:
        return {"errors": ["Visuals node missing plan"]}

    from ...agents.base import parse_json_response

    # Run Color and VFX in parallel
    async def run_color():
        try:
            director_instructions = (plan.get("instructions", {}) if isinstance(plan, dict) else {}).get("color", "")
            resp = await run_with_stage_timeout(
                color_agent.run({
                    "plan": plan.get("directors_vision") if isinstance(plan, dict) else plan, 
                    "instructions": director_instructions,
                    "mood": mood,
                    "media_intelligence": state.get("media_intelligence", {})
                }),
                stage="visuals_color",
                job_id=state.get("job_id"),
            )
            return parse_json_response(resp.get("raw_response", "{}"))
        except Exception as e:
            print(f"Color Agent Parse Error: {e}")
            return {}

    async def run_vfx():
        try:
            resp = await run_with_stage_timeout(
                vfx_agent.run({"plan": plan, "mood": mood}),
                stage="visuals_vfx",
                job_id=state.get("job_id"),
            )
            return parse_json_response(resp.get("raw_response", "{}"))
        except Exception as e:
            print(f"VFX Agent Parse Error: {e}")
            return {}

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
    elif color_data.get("color_mood"):
        # Fallback to a basic enhancement if no specific filter but mood is given
        effects.append({
            "type": "ffmpeg_filter",
            "value": "eq=contrast=1.1:saturation=1.1",
            "name": f"mood_{color_data['color_mood']}"
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
        # Strip potential -vf lead-in
        clean_filter = vfx_data["ffmpeg_filter"].replace('-vf "', '').replace('"', '').strip()
        effects.append({
            "type": "ffmpeg_filter",
            "value": clean_filter,
            "name": "vfx_summary"
        })

    # Add consistent baseline color pipeline filters (scene match + skin protection).
    pipeline_filters = build_color_pipeline_filters(
        mood=mood,
        media_intel=state.get("media_intelligence"),
        visual_effects=[],
    )
    for idx, flt in enumerate(pipeline_filters):
        effects.append({
            "type": "ffmpeg_filter",
            "value": flt,
            "name": f"color_pipeline_{idx}",
        })
    
    return {"visual_effects": effects}

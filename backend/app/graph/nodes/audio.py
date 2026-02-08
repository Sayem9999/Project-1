from ..state import GraphState
from ...agents import audio_agent
import json

async def audio_node(state: GraphState) -> GraphState:
    """
    Audio Node: Selects music and sound effects based on the Cut.
    """
    print("--- [Graph] Audio Scoring ---")
    
    plan = state.get("director_plan")
    cuts = state.get("cuts")
    
    if not plan or not cuts:
        return {"errors": ["Audio node missing inputs"]}
        
    payload = {
        "plan": plan,
        "cut_list": cuts,
        "mood": state.get("user_request", {}).get("mood", "professional")
    }
        
    try:
        resp = await audio_agent.run(payload)
        raw = resp.get("raw_response", "{}")
        clean = raw.replace("```json", "").replace("```", "").strip()
        audio_data = json.loads(clean)
        
        return {"audio_tracks": audio_data.get("audio_tracks", [])}
    except Exception as e:
        print(f"Audio Error: {e}")
        return {"errors": [str(e)]}

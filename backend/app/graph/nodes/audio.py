from ..state import GraphState
from ...agents import audio_agent
from ...services.audio_intelligence import AudioAnalyzer
import json
import structlog

logger = structlog.get_logger()


async def audio_node(state: GraphState) -> GraphState:
    """
    Audio Node: Selects music and sound effects based on the Cut.
    Uses AudioIntelligence to detect loudness and ducking needs.
    """
    logger.info("audio_node_start", job_id=state.get("job_id"))
    
    plan = state.get("director_plan")
    cuts = state.get("cuts")
    source_path = state.get("source_path", "")
    
    if not plan or not cuts:
        return {"errors": ["Audio node missing inputs"]}
    
    # Analyze audio intelligence
    audio_intel = await _get_audio_intelligence(source_path)
    
    payload = {
        "plan": plan,
        "cut_list": cuts,
        "mood": state.get("user_request", {}).get("mood", "professional"),
        "audio_intelligence": audio_intel,
    }
        
    try:
        resp = await audio_agent.run(payload)
        raw = resp.get("raw_response", "{}")
        clean = raw.replace("```json", "").replace("```", "").strip()
        audio_data = json.loads(clean)
        
        logger.info(
            "audio_node_complete",
            job_id=state.get("job_id"),
            track_count=len(audio_data.get("audio_tracks", []))
        )
        
        return {
            "audio_tracks": audio_data.get("audio_tracks", []),
            "audio_intelligence": audio_intel,
        }
    except Exception as e:
        logger.error("audio_node_error", job_id=state.get("job_id"), error=str(e))
        return {"errors": [str(e)]}


async def _get_audio_intelligence(source_path: str) -> dict:
    """
    Get audio profiling data (loudness, ducking needs).
    """
    if not source_path:
        return {}
    
    try:
        analyzer = AudioAnalyzer()
        profile = await analyzer.analyze(source_path)
        
        return {
            "integrated_loudness": profile.get("integrated_loudness", -23),
            "true_peak": profile.get("true_peak", -1),
            "ducking_segments": profile.get("ducking_segments", []),
            "noise_floor": profile.get("noise_floor", -60),
        }
    except Exception as e:
        logger.warning("audio_analysis_failed", error=str(e))
        return {"integrated_loudness": -23, "true_peak": -1}


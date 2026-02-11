from ..state import GraphState
from ...agents import cutter_agent
from ...services.media_analysis import MediaAnalyzer
import json
import structlog

logger = structlog.get_logger()


async def cutter_node(state: GraphState) -> GraphState:
    """
    Cutter Node: Generates the EDL (Edit Decision List).
    Uses shot boundary detection to inform cut decisions.
    """
    logger.info("cutter_node_start", job_id=state.get("job_id"))
    
    plan = state.get("director_plan")
    if not plan:
        return {"errors": ["No director plan found"]}
    
    # Get shot metadata if available
    shot_metadata = await _get_shot_metadata(state)
    
    # Include revision prompt if iterating
    revision_prompt = state.get("revision_prompt", "")
    
    try:
        # Build enhanced payload with shot boundaries
        payload = {
            "job_id": state.get("job_id"),
            "plan": plan,
            "shot_boundaries": shot_metadata.get("shots", []),
            "scene_count": shot_metadata.get("scene_count", 0),
            "avg_shot_duration": shot_metadata.get("avg_duration", 0),
        }
        
        if revision_prompt:
            payload["revision_feedback"] = revision_prompt
        
        cuts_data = await cutter_agent.run(payload)
        cuts = [cut.model_dump() for cut in cuts_data.cuts]
        
        # Validate cuts against shot boundaries
        validated_cuts = _validate_cuts_against_shots(cuts, shot_metadata.get("shots", []))
        
        logger.info(
            "cutter_node_complete",
            job_id=state.get("job_id"),
            cut_count=len(validated_cuts),
            shot_count=len(shot_metadata.get("shots", []))
        )
        
        return {
            "cuts": validated_cuts,
            "shot_metadata": shot_metadata,
        }
    except Exception as e:
        logger.error("cutter_node_error", job_id=state.get("job_id"), error=str(e))
        return {"errors": [str(e)]}


async def _get_shot_metadata(state: GraphState) -> dict:
    """
    Get shot boundary metadata from scene detection.
    Uses cached results if available.
    """
    # Check for cached shot data
    if state.get("shot_metadata"):
        return state["shot_metadata"]
    
    source_path = state.get("source_path", "")
    if not source_path:
        return {"shots": [], "scene_count": 0, "avg_duration": 0}
    
    try:
        analyzer = MediaAnalyzer()
        scenes = await analyzer.detect_scenes(source_path)
        
        shots = []
        total_duration = 0
        
        for i, scene in enumerate(scenes):
            shot = {
                "id": i,
                "start": scene.start_time,
                "end": scene.end_time,
                "duration": scene.duration,
                "scene_type": "scenedetect",
            }
            shots.append(shot)
            total_duration += shot["duration"]
        
        avg_duration = total_duration / len(shots) if shots else 0
        
        return {
            "shots": shots,
            "scene_count": len(shots),
            "avg_duration": avg_duration,
        }
    except Exception as e:
        logger.warning("shot_detection_failed", error=str(e))
        return {"shots": [], "scene_count": 0, "avg_duration": 0}


def _validate_cuts_against_shots(cuts: list, shots: list) -> list:
    """
    Validate and adjust cuts to respect shot boundaries where appropriate.
    Snaps cuts to nearest shot boundary if close.
    """
    if not shots:
        return cuts
    
    shot_boundaries = set()
    for shot in shots:
        shot_boundaries.add(shot.get("start", 0))
        shot_boundaries.add(shot.get("end", 0))
    
    validated = []
    snap_threshold = 0.5  # seconds
    
    for cut in cuts:
        start = cut.get("start", 0)
        end = cut.get("end", 0)
        
        # Snap to nearest shot boundary if close
        for boundary in shot_boundaries:
            if abs(start - boundary) < snap_threshold:
                start = boundary
            if abs(end - boundary) < snap_threshold:
                end = boundary
        
        validated.append({
            **cut,
            "start": start,
            "end": end,
            "snapped_to_shot": start != cut.get("start") or end != cut.get("end"),
        })
    
    return validated

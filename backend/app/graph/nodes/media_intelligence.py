import structlog
from typing import Any, Dict
from ...services.media_analysis import media_analyzer
from ...services.audio_intelligence import audio_intelligence
from ..state import GraphState

logger = structlog.get_logger()

async def media_intelligence_node(state: GraphState) -> Dict[str, Any]:
    """
    Node that performs technical analysis of the media with granular progress updates.
    """
    job_id = state.get("job_id")
    source_path = state.get("source_path")
    user_id = state.get("user_id")
    
    # Late import to avoid circular dependency
    from ...services.workflow_engine import publish_progress
    
    logger.info("media_intelligence_node_start", job_id=job_id)

    # Use existing intelligence if provided by client (Better Way / Holy Grail)
    existing_intel = state.get("media_intelligence")
    if existing_intel and existing_intel.get("visual"):
        logger.info("media_intelligence_skipping_analysis", job_id=job_id, source="client")
        return {
            "media_intelligence": existing_intel
        }
    
    try:
        # Phase 1: Metadata
        publish_progress(job_id, "processing", "Analyzing video structure...", 10, user_id=user_id)
        metadata = await media_analyzer.get_metadata(source_path)
        
        # Phase 2: Scenes
        publish_progress(job_id, "processing", "Detecting scene changes...", 12, user_id=user_id)
        scenes = await media_analyzer.detect_scenes(source_path)
        
        # Phase 3: Audio
        publish_progress(job_id, "processing", "Profiling audio loudness...", 15, user_id=user_id)
        audio_analysis = await audio_intelligence.analyze(source_path)
        
        # Phase 4: Speech/Finalize
        publish_progress(job_id, "processing", "Finalizing intelligence data...", 18, user_id=user_id)
        
        # Combine into a dictionary
        intelligence_data = {
            "visual": {
                "metadata": metadata.__dict__ if metadata else {},
                "scenes": [s.__dict__ for s in scenes],
                "avg_shot_length": (sum(s.duration for s in scenes) / len(scenes)) if scenes else None
            },
            "audio": {
                "overall_lufs": audio_analysis.overall_lufs,
                "overall_peak": audio_analysis.overall_peak,
                "silence_regions": [s.__dict__ for s in audio_analysis.silence_regions],
                "speech_regions": audio_analysis.speech_regions,
                "needs_normalization": audio_analysis.needs_normalization
            }
        }
        
        return {
            "media_intelligence": intelligence_data
        }
    except Exception as e:
        logger.error("media_intelligence_node_failed", job_id=job_id, error=str(e))
        return {
            "errors": [f"Media intelligence failed: {str(e)}"]
        }

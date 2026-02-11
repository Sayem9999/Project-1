import structlog
from typing import Any, Dict
from ...services.media_analysis import media_analyzer
from ...services.audio_intelligence import audio_intelligence
from ..state import GraphState

logger = structlog.get_logger()

async def media_intelligence_node(state: GraphState) -> Dict[str, Any]:
    """
    Node that performs technical analysis of the media.
    """
    job_id = state.get("job_id")
    source_path = state.get("source_path")
    
    logger.info("media_intelligence_node_start", job_id=job_id)

    # Use existing intelligence if provided by client (Better Way / Holy Grail)
    existing_intel = state.get("media_intelligence")
    if existing_intel and existing_intel.get("visual"):
        logger.info("media_intelligence_skipping_analysis", job_id=job_id, source="client")
        return {
            "media_intelligence": existing_intel
        }
    
    try:
        # Run visual analysis
        visual_analysis = await media_analyzer.analyze(source_path)
        
        # Run audio analysis
        audio_analysis = await audio_intelligence.analyze(source_path)
        
        # Combine into a dictionary
        intelligence_data = {
            "visual": {
                "metadata": visual_analysis.metadata.__dict__ if visual_analysis.metadata else {},
                "scenes": [s.__dict__ for s in visual_analysis.scenes],
                "avg_shot_length": visual_analysis.avg_shot_length
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

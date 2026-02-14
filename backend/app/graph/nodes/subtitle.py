import structlog
from pathlib import Path
from typing import Any, Dict
from ..state import GraphState
from ...agents import subtitle_agent
from ...services.post_production_depth import subtitle_qa_report

logger = structlog.get_logger()

async def subtitle_node(state: GraphState) -> Dict[str, Any]:
    """
    Subtitles Node: Generates SRT file content using AI.
    """
    job_id = state.get("job_id")
    source_path = state.get("source_path")
    user_id = state.get("user_id")
    
    # Late import to avoid circular dependency
    from ...services.workflow_engine import publish_progress
    
    logger.info("subtitle_node_start", job_id=job_id)
    publish_progress(job_id, "processing", "Transcribing and generating subtitles...", 70, user_id=user_id)
    
    try:
        # Run Subtitle Agent
        payload = {"source_path": source_path}
        sub_resp = await subtitle_agent.run(payload)
        srt_content = sub_resp.get("raw_response", "") if isinstance(sub_resp, dict) else ""
        
        if not srt_content or "1" not in srt_content:
            logger.warning("subtitle_node_no_content", job_id=job_id)
            return {"srt_path": None}
            
        # Save SRT to temporary file
        from ...config import settings
        srt_filename = f"job-{job_id}.srt"
        srt_path = Path(settings.storage_root) / "outputs" / srt_filename
        srt_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(srt_content)
            
        logger.info("subtitle_node_complete", job_id=job_id, srt_path=str(srt_path))
        
        qa = subtitle_qa_report(srt_content)
        return {
            "srt_path": str(srt_path),
            "subtitle_qa": qa,
        }
    except Exception as e:
        logger.error("subtitle_node_failed", job_id=job_id, error=str(e))
        # Don't fail the whole pipeline for subtitles
        return {
            "errors": [f"Subtitle generation failed: {str(e)}"],
            "srt_path": None
        }

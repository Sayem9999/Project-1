import structlog
from pathlib import Path
from typing import Any, Dict
from ..state import GraphState
from ...agents import subtitle_agent
from ...services.post_production_depth import subtitle_qa_report
from ._timeouts import run_with_stage_timeout

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
        # Run Script Agent (SCRIBE) with structured output
        from ...agents import script_agent
        from ...config import settings
        from ...agents.base import parse_json_response

        # Director's mood and plan
        mood = state.get("user_request", {}).get("mood", "professional")
        plan = state.get("director_plan", "Professional social media cut.")

        payload = {
            "source_path": source_path,
            "mood": mood,
            "plan": plan
        }
        
        script_resp = await run_with_stage_timeout(
            script_agent.run(payload),
            stage="scribe_script",
            job_id=job_id,
        )
        
        # Parse structured JSON
        script_data = parse_json_response(script_resp.get("raw_response", "{}"))
        
        # We still need raw SRT content. SCRIBE's ffmpeg_subtitle_filter usually depends on an SRT file.
        # If the agent didn't provide raw SRT but provided timings, we can generate it or look at subtitle_agent.
        # For Phase 8, let's assume SCRIBE provides structured "word_timings" and we still might need subtitle_agent for basic SRT task
        # OR SCRIBE handles it all. 
        
        # TO ELEVATE: Let's run subtitle_agent in parallel for the raw SRT if SCRIBE only does the kinetic highlights.
        # But ideally SCRIBE (Scribe Agent) should eventually replace it.
        # For now, let's stick to using script_data for the Kinetic Branding.
        
        # Capture word timings for Phase 8 Kinetic Highlights
        word_timings = script_data.get("word_timings", [])
        highlight_color = script_data.get("highlight_color", "#FFFF00")
        
        # Fallback to subtitle_agent for raw SRT if not in script_data
        srt_content = state.get("srt_content")
        if not srt_content:
            sub_resp = await run_with_stage_timeout(
                subtitle_agent.run({"source_path": source_path}),
                stage="subtitle_raw",
                job_id=job_id,
            )
            srt_content = sub_resp.get("raw_response", "")
        
        if not srt_content:
            logger.warning("subtitle_node_no_content", job_id=job_id)
            return {"srt_path": None}
            
        # Save SRT
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
            "word_timings": word_timings,
            "highlight_color": highlight_color,
            "subtitle_style": script_data.get("subtitle_style", "professional"),
        }
    except TimeoutError:
        logger.warning("subtitle_node_timeout", job_id=job_id)
        return {
            "errors": ["Subtitle generation timed out"],
            "srt_path": None,
        }
    except Exception as e:
        logger.error("subtitle_node_failed", job_id=job_id, error=str(e))
        # Don't fail the whole pipeline for subtitles
        return {
            "errors": [f"Subtitle generation failed: {str(e)}"],
            "srt_path": None
        }

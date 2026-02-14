import structlog
from typing import Dict, Any, List
from .workflow_engine import normalize_agent_result
from ..agents.director_agent import run as run_director
from ..agents.cutter_agent import run as run_cutter
from ..agents.color_agent import run as run_color

logger = structlog.get_logger()

class OpenClawService:
    """
    OpenClaw Intelligence Provider (Strictly Technical Editing).
    Orchestrates specialized agents to generate a technical editing strategy for n8n.
    """

    async def get_editing_strategy(self, job_id: int, media_intelligence: Dict[str, Any], user_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes media intelligence and user requirements to produce a concrete editing plan.
        """
        logger.info("openclaw_generating_strategy", job_id=job_id)

        # 1. Get Director's Vision (Technical Focus)
        director_payload = {
            "job_id": job_id,
            "pacing": user_requirements.get("pacing", "medium"),
            "mood": user_requirements.get("mood", "professional"),
            "ratio": user_requirements.get("ratio", "16:9"),
            "memory_context": "Strict technical edit. No generative assets.",
            "feedback": ""
        }
        director_out = await run_director(director_payload)
        
        # 2. Get Cuts from SLICE (Cutter Agent)
        cutter_payload = {
            "job_id": job_id,
            "instructions": director_out.instructions.get("cutter", "Standard interview cuts"),
            "media_intelligence": media_intelligence
        }
        cutter_out = await run_cutter(cutter_payload)
        
        # 3. Get Color Strategy from PRISM (Colorist Agent)
        color_payload = {
            "job_id": job_id,
            "instructions": director_out.instructions.get("color", "Natural color correction"),
            "media_intelligence": media_intelligence
        }
        color_out = await run_color(color_payload)

        # 4. Construct the Final Strategy for n8n
        strategy = {
            "job_id": job_id,
            "vision": director_out.directors_vision,
            "cuts": cutter_out.cuts if hasattr(cutter_out, "cuts") else [],
            "vf_filters": color_out.ffmpeg_filter if hasattr(color_out, "ffmpeg_filter") else None,
            "af_filters": "loudnorm=I=-16:TP=-1.5:LRA=11", # Sensible default for technical edits
            "metadata": {
                "mood": director_out.mood,
                "pacing": director_out.pacing,
                "color_palette": director_out.color_palette
            }
        }

        logger.info("openclaw_strategy_generated", job_id=job_id)
        return strategy

openclaw_service = OpenClawService()

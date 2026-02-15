import structlog
import asyncio
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
        director_raw = await run_director(director_payload, provider="gemini")
        director_out = normalize_agent_result(director_raw)
        instructions = director_out.get("instructions") or {}
        if not isinstance(instructions, dict):
            instructions = {}

        # 2. Get Cuts from SLICE (Cutter Agent)
        cutter_payload = {
            "job_id": job_id,
            "instructions": instructions.get("cutter", "Standard interview cuts"),
            "media_intelligence": media_intelligence
        }

        # 3. Get Color Strategy from PRISM (Colorist Agent)
        color_payload = {
            "job_id": job_id,
            "instructions": instructions.get("color", "Natural color correction"),
            "media_intelligence": media_intelligence
        }

        cutter_raw, color_raw = await asyncio.gather(
            run_cutter(cutter_payload, provider="gemini"),
            run_color(color_payload, provider="gemini"),
            return_exceptions=True,
        )

        cutter_out = {}
        if isinstance(cutter_raw, Exception):
            logger.warning("openclaw_cutter_failed", job_id=job_id, error=str(cutter_raw))
        else:
            cutter_out = normalize_agent_result(cutter_raw)

        color_out = {}
        if isinstance(color_raw, Exception):
            logger.warning("openclaw_color_failed", job_id=job_id, error=str(color_raw))
        else:
            color_out = normalize_agent_result(color_raw)

        cuts = cutter_out.get("cuts") or []
        if not isinstance(cuts, list):
            cuts = []

        vf_filters = (
            color_out.get("ffmpeg_color_filter")
            or color_out.get("ffmpeg_filter")
            or None
        )

        # 4. Construct the Final Strategy for n8n
        strategy = {
            "job_id": job_id,
            "vision": director_out.get("directors_vision", ""),
            "cuts": cuts,
            "vf_filters": vf_filters,
            "af_filters": "loudnorm=I=-16:TP=-1.5:LRA=11",  # Sensible default for technical edits
            "metadata": {
                "mood": director_out.get("mood", user_requirements.get("mood", "professional")),
                "pacing": director_out.get("pacing", user_requirements.get("pacing", "medium")),
                "color_palette": director_out.get("color_palette", "natural")
            }
        }

        logger.info("openclaw_strategy_generated", job_id=job_id)
        return strategy

openclaw_service = OpenClawService()

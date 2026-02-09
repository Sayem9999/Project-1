"""
QC Gate Node - AI quality check before rendering.
Uses separate critic model to evaluate output quality.
"""
import structlog
from typing import Dict, Any, Optional
from dataclasses import dataclass

from ..state import GraphState
from ...agents.base import run_agent_with_schema
from ...agents.schemas import QCOutput
from ...agents.routing_policy import provider_router, RoutingPolicy

logger = structlog.get_logger()


# QC prompt for quality assessment
QC_GATE_PROMPT = """You are THE PRODUCER - the final quality gatekeeper before rendering.

Review the complete edit plan and determine if it is ready for rendering.

**Evaluation Criteria:**
1. **Coherence**: Do cuts flow logically? Is pacing consistent?
2. **Technical Quality**: Are all timings valid? No overlaps or gaps?
3. **Audio Balance**: Is speech clear? Music not overpowering?
4. **Visual Consistency**: Do effects match the mood? Colors harmonious?
5. **Client Alignment**: Does output match the original request?

**Input:**
- User Request: {user_request}
- Director Plan: {director_plan}
- Cuts: {cuts_count} segments
- Visual Effects: {effects_count} effects
- Audio Tracks: {audio_count} tracks
- Validation Errors: {validation_errors}
- Validation Warnings: {validation_warnings}

**Output Requirements:**
Return JSON with:
- approved: boolean (true if ready to render)
- score: 1-10 quality rating
- verdict: one-line summary
- issues: list of specific issues found
- suggestions: list of improvement suggestions
"""


@dataclass
class QCGateConfig:
    """Configuration for QC gate."""
    min_score: int = 6
    max_retries: int = 1
    block_on_validation_errors: bool = True


class QCGate:
    """
    Quality gate that blocks rendering if quality is insufficient.
    """
    
    def __init__(self, config: QCGateConfig = None):
        self.config = config or QCGateConfig()
    
    async def evaluate(self, state: GraphState) -> Dict[str, Any]:
        """Evaluate the edit plan quality."""
        job_id = state.get("job_id", 0)
        
        # Check for validation errors first
        validation_result = state.get("validation_result", {})
        validation_errors = validation_result.get("errors", [])
        validation_warnings = validation_result.get("warnings", [])
        
        # Block immediately if there are validation errors
        if validation_errors and self.config.block_on_validation_errors:
            logger.warning(
                "qc_gate_blocked_validation",
                job_id=job_id,
                error_count=len(validation_errors)
            )
            return {
                "approved": False,
                "score": 0,
                "verdict": "Blocked due to validation errors",
                "issues": validation_errors,
                "suggestions": ["Fix validation errors before rendering"]
            }
        
        # Build context for QC agent
        payload = {
            "user_request": state.get("user_request", {}),
            "director_plan": state.get("director_plan", {}),
            "cuts_count": len(state.get("cuts", [])),
            "effects_count": len(state.get("visual_effects", [])),
            "audio_count": len(state.get("audio_tracks", [])),
            "validation_errors": validation_errors,
            "validation_warnings": validation_warnings
        }
        
        try:
            # Use QC-specific provider (separate from main agents)
            qc_provider = provider_router.get_qc_provider()
            model = qc_provider.models[0] if qc_provider else "gemini-1.5-flash"
            
            result = await run_agent_with_schema(
                system_prompt=QC_GATE_PROMPT,
                payload=payload,
                schema=QCOutput,
                agent_name="qc_gate",
                job_id=job_id,
                model=model
            )
            
            qc_result = result.model_dump()
            
            # Apply minimum score threshold
            if qc_result.get("score", 0) < self.config.min_score:
                qc_result["approved"] = False
                if "Score below threshold" not in qc_result.get("verdict", ""):
                    qc_result["verdict"] = f"Score {qc_result.get('score')}/10 below minimum {self.config.min_score}"
            
            logger.info(
                "qc_gate_complete",
                job_id=job_id,
                approved=qc_result.get("approved"),
                score=qc_result.get("score")
            )
            
            return qc_result
            
        except Exception as e:
            logger.error("qc_gate_failed", job_id=job_id, error=str(e))
            # On error, allow rendering but flag it
            return {
                "approved": True,
                "score": 5,
                "verdict": "QC evaluation failed, proceeding with caution",
                "issues": [f"QC error: {str(e)}"],
                "suggestions": ["Manual review recommended"]
            }


# Global gate instance
qc_gate = QCGate()


async def qc_gate_node(state: GraphState) -> Dict[str, Any]:
    """
    LangGraph node for QC gate evaluation.
    """
    logger.info("qc_gate_node_start", job_id=state.get("job_id"))
    
    result = await qc_gate.evaluate(state)
    
    # Add to errors if not approved
    new_errors = state.get("errors", []).copy()
    if not result.get("approved"):
        new_errors.append(f"QC Gate: {result.get('verdict')}")
    
    return {
        "errors": new_errors,
        "qc_result": result
    }

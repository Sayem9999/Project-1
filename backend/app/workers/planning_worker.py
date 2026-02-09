"""
Planning Worker - Dedicated Celery worker for AI planning tasks.
Separates AI planning from rendering for better resource management.
"""
from celery import Celery
from celery.utils.log import get_task_logger
import structlog
from typing import Dict, Any, Optional

from ..celery_app import celery_app
from ..graph.workflow import app as langgraph_app
from ..agents.artifacts import ArtifactStore, EditPlan

logger = structlog.get_logger()
celery_logger = get_task_logger(__name__)


@celery_app.task(
    name="planning.run_full_planning",
    bind=True,
    max_retries=2,
    default_retry_delay=30,
    queue="planning",  # Dedicated planning queue
    priority=5  # Default priority
)
def run_full_planning(
    self,
    job_id: int,
    source_path: str,
    user_request: Dict[str, Any],
    tier: str = "standard"
) -> Dict[str, Any]:
    """
    Run the full AI planning pipeline.
    Returns the EditPlan ready for rendering.
    """
    celery_logger.info(f"Starting planning for job {job_id}")
    
    # Adjust priority based on tier
    priority = get_tier_priority(tier)
    
    try:
        # Create initial state
        initial_state = {
            "job_id": job_id,
            "source_path": source_path,
            "user_request": user_request,
            "tier": tier,
            "errors": [],
            "validation_result": None,
            "qc_result": None,
            "retry_count": 0,
        }
        
        # Run LangGraph workflow
        final_state = langgraph_app.invoke(initial_state)
        
        # Check for QC approval
        qc_result = final_state.get("qc_result", {})
        if not qc_result.get("approved", False):
            celery_logger.warning(f"Job {job_id} failed QC: {qc_result.get('verdict')}")
            return {
                "success": False,
                "job_id": job_id,
                "stage": "qc_gate",
                "error": qc_result.get("verdict", "QC not approved"),
                "qc_score": qc_result.get("score", 0)
            }
        
        # Save artifacts
        artifact_store = ArtifactStore()
        edit_plan = EditPlan(job_id=job_id, completed=False)
        
        for stage in ["director_plan", "cuts", "visual_effects", "audio_tracks"]:
            if final_state.get(stage):
                artifact_store.save_stage(job_id, stage, final_state[stage], edit_plan)
        
        celery_logger.info(f"Planning complete for job {job_id}")
        
        return {
            "success": True,
            "job_id": job_id,
            "edit_plan_path": artifact_store._get_plan_path(job_id),
            "qc_score": qc_result.get("score", 10),
            "ready_for_render": True
        }
        
    except Exception as e:
        celery_logger.error(f"Planning failed for job {job_id}: {str(e)}")
        
        # Retry with backoff
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        
        return {
            "success": False,
            "job_id": job_id,
            "stage": "planning",
            "error": str(e)
        }


@celery_app.task(
    name="planning.run_partial_planning",
    bind=True,
    queue="planning",
    priority=5
)
def run_partial_planning(
    self,
    job_id: int,
    stage: str,
    payload: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Run a single planning stage (for resume scenarios).
    """
    from ..agents.base import run_agent_with_schema
    from ..agents.schemas import AGENT_SCHEMAS
    
    celery_logger.info(f"Running {stage} for job {job_id}")
    
    try:
        schema = AGENT_SCHEMAS.get(stage)
        if not schema:
            return {"success": False, "error": f"Unknown stage: {stage}"}
        
        # This would need the appropriate prompt for each stage
        result = run_agent_with_schema(
            system_prompt="",  # Would need stage-specific prompt
            payload=payload,
            schema=schema,
            agent_name=stage,
            job_id=job_id
        )
        
        return {
            "success": True,
            "job_id": job_id,
            "stage": stage,
            "result": result.model_dump()
        }
        
    except Exception as e:
        celery_logger.error(f"Stage {stage} failed for job {job_id}: {str(e)}")
        return {
            "success": False,
            "job_id": job_id,
            "stage": stage,
            "error": str(e)
        }


def get_tier_priority(tier: str) -> int:
    """
    Get Celery task priority based on subscription tier.
    Higher number = higher priority.
    """
    priorities = {
        "enterprise": 9,
        "pro": 7,
        "standard": 5,
        "free": 3,
    }
    return priorities.get(tier, 5)

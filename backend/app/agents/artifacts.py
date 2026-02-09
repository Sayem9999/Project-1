"""
Artifact Persistence Module - Typed EditPlan and stage artifact storage.
Enables resume-from-last-artifact on pipeline failures.
"""
import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional, Any
from datetime import datetime
import structlog
from pathlib import Path

from .schemas import (
    DirectorOutput, CutterOutput, ColorOutput, AudioOutput,
    QCOutput, ScriptOutput, TransitionOutput, ThumbnailOutput,
    HookOutput, PlatformOutput, BrandSafetyOutput, ABTestOutput
)

logger = structlog.get_logger()


@dataclass
class EditPlan:
    """
    Typed workflow contract for the video editing pipeline.
    Each stage populates its corresponding field.
    Enables checkpointing and resume-from-failure.
    """
    job_id: int
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Stage outputs (None = not yet executed)
    director_plan: Optional[dict] = None
    cuts: Optional[dict] = None
    color_grade: Optional[dict] = None
    audio_plan: Optional[dict] = None
    qc_result: Optional[dict] = None
    script: Optional[dict] = None
    transitions: Optional[dict] = None
    thumbnail: Optional[dict] = None
    
    # New specialist stages
    hook: Optional[dict] = None
    platform_adaptation: Optional[dict] = None
    brand_safety: Optional[dict] = None
    ab_variants: Optional[dict] = None
    
    # Metadata
    current_stage: str = "init"
    failed_stage: Optional[str] = None
    error_message: Optional[str] = None
    completed: bool = False
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "EditPlan":
        """Create EditPlan from dictionary."""
        return cls(**data)


class ArtifactStore:
    """
    Persistent storage for pipeline stage artifacts.
    Supports local filesystem and can be extended for cloud storage.
    """
    
    def __init__(self, base_path: str = "storage/artifacts"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _job_path(self, job_id: int) -> Path:
        """Get the artifact directory for a job."""
        path = self.base_path / str(job_id)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def save_stage(
        self, 
        job_id: int, 
        stage: str, 
        data: Any,
        edit_plan: Optional[EditPlan] = None
    ) -> str:
        """
        Save a stage artifact to disk.
        
        Returns: Path to saved artifact
        """
        job_path = self._job_path(job_id)
        artifact_path = job_path / f"{stage}.json"
        
        # Convert Pydantic models to dict
        if hasattr(data, "model_dump"):
            data = data.model_dump()
        
        with open(artifact_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(
            "artifact_saved",
            job_id=job_id,
            stage=stage,
            path=str(artifact_path)
        )
        
        # Update EditPlan if provided
        if edit_plan:
            setattr(edit_plan, stage.replace('-', '_'), data)
            edit_plan.current_stage = stage
            self.save_edit_plan(job_id, edit_plan)
        
        return str(artifact_path)
    
    def load_stage(self, job_id: int, stage: str) -> Optional[dict]:
        """Load a stage artifact from disk."""
        artifact_path = self._job_path(job_id) / f"{stage}.json"
        
        if not artifact_path.exists():
            return None
        
        with open(artifact_path, "r") as f:
            return json.load(f)
    
    def save_edit_plan(self, job_id: int, edit_plan: EditPlan) -> str:
        """Save the complete EditPlan."""
        job_path = self._job_path(job_id)
        plan_path = job_path / "edit_plan.json"
        
        with open(plan_path, "w") as f:
            json.dump(edit_plan.to_dict(), f, indent=2, default=str)
        
        return str(plan_path)
    
    def load_edit_plan(self, job_id: int) -> Optional[EditPlan]:
        """Load an existing EditPlan for resume."""
        plan_path = self._job_path(job_id) / "edit_plan.json"
        
        if not plan_path.exists():
            return None
        
        with open(plan_path, "r") as f:
            data = json.load(f)
        
        logger.info("edit_plan_loaded", job_id=job_id)
        return EditPlan.from_dict(data)
    
    def get_last_valid_stage(self, job_id: int) -> Optional[str]:
        """
        Find the last successfully completed stage.
        Used for resume-from-failure.
        """
        edit_plan = self.load_edit_plan(job_id)
        if not edit_plan:
            return None
        
        # Stage order
        stages = [
            "director_plan", "cuts", "color_grade", "audio_plan",
            "script", "transitions", "thumbnail", "qc_result",
            "hook", "platform_adaptation", "brand_safety", "ab_variants"
        ]
        
        last_valid = None
        for stage in stages:
            if getattr(edit_plan, stage, None) is not None:
                last_valid = stage
            else:
                break
        
        return last_valid
    
    def mark_failed(self, job_id: int, stage: str, error: str) -> None:
        """Mark a stage as failed in the EditPlan."""
        edit_plan = self.load_edit_plan(job_id)
        if edit_plan:
            edit_plan.failed_stage = stage
            edit_plan.error_message = error
            self.save_edit_plan(job_id, edit_plan)
            
            logger.error(
                "pipeline_stage_failed",
                job_id=job_id,
                stage=stage,
                error=error
            )


# Global store instance
artifact_store = ArtifactStore()

"""
Render Worker - Dedicated Celery worker for FFmpeg rendering.
Separates rendering from AI planning for better resource isolation.
"""
from celery import Celery
from celery.utils.log import get_task_logger
import structlog
from typing import Dict, Any, Optional
from pathlib import Path
import time

from ..celery_app import celery_app
from ..services.timeline_dsl import Timeline, from_graph_state
from ..services.ffmpeg_compiler import FFmpegCompiler
from ..services.gpu_capabilities import gpu_detector
from ..agents.artifacts import ArtifactStore

logger = structlog.get_logger()
celery_logger = get_task_logger(__name__)


@celery_app.task(
    name="render.execute_render",
    bind=True,
    max_retries=1,
    default_retry_delay=60,
    queue="render",  # Dedicated render queue
    priority=5,
    time_limit=1800,  # 30 minute hard limit
    soft_time_limit=1500  # 25 minute soft limit
)
def execute_render(
    self,
    job_id: int,
    edit_plan_path: str,
    output_path: str,
    tier: str = "standard"
) -> Dict[str, Any]:
    """
    Execute FFmpeg rendering from an approved EditPlan.
    """
    celery_logger.info(f"Starting render for job {job_id}")
    start_time = time.time()
    
    try:
        # Load edit plan
        artifact_store = ArtifactStore()
        edit_plan = artifact_store.load_edit_plan(job_id)
        
        if not edit_plan:
            return {
                "success": False,
                "job_id": job_id,
                "error": "Edit plan not found"
            }
        
        # Convert to timeline DSL
        state = {
            "job_id": job_id,
            "source_path": edit_plan.source_path if hasattr(edit_plan, 'source_path') else "",
            "cuts": edit_plan.cuts or [],
            "visual_effects": edit_plan.visual_effects or [],
            "audio_tracks": edit_plan.audio_tracks or [],
            "director_plan": edit_plan.director_plan or {},
        }
        
        timeline = from_graph_state(state)
        
        # Get GPU-optimized compiler
        gpu_caps = gpu_detector.get_capabilities()
        compiler = FFmpegCompiler()
        
        # Compile and execute
        result = compiler.execute(timeline, output_path)
        
        render_time = time.time() - start_time
        
        if result["success"]:
            celery_logger.info(f"Render complete for job {job_id} in {render_time:.1f}s")
            
            # Mark edit plan as complete
            edit_plan.completed = True
            artifact_store.save_edit_plan(job_id, edit_plan)
            
            return {
                "success": True,
                "job_id": job_id,
                "output_path": output_path,
                "render_time_seconds": round(render_time, 2),
                "gpu_used": gpu_caps.has_gpu,
                "encoder": gpu_caps.recommended_encoder
            }
        else:
            celery_logger.error(f"Render failed for job {job_id}: {result.get('error')}")
            return {
                "success": False,
                "job_id": job_id,
                "error": result.get("error"),
                "cmd": result.get("cmd")
            }
        
    except Exception as e:
        celery_logger.error(f"Render exception for job {job_id}: {str(e)}")
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        
        return {
            "success": False,
            "job_id": job_id,
            "error": str(e)
        }


@celery_app.task(
    name="render.generate_thumbnail",
    bind=True,
    queue="render",
    priority=3  # Lower priority than main renders
)
def generate_thumbnail(
    self,
    job_id: int,
    video_path: str,
    output_path: str,
    timestamp: float = 5.0
) -> Dict[str, Any]:
    """
    Generate thumbnail from rendered video.
    """
    import subprocess
    
    celery_logger.info(f"Generating thumbnail for job {job_id}")
    
    try:
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(timestamp),
            "-i", video_path,
            "-vframes", "1",
            "-q:v", "2",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            return {
                "success": True,
                "job_id": job_id,
                "thumbnail_path": output_path
            }
        else:
            return {
                "success": False,
                "job_id": job_id,
                "error": result.stderr
            }
            
    except Exception as e:
        return {
            "success": False,
            "job_id": job_id,
            "error": str(e)
        }


@celery_app.task(
    name="render.generate_preview",
    bind=True,
    queue="render",
    priority=4
)
def generate_preview(
    self,
    job_id: int,
    video_path: str,
    output_path: str,
    max_duration: int = 30
) -> Dict[str, Any]:
    """
    Generate preview clip from rendered video.
    """
    import subprocess
    
    celery_logger.info(f"Generating preview for job {job_id}")
    
    try:
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-t", str(max_duration),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "28",
            "-c:a", "aac",
            "-b:a", "128k",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            return {
                "success": True,
                "job_id": job_id,
                "preview_path": output_path
            }
        else:
            return {
                "success": False,
                "job_id": job_id,
                "error": result.stderr
            }
            
    except Exception as e:
        return {
            "success": False,
            "job_id": job_id,
            "error": str(e)
        }


def get_render_priority(tier: str, is_priority: bool = False) -> int:
    """
    Get render priority based on tier and urgency.
    """
    base_priorities = {
        "enterprise": 9,
        "pro": 7,
        "standard": 5,
        "free": 3,
    }
    priority = base_priorities.get(tier, 5)
    
    if is_priority:
        priority = min(10, priority + 2)
    
    return priority

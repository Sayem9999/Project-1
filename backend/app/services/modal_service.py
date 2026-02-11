import os
import structlog
from typing import List, Dict, Any, Optional
from ..config import settings
from .storage_service import storage_service

logger = structlog.get_logger()

class ModalService:
    """
    Handles offloading heavy tasks to Modal GPU runners.
    """
    
    def __init__(self):
        self.enabled = bool(settings.modal_token_id and settings.modal_token_secret)
        if not self.enabled:
            logger.info("modal_service_disabled", reason="Missing credentials")

    async def render_video(
        self,
        job_id: int,
        source_path: str,
        cuts: List[Dict[str, Any]],
        fps: int = 24,
        crf: int = 18
    ) -> Optional[str]:
        """
        Offloads rendering to Modal.
        Returns the output path (on R2) if successful.
        """
        if not self.enabled:
            return None
            
        try:
            import modal
            
            # 1. Ensure source is on R2
            # Modal worker needs a URL to download the file.
            if not source_path.startswith("http"):
                logger.info("modal_uploading_source", job_id=job_id)
                source_url = await storage_service.upload_file(source_path, folder="temp_modal")
            else:
                source_url = source_path
                
            # 2. Lookup Modal Function
            # Note: The function must be deployed with 'modal deploy modal_worker.py'
            f = modal.Function.lookup("proedit-worker", "render_video_v1")
            
            # 3. Trigger remote execution
            # We pass the R2 URL to the worker.
            output_key = f"outputs/job-{job_id}-pro.mp4"
            
            logger.info("modal_trigger_render", job_id=job_id, gpu="T4")
            
            # Use call() for blocking execution (since compiler_node is async anyway)
            remote_key = f.remote(
                job_id=job_id,
                source_url=source_url,
                cuts=cuts,
                output_key=output_key,
                fps=fps,
                crf=crf
            )
            
            # 4. Construct the output URL
            if settings.r2_public_url:
                return f"{settings.r2_public_url}/{remote_key}"
            
            # Fallback to local path representation if that's what the system expects
            return f"storage/{remote_key}"
            
        except Exception as e:
            logger.error("modal_render_failed", job_id=job_id, error=str(e))
            return None

# Singleton
modal_service = ModalService()

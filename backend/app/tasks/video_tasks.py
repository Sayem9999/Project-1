"""
Video Processing Celery Task
Wrapper around workflow engine for background execution
"""
import asyncio
import os
import redis
import json
from ..celery_app import celery_app
from ..services.workflow_engine import process_job

# Redis for progress pub/sub
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


def get_redis():
    """Get Redis client for progress updates."""
    return redis.from_url(REDIS_URL)


def publish_progress(job_id: int, status: str, message: str, progress: int = 0):
    """Publish job progress to Redis for WebSocket streaming."""
    try:
        r = get_redis()
        data = json.dumps({
            "job_id": job_id,
            "status": status,
            "message": message,
            "progress": progress
        })
        r.publish(f"job:{job_id}:progress", data)
        # Also store latest state for clients that connect late
        r.setex(f"job:{job_id}:latest", 3600, data)
    except Exception as e:
        print(f"[Redis] Publish error: {e}")


@celery_app.task(bind=True, max_retries=2)
def process_video_task(self, job_id: int, source_path: str, pacing: str = "medium", mood: str = "professional", ratio: str = "16:9"):
    """
    Celery task for video processing.
    Wraps the async workflow engine.
    """
    publish_progress(job_id, "processing", "Starting video processing...", 5)
    
    try:
        # Run the async workflow in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                process_job(job_id, source_path, pacing, mood, ratio)
            )
            publish_progress(job_id, "complete", "Video processing complete!", 100)
            return {"status": "complete", "job_id": job_id}
        finally:
            loop.close()
            
    except Exception as e:
        publish_progress(job_id, "failed", f"Processing failed: {str(e)}", 0)
        raise self.retry(exc=e, countdown=30)

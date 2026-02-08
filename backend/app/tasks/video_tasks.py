"""
Video Processing Celery Task
Wrapper around workflow engine for background execution
"""
import asyncio
import os
import json

# Redis for progress pub/sub
REDIS_URL = os.getenv("REDIS_URL")


def get_redis():
    """Get Redis client for progress updates with SSL support."""
    if not REDIS_URL:
        return None
    import redis
    # decode_responses for cleaner string handling
    return redis.from_url(REDIS_URL, decode_responses=True)


def publish_progress(job_id: int, status: str, message: str, progress: int = 0):
    """Publish job progress to Redis for WebSocket streaming."""
    try:
        r = get_redis()
        if not r:
            return
        data = json.dumps({
            "job_id": job_id,
            "status": status,
            "message": message,
            "progress": progress
        })
        r.publish(f"job:{job_id}:progress", data)
        r.setex(f"job:{job_id}:latest", 3600, data)
    except Exception as e:
        print(f"[Redis] Publish error: {e}")


# Lazy import Celery to avoid import errors when Redis is not configured
def get_celery_app():
    from ..celery_app import celery_app
    return celery_app


# Only define task if we can import Celery
try:
    celery_app = get_celery_app()
    
    @celery_app.task(bind=True, max_retries=2)
    def process_video_task(self, job_id: int, source_path: str, pacing: str = "medium", mood: str = "professional", ratio: str = "16:9"):
        """
        Celery task for video processing.
        Wraps the async workflow engine.
        """
        publish_progress(job_id, "processing", "Starting video processing...", 5)
        
        try:
            from ..services.workflow_engine import process_job
            
            # Run the async workflow in a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(
                    process_job(job_id, source_path, pacing, mood, ratio)
                )
                publish_progress(job_id, "complete", "Video processing complete!", 100)
                return {"status": "complete", "job_id": job_id}
            finally:
                loop.close()
                
        except Exception as e:
            publish_progress(job_id, "failed", f"Processing failed: {str(e)}", 0)
            raise self.retry(exc=e, countdown=30)

except Exception as e:
    print(f"[Celery] Could not initialize: {e}")
    process_video_task = None

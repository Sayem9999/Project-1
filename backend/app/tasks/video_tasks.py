"""
Video Processing Celery Task
Wrapper around workflow engine for background execution
"""
import asyncio
import os
import json

from ..config import settings

# Redis for progress pub/sub
REDIS_URL = settings.redis_url


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
    def process_video_task(
        self,
        job_id: int,
        source_path: str,
        pacing: str = "medium",
        mood: str = "professional",
        ratio: str = "16:9",
        tier: str = "pro",
        platform: str = "youtube",
        brand_safety: str = "standard",
    ):
        """
        Celery task for video processing.
        Wraps the async workflow engine.
        """
        # Inject version info into worker stats for API visibility
        try:
            from celery.signals import worker_ready
            @worker_ready.connect
            def on_worker_ready(sender, **kwargs):
                from ..config import settings
                sender.app.control.broadcast('rate_limit', arguments={'task_name': 'app.tasks.video_tasks.process_video_task', 'rate_limit': '10/m'})
                # We can't easily push to stats() here, but we can verify on start
                print(f"[Worker] Version: {settings.code_version}")
        except:
            pass
            
        from ..services.worker_heartbeat import update_worker_heartbeat
        update_worker_heartbeat()
        
        publish_progress(job_id, "processing", f"Starting video processing ({tier})...", 5)
        
        try:
            from ..services.workflow_engine import process_job
            asyncio.run(process_job(
                job_id,
                source_path,
                pacing=pacing,
                mood=mood,
                ratio=ratio,
                tier=tier, 
                platform=platform,
                brand_safety=brand_safety
            ))
        except Exception as e:
            print(f"[Celery] Task execution failed: {e}")
            publish_progress(job_id, "failed", f"Task execution failed: {str(e)}", 0)
            raise e

except Exception as e:
    print(f"[Celery] Could not initialize: {e}")
    process_video_task = None

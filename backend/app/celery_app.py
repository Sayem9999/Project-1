"""
Celery Application Configuration
Background task processing with Redis broker
"""
import os
import ssl
from celery import Celery

# Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    # Fallback or disable if not present
    REDIS_URL = "redis://localhost:6379/0"

celery_app = Celery(
    "proedit",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.video_tasks"]
)

if REDIS_URL.startswith("rediss://"):
    celery_app.conf.update(
        broker_use_ssl={
            "ssl_cert_reqs": ssl.CERT_NONE
        },
        redis_backend_use_ssl={
            "ssl_cert_reqs": ssl.CERT_NONE
        }
    )

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 min max per task
    worker_prefetch_multiplier=1,  # One task at a time per worker
    task_acks_late=True,  # Acknowledge after completion
)

# Optional: Task routes for different queues
celery_app.conf.task_routes = {
    "app.tasks.video_tasks.process_video_task": {"queue": "video"},
}

"""
Celery Application Configuration
Background task processing with Redis broker
"""
import os
import ssl
from celery import Celery

from app.config import settings

# Redis URL from settings
REDIS_URL = settings.redis_url or "redis://localhost:6379/0"

celery_app = Celery(
    "proedit",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.video_tasks"]
)

if REDIS_URL.startswith("rediss://"):
    cert_reqs = os.getenv("REDIS_SSL_CERT_REQS", "none").strip().lower()
    cert_map = {
        "none": ssl.CERT_NONE,
        "optional": ssl.CERT_OPTIONAL,
        "required": ssl.CERT_REQUIRED,
    }
    ssl_kwargs = {
        "ssl_cert_reqs": cert_map.get(cert_reqs, ssl.CERT_NONE),
    }
    ca_certs = os.getenv("REDIS_SSL_CA_CERTS")
    if ca_certs:
        ssl_kwargs["ssl_ca_certs"] = ca_certs
    celery_app.conf.update(
        broker_use_ssl=ssl_kwargs,
        redis_backend_use_ssl=ssl_kwargs,
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

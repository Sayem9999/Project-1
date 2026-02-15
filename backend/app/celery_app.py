"""
Celery Application Configuration
Simplified for local stability.
"""
import os
import ssl
from celery import Celery
from app.config import settings

REDIS_URL = settings.redis_url or "redis://localhost:6379/0"

celery_app = Celery(
    "proedit",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.video_tasks"]
)

if REDIS_URL.startswith("rediss://"):
    ssl_kwargs = {
        "ssl_cert_reqs": ssl.CERT_NONE,
    }
    celery_app.conf.update(
        broker_use_ssl=ssl_kwargs,
        redis_backend_use_ssl=ssl_kwargs,
        # Upstash specific stability settings
        broker_transport_options={
            "socket_timeout": 10,
            "socket_connect_timeout": 10,
            "retry_on_timeout": True,
            "visibility_timeout": 3600
        },
        redis_backend_transport_options={
            "socket_timeout": 10,
            "retry_on_timeout": True
        }
    )

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    broker_pool_limit=1,
    # Standard queue visibility timeout (auto-release stuck tasks after 1 hour)
    broker_transport_options={
        "visibility_timeout": 3600,
        "socket_timeout": 15,
        "socket_connect_timeout": 15,
    },
)

celery_app.conf.task_routes = {
    "app.tasks.video_tasks.process_video_task": {"queue": settings.celery_video_queue or "video"},
}

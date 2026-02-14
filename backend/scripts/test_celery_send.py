import os
import ssl
from celery import Celery

REDIS_URL = "rediss://default:AcT1AAIncDJjMmUyYmRiZjRjMzc0YzVhYmYwNTViYWQ1YWEzZjJhZHAyNTA0MjE@safe-stallion-50421.upstash.io:6379"

app = Celery("tester", broker=REDIS_URL)

ssl_kwargs = {
    "ssl_cert_reqs": ssl.CERT_NONE,
}
app.conf.update(
    broker_use_ssl=ssl_kwargs,
    broker_connection_retry_on_startup=True
)

print("Attempting to send ping task...")
try:
    # Just a test task name that doesn't need to exist
    app.send_task("test_ping", args=[], queue="video_local")
    print("Task sent successfully!")
except Exception as e:
    print(f"Failed to send task: {e}")

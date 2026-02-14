import asyncio
from app.config import settings
from app.routers.jobs import USE_CELERY, get_celery_dispatch_diagnostics

async def check_api_env():
    print("--- API Celery Diagnostic ---")
    print(f"USE_CELERY: {USE_CELERY}")
    print(f"REDIS_URL: {settings.redis_url}")
    print(f"Configured Queue: {settings.celery_video_queue}")
    
    print("\nAttempting to reach workers...")
    diag = get_celery_dispatch_diagnostics(timeout=2.0)
    print(f"Diagnostics: {diag}")

if __name__ == "__main__":
    asyncio.run(check_api_env())

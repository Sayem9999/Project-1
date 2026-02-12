from app.tasks.video_tasks import process_video_task
from app.config import settings

def test_dispatch():
    print(f"Attempting to dispatch task to: {settings.redis_url[:20]}...")
    try:
        # Just send a dummy task (it will fail in worker if IDs don't exist, but we want to see if it DISPATCHES)
        task = process_video_task.apply_async(
            args=[999, "dummy.mp4", "medium", "professional", "16:9", "pro", "youtube", "standard"],
            queue="video_local"
        )
        print(f"[OK] Task dispatched! Task ID: {task.id}")
    except Exception as e:
        print(f"[FAIL] Dispatch failed: {e}")

if __name__ == "__main__":
    test_dispatch()

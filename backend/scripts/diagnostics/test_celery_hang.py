import os
import time
from app.config import settings
from app.routers.jobs import get_celery_dispatch_diagnostics

def test_celery_hang():
    print("--- Testing Celery Diagnostics ---")
    start = time.perf_counter()
    try:
        print("Calling get_celery_dispatch_diagnostics(timeout=1.5)...")
        # Note: This is a synchronous call in the codebase
        result = get_celery_dispatch_diagnostics(timeout=1.5)
        print(f"Result: {result}")
        print(f"Time taken: {time.perf_counter() - start:.2f}s")
    except Exception as e:
        print(f"Celery Error: {e}")

if __name__ == "__main__":
    import sys
    sys.path.append(os.getcwd())
    test_celery_hang()

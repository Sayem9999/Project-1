import asyncio
import time
import os
import sys

# Add backend to path
sys.path.append(os.getcwd())

from app.services.integration_health import get_integration_health
from app.services.llm_health import get_llm_health_summary
from app.routers.jobs import get_celery_dispatch_diagnostics
from app.services.storage_service import storage_service
from app.tasks.cleanup import get_cleanup_status

async def test_timings():
    print("--- Admin Health Diagnostic Timings ---")
    
    # 1. Celery (Async)
    start = time.perf_counter()
    print("Checking Celery...")
    try:
        # Note: I converted this to async earlier
        res = await get_celery_dispatch_diagnostics(timeout=1.5)
        print(f"Celery OK ({time.perf_counter() - start:.2f}s)")
    except Exception as e:
        print(f"Celery FAILED ({time.perf_counter() - start:.2f}s): {e}")

    # 2. Integration Health (Sync)
    start = time.perf_counter()
    print("Checking Integrations (Modal/R2)...")
    try:
        res = get_integration_health(run_probe=False)
        print(f"Integrations OK ({time.perf_counter() - start:.2f}s)")
    except Exception as e:
        print(f"Integrations FAILED ({time.perf_counter() - start:.2f}s): {e}")

    # 3. LLM Health (Sync)
    start = time.perf_counter()
    print("Checking LLM Health...")
    try:
        res = get_llm_health_summary()
        print(f"LLM Health OK ({time.perf_counter() - start:.2f}s)")
    except Exception as e:
        print(f"LLM Health FAILED ({time.perf_counter() - start:.2f}s): {e}")

    # 4. Storage Usage (Sync)
    start = time.perf_counter()
    print("Checking Storage Usage...")
    try:
        res = storage_service.get_storage_usage()
        print(f"Storage OK ({time.perf_counter() - start:.2f}s)")
    except Exception as e:
        print(f"Storage FAILED ({time.perf_counter() - start:.2f}s): {e}")

if __name__ == "__main__":
    asyncio.run(test_timings())

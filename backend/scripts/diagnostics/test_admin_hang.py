import asyncio
import os
import time
import sys
from app.config import settings
from app.services.storage_service import storage_service

async def test_storage_usage():
    print("\n--- Testing Storage Usage ---")
    start = time.perf_counter()
    try:
        print(f"R2 Configured: {storage_service.use_r2}")
        if storage_service.use_r2:
            print(f"Bucket: {storage_service.bucket}")
            print(f"Endpoint: https://{settings.r2_account_id}.r2.cloudflarestorage.com")
        
        print("Calling get_storage_usage()...")
        # Since it's a sync call in the service, we'll try to run it with a timeout if it was async, 
        # but since it's sync, it will just block.
        usage = storage_service.get_storage_usage()
        print(f"Usage: {usage}")
        print(f"Time taken: {time.perf_counter() - start:.2f}s")
    except Exception as e:
        print(f"Storage Usage Error: {e}")

async def test_modal_health():
    print("\n--- Testing Modal Health ---")
    from app.services.integration_health import check_modal_lookup
    start = time.perf_counter()
    try:
        print("Calling check_modal_lookup()...")
        result = check_modal_lookup()
        print(f"Result: {result}")
        print(f"Time taken: {time.perf_counter() - start:.2f}s")
    except Exception as e:
        print(f"Modal Health Error: {e}")

if __name__ == "__main__":
    sys.path.append(os.getcwd())
    asyncio.run(test_storage_usage())
    asyncio.run(test_modal_health())

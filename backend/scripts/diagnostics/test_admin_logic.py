import asyncio
import os
import time
from app.db import SessionLocal
from app.models import User
from sqlalchemy import select
from app.routers.admin import get_admin_health, get_admin_stats
from app.routers.jobs import get_celery_dispatch_diagnostics
from app.services.integration_health import get_integration_health
from app.services.storage_service import storage_service

async def test_admin_health():
    print("--- Testing Admin Health Logic ---")
    try:
        print("Testing celery diagnostics...")
        celery = get_celery_dispatch_diagnostics(timeout=1.5)
        print("Celery diagnostics OK")
        
        print("Testing storage usage...")
        storage = storage_service.get_storage_usage()
        print("Storage usage OK")
        
        print("Testing integration health (no probe)...")
        integrations = get_integration_health(run_probe=False)
        print("Integrations health OK")
        
        print("Testing admin health endpoint logic...")
        async with SessionLocal() as session:
            # Mock current user
            class MockUser:
                id = 1
                is_admin = True
            
            health = await get_admin_health(session, MockUser())
            print("Admin health OK")
            
    except Exception as e:
        print(f"ERROR: {e}")

async def test_admin_stats():
    print("\n--- Testing Admin Stats Logic ---")
    try:
        async with SessionLocal() as session:
            class MockUser:
                id = 1
                is_admin = True
            
            stats = await get_admin_stats(session, MockUser())
            print("Admin stats OK")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    # Manually append current dir to sys.path if needed
    import sys
    sys.path.append(os.getcwd())
    asyncio.run(test_admin_health())
    asyncio.run(test_admin_stats())

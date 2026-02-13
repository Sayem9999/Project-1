import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_path = Path("backend").absolute()
sys.path.append(str(backend_path))

# Mock environment for settings
os.environ["SECRET_KEY"] = "dummy_secret_for_testing"
db_path = backend_path / "storage" / "edit_ai.db"
# Ensure directory exists
db_path.parent.mkdir(parents=True, exist_ok=True)
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"

async def verify_db_interaction():
    print(f"Python Version: {sys.version}")
    print(f"Sys Path: {sys.path}")
    try:
        import pydantic_settings
        print(f"pydantic_settings version: {pydantic_settings.__version__}")
    except ImportError as e:
        print(f"Failed to import pydantic_settings: {e}")

    try:
        from app.db import SessionLocal, engine, Base
        from app.models import User, Job, JobStatus
        from sqlalchemy import select, text
        
        print("Initializing database session...")
        
        # Test 1: Simple Select
        async with SessionLocal() as session:
            print("Testing simple SELECT 1...")
            result = await session.execute(text("SELECT 1"))
            print(f"Result: {result.scalar()}")
            
        # Test 2: Model Interaction (Create & Read)
        async with SessionLocal() as session:
            print("Testing Model Create (User)...")
            # Create dummy user
            test_email = f"test_314_{int(datetime.now().timestamp())}@example.com"
            new_user = User(email=test_email, password_hash="dummy")
            session.add(new_user)
            await session.commit()
            print(f"User created with ID: {new_user.id}")
            
            print("Testing Model Create (Job)...")
            new_job = Job(
                user_id=new_user.id,
                source_path="test/path.mp4",
                status=JobStatus.processing,
                media_intelligence={"test": "data"}
            )
            session.add(new_job)
            await session.commit()
            print(f"Job created with ID: {new_job.id}")
            
            print("Testing Model Query (Job with Relations)...")
            stmt = select(Job).where(Job.id == new_job.id)
            result = await session.execute(stmt)
            fetched_job = result.scalar_one()
            print(f"Fetched Job Status: {fetched_job.status}")
            print(f"Fetched Job Intelligence: {fetched_job.media_intelligence}")
            
            # Clean up
            print("Cleaning up...")
            await session.delete(fetched_job)
            await session.delete(new_user)
            await session.commit()
            
        print("SUCCESS: Database interactions passed without crashes.")
        
    except Exception as e:
        print("\nCRITICAL FAILURE: Interaction failed.")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_db_interaction())

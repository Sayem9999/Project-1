import asyncio
import json
import os
from sqlalchemy import select, desc
from app.db import SessionLocal
from app.models import Job

async def inspect_latest_job():
    async with SessionLocal() as session:
        result = await session.execute(
            select(Job).order_by(desc(Job.id)).limit(1)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            print("No jobs found in database.")
            return

        print(f"=== Job #{job.id} Status: {job.status} ===")
        print(f"Created: {job.created_at}")
        print(f"Progress: {job.progress_message}")
        print(f"\n[Media Intelligence]")
        print(json.dumps(job.media_intelligence, indent=2))
        
        print(f"\n[Director Plan]")
        print(json.dumps(job.director_plan, indent=2))
        
        print(f"\n[Cutter Output]")
        # Search for cutter node output in specialist_results or metadata
        print(json.dumps(job.specialist_results.get('cutter', {}) if job.specialist_results else {}, indent=2))
        
        print(f"\n[All Specialist Keys]")
        print(list(job.specialist_results.keys()) if job.specialist_results else [])

if __name__ == "__main__":
    import sys
    # Add backend to path to import app modules
    sys.path.append(os.getcwd())
    asyncio.run(inspect_latest_job())

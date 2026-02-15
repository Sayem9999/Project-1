
import asyncio
from app.db import SessionLocal
from app.models import Job, JobStatus
from sqlalchemy import select

async def fix_jobs():
    async with SessionLocal() as session:
        # Fix Jobs that have files on disk but are marked failed/None in DB
        targets = [96, 95, 79]
        for tid in targets:
            job = await session.get(Job, tid)
            if job:
                print(f"Fixing Job {tid}...")
                job.status = JobStatus.complete
                job.output_path = f"storage/outputs/job-{tid}-pro.mp4"
                job.progress_message = "Pro Edit Ready! (Rescued from crash)"
                session.add(job)
        
        await session.commit()
        print("Jobs updated.")

if __name__ == "__main__":
    asyncio.run(fix_jobs())

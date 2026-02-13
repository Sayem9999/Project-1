import asyncio
from app.db import SessionLocal
from app.models import Job, User
from app.routers.jobs import enqueue_job
from sqlalchemy import select

async def trigger_job(job_id: int):
    async with SessionLocal() as session:
        job = await session.scalar(select(Job).where(Job.id == job_id))
        if not job:
            print("Job not found")
            return
        
        # Simulate API start_job logic
        job.status = "processing"
        job.progress_message = "Manually triggered retry..."
        session.add(job)
        
        await enqueue_job(
            job,
            job.pacing or "medium",
            job.mood or "professional",
            job.ratio or "16:9",
            job.tier or "standard",
            job.platform or "youtube",
            job.brand_safety or "standard",
        )
        await session.commit()
        print(f"Job {job_id} triggered. Check worker logs.")

if __name__ == "__main__":
    asyncio.run(trigger_job(2))

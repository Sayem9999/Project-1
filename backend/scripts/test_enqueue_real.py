import asyncio
from app.db import SessionLocal
from app.models import Job
from app.routers.jobs import enqueue_job

async def test_enqueue():
    async with SessionLocal() as session:
        # Get job 15 (which is currently queued)
        from sqlalchemy import select
        res = await session.execute(select(Job).where(Job.id == 15))
        job = res.scalar_one_or_none()
        
        if not job:
            print("Job 15 not found")
            return
            
        print(f"Attempting to enqueue job {job.id}...")
        try:
            await enqueue_job(
                job,
                job.pacing or "medium",
                job.mood or "professional",
                job.ratio or "16:9",
                job.tier or "pro",
                job.platform or "youtube",
                job.brand_safety or "standard"
            )
            print("Successfully enqueued!")
        except Exception as e:
            print(f"Enqueue failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_enqueue())

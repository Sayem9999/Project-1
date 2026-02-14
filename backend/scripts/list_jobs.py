import asyncio
from sqlalchemy import select
from app.db import SessionLocal
from app.models import Job

async def list_jobs():
    async with SessionLocal() as session:
        result = await session.execute(
            select(Job).order_by(Job.id.desc()).limit(10)
        )
        jobs = result.scalars().all()
        print(f"{'ID':<5} | {'Status':<15} | {'Progress':<30} | {'Tier':<10}")
        print("-" * 70)
        for job in jobs:
            print(f"{job.id:<5} | {job.status:<15} | {str(job.progress_message)[:30]:<30} | {job.tier:<10}")

if __name__ == "__main__":
    asyncio.run(list_jobs())

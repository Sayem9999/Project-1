import asyncio
from sqlalchemy import select
from app.db import SessionLocal
from app.models import Job

async def check_job_details():
    async with SessionLocal() as session:
        result = await session.execute(
            select(Job).where(Job.id.in_([13, 14]))
        )
        jobs = result.scalars().all()
        for job in jobs:
            print(f"ID: {job.id}, Status: {job.status}, Created: {job.created_at}, Updated: {job.updated_at}")
            print(f"Progress: {job.progress_message}")
            print("-" * 40)

if __name__ == "__main__":
    asyncio.run(check_job_details())

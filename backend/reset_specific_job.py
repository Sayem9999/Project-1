import asyncio
from app.db import SessionLocal
from app.models import Job
from sqlalchemy import update

async def reset_job(job_id: int):
    async with SessionLocal() as session:
        await session.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(status='queued', progress_message='Reset for manual retry')
        )
        await session.commit()
        print(f'Job {job_id} reset to queued')

if __name__ == "__main__":
    asyncio.run(reset_job(2))

import asyncio
from app.db import get_session
from app.models import Job, User
from sqlalchemy import select

async def run():
    async for session in get_session():
        res = await session.execute(select(User).order_by(User.id.desc()).limit(2))
        users = res.scalars().all()
        for u in users:
            print(f"User: {u.email}\nCredits: {u.credits}")
            res_jobs = await session.execute(select(Job).where(Job.user_id == u.id).order_by(Job.id.desc()).limit(5))
            jobs = res_jobs.scalars().all()
            for j in jobs:
                print(f"  Job {j.id}: status={j.status}, cost={j.cost}, msg={j.progress_message}")
        break

if __name__ == "__main__":
    asyncio.run(run())

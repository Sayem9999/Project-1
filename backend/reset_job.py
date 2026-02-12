import asyncio
from app.db import get_session
from app.models import Job
from sqlalchemy import update

async def reset():
    async for session in get_session():
        await session.execute(update(Job).where(Job.status == 'failed').values(status='queued', progress_message='Retrying with stability fixes'))
        await session.commit()
        print('Reset failed jobs')
        break

if __name__ == "__main__":
    asyncio.run(reset())

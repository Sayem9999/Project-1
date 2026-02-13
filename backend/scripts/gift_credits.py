import asyncio
from app.db import get_session
from app.models import User
from sqlalchemy import update

async def gift():
    async for session in get_session():
        await session.execute(update(User).where(User.email == 'sayemf21@gmail.com').values(credits=10))
        await session.commit()
        print('Gifted 10 credits to sayemf21@gmail.com')
        break

if __name__ == "__main__":
    asyncio.run(gift())
 Kabir, sayenf21@gmail.com, credits: 10

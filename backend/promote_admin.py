import asyncio
from app.db import SessionLocal
from app.models import User
from sqlalchemy import select

async def find_user_pattern(pattern: str):
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.email.like(f"%{pattern}%")))
        users = result.scalars().all()
        print(f"Users matching '{pattern}':")
        for u in users:
            print(f"- {u.email} (ID: {u.id}, Admin: {u.is_admin})")

if __name__ == "__main__":
    asyncio.run(find_user_pattern("sayem"))

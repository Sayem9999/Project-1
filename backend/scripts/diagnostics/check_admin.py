import asyncio
from app.db import SessionLocal
from app.models import User
from sqlalchemy import select

async def check_admin():
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.is_admin == True))
        admins = result.scalars().all()
        if not admins:
            print("No admin users found.")
        for admin in admins:
            print(f"Admin: {admin.email} (ID: {admin.id})")

if __name__ == "__main__":
    asyncio.run(check_admin())

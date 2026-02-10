import argparse
import asyncio
import os
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

if load_dotenv:
    backend_env = BACKEND_DIR / ".env"
    if backend_env.exists():
        load_dotenv(backend_env)

from app.config import settings  # noqa: E402
from app.models import User  # noqa: E402


def normalize_db_url(db_url: str) -> str:
    if db_url.startswith("postgres://"):
        return db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    if db_url.startswith("postgresql://") and "asyncpg" not in db_url:
        return db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if db_url.startswith("sqlite://") and "aiosqlite" not in db_url:
        return db_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    return db_url


async def run(args: argparse.Namespace) -> int:
    if not settings.database_url:
        print("DATABASE_URL is not set. Export it or set it in backend/.env.")
        return 1

    db_url = normalize_db_url(settings.database_url)
    engine = create_async_engine(db_url, future=True)

    async with AsyncSession(engine) as session:
        user = None
        if args.email:
            user = await session.scalar(select(User).where(User.email == args.email))
        else:
            user = await session.get(User, args.user_id)

        if not user:
            print("User not found.")
            return 1

        if args.set_credits is not None:
            user.credits = args.set_credits
        elif args.add_credits is not None:
            user.credits = (user.credits or 0) + args.add_credits

        if args.make_admin:
            user.is_admin = True
        if args.remove_admin:
            user.is_admin = False

        if any([args.set_credits is not None, args.add_credits is not None, args.make_admin, args.remove_admin]):
            await session.commit()

        await session.refresh(user)
        print(
            f"OK: id={user.id} email={user.email} credits={user.credits} is_admin={bool(user.is_admin)}"
        )
        return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Admin tool to set user credits/admin status.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--email", help="User email address")
    group.add_argument("--user-id", type=int, help="User ID")
    credits = parser.add_mutually_exclusive_group()
    credits.add_argument("--set-credits", type=int, help="Set credits to exact value")
    credits.add_argument("--add-credits", type=int, help="Add credits (delta)")
    parser.add_argument("--make-admin", action="store_true", help="Grant admin privileges")
    parser.add_argument("--remove-admin", action="store_true", help="Revoke admin privileges")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())

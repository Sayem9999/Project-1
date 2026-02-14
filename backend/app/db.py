from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import event
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import DeclarativeBase
from .config import settings


class Base(DeclarativeBase):
    pass


# Handle Render's postgres:// scheme and ensure asyncpg is used for PostgreSQL
db_url = settings.database_url
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://") and "asyncpg" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    # Ensure SQLite uses aiosqlite for async
    elif db_url.startswith("sqlite://") and "aiosqlite" not in db_url:
        db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://", 1)

engine = create_async_engine(db_url, future=True)

# SQLite reliability: enable WAL and a short busy timeout to prevent request hangs
# when API and worker are reading/writing concurrently in local dev.
if db_url and db_url.startswith("sqlite"):
    engine = create_async_engine(
        db_url,
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=NullPool,
    )

    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragmas(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
            cursor.execute("PRAGMA busy_timeout=3000;")  # ms
        finally:
            cursor.close()
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session():
    async with SessionLocal() as session:
        yield session

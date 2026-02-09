import pytest
import asyncio
import sys
import os

# Set required env vars BEFORE importing app modules
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest")

# Add backend root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db import Base, get_session
from app.main import app

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test session."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

@pytest.fixture
async def client(session) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

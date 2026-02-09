import logging
import os
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text

from .config import settings
from .db import Base, engine
from .routers import agents, auth, jobs, oauth, payments, websocket

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
logger = logging.getLogger('proedit.api')

app = FastAPI(title=settings.app_name)

origin_regex = r"https://.*\.vercel\.app|http://localhost:3000|https://.*\.onrender\.com"

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info('Request %s %s | Origin=%s', request.method, request.url, request.headers.get('origin'))
    return await call_next(request)


def _sqlite_safe_column_migration(connection) -> list[str]:
    """Apply lightweight, idempotent column migrations compatible with SQLite and Postgres."""
    inspector = inspect(connection)
    executed: list[str] = []

    desired_columns: dict[str, dict[str, str]] = {
        'users': {
            'oauth_provider': 'VARCHAR(50)',
            'oauth_id': 'VARCHAR(255)',
            'name': 'VARCHAR(255)',
            'avatar_url': 'VARCHAR(500)',
            'credits': 'INTEGER DEFAULT 10',
        },
        'jobs': {
            'thumbnail_path': 'TEXT',
        },
    }

    for table_name, columns in desired_columns.items():
        existing = {col['name'] for col in inspector.get_columns(table_name)}
        for column_name, column_type in columns.items():
            if column_name in existing:
                continue
            statement = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            connection.execute(text(statement))
            executed.append(statement)

    return executed


@app.on_event('startup')
async def startup() -> None:
    logger.info('Startup: Gemini Key Present: %s', bool(settings.gemini_api_key))
    logger.info('Startup: OpenAI Key Present: %s', bool(settings.openai_api_key))
    logger.info('Startup: Groq Key Present: %s', bool(settings.groq_api_key))
    logger.info('Startup: Google OAuth Configured: %s', bool(settings.google_client_id))
    logger.info('Startup: Redis URL Present: %s', bool(os.getenv('REDIS_URL')))
    logger.info('Startup: R2 Storage Configured: %s', bool(settings.r2_account_id))

    os.makedirs('storage', exist_ok=True)
    os.makedirs('storage/uploads', exist_ok=True)
    os.makedirs('storage/outputs', exist_ok=True)

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            executed_migrations = await conn.run_sync(_sqlite_safe_column_migration)
            for statement in executed_migrations:
                logger.info('[Migration] Executed: %s', statement)
    except Exception as exc:
        logger.exception('Startup DB Error: %s', exc)


@app.get('/')
async def root() -> dict[str, str]:
    return {'message': 'Proedit API is running'}


@app.get('/debug')
async def debug_config() -> dict[str, Any]:
    return {
        'celery_enabled': bool(os.getenv('REDIS_URL')),
        'redis_url_present': bool(os.getenv('REDIS_URL')),
        'db_url_present': bool(os.getenv('DATABASE_URL')),
        'frontend_url': os.getenv('FRONTEND_URL'),
        'cors_origins': [
            str(origin)
            for origin in app.user_middleware[0].options.get('allow_origins', [])
        ] if hasattr(app, 'user_middleware') else 'unknown',
    }


@app.get('/health')
async def health() -> dict[str, str]:
    return {'status': 'ok'}


app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(oauth.router, prefix=settings.api_prefix)
app.include_router(jobs.router, prefix=settings.api_prefix)
app.include_router(agents.router, prefix=settings.api_prefix)
app.include_router(payments.router, prefix=settings.api_prefix)
app.include_router(websocket.router)

app.mount('/storage', StaticFiles(directory='storage'), name='storage')

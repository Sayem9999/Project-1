from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Any
import time
import uuid
import asyncio
import structlog
import sentry_sdk
from .config import settings
from .db import engine, Base
from .routers import auth, jobs, agents, oauth, websocket
from .logging_config import configure_logging

import os

# Configure Logging
configure_logging()
logger = structlog.get_logger()

# Initialize Sentry
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

app = FastAPI(title=settings.app_name)

# CORS configuration - allow frontend origins
# Regex to match any Vercel deployment for this project
origin_regex = r"https://.*\.vercel\.app|http://localhost:3000|https://.*\.onrender\.com"

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
from .middleware.rate_limit import rate_limit_middleware
app.middleware("http")(rate_limit_middleware)

# Security headers middleware  
from .middleware.security_headers import security_headers_middleware
app.middleware("http")(security_headers_middleware)

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)
    
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        process_time_ms = round(process_time * 1000, 2)
        
        # Log slow requests at WARNING level
        if process_time > 5.0:
            logger.warning(
                "slow_request",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_seconds=round(process_time, 2)
            )
        else:
            logger.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=process_time
            )
        
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{process_time_ms}ms"
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            "request_failed",
            method=request.method,
            path=request.url.path,
            duration=process_time,
            error=str(e)
        )
        raise


@app.on_event("startup")
async def startup() -> None:
    import os
    logger.info("startup_config",
        gemini_key_present=bool(settings.gemini_api_key),
        openai_key_present=bool(settings.openai_api_key),
        groq_key_present=bool(settings.groq_api_key),
        google_oauth_configured=bool(settings.google_client_id),
        redis_url_present=bool(os.getenv('REDIS_URL')),
        r2_storage_configured=bool(settings.r2_account_id)
    )
    
    # Ensure storage directories
    os.makedirs("storage", exist_ok=True)
    os.makedirs("storage/uploads", exist_ok=True)
    os.makedirs("storage/outputs", exist_ok=True)
    
    # Migrate using Alembic
    logger.info("startup_migrations_start")
    try:
        from alembic.config import Config
        from alembic import command
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        def run_migrations():
            # Assume alembic.ini is in the current working directory (backend root)
            alembic_cfg = Config("alembic.ini")
            
            # Explicitly set the URL to handle any async driver requirements
            from app.config import settings
            db_url = settings.database_url
            if db_url:
                if db_url.startswith("postgres://"):
                    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
                elif db_url.startswith("postgresql://") and "asyncpg" not in db_url:
                    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
                elif db_url.startswith("sqlite://") and "aiosqlite" not in db_url:
                    db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
            
            alembic_cfg.set_main_option("sqlalchemy.url", db_url)
            command.upgrade(alembic_cfg, "head")
        
        # Run in thread pool to avoid blocking event loop
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, run_migrations)
        
        logger.info("startup_migrations_complete")
    except Exception as e:
        logger.error("startup_migrations_failed", error=str(e))

    # Schedule background tasks
    from .tasks.cleanup import run_cleanup_task
    asyncio.create_task(periodic_cleanup_wrapper(run_cleanup_task))

async def periodic_cleanup_wrapper(task_func):
    """Run cleanup every 24 hours."""
    while True:
        try:
            # Wait for 24 hours (86400 seconds)
            # Check immediately on startup? Maybe wait 1 hour first.
            await asyncio.sleep(60 * 60) # Wait 1 hour between checks/start
            await task_func()
        except Exception as e:
            logger.error("background_task_failed", error=str(e))
            await asyncio.sleep(60 * 5) # Retry after 5 min on error



@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Proedit API is running"}



@app.get("/debug")
async def debug_config() -> dict[str, Any]:
    """Debug endpoint to check environment configuration."""
    return {
        "celery_enabled": bool(os.getenv("REDIS_URL")),
        "redis_url_present": bool(os.getenv("REDIS_URL")),
        "db_url_present": bool(os.getenv("DATABASE_URL")),
        "frontend_url": os.getenv("FRONTEND_URL"),
        "cors_origins": [str(origin) for origin in app.user_middleware[0].options.get("allow_origins", [])] if hasattr(app, "user_middleware") else "unknown",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(oauth.router, prefix=settings.api_prefix)
app.include_router(jobs.router, prefix=settings.api_prefix)
app.include_router(agents.router, prefix=settings.api_prefix)
from .routers import payments, admin
app.include_router(payments.router, prefix=settings.api_prefix)
app.include_router(admin.router, prefix=settings.api_prefix)
app.include_router(websocket.router)

from fastapi.staticfiles import StaticFiles
app.mount("/storage", StaticFiles(directory="storage"), name="storage")


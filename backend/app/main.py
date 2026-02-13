from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Any
from sqlalchemy import select, update
import time
import uuid
import asyncio
import structlog
import sentry_sdk
import re
from .config import settings
from .db import engine, Base, SessionLocal
from .routers import auth, jobs, agents, oauth, websocket, maintenance
from .logging_config import configure_logging
from .models import User
from .services.introspection import introspection_service

import os

from contextlib import asynccontextmanager
from starlette.types import ASGIApp, Receive, Scope, Send

# Configure Logging
configure_logging()
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Validate settings at startup
    settings.validate_required_settings()
    
    logger.info("startup_config",
        gemini_key_present=bool(settings.gemini_api_key),
        openai_key_present=bool(settings.openai_api_key),
        groq_key_present=bool(settings.groq_api_key),
        google_oauth_configured=bool(settings.google_client_id),
        redis_url_present=bool(settings.redis_url),
        r2_storage_configured=bool(settings.r2_account_id),
        db_url_redacted=re.sub(r'://.*@', '://***@', settings.database_url) if settings.database_url else "none",
        redis_url_redacted=re.sub(r'://.*@', '://***@', settings.redis_url) if settings.redis_url else "none"
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
        
        def run_migrations():
            alembic_cfg = Config("alembic.ini")
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
        
        from concurrent.futures import ThreadPoolExecutor
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, run_migrations)
        
        logger.info("startup_migrations_complete")
    except Exception as e:
        logger.error("startup_migrations_failed", error=str(e))

    # Bootstrap admin user if configured
    try:
        await bootstrap_admin()
    except Exception as e:
        logger.error("bootstrap_admin_failed", error=str(e))

    # Clean up processing jobs left behind by previous run
    try:
        await clear_stuck_jobs()
    except Exception as e:
        logger.error("startup_cleanup_failed", error=str(e))

    # Ensure DB indices for admin dashboard performance
    try:
        from sqlalchemy import text
        async with engine.begin() as conn:
            # Enable WAL mode for better concurrency on SQLite
            await conn.execute(text("PRAGMA journal_mode=WAL"))
            await conn.execute(text("PRAGMA synchronous=NORMAL"))
            await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_jobs_created_at ON jobs (created_at)"))
            await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_jobs_status ON jobs (status)"))
            await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_created_at ON users (created_at)"))
        logger.info("startup_indices_verified")
    except Exception as e:
        logger.error("startup_indices_failed", error=str(e))

    # Start Admin Cache (zero-wait dashboard)
    from .services.admin_cache import refresh_admin_data
    asyncio.create_task(refresh_admin_data())
    
    logger.info("startup_ready")
    yield


async def bootstrap_admin() -> None:
    email = settings.admin_bootstrap_email
    if not email:
        return
    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.email == email))
        if not user:
            logger.warning("bootstrap_admin_user_missing", email=email)
            return
        already_admin = bool(user.is_admin)
        if already_admin and settings.admin_bootstrap_once:
            logger.info("bootstrap_admin_skip", email=email)
            return
        if not already_admin:
            user.is_admin = True
            await session.commit()
        logger.info(
            "bootstrap_admin_done",
            email=email,
            user_id=user.id,
            already_admin=already_admin
        )

async def clear_stuck_jobs():
    """Reset jobs that were left in 'processing' state after a crash or restart."""
    from .models import Job
    
    logger.info("startup_cleanup_stuck_jobs_start")
    try:
        async with SessionLocal() as session:
            # Set to 'failed' with a clear message.
            # This follows the user request to "cancel" them on restart.
            result = await session.execute(
                update(Job)
                .where(Job.status == "processing")
                .values(
                    status="failed",
                    progress_message="Job interrupted by system restart. Please retry manually."
                )
            )
            await session.commit()
            if result.rowcount > 0:
                logger.info("startup_cleanup_stuck_jobs_complete", affected_rows=result.rowcount)
            else:
                logger.info("startup_cleanup_stuck_jobs_none")
    except Exception as e:
        logger.error("startup_cleanup_stuck_jobs_failed", error=str(e))

async def periodic_cleanup_wrapper(task_func):
    """Run cleanup every 24 hours."""
    while True:
        try:
            # Wait for 1 hour between checks/start
            await asyncio.sleep(60 * 60)
            await task_func()
        except Exception as e:
            logger.error("background_task_failed", error=str(e))
            await asyncio.sleep(60 * 5) # Retry after 5 min on error


async def periodic_introspection_wrapper():
    """Periodically self-heal and refresh system-map graph cache."""
    interval = 60 * 10  # 10 minutes
    # Warm initial snapshot after startup without blocking request handling.
    # try:
    #     await asyncio.to_thread(introspection_service.scan, None, True)
    # except Exception as e:
    #     logger.error("introspection_warmup_failed", error=str(e))

    while True:
        try:
            await asyncio.sleep(interval)
            result = await asyncio.to_thread(introspection_service.self_heal)
            logger.info(
                "introspection_self_heal_complete",
                status=result.get("status"),
                integrity_score=result.get("integrity_score"),
                actions=result.get("actions", []),
            )
        except Exception as e:
            logger.error("introspection_self_heal_failed", error=str(e))
            await asyncio.sleep(60)

app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan
)

class PrivateNetworkAccessMiddleware:
    """
    Support Chrome/Firefox "Private Network Access" (PNA) when a public site (Vercel)
    calls into a private network endpoint (Tailscale Funnel).

    Browsers send an OPTIONS preflight containing:
      Access-Control-Request-Private-Network: true

    The server must reply with:
      Access-Control-Allow-Private-Network: true
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Normalize headers to a dict for checks.
        raw_headers = scope.get("headers") or []
        headers: dict[str, str] = {}
        for k, v in raw_headers:
            try:
                headers[k.decode("latin-1").lower()] = v.decode("latin-1")
            except Exception:
                continue

        method = (scope.get("method") or "").upper()
        origin = headers.get("origin")
        # Always allow PNA on OPTIONS responses. Browsers require this on certain
        # local/private-network preflights; being permissive here is fine because
        # we already run with allow_origins=["*"] and token auth.
        is_preflight = method == "OPTIONS"
        wants_pna = headers.get("access-control-request-private-network") == "true"
        should_add_pna = is_preflight or wants_pna

        async def send_wrapper(message):
            if message.get("type") == "http.response.start":
                hdrs = list(message.get("headers") or [])
                # Guarantee ACAO on funnel/proxy responses. If CORSMiddleware already set it,
                # don't duplicate.
                if not any(k.lower() == b"access-control-allow-origin" for k, _ in hdrs):
                    hdrs.append((b"access-control-allow-origin", b"*"))
                if should_add_pna and not any(k.lower() == b"access-control-allow-private-network" for k, _ in hdrs):
                    hdrs.append((b"access-control-allow-private-network", b"true"))
                message["headers"] = hdrs
            await send(message)

        await self.app(scope, receive, send_wrapper)

@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "1.0.0"
    }

@app.get("/api/health")
async def api_health() -> dict[str, Any]:
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "1.0.0",
        "api": "v1"
    }

@app.get("/ready")
@app.get(f"{settings.api_prefix}/ready")
async def ready() -> dict[str, str]:
    return {"status": "ready"}

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    # Standard security headers + CORP to allow cross-origin media loading (ORB prevention)
    response = await call_next(request)
    response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

app.add_middleware(
    CORSMiddleware,
    # Explicitly include the Vercel frontend and Tailscale node to ensure reliable CORS mapping.
    # While ["*"] is generally permissive, specific origins help with credentialed requests
    # and certain strict browser contexts (like PNA).
    allow_origins=[
        "http://localhost:3000",
        "https://project-1-alpha-three.vercel.app",
        "https://desktop-ajdgsgd.tail4e4049.ts.net"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # For Private Network Access (PNA), we need to tell the browser it's okay.
    expose_headers=["Access-Control-Allow-Private-Network"]
)

app.add_middleware(PrivateNetworkAccessMiddleware)

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

@app.get("/debug/redis")
async def debug_redis() -> dict[str, Any]:
    """Verify Redis connectivity without exposing secrets."""
    if not settings.redis_url:
        return {"configured": False, "reachable": False, "error": "REDIS_URL not set"}

    try:
        import redis.asyncio as redis  # type: ignore
    except Exception:
        return {"configured": True, "reachable": False, "error": "redis client not available"}

    def redact(value: str) -> str:
        return re.sub(r"(redis(?:s)?://)([^@]+)@", r"\\1***@", value)

    start = time.perf_counter()
    try:
        client = redis.from_url(settings.redis_url, decode_responses=True)
        pong = await client.ping()
        await client.close()
        latency_ms = int((time.perf_counter() - start) * 1000)
        return {"configured": True, "reachable": bool(pong), "latency_ms": latency_ms}
    except Exception as e:
        message = redact(str(e))
        return {"configured": True, "reachable": False, "error": message}
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(oauth.router, prefix=settings.api_prefix)
app.include_router(agents.router, prefix=settings.api_prefix)
from .routers import payments, admin, jobs
app.include_router(payments.router, prefix=settings.api_prefix)
app.include_router(admin.router, prefix=settings.api_prefix)
app.include_router(jobs.router, prefix=settings.api_prefix)
app.include_router(maintenance.router, prefix=settings.api_prefix)
app.include_router(websocket.router)

from fastapi.staticfiles import StaticFiles
app.mount("/storage", StaticFiles(directory="storage"), name="storage")


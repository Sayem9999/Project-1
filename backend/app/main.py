from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Any
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .db import engine, Base
from .routers import auth, jobs, agents, oauth, websocket

import os

app = FastAPI(title=settings.app_name)

# CORS configuration - allow frontend origins
# Regex to match any Vercel deployment for this project
origin_regex = r"https://.*\.vercel\.app|http://localhost:3000"

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Request: {request.method} {request.url} | Origin: {request.headers.get('origin')}")
    response = await call_next(request)
    return response


@app.on_event("startup")
async def startup() -> None:
    import os
    print(f"Startup: Gemini Key Present: {bool(settings.gemini_api_key)}")
    print(f"Startup: OpenAI Key Present: {bool(settings.openai_api_key)}")
    print(f"Startup: Groq Key Present: {bool(settings.groq_api_key)}")
    print(f"Startup: Google OAuth Configured: {bool(settings.google_client_id)}")
    print(f"Startup: Redis URL Present: {bool(os.getenv('REDIS_URL'))}")
    print(f"Startup: R2 Storage Configured: {bool(settings.r2_account_id)}")
    
    # Ensure storage directories
    os.makedirs("storage", exist_ok=True)
    os.makedirs("storage/uploads", exist_ok=True)
    os.makedirs("storage/outputs", exist_ok=True)
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
            # Migrate: Add OAuth columns if they don't exist
            from sqlalchemy import text
            migration_queries = [
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS oauth_provider VARCHAR(50)",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS oauth_id VARCHAR(255)",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS name VARCHAR(255)",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500)",
                "ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL",
                "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS thumbnail_path TEXT",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS credits INTEGER DEFAULT 10",
            ]
            for query in migration_queries:
                try:
                    await conn.execute(text(query))
                    print(f"[Migration] Executed: {query[:50]}...")
                except Exception as me:
                    print(f"[Migration] Skipped: {str(me)[:50]}")
    except Exception as e:
        print(f"Startup DB Error: {e}")



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
from .routers import payments
app.include_router(payments.router, prefix=settings.api_prefix)
app.include_router(websocket.router)

from fastapi.staticfiles import StaticFiles
app.mount("/storage", StaticFiles(directory="storage"), name="storage")


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .db import engine, Base
from .routers import auth, jobs, agents, oauth, websocket

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(oauth.router, prefix=settings.api_prefix)
app.include_router(jobs.router, prefix=settings.api_prefix)
app.include_router(agents.router, prefix=settings.api_prefix)
app.include_router(websocket.router)  # WebSocket at root level


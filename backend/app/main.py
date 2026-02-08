from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .db import engine, Base
from .routers import auth, jobs, agents

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
    # Ensure storage directory exists for SQLite fallback
    import os
    os.makedirs("storage", exist_ok=True)
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Startup DB Error: {e}")
        # We don't exit here so the app can at least start and serve /health
        # The user will see errors when trying to use features, which is better than a timeout.


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Proedit API is running"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(jobs.router, prefix=settings.api_prefix)
app.include_router(agents.router, prefix=settings.api_prefix)

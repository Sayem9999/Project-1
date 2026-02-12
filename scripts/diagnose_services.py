import os
import sys
import asyncio
import redis.asyncio as redis
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def diagnose():
    print("--- Proedit Hub Diagnostics ---")
    
    # 1. Load Env
    env_path = os.path.join("backend", ".env")
    if not os.path.exists(env_path):
        print(f"[FAIL] .env not found at {env_path}")
        return
    load_dotenv(env_path, override=True)
    print("[OK] .env loaded (forced)")

    # 2. Check Database
    db_url = os.getenv("DATABASE_URL")
    print(f"Checking DB: {db_url}")
    try:
        engine = create_async_engine(db_url)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("[OK] Database connection successful")
    except Exception as e:
        print(f"[FAIL] Database connection failed: {e}")

    # 3. Check Redis
    redis_url = os.getenv("REDIS_URL")
    print(f"Checking Redis: {redis_url[:20]}...")
    try:
        r = redis.from_url(redis_url)
        await r.ping()
        print("[OK] Redis connection successful")
        await r.close()
    except Exception as e:
        print(f"[FAIL] Redis connection failed: {e}")

    # 4. Check Port 8000
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        is_open = s.connect_ex(('127.0.0.1', 8000)) == 0
        if is_open:
            print("[OK] Port 8000 is LISTENING")
        else:
            print("[FAIL] Port 8000 is NOT listening")

if __name__ == "__main__":
    asyncio.run(diagnose())

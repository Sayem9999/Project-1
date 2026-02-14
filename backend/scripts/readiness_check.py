import argparse
import asyncio
import os
import subprocess
import sys
import shutil
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

sys.path.append(str(Path(__file__).resolve().parents[1]))
from app.config import settings


def _resolve_tool_path(tool_name: str) -> str:
    ext = ".exe" if os.name == "nt" else ""
    repo_root = Path(__file__).resolve().parents[2]
    bundled = repo_root / "tools" / "ffmpeg-8.0.1-essentials_build" / "bin" / f"{tool_name}{ext}"
    if bundled.exists():
        return str(bundled)
    on_path = shutil.which(tool_name)
    if on_path:
        return on_path
    if tool_name == "ffmpeg":
        try:
            import imageio_ffmpeg

            return imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            pass
    return tool_name


def check_ffmpeg() -> tuple[bool, str]:
    ffmpeg_bin = _resolve_tool_path("ffmpeg")
    try:
        proc = subprocess.run(
            [ffmpeg_bin, "-version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if proc.returncode != 0:
            return False, f"ffmpeg command failed with code {proc.returncode}"
        first = (proc.stdout or "").splitlines()[0] if proc.stdout else "ffmpeg detected"
        return True, f"{first} (bin={ffmpeg_bin})"
    except Exception as exc:
        return False, f"ffmpeg unavailable: {exc}"


async def check_database() -> tuple[bool, str]:
    engine = create_async_engine(settings.database_url, future=True)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True, "database connection ok"
    except Exception as exc:
        return False, f"database connection failed: {exc}"
    finally:
        await engine.dispose()


async def check_redis() -> tuple[bool, str]:
    if not settings.redis_url:
        return True, "redis not configured (optional for local inline mode)"
    try:
        import redis.asyncio as redis  # type: ignore

        client = redis.from_url(settings.redis_url, decode_responses=True)
        pong = await client.ping()
        await client.aclose()
        if pong:
            return True, "redis ping ok"
        return False, "redis ping returned false"
    except Exception as exc:
        return False, f"redis connection failed: {exc}"


def check_llm_config() -> tuple[bool, str]:
    if settings.gemini_api_key or settings.groq_api_key or settings.openai_api_key:
        return True, "at least one LLM key configured"
    return False, "no LLM API key configured (set GEMINI_API_KEY, GROQ_API_KEY, or OPENAI_API_KEY)"


def check_n8n_config() -> tuple[bool, str]:
    if not settings.n8n_base_url:
        return True, "n8n outbound webhook disabled (N8N_BASE_URL not set)"
    if not settings.n8n_webhook_secret:
        return False, "N8N_BASE_URL set but N8N_WEBHOOK_SECRET missing"
    return True, f"n8n configured ({settings.n8n_base_url}{settings.n8n_job_status_path})"


async def main() -> int:
    parser = argparse.ArgumentParser(description="Backend readiness preflight")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat optional checks (redis/n8n disabled) as failures",
    )
    args = parser.parse_args()

    checks: list[tuple[str, bool, str]] = []

    ok, msg = check_ffmpeg()
    checks.append(("ffmpeg", ok, msg))

    ok, msg = await check_database()
    checks.append(("database", ok, msg))

    ok, msg = await check_redis()
    if args.strict and "optional" in msg:
        ok = False
    checks.append(("redis", ok, msg))

    ok, msg = check_llm_config()
    checks.append(("llm", ok, msg))

    ok, msg = check_n8n_config()
    if args.strict and "disabled" in msg:
        ok = False
    checks.append(("n8n", ok, msg))

    print("== Backend Readiness ==")
    failed = 0
    for name, ok, msg in checks:
        state = "PASS" if ok else "FAIL"
        print(f"[{state}] {name}: {msg}")
        if not ok:
            failed += 1

    if failed == 0:
        print("READY: backend preflight passed")
        return 0
    print(f"NOT READY: {failed} check(s) failed")
    return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

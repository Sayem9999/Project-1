import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy import select, update

from ..services.storage_service import storage_service
from ..config import settings
from ..db import SessionLocal
from ..models import Job

logger = logging.getLogger(__name__)

LAST_CLEANUP_STATUS: dict = {
    "last_run": None,
    "deleted_local": 0,
    "deleted_r2": 0,
    "stalled_jobs": 0,
}

LOCAL_RETENTION_DAYS = 7


async def cleanup_local_files() -> int:
    root = Path(settings.storage_root)
    upload_dir = root / "uploads"
    output_dir = root / "outputs"

    if not root.exists():
        return 0

    async with SessionLocal() as session:
        result = await session.execute(select(Job.source_path, Job.output_path, Job.thumbnail_path))
        rows = result.all()

    referenced: set[str] = set()
    for source_path, output_path, thumbnail_path in rows:
        for path in [source_path, output_path, thumbnail_path]:
            if not path or str(path).startswith("http"):
                continue
            candidate = Path(path)
            if not candidate.is_absolute():
                candidate = (Path(".") / candidate).resolve()
            referenced.add(str(candidate))

    cutoff = datetime.utcnow() - timedelta(days=LOCAL_RETENTION_DAYS)
    deleted = 0

    for directory in [upload_dir, output_dir]:
        if not directory.exists():
            continue
        for file_path in directory.glob("**/*"):
            if not file_path.is_file():
                continue
            if str(file_path.resolve()) in referenced:
                continue
            try:
                mtime = datetime.utcfromtimestamp(file_path.stat().st_mtime)
                if mtime < cutoff:
                    file_path.unlink(missing_ok=True)
                    deleted += 1
            except Exception as e:
                logger.error("cleanup_local_error", path=str(file_path), error=str(e))

    return deleted


async def run_cleanup_task():
    """
    Background task to clean up old files from storage.
    This should be scheduled to run periodically (e.g., once a day).
    """
    logger.info("Starting storage cleanup task...")
    try:
        # Run synchronous boto3 cleanup in a thread executor to avoid blocking the loop
        loop = asyncio.get_running_loop()
        deleted_r2 = await loop.run_in_executor(None, storage_service.cleanup_old_files)
        deleted_local = await cleanup_local_files()
        stalled = await mark_stalled_jobs()
        LAST_CLEANUP_STATUS.update(
            {
                "last_run": datetime.utcnow().isoformat(),
                "deleted_local": deleted_local,
                "deleted_r2": deleted_r2,
                "stalled_jobs": stalled,
            }
        )
        logger.info(
            "Storage cleanup completed. Deleted %s local files, %s R2 files. Marked %s stalled jobs.",
            deleted_local,
            deleted_r2,
            stalled,
        )
    except Exception as e:
        logger.error(f"Error during storage cleanup: {e}")


def get_cleanup_status() -> dict:
    return LAST_CLEANUP_STATUS.copy()


async def mark_stalled_jobs() -> int:
    """Mark jobs stuck in processing for too long as failed."""
    timeout_minutes = 180
    cutoff = datetime.utcnow() - timedelta(minutes=timeout_minutes)
    async with SessionLocal() as session:
        result = await session.execute(
            update(Job)
            .where(Job.status == "processing", Job.updated_at < cutoff)
            .values(status="failed", progress_message="Marked failed after timeout.")
            .execution_options(synchronize_session=False)
        )
        await session.commit()
        return result.rowcount or 0

if __name__ == "__main__":
    # Allow running as a standalone script
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_cleanup_task())

import asyncio
import logging
from ..services.storage_service import storage_service

logger = logging.getLogger(__name__)

async def run_cleanup_task():
    """
    Background task to clean up old files from storage.
    This should be scheduled to run periodically (e.g., once a day).
    """
    logger.info("Starting storage cleanup task...")
    try:
        # Run synchronous boto3 cleanup in a thread executor to avoid blocking the loop
        loop = asyncio.get_running_loop()
        deleted_count = await loop.run_in_executor(None, storage_service.cleanup_old_files)
        logger.info(f"Storage cleanup completed. Deleted {deleted_count} files.")
    except Exception as e:
        logger.error(f"Error during storage cleanup: {e}")

if __name__ == "__main__":
    # Allow running as a standalone script
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_cleanup_task())

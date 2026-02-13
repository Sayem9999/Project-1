import os
import time
import shutil
import structlog
from pathlib import Path

logger = structlog.get_logger()

class CleanupService:
    def __init__(self, storage_root: str = "storage"):
        self.storage_root = Path(storage_root)
        self.temp_dir = self.storage_root / "temp"
        self.outputs_dir = self.storage_root / "outputs"

    async def run_cleanup(self, max_age_hours: int = 6):
        logger.info("cleanup_start", max_age_hours=max_age_hours)
        total_freed = 0
        now = time.time()
        max_age_seconds = max_age_hours * 3600

        # 1. Clean temp folder
        if self.temp_dir.exists():
            for item in self.temp_dir.iterdir():
                if item.stat().st_mtime < (now - max_age_seconds):
                    try:
                        size = self._get_size(item)
                        if item.is_file():
                            item.unlink()
                        else:
                            shutil.rmtree(item)
                        total_freed += size
                        logger.info("cleanup_removed", path=str(item), size=size)
                    except Exception as e:
                        logger.error("cleanup_error", path=str(item), error=str(e))

        # 2. Clean job parts in outputs
        if self.outputs_dir.exists():
            for item in self.outputs_dir.glob("job-*-parts"):
                if item.is_dir() and item.stat().st_mtime < (now - max_age_seconds):
                    try:
                        size = self._get_size(item)
                        shutil.rmtree(item)
                        total_freed += size
                        logger.info("cleanup_removed_parts", path=str(item), size=size)
                    except Exception as e:
                        logger.error("cleanup_error", path=str(item), error=str(e))

        logger.info("cleanup_complete", total_freed_bytes=total_freed)
        return total_freed

    def _get_size(self, path: Path) -> int:
        if path.is_file():
            return path.stat().st_size
        return sum(f.stat().st_size for f in path.glob('**/*') if f.is_file())

cleanup_service = CleanupService()

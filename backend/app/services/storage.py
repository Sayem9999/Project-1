from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile
from ..config import settings


class StorageService:
    def __init__(self) -> None:
        self.root = Path(settings.storage_root)
        self.upload_dir = self.root / "uploads"
        self.output_dir = self.root / "outputs"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, file: UploadFile) -> str:
        ext = Path(file.filename or "video.mp4").suffix or ".mp4"
        target = self.upload_dir / f"{uuid4()}{ext}"
        with target.open("wb") as handle:
            while chunk := await file.read(1024 * 1024):
                handle.write(chunk)
        return str(target)


storage_service = StorageService()

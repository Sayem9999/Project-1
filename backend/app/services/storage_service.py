"""
Cloudflare R2 Storage Service
S3-compatible object storage for video files.
"""
import boto3
from botocore.config import Config
from pathlib import Path
import uuid
from ..config import settings


class StorageService:
    """Handles file uploads to Cloudflare R2 (or local storage as fallback)."""
    
    def __init__(self):
        self.use_r2 = all([
            settings.r2_account_id,
            settings.r2_access_key_id,
            settings.r2_secret_access_key,
        ])
        
        if self.use_r2:
            self.s3_client = boto3.client(
                "s3",
                endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
                aws_access_key_id=settings.r2_access_key_id,
                aws_secret_access_key=settings.r2_secret_access_key,
                config=Config(signature_version="s3v4"),
                region_name="auto",
            )
            self.bucket = settings.r2_bucket_name
            print("[Storage] Using Cloudflare R2")
        else:
            self.s3_client = None
            print("[Storage] Using local filesystem (R2 not configured)")
    
    async def upload_file(self, local_path: str, folder: str = "uploads") -> str:
        """
        Upload a file to R2 or keep in local storage.
        Returns the public URL or local path.
        """
        path = Path(local_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {local_path}")
        
        # Generate unique key
        unique_id = uuid.uuid4().hex[:8]
        key = f"{folder}/{unique_id}-{path.name}"
        
        if self.use_r2 and self.s3_client:
            # Upload to R2
            content_type = self._get_content_type(path.suffix)
            
            with open(path, "rb") as f:
                self.s3_client.upload_fileobj(
                    f,
                    self.bucket,
                    key,
                    ExtraArgs={"ContentType": content_type}
                )
            
            # Return public URL
            if settings.r2_public_url:
                return f"{settings.r2_public_url}/{key}"
            else:
                # Generate presigned URL (valid for 7 days)
                return self.s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket, "Key": key},
                    ExpiresIn=604800,
                )
        else:
            # Fallback to local storage
            return str(path)
    
    async def delete_file(self, key: str) -> bool:
        """Delete a file from R2."""
        if self.use_r2 and self.s3_client:
            try:
                self.s3_client.delete_object(Bucket=self.bucket, Key=key)
                return True
            except Exception as e:
                print(f"[Storage] Delete error: {e}")
                return False
        return False
    
    def get_presigned_upload_url(self, filename: str, folder: str = "uploads") -> dict:
        """
        Generate a presigned URL for direct browser upload.
        Returns dict with upload_url and final_key.
        """
        if not self.use_r2 or not self.s3_client:
            raise Exception("R2 not configured - cannot generate presigned URL")
        
        unique_id = uuid.uuid4().hex[:8]
        key = f"{folder}/{unique_id}-{filename}"
        content_type = self._get_content_type(Path(filename).suffix)
        
        presigned_url = self.s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self.bucket,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=3600,  # 1 hour
        )
        
        return {
            "upload_url": presigned_url,
            "key": key,
            "public_url": f"{settings.r2_public_url}/{key}" if settings.r2_public_url else None,
        }
    
    def _get_content_type(self, suffix: str) -> str:
        """Map file extension to MIME type."""
        types = {
            ".mp4": "video/mp4",
            ".mov": "video/quicktime",
            ".avi": "video/x-msvideo",
            ".webm": "video/webm",
            ".mkv": "video/x-matroska",
            ".srt": "text/plain",
            ".vtt": "text/vtt",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
        }
        return types.get(suffix.lower(), "application/octet-stream")


# Singleton instance
storage_service = StorageService()

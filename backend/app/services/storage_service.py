"""
Cloudflare R2 Storage Service with Free Tier Limits
- 10GB storage cap
- Auto-cleanup of old files
- Per-file size limit (100MB)
"""
import boto3
from botocore.config import Config
from pathlib import Path
import uuid
from datetime import datetime, timedelta
from ..config import settings


# Free tier limits
MAX_STORAGE_BYTES = 10 * 1024 * 1024 * 1024  # 10 GB
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB per file
CLEANUP_THRESHOLD = 0.85  # Start cleanup at 85% (8.5 GB)
FILE_RETENTION_DAYS = 7  # Delete files older than 7 days


class StorageService:
    """Handles file uploads to Cloudflare R2 with free tier limits."""
    
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
            print(f"[Storage] R2 enabled - Bucket: {self.bucket}, Limit: 10GB")
        else:
            self.s3_client = None
            print("[Storage] Local filesystem (R2 not configured)")
    
    def get_storage_usage(self) -> dict:
        """Get current storage usage in bytes and file count."""
        if not self.use_r2 or not self.s3_client:
            return {"bytes": 0, "files": 0, "percent": 0}
        
        total_bytes = 0
        file_count = 0
        
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=self.bucket):
                for obj in page.get('Contents', []):
                    total_bytes += obj['Size']
                    file_count += 1
        except Exception as e:
            print(f"[Storage] Error getting usage: {e}")
            
        return {
            "bytes": total_bytes,
            "files": file_count,
            "percent": round((total_bytes / MAX_STORAGE_BYTES) * 100, 1),
            "limit_gb": MAX_STORAGE_BYTES / (1024**3),
            "used_gb": round(total_bytes / (1024**3), 2),
        }
    
    def cleanup_old_files(self, force: bool = False) -> int:
        """Delete files older than retention period. Returns count deleted."""
        if not self.use_r2 or not self.s3_client:
            return 0
        
        usage = self.get_storage_usage()
        should_cleanup = force or (usage["percent"] >= CLEANUP_THRESHOLD * 100)
        
        if not should_cleanup:
            return 0
        
        print(f"[Storage] Cleanup triggered at {usage['percent']}% usage")
        
        deleted_count = 0
        cutoff_date = datetime.utcnow() - timedelta(days=FILE_RETENTION_DAYS)
        files_to_delete = []
        
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=self.bucket):
                for obj in page.get('Contents', []):
                    if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                        files_to_delete.append({'Key': obj['Key']})
            
            if files_to_delete:
                # Delete in batches of 1000 (S3 limit)
                for i in range(0, len(files_to_delete), 1000):
                    batch = files_to_delete[i:i+1000]
                    self.s3_client.delete_objects(
                        Bucket=self.bucket,
                        Delete={'Objects': batch}
                    )
                    deleted_count += len(batch)
                
                print(f"[Storage] Deleted {deleted_count} old files")
        except Exception as e:
            print(f"[Storage] Cleanup error: {e}")
        
        return deleted_count
    
    async def upload_file(self, local_path: str, folder: str = "uploads") -> str:
        """Upload a file to R2 with size limits."""
        path = Path(local_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {local_path}")
        
        file_size = path.stat().st_size
        
        # Check file size limit
        if file_size > MAX_FILE_SIZE_BYTES:
            raise ValueError(f"File too large: {file_size / (1024**2):.1f}MB. Max: 100MB")
        
        if self.use_r2 and self.s3_client:
            # Check storage capacity and cleanup if needed
            usage = self.get_storage_usage()
            if usage["bytes"] + file_size > MAX_STORAGE_BYTES:
                self.cleanup_old_files(force=True)
                # Re-check after cleanup
                usage = self.get_storage_usage()
                if usage["bytes"] + file_size > MAX_STORAGE_BYTES:
                    raise ValueError("Storage limit reached (10GB). Try again later.")
            
            # Generate unique key
            unique_id = uuid.uuid4().hex[:8]
            key = f"{folder}/{unique_id}-{path.name}"
            content_type = self._get_content_type(path.suffix)
            
            with open(path, "rb") as f:
                self.s3_client.upload_fileobj(
                    f, self.bucket, key,
                    ExtraArgs={"ContentType": content_type}
                )
            
            # Return public URL or presigned URL
            if settings.r2_public_url:
                return f"{settings.r2_public_url}/{key}"
            return self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=604800,  # 7 days
            )
        else:
            return str(path)
    
    async def delete_file(self, key: str) -> bool:
        """Delete a single file from R2."""
        if self.use_r2 and self.s3_client:
            try:
                self.s3_client.delete_object(Bucket=self.bucket, Key=key)
                return True
            except Exception as e:
                print(f"[Storage] Delete error: {e}")
        return False
    
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
        }
        return types.get(suffix.lower(), "application/octet-stream")


# Singleton
storage_service = StorageService()

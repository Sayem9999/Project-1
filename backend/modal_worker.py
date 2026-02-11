import modal
import os
from pathlib import Path
from typing import List, Dict, Any
from urllib.parse import urlparse

# 1. Setup Image
# We need MoviePy, FFmpeg, and dependencies for audio/video processing
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "git")
    .pip_install(
        "moviepy",
        "boto3",
        "pydantic",
        "requests"
    )
)

app = modal.App("proedit-worker", image=image)

# Shared volume for caching models if needed (not needed for basic MoviePy)
volume = modal.Volume.from_name("proedit-assets", create_if_missing=True)

@app.function(
    gpu="T4",
    timeout=600,
    volumes={"/assets": volume},
    secrets=[
        modal.Secret.from_name("proedit-r2-secrets")
    ]
)
def render_video_v1(
    job_id: int,
    source_url: str,
    cuts: List[Dict[str, Any]],
    output_key: str,
    fps: int = 24,
    crf: int = 18,
    vf_filters: str | None = None,
    af_filters: str | None = None
):
    """
    Renders a video on Modal GPU.
    Downloads source from R2, processes with MoviePy, uploads result back to R2.
    """
    import moviepy as mp
    import boto3
    import requests
    import subprocess
    import time
    from botocore.config import Config
    
    print(f"--- Modal: Starting Render Job {job_id} ---")
    
    # Setup R2 Client (via secrets)
    r2_account_id = os.environ["R2_ACCOUNT_ID"]
    r2_access_key = os.environ["R2_ACCESS_KEY_ID"]
    r2_secret_key = os.environ["R2_SECRET_ACCESS_KEY"]
    bucket_name = os.environ["R2_BUCKET_NAME"]
    
    s3 = boto3.client(
        "s3",
        endpoint_url=f"https://{r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=r2_access_key,
        aws_secret_access_key=r2_secret_key,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )
    
    def _extract_r2_key_from_url(url: str) -> str | None:
        """
        Extract object key from account-style R2 URL:
        https://<account>.r2.cloudflarestorage.com/<bucket>/<key>?...
        """
        parsed = urlparse(url)
        expected_host = f"{r2_account_id}.r2.cloudflarestorage.com"
        if parsed.netloc.lower() != expected_host.lower():
            return None
        path = parsed.path.lstrip("/")
        prefix = f"{bucket_name}/"
        if not path.startswith(prefix):
            return None
        key = path[len(prefix):]
        return key or None

    def _download_with_http_retries(url: str, dest: Path, retries: int = 3) -> None:
        last_error = None
        for attempt in range(1, retries + 1):
            try:
                with requests.get(url, stream=True, timeout=180) as resp:
                    resp.raise_for_status()
                    with open(dest, "wb") as f:
                        for chunk in resp.iter_content(chunk_size=1024 * 1024):
                            if chunk:
                                f.write(chunk)
                if dest.exists() and dest.stat().st_size > 1024:
                    return
                raise RuntimeError(f"Downloaded file too small: {dest.stat().st_size if dest.exists() else 0} bytes")
            except Exception as e:
                last_error = e
                print(f"HTTP download attempt {attempt}/{retries} failed: {e}")
                time.sleep(min(5 * attempt, 15))
        raise RuntimeError(f"HTTP download failed after {retries} attempts: {last_error}")

    def _validate_video(path: Path) -> None:
        probe = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=nk=1:nw=1",
                str(path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if probe.returncode != 0:
            raise RuntimeError(f"ffprobe validation failed: {probe.stderr.strip() or probe.stdout.strip()}")
        duration_raw = (probe.stdout or "").strip()
        try:
            duration = float(duration_raw)
        except Exception:
            duration = 0.0
        if duration <= 0:
            raise RuntimeError(f"ffprobe returned invalid duration: {duration_raw!r}")

    # 1. Download Source
    source_local = Path(f"/tmp/source_{job_id}.mp4")
    print(f"Downloading source: {source_url}")
    source_key = _extract_r2_key_from_url(source_url)
    if source_key:
        print(f"Downloading via R2 API key={source_key}")
        with open(source_local, "wb") as f:
            s3.download_fileobj(bucket_name, source_key, f)
    else:
        _download_with_http_retries(source_url, source_local, retries=3)

    print(f"Downloaded size: {source_local.stat().st_size} bytes")
    _validate_video(source_local)
            
    # 2. Process with MoviePy
    print(f"Processing {len(cuts)} cuts...")
    original_clip = mp.VideoFileClip(str(source_local))
    
    clips = []
    for cut in cuts:
        start = float(cut.get("start", 0))
        end = float(cut.get("end", original_clip.duration))
        if start >= original_clip.duration: continue
        if end > original_clip.duration: end = original_clip.duration
        if start >= end: continue
        
        sub = original_clip.subclipped(start, end)
        clips.append(sub)
        
    if not clips:
        final_video = original_clip
    else:
        final_video = mp.concatenate_videoclips(clips, method="compose")
        
    # Prepare additional filters
    extra_params = ["-crf", str(crf)]
    if vf_filters:
        extra_params += ["-vf", vf_filters]
    if af_filters:
        extra_params += ["-af", af_filters]

    # 3. Export
    output_local = Path(f"/tmp/output_{job_id}.mp4")
    try:
        final_video.write_videofile(
            str(output_local),
            codec="h264_nvenc", # Prefer GPU encoding when available.
            audio_codec="aac",
            fps=fps,
            ffmpeg_params=extra_params + ["-preset", "p4"],
            logger=None
        )
    except Exception:
        # Fallback keeps jobs completing even if NVENC is unavailable
        final_video.write_videofile(
            str(output_local),
            codec="libx264",
            audio_codec="aac",
            fps=fps,
            ffmpeg_params=extra_params + ["-preset", "medium"],
            logger=None
        )
    
    # 4. Upload to R2
    print(f"Uploading to R2: {output_key}")
    with open(output_local, "rb") as f:
        s3.upload_fileobj(f, bucket_name, output_key, ExtraArgs={"ContentType": "video/mp4"})
        
    # Clean up
    original_clip.close()
    final_video.close()
    source_local.unlink(missing_ok=True)
    output_local.unlink(missing_ok=True)
    
    return output_key

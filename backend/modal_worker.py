import modal
import os
from pathlib import Path
from typing import List, Dict, Any

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
    crf: int = 18
):
    """
    Renders a video on Modal GPU.
    Downloads source from R2, processes with MoviePy, uploads result back to R2.
    """
    import moviepy as mp
    import boto3
    import requests
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
    
    # 1. Download Source
    source_local = Path(f"/tmp/source_{job_id}.mp4")
    print(f"Downloading source: {source_url}")
    resp = requests.get(source_url, stream=True, timeout=120)
    resp.raise_for_status()
    with open(source_local, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
            
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
        
    # 3. Export
    output_local = Path(f"/tmp/output_{job_id}.mp4")
    try:
        final_video.write_videofile(
            str(output_local),
            codec="h264_nvenc", # Prefer GPU encoding when available.
            audio_codec="aac",
            fps=fps,
            ffmpeg_params=["-crf", str(crf), "-preset", "p4"], # NVENC presets: p1...p7
            logger=None
        )
    except Exception:
        # Fallback keeps jobs completing even if NVENC is unavailable in the runtime image.
        final_video.write_videofile(
            str(output_local),
            codec="libx264",
            audio_codec="aac",
            fps=fps,
            ffmpeg_params=["-crf", str(crf), "-preset", "medium"],
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

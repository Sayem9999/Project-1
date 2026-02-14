#!/usr/bin/env python3
import json
import time
import uuid
import subprocess
import os
import shutil
from pathlib import Path
from urllib import request, error

API = "http://127.0.0.1:8000/api"
OUT_DIR = Path("tmp/pro_e2e")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def resolve_ffmpeg() -> str:
    exe = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    candidates = [
        Path("tools") / "ffmpeg-8.0.1-essentials_build" / "bin" / exe,
        Path("..") / "tools" / "ffmpeg-8.0.1-essentials_build" / "bin" / exe,
        Path(r"C:\pinokio\api\editstudio\tools\ffmpeg-8.0.1-essentials_build\bin") / exe,
        Path(r"C:\pinokio\bin\miniconda\Library\bin") / exe,
    ]
    for c in candidates:
        try:
            if c.exists():
                return str(c)
        except Exception:
            continue

    on_path = shutil.which("ffmpeg")
    if on_path:
        return on_path

    try:
        import imageio_ffmpeg  # type: ignore

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def http_json(method: str, url: str, payload: dict | None = None, token: str | None = None):
    data = None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, headers=headers, method=method)
    timeout = 60 if "/start" in url else 30
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
        raise
    except Exception as e:
        print(f"Connection Error: {e}")
        raise


def upload_pro_file(path: Path, token: str):
    boundary = "----WebKitFormBoundary" + uuid.uuid4().hex
    file_bytes = path.read_bytes()
    
    # Form data parts
    fields = {
        "theme": "professional",
        "pacing": "medium",
        "mood": "cinematic",
        "ratio": "16:9",
        "tier": "pro",
        "platform": "youtube"
    }
    
    body = b""
    for name, value in fields.items():
        body += (
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"{name}\"\r\n\r\n"
            f"{value}\r\n"
        ).encode("utf-8")

    # File part
    body += (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"file\"; filename=\"{path.name}\"\r\n"
        f"Content-Type: video/mp4\r\n\r\n"
    ).encode("utf-8")
    
    body += file_bytes
    body += f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = request.Request(
        f"{API}/jobs/upload",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    print("--- ProEdit Studio PROFESSIONAL E2E CHECK ---")
    
    # Generate test video if needed
    video = OUT_DIR / "pro-check-input.mp4"
    if not video.exists():
        print("Generating test video file...")
        ffmpeg_path = resolve_ffmpeg()
        
        try:
            subprocess.run([
                ffmpeg_path, "-y", "-f", "lavfi", "-i", "testsrc=size=1280x720:rate=24",
                "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000",
                "-t", "5", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(video)
            ], check=True, capture_output=True)
            print(f"Generated test video: {video}")
        except Exception as e:
            print(f"FFmpeg failed, checking for existing uploads...")
            uploads = list(Path("backend/storage/uploads").glob("*.mp4"))
            if uploads:
                import shutil
                shutil.copy(uploads[0], video)
                print(f"Using existing upload: {uploads[0]}")
            else:
                print("FATAL: No input video available.")
                return

    # User Auth
    email = f"pro-check-{uuid.uuid4().hex[:8]}@proedit.ai"
    password = "ProPassword123!"
    print(f"Creating test user: {email}")
    
    try:
        signup = http_json("POST", f"{API}/auth/signup", {"email": email, "password": password})
        token = signup["access_token"]
    except Exception as e:
        print(f"Auth failed. Is the server running at {API}?")
        return

    # Upload with Tier=PRO
    print(f"Uploading video with PRO tier...")
    job = upload_pro_file(video, token)
    job_id = job["id"]
    print(f"Job ID: {job_id} | Tier: {job.get('tier')}")

    # Start Job
    print("Initializing Hollywood Pipeline (LangGraph)...")
    http_json("POST", f"{API}/jobs/{job_id}/start", token=token)

    # Monitor Progress
    print("Monitoring real-time progress...")
    last_msg = ""
    for i in range(600): # 10 min
        time.sleep(2)
        status = http_json("GET", f"{API}/jobs/{job_id}", token=token)
        msg = status.get("progress_message", "")
        if msg != last_msg:
            print(f"[{status['status'].upper()}] {msg}")
            last_msg = msg
        
        if status["status"] in ("complete", "failed"):
            break
    
    if status["status"] == "complete":
        print("\n✅ PROFESSIONAL E2E CHECK SUCCESSFUL")
        print(f"Output: {status.get('output_path')}")
        
        # Download check
        print("Verifying download availability...")
        out_file = OUT_DIR / f"pro-output-{job_id}.mp4"
        req = request.Request(f"{API}/jobs/{job_id}/download", headers={"Authorization": f"Bearer {token}"})
        with request.urlopen(req, timeout=60) as resp:
            out_file.write_bytes(resp.read())
        print(f"Downloaded output size: {out_file.stat().st_size} bytes")
    else:
        print("\n❌ PROFESSIONAL E2E CHECK FAILED")
        print(f"Last Status: {status}")


if __name__ == "__main__":
    main()

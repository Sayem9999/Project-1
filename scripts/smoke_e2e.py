#!/usr/bin/env python3
import json
import time
import uuid
import subprocess
from pathlib import Path
from urllib import request, error

API = "http://127.0.0.1:8000/api"
OUT_DIR = Path("tmp/smoke")
OUT_DIR.mkdir(parents=True, exist_ok=True)


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


def upload_file(path: Path, token: str):
    boundary = "----WebKitFormBoundary" + uuid.uuid4().hex
    file_bytes = path.read_bytes()
    
    # Theme part
    theme_part = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"theme\"\r\n\r\n"
        f"viral\r\n"
    ).encode("utf-8")

    # File part
    file_header = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"file\"; filename=\"{path.name}\"\r\n"
        f"Content-Type: video/mp4\r\n\r\n"
    ).encode("utf-8")
    
    footer = f"\r\n--{boundary}--\r\n".encode("utf-8")
    
    body = theme_part + file_header + file_bytes + footer

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
    video = OUT_DIR / "real-input.mp4"
    ffmpeg_path = r"C:\Users\Sayem\Downloads\New folder\Project-1-1\tools\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"
    if video.exists() and video.stat().st_size < 1000: # Delete dummy/small files
        video.unlink()
        
    if not video.exists():
        try:
            subprocess.run([
                ffmpeg_path, "-y", "-f", "lavfi", "-i", "testsrc=size=1280x720:rate=30",
                "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000",
                "-t", "6", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(video)
            ], check=True, capture_output=True)
        except Exception as e:
            print(f"FFmpeg generation failed: {e}")
            if not video.exists():
                 # Try to copy an existing upload if available
                 uploads = list(Path("backend/storage/uploads").glob("*.mp4"))
                 if uploads:
                     import shutil
                     shutil.copy(uploads[0], video)
                     print(f"Using existing upload: {uploads[0]}")
                 else:
                     print("No video found, creating dummy text file (Warning: may cause pipeline failure)")
                     video.write_text("dummy video content")
    else:
        print(f"Using existing video: {video}")

    email = f"smoke-{uuid.uuid4().hex[:8]}@example.com"
    password = "StrongPass123!"

    signup = http_json("POST", f"{API}/auth/signup", {"email": email, "password": password})
    token = signup["access_token"]

    job = upload_file(video, token)
    job_id = job["id"]
    print(f"Uploaded job {job_id}, starting...")

    # Explicitly start the job
    http_json("POST", f"{API}/jobs/{job_id}/start", token=token)
    print("Job started successfully.")

    status = job
    seen_statuses = {status["status"]}
    for i in range(600):  # Wait up to 10 minutes
        time.sleep(1)
        status = http_json("GET", f"{API}/jobs/{job_id}", token=token)
        seen_statuses.add(status["status"])
        if i % 10 == 0:
            print(f"Status check {i}: {status['status']} - {status.get('progress_message')}")
        if status["status"] in ("complete", "failed"):
            break

    if "processing" not in seen_statuses:
        raise SystemExit(f"Expected processing callback status, saw: {sorted(seen_statuses)}")
    if status["status"] != "complete":
        raise SystemExit(f"Job did not complete: {status}")

    req = request.Request(
        f"{API}/jobs/{job_id}/download",
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    out_file = OUT_DIR / f"download-{job_id}.mp4"
    with request.urlopen(req, timeout=60) as resp:
        out_file.write_bytes(resp.read())

    if out_file.stat().st_size <= 0:
        raise SystemExit("Downloaded output is empty")

    print(json.dumps({"job_id": job_id, "status": status["status"], "seen_statuses": sorted(seen_statuses), "output": str(out_file)}, indent=2))


if __name__ == "__main__":
    main()

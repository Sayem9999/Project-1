#!/usr/bin/env python3
import json
import time
import uuid
import subprocess
from pathlib import Path
from urllib import request

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
    with request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def upload_file(path: Path, token: str):
    boundary = "----WebKitFormBoundary" + uuid.uuid4().hex
    file_bytes = path.read_bytes()
    body = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"file\"; filename=\"{path.name}\"\r\n"
        f"Content-Type: video/mp4\r\n\r\n"
    ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")
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
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc=size=1280x720:rate=30",
        "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000",
        "-t", "6", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(video)
    ], check=True, capture_output=True)

    email = f"smoke-{uuid.uuid4().hex[:8]}@example.com"
    password = "StrongPass123!"

    signup = http_json("POST", f"{API}/auth/signup", {"email": email, "password": password})
    token = signup["access_token"]

    job = upload_file(video, token)
    job_id = job["id"]

    status = job
    seen_statuses = {status["status"]}
    for _ in range(40):
        time.sleep(0.5)
        status = http_json("GET", f"{API}/jobs/{job_id}", token=token)
        seen_statuses.add(status["status"])
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

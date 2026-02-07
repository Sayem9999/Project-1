#!/usr/bin/env python3
import json
import shutil
import subprocess
import threading
import time
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import request

BACKEND_BASE = "http://127.0.0.1:8000/api"
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def callback(job_id: int, status: str, progress_message: str, output_path: str | None = None):
    payload = {"status": status, "progress_message": progress_message, "output_path": output_path}
    req = request.Request(
        f"{BACKEND_BASE}/workflow/n8n/callback/{job_id}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=15) as resp:
        resp.read()


def resolve_path(raw: str) -> Path:
    p = Path(raw)
    if p.exists():
        return p
    alt = PROJECT_ROOT / "backend" / raw
    if alt.exists():
        return alt
    return p


def process_job(job_id: int, source_path_raw: str):
    try:
        source_path = resolve_path(source_path_raw)
        output_rel = f"storage/outputs/job-{job_id}.mp4"
        output_abs = PROJECT_ROOT / "backend" / output_rel
        output_abs.parent.mkdir(parents=True, exist_ok=True)

        callback(job_id, "processing", "Mock n8n: analyzing transcript and planning edits")
        time.sleep(1.5)

        try:
            subprocess.run(
                [
                    "ffmpeg", "-y", "-i", str(source_path),
                    "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2",
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                    str(output_abs),
                ],
                check=True,
                capture_output=True,
            )
        except Exception:
            shutil.copyfile(source_path, output_abs)

        callback(job_id, "complete", "Mock n8n: render complete", str(output_abs))
    except Exception as exc:
        try:
            callback(job_id, "failed", f"Mock n8n failed: {exc}")
        except Exception:
            pass


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/webhook/edit-ai-process":
            self.send_response(404)
            self.end_headers()
            return
        content_length = int(self.headers.get("Content-Length", "0"))
        data = json.loads(self.rfile.read(content_length).decode("utf-8"))
        job_id = int(data["job_id"])
        source_path = data["source_path"]

        threading.Thread(target=process_job, args=(job_id, source_path), daemon=True).start()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"ok":true}')


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 5678), Handler).serve_forever()

import requests
import time
import sys
import os
import shutil
import subprocess
from pathlib import Path

API_BASE = "http://localhost:8000/api"
TEST_EMAIL = f"smoke_test_{int(time.time())}@example.com"
TEST_PASS = "Password123!"


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


def ensure_test_video() -> str:
    out_dir = Path("tmp") / "smoke"
    out_dir.mkdir(parents=True, exist_ok=True)
    video_path = out_dir / "smoke_test_input.mp4"

    # Prefer an existing real upload if present.
    uploads = list(Path("backend/storage/uploads").glob("*.mp4"))
    if uploads:
        return str(uploads[0])

    if video_path.exists() and video_path.stat().st_size > 1000:
        return str(video_path)

    ffmpeg = resolve_ffmpeg()
    try:
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-f",
                "lavfi",
                "-i",
                "testsrc=size=1280x720:rate=24",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=440:sample_rate=48000",
                "-t",
                "5",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                str(video_path),
            ],
            check=True,
            capture_output=True,
        )
    except Exception as e:
        print(f"FFmpeg generation failed: {e}")
        # As a last resort, create a small dummy file (may fail downstream).
        video_path.write_bytes(b"dummy")

    return str(video_path)


def run_smoke_test():
    print(f"--- Starting Smoke Test: {TEST_EMAIL} ---")
    
    # 1. Signup
    print("Step 1: Signing up...")
    res = requests.post(f"{API_BASE}/auth/signup", json={"email": TEST_EMAIL, "password": TEST_PASS})
    if res.status_code != 200:
        print(f"Signup failed: {res.text}")
        return
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Signup successful.")

    # 2. Upload Dummy Video
    print("Step 2: Uploading video...")
    video_path = ensure_test_video()
        
    with open(video_path, "rb") as f:
        files = {"file": ("dummy_video.mp4", f, "video/mp4")}
        data = {
            "theme": "professional",
            "tier": "pro",
            "platform": "youtube"
        }
        res = requests.post(f"{API_BASE}/jobs/upload", headers=headers, files=files, data=data)
    
    if res.status_code != 200:
        print(f"Upload failed: {res.text}")
        return
        
    job = res.json()
    job_id = job["id"]
    print(f"Upload successful. Job ID: {job_id}")

    # 2b. Start Job (frontend does this too)
    print("Step 2b: Starting job...")
    res = requests.post(f"{API_BASE}/jobs/{job_id}/start", headers=headers)
    if res.status_code != 200:
        print(f"Start failed: {res.text}")
        return
    print("Start accepted.")

    # 3. Monitor Progress
    print("Step 3: Monitoring progress...")
    last_msg = ""
    start_time = time.time()
    timeout = 900 # 15 minutes (Pro pipeline can take several minutes on cold start)
    
    while time.time() - start_time < timeout:
        res = requests.get(f"{API_BASE}/jobs/{job_id}", headers=headers)
        if res.status_code != 200:
            print(f"Failed to fetch job status: {res.text}")
            break
            
        job = res.json()
        status = job["status"]
        msg = job.get("progress_message", "No message")
        
        if msg != last_msg:
            print(f"[{status}] {msg}")
            last_msg = msg
            
        if status == "complete":
            print("\n--- Smoke Test SUCCESS ---")
            print(f"Brand Safety Result: {job.get('brand_safety_result')}")
            print(f"AB Test Result: {job.get('ab_test_result')}")
            return
        elif status == "failed":
            print(f"\n--- Smoke Test FAILED ---")
            print(f"Final Message: {msg}")
            return
            
        time.sleep(5)
    
    print("\n--- Smoke Test TIMEOUT ---")

if __name__ == "__main__":
    run_smoke_test()

import requests
import time
import sys
import os

API_BASE = "http://localhost:8000/api"
TEST_EMAIL = f"smoke_test_{int(time.time())}@example.com"
TEST_PASS = "Password123!"

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
    video_path = "frontend/dummy_video.mp4"
    if not os.path.exists(video_path):
        print(f"Error: {video_path} not found.")
        return
        
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

    # 3. Monitor Progress
    print("Step 3: Monitoring progress...")
    last_msg = ""
    start_time = time.now()
    timeout = 300 # 5 minutes
    
    while time.now() - start_time < timeout:
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
    # Ensure time.now() replacement if needed, but standard time.time() is better
    import time as t
    time.now = t.time
    run_smoke_test()

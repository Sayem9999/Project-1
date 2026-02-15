
import asyncio
import httpx
import sys
import os
import time

# Configuration
API_URL = "http://localhost:8000/api"
VIDEO_FILE = "backend/tests/fixtures/test_video.mp4" 
INVALID_FILE = "backend/tests/fixtures/invalid_file.txt"

# Auth Helper
TOKEN = None
EMAIL = f"test_{int(time.time())}@example.com"
PASSWORD = "TestPassword123!"

async def get_auth_headers(client):
    global TOKEN
    if TOKEN:
        return {"Authorization": f"Bearer {TOKEN}"}
    
    # Register
    try:
        print(f"DTO Registering {EMAIL}...")
        resp = await client.post(f"{API_URL}/auth/signup", json={"email": EMAIL, "password": PASSWORD, "full_name": "Test User"})
        if resp.status_code == 200:
             print("✅ Registered")
             TOKEN = resp.json()["access_token"]
             return {"Authorization": f"Bearer {TOKEN}"}
        elif resp.status_code == 400 and "already registered" in resp.text:
             print("ℹ️ User already exists")
        else:
             print(f"⚠️ Registration warning: {resp.status_code} {resp.text}")

        # Login
        print("DTO Logging in...")
        resp = await client.post(f"{API_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD})
        resp.raise_for_status()
        TOKEN = resp.json()["access_token"]
        print("✅ Logged In")
        return {"Authorization": f"Bearer {TOKEN}"}
    except Exception as e:
        print(f"❌ Auth Failed: {e}")
        sys.exit(1)

async def test_health():
    print(f"Testing Health Check at {API_URL}/health...")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{API_URL}/health")
            resp.raise_for_status()
            print("✅ Health Check Passed")
        except Exception as e:
            print(f"❌ Health Check Failed: {e}")
            sys.exit(1)

async def test_invalid_upload():
    print("Testing Invalid File Upload...")
    # create dummy invalid file
    os.makedirs("backend/tests/fixtures", exist_ok=True)
    with open(INVALID_FILE, "w") as f:
        f.write("This is not a video.")
    
    async with httpx.AsyncClient() as client:
        headers = await get_auth_headers(client)
        try:
            files = {"file": ("invalid_file.txt", open(INVALID_FILE, "rb"), "text/plain")}
            resp = await client.post(f"{API_URL}/jobs/upload", files=files, headers=headers)
            if resp.status_code == 400:
                print("✅ Invalid Upload Rejected correctly (400)")
            else:
                print(f"❌ Invalid Upload Failed: Expected 400, got {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"❌ Invalid Upload Test Error: {e}")

async def test_concurrency():
    print("Testing Concurrent Uploads (3 requests)...")
    # create dummy video file
    with open(VIDEO_FILE, "wb") as f:
        f.write(os.urandom(1024 * 1024)) # 1MB dummy video

    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = await get_auth_headers(client)
        tasks = []
        for i in range(3):
             files = {"file": (f"test_video_{i}.mp4", open(VIDEO_FILE, "rb"), "video/mp4")}
             tasks.append(client.post(f"{API_URL}/jobs/upload", files=files, headers=headers))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = 0
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                 print(f"❌ Request {i} Failed: {res}")
            elif res.status_code == 200:
                 success_count += 1
                 print(f"✅ Request {i} Succeeded: {res.json().get('id')}")
            else:
                 print(f"❌ Request {i} Failed with status {res.status_code}: {res.text}")
        
        if success_count == 3:
            print("✅ Concurrency Test Passed")
        else:
            print(f"⚠️ Concurrency Test: {success_count}/3 succeeded")
            
async def main():
    print("🚀 Starting Extended E2E Tests...")
    await test_health()
    await test_invalid_upload()
    await test_concurrency()
    print("✅ All Extended Tests Completed.")

if __name__ == "__main__":
    asyncio.run(main())

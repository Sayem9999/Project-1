import asyncio
import aiohttp
import sys
import os

# Configuration
API_URL = "http://localhost:8000/api"
TEST_VIDEO_PATH = "backend/tests/fixtures/sample_video.mp4" # We might need to create this if it doesn't exist

async def run_smoke_test():
    print(f"🔥 Starting MVP Smoke Test against {API_URL}")
    
    async with aiohttp.ClientSession() as session:
        # 1. Health Check
        print("\n1. Checking Health...")
        try:
            async with session.get(f"{API_URL}/health", timeout=5) as resp:
                if resp.status != 200:
                    print(f"❌ API Unhealthy: {resp.status}")
                    return
                data = await resp.json()
                print(f"✅ API Healthy: {data}")
        except Exception as e:
            print(f"❌ API Unreachable: {e}")
            return

        # 2. Login (Admin Bootstrap)
        print("\n2. Authenticating as Admin...")
        
        # Let's try to register a temp user for the test
        user_email = f"test_mvp_{os.getpid()}@example.com"
        password = "Password123!"
        
        try:
            async with session.post(f"{API_URL}/auth/signup", json={
                "email": user_email,
                "password": password
            }) as resp:
                if resp.status not in [200, 400]: # 400 if already exists is fine
                    print(f"❌ Signup Failed: {await resp.text()}")
                    return
                if resp.status == 200:
                     print("✅ User Registered")
                else:
                     print("ℹ️ User exists, proceeding to login")

            async with session.post(f"{API_URL}/auth/login", json={
                "email": user_email,
                "password": password
            }) as resp:
                if resp.status != 200:
                    print(f"❌ Login Failed: {await resp.text()}")
                    return
                token_data = await resp.json()
                token = token_data["access_token"]
                print("✅ Authenticated")
        except Exception as e:
            print(f"❌ Auth Failed: {e}")
            return

        headers = {"Authorization": f"Bearer {token}"}

        # 3. Upload Video
        print("\n3. Uploading Video...")
        # Check if file exists, if not create a dummy one
        if not os.path.exists("dummy_video.mp4"):
            with open("dummy_video.mp4", "wb") as f:
                f.write(b"fake video content" * 1000)
        
        data = aiohttp.FormData()
        data.add_field('file',
                       open('dummy_video.mp4', 'rb'),
                       filename='dummy_video.mp4',
                       content_type='video/mp4')
        data.add_field('theme', 'professional')

        try:
            async with session.post(f"{API_URL}/jobs/upload", data=data, headers=headers) as resp:
                if resp.status != 200:
                    print(f"❌ Upload Failed: {await resp.text()}")
                    return
                job_data = await resp.json()
                job_id = job_data["id"]
                print(f"✅ Video Uploaded (Job ID: {job_id})")
        except Exception as e:
             print(f"❌ Upload Error: {e}")
             return

        # 4. Start Job (if not started automatically)
        # The upload endpoint in schemas.py has start_immediately=True by default in the router?
        # Let's check the status.
        print(f"   Initial Status: {job_data['status']}")

        # 5. Poll for Progress
        print("\n4. Polling for Completion (Timeout: 60s)...")
        for i in range(12): # 12 * 5s = 60s
            try:
                async with session.get(f"{API_URL}/jobs/{job_id}", headers=headers) as resp:
                    job_status = await resp.json()
                    status = job_status["status"]
                    print(f"   [{i*5}s] Status: {status} - {job_status.get('progress_message', '')}")
                    
                    if status == "complete":
                        print("✅ Job Completed Successfully!")
                        return # SUCCESS
                    if status == "failed":
                        print(f"❌ Job Failed: {job_status.get('progress_message')}")
                        return # FAIL (but managed)
            except Exception as e:
                 print(f"⚠️ Polling Error: {e}")
            
            await asyncio.sleep(5)
        else:
             print("⚠️ Timed out waiting for completion")

if __name__ == "__main__":
    try:
        asyncio.run(run_smoke_test())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")

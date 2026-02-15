import asyncio
import sys
import os
import httpx
import json
import logging
from datetime import datetime, timezone

# Add parent dir to path to import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Load env vars before importing config
from dotenv import load_dotenv
load_dotenv()

from app.services.n8n_service import n8n_service
from app.config import settings

# Mock Job Data
MOCK_PAYLOAD = {
    "event": "job.status.changed",
    "job_id": 999,
    "user_id": 1,
    "status": "complete",
    "message": "Test Webhook Trigger from ProEdit",
    "output_path": "https://example.com/test_video.mp4",
    "thumbnail_path": "https://example.com/thumb.jpg",
    "tier": "pro",
    "platform": "youtube",
    "timestamp": datetime.now(timezone.utc).isoformat()
}

async def send_to_url(url: str, client: httpx.AsyncClient):
    print(f"👉 Trying: {url}")
    try:
        resp = await client.post(url, json=MOCK_PAYLOAD, headers={"Content-Type": "application/json"})
        if 200 <= resp.status_code < 300:
            print(f"✅ SUCCESS! Received {resp.status_code}")
            return True
        else:
            print(f"❌ Failed: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    base_url = (settings.n8n_base_url or "http://localhost:5678").rstrip("/")
    path = "proedit/job-status"
    
    # n8n has two URL schemes:
    # 1. Production: /webhook/...
    # 2. Editor Test: /webhook-test/...
    
    prod_url = f"{base_url}/webhook/{path}"
    test_url = f"{base_url}/webhook-test/{path}"
    
    print("🚀 Triggering n8n Webhook Test...")
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        # Try Test URL first (since user is likely "waiting for trigger")
        if await send_to_url(test_url, client):
            print("\n🎉 The n8n Editor captured the event!")
            return

        print("\n⚠️ Test URL failed, trying Production URL...")
        if await send_to_url(prod_url, client):
             print("\n🎉 The Active Workflow captured the event!")
             return

    print("\n❌ Could not trigger n8n. Please check:")
    print("1. Is the Webhook Node set to POST?")
    print(f"2. Is the path set to '{path}'?")
    print("3. Did you click 'Listen for Event'?")

if __name__ == "__main__":
    asyncio.run(main())

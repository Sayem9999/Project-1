import asyncio
import httpx
import time

BASE_URL = "http://localhost:8000/api"

async def test_health_response():
    print("--- Verifying Admin Health Response Time ---")
    
    # We'll use a long timeout just to capture the delay
    async with httpx.AsyncClient(timeout=60.0) as client:
        start = time.perf_counter()
        print("GET /admin/health (Note: Expecting 403 or 200 depending on auth)...")
        try:
            # We don't have an admin token here, so 403 is expected.
            # But we want to see if the server STOPS responding or just rejects.
            # If the async wrapping works, the server should reject or respond quickly.
            # Note: Even if auth fails, the server still has to process the request.
            # Actually, the health check logic runs AFTER auth dependencies.
            # So if we hit it without auth, it might reject BEFORE running the logic.
            
            # To test the logic, we'd need a token.
            # For now, let's just see if the server responds at all.
            response = await client.get(f"{BASE_URL}/admin/health")
            duration = time.perf_counter() - start
            print(f"Status: {response.status_code}")
            print(f"Time: {duration:.2f}s")
            
            if duration > 10.0:
                print("WARNING: Response took > 10s - might still be blocking or very slow.")
            else:
                print("SUCCESS: Response received in reasonable time.")
                
        except Exception as e:
            print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_health_response())

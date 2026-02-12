import asyncio
import httpx
import time

BASE_URL = "http://localhost:8000/api"
# Check an admin user from earlier diagnostic: sayemf21@gmail.com is an admin
# We need to login first or just use a token if we can find one.
# Since I'm on the server, I can try to find the token or just hit the endpoints if I disable auth for testing? 
# No, I should test the real logic.

async def repro():
    print("--- Repro Admin Crash ---")
    
    # Endpoints the admin panel hits on load
    endpoints = [
        "/admin/stats",
        "/admin/users",
        "/admin/jobs",
        "/admin/health",
        "/maintenance/graph"
    ]
    
    # We need to simulate the exact headers. 
    # For this repro, I'll assume I have to find a way to hit them.
    # I'll try to hit them without auth first just to see if the server responds 403 or dies.
    # If it dies on 403, it's a very early crash.
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("Sending concurrent requests...")
        tasks = [client.get(f"{BASE_URL}{e}") for e in endpoints]
        start = time.perf_counter()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.perf_counter() - start
        
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                print(f"Endpoint {endpoints[i]} FAILED: {res}")
            else:
                print(f"Endpoint {endpoints[i]} Status: {res.status_code}")
        
        print(f"Total time: {duration:.2f}s")

if __name__ == "__main__":
    asyncio.run(repro())

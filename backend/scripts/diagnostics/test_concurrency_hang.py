import asyncio
import httpx
import time

BASE_URL = "http://localhost:8000/api"

async def hit_health(i):
    async with httpx.AsyncClient(timeout=30.0) as client:
        start = time.perf_counter()
        try:
            print(f"Request {i} starting...")
            response = await client.get(f"{BASE_URL}/admin/health")
            print(f"Request {i} finished: {response.status_code} in {time.perf_counter() - start:.2f}s")
        except Exception as e:
            print(f"Request {i} failed: {e}")

async def main():
    print("--- Pounding Admin Health with 10 parallel requests ---")
    tasks = [hit_health(i) for i in range(10)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

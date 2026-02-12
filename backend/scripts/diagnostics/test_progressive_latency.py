import asyncio
import httpx
import time

BASE_URL = "http://localhost:8000/api"

async def test_loop():
    print("--- Admin Health Progressive Latency Test ---")
    async with httpx.AsyncClient(timeout=10.0) as client:
        for i in range(20):
            start = time.perf_counter()
            try:
                # Note: hit /health (simple) first to check loop
                res = await client.get("http://localhost:8000/health")
                duration = time.perf_counter() - start
                print(f"[{i}] /health: {res.status_code}, {duration:.4f}s")
                
                # Then hit /admin/health (even if 403)
                start_admin = time.perf_counter()
                res_admin = await client.get(f"{BASE_URL}/admin/health")
                duration_admin = time.perf_counter() - start_admin
                print(f"[{i}] /admin/health: {res_admin.status_code}, {duration_admin:.4f}s")
            except Exception as e:
                print(f"[{i}] ERROR: {e}")
            await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(test_loop())

import os
import sys
import time
from urllib.parse import urlparse

# Add parent dir to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from app.config import settings
from app.celery_app import celery_app

def test_redis():
    url = settings.redis_url
    if not url:
        print("❌ REDIS_URL is not set.")
        return False
    
    print(f"🔗 Testing Redis URL: {url}")
    try:
        import redis
        r = redis.from_url(url, socket_timeout=5, socket_connect_timeout=5)
        start = time.time()
        r.ping()
        print(f"✅ Redis PING success in {time.time() - start:.2f}s")
        return True
    except Exception as e:
        print(f"❌ Redis PING failed: {e}")
        return False

def test_celery_inspect():
    print("🕵️ Inspecting Celery Workers...")
    try:
        start = time.time()
        inspect = celery_app.control.inspect(timeout=2.0)
        
        print("  - Pinging workers...")
        ping_res = inspect.ping()
        print(f"    Ping Response: {ping_res}")
        
        print("  - Checking active queues...")
        queues_res = inspect.active_queues()
        print(f"    Queues Response: {queues_res}")
        
        print(f"✅ Celery inspect completed in {time.time() - start:.2f}s")
        
        if not ping_res:
            print("⚠️ No workers detected. Please start the worker!")
            
    except Exception as e:
        print(f"❌ Celery inspect failed: {e}")

if __name__ == "__main__":
    if test_redis():
        test_celery_inspect()

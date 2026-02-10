"""
WebSocket endpoint for real-time job progress streaming
"""
import os
import json
import asyncio
import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import redis.asyncio as redis

router = APIRouter()

REDIS_URL = os.getenv("REDIS_URL")


@router.websocket("/ws/jobs/{job_id}")
async def job_progress_websocket(websocket: WebSocket, job_id: int):
    """
    WebSocket endpoint for real-time job progress.
    Clients connect and receive progress updates as they happen.
    """
    await websocket.accept()
    
    if not REDIS_URL:
        await websocket.close(code=1000, reason="Redis not configured")
        return

    r = None
    pubsub = None
    try:
        # Connect to Redis
        r = redis.from_url(REDIS_URL, decode_responses=True)
        pubsub = r.pubsub()
        await pubsub.subscribe(f"job:{job_id}:progress")
        
        # Send latest state if available
        latest = await r.get(f"job:{job_id}:latest")
        if latest:
            await websocket.send_text(latest.decode() if isinstance(latest, bytes) else latest)
        
        # Listen for updates
        last_ping = time.monotonic()
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message.get("data"):
                data = message["data"]
                if isinstance(data, bytes):
                    data = data.decode()
                await websocket.send_text(data)
                
                # Check if job is complete/failed
                try:
                    parsed = json.loads(data)
                    if parsed.get("status") in ["complete", "failed"]:
                        break
                except:
                    pass
            else:
                # Send ping to keep connection alive every ~25s
                if time.monotonic() - last_ping > 25:
                    try:
                        await websocket.send_json({"type": "ping"})
                        last_ping = time.monotonic()
                    except:
                        break
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[WebSocket] Error: {e}")
    finally:
        try:
            if pubsub:
                await pubsub.unsubscribe(f"job:{job_id}:progress")
            if r:
                await r.close()
        except:
            pass

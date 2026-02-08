"""
WebSocket endpoint for real-time job progress streaming
"""
import os
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import redis.asyncio as redis

router = APIRouter()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


@router.websocket("/ws/jobs/{job_id}")
async def job_progress_websocket(websocket: WebSocket, job_id: int):
    """
    WebSocket endpoint for real-time job progress.
    Clients connect and receive progress updates as they happen.
    """
    await websocket.accept()
    
    try:
        # Connect to Redis
        r = redis.from_url(REDIS_URL)
        pubsub = r.pubsub()
        await pubsub.subscribe(f"job:{job_id}:progress")
        
        # Send latest state if available
        latest = await r.get(f"job:{job_id}:latest")
        if latest:
            await websocket.send_text(latest.decode() if isinstance(latest, bytes) else latest)
        
        # Listen for updates
        while True:
            message = await asyncio.wait_for(
                pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0),
                timeout=30.0  # Send ping every 30s
            )
            
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
                    
    except asyncio.TimeoutError:
        # Send ping to keep connection alive
        try:
            await websocket.send_json({"type": "ping"})
        except:
            pass
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[WebSocket] Error: {e}")
    finally:
        try:
            await pubsub.unsubscribe(f"job:{job_id}:progress")
            await r.close()
        except:
            pass

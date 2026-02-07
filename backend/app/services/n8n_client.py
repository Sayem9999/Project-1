import httpx
from ..config import settings


async def trigger_edit_workflow(job_id: int, source_path: str) -> None:
    payload = {"job_id": job_id, "source_path": source_path}
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(settings.n8n_webhook_url, json=payload)
        response.raise_for_status()

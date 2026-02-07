import asyncio
import httpx
from ..config import settings


class N8NTriggerError(RuntimeError):
    pass


async def trigger_edit_workflow(job_id: int, source_path: str) -> None:
    payload = {"job_id": job_id, "source_path": source_path}
    last_error: Exception | None = None

    for attempt in range(1, 4):
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(settings.n8n_webhook_url, json=payload)
                response.raise_for_status()
                return
        except (httpx.HTTPError, httpx.NetworkError) as exc:
            last_error = exc
            if attempt < 3:
                await asyncio.sleep(1.5 * attempt)

    raise N8NTriggerError(f"Failed to trigger n8n workflow after retries: {last_error}")

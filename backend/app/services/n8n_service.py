from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone

import httpx

from ..config import settings
from ..models import Job

logger = logging.getLogger(__name__)


class N8NService:
    """Outbound n8n webhook client with timeout, retries, and HMAC signature."""

    def _build_url(self) -> str | None:
        base = (settings.n8n_base_url or "").strip().rstrip("/")
        path = (settings.n8n_job_status_path or "").strip()
        if not base:
            return None
        if not path:
            return base
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{base}{path}"

    @staticmethod
    def _canonical_body(payload: dict) -> bytes:
        return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")

    def _signature(self, timestamp: str, body: bytes) -> str | None:
        secret = settings.n8n_webhook_secret
        if not secret:
            return None
        message = timestamp.encode("utf-8") + b"." + body
        digest = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()
        return f"sha256={digest}"

    async def trigger_orchestration(self, job: Job) -> bool:
        """
        Notifies n8n that a job has entered the Clawdbot/OpenClaw phase.
        This signals n8n to start fetching context and generating a strategy.
        """
        url = self._build_url()
        if not url:
            return False

        now = datetime.now(timezone.utc).isoformat()
        payload = {
            "event": "job.orchestration.required",
            "job_id": job.id,
            "user_id": job.user_id,
            "status": job.status,
            "message": job.progress_message,
            "tier": job.tier,
            "mood": job.mood,
            "pacing": job.pacing,
            "ratio": job.ratio,
            "platform": job.platform,
            "timestamp": now,
        }
        
        body = self._canonical_body(payload)
        event_id = f"job-{job.id}-orchestration-{now}"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "proedit-backend/n8n-orchestrator",
            "X-ProEdit-Timestamp": now,
            "X-ProEdit-Event-Id": event_id,
        }
        signature = self._signature(now, body)
        if signature:
            headers["X-ProEdit-Signature"] = signature

        timeout = max(0.1, float(settings.n8n_timeout_seconds))
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, content=body, headers=headers)
                return 200 <= response.status_code < 300
        except Exception as exc:
            logger.warning("n8n_orchestration_trigger_failed", extra={"error": str(exc)})
            return False

    async def send_job_status_event(self, job: Job) -> bool:
        """Send terminal job status to n8n. Returns False on any delivery failure."""
        url = self._build_url()
        if not url:
            return False
        if job.status not in {"complete", "failed"}:
            return False

        now = datetime.now(timezone.utc).isoformat()
        payload = {
            "event": "job.status.changed",
            "job_id": job.id,
            "user_id": job.user_id,
            "status": job.status,
            "message": job.progress_message,
            "output_path": job.output_path,
            "thumbnail_path": job.thumbnail_path,
            "tier": job.tier,
            "platform": job.platform,
            "director_plan": getattr(job, "director_plan", None),
            "qc_result": getattr(job, "qc_result", None),
            "scout_result": getattr(job, "scout_result", None),
            "brand_safety_result": getattr(job, "brand_safety_result", None),
            "post_settings": getattr(job, "post_settings", None),
            "audio_qa": getattr(job, "audio_qa", None),
            "color_qa": getattr(job, "color_qa", None),
            "subtitle_qa": getattr(job, "subtitle_qa", None),
            "timestamp": now,
        }
        body = self._canonical_body(payload)
        event_id = f"job-{job.id}-{job.status}-{now}"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "proedit-backend/n8n-webhook",
            "X-ProEdit-Timestamp": now,
            "X-ProEdit-Event-Id": event_id,
        }
        signature = self._signature(now, body)
        if signature:
            headers["X-ProEdit-Signature"] = signature

        retries = max(0, int(settings.n8n_retry_attempts))
        timeout = max(0.1, float(settings.n8n_timeout_seconds))
        backoff = max(0.0, float(settings.n8n_retry_backoff_seconds))

        for attempt in range(retries + 1):
            try:
                headers["X-ProEdit-Attempt"] = str(attempt + 1)
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(url, content=body, headers=headers)

                if 200 <= response.status_code < 300:
                    return True

                if response.status_code < 500:
                    logger.warning("n8n_webhook_non_retryable", extra={"status_code": response.status_code})
                    return False
            except Exception as exc:
                logger.warning("n8n_webhook_request_failed", extra={"attempt": attempt + 1, "error": str(exc)})

            if attempt < retries and backoff > 0:
                # Exponential backoff: b, 2b, 4b...
                await asyncio.sleep(backoff * (2 ** attempt))

        return False


n8n_service = N8NService()

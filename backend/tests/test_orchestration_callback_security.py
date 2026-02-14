import hashlib
import hmac
import json
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient

from app.config import settings
from app.models import Job, JobStatus, ProcessedWebhook


def _signed_headers(secret: str, body: bytes, event_id: str, timestamp: str | None = None) -> dict[str, str]:
    ts = timestamp or datetime.now(timezone.utc).isoformat()
    sig = "sha256=" + hmac.new(
        secret.encode("utf-8"),
        ts.encode("utf-8") + b"." + body,
        hashlib.sha256,
    ).hexdigest()
    return {
        "X-ProEdit-Timestamp": ts,
        "X-ProEdit-Signature": sig,
        "X-ProEdit-Event-Id": event_id,
        "Content-Type": "application/json",
    }


@pytest.mark.asyncio
async def test_orchestration_callback_accepts_valid_signature(client: AsyncClient, session, monkeypatch):
    signup = {"email": "orch-callback-valid@example.com", "password": "SecurePassword123"}
    res = await client.post("/api/auth/signup", json=signup)
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me = await client.get("/api/auth/me", headers=headers)
    user_id = me.json()["id"]

    job = Job(
        user_id=user_id,
        source_path="https://example.com/source.mp4",
        status=JobStatus.processing,
        theme="professional",
        tier="pro",
        pacing="medium",
        mood="professional",
        ratio="16:9",
        platform="youtube",
        brand_safety="standard",
        progress_message="Processing",
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    async def fake_render_orchestrated_job(*args, **kwargs):
        return None

    import app.services.workflow_engine as workflow_engine

    monkeypatch.setattr(workflow_engine, "render_orchestrated_job", fake_render_orchestrated_job)
    monkeypatch.setattr(settings, "orchestration_webhook_secret", "orchestration-secret", raising=False)

    payload = {
        "job_id": job.id,
        "user_id": user_id,
        "cuts": [{"start": 0.0, "end": 2.0, "reason": "hook"}],
        "vf_filters": "eq=contrast=1.1",
        "af_filters": "loudnorm=I=-16:TP=-1.5:LRA=11",
    }
    body = json.dumps(payload, separators=(",", ":"), sort_keys=False).encode("utf-8")
    callback_headers = _signed_headers("orchestration-secret", body, event_id="evt-valid-1")

    res = await client.post(f"/api/orchestration/callback/{job.id}", content=body, headers=callback_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "success"

    processed = await session.get(ProcessedWebhook, "evt-valid-1")
    assert processed is not None


@pytest.mark.asyncio
async def test_orchestration_callback_rejects_invalid_signature(client: AsyncClient, session, monkeypatch):
    signup = {"email": "orch-callback-invalid@example.com", "password": "SecurePassword123"}
    res = await client.post("/api/auth/signup", json=signup)
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me = await client.get("/api/auth/me", headers=headers)
    user_id = me.json()["id"]

    job = Job(
        user_id=user_id,
        source_path="https://example.com/source.mp4",
        status=JobStatus.processing,
        theme="professional",
        tier="pro",
        pacing="medium",
        mood="professional",
        ratio="16:9",
        platform="youtube",
        brand_safety="standard",
        progress_message="Processing",
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    monkeypatch.setattr(settings, "orchestration_webhook_secret", "orchestration-secret", raising=False)
    payload = {"job_id": job.id, "user_id": user_id, "cuts": [{"start": 0.0, "end": 2.0}]}
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "X-ProEdit-Timestamp": datetime.now(timezone.utc).isoformat(),
        "X-ProEdit-Signature": "sha256=deadbeef",
        "X-ProEdit-Event-Id": "evt-invalid-1",
        "Content-Type": "application/json",
    }

    res = await client.post(f"/api/orchestration/callback/{job.id}", content=body, headers=headers)
    assert res.status_code == 401
    assert "Invalid orchestration signature" in res.text


@pytest.mark.asyncio
async def test_orchestration_callback_blocks_replay(client: AsyncClient, session, monkeypatch):
    signup = {"email": "orch-callback-replay@example.com", "password": "SecurePassword123"}
    res = await client.post("/api/auth/signup", json=signup)
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me = await client.get("/api/auth/me", headers=headers)
    user_id = me.json()["id"]

    job = Job(
        user_id=user_id,
        source_path="https://example.com/source.mp4",
        status=JobStatus.processing,
        theme="professional",
        tier="pro",
        pacing="medium",
        mood="professional",
        ratio="16:9",
        platform="youtube",
        brand_safety="standard",
        progress_message="Processing",
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    async def fake_render_orchestrated_job(*args, **kwargs):
        return None

    import app.services.workflow_engine as workflow_engine

    monkeypatch.setattr(workflow_engine, "render_orchestrated_job", fake_render_orchestrated_job)
    monkeypatch.setattr(settings, "orchestration_webhook_secret", "orchestration-secret", raising=False)

    payload = {"job_id": job.id, "user_id": user_id, "cuts": [{"start": 0.0, "end": 2.0}]}
    body = json.dumps(payload).encode("utf-8")
    callback_headers = _signed_headers("orchestration-secret", body, event_id="evt-replay-1")

    first = await client.post(f"/api/orchestration/callback/{job.id}", content=body, headers=callback_headers)
    assert first.status_code == 200
    assert first.json()["status"] == "success"

    second = await client.post(f"/api/orchestration/callback/{job.id}", content=body, headers=callback_headers)
    assert second.status_code == 200
    assert second.json()["status"] == "duplicate"

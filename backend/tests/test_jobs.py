import pytest
from httpx import AsyncClient
from fastapi import HTTPException
from types import SimpleNamespace
from unittest.mock import patch
from sqlalchemy import select
from app.models import User, Job, JobStatus
import app.routers.jobs as jobs_router

# Fixtures from conftest.py

@pytest.mark.asyncio
async def test_job_permissions(client: AsyncClient, session):
    # Create User A
    signup_a = {"email": "userA@example.com", "password": "SecurePassword123"}
    res = await client.post("/api/auth/signup", json=signup_a)
    token_a = res.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    # Create User B
    signup_b = {"email": "userB@example.com", "password": "SecurePassword123"}
    res = await client.post("/api/auth/signup", json=signup_b)
    token_b = res.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A creates a job (simulate via DB to avoid mocking upload again if possible, or use upload endpoint)
    # Using DB directly is faster and cleaner for permission testing
    
    # Get User A ID
    res = await client.get("/api/auth/me", headers=headers_a)
    user_a_id = res.json()["id"]

    # Create dummy job for User A
    job = Job(
        user_id=user_a_id,
        source_path="uploads/test_video.mp4",
        status=JobStatus.complete,
        theme="professional",
        progress_message="Done",
        output_path="outputs/test_job.mp4"
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)
    job_id = job.id

    # User A can get their job
    res = await client.get(f"/api/jobs/{job_id}", headers=headers_a)
    assert res.status_code == 200
    assert res.json()["id"] == job_id

    # User B CANNOT get User A's job
    res = await client.get(f"/api/jobs/{job_id}", headers=headers_b)
    # Expect 404 (Not Found) commonly preferred over 403 to avoid leaking existence, 
    # but 403 is also acceptable depending on implementation.
    # checking jobs.py will confirm.
    assert res.status_code in [403, 404]


@pytest.mark.asyncio
async def test_enqueue_job_production_fails_if_celery_disabled(monkeypatch):
    job = SimpleNamespace(id=1, source_path="uploads/test_video.mp4")
    monkeypatch.setattr(jobs_router, "USE_CELERY", False)
    monkeypatch.setattr(jobs_router.settings, "environment", "production", raising=False)

    with pytest.raises(HTTPException) as exc:
        await jobs_router.enqueue_job(
            job,
            pacing="medium",
            mood="professional",
            ratio="16:9",
            tier="pro",
            platform="youtube",
            brand_safety="standard",
        )

    assert exc.value.status_code == 503
    assert "Queue dispatch unavailable" in str(exc.value.detail)


@pytest.mark.asyncio
async def test_enqueue_job_production_fails_if_celery_dispatch_errors(monkeypatch):
    job = SimpleNamespace(id=1, source_path="uploads/test_video.mp4")
    monkeypatch.setattr(jobs_router, "USE_CELERY", True)
    monkeypatch.setattr(jobs_router.settings, "environment", "production", raising=False)

    with patch("app.tasks.video_tasks.process_video_task") as mock_task:
        mock_task.delay.side_effect = RuntimeError("redis down")

        with pytest.raises(HTTPException) as exc:
            await jobs_router.enqueue_job(
                job,
                pacing="medium",
                mood="professional",
                ratio="16:9",
                tier="pro",
                platform="youtube",
                brand_safety="standard",
            )

    assert exc.value.status_code == 503
    assert "Queue dispatch failed" in str(exc.value.detail)

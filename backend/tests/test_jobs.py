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
    monkeypatch.setattr(
        jobs_router,
        "get_celery_dispatch_diagnostics",
        lambda timeout=1.5: {
            "broker": "rediss://broker:6379/0",
            "worker_count": 1,
            "workers": ["celery@test"],
            "queues": {"celery@test": ["video", "celery"]},
        },
    )

    with patch("app.tasks.video_tasks.process_video_task") as mock_task:
        mock_task.apply_async.side_effect = RuntimeError("redis down")

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


@pytest.mark.asyncio
async def test_enqueue_job_production_fails_if_no_active_workers(monkeypatch):
    job = SimpleNamespace(id=1, source_path="uploads/test_video.mp4")
    monkeypatch.setattr(jobs_router, "USE_CELERY", True)
    monkeypatch.setattr(jobs_router.settings, "environment", "production", raising=False)
    monkeypatch.setattr(
        jobs_router,
        "get_celery_dispatch_diagnostics",
        lambda timeout=1.5: {
            "broker": "rediss://broker:6379/0",
            "worker_count": 0,
            "workers": [],
            "queues": {},
        },
    )

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
    assert "No active Celery worker reachable" in str(exc.value.detail)


@pytest.mark.asyncio
async def test_enqueue_job_production_fails_if_no_video_queue_consumer(monkeypatch):
    job = SimpleNamespace(id=1, source_path="uploads/test_video.mp4")
    monkeypatch.setattr(jobs_router, "USE_CELERY", True)
    monkeypatch.setattr(jobs_router.settings, "environment", "production", raising=False)
    monkeypatch.setattr(
        jobs_router,
        "get_celery_dispatch_diagnostics",
        lambda timeout=1.5: {
            "broker": "rediss://broker:6379/0",
            "worker_count": 1,
            "workers": ["celery@test"],
            "queues": {"celery@test": ["celery"]},
        },
    )

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
    assert "No active Celery worker subscribed to 'video' queue" in str(exc.value.detail)


@pytest.mark.asyncio
async def test_upload_persists_post_settings(client: AsyncClient, session, monkeypatch):
    signup = {"email": "upload-post@example.com", "password": "SecurePassword123"}
    res = await client.post("/api/auth/signup", json=signup)
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    async def mock_save_upload(_file):
        return "uploads/mock_source.mp4"

    monkeypatch.setattr(jobs_router.storage_service, "save_upload", mock_save_upload)

    res = await client.post(
        "/api/jobs/upload",
        headers=headers,
        files={"file": ("clip.mp4", b"fake-video-content", "video/mp4")},
        data={
            "theme": "cinematic",
            "pacing": "fast",
            "mood": "energetic",
            "ratio": "9:16",
            "platform": "tiktok",
            "tier": "pro",
            "brand_safety": "strict",
            "transition_style": "wipe",
            "transition_duration": "0.4",
            "speed_profile": "fast",
            "subtitle_preset": "social",
            "color_profile": "cinematic",
            "skin_protect_strength": "0.7",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["post_settings"]["transition_style"] == "wipe"
    assert data["post_settings"]["speed_profile"] == "fast"
    assert data["post_settings"]["subtitle_preset"] == "social"

    job = await session.get(Job, data["id"])
    assert job is not None
    assert job.post_settings["transition_style"] == "wipe"
    assert float(job.post_settings["transition_duration"]) == 0.4
    assert float(job.post_settings["skin_protect_strength"]) == 0.7


@pytest.mark.asyncio
async def test_start_job_returns_without_waiting_for_queue_dispatch(client: AsyncClient, session, monkeypatch):
    """Regression: /jobs/{id}/start must not hang if Celery broker/dispatch is slow."""
    signup = {"email": "start-nonblock@example.com", "password": "SecurePassword123"}
    res = await client.post("/api/auth/signup", json=signup)
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me = await client.get("/api/auth/me", headers=headers)
    user_id = me.json()["id"]

    # Create queued job directly (avoid upload mocking complexity here).
    job = Job(
        user_id=user_id,
        # Use http URL to skip local file existence checks in /start.
        source_path="http://example.com/test.mp4",
        status=JobStatus.queued,
        theme="professional",
        progress_message="Awaiting manual start.",
        tier="pro",
        pacing="medium",
        mood="professional",
        ratio="16:9",
        platform="youtube",
        brand_safety="standard",
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    async def slow_enqueue(*args, **kwargs):
        # Simulate slow broker/dispatch; endpoint should still return promptly (bounded wait + fallback).
        import asyncio
        await asyncio.sleep(10)

    async def noop_dispatch(*args, **kwargs):
        return None

    monkeypatch.setattr(jobs_router, "enqueue_job", slow_enqueue)
    monkeypatch.setattr(jobs_router, "_dispatch_job_background", noop_dispatch)

    res = await client.post(f"/api/jobs/{job.id}/start", headers=headers)
    assert res.status_code == 200

    refreshed = await session.get(Job, job.id)
    assert refreshed is not None
    assert refreshed.status == JobStatus.processing


@pytest.mark.asyncio
async def test_edit_persists_post_settings(client: AsyncClient, session):
    signup = {"email": "edit-post@example.com", "password": "SecurePassword123"}
    res = await client.post("/api/auth/signup", json=signup)
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me = await client.get("/api/auth/me", headers=headers)
    user_id = me.json()["id"]

    source_job = Job(
        user_id=user_id,
        source_path="https://example.com/source.mp4",
        status=JobStatus.complete,
        theme="professional",
        tier="pro",
        pacing="medium",
        mood="professional",
        ratio="16:9",
        platform="youtube",
        brand_safety="standard",
        progress_message="Done",
    )
    session.add(source_job)
    await session.commit()
    await session.refresh(source_job)

    res = await client.post(
        f"/api/jobs/{source_job.id}/edit",
        headers=headers,
        json={
            "theme": "modern",
            "pacing": "slow",
            "mood": "cinematic",
            "ratio": "1:1",
            "platform": "instagram",
            "tier": "pro",
            "brand_safety": "strict",
            "transition_style": "dissolve",
            "transition_duration": 0.3,
            "speed_profile": "balanced",
            "subtitle_preset": "broadcast",
            "color_profile": "natural",
            "skin_protect_strength": 0.6,
        },
    )
    assert res.status_code == 200
    payload = res.json()
    assert payload["post_settings"]["subtitle_preset"] == "broadcast"
    assert float(payload["post_settings"]["transition_duration"]) == 0.3

    created_job = await session.get(Job, payload["id"])
    assert created_job is not None
    assert created_job.post_settings["color_profile"] == "natural"
    assert float(created_job.post_settings["skin_protect_strength"]) == 0.6


@pytest.mark.asyncio
async def test_upload_normalizes_invalid_post_settings(client: AsyncClient, session, monkeypatch):
    signup = {"email": "upload-post-invalid@example.com", "password": "SecurePassword123"}
    res = await client.post("/api/auth/signup", json=signup)
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    async def mock_save_upload(_file):
        return "uploads/mock_source.mp4"

    monkeypatch.setattr(jobs_router.storage_service, "save_upload", mock_save_upload)

    res = await client.post(
        "/api/jobs/upload",
        headers=headers,
        files={"file": ("clip.mp4", b"fake-video-content", "video/mp4")},
        data={
            "transition_style": "unknown",
            "transition_duration": "99",
            "speed_profile": "ultra",
            "subtitle_preset": "none",
            "color_profile": "retro",
            "skin_protect_strength": "-5",
        },
    )
    assert res.status_code == 200
    payload = res.json()
    post = payload["post_settings"]
    assert post["transition_style"] == "dissolve"
    assert post["speed_profile"] == "balanced"
    assert post["subtitle_preset"] == "platform_default"
    assert post["color_profile"] == "natural"
    assert float(post["transition_duration"]) == 1.5
    assert float(post["skin_protect_strength"]) == 0.0


@pytest.mark.asyncio
async def test_edit_rejects_invalid_post_settings_enum(client: AsyncClient, session):
    signup = {"email": "edit-post-invalid@example.com", "password": "SecurePassword123"}
    res = await client.post("/api/auth/signup", json=signup)
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me = await client.get("/api/auth/me", headers=headers)
    user_id = me.json()["id"]

    source_job = Job(
        user_id=user_id,
        source_path="https://example.com/source.mp4",
        status=JobStatus.complete,
        theme="professional",
        tier="pro",
        pacing="medium",
        mood="professional",
        ratio="16:9",
        platform="youtube",
        brand_safety="standard",
        progress_message="Done",
    )
    session.add(source_job)
    await session.commit()
    await session.refresh(source_job)

    res = await client.post(
        f"/api/jobs/{source_job.id}/edit",
        headers=headers,
        json={
            "transition_style": "invalid-transition",
        },
    )
    assert res.status_code == 422

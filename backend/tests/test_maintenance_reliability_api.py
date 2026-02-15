import pytest

from app.config import settings
from app.models import Job, JobStatus, User


@pytest.mark.asyncio
async def test_timeout_reliability_summary_taxonomy_and_alerts(client, session, monkeypatch):
    signup = {"email": "admin-reliability@example.com", "password": "SecurePassword123"}
    res = await client.post("/api/auth/signup", json=signup)
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me = await client.get("/api/auth/me", headers=headers)
    user_id = me.json()["id"]

    user = await session.get(User, user_id)
    user.is_admin = True
    session.add(user)
    await session.flush()

    session.add_all(
        [
            Job(
                user_id=user_id,
                source_path="storage/uploads/a.mp4",
                status=JobStatus.complete,
                progress_message="complete",
                performance_metrics={"stage_timeout_total": 0, "stage_timeout_counts": {}},
            ),
            Job(
                user_id=user_id,
                source_path="storage/uploads/b.mp4",
                status=JobStatus.complete,
                progress_message="complete degraded",
                performance_metrics={"stage_timeout_total": 2, "stage_timeout_counts": {"director": 2}},
            ),
            Job(
                user_id=user_id,
                source_path="storage/uploads/c.mp4",
                status=JobStatus.complete,
                progress_message="complete degraded",
                performance_metrics={"stage_timeout_total": 1, "stage_timeout_counts": {"audio": 1}},
            ),
            Job(
                user_id=user_id,
                source_path="storage/uploads/d.mp4",
                status=JobStatus.failed,
                progress_message="Processing failed: provider timeout unavailable",
                performance_metrics={"stage_timeout_total": 0, "stage_timeout_counts": {}},
            ),
            Job(
                user_id=user_id,
                source_path="storage/uploads/e.mp4",
                status=JobStatus.failed,
                progress_message="Processing failed: ffmpeg filter graph error",
                performance_metrics={"stage_timeout_total": 0, "stage_timeout_counts": {}},
            ),
        ]
    )
    await session.commit()

    monkeypatch.setattr(settings, "reliability_max_timeouts_per_job", 1)
    monkeypatch.setattr(settings, "reliability_timeout_rate_threshold", 0.2)
    monkeypatch.setattr(settings, "reliability_stage_timeout_spike_threshold", 2)

    response = await client.get(
        "/api/maintenance/reliability/timeout-summary?recent_jobs=10",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()

    assert body["summary"]["timeout_jobs"] == 2
    assert body["summary"]["timeout_events"] == 3
    assert body["summary"]["taxonomy"] == {
        "timeout_degraded_success": 2,
        "hard_failure": 1,
        "external_dependency_outage": 1,
    }
    assert body["summary"]["top_timeout_stages"][0] == {"stage": "director", "timeout_count": 2}

    alert_types = {item["type"] for item in body["alerts"]}
    assert "max_timeouts_per_job_exceeded" in alert_types
    assert "timeout_rate_exceeded" in alert_types
    assert "stage_timeout_spike" in alert_types


@pytest.mark.asyncio
async def test_timeout_reliability_summary_requires_admin(client):
    signup = {"email": "non-admin-reliability@example.com", "password": "SecurePassword123"}
    res = await client.post("/api/auth/signup", json=signup)
    token = res.json()["access_token"]

    response = await client.get(
        "/api/maintenance/reliability/timeout-summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403

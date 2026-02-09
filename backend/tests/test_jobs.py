import pytest
from httpx import AsyncClient
from sqlalchemy import select
from app.models import User, Job, JobStatus

# Fixtures from conftest.py

@pytest.mark.asyncio
async def test_job_permissions(client: AsyncClient, session):
    # Create User A
    signup_a = {"email": "userA@example.com", "password": "password123"}
    res = await client.post("/api/auth/signup", json=signup_a)
    token_a = res.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    # Create User B
    signup_b = {"email": "userB@example.com", "password": "password123"}
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

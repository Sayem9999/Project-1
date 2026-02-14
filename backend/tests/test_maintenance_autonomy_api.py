import pytest
from httpx import AsyncClient

from app.models import User


@pytest.mark.asyncio
async def test_autonomy_status_profile_run_and_audit_log(client: AsyncClient, session, monkeypatch):
    signup = {"email": "admin-autonomy@example.com", "password": "SecurePassword123"}
    res = await client.post("/api/auth/signup", json=signup)
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me = await client.get("/api/auth/me", headers=headers)
    user_id = me.json()["id"]

    user = await session.get(User, user_id)
    user.is_admin = True
    session.add(user)
    await session.commit()

    # Status
    status = await client.get("/api/maintenance/autonomy/status", headers=headers)
    assert status.status_code == 200
    assert "profile_mode" in status.json()

    # Set profile
    profile = await client.post("/api/maintenance/autonomy/profile?mode=aggressive", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["profile_mode"] == "aggressive"

    # Run autonomy with force flags
    run = await client.post(
        "/api/maintenance/autonomy/run?force_heal=true&force_improve=true",
        headers=headers,
    )
    assert run.status_code == 200
    body = run.json()
    assert body["heal_ran"] is True
    assert body["improve_ran"] is True

    # Verify admin audit trail exists
    audit = await client.get("/api/admin/audit/actions?action_prefix=autonomy", headers=headers)
    assert audit.status_code == 200
    rows = audit.json()
    assert any(item["action"] == "autonomy.profile.set" for item in rows)
    assert any(item["action"] == "autonomy.run" for item in rows)

    # Filter API by exact action
    only_runs = await client.get("/api/admin/audit/actions?action=autonomy.run", headers=headers)
    assert only_runs.status_code == 200
    run_rows = only_runs.json()
    assert run_rows
    assert all(item["action"] == "autonomy.run" for item in run_rows)

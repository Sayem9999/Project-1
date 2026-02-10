import pytest
from httpx import AsyncClient

# Fixtures are provided by conftest.py

@pytest.mark.asyncio
async def test_signup(client: AsyncClient):
    payload = {"email": "test@example.com", "password": "SecurePassword123"}
    response = await client.post("/api/auth/signup", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient):
    payload = {"email": "duplicate@example.com", "password": "SecurePassword123"}
    # First signup
    await client.post("/api/auth/signup", json=payload)
    # Second signup
    response = await client.post("/api/auth/signup", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"]["message"] == "Email already registered"
    assert response.json()["detail"]["error_code"] == "email_already_exists"

@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    # Setup user
    signup_payload = {"email": "login@example.com", "password": "SecurePassword123"}
    await client.post("/api/auth/signup", json=signup_payload)

    # Login
    login_payload = {"email": "login@example.com", "password": "SecurePassword123"}
    response = await client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    login_payload = {"email": "nonexistent@example.com", "password": "wrongpassword"}
    response = await client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 401
    assert response.json()["detail"]["message"] == "Invalid credentials"
    assert response.json()["detail"]["error_code"] == "auth_failed"

@pytest.mark.asyncio
async def test_me_endpoint(client: AsyncClient):
    # Setup user
    signup_payload = {"email": "me@example.com", "password": "SecurePassword123"}
    signup_res = await client.post("/api/auth/signup", json=signup_payload)
    token = signup_res.json()["access_token"]

    # Access /me with token
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert "credits" in data

@pytest.mark.asyncio
async def test_me_endpoint_unauthorized(client: AsyncClient):
    response = await client.get("/api/auth/me")
    # HTTPBearer(auto_error=True) returns 403 when no credentials are provided
    assert response.status_code == 403

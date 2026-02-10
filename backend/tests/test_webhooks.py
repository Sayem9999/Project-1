import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock, patch
from sqlalchemy import select
from app.models import User

# Fixtures from conftest.py

@pytest.mark.asyncio
async def test_stripe_webhook_add_credits(client: AsyncClient, session):
    # Create user first
    signup_payload = {"email": "payer@example.com", "password": "SecurePassword123"}
    res = await client.post("/api/auth/signup", json=signup_payload)
    token = res.json()["access_token"]
    
    # Get user ID
    res = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    user_id = res.json()["id"]

    # Mock Stripe Webhook
    mock_event = {
        "id": "evt_test_123",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "client_reference_id": str(user_id),
                "metadata": {"credits": "50"}
            }
        }
    }

    with patch("stripe.Webhook.construct_event", return_value=mock_event):
        with patch("app.routers.payments.settings") as mock_settings:
            mock_settings.stripe_webhook_secret = "whsec_test_secret"
            
            # Send webhook
            headers = {"Stripe-Signature": "test_signature"}
            res = await client.post("/api/payments/webhook", json=mock_event, headers=headers)
            assert res.status_code == 200
            assert res.json()["status"] == "success"

            # Verify credits updated
            res = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
            assert res.json()["credits"] == 10 + 50  # 60

            # Test Idempotency: Send same event ID again
            res = await client.post("/api/payments/webhook", json=mock_event, headers=headers)
            assert res.status_code == 200
            
            # Verify credits NOT updated (should still be 60)
            # NOTE: This requires backend implementation of idempotency check (e.g. check event ID in DB)
            # If backend doesn't support it yet, this test will fail if it adds credits again (110).
            # We will assume for now we need to implement the fix if it fails or just verify current behavior.
            res = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
            assert res.json()["credits"] == 60

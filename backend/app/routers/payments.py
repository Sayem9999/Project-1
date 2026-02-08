import os
import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from ..deps import get_current_user
from ..models import User

router = APIRouter(prefix="/payments", tags=["payments"])

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
PRICE_ID_PRO = os.getenv("STRIPE_PRICE_ID_PRO") # e.g. price_H5ggYJ...
FRONTEND_URL = os.getenv("NEXT_PUBLIC_APP_URL", "http://localhost:3000")


@router.get("/debug")
async def debug_payments():
    return {"status": "ok", "stripe_key_configured": bool(settings.stripe_secret_key)}

@router.post("/create-checkout-session")
async def create_checkout_session(
    current_user: User = Depends(get_current_user)
):
    """
    Create a Stripe Checkout Session for buying credits.
    """
    if not stripe.api_key:
        raise HTTPException(status_code=503, detail="Stripe not configured")
        
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": PRICE_ID_PRO, # Ensure this env var is set
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=f"{FRONTEND_URL}/dashboard?credits_added=true",
            cancel_url=f"{FRONTEND_URL}/pricing",
            client_reference_id=str(current_user.id),
            metadata={
                "user_id": str(current_user.id),
                "credits": "10" # Grant 10 credits for this pack
            }
        )
        return {"url": checkout_session.url}
    except Exception as e:
        print(f"[Stripe] Checkout Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None), session: AsyncSession = Depends(get_session)):
    """
    Handle Stripe Webhooks (e.g. checkout.session.completed)
    """
    if not WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Webhook secret not configured")

    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event["type"] == "checkout.session.completed":
        session_data = event["data"]["object"]
        
        # Extract user_id and credits from metadata
        user_id = session_data.get("client_reference_id")
        metadata = session_data.get("metadata", {})
        credits_to_add = int(metadata.get("credits", 0))
        
        if user_id and credits_to_add > 0:
            print(f"[Stripe] Adding {credits_to_add} credits to user {user_id}")
            # Update User Credits
            stmt = select(User).where(User.id == int(user_id))
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                user.credits = (user.credits or 0) + credits_to_add
                session.add(user)
                await session.commit()
                print(f"[Stripe] Success! User {user_id} now has {user.credits} credits.")
            else:
                print(f"[Stripe] Error: User {user_id} not found.")

    return {"status": "success"}

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from ..deps import get_current_user
from ..models import User, ProcessedWebhook
from ..config import settings

router = APIRouter(prefix="/payments", tags=["payments"])

# Initialize Stripe if keys are present
if settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key

@router.get("/debug")
async def debug_payments():
    return {
        "status": "ok", 
        "stripe_key_configured": bool(settings.stripe_secret_key),
        "webhook_secret_configured": bool(settings.stripe_webhook_secret),
        "price_id_configured": bool(settings.stripe_price_id_pro)
    }

@router.post("/create-checkout-session")
async def create_checkout_session(
    current_user: User = Depends(get_current_user)
):
    """
    Create a Stripe Checkout Session for buying credits.
    """
    if not settings.stripe_secret_key or not settings.stripe_price_id_pro:
        raise HTTPException(status_code=503, detail="Stripe payments are not currently configured.")
        
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": settings.stripe_price_id_pro,
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=f"{settings.frontend_url}/dashboard?credits_added=true",
            cancel_url=f"{settings.frontend_url}/pricing",
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
    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=503, detail="Webhook secret not configured")

    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.stripe_webhook_secret
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Idempotency Check
    event_id = event.get("id")
    if event_id:
        existing = await session.get(ProcessedWebhook, event_id)
        if existing:
            return {"status": "success", "message": "Already processed"}

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
                
                # Mark as processed
                if event_id:
                    session.add(ProcessedWebhook(id=event_id))
                    
                await session.commit()
                print(f"[Stripe] Success! User {user_id} now has {user.credits} credits.")
            else:
                print(f"[Stripe] Error: User {user_id} not found.")

    return {"status": "success"}

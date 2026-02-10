from fastapi import APIRouter, HTTPException, Query
import httpx
from sqlalchemy import select

from ..config import settings
from ..db import AsyncSession as DBSession, engine
from ..models import User
from ..security import generate_access_token

router = APIRouter(prefix="/auth/oauth", tags=["oauth"])


@router.get("/google")
async def google_login():
    """Redirect to Google OAuth consent screen."""
    if not settings.google_client_id:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")
    
    redirect_uri = f"{settings.frontend_url}/auth/callback/google"
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={settings.google_client_id}"
        f"&redirect_uri={redirect_uri}"
        "&response_type=code"
        "&scope=openid%20email%20profile"
        "&access_type=offline"
    )
    return {"auth_url": google_auth_url}


@router.post("/google/callback")
async def google_callback(code: str = Query(...)):
    """Exchange Google auth code for user info and create/login user."""
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")
    
    redirect_uri = f"{settings.frontend_url}/auth/callback/google"
    print(f"[OAuth] Exchanging code, redirect_uri: {redirect_uri}")
    
    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")
        
        tokens = token_response.json()
        access_token = tokens.get("access_token")
        
        # Get user info
        userinfo_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        
        if userinfo_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        userinfo = userinfo_response.json()
    
    # Create or update user
    async with DBSession(engine) as session:
        user = await session.scalar(
            select(User).where(
                (User.oauth_provider == "google") & (User.oauth_id == str(userinfo["id"]))
            )
        )
        
        if not user:
            # Check if email already exists
            user = await session.scalar(select(User).where(User.email == userinfo["email"]))
            if user:
                # Link OAuth to existing account
                user.oauth_provider = "google"
                user.oauth_id = str(userinfo["id"])
                user.name = userinfo.get("name")
                user.avatar_url = userinfo.get("picture")
            else:
                # Create new user
                user = User(
                    email=userinfo["email"],
                    oauth_provider="google",
                    oauth_id=str(userinfo["id"]),
                    name=userinfo.get("name"),
                    avatar_url=userinfo.get("picture"),
                    monthly_credits=settings.monthly_credits_default,
                    credits=settings.monthly_credits_default,
                )
                session.add(user)
        
        await session.commit()
        await session.refresh(user)
        
        return {
            "access_token": generate_access_token(user.id, user.email),
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.name,
                "avatar_url": user.avatar_url,
                "is_admin": bool(user.is_admin),
            }
        }

"""
OAuth Authentication Router
Handles Google and GitHub OAuth login flows.
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from ..config import settings
from ..db import AsyncSession as DBSession, engine
from ..models import User
from ..security import generate_access_token

router = APIRouter(prefix="/auth/oauth", tags=["oauth"])


# ============ Google OAuth ============

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
async def google_callback(code: str):
    """Exchange Google auth code for user info and create/login user."""
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")
    
    redirect_uri = f"{settings.frontend_url}/auth/callback/google"
    
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
            # Check if email already exists (maybe from password signup)
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
                "name": user.name,
                "avatar_url": user.avatar_url,
            }
        }


# ============ GitHub OAuth ============

@router.get("/github")
async def github_login():
    """Redirect to GitHub OAuth consent screen."""
    if not settings.github_client_id:
        raise HTTPException(status_code=503, detail="GitHub OAuth not configured")
    
    redirect_uri = f"{settings.frontend_url}/auth/callback/github"
    github_auth_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={settings.github_client_id}"
        f"&redirect_uri={redirect_uri}"
        "&scope=user:email"
    )
    return {"auth_url": github_auth_url}


@router.post("/github/callback")
async def github_callback(code: str):
    """Exchange GitHub auth code for user info and create/login user."""
    if not settings.github_client_id or not settings.github_client_secret:
        raise HTTPException(status_code=503, detail="GitHub OAuth not configured")
    
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "code": code,
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
            },
        )
        
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")
        
        tokens = token_response.json()
        access_token = tokens.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token received")
        
        # Get user info
        userinfo_response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
            },
        )
        
        if userinfo_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        userinfo = userinfo_response.json()
        
        # Get primary email if not public
        email = userinfo.get("email")
        if not email:
            emails_response = await client.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
            )
            if emails_response.status_code == 200:
                emails = emails_response.json()
                primary = next((e for e in emails if e.get("primary")), None)
                email = primary["email"] if primary else emails[0]["email"]
    
    # Create or update user
    async with DBSession(engine) as session:
        user = await session.scalar(
            select(User).where(
                (User.oauth_provider == "github") & (User.oauth_id == str(userinfo["id"]))
            )
        )
        
        if not user:
            # Check if email already exists
            user = await session.scalar(select(User).where(User.email == email))
            if user:
                # Link OAuth to existing account
                user.oauth_provider = "github"
                user.oauth_id = str(userinfo["id"])
                user.name = userinfo.get("name") or userinfo.get("login")
                user.avatar_url = userinfo.get("avatar_url")
            else:
                # Create new user
                user = User(
                    email=email,
                    oauth_provider="github",
                    oauth_id=str(userinfo["id"]),
                    name=userinfo.get("name") or userinfo.get("login"),
                    avatar_url=userinfo.get("avatar_url"),
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
                "name": user.name,
                "avatar_url": user.avatar_url,
            }
        }

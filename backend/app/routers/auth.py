from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from ..models import User
from ..schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from ..security import hash_password, verify_password, generate_access_token
from ..errors import AuthError, AppBaseException, ErrorCode
from ..deps import get_current_user
from ..config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


def _is_bootstrap_admin_email(email: str) -> bool:
    target = (settings.admin_bootstrap_email or "").strip().lower()
    return bool(target) and email.strip().lower() == target


async def _ensure_bootstrap_admin(user: User, session: AsyncSession) -> None:
    if _is_bootstrap_admin_email(user.email) and not bool(user.is_admin):
        user.is_admin = True
        session.add(user)
        await session.commit()
        await session.refresh(user)


@router.post("/signup", response_model=TokenResponse)
async def signup(payload: RegisterRequest, session: AsyncSession = Depends(get_session)):
    existing = await session.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise AppBaseException(status.HTTP_400_BAD_REQUEST, ErrorCode.EMAIL_ALREADY_EXISTS, "Email already registered")

    try:
        user = User(
            email=payload.email,
            password_hash=hash_password(payload.password),
            monthly_credits=settings.monthly_credits_default,
            credits=settings.monthly_credits_default,
            is_admin=_is_bootstrap_admin_email(payload.email),
        )
    except ValueError as e:
        raise AppBaseException(status.HTTP_400_BAD_REQUEST, ErrorCode.VALIDATION_ERROR, str(e))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return TokenResponse(access_token=generate_access_token(user.id, user.email))


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)):
    user = await session.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise AuthError("Invalid credentials")
    await _ensure_bootstrap_admin(user, session)
    return TokenResponse(access_token=generate_access_token(user.id, user.email))


@router.post("/admin/login", response_model=TokenResponse)
async def admin_login(payload: LoginRequest, session: AsyncSession = Depends(get_session)):
    user = await session.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise AuthError("Invalid credentials")
    await _ensure_bootstrap_admin(user, session)
    if not bool(user.is_admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return TokenResponse(access_token=generate_access_token(user.id, user.email))


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.name,
        avatar_url=current_user.avatar_url,
        credits=current_user.credits or 0,
        is_admin=bool(current_user.is_admin),
    )

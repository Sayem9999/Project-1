from datetime import datetime, date
from pydantic import BaseModel, EmailStr, field_validator, Field
from .config import settings
from .models import JobStatus
import re
from typing import Literal


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        policy = (settings.password_policy or "basic").lower()
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if policy in ("basic", "lenient"):
            return v
        if policy in ("standard", "medium"):
            if not re.search(r'[A-Za-z]', v):
                raise ValueError('Password must contain at least one letter')
            if not re.search(r'\d', v):
                raise ValueError('Password must contain at least one digit')
            return v
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class EditJobRequest(BaseModel):
    theme: str = "professional"
    pacing: str = "medium"
    mood: str = "professional"
    ratio: str = "16:9"
    platform: str = "youtube"
    tier: str = "pro"
    brand_safety: str = "standard"
    transition_style: Literal["cut", "dissolve", "wipe", "crossfade", "wipe_left", "wipe_right", "slide_left", "slide_right"] = "dissolve"
    transition_duration: float = Field(default=0.25, ge=0.1, le=1.5)
    speed_profile: Literal["slow", "balanced", "fast"] = "balanced"
    subtitle_preset: Literal["platform_default", "broadcast", "social"] = "platform_default"
    color_profile: Literal["natural", "cinematic", "punchy"] = "natural"
    skin_protect_strength: float = Field(default=0.5, ge=0.0, le=1.0)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    avatar_url: str | None = None
    credits: int = 0
    is_admin: bool = False


class AdminUserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    avatar_url: str | None = None
    credits: int = 0
    monthly_credits: int | None = None
    last_credit_reset: date | None = None
    is_admin: bool = False
    oauth_provider: str | None = None
    created_at: datetime


class JobResponse(BaseModel):
    id: int
    status: JobStatus
    theme: str
    tier: str | None = None
    credits_cost: int | None = None
    pacing: str | None = None
    mood: str | None = None
    ratio: str | None = None
    platform: str | None = None
    brand_safety: str | None = None
    cancel_requested: bool | None = None
    progress_message: str
    output_path: str | None
    thumbnail_path: str | None
    created_at: datetime
    updated_at: datetime | None = None
    
    # Phase 5 Fields
    media_intelligence: dict | None = None
    qc_result: dict | None = None
    director_plan: dict | None = None
    brand_safety_result: dict | None = None
    ab_test_result: dict | None = None
    performance_metrics: dict | None = None
    post_settings: dict | None = None
    audio_qa: dict | None = None
    color_qa: dict | None = None
    subtitle_qa: dict | None = None


class N8NCallbackRequest(BaseModel):
    status: JobStatus
    progress_message: str
    output_path: str | None = None


class AgentInput(BaseModel):
    job_id: int
    transcript: str
    theme: str = "professional"
    style_profile: str = "clean, professional, natural pacing"
    clip_metadata: dict


class ArchitectInput(BaseModel):
    query: str


class AgentOutput(BaseModel):
    agent: str
    directives: dict


class CreditLedgerResponse(BaseModel):
    id: int
    user_id: int
    user_email: EmailStr
    delta: int
    balance_after: int
    reason: str | None = None
    source: str
    job_id: int | None = None
    created_by: int | None = None
    created_by_email: EmailStr | None = None
    created_at: datetime


class AdminActionLogResponse(BaseModel):
    id: int
    admin_user_id: int
    admin_email: EmailStr
    action: str
    target_type: str
    target_id: str | None = None
    details: dict | None = None
    created_at: datetime

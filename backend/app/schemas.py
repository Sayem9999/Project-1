from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator
from .config import settings
from .models import JobStatus
import re


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
    is_admin: bool = False
    oauth_provider: str | None = None
    created_at: datetime


class JobResponse(BaseModel):
    id: int
    status: JobStatus
    theme: str
    tier: str | None = None
    credits_cost: int | None = None
    progress_message: str
    output_path: str | None
    thumbnail_path: str | None
    created_at: datetime
    
    # Phase 5 Fields
    media_intelligence: dict | None = None
    qc_result: dict | None = None
    director_plan: dict | None = None
    brand_safety_result: dict | None = None
    ab_test_result: dict | None = None


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


class AgentOutput(BaseModel):
    agent: str
    directives: dict

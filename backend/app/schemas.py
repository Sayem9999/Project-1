from datetime import datetime
from pydantic import BaseModel, EmailStr
from .models import JobStatus


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: EmailStr


class JobResponse(BaseModel):
    id: int
    status: JobStatus
    progress_message: str
    output_path: str | None
    created_at: datetime


class N8NCallbackRequest(BaseModel):
    status: JobStatus
    progress_message: str
    output_path: str | None = None


class AgentInput(BaseModel):
    job_id: int
    transcript: str
    style_profile: str = "clean, professional, natural pacing"
    clip_metadata: dict


class AgentOutput(BaseModel):
    agent: str
    directives: dict

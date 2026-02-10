from __future__ import annotations
import enum
from typing import Optional, Union
from datetime import datetime, date
from sqlalchemy import String, DateTime, Date, Enum, ForeignKey, Text, Column, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


class JobStatus(str, enum.Enum):
    queued = "queued"
    processing = "processing"
    complete = "complete"
    failed = "failed"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=True)  # Nullable for OAuth users
    
    # OAuth fields
    oauth_provider: Mapped[str] = mapped_column(String(50), nullable=True)  # 'google', 'github', or null
    oauth_id: Mapped[str] = mapped_column(String(255), nullable=True)  # Provider's user ID
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str] = mapped_column(String(500), nullable=True)
    
    credits: Mapped[int] = mapped_column(Integer, default=10)
    monthly_credits: Mapped[int] = mapped_column(Integer, default=10)
    last_credit_reset: Mapped[date] = mapped_column(Date, nullable=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    # jobs = relationship("Job", back_populates="user")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    source_path: Mapped[str] = mapped_column(Text, nullable=False)
    output_path: Mapped[str] = mapped_column(Text, nullable=True)
    thumbnail_path: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.queued, nullable=False)
    theme: Mapped[str] = mapped_column(String, default="professional", nullable=False)
    tier: Mapped[str] = mapped_column(String(50), default="standard", nullable=False)
    credits_cost: Mapped[int] = mapped_column(Integer, default=1)
    progress_message: Mapped[str] = mapped_column(Text, default="Upload complete, waiting for processing.")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Phase 5 Fields
    media_intelligence: Mapped[dict] = mapped_column(JSON, nullable=True)
    qc_result: Mapped[dict] = mapped_column(JSON, nullable=True)
    director_plan: Mapped[dict] = mapped_column(JSON, nullable=True)
    brand_safety_result: Mapped[dict] = mapped_column(JSON, nullable=True)
    ab_test_result: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Relationships (if needed in future)
    # user: Mapped["User"] = relationship("User", back_populates="jobs")


class CreditLedger(Base):
    __tablename__ = "credit_ledger"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    job_id: Mapped[Optional[int]] = mapped_column(ForeignKey("jobs.id"), nullable=True)
    delta: Mapped[int] = mapped_column(Integer, nullable=False)
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="system", nullable=False)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ProcessedWebhook(Base):
    __tablename__ = "processed_webhooks"
    
    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

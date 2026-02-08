from __future__ import annotations
import enum
import typing
from datetime import datetime
from sqlalchemy import String, DateTime, Enum, ForeignKey, Text, Column, Integer
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
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Nullable for OAuth users
    
    # OAuth fields
    oauth_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)  # 'google', 'github', or null
    oauth_id: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Provider's user ID
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    source_path = Column(Text, nullable=False)
    output_path = Column(Text, nullable=True)
    status = Column(Enum(JobStatus), default=JobStatus.queued, nullable=False)
    theme = Column(String, default="professional", nullable=False)
    progress_message = Column(Text, default="Upload complete, waiting for processing.")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

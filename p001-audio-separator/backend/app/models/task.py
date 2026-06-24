"""SQLAlchemy Task model for tracking audio processing jobs."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core.config import settings


class Base(DeclarativeBase):
    """Base for all SQLAlchemy ORM models."""

    pass


class Task(Base):
    """Represents an audio processing task."""

    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False, index=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    duration: Mapped[float] = mapped_column(Float, nullable=True)  # seconds

    # Processing status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        index=True,
    )
    # Status values: pending, processing, completed, failed

    # Current operation info
    mode: Mapped[str] = mapped_column(String(20), nullable=True)
    # Mode values: 2track, 4track, transform, chords

    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    progress_message: Mapped[str] = mapped_column(String(255), nullable=False, default="")

    # Results
    result_paths: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # e.g. {"vocals": "/path/vocals.mp3", "drums": "/path/drums.mp3", ...}
    chord_result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # e.g. {"chords": [{"start": 0.0, "end": 2.5, "chord": "C:maj"}, ...]}

    # Error
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Security
    token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc) + timedelta(hours=settings.FILE_RETENTION_HOURS),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        """Return a dict representation for API responses."""
        return {
            "task_id": str(self.id),
            "status": self.status,
            "mode": self.mode,
            "progress": self.progress,
            "progress_message": self.progress_message,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "duration": self.duration,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }

    def is_expired(self) -> bool:
        """Check if the task has expired."""
        return datetime.now(timezone.utc) > self.expires_at

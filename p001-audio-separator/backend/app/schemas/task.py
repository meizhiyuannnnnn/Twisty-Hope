"""Pydantic schemas for task-related request/response models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class TaskResponse(BaseModel):
    """Public task information returned to the client."""

    task_id: str
    status: str
    mode: str | None = None
    progress: int = 0
    progress_message: str = ""
    original_filename: str
    file_size: int
    duration: float | None = None
    created_at: str | None = None
    expires_at: str | None = None


class TaskDetailResponse(TaskResponse):
    """Detailed task response including result information."""

    result_stems: list[str] | None = None  # List of available stem names
    chord_result: dict | None = None
    error_message: str | None = None


class SeparateRequest(BaseModel):
    """Request to trigger source separation."""

    mode: str = Field(default="2track", description="Separation mode: '2track' or '4track'")


class TransformRequest(BaseModel):
    """Request to trigger audio transformation."""

    speed: float = Field(default=1.0, ge=0.5, le=1.5, description="Speed factor (0.5 to 1.5)")
    pitch: int = Field(default=0, ge=-12, le=12, description="Pitch shift in semitones (-12 to +12)")


class ProgressMessage(BaseModel):
    """WebSocket progress update message."""

    type: str = "progress"
    task_id: str
    status: str
    progress: int
    message: str


class ChordResultResponse(BaseModel):
    """Chord analysis result."""

    task_id: str
    chords: list[dict]  # [{"start": float, "end": float, "chord": str}]


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str
    suggestion: str | None = None

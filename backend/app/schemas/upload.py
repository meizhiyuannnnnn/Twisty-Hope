"""Pydantic schemas for file upload request/response."""

from __future__ import annotations

from pydantic import BaseModel


class UploadResponse(BaseModel):
    """Response after a successful file upload."""

    task_id: str
    token: str
    original_filename: str
    file_size: int
    duration: float | None = None
    message: str = "文件上传成功，请选择处理操作"


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    queue_length: int = 0

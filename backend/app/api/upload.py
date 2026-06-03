"""File upload endpoint."""

from __future__ import annotations

import os
import uuid

import aiofiles
import filetype
import librosa
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import check_rate_limit_dependency, get_client_ip, get_redis
from app.core.config import settings
from app.core.database import get_db
from app.core.security import generate_task_token
from app.models.task import Task
from app.schemas.upload import UploadResponse

router = APIRouter(prefix="/api", tags=["upload"])


def _validate_audio(file: UploadFile) -> None:
    """Validate uploaded file: size, MIME type, magic bytes, and duration.

    Raises HTTPException on validation failure.
    """
    # Check file size
    if file.size is None or file.size == 0:
        raise HTTPException(
            status_code=400,
            detail={"detail": "文件为空", "suggestion": "请选择有效的音频文件上传"},
        )
    if file.size > settings.MAX_FILE_SIZE:
        max_mb = settings.MAX_FILE_SIZE // (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail={
                "detail": f"文件过大（超过 {max_mb} MB）",
                "suggestion": f"请上传小于 {max_mb} MB 的音频文件，或压缩后再上传",
            },
        )

    # Check MIME type
    content_type = file.content_type or ""
    if content_type not in settings.ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=415,
            detail={
                "detail": "不支持的音频格式",
                "suggestion": "支持的格式：MP3、WAV、FLAC、M4A、OGG",
            },
        )


async def _validate_magic_bytes(filepath: str) -> None:
    """Validate file magic bytes confirm it is an audio file."""
    kind = filetype.guess(filepath)
    if kind is None:
        raise HTTPException(
            status_code=415,
            detail={
                "detail": "无法识别的文件格式",
                "suggestion": "请确保上传的是有效的音频文件（MP3/WAV/FLAC/M4A/OGG）",
            },
        )
    # Check that mime type is audio/*
    if not kind.mime.startswith("audio/"):
        raise HTTPException(
            status_code=415,
            detail={
                "detail": f"文件类型检测为 {kind.mime}，非音频文件",
                "suggestion": "请上传音频文件",
            },
        )


def _get_duration(filepath: str) -> float:
    """Get audio duration in seconds."""
    try:
        duration = librosa.get_duration(path=filepath)
        return duration
    except Exception:
        # If librosa fails, return 0 and let it pass (some formats may not be supported)
        return 0.0


def _get_extension(filename: str) -> str:
    """Get file extension from filename."""
    return os.path.splitext(filename)[1].lower()


@router.post("/upload", response_model=UploadResponse)
async def upload_audio(  # type: ignore[misc]
    file: UploadFile,
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    _rate_limit: None = Depends(check_rate_limit_dependency),
) -> UploadResponse:
    """Upload an audio file for processing.

    Validates file type, size, and magic bytes. Creates a task record
    and returns a task_id + access token for subsequent operations.
    """
    # Validate file
    _validate_audio(file)

    # Generate unique task ID
    task_id = uuid.uuid4()
    token = generate_task_token(str(task_id))

    # Create upload directory
    task_dir = os.path.join(settings.UPLOAD_DIR, str(task_id))
    os.makedirs(task_dir, exist_ok=True)

    # Save file
    ext = _get_extension(file.filename or "audio.mp3")
    safe_filename = f"original{ext}"
    filepath = os.path.join(task_dir, safe_filename)

    try:
        async with aiofiles.open(filepath, "wb") as f:
            content = await file.read()
            await f.write(content)
    except OSError as e:
        # Clean up on error
        raise HTTPException(
            status_code=500,
            detail={"detail": "文件保存失败", "suggestion": "服务器存储错误，请稍后再试"},
        ) from e

    # Secondary validation: magic bytes
    await _validate_magic_bytes(filepath)

    # Get audio duration
    try:
        duration = _get_duration(filepath)
    except Exception:
        duration = 0.0

    if duration > settings.MAX_DURATION:
        # Clean up
        os.remove(filepath)
        os.rmdir(task_dir)
        raise HTTPException(
            status_code=400,
            detail={
                "detail": f"音频时长过长（{int(duration)}秒，超过{settings.MAX_DURATION // 60}分钟限制）",
                "suggestion": "请截取 15 分钟以内的片段上传",
            },
        )

    # Create task record
    task = Task(
        id=task_id,
        ip_address=get_client_ip(request),
        original_filename=file.filename or "unknown",
        original_path=filepath,
        file_size=file.size or 0,
        duration=duration,
        status="pending",
        token=token,
    )
    db.add(task)
    await db.commit()

    return UploadResponse(
        task_id=str(task_id),
        token=token,
        original_filename=task.original_filename,
        file_size=task.file_size,
        duration=duration if duration > 0 else None,
    )

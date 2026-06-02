"""Task management endpoints — query, trigger operations."""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_redis, get_task_by_id
from app.core.database import get_db
from app.models.task import Task
from app.schemas.task import (
    ChordResultResponse,
    SeparateRequest,
    TaskDetailResponse,
    TaskResponse,
    TransformRequest,
)

router = APIRouter(prefix="/api/task", tags=["task"])


@router.get("/{task_id}", response_model=TaskDetailResponse)
async def get_task(  # type: ignore[misc]
    task_id: str,
    token: str = Query(..., description="Access token"),
    db: AsyncSession = Depends(get_db),
) -> TaskDetailResponse:
    """Get task status and details.

    Requires the access token returned at upload time.
    """
    task = await get_task_by_id(task_id, token, db)

    # Determine available stems from result_paths
    result_stems = None
    if task.result_paths:
        result_stems = list(task.result_paths.keys())

    return TaskDetailResponse(
        task_id=str(task.id),
        status=task.status,
        mode=task.mode,
        progress=task.progress,
        progress_message=task.progress_message,
        original_filename=task.original_filename,
        file_size=task.file_size,
        duration=task.duration,
        created_at=task.created_at.isoformat() if task.created_at else None,
        expires_at=task.expires_at.isoformat() if task.expires_at else None,
        result_stems=result_stems,
        chord_result=task.chord_result,
        error_message=task.error_message,
    )


@router.post("/{task_id}/separate", response_model=TaskResponse)
async def trigger_separation(  # type: ignore[misc]
    task_id: str,
    req: SeparateRequest,
    token: str = Query(..., description="Access token"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> TaskResponse:
    """Trigger source separation (2-track or 4-track).

    Pushes the job to the Redis queue for processing.
    """
    if req.mode not in ("2track", "4track"):
        raise HTTPException(
            status_code=400,
            detail={
                "detail": "无效的分离模式",
                "suggestion": "请选择 '2track'（人声+伴奏）或 '4track'（四轨分离）",
            },
        )

    task = await get_task_by_id(task_id, token, db)

    if task.status == "processing":
        raise HTTPException(
            status_code=409,
            detail={
                "detail": "任务正在处理中",
                "suggestion": "请等待当前任务完成后再发起新操作",
            },
        )

    # Update task status
    task.status = "pending"
    task.mode = req.mode
    task.progress = 0
    task.progress_message = "已加入处理队列"
    await db.commit()

    # Push to Redis queue
    job_data = json.dumps({
        "task_id": str(task.id),
        "operation": "separate",
        "mode": req.mode,
    })
    await redis.rpush("audio:tasks", job_data)

    return TaskResponse(
        task_id=str(task.id),
        status=task.status,
        mode=task.mode,
        progress=task.progress,
        progress_message=task.progress_message,
        original_filename=task.original_filename,
        file_size=task.file_size,
        duration=task.duration,
        created_at=task.created_at.isoformat() if task.created_at else None,
        expires_at=task.expires_at.isoformat() if task.expires_at else None,
    )


@router.post("/{task_id}/transform", response_model=TaskResponse)
async def trigger_transform(  # type: ignore[misc]
    task_id: str,
    req: TransformRequest,
    token: str = Query(..., description="Access token"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> TaskResponse:
    """Trigger speed/pitch transformation.

    speed: 0.5 to 1.5 (0.5 = half speed, 1.0 = normal, 1.5 = 1.5x speed)
    pitch: -12 to +12 semitones
    """
    task = await get_task_by_id(task_id, token, db)

    if task.status == "processing":
        raise HTTPException(
            status_code=409,
            detail={
                "detail": "任务正在处理中",
                "suggestion": "请等待当前任务完成后再发起新操作",
            },
        )

    # Update task status
    task.status = "pending"
    task.mode = "transform"
    task.progress = 0
    task.progress_message = "已加入处理队列"
    await db.commit()

    # Push to Redis queue
    job_data = json.dumps({
        "task_id": str(task.id),
        "operation": "transform",
        "speed": req.speed,
        "pitch": req.pitch,
    })
    await redis.rpush("audio:tasks", job_data)

    return TaskResponse(
        task_id=str(task.id),
        status=task.status,
        mode=task.mode,
        progress=task.progress,
        progress_message=task.progress_message,
        original_filename=task.original_filename,
        file_size=task.file_size,
        duration=task.duration,
        created_at=task.created_at.isoformat() if task.created_at else None,
        expires_at=task.expires_at.isoformat() if task.expires_at else None,
    )


@router.post("/{task_id}/chords", response_model=TaskResponse)
async def trigger_chords(  # type: ignore[misc]
    task_id: str,
    token: str = Query(..., description="Access token"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> TaskResponse:
    """Trigger chord analysis on the uploaded audio."""
    task = await get_task_by_id(task_id, token, db)

    if task.status == "processing":
        raise HTTPException(
            status_code=409,
            detail={
                "detail": "任务正在处理中",
                "suggestion": "请等待当前任务完成后再发起新操作",
            },
        )

    task.status = "pending"
    task.mode = "chords"
    task.progress = 0
    task.progress_message = "已加入和弦分析队列"
    await db.commit()

    job_data = json.dumps({
        "task_id": str(task.id),
        "operation": "chords",
    })
    await redis.rpush("audio:tasks", job_data)

    return TaskResponse(
        task_id=str(task.id),
        status=task.status,
        mode=task.mode,
        progress=task.progress,
        progress_message=task.progress_message,
        original_filename=task.original_filename,
        file_size=task.file_size,
        duration=task.duration,
        created_at=task.created_at.isoformat() if task.created_at else None,
        expires_at=task.expires_at.isoformat() if task.expires_at else None,
    )

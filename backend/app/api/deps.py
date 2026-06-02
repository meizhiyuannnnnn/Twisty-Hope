"""FastAPI dependencies — DB session, rate limiting, task lookup."""

from __future__ import annotations

from typing import AsyncGenerator
from uuid import UUID

import redis.asyncio as aioredis
from fastapi import Depends, HTTPException, Request
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import check_rate_limit
from app.models.task import Task


async def get_redis() -> AsyncGenerator[Redis, None]:  # type: ignore[misc]
    """Dependency: yield a Redis connection."""
    r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield r
    finally:
        await r.aclose()  # type: ignore[attr-defined]


async def check_rate_limit_dependency(
    request: Request,
    redis: Redis = Depends(get_redis),
) -> None:
    """Dependency: enforce IP-based rate limiting.

    Raises HTTPException 429 if the IP has exceeded the limit.
    """
    ip = request.client.host if request.client else "unknown"
    allowed, remaining = await check_rate_limit(ip, redis)

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "detail": "请求过于频繁，请稍后再试",
                "suggestion": f"当前限制为每小时 {settings.RATE_LIMIT_PER_HOUR} 次，请稍后再来",
            },
        )


async def get_task_by_id(
    task_id: str,
    token: str,
    db: AsyncSession,
) -> Task:
    """Look up a task by ID and validate the access token.

    Args:
        task_id: UUID string of the task.
        token: Access token for authorization.
        db: Database session.

    Returns:
        The Task ORM object.

    Raises:
        HTTPException 404 if task not found, 403 if token invalid.
    """
    try:
        uid = UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={"detail": "无效的任务 ID 格式", "suggestion": "请检查任务 ID 是否正确"},
        )

    result = await db.execute(select(Task).where(Task.id == uid))
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail={"detail": "任务不存在", "suggestion": "任务可能已被删除或链接无效"},
        )

    if task.token != token:
        raise HTTPException(
            status_code=403,
            detail={"detail": "访问令牌无效", "suggestion": "请使用上传时返回的正确链接"},
        )

    if task.is_expired():
        raise HTTPException(
            status_code=410,
            detail={
                "detail": "文件已过期（超过 24 小时）",
                "suggestion": "请重新上传文件进行处理",
            },
        )

    return task

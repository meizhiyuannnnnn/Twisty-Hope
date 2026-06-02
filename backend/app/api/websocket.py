"""WebSocket endpoint for real-time task progress updates."""

from __future__ import annotations

import asyncio
import json

import redis.asyncio as aioredis
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.core.config import settings
from app.core.database import async_session_factory
from app.models.task import Task

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/task/{task_id}")
async def task_progress_websocket(  # type: ignore[misc]
    websocket: WebSocket,
    task_id: str,
    token: str = Query(...),
) -> None:
    """WebSocket endpoint for real-time task progress.

    Client connects with task_id and access token.
    Server pushes progress updates as JSON messages.

    Message format:
        {"type": "progress", "task_id": "...", "status": "...", "progress": 0-100, "message": "..."}

    Also listens for task completion/failure via Redis pub/sub.
    """
    # Validate token by checking the task exists
    async with async_session_factory() as db:
        from uuid import UUID

        try:
            uid = UUID(task_id)
        except ValueError:
            await websocket.close(code=4000, reason="Invalid task ID")
            return

        result = await db.execute(select(Task).where(Task.id == uid))
        task = result.scalar_one_or_none()

        if task is None or task.token != token:
            await websocket.close(code=4003, reason="Invalid token")
            return

    await websocket.accept()

    redis: aioredis.Redis | None = None
    pubsub = None

    try:
        redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        pubsub = redis.pubsub()

        channel = f"task:{task_id}:progress"
        await pubsub.subscribe(channel)

        # Send current state immediately
        async with async_session_factory() as db:
            result = await db.execute(select(Task).where(Task.id == uid))
            current_task = result.scalar_one_or_none()
            if current_task:
                await websocket.send_json({
                    "type": "progress",
                    "task_id": task_id,
                    "status": current_task.status,
                    "progress": current_task.progress,
                    "message": current_task.progress_message or "",
                })

        # Listen for progress updates
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    await websocket.send_json(data)
                except json.JSONDecodeError:
                    pass
            elif message["type"] == "subscribe":
                pass  # Ignore subscription confirmation

    except WebSocketDisconnect:
        pass  # Client disconnected, normal
    except Exception:
        pass  # Silently handle errors
    finally:
        if pubsub is not None:
            try:
                await pubsub.unsubscribe(channel)
            except Exception:
                pass
        if redis is not None:
            try:
                await redis.aclose()  # type: ignore[attr-defined]
            except Exception:
                pass

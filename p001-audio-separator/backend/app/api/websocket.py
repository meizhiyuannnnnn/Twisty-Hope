"""WebSocket endpoint for real-time task progress updates."""

from __future__ import annotations

import asyncio
import json
from uuid import UUID

import redis.asyncio as aioredis
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.core.config import settings
from app.core.database import async_session_factory
from app.models.task import Task

router = APIRouter(tags=["websocket"])

# ── stem name → Chinese label mapping ──────────────────────────────
_STEM_LABELS: dict[str, str] = {
    "vocals": "人声",
    "accompaniment": "伴奏",
    "drums": "鼓",
    "bass": "贝斯",
    "other": "其他",
    "transformed": "变速变调",
}


def _build_stems(task: Task, token: str) -> list[dict]:
    """Build stems array with download URLs from task result_paths."""
    if not task.result_paths:
        return []
    stems: list[dict] = []
    for name in task.result_paths:
        stems.append({
            "stem_id": name,
            "label": _STEM_LABELS.get(name, name),
            "url": f"/api/task/{task.id}/download/{name}?token={token}",
        })
    return stems


async def _enrich_message(data: dict, task_id: str, token: str) -> dict:
    """If the message indicates completion, enrich with stems from DB."""
    if data.get("status") not in ("completed",):
        return data

    async with async_session_factory() as db:
        result = await db.execute(select(Task).where(Task.id == UUID(task_id)))
        task = result.scalar_one_or_none()
        if task and task.result_paths:
            data["stems"] = _build_stems(task, token)
    return data


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
        {"type": "progress", "task_id": "...", "status": "...", "progress": 0-100,
         "message": "...", "stems": [...]}
    """
    # Validate token by checking the task exists
    try:
        uid = UUID(task_id)
    except ValueError:
        await websocket.close(code=4000, reason="Invalid task ID")
        return

    async with async_session_factory() as db:
        result = await db.execute(select(Task).where(Task.id == uid))
        task = result.scalar_one_or_none()

        if task is None or task.token != token:
            await websocket.close(code=4003, reason="Invalid token")
            return

    await websocket.accept()

    redis: aioredis.Redis | None = None
    pubsub = None

    try:
        redis = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_timeout=30,
            socket_connect_timeout=10,
        )
        pubsub = redis.pubsub()

        channel = f"task:{task_id}:progress"
        await pubsub.subscribe(channel)

        # Send current state immediately (with stems if already completed)
        async with async_session_factory() as db:
            result = await db.execute(select(Task).where(Task.id == uid))
            current_task = result.scalar_one_or_none()
            if current_task:
                msg: dict = {
                    "type": "progress",
                    "task_id": task_id,
                    "status": current_task.status,
                    "progress": current_task.progress,
                    "message": current_task.progress_message or "",
                }
                if current_task.status == "completed" and current_task.result_paths:
                    msg["stems"] = _build_stems(current_task, token)
                await websocket.send_json(msg)

        # Listen for progress updates
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    # Enrich completed messages with stems from DB
                    data = await _enrich_message(data, task_id, token)
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

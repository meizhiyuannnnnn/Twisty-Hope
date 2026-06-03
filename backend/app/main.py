"""FastAPI application entry point.

Audio separation web service — free, user-friendly online tool
for separating vocals and accompaniment from music files.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import download, task, upload, websocket
from app.core.config import settings
from app.core.database import engine
from app.models.task import Base  # noqa: F401 — ensure all ORM models are loaded
from app.services.cleaner import cleanup_loop


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[arg-type]
    """Application lifespan: start background tasks on startup, clean up on shutdown."""
    # Create database tables if they don't exist yet
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Start file cleanup scheduler as background task
    cleanup_task = asyncio.create_task(cleanup_loop(interval=600))

    yield

    # Shutdown: cancel cleanup task
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="免费在线音频分离工具 — 支持人声/伴奏分离、多乐器分离、变速变调、和弦识别",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router)
app.include_router(task.router)
app.include_router(download.router)
app.include_router(websocket.router)


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint — returns service status and queue metrics."""
    queue_length = 0
    try:
        redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        queue_length = await redis_client.llen("audio:tasks")
        await redis_client.aclose()  # type: ignore[attr-defined]
    except Exception:
        queue_length = -1  # Redis unavailable

    return {
        "status": "ok",
        "version": settings.VERSION,
        "queue_length": queue_length,
    }


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
    }

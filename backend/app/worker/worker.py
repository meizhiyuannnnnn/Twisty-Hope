"""Redis-backed task worker — processes audio jobs from the queue.

Usage:
    python -m app.worker.worker

The worker polls Redis list 'audio:tasks' for new jobs, processes them one at a time
(FIFO order, single GPU serial processing), and publishes progress updates via Redis pub/sub.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import traceback
from pathlib import Path

import redis.asyncio as aioredis
from sqlalchemy import select

# Ensure app is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.core.config import settings
from app.core.database import async_session_factory
from app.models.task import Task
from app.services.chords import run_chord_analysis
from app.services.separator import convert_stems_to_mp3, run_separation
from app.services.transformer import transform_audio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("worker")


def _make_progress_callback(task_id: str, redis_client: aioredis.Redis):
    """Create a synchronous progress callback that publishes to Redis."""

    def callback(progress: int, message: str) -> None:
        data = json.dumps({
            "type": "progress",
            "task_id": task_id,
            "status": "processing",
            "progress": progress,
            "message": message,
        })
        # Schedule async publish
        asyncio.ensure_future(
            redis_client.publish(f"task:{task_id}:progress", data),
            loop=asyncio.get_running_loop(),
        )

    return callback


async def update_task_status(
    task_id: str,
    status: str,
    progress: int = 0,
    message: str = "",
    result_paths: dict | None = None,
    chord_result: dict | None = None,
    error_message: str | None = None,
) -> None:
    """Update task status in the database."""
    from uuid import UUID

    async with async_session_factory() as db:
        result = await db.execute(select(Task).where(Task.id == UUID(task_id)))
        task = result.scalar_one_or_none()
        if task is None:
            logger.error("Task %s not found for status update", task_id)
            return

        task.status = status
        task.progress = progress
        task.progress_message = message
        if result_paths is not None:
            task.result_paths = result_paths
        if chord_result is not None:
            task.chord_result = chord_result
        if error_message is not None:
            task.error_message = error_message
        await db.commit()


async def publish_progress(redis_client: aioredis.Redis, task_id: str, status: str, progress: int, message: str) -> None:
    """Publish a progress update to the task's Redis channel."""
    data = json.dumps({
        "type": "progress",
        "task_id": task_id,
        "status": status,
        "progress": progress,
        "message": message,
    })
    await redis_client.publish(f"task:{task_id}:progress", data)


async def process_separate(redis_client: aioredis.Redis, task_id: str, mode: str) -> None:
    """Process a source separation job."""
    logger.info("Processing separation: task=%s mode=%s", task_id, mode)

    # Get task info
    from uuid import UUID

    async with async_session_factory() as db:
        result = await db.execute(select(Task).where(Task.id == UUID(task_id)))
        task = result.scalar_one_or_none()
        if task is None:
            logger.error("Task %s not found", task_id)
            return
        input_path = task.original_path
        output_dir = os.path.join(os.path.dirname(input_path), "output")

    os.makedirs(output_dir, exist_ok=True)

    try:
        await update_task_status(task_id, "processing", 0, "开始处理...")
        await publish_progress(redis_client, task_id, "processing", 0, "开始处理...")

        progress_cb = _make_progress_callback(task_id, redis_client)

        # Run separation (produces WAV files)
        wav_stems = await run_separation(
            input_path,
            output_dir,
            mode,
            progress_callback=progress_cb,
        )

        await update_task_status(task_id, "processing", 95, "正在转换为 MP3...")
        await publish_progress(redis_client, task_id, "processing", 95, "正在转换为 MP3 格式（320kbps）...")

        # Convert to MP3
        mp3_stems = convert_stems_to_mp3(wav_stems, output_dir, bitrate=settings.MP3_BITRATE)

        # Save result paths (MP3 files)
        await update_task_status(
            task_id,
            "completed",
            100,
            "处理完成！请下载音频文件",
            result_paths=mp3_stems,
        )
        await publish_progress(redis_client, task_id, "completed", 100, "处理完成！")

        logger.info("Separation completed: task=%s mode=%s stems=%s", task_id, mode, list(mp3_stems.keys()))

    except Exception as e:
        error_msg = f"分离失败: {str(e)}"
        logger.exception("Separation failed: task=%s", task_id)
        await update_task_status(task_id, "failed", 0, error_msg, error_message=error_msg)
        await publish_progress(redis_client, task_id, "failed", 0, error_msg)


async def process_transform(redis_client: aioredis.Redis, task_id: str, speed: float, pitch: int) -> None:
    """Process an audio transformation job."""
    logger.info("Processing transform: task=%s speed=%s pitch=%s", task_id, speed, pitch)

    from uuid import UUID

    async with async_session_factory() as db:
        result = await db.execute(select(Task).where(Task.id == UUID(task_id)))
        task = result.scalar_one_or_none()
        if task is None:
            return
        input_path = task.original_path
        output_dir = os.path.join(os.path.dirname(input_path), "output")

    os.makedirs(output_dir, exist_ok=True)

    try:
        await update_task_status(task_id, "processing", 0, "开始变速变调处理...")
        await publish_progress(redis_client, task_id, "processing", 0, "开始变速变调处理...")

        progress_cb = _make_progress_callback(task_id, redis_client)
        result_files = await transform_audio(
            input_path,
            output_dir,
            speed=speed,
            pitch_steps=pitch,
            progress_callback=progress_cb,
        )

        await update_task_status(
            task_id,
            "completed",
            100,
            "变速变调处理完成！",
            result_paths=result_files,
        )
        await publish_progress(redis_client, task_id, "completed", 100, "处理完成！")

    except Exception as e:
        error_msg = f"变速变调失败: {str(e)}"
        logger.exception("Transform failed: task=%s", task_id)
        await update_task_status(task_id, "failed", 0, error_msg, error_message=error_msg)
        await publish_progress(redis_client, task_id, "failed", 0, error_msg)


async def process_chords(redis_client: aioredis.Redis, task_id: str) -> None:
    """Process a chord analysis job."""
    logger.info("Processing chords: task=%s", task_id)

    from uuid import UUID

    async with async_session_factory() as db:
        result = await db.execute(select(Task).where(Task.id == UUID(task_id)))
        task = result.scalar_one_or_none()
        if task is None:
            return
        input_path = task.original_path
        output_dir = os.path.join(os.path.dirname(input_path), "output")

    os.makedirs(output_dir, exist_ok=True)

    try:
        await update_task_status(task_id, "processing", 0, "开始和弦分析...")
        await publish_progress(redis_client, task_id, "processing", 0, "开始和弦分析...")

        progress_cb = _make_progress_callback(task_id, redis_client)
        chords = await run_chord_analysis(input_path, progress_callback=progress_cb)

        chord_result = {"chords": chords}
        await update_task_status(
            task_id,
            "completed",
            100,
            f"和弦分析完成，共 {len(chords)} 个和弦段落",
            chord_result=chord_result,
        )
        await publish_progress(redis_client, task_id, "completed", 100, "和弦分析完成！")

    except Exception as e:
        error_msg = f"和弦分析失败: {str(e)}"
        logger.exception("Chord analysis failed: task=%s", task_id)
        await update_task_status(task_id, "failed", 0, error_msg, error_message=error_msg)
        await publish_progress(redis_client, task_id, "failed", 0, error_msg)


async def run_worker() -> None:
    """Main worker loop — polls Redis queue and processes jobs."""
    logger.info("Worker starting...")
    logger.info("Redis: %s", settings.REDIS_URL)
    logger.info("Device: %s", settings.DEVICE)

    redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    try:
        while True:
            try:
                # Blocking pop from the queue (FIFO)
                result = await redis_client.blpop("audio:tasks", timeout=5)

                if result is None:
                    continue  # No jobs, wait and retry

                _, job_json = result
                job = json.loads(job_json)

                task_id = job["task_id"]
                operation = job["operation"]

                logger.info("Dequeued job: task=%s operation=%s", task_id, operation)

                if operation == "separate":
                    await process_separate(redis_client, task_id, job["mode"])
                elif operation == "transform":
                    await process_transform(redis_client, task_id, job["speed"], job["pitch"])
                elif operation == "chords":
                    await process_chords(redis_client, task_id)
                else:
                    logger.error("Unknown operation: %s", operation)

            except asyncio.CancelledError:
                logger.info("Worker cancelled")
                break
            except Exception:
                logger.exception("Worker error processing job")
                await asyncio.sleep(1)
    finally:
        await redis_client.aclose()  # type: ignore[attr-defined]


def main() -> None:
    """Entry point for the worker process."""
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()

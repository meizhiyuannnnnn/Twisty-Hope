"""File cleanup service — removes expired upload files.

Runs as a background task, periodically scanning for expired task files
and deleting them. Can be triggered manually or via scheduler.
"""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
import time
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.config import settings
from app.core.database import async_session_factory
from app.models.task import Task

logger = logging.getLogger(__name__)


async def cleanup_expired_files() -> int:
    """Delete files for all expired tasks.

    Returns:
        Number of tasks cleaned up.
    """
    now = datetime.now(timezone.utc)
    cleaned = 0

    async with async_session_factory() as session:
        result = await session.execute(
            select(Task).where(Task.expires_at < now)
        )
        expired_tasks = result.scalars().all()

        for task in expired_tasks:
            try:
                # Delete task directory with all files
                task_dir = os.path.dirname(task.original_path)
                if os.path.exists(task_dir):
                    shutil.rmtree(task_dir)
                    logger.info("Cleaned up expired task %s: %s", task.id, task_dir)

                # Also clean up any result files
                if task.result_paths:
                    for stem_path in task.result_paths.values():
                        result_dir = os.path.dirname(stem_path)
                        if os.path.exists(result_dir) and result_dir != task_dir:
                            shutil.rmtree(result_dir)

                await session.delete(task)
                cleaned += 1
            except OSError as e:
                logger.warning("Failed to clean up task %s: %s", task.id, e)

        if cleaned > 0:
            await session.commit()
            logger.info("Cleaned up %d expired tasks", cleaned)

    return cleaned


async def cleanup_loop(interval: int = 600) -> None:
    """Run cleanup in a loop every `interval` seconds.

    Args:
        interval: Seconds between cleanup runs (default: 10 minutes).
    """
    logger.info("File cleanup service started (interval=%ds)", interval)
    while True:
        try:
            count = await cleanup_expired_files()
            if count > 0:
                logger.info("File cleanup: removed %d expired tasks", count)
        except Exception:
            logger.exception("Error during file cleanup")
        await asyncio.sleep(interval)


async def get_total_upload_size() -> int:
    """Get total size of all current upload files in bytes."""
    upload_dir = settings.UPLOAD_DIR
    if not os.path.exists(upload_dir):
        return 0

    total = 0
    for dirpath, _dirnames, filenames in os.walk(upload_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total += os.path.getsize(fp)
            except OSError:
                pass
    return total

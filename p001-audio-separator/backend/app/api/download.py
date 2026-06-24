"""File download endpoints."""

from __future__ import annotations

import io
import os
import zipfile

import aiofiles
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_task_by_id
from app.core.database import get_db

router = APIRouter(prefix="/api/task", tags=["download"])


@router.get("/{task_id}/download/{stem_name}")
async def download_stem(  # type: ignore[misc]
    task_id: str,
    stem_name: str,
    token: str = Query(..., description="Access token"),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Download a single audio stem (MP3).

    Args:
        task_id: Task UUID.
        stem_name: Name of the stem (e.g., 'vocals', 'accompaniment', 'drums', etc.)
        token: Access token.
    """
    task = await get_task_by_id(task_id, token, db)

    if task.status != "completed":
        raise HTTPException(
            status_code=400,
            detail={
                "detail": "任务尚未完成",
                "suggestion": "请等待处理完成后再下载",
            },
        )

    if not task.result_paths or stem_name not in task.result_paths:
        available = list(task.result_paths.keys()) if task.result_paths else []
        raise HTTPException(
            status_code=404,
            detail={
                "detail": f"音轨 '{stem_name}' 不存在",
                "suggestion": f"可用的音轨: {', '.join(available)}" if available else "无可用音轨",
            },
        )

    filepath = task.result_paths[stem_name]
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=410,
            detail={
                "detail": "文件已被清理",
                "suggestion": "文件已超过24小时自动删除，请重新上传处理",
            },
        )

    download_name = f"{stem_name}_{task.original_filename.rsplit('.', 1)[0]}.mp3"
    return FileResponse(
        path=filepath,
        filename=download_name,
        media_type="audio/mpeg",
    )


@router.get("/{task_id}/download")
async def download_all(  # type: ignore[misc]
    task_id: str,
    token: str = Query(..., description="Access token"),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Download all stems as a ZIP archive."""
    task = await get_task_by_id(task_id, token, db)

    if task.status != "completed":
        raise HTTPException(
            status_code=400,
            detail={
                "detail": "任务尚未完成",
                "suggestion": "请等待处理完成后再下载",
            },
        )

    if not task.result_paths:
        raise HTTPException(
            status_code=404,
            detail={"detail": "无可用音轨", "suggestion": "请先执行音频分离操作"},
        )

    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for stem_name, filepath in task.result_paths.items():
            if os.path.exists(filepath):
                arcname = f"{stem_name}.mp3"
                zf.write(filepath, arcname)

    zip_buffer.seek(0)

    zip_name = f"{task.original_filename.rsplit('.', 1)[0]}_stems.zip"
    return StreamingResponse(
        iter([zip_buffer.getvalue()]),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{zip_name}"'},
    )

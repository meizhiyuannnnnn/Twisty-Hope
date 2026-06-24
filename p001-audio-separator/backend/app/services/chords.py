"""Chord analysis service."""

from __future__ import annotations

import asyncio
from typing import Callable

from app.ai.chordino import analyze_chords


async def run_chord_analysis(
    input_path: str,
    progress_callback: Callable | None = None,
) -> list[dict]:
    """Run chord analysis asynchronously.

    Args:
        input_path: Path to the audio file.
        progress_callback: Optional sync callback(progress, message).

    Returns:
        List of chord segments: [{"start": float, "end": float, "chord": str}, ...]
    """
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        analyze_chords,
        input_path,
        512,
        progress_callback,
    )
    return result

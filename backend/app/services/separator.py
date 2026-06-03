"""Audio separation service — orchestrates Demucs model inference."""

from __future__ import annotations

import asyncio
import os
import subprocess
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from app.ai.demucs import DemucsSeparator

# Global model instance (lazy loaded, shared across requests)
_separator: DemucsSeparator | None = None  # type: ignore[valid-type]


def get_separator(progress_callback: Callable | None = None) -> DemucsSeparator:  # type: ignore[valid-type]
    """Get or create the Demucs separator instance."""
    global _separator
    if _separator is None:
        from app.ai.demucs import DemucsSeparator  # Lazy import for testability

        _separator = DemucsSeparator(progress_callback=progress_callback)
    elif progress_callback:
        _separator.progress_callback = progress_callback
    return _separator


def convert_to_mp3(input_wav: str, output_mp3: str, bitrate: str = "320k") -> str:
    """Convert a WAV file to MP3 using ffmpeg.

    Args:
        input_wav: Path to input WAV file.
        output_mp3: Path to output MP3 file.
        bitrate: MP3 bitrate (e.g., '320k', '192k', '128k').

    Returns:
        Path to the output MP3 file.
    """
    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output
        "-i",
        input_wav,
        "-codec:a",
        "libmp3lame",
        "-b:a",
        bitrate,
        "-map_metadata",
        "-1",  # Strip metadata
        output_mp3,
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return output_mp3


async def run_separation(
    input_path: str,
    output_dir: str,
    mode: str = "2track",
    progress_callback: Callable | None = None,
) -> dict[str, str]:
    """Run audio separation asynchronously.

    Args:
        input_path: Path to input audio file.
        output_dir: Directory to store output files.
        mode: '2track' or '4track'.
        progress_callback: Sync callback(int, str) for progress.

    Returns:
        Dict mapping stem name to WAV file path.
    """
    separator = get_separator(progress_callback)
    # Run in thread pool since Demucs is CPU/GPU bound
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        separator.separate,
        input_path,
        output_dir,
        mode,
    )
    return result


def convert_stems_to_mp3(
    stems: dict[str, str],
    output_dir: str,
    bitrate: str = "320k",
) -> dict[str, str]:
    """Convert all WAV stems to MP3 format.

    Args:
        stems: Dict of stem_name -> WAV file path.
        output_dir: Directory for MP3 output.
        bitrate: MP3 encoding bitrate.

    Returns:
        Dict of stem_name -> MP3 file path.
    """
    mp3_stems: dict[str, str] = {}
    for name, wav_path in stems.items():
        mp3_path = os.path.join(output_dir, f"{name}.mp3")
        convert_to_mp3(wav_path, mp3_path, bitrate)
        mp3_stems[name] = mp3_path
    return mp3_stems

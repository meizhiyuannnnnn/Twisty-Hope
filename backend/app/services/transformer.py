"""Audio transformation service — speed and pitch changes using librosa."""

from __future__ import annotations

import os
from typing import Callable

import librosa
import numpy as np
import soundfile as sf

from app.services.separator import convert_to_mp3


async def transform_audio(
    input_path: str,
    output_dir: str,
    speed: float = 1.0,
    pitch_steps: int = 0,
    progress_callback: Callable | None = None,
) -> dict[str, str]:
    """Apply speed and/or pitch transformation to an audio file.

    Uses librosa.time_stretch (phase vocoder) for speed change and
    librosa.pitch_shift for pitch change. Both preserve quality well.

    Args:
        input_path: Path to input audio file.
        output_dir: Directory to save output.
        speed: Speed multiplier (0.5 to 1.5). 1.0 = no change.
        pitch_steps: Pitch shift in semitones (-12 to +12). 0 = no change.
        progress_callback: Optional sync callback(progress, message).

    Returns:
        Dict with single key "transformed" -> output MP3 path.
    """
    if progress_callback:
        progress_callback(10, "正在加载音频...")

    # Load audio
    y, sr = librosa.load(input_path, sr=None, mono=False)

    if progress_callback:
        progress_callback(30, "正在处理...")

    # Apply speed change (time stretching without pitch change)
    if speed != 1.0:
        if progress_callback:
            progress_callback(40, f"正在变速处理 (x{speed:.2f})...")
        # Process each channel separately for stereo
        if y.ndim == 2:
            channels = []
            for ch in range(y.shape[0]):
                channels.append(librosa.effects.time_stretch(y[ch], rate=speed))
            y = np.stack(channels)
        else:
            y = librosa.effects.time_stretch(y, rate=speed)

    # Apply pitch shift (without changing speed)
    if pitch_steps != 0:
        if progress_callback:
            progress_callback(60, f"正在变调处理 ({pitch_steps:+d} 半音)...")
        if y.ndim == 2:
            channels = []
            for ch in range(y.shape[0]):
                channels.append(
                    librosa.effects.pitch_shift(y[ch], sr=sr, n_steps=pitch_steps)
                )
            y = np.stack(channels)
        else:
            y = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch_steps)

    if progress_callback:
        progress_callback(80, "正在保存处理结果...")

    # Save as WAV first, then convert to MP3
    os.makedirs(output_dir, exist_ok=True)
    wav_path = os.path.join(output_dir, "transformed.wav")
    sf.write(wav_path, y.T if y.ndim == 2 else y, sr)

    mp3_path = os.path.join(output_dir, "transformed.mp3")
    convert_to_mp3(wav_path, mp3_path)

    if progress_callback:
        progress_callback(100, "变速变调处理完成")

    return {"transformed": mp3_path}

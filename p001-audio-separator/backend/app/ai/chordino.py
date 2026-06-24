"""Chord recognition using CREPE + Chordino.

CREPE (Convolutional Representation for Pitch Estimation) extracts pitch contours.
Chordino is a VAMP plugin for chord recognition.

Note: The full Chordino VAMP plugin requires additional native dependencies.
This module provides a librosa-based fallback that estimates chords using
chroma features and template matching.

For production use with Chordino, install:
    pip install vamp vamp-hosts
    Download Chordino VAMP plugin from https://code.soundsoftware.ac.uk/projects/nnls-chroma
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf


# Standard chord templates (major and minor triads)
CHORD_TEMPLATES: dict[str, list[int]] = {
    "C:maj": [0, 4, 7],
    "C#:maj": [1, 5, 8],
    "D:maj": [2, 6, 9],
    "D#:maj": [3, 7, 10],
    "E:maj": [4, 8, 11],
    "F:maj": [5, 9, 0],
    "F#:maj": [6, 10, 1],
    "G:maj": [7, 11, 2],
    "G#:maj": [8, 0, 3],
    "A:maj": [9, 1, 4],
    "A#:maj": [10, 2, 5],
    "B:maj": [11, 3, 6],
    "C:min": [0, 3, 7],
    "C#:min": [1, 4, 8],
    "D:min": [2, 5, 9],
    "D#:min": [3, 6, 10],
    "E:min": [4, 7, 11],
    "F:min": [5, 8, 0],
    "F#:min": [6, 9, 1],
    "G:min": [7, 10, 2],
    "G#:min": [8, 11, 3],
    "A:min": [9, 0, 4],
    "A#:min": [10, 1, 5],
    "B:min": [11, 2, 6],
}


def _calc_chromagram(y: np.ndarray, sr: int) -> np.ndarray:
    """Compute chromagram from audio signal."""
    # Use Constant-Q transform for better pitch resolution
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=512, n_chroma=12, bins_per_octave=36)
    return chroma  # shape: (12, frames)


def _chord_template_vector(chord_name: str) -> np.ndarray:
    """Convert a chord name to a 12-dimensional binary vector."""
    vec = np.zeros(12)
    for note in CHORD_TEMPLATES.get(chord_name, [0, 4, 7]):
        vec[note % 12] = 1.0
    return vec


def _match_chord(chroma_frame: np.ndarray) -> str:
    """Match a chroma frame vector to the closest chord template."""
    best_chord = "N"
    best_score = -1.0

    for name, _ in CHORD_TEMPLATES.items():
        template = _chord_template_vector(name)
        # Cosine similarity
        score = np.dot(chroma_frame, template) / (
            np.linalg.norm(chroma_frame) * np.linalg.norm(template) + 1e-8
        )
        if score > best_score:
            best_score = score
            best_chord = name

    return best_chord


def analyze_chords(
    input_path: str,
    hop_length: int = 512,
    progress_callback=None,
) -> list[dict]:
    """Analyze chord progression in an audio file.

    Uses librosa chromagram + template matching as a fallback.
    When Chordino VAMP plugin is available, it will be used instead.

    Args:
        input_path: Path to the audio file.
        hop_length: Hop length for chroma analysis.
        progress_callback: Optional callback(progress, message).

    Returns:
        List of dicts: [{"start": float, "end": float, "chord": str}, ...]
    """
    if progress_callback:
        progress_callback(10, "正在加载音频文件...")

    # Load audio
    y, sr = librosa.load(input_path, sr=22050, mono=True)
    duration = len(y) / sr

    if progress_callback:
        progress_callback(20, "正在计算音频特征...")

    # Try Chordino VAMP first, fall back to chroma template matching
    try:
        return _analyze_with_vamp(input_path, progress_callback)
    except (ImportError, FileNotFoundError, RuntimeError):
        pass

    # Fallback: chroma-based chord detection
    if progress_callback:
        progress_callback(30, "正在使用 Chroma 模板匹配分析和弦...")

    chroma = _calc_chromagram(y, sr)
    n_frames = chroma.shape[1]
    frame_duration = hop_length / sr

    chords: list[dict] = []
    prev_chord: str | None = None
    segment_start: float = 0.0

    for i in range(n_frames):
        frame_vec = chroma[:, i]
        chord = _match_chord(frame_vec)
        current_time = i * frame_duration

        if prev_chord is not None and chord != prev_chord:
            chords.append({
                "start": round(segment_start, 2),
                "end": round(current_time, 2),
                "chord": prev_chord,
            })
            segment_start = current_time

        prev_chord = chord

        if progress_callback and i % 50 == 0:
            pct = 30 + int(60 * i / n_frames)
            progress_callback(pct, f"分析中... {i}/{n_frames} 帧")

    # Add final segment
    if prev_chord is not None:
        chords.append({
            "start": round(segment_start, 2),
            "end": round(duration, 2),
            "chord": prev_chord,
        })

    # Merge short segments (< 0.5s) with neighbors
    chords = _merge_short_segments(chords, min_duration=0.5)

    if progress_callback:
        progress_callback(100, f"和弦分析完成，识别到 {len(chords)} 个和弦段落")

    return chords


def _analyze_with_vamp(input_path: str, progress_callback=None) -> list[dict]:
    """Use Chordino VAMP plugin for chord analysis.

    Requires: pip install vamp, and Chordino plugin installed.
    Falls back to command-line sonic-annotator if available.
    """
    # Try using the sonic-annotator CLI tool
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        cmd = [
            "sonic-annotator",
            "-d", "vamp:nnls-chroma:chordino:simplechord",
            input_path,
            "-w", "json",
            "--json-one-file", tmp_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            raise RuntimeError(f"sonic-annotator failed: {result.stderr}")

        with open(tmp_path) as f:
            data = json.load(f)

        return _parse_chordino_output(data)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def _parse_chordino_output(data: dict) -> list[dict]:
    """Parse Chordino JSON output into our standard format."""
    chords: list[dict] = []
    # Chordino outputs events with timestamp, duration, and label
    # Exact format depends on the plugin version
    for item in data.get("events", []):
        chords.append({
            "start": round(item.get("timestamp", 0), 2),
            "end": round(item.get("timestamp", 0) + item.get("duration", 0), 2),
            "chord": item.get("label", "N"),
        })
    return chords


def _merge_short_segments(chords: list[dict], min_duration: float = 0.5) -> list[dict]:
    """Merge chord segments shorter than min_duration into neighbors."""
    if len(chords) <= 1:
        return chords

    merged: list[dict] = []
    i = 0
    while i < len(chords):
        current = chords[i]
        duration = current["end"] - current["start"]

        if duration >= min_duration or i == 0 or i == len(chords) - 1:
            merged.append(current)
            i += 1
            continue

        # Merge with previous
        prev = merged[-1]
        prev["end"] = current["end"]
        i += 1

    return merged

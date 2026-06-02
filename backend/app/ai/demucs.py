"""Demucs HT source separation wrapper.

Demucs HT (Hybrid Transformer) is Meta's state-of-the-art music source separation model.
It separates audio into 4 sources: vocals, drums, bass, other.

For 2-track mode (vocals + accompaniment):
    - vocals: kept as-is
    - accompaniment: drums + bass + other mixed together

Model file is automatically downloaded via torch.hub on first use.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import numpy as np
import torch
import torchaudio

from app.core.config import settings


class DemucsSeparator:
    """Wrapper around Demucs HT for audio source separation."""

    def __init__(self, progress_callback=None):
        """Initialize Demucs model.

        Args:
            progress_callback: Optional async callback(progress_pct, message) for progress updates.
        """
        self.model = None
        self.device = settings.DEVICE if torch.cuda.is_available() else "cpu"
        self.progress_callback = progress_callback

    def _ensure_model_loaded(self) -> None:
        """Lazy-load the Demucs model."""
        if self.model is not None:
            return
        self._report_progress(5, "正在加载 Demucs HT 模型...")
        self.model = torch.hub.load("facebookresearch/demucs", settings.DEMUCS_MODEL)
        self.model.to(self.device)
        self.model.eval()
        self._report_progress(10, "Demucs HT 模型加载完成")

    def _report_progress(self, pct: int, message: str) -> None:
        """Report progress via callback if available."""
        if self.progress_callback:
            self.progress_callback(pct, message)

    def separate(
        self,
        input_path: str,
        output_dir: str,
        mode: str = "4track",
    ) -> dict[str, str]:
        """Run source separation on an audio file.

        Args:
            input_path: Path to the input audio file.
            output_dir: Directory to write output files.
            mode: '2track' for vocals+accompaniment, '4track' for 4 stems.

        Returns:
            Dict mapping stem name to output file path.
        """
        self._ensure_model_loaded()

        # Load audio
        self._report_progress(10, "正在读取音频文件...")
        wav, sr = torchaudio.load(input_path)

        # Resample if necessary
        if sr != self.model.samplerate:
            self._report_progress(15, "正在重采样...")
            wav = torchaudio.functional.resample(wav, sr, self.model.samplerate)
            sr = self.model.samplerate

        # Convert to mono if needed (Demucs expects stereo, but handles mono too)
        if wav.shape[0] == 1:
            wav = wav.repeat(2, 1)

        wav = wav.to(self.device)

        # Run separation
        self._report_progress(20, "正在执行音频分离（这可能需要几分钟）...")
        start_time = time.time()

        with torch.no_grad():
            # Demucs returns a dict of {source_name: tensor}
            sources = self.model.separate(wav[None])  # Add batch dimension

        elapsed = time.time() - start_time

        # sources is a dict like {'vocals': (1, 2, samples), 'drums': ..., 'bass': ..., 'other': ...}
        os.makedirs(output_dir, exist_ok=True)

        results: dict[str, str] = {}

        if mode == "2track":
            # Mix drums + bass + other into accompaniment
            self._report_progress(80, "正在合成伴奏轨道...")
            accompaniment = (
                sources["drums"][0] + sources["bass"][0] + sources["other"][0]
            )
            # Normalize to prevent clipping
            max_val = accompaniment.abs().max()
            if max_val > 1.0:
                accompaniment = accompaniment / max_val

            # Save vocals
            vocals_path = os.path.join(output_dir, "vocals.wav")
            torchaudio.save(vocals_path, sources["vocals"][0].cpu(), sr)
            results["vocals"] = vocals_path

            # Save accompaniment
            accomp_path = os.path.join(output_dir, "accompaniment.wav")
            torchaudio.save(accomp_path, accompaniment.cpu(), sr)
            results["accompaniment"] = accomp_path

            self._report_progress(95, f"分离完成，耗时 {elapsed:.1f} 秒")
        else:
            # 4-track: save all stems
            step_pct = 60.0 / len(sources)
            for i, (name, source) in enumerate(sources.items()):
                pct = 20 + int((i + 1) * step_pct)
                self._report_progress(pct, f"正在保存 {name} 轨道...")
                out_path = os.path.join(output_dir, f"{name}.wav")
                torchaudio.save(out_path, source[0].cpu(), sr)
                results[name] = out_path
            self._report_progress(95, f"分离完成，耗时 {elapsed:.1f} 秒")

        self._report_progress(100, "处理完成")
        return results

    @staticmethod
    def get_output_stems(mode: str) -> list[str]:
        """Return expected output stem names for a given mode."""
        if mode == "2track":
            return ["vocals", "accompaniment"]
        return ["vocals", "drums", "bass", "other"]

"""Demucs HT source separation wrapper.

Uses ``torchaudio.models.hdemucs_high`` (built-in) to avoid relying on
``torch.hub.load`` which requires GitHub access.  Model weights are
downloaded from ModelScope (modelscope.cn) — accessible in China.

For 2-track mode (vocals + accompaniment):
    - vocals: kept as-is
    - accompaniment: drums + bass + other mixed together
"""

from __future__ import annotations

import os
import time

import torch
import torchaudio

from app.core.config import settings

# ModelScope repo for the hdemucs_high weights
MODELSCOPE_MODEL = "monetjoe/hdemucs_high_musdbhq"


class DemucsSeparator:
    """Wrapper around HDemucs for audio source separation."""

    def __init__(self, progress_callback=None):
        self.model = None
        self.device = settings.DEVICE if torch.cuda.is_available() else "cpu"
        self.progress_callback = progress_callback
        self._sources = ["drums", "bass", "other", "vocals"]

    def _ensure_model_loaded(self) -> None:
        """Lazy-load the HDemucs model and weights."""
        if self.model is not None:
            return

        self._report_progress(2, "正在加载 HDemucs 模型架构...")
        model = torchaudio.models.hdemucs_high(
            sources=self._sources,
        )
        self._sources = model.sources  # use the canonical ordering

        # Download / load weights from ModelScope (or local cache)
        self._report_progress(4, "正在下载模型权重（首次约 300MB）...")
        weight_path = self._get_weights()
        state_dict = torch.load(weight_path, map_location="cpu", weights_only=True)
        model.load_state_dict(state_dict)

        model.to(self.device)
        model.eval()
        self.model = model
        self._report_progress(10, "HDemucs 模型加载完成")

    @staticmethod
    def _get_weights() -> str:
        """Return path to the model weights file, downloading if needed."""
        from pathlib import Path

        import modelscope

        cache_dir = Path.home() / ".cache" / "torch" / "hub"
        cache_dir.mkdir(parents=True, exist_ok=True)

        model_dir = modelscope.snapshot_download(
            MODELSCOPE_MODEL,
            cache_dir=str(cache_dir),
        )
        # The checkpoint file name inside the repo
        weight_file = os.path.join(model_dir, "hdemucs_high_musdbhq_only.pt")
        if not os.path.exists(weight_file):
            # Try alternative names
            for f in os.listdir(model_dir):
                if f.endswith(".pt") or f.endswith(".pth"):
                    weight_file = os.path.join(model_dir, f)
                    break
        return weight_file

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

        # Load audio (use soundfile backend to avoid torchcodec dependency)
        self._report_progress(10, "正在读取音频文件...")
        import soundfile as sf

        data, sr = sf.read(input_path)
        # soundfile returns (samples, channels) as float64 numpy array,
        # torchaudio expects (channels, samples) as float32 tensor
        if data.ndim == 1:
            # Mono → duplicate to stereo
            data = data.reshape(-1, 1)
        wav = torch.from_numpy(data.T.copy()).float()

        # Resample to 44100 Hz (HDemucs sample rate)
        if sr != 44100:
            self._report_progress(15, "正在重采样到 44100 Hz...")
            wav = torchaudio.functional.resample(wav, sr, 44100)
            sr = 44100

        # Ensure stereo
        if wav.shape[0] == 1:
            wav = wav.repeat(2, 1)
        elif wav.shape[0] > 2:
            wav = wav[:2, :]  # take first 2 channels

        # Normalize
        ref = wav.mean(dim=0)
        wav = (wav - ref.mean()) / (ref.std() + 1e-8)

        wav = wav.to(self.device)

        # Run separation
        self._report_progress(20, "正在执行音频分离（这可能需要几分钟）...")
        start_time = time.time()

        with torch.no_grad():
            # Model expects (batch, sources, channels, samples)
            sources = self.model(wav[None])[0]  # remove batch dim

        elapsed = time.time() - start_time
        os.makedirs(output_dir, exist_ok=True)

        results: dict[str, str] = {}

        if mode == "2track":
            # Find vocals index
            vocals_idx = self._sources.index("vocals")
            vocals = sources[vocals_idx]

            # Mix non-vocal stems into accompaniment
            acc_indices = [i for i, n in enumerate(self._sources) if n != "vocals"]
            accompaniment = sources[acc_indices].sum(dim=0)

            # Normalize
            max_val = accompaniment.abs().max()
            if max_val > 1.0:
                accompaniment = accompaniment / max_val

            self._report_progress(80, "正在保存音频轨道...")

            vocals_path = os.path.join(output_dir, "vocals.wav")
            sf.write(vocals_path, vocals.cpu().T.numpy(), sr)
            results["vocals"] = vocals_path

            accomp_path = os.path.join(output_dir, "accompaniment.wav")
            sf.write(accomp_path, accompaniment.cpu().T.numpy(), sr)
            results["accompaniment"] = accomp_path

            self._report_progress(95, f"分离完成，耗时 {elapsed:.1f} 秒")
        else:
            # 4-track: save all stems
            step_pct = 60.0 / len(self._sources)
            for i, name in enumerate(self._sources):
                pct = 20 + int((i + 1) * step_pct)
                self._report_progress(pct, f"正在保存 {name} 轨道...")
                out_path = os.path.join(output_dir, f"{name}.wav")
                sf.write(out_path, sources[i].cpu().T.numpy(), sr)
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

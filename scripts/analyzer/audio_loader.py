"""Chargement audio en numpy float32, stereo preserve.

soundfile gere nativement WAV/FLAC/OGG/AIFF. Pour MP3/AAC/M4A/Opus on
retombe sur librosa (qui passe par audioread/ffmpeg).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np


def load_audio(path: Path) -> tuple[np.ndarray, int]:
    """Retourne (data, samplerate).

    `data` est en float32 dans [-1, 1], shape :
    - (samples,) si mono
    - (samples, channels) si multicanal
    """
    import warnings
    try:
        import soundfile as sf
        data, sr = sf.read(str(path), always_2d=False, dtype="float32")
    except Exception:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import librosa
            data, sr = librosa.load(str(path), sr=None, mono=False)
            if data.ndim == 2:
                data = data.T
            data = data.astype(np.float32)
    return data, int(sr)


def to_mono(data: np.ndarray) -> np.ndarray:
    """Reduit en mono par moyenne des canaux."""
    if data.ndim == 1:
        return data
    return data.mean(axis=1).astype(np.float32)

"""Analyse temporelle : peak / true peak / RMS / clipping."""
from __future__ import annotations

import numpy as np

from .audio_loader import to_mono
from .types import SignalReport

# Seuil de clipping : -0.026 dBFS (samples a la limite du conteneur)
CLIPPING_THRESHOLD = 0.997


def _to_dbfs(value: float) -> float:
    """Convertit une amplitude lineaire [0, 1] en dBFS. -inf si silence."""
    if value <= 0:
        return float("-inf")
    return float(20.0 * np.log10(value))


def _true_peak(mono: np.ndarray, oversample: int = 4) -> float:
    """True peak via oversampling polyphasique (ITU-R BS.1770).

    L'oversampling 4x detecte les intersample peaks qui apparaissent apres
    reconstruction DAC. Utilise scipy.signal.resample_poly pour la qualite."""
    from scipy.signal import resample_poly

    # Limite la taille pour eviter une explosion memoire sur les morceaux longs
    max_samples = 30 * 48000  # ~30s suffisent pour estimer le true peak
    if len(mono) > max_samples:
        # Echantillonnage : prend plusieurs fenetres uniformement
        step = len(mono) // 6
        windows = [mono[i:i + max_samples // 6] for i in range(0, len(mono), step)][:6]
        peak = 0.0
        for win in windows:
            up = resample_poly(win, oversample, 1)
            peak = max(peak, float(np.abs(up).max()))
        return peak
    upsampled = resample_poly(mono, oversample, 1)
    return float(np.abs(upsampled).max())


def analyze(data: np.ndarray) -> SignalReport:
    mono = to_mono(data)
    abs_mono = np.abs(mono)
    sample_peak = float(abs_mono.max())
    rms = float(np.sqrt(np.mean(mono.astype(np.float64) ** 2)))

    clipped_mask = abs_mono >= CLIPPING_THRESHOLD
    clipping_count = int(clipped_mask.sum())
    clipping_ratio = clipping_count / len(mono) if len(mono) > 0 else 0.0

    tp = _true_peak(mono)

    return SignalReport(
        sample_peak_dbfs=_to_dbfs(sample_peak),
        true_peak_dbfs=_to_dbfs(tp),
        rms_dbfs=_to_dbfs(rms),
        clipping_ratio=clipping_ratio,
        clipping_count=clipping_count,
    )

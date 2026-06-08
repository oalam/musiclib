"""Mesure de loudness ITU-R BS.1770 via pyloudnorm."""
from __future__ import annotations

import numpy as np

from .types import LoudnessReport


def analyze(data: np.ndarray, sample_rate: int) -> LoudnessReport:
    """LUFS integre + loudness range (LRA).

    pyloudnorm calcule directement le LUFS integre selon BS.1770-4. Le LRA
    n'est pas expose en standard ; on l'approche via la distribution des
    LUFS short-term (fenetre 3s, hop 1s) avec gating relatif."""
    import pyloudnorm as pyln

    # pyloudnorm accepte (samples,) ou (samples, channels)
    meter = pyln.Meter(sample_rate)
    try:
        integrated = float(meter.integrated_loudness(data))
    except Exception:
        integrated = float("-inf")

    lra = _loudness_range(data, sample_rate, meter)

    return LoudnessReport(
        integrated_lufs=integrated if np.isfinite(integrated) else -70.0,
        loudness_range_lu=lra,
    )


def _loudness_range(data: np.ndarray, sr: int, meter: object) -> float:
    """Approximation LRA via fenetres short-term gatees relatives."""
    block_s = 3.0
    hop_s = 1.0
    block_n = int(block_s * sr)
    hop_n = int(hop_s * sr)
    if len(data) < block_n * 2:
        return 0.0

    short_term: list[float] = []
    for start in range(0, len(data) - block_n, hop_n):
        block = data[start:start + block_n]
        try:
            value = float(meter.integrated_loudness(block))  # type: ignore[attr-defined]
        except Exception:
            continue
        if np.isfinite(value) and value > -70:
            short_term.append(value)

    if len(short_term) < 10:
        return 0.0
    arr = np.array(short_term)
    # Gating relatif : on garde les blocs au-dessus de (moyenne - 20 LU)
    threshold = float(arr.mean()) - 20.0
    kept = arr[arr > threshold]
    if len(kept) < 2:
        return 0.0
    return float(np.percentile(kept, 95) - np.percentile(kept, 10))

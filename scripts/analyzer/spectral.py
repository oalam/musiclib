"""Analyse spectrale : largeur de bande utile et detection fake-lossless.

Strategie : on calcule la PSD (Welch), on identifie la frequence au-dessus
de laquelle l'energie spectrale chute brutalement (signature du low-pass
des codecs lossy). Un FLAC qui cale a 16 kHz est en realite un MP3 128
re-encode."""
from __future__ import annotations

import numpy as np

from .audio_loader import to_mono
from .types import SpectralReport


def _psd(data: np.ndarray, sr: int) -> tuple[np.ndarray, np.ndarray]:
    from scipy.signal import welch
    mono = to_mono(data).astype(np.float64)
    nperseg = min(8192, len(mono))
    if nperseg < 256:
        return np.array([]), np.array([])
    freqs, psd = welch(mono, fs=sr, nperseg=nperseg)
    return freqs, psd


def _bandwidth_cutoff(freqs: np.ndarray, psd: np.ndarray) -> float:
    """Frequence de coupure : on descend depuis Nyquist tant que la PSD est
    au-dessus d'un seuil relatif a la PSD max dans la bande utile."""
    if len(freqs) == 0 or len(psd) == 0:
        return 0.0
    # Reference : max PSD entre 1 kHz et 6 kHz (zone de contenu musical)
    ref_band = (freqs >= 1000) & (freqs <= 6000)
    if not ref_band.any():
        return float(freqs[-1])
    ref_max = float(psd[ref_band].max())
    if ref_max <= 0:
        return float(freqs[-1])
    threshold = ref_max * 1e-4  # -40 dB relatif a la zone musicale
    # Cherche la derniere freq ou psd > threshold
    above = np.where(psd > threshold)[0]
    if len(above) == 0:
        return 0.0
    return float(freqs[above[-1]])


def _fake_lossless_probability(cutoff_hz: float, is_lossless: bool) -> float:
    """Probabilite que la source soit en realite lossy.

    Non applicable si le conteneur est deja lossy (retourne 0).
    Pour un conteneur lossless, on s'attend a cutoff > 20 kHz."""
    if not is_lossless:
        return 0.0
    if cutoff_hz >= 21000:
        return 0.0
    if cutoff_hz >= 19500:
        return 0.2
    if cutoff_hz >= 17500:
        return 0.55
    if cutoff_hz >= 15500:
        return 0.85
    return 0.95


def _hf_energy_ratio(freqs: np.ndarray, psd: np.ndarray, threshold_hz: float = 16000) -> float:
    """Fraction d'energie spectrale au-dessus du seuil."""
    if len(psd) == 0 or psd.sum() <= 0:
        return 0.0
    mask = freqs > threshold_hz
    if not mask.any():
        return 0.0
    return float(psd[mask].sum() / psd.sum())


def analyze(data: np.ndarray, sample_rate: int, is_lossless_container: bool) -> SpectralReport:
    freqs, psd = _psd(data, sample_rate)
    cutoff = _bandwidth_cutoff(freqs, psd)
    hf_ratio = _hf_energy_ratio(freqs, psd)
    fake_p = _fake_lossless_probability(cutoff, is_lossless_container)
    return SpectralReport(
        bandwidth_cutoff_hz=round(cutoff, 0),
        high_freq_energy_ratio=round(hf_ratio, 4),
        fake_lossless_probability=round(fake_p, 2),
    )

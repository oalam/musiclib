"""Analyse fréquentielle par bandes (Phase 6.A).

Mesure le pourcentage d'energie spectrale dans 7 bandes :
- sub      (20-60 Hz)    : caisson sub, critical pour sound system
- bass     (60-200 Hz)   : bass
- low_mid  (200-500 Hz)  : zone de mud
- mid      (500-2k Hz)   : corps des leads
- presence (2k-5k Hz)    : clarté / intelligibilité
- high     (5k-10k Hz)   : zone des cymbales / synthese aigue
- air      (10k+ Hz)     : harmoniques aigus

Total normalise a 100%. Calcul via Welch PSD (8192 samples par fenetre)
puis integration de la densite dans chaque bande.
"""
from __future__ import annotations

import numpy as np

from .audio_loader import to_mono
from .types import FrequencyBandsReport

# (lo_hz, hi_hz, field_name)
_BANDS: list[tuple[float, float, str]] = [
    (20,    60,           "sub_pct"),
    (60,    200,          "bass_pct"),
    (200,   500,          "low_mid_pct"),
    (500,   2000,         "mid_pct"),
    (2000,  5000,         "presence_pct"),
    (5000,  10000,        "high_pct"),
    (10000, float("inf"), "air_pct"),
]


def _classify_profile(values: dict[str, float]) -> str:
    """Heuristique de profil tonal en mots cles."""
    low = values["sub_pct"] + values["bass_pct"]
    mid = values["low_mid_pct"] + values["mid_pct"]
    high = values["presence_pct"] + values["high_pct"] + values["air_pct"]

    if low < 12:
        return "thin"
    if low >= 45 and high < 15:
        return "bass-heavy"
    if low >= 35 and high >= 20:
        return "warm full"
    if mid >= 55:
        return "mid-heavy"
    if high >= 35:
        return "bright"
    if abs(low - high) <= 10 and abs(low - mid) <= 15:
        return "balanced"
    return "balanced"


def analyze(data: np.ndarray, sample_rate: int) -> FrequencyBandsReport:
    """Compute energy % per frequency band via Welch PSD."""
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from scipy.signal import welch

        mono = to_mono(data).astype(np.float64)
        nperseg = min(16384, len(mono))
        if nperseg < 256:
            return FrequencyBandsReport()
        freqs, psd = welch(mono, fs=sample_rate, nperseg=nperseg)

    # Limite a la bande utile (au-dessus de 20 Hz)
    mask_useful = freqs >= 20
    total = float(psd[mask_useful].sum())
    if total <= 0:
        return FrequencyBandsReport()

    values: dict[str, float] = {}
    for lo, hi, field in _BANDS:
        m = (freqs >= lo) & (freqs < hi)
        if m.any():
            values[field] = round(float(psd[m].sum() / total * 100), 1)
        else:
            values[field] = 0.0

    return FrequencyBandsReport(
        **values,
        tonal_profile=_classify_profile(values),
    )


def to_compact_string(report: FrequencyBandsReport) -> str:
    """Format compact pour library.md : 'sub:8 bass:22 lowmid:18 ...'."""
    return (
        f"sub:{int(round(report.sub_pct))} "
        f"bass:{int(round(report.bass_pct))} "
        f"lowmid:{int(round(report.low_mid_pct))} "
        f"mid:{int(round(report.mid_pct))} "
        f"pres:{int(round(report.presence_pct))} "
        f"high:{int(round(report.high_pct))} "
        f"air:{int(round(report.air_pct))}"
        f" | {report.tonal_profile}"
        if report.tonal_profile else
        f"sub:{int(round(report.sub_pct))} ..."
    )

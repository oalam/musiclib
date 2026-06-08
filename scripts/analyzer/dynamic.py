"""Dynamique du signal : crest factor + categorisation."""
from __future__ import annotations

from .types import DynamicReport, SignalReport


def categorize_crest(crest_db: float) -> str:
    """Classe la dynamique selon crest factor en dB.

    >12 dB : tres dynamique (mastering audiophile, classique, jazz)
    8-12 dB : bon mastering moderne
    6-8 dB  : compresse standard (radio, club)
    <6 dB   : surcompresse (brickwall, loudness war)
    """
    if crest_db >= 12.0:
        return "very_dynamic"
    if crest_db >= 8.0:
        return "good"
    if crest_db >= 6.0:
        return "modern"
    if crest_db >= 4.0:
        return "compressed"
    return "overcompressed"


def analyze(signal: SignalReport) -> DynamicReport:
    """Crest factor = peak - RMS, en dB."""
    crest = signal.true_peak_dbfs - signal.rms_dbfs
    return DynamicReport(
        crest_factor_db=round(crest, 2),
        dynamic_rating=categorize_crest(crest),
    )

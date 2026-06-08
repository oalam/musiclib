"""Score audiophile agrege.

Pondeoration (sur 100, normalisee sur les categories presentes en Phase 1) :
- Dynamique         25
- Spectre           25
- Clipping          20
- Codec/transcoding 15
- (Stereo / noise : Phase 2)

Les seuils sont calibres sur une heuristique generique adaptee aux musiques
electroniques modernes : pas de penalite pour un mastering 'club' (8-10 dB
de crest), mais red flag si on detecte un brickwall ou un transcoding."""
from __future__ import annotations

from .types import (
    DynamicReport,
    LoudnessReport,
    MetadataReport,
    QualityScore,
    SignalReport,
    SpectralReport,
)

WEIGHTS = {
    "dynamic": 25.0,
    "spectral": 25.0,
    "clipping": 20.0,
    "codec": 15.0,
}


def _dynamic_score(dyn: DynamicReport) -> float:
    cf = dyn.crest_factor_db
    if cf >= 12:
        return 100.0
    if cf >= 8:
        # 8 -> 70, 12 -> 100 (linear)
        return 70.0 + (cf - 8.0) * 7.5
    if cf >= 6:
        return 40.0 + (cf - 6.0) * 15.0
    if cf >= 4:
        return 20.0 + (cf - 4.0) * 10.0
    return max(0.0, cf * 5.0)


def _spectral_score(spec: SpectralReport, is_lossless: bool) -> float:
    """Score base sur la largeur de bande utile.

    Pour un conteneur lossy, on attend ~20 kHz pour ≥256 kbps, ~17 kHz pour
    128 kbps. Pour un lossless, on attend > 21 kHz."""
    cutoff = spec.bandwidth_cutoff_hz
    if is_lossless:
        if cutoff >= 21000:
            return 100.0
        if cutoff >= 19500:
            return 80.0
        if cutoff >= 17500:
            return 55.0
        if cutoff >= 15500:
            return 30.0
        return 15.0
    # Lossy : cutoff plus permissif (un Opus 128 cale a 19-20 kHz)
    if cutoff >= 19500:
        return 100.0
    if cutoff >= 18000:
        return 85.0
    if cutoff >= 16500:
        return 70.0
    if cutoff >= 15000:
        return 50.0
    if cutoff >= 12000:
        return 30.0
    return 15.0


def _clipping_score(sig: SignalReport) -> float:
    cr = sig.clipping_ratio
    if cr < 1e-5:
        return 100.0
    if cr < 1e-4:
        return 85.0
    if cr < 1e-3:
        return 65.0
    if cr < 1e-2:
        return 35.0
    return 10.0


def _codec_score(meta: MetadataReport, spec: SpectralReport) -> float:
    """Qualite du codec / detection transcoding."""
    if meta.is_lossless_container:
        if spec.fake_lossless_probability > 0.5:
            return 25.0  # fake lossless = pire qu'un mp3 honnete
        return 100.0
    # Lossy : score par bitrate
    br = meta.bitrate_kbps or 0
    if br >= 320:
        base = 95.0
    elif br >= 256:
        base = 90.0
    elif br >= 192:
        base = 80.0
    elif br >= 160:
        base = 70.0
    elif br >= 128:
        base = 55.0
    elif br >= 96:
        base = 35.0
    else:
        base = 20.0
    # Bonus pour les codecs efficients
    if "opus" in meta.codec:
        base = min(100.0, base + 15.0)
    elif "vorbis" in meta.codec:
        base = min(100.0, base + 8.0)
    elif "aac" in meta.codec or "mp4a" in meta.codec:
        base = min(100.0, base + 5.0)
    return base


def _rating(score: float) -> str:
    if score >= 95:
        return "reference"
    if score >= 85:
        return "excellent"
    if score >= 70:
        return "good"
    if score >= 50:
        return "average"
    if score >= 30:
        return "poor"
    return "severely_degraded"


def _flags(
    meta: MetadataReport,
    sig: SignalReport,
    loud: LoudnessReport,
    dyn: DynamicReport,
    spec: SpectralReport,
) -> list[str]:
    out: list[str] = []
    if dyn.dynamic_rating == "overcompressed":
        out.append("overcompressed")
    if sig.clipping_ratio > 1e-3:
        out.append("clipping_detected")
    if sig.true_peak_dbfs > -0.1:
        out.append("intersample_clipping_risk")
    if loud.integrated_lufs > -7.0:
        out.append("crushed_master")
    if meta.is_lossless_container and spec.fake_lossless_probability > 0.5:
        out.append("fake_lossless_suspected")
    if not meta.is_lossless_container and (meta.bitrate_kbps or 0) < 128:
        out.append("low_bitrate")
    if meta.sample_rate_hz < 44100:
        out.append("low_sample_rate")
    return out


def compute(
    meta: MetadataReport,
    sig: SignalReport,
    loud: LoudnessReport,
    dyn: DynamicReport,
    spec: SpectralReport,
) -> QualityScore:
    components = {
        "dynamic": round(_dynamic_score(dyn), 1),
        "spectral": round(_spectral_score(spec, meta.is_lossless_container), 1),
        "clipping": round(_clipping_score(sig), 1),
        "codec": round(_codec_score(meta, spec), 1),
    }
    total_w = sum(WEIGHTS.values())
    weighted = sum(components[k] * WEIGHTS[k] for k in WEIGHTS) / total_w
    score = max(0.0, min(100.0, weighted))
    return QualityScore(
        score=round(score, 1),
        rating=_rating(score),
        components=components,
        flags=_flags(meta, sig, loud, dyn, spec),
    )

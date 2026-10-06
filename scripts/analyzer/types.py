"""Modeles Pydantic pour serialisation JSON et passage entre modules."""
from __future__ import annotations

from pydantic import BaseModel, Field


class MetadataReport(BaseModel):
    """Issu de ffprobe : caracteristiques du conteneur audio."""
    codec: str
    bitrate_kbps: int | None = None
    sample_rate_hz: int
    bit_depth: int | None = None
    channels: int
    duration_s: float
    container: str
    is_lossless_container: bool
    encoder: str | None = None


class SignalReport(BaseModel):
    """Mesures temporelles brutes sur le signal."""
    sample_peak_dbfs: float
    true_peak_dbfs: float
    rms_dbfs: float
    clipping_ratio: float = Field(..., description="Fraction de samples >= 0.997")
    clipping_count: int


class LoudnessReport(BaseModel):
    """Mesures perceptuelles (ITU-R BS.1770)."""
    integrated_lufs: float
    loudness_range_lu: float


class DynamicReport(BaseModel):
    """Dynamique percue."""
    crest_factor_db: float
    dynamic_rating: str  # very_dynamic / good / modern / compressed / overcompressed


class SpectralReport(BaseModel):
    """Analyse spectrale : largeur de bande utile et coherence lossless."""
    bandwidth_cutoff_hz: float
    high_freq_energy_ratio: float
    fake_lossless_probability: float = Field(
        0.0,
        description="0 si conteneur lossy (non applicable), 0-1 si lossless",
    )


class QualityScore(BaseModel):
    """Score audiophile agrege."""
    score: float = Field(..., ge=0, le=100)
    rating: str  # reference / excellent / good / average / poor / severely_degraded
    components: dict[str, float]
    flags: list[str] = Field(default_factory=list)


class BeatReport(BaseModel):
    """Beat tracking : tempo + positions des beats + confiance + rythmique
    enrichie (Phase 6.C)."""
    tempo_bpm: float
    beat_count: int
    beat_times_s: list[float] = Field(default_factory=list)
    half_time_corrected: bool = False
    manual_override: bool = Field(
        False, description="True si tempo vient de library.md (corrigé à la main)"
    )
    confidence: float = Field(
        1.0, ge=0, le=1,
        description="Confiance dans le tempo (1.0 = sûr, <0.7 = incertain)",
    )
    candidates_bpm: list[float] = Field(
        default_factory=list,
        description="BPM alternatifs detectes (half-time, autre algo, etc.)",
    )
    # Phase 6.C
    onset_density_per_s: float = Field(
        0.0, ge=0,
        description="Onsets / seconde — proxy de complexite rythmique",
    )
    beat_strength: float = Field(
        0.0, ge=0,
        description="Amplitude moyenne des onsets aux positions de beats (proxy 'punch')",
    )
    time_signature: str = Field(
        "4/4", description="Signature detectee : 4/4 / 3/4 / 6/8 / 5/4 / 7/8 / 17/8"
    )
    time_signature_confidence: float = Field(
        0.5, ge=0, le=1,
        description="Confiance dans la signature (4/4 = par defaut si bas)",
    )


class RhythmSignatureReport(BaseModel):
    """Empreinte de groove tempo-invariante (Phase 6.D).

    Decrit la *forme* du pattern rythmique, plie sur une mesure de 16 pas,
    independamment du tempo. Concue pour la similarite et le clustering par
    groove : elle n'encode VOLONTAIREMENT ni BPM, ni key, ni energy (ces axes
    sont deja couverts par Camelot + BPM + energy dans `compatibility.py`),
    afin de rester orthogonale et non redondante.

    Les patterns sont normalises (max = 1.0). Comparaison via cross-correlation
    sur les 16 rotations (invariance a la phase du downbeat) : cf.
    `rhythm_signature.rhythm_distance`.
    """
    steps: int = Field(16, description="Nombre de pas par mesure (16 = doubles-croches en 4/4)")
    beats_per_bar: int = Field(4, description="Beats par mesure deduits de time_signature")
    bars_used: int = Field(0, ge=0, description="Nombre de mesures repliees pour l'agregat")
    bar_pattern: list[float] = Field(
        default_factory=list,
        description="Pattern global (somme des bandes), 1 valeur par pas, normalise",
    )
    sub_pattern: list[float] = Field(
        default_factory=list, description="Pattern bande sub/bass (kick) — 20-200 Hz"
    )
    mid_pattern: list[float] = Field(
        default_factory=list, description="Pattern bande mid (snare/clap/corps) — 200-2k Hz"
    )
    high_pattern: list[float] = Field(
        default_factory=list, description="Pattern bande high (hats/texture) — 2k Hz+"
    )
    syncopation: float = Field(
        0.0, ge=0, le=1,
        description="Part d'energie hors-temps vs sur-temps (0 = martele, 1 = tres syncope)",
    )
    pulse_clarity: float = Field(
        0.0, ge=0, le=1,
        description="Nettete/regularite du pulse (1 = metronomique, 0 = flou)",
    )
    swing: float = Field(
        0.0, ge=0, le=1,
        description="Microtiming des contretemps (0 = droit, >0.5 = shuffle marque)",
    )
    method: str = "onset_fold_16_per_band"


class Segment(BaseModel):
    """Un segment structurel du morceau."""
    start_s: float
    end_s: float
    duration_s: float
    rms_dbfs: float
    label: str  # intro / build / peak / main / breakdown / outro


class StructureReport(BaseModel):
    """Decoupage en segments par features beat-synchrones."""
    segments: list[Segment]
    n_segments: int
    method: str = "librosa_agglomerative_beat_sync"


class CuePoint(BaseModel):
    """Un cue point detecte."""
    time_s: float
    type: str  # intro_start / beat_entry / drop / breakdown / outro
    confidence: float = Field(..., ge=0, le=1)
    label: str | None = None


class CuesReport(BaseModel):
    """Liste de cue points + format generique JSON."""
    cues: list[CuePoint]


class FrequencyBandsReport(BaseModel):
    """Distribution d'energie par bandes de frequence (Phase 6.A).

    Pourcentages d'energie integree par bande, somme = 100%. Aide a
    evaluer le contenu spectral pour un sound system free party."""
    sub_pct: float = Field(0.0, ge=0, le=100, description="20-60 Hz")
    bass_pct: float = Field(0.0, ge=0, le=100, description="60-200 Hz")
    low_mid_pct: float = Field(0.0, ge=0, le=100, description="200-500 Hz")
    mid_pct: float = Field(0.0, ge=0, le=100, description="500-2000 Hz")
    presence_pct: float = Field(0.0, ge=0, le=100, description="2-5 kHz")
    high_pct: float = Field(0.0, ge=0, le=100, description="5-10 kHz")
    air_pct: float = Field(0.0, ge=0, le=100, description="10 kHz+")
    tonal_profile: str = Field(
        "",
        description="bass-heavy / balanced / mid-heavy / bright / warm / thin",
    )


class QualityReport(BaseModel):
    """Rapport complet pour un fichier audio."""
    file_path: str
    slug: str
    artist: str | None = None
    title: str | None = None
    analyzed_at: str  # ISO date
    metadata: MetadataReport
    signal: SignalReport
    loudness: LoudnessReport
    dynamic: DynamicReport
    spectral: SpectralReport
    quality: QualityScore
    # Phase 2 : optionnel (skippe avec --quick)
    beats: BeatReport | None = None
    structure: StructureReport | None = None
    cues: CuesReport | None = None
    # Phase 6.A : optionnel
    frequency_bands: FrequencyBandsReport | None = None
    # Phase 6.D : optionnel (calcule avec Phase 2, skippe avec --quick)
    rhythm_signature: RhythmSignatureReport | None = None


# --- Phase 7.B : draft de bank Digitakt II -----------------------------------

class DigitaktTrig(BaseModel):
    """Un trig sur la grille de pas d'une track Digitakt."""
    step: int = Field(..., ge=0, description="Index de pas (0-based) dans le pattern")
    velocity: int = Field(100, ge=1, le=127)
    note: int | None = Field(None, description="Note MIDI estimee (tracks tonales)")


class DigitaktTrack(BaseModel):
    """Une des 16 tracks, role fixe par la doctrine (digitakt/doctrine.md)."""
    index: int = Field(..., ge=1, le=16)
    role: str
    source: str = Field("", description="Stem / bande d'ou vient la detection")
    active: bool = False
    level: float = Field(0.0, ge=0, le=1, description="Niveau relatif au max de la track")
    trigs: list[DigitaktTrig] = Field(default_factory=list)


class DigitaktPattern(BaseModel):
    """Un pattern = une section du morceau, repliee sur <= 128 pas."""
    slot: int = Field(..., ge=1, le=16)
    label: str
    start_s: float
    end_s: float
    bars: int = Field(..., ge=1, le=8, description="Mesures dans le pattern (1, 2, 4 ou 8)")
    steps: int = Field(..., ge=1, le=128, description="Longueur du pattern en pas")
    repeats: float = Field(..., description="Nb de tours du pattern sur la section")
    tracks: list[DigitaktTrack]


class DigitaktPhrase(BaseModel):
    """Phrase de N mesures : quelles tracks jouent (partition de mutes)."""
    start_s: float
    bar: int = Field(..., ge=0, description="Index de mesure de debut")
    pattern_slot: int
    active: list[int] = Field(default_factory=list, description="Tracks actives (1-16)")


class DigitaktBank(BaseModel):
    """Draft de bank : 1 morceau = 1 bank de <= 16 patterns."""
    slug: str
    artist: str = ""
    title: str = ""
    bpm: float
    time_signature: str = "4/4"
    steps_per_bar: int = 16
    from_stems: bool
    phrase_bars: int = 8
    patterns: list[DigitaktPattern]
    mutes: list[DigitaktPhrase] = Field(default_factory=list)
    generated_at: str
    method: str = "stem_band_fold_v1"

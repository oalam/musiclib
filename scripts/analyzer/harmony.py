"""Analyse harmonique : gamme du morceau et accords par mesure (Phase 7.H).

Gamme : le profil chroma du morceau (pondere par l'energie) est compare aux
gammes du KEYBOARD SETUP de la DT2 (annexe D du manuel, sous-ensemble arbitre :
7 modes, mineurs harmonique / melodique, pentatoniques, blues) sur les 12
fondamentales. Les modes relatifs partagent les memes notes : la fondamentale
est departagee par le poids de la note dans le profil et dans la basse.

Accords : chroma moyen de chaque mesure compare a des gabarits de triades
(majeur, mineur, sus2, sus4, diminue) et a la quinte a vide ; « N » quand la
mesure n'a pas de contenu tonal exploitable. Progression = suite des accords
distincts de chaque section.

Fonctions pures sur des profils numpy ; `analyze` fait le calcul audio.
"""
from __future__ import annotations

from datetime import date

import numpy as np
from pydantic import BaseModel

NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")

# nom DT2 (KB SCALE, annexe D) -> (libelle francais, intervalles)
SCALES: dict[str, tuple[str, tuple[int, ...]]] = {
    "IONIAN (MAJOR)": ("majeur (ionien)", (0, 2, 4, 5, 7, 9, 11)),
    "DORIAN": ("dorien", (0, 2, 3, 5, 7, 9, 10)),
    "PHRYGIAN": ("phrygien", (0, 1, 3, 5, 7, 8, 10)),
    "LYDIAN": ("lydien", (0, 2, 4, 6, 7, 9, 11)),
    "MIXOLYDIAN": ("mixolydien", (0, 2, 4, 5, 7, 9, 10)),
    "AEOLIAN (MINOR)": ("mineur (éolien)", (0, 2, 3, 5, 7, 8, 10)),
    "LOCRIAN": ("locrien", (0, 1, 3, 5, 6, 8, 10)),
    "MELODIC MINOR": ("mineur mélodique", (0, 2, 3, 5, 7, 9, 11)),
    "HARMONIC MINOR": ("mineur harmonique", (0, 2, 3, 5, 7, 8, 11)),
    "PENTATONIC MINOR": ("pentatonique mineure", (0, 3, 5, 7, 10)),
    "PENTATONIC MAJOR": ("pentatonique majeure", (0, 2, 4, 7, 9)),
    "BLUES": ("blues", (0, 3, 5, 6, 7, 10)),
}

# qualite -> (suffixe de l'accord, intervalles)
CHORDS: dict[str, tuple[str, tuple[int, ...]]] = {
    "maj": ("", (0, 4, 7)),
    "min": ("m", (0, 3, 7)),
    "sus2": ("sus2", (0, 2, 7)),
    "sus4": ("sus4", (0, 5, 7)),
    "dim": ("dim", (0, 3, 6)),
    "5": ("5", (0, 7)),
}

_TONIC_WEIGHT = 0.35    # poids de la fondamentale (profil + basse) face a l'ajustement des notes
_CHORD_MIN = 0.6        # cosinus minimal pour nommer un accord
_TONAL_MIN = 0.15       # energie chroma d'une mesure / mediane sous laquelle = « N »
_BASS_BONUS = 0.15      # bonus d'un accord dont la fondamentale est a la basse
_UNCERTAIN = 0.05       # marge sous laquelle la gamme est donnee comme incertaine
_PEAKS = 3              # notes dominantes retenues par trame (contenu tonal)


class ScaleMatch(BaseModel):
    root: int                  # 0 = C
    root_name: str
    scale: str                 # nom DT2 (KB SCALE)
    label: str                 # ex. « F mineur (éolien) »
    notes: list[str]
    score: float


class ScaleResult(ScaleMatch):
    margin: float              # ecart avec le premier candidat d'une autre gamme / fondamentale
    uncertain: bool = False    # marge faible : gamme a confirmer a l'oreille (fondamentale fiable)
    candidates: list[ScaleMatch]


class BarChord(BaseModel):
    bar: int
    start_s: float
    end_s: float
    label: str                 # ex. « Fm », « C5 », « N »
    root: int | None = None
    quality: str | None = None
    confidence: float = 0.0


class SectionProgression(BaseModel):
    label: str
    start_s: float
    end_s: float
    chords: list[str]


class Harmony(BaseModel):
    analyzed_at: str
    source: str                # "stems" | "mix"
    scale: ScaleResult
    chords: list[BarChord]
    progression: list[SectionProgression]


def _norm(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 0 else v


def _template(intervals: tuple[int, ...], root: int) -> np.ndarray:
    t = np.zeros(12)
    t[[(root + i) % 12 for i in intervals]] = 1.0
    return t


def _scale_match(root: int, name: str, score: float) -> ScaleMatch:
    label, intervals = SCALES[name]
    return ScaleMatch(root=root, root_name=NOTE_NAMES[root], scale=name,
                      label=f"{NOTE_NAMES[root]} {label}",
                      notes=[NOTE_NAMES[(root + i) % 12] for i in intervals],
                      score=round(score, 3))


def detect_scale(profile: np.ndarray, bass: np.ndarray | None = None) -> ScaleResult:
    """Meilleure gamme pour un profil chroma (12,) ; `bass` = profil du stem basse."""
    prof = np.asarray(profile, dtype=float)
    prof = prof / prof.max() if prof.max() > 0 else prof
    tonic = prof.copy()
    if bass is not None and np.max(bass) > 0:
        tonic = 0.5 * tonic + 0.5 * np.asarray(bass, dtype=float) / np.max(bass)
    scored: list[tuple[float, int, str]] = []
    for name, (_, intervals) in SCALES.items():
        for root in range(12):
            fit = float(np.corrcoef(prof, _template(intervals, root))[0, 1])
            scored.append((fit + _TONIC_WEIGHT * float(tonic[root]), root, name))
    scored.sort(key=lambda s: -s[0])
    best_score, best_root, best_name = scored[0]
    # marge : ecart avec la meilleure autre fondamentale (les gammes voisines sur la
    # meme fondamentale, ex. penta mineure / eolien, ne se contredisent pas : alternatives)
    runner = next(s for s in scored[1:] if s[1] != best_root)
    best = _scale_match(best_root, best_name, best_score)
    margin = round(best_score - runner[0], 3)
    return ScaleResult(**best.model_dump(), margin=margin, uncertain=margin < _UNCERTAIN,
                       candidates=[_scale_match(r, n, s) for s, r, n in scored[1:5]])


def detect_chord(chroma: np.ndarray, bass: np.ndarray | None = None) -> tuple[str, int | None, str | None, float]:
    """Accord d'un chroma (12,) : (libelle, fondamentale, qualite, confiance)."""
    x = _norm(np.asarray(chroma, dtype=float))
    if not np.any(x):
        return "N", None, None, 0.0
    b = None
    if bass is not None and np.max(bass) > 0:
        b = np.asarray(bass, dtype=float) / np.max(bass)
    best: tuple[float, float, int, str] = (-1.0, 0.0, 0, "maj")
    for quality, (_, intervals) in CHORDS.items():
        for root in range(12):
            cos = float(x @ _norm(_template(intervals, root)))
            score = cos + (_BASS_BONUS * float(b[root]) if b is not None else 0.0)
            if score > best[0]:
                best = (score, cos, root, quality)
    _, cos, root, quality = best
    if cos < _CHORD_MIN:
        return "N", None, None, round(cos, 3)
    return f"{NOTE_NAMES[root]}{CHORDS[quality][0]}", root, quality, round(cos, 3)


def bar_chords(chroma: np.ndarray, times: np.ndarray, bar_times: list[float],
               bass_chroma: np.ndarray | None = None) -> list[BarChord]:
    """Un accord par mesure ; chroma (12, n_frames) non normalise, `times` (n_frames,)."""
    energies: list[float] = []
    means: list[tuple[np.ndarray, np.ndarray | None]] = []
    for b0, b1 in zip(bar_times[:-1], bar_times[1:]):
        sel = (times >= b0) & (times < b1)
        m = chroma[:, sel].mean(axis=1) if sel.any() else np.zeros(12)
        bm = bass_chroma[:, sel].mean(axis=1) if bass_chroma is not None and sel.any() else None
        energies.append(float(m.sum()))
        means.append((m, bm))
    ref = float(np.median([e for e in energies if e > 0])) if any(e > 0 for e in energies) else 0.0
    out: list[BarChord] = []
    for i, ((m, bm), e) in enumerate(zip(means, energies)):
        b0, b1 = bar_times[i], bar_times[i + 1]
        if ref <= 0 or e < _TONAL_MIN * ref:
            out.append(BarChord(bar=i, start_s=round(b0, 3), end_s=round(b1, 3), label="N"))
            continue
        label, root, quality, conf = detect_chord(m, bm)
        out.append(BarChord(bar=i, start_s=round(b0, 3), end_s=round(b1, 3), label=label,
                            root=root, quality=quality, confidence=conf))
    return out


def progression(chords: list[BarChord], sections: list[tuple[str, float, float]],
                max_chords: int = 8) -> list[SectionProgression]:
    """Suite des accords distincts (consecutifs dedoublonnes, « N » ignore) par section."""
    out: list[SectionProgression] = []
    for label, s0, s1 in sections:
        seq: list[str] = []
        for c in chords:
            mid = (c.start_s + c.end_s) / 2
            if s0 <= mid < s1 and c.label != "N" and (not seq or seq[-1] != c.label):
                seq.append(c.label)
        out.append(SectionProgression(label=label, start_s=round(s0, 3), end_s=round(s1, 3),
                                      chords=seq[:max_chords]))
    return out


def peak_profile(chroma: np.ndarray, k: int = _PEAKS) -> np.ndarray:
    """Profil (12,) : les `k` notes dominantes de chaque trame, ponderees par son energie.

    Plus robuste qu'une moyenne sur un contenu bruite (FX, synthes satures) dont le
    chroma moyen est presque plat ; k = 1 sur la basse donne sa note tenue."""
    if not chroma.size:
        return np.zeros(12)
    energy = chroma.sum(axis=0)
    top = np.argsort(chroma, axis=0)[-k:]
    hist = np.zeros(12)
    for j in range(chroma.shape[1]):
        hist[top[:, j]] += energy[j]
    return hist / hist.max() if hist.max() > 0 else hist


def analyze(tonal: np.ndarray, sr: int, bar_times: list[float],
            sections: list[tuple[str, float, float]], source: str,
            bass: np.ndarray | None = None) -> Harmony:
    """Calcul audio : `tonal` = stem other (ou mix), `bass` = stem basse si disponible."""
    import librosa  # import local : seul le calcul audio en a besoin

    hop = 2048
    target = 22050
    if sr != target:
        tonal = librosa.resample(tonal, orig_sr=sr, target_sr=target)
        bass = librosa.resample(bass, orig_sr=sr, target_sr=target) if bass is not None else None
        sr = target
    # composante harmonique : retire batterie residuelle, bruit et attaques des FX
    tonal = librosa.effects.harmonic(tonal, margin=3)
    chroma = librosa.feature.chroma_cqt(y=tonal, sr=sr, hop_length=hop, norm=None)
    bass_chroma = None
    if bass is not None:
        bass_chroma = librosa.feature.chroma_cqt(y=bass, sr=sr, hop_length=hop, norm=None,
                                                 fmin=librosa.note_to_hz("C1"), n_octaves=4)
        n = min(chroma.shape[1], bass_chroma.shape[1])
        chroma, bass_chroma = chroma[:, :n], bass_chroma[:, :n]
    bass_profile = peak_profile(bass_chroma, 1) if bass_chroma is not None else None
    # la basse porte aussi la tonalite : profil global = notes dominantes + basse
    profile = peak_profile(chroma) + (bass_profile if bass_profile is not None else 0)
    times = librosa.frames_to_time(np.arange(chroma.shape[1]), sr=sr, hop_length=hop)
    scale = detect_scale(profile, bass_profile)
    chords = bar_chords(chroma + (bass_chroma if bass_chroma is not None else 0), times,
                        bar_times, bass_chroma)
    return Harmony(analyzed_at=date.today().isoformat(), source=source, scale=scale,
                   chords=chords, progression=progression(chords, sections))


def keyboard_setup(scale: ScaleMatch) -> str:
    """Reglage a faire sur la DT2 : [FUNC] + [KEYBOARD] > KB SCALE / ROOT NOTE (§8.5.2)."""
    return f"KB SCALE = {scale.scale}, ROOT NOTE = {scale.root_name}"

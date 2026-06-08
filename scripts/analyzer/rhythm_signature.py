"""Empreinte de groove tempo-invariante (Phase 6.D).

Idee : decrire la *forme* du pattern rythmique, repliee sur une mesure de
16 pas, independamment du tempo. Deux tracks a 180 BPM peuvent etre un tribe
roulant en croches syncopees ou un acid four-on-floor martele — meme BPM,
meme key, meme energy, mais groove radicalement different. Ce module capture
precisement cet axe, que Camelot + BPM + energy n'encodent pas.

Pipeline :
1. Une mel-spectrogram, decoupee en 3 bandes (sub / mid / high).
2. Onset strength (flux spectral positif) par bande.
3. Repliage des enveloppes sur une grille de 16 pas/mesure, via les
   `beat_times` du beat tracking → 3 patterns normalises + un pattern global.
4. Scalaires derives : syncope (energie hors-temps), pulse clarity
   (regularite), swing (microtiming des contretemps).

Similarite :
- `rhythm_distance(a, b)` ∈ [0, 1] : patterns compares par cross-correlation
  sur les 16 rotations (invariance a la phase du downbeat, jamais detecte
  pareil d'une track a l'autre) ; scalaires par difference absolue.
- `cluster(sigs, k)` : clustering agglomeratif sur la matrice de distances.

Volontairement SANS BPM / key / energy : on reste orthogonal a
`compatibility.py` (cf. SPEC « Decisions arbitrees »).
"""
from __future__ import annotations

import numpy as np

from .audio_loader import to_mono
from .types import RhythmSignatureReport

_HOP = 512
_STEPS = 16

# (lo_hz, hi_hz) par bande rythmique
_BANDS: dict[str, tuple[float, float]] = {
    "sub": (20.0, 200.0),       # kick / sub-bass
    "mid": (200.0, 2000.0),     # snare / clap / corps
    "high": (2000.0, float("inf")),  # hats / texture
}

# Poids des composantes pour rhythm_distance (somme = 1.0)
_W_BAR = 0.25
_W_SUB = 0.20
_W_MID = 0.15
_W_HIGH = 0.10
_W_SYNC = 0.15
_W_PULSE = 0.10
_W_SWING = 0.05


def beats_per_bar(time_signature: str) -> int:
    """Public : numerateur de la signature → beats par mesure (defaut 4)."""
    return _beats_per_bar(time_signature)


def _beats_per_bar(time_signature: str) -> int:
    """Numerateur de la signature → beats par mesure. Defaut 4."""
    try:
        num = int(time_signature.split("/")[0])
        return num if num > 0 else 4
    except (ValueError, AttributeError, IndexError):
        return 4


def band_envelopes(
    mono: np.ndarray, sample_rate: int
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Public : onset strength (sub/mid/high) + temps des frames. Reutilise
    par groove.py pour la transcription. Hop = `_HOP`."""
    return _band_envelopes(mono, sample_rate)


def _band_envelopes(
    mono: np.ndarray, sample_rate: int
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Onset strength par bande + temps des frames.

    Une seule mel-spectrogram calculee, puis onset_strength sur les lignes
    mel de chaque bande (flux spectral positif). Retourne (envelopes, times)."""
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import librosa

        melspec = librosa.feature.melspectrogram(
            y=mono, sr=sample_rate, hop_length=_HOP
        )
        mel_db = librosa.power_to_db(melspec, ref=np.max)
        mel_f = librosa.mel_frequencies(n_mels=melspec.shape[0], fmax=sample_rate / 2)

        envelopes: dict[str, np.ndarray] = {}
        n_frames = 0
        for name, (lo, hi) in _BANDS.items():
            rows = np.where((mel_f >= lo) & (mel_f < hi))[0]
            if len(rows) == 0:
                envelopes[name] = np.zeros(0)
                continue
            env = librosa.onset.onset_strength(S=mel_db[rows], sr=sample_rate)
            envelopes[name] = env
            n_frames = max(n_frames, len(env))

        times = librosa.frames_to_time(
            np.arange(n_frames), sr=sample_rate, hop_length=_HOP
        )
    return envelopes, times


def _fold_pattern(
    env: np.ndarray,
    frame_times: np.ndarray,
    bar_starts: np.ndarray,
    steps: int,
) -> tuple[np.ndarray, int]:
    """Replie une enveloppe sur une grille de `steps` pas, moyennee sur les
    mesures. Retourne (pattern non normalise, nb de mesures utilisees)."""
    pattern = np.zeros(steps)
    bars_used = 0
    if env.size == 0 or len(bar_starts) < 2:
        return pattern, 0
    n = min(len(env), len(frame_times))
    env = env[:n]
    frame_times = frame_times[:n]
    for bi in range(len(bar_starts) - 1):
        t0 = float(bar_starts[bi])
        t1 = float(bar_starts[bi + 1])
        if t1 <= t0:
            continue
        mask = (frame_times >= t0) & (frame_times < t1)
        if not mask.any():
            continue
        rel = (frame_times[mask] - t0) / (t1 - t0)
        idx = np.clip((rel * steps).astype(int), 0, steps - 1)
        np.add.at(pattern, idx, env[mask])
        bars_used += 1
    return pattern, bars_used


def _stretch(pattern: np.ndarray) -> np.ndarray:
    """Etire un pattern en [0, 1] par min-max (revele le relief des hits).

    Le plancher continu de l'onset strength est ainsi retire : un kick
    four-on-floor ressort net, un break syncope montre ses contretemps."""
    if pattern.size == 0:
        return pattern
    lo = float(pattern.min())
    hi = float(pattern.max())
    if hi - lo <= 0:
        return np.zeros_like(pattern)
    return (pattern - lo) / (hi - lo)


def _normalize(pattern: np.ndarray) -> list[float]:
    """Pattern etire min-max → liste de floats arrondis."""
    return [round(float(v), 4) for v in _stretch(pattern)]


def _beat_step_indices(steps: int, beats_per_bar: int) -> list[int]:
    """Indices des pas tombant sur les temps (downbeats inclus)."""
    spb = steps / beats_per_bar
    return sorted({int(round(b * spb)) % steps for b in range(beats_per_bar)})


def _syncopation(bar_pattern: np.ndarray, steps: int, beats_per_bar: int) -> float:
    """Part d'energie hors-temps, ponderee par distance metrique au temps.

    Calculee sur le pattern etire (plancher retire) pour rester discriminante.
    Temps fort = poids 0, croche hors-temps = 0.5, double-croche = 1.0."""
    bar_pattern = _stretch(bar_pattern)
    total = float(bar_pattern.sum())
    if total <= 0:
        return 0.0
    beat_steps = set(_beat_step_indices(steps, beats_per_bar))
    spb = steps / beats_per_bar
    weights = np.zeros(steps)
    for s in range(steps):
        if s in beat_steps:
            weights[s] = 0.0
        elif spb >= 2 and abs((s % spb) - spb / 2) < 0.5:  # croche (mi-temps)
            weights[s] = 0.5
        else:
            weights[s] = 1.0
    return float(np.clip((weights * bar_pattern).sum() / total, 0.0, 1.0))


def _pulse_clarity(oenv: np.ndarray) -> float:
    """Nettete du pulse via autocorrelation de l'onset envelope globale."""
    if oenv.size < 8:
        return 0.0
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import librosa

        ac = librosa.autocorrelate(oenv - oenv.mean())
    if ac.size < 3 or ac[0] <= 0:
        return 0.0
    ac = ac[1:]  # on ignore le lag 0
    peak = float(ac.max())
    mean = float(np.abs(ac).mean())
    if peak <= 0:
        return 0.0
    return float(np.clip((peak - mean) / (peak + 1e-9), 0.0, 1.0))


def _swing(bar_pattern: np.ndarray, steps: int, beats_per_bar: int) -> float:
    """Microtiming des contretemps : ratio energie 'a' vs 'e' de chaque temps.

    0.5 = droit, >0.5 = contretemps pousses tard (shuffle). Defini seulement
    quand 4 pas/temps (sinon 0.5 neutre)."""
    if steps % beats_per_bar != 0:
        return 0.5
    spb = steps // beats_per_bar
    if spb != 4:
        return 0.5
    bar_pattern = _stretch(bar_pattern)
    e_energy = 0.0  # le 'e' (1er 16e apres le temps)
    a_energy = 0.0  # le 'a' (3e 16e, dernier avant temps suivant)
    for b in range(beats_per_bar):
        base = b * spb
        e_energy += float(bar_pattern[base + 1])
        a_energy += float(bar_pattern[base + 3])
    denom = e_energy + a_energy
    if denom <= 0:
        return 0.5
    return float(np.clip(a_energy / denom, 0.0, 1.0))


# Seuil de confiance au-dela duquel on prend une signature impaire au serieux
# pour la grille de repliage. En dessous, on replie en 4/4 (prior fort du
# corpus tribe/acid/dubstep, et detection signature peu fiable a bas conf).
_SIG_CONF_THRESHOLD = 0.5


def analyze(
    data: np.ndarray,
    sample_rate: int,
    beat_times: list[float],
    time_signature: str = "4/4",
    time_signature_confidence: float = 0.5,
    steps: int = _STEPS,
) -> RhythmSignatureReport:
    """Calcule la signature rythmique a partir du signal + des beats detectes.

    `beat_times` vient de `BeatReport.beat_times_s`. Sans assez de beats
    (< 2 mesures), retourne un rapport vide (bars_used=0).

    La grille de repliage utilise 4 temps/mesure par defaut ; une signature
    impaire n'est prise pour la grille que si sa confiance depasse le seuil
    (sinon un mauvais 3/4 desaligne les mesures et lisse le pattern)."""
    bpb = _beats_per_bar(time_signature)
    if bpb != 4 and time_signature_confidence < _SIG_CONF_THRESHOLD:
        bpb = 4
    report = RhythmSignatureReport(steps=steps, beats_per_bar=bpb)

    beats = np.asarray([t for t in beat_times if t >= 0], dtype=float)
    if beats.size < 2 * bpb:
        return report  # pas assez de mesures pour replier proprement

    mono = to_mono(data)
    if mono.size < sample_rate:  # < 1 s
        return report

    envelopes, frame_times = _band_envelopes(mono, sample_rate)
    bar_starts = beats[::bpb]  # debut de chaque mesure

    folded: dict[str, np.ndarray] = {}
    bars_used = 0
    for name in _BANDS:
        pat, used = _fold_pattern(envelopes.get(name, np.zeros(0)),
                                  frame_times, bar_starts, steps)
        folded[name] = pat
        bars_used = max(bars_used, used)

    bar_raw = folded["sub"] + folded["mid"] + folded["high"]

    # Onset envelope globale (somme des bandes) pour le pulse clarity
    max_len = max((e.size for e in envelopes.values()), default=0)
    oenv = np.zeros(max_len)
    for e in envelopes.values():
        if e.size:
            oenv[: e.size] += e

    report.bars_used = bars_used
    report.bar_pattern = _normalize(bar_raw)
    report.sub_pattern = _normalize(folded["sub"])
    report.mid_pattern = _normalize(folded["mid"])
    report.high_pattern = _normalize(folded["high"])
    report.syncopation = round(_syncopation(bar_raw, steps, bpb), 3)
    report.pulse_clarity = round(_pulse_clarity(oenv), 3)
    report.swing = round(_swing(bar_raw, steps, bpb), 3)
    return report


# ---------------------------------------------------------------------------
# Similarite
# ---------------------------------------------------------------------------

def _circular_similarity(a: list[float], b: list[float]) -> float:
    """Correlation de Pearson max sur toutes les rotations ∈ [0, 1].

    Centree (moyenne retiree) pour ignorer le niveau continu et ne comparer
    que la *forme* ; invariante a la phase du downbeat (decalage circulaire).
    Deux patterns plats (variance nulle, ex. bande sans contenu rythmique) =
    meme absence de forme → 1.0 ; un plat + un avec relief → 0.0."""
    va = np.asarray(a, dtype=float)
    vb = np.asarray(b, dtype=float)
    if va.size == 0 or vb.size == 0 or va.size != vb.size:
        return 0.0
    va = va - va.mean()
    vb = vb - vb.mean()
    na = np.linalg.norm(va)
    nb = np.linalg.norm(vb)
    if na <= 0 and nb <= 0:
        return 1.0  # deux bandes vides : meme absence de pattern
    if na <= 0 or nb <= 0:
        return 0.0  # une seule a du relief : dissemblables
    va = va / na
    vb = vb / nb
    best = max(float(np.dot(va, np.roll(vb, r))) for r in range(va.size))
    return float(np.clip(best, 0.0, 1.0))


def rhythm_distance(a: RhythmSignatureReport, b: RhythmSignatureReport) -> float:
    """Distance de groove ∈ [0, 1]. 0 = identique, 1 = totalement different."""
    d_bar = 1.0 - _circular_similarity(a.bar_pattern, b.bar_pattern)
    d_sub = 1.0 - _circular_similarity(a.sub_pattern, b.sub_pattern)
    d_mid = 1.0 - _circular_similarity(a.mid_pattern, b.mid_pattern)
    d_high = 1.0 - _circular_similarity(a.high_pattern, b.high_pattern)
    d_sync = abs(a.syncopation - b.syncopation)
    d_pulse = abs(a.pulse_clarity - b.pulse_clarity)
    d_swing = abs(a.swing - b.swing)
    dist = (
        _W_BAR * d_bar
        + _W_SUB * d_sub
        + _W_MID * d_mid
        + _W_HIGH * d_high
        + _W_SYNC * d_sync
        + _W_PULSE * d_pulse
        + _W_SWING * d_swing
    )
    return float(np.clip(dist, 0.0, 1.0))


def to_vector(sig: RhythmSignatureReport) -> np.ndarray:
    """Vecteur phase-canonique (pour clustering euclidien si besoin).

    Toutes les bandes sont rotees du meme decalage (argmax du pattern global),
    ce qui canonicalise le downbeat tout en preservant la relation inter-bandes
    (kick vs hat)."""
    bar = np.asarray(sig.bar_pattern, dtype=float)
    if bar.size == 0:
        return np.zeros(3 * sig.steps + 3)
    shift = int(np.argmax(bar))
    parts = [
        np.roll(np.asarray(sig.sub_pattern, dtype=float), -shift),
        np.roll(np.asarray(sig.mid_pattern, dtype=float), -shift),
        np.roll(np.asarray(sig.high_pattern, dtype=float), -shift),
        np.array([sig.syncopation, sig.pulse_clarity, sig.swing]),
    ]
    return np.concatenate(parts)


def cluster(
    sigs: list[tuple[str, RhythmSignatureReport]],
    k: int,
) -> dict[str, int]:
    """Clustering agglomeratif (matrice de distances precalculee).

    Retourne {slug: label}. Utilise `rhythm_distance` comme metrique, cohérent
    avec le voisinage. `k` est borne au nombre de tracks."""
    from sklearn.cluster import AgglomerativeClustering

    n = len(sigs)
    if n == 0:
        return {}
    k = max(1, min(k, n))
    if n <= k:
        return {slug: i for i, (slug, _) in enumerate(sigs)}

    dmat = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = rhythm_distance(sigs[i][1], sigs[j][1])
            dmat[i, j] = dmat[j, i] = d

    model = AgglomerativeClustering(
        n_clusters=k, metric="precomputed", linkage="average"
    )
    labels = model.fit_predict(dmat)
    return {sigs[i][0]: int(labels[i]) for i in range(n)}


# ---------------------------------------------------------------------------
# Rendu
# ---------------------------------------------------------------------------

_SPARK = "▁▂▃▄▅▆▇█"


def to_sparkline(pattern: list[float]) -> str:
    """Pattern normalise → barres ASCII (un caractere par pas)."""
    if not pattern:
        return ""
    chars = []
    for v in pattern:
        idx = int(round(float(np.clip(v, 0.0, 1.0)) * (len(_SPARK) - 1)))
        chars.append(_SPARK[idx])
    return "".join(chars)

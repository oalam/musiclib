"""Beat tracking robuste : 3 detecteurs independants + consensus.

Detecteurs :
1. `librosa.beat.beat_track` : dynamic programming sur onset envelope
2. `librosa.feature.tempo` : autocorrelation du tempogramme
3. IOI comb-filter (custom) : detection des onsets en pics discrets, puis
   scoring d'un comb-filter sur la distribution des intervalles
   inter-onsets (harmoniques k=1..4). Algo structurellement different
   des deux precedents : il ne regarde pas l'onset envelope continu mais
   les pics d'attaque eux-memes.

Consensus :
- Clustering des candidats par tolerance ±5% en tempo, en acceptant aussi
  les relations harmoniques (x2 ou /2 = meme cluster harmonique).
- Vote majoritaire entre les 3 detecteurs.
- Confiance = (votes du cluster gagnant) / (nb detecteurs valides), bornee
  par la coherence intra-cluster.

Override : si `override_bpm` est fourni (typiquement library.md corrige a
la main), il est utilise comme tempo primaire MAIS les 3 detecteurs sont
quand meme lances et leurs resultats listes en candidats — tu peux ainsi
voir si la valeur manuelle est en accord ou en desaccord avec les algos.
"""
from __future__ import annotations

import numpy as np

from .audio_loader import to_mono
from .types import BeatReport

_CLUSTER_TOL = 0.05  # 5% relatif

# Signatures rythmiques candidates pour autocorrelation
_METER_CANDIDATES: dict[str, int] = {
    "4/4": 4, "3/4": 3, "6/8": 6,
    "5/4": 5, "7/8": 7, "17/8": 17,
}


def _close(a: float, b: float, tol: float = _CLUSTER_TOL) -> bool:
    if a <= 0 or b <= 0:
        return False
    return abs(a - b) / max(a, b) < tol


def _enrich_rhythm(
    mono: np.ndarray,
    sample_rate: int,
    beat_times: np.ndarray,
) -> tuple[float, float, str, float]:
    """Calcule onset_density, beat_strength, time_signature.

    Retourne (onset_density_per_s, beat_strength, signature, signature_confidence)."""
    import librosa
    duration = len(mono) / sample_rate
    if duration <= 0:
        return 0.0, 0.0, "4/4", 0.5

    # Onset envelope (continue) + onset detection (pics discrets)
    onset_env = librosa.onset.onset_strength(y=mono, sr=sample_rate)
    onsets_s = librosa.onset.onset_detect(y=mono, sr=sample_rate, units="time")
    onset_density = float(len(onsets_s)) / duration

    # Beat strength : amplitude de l'onset envelope aux positions de beats
    if len(beat_times) > 0 and len(onset_env) > 0:
        beat_frames = librosa.time_to_frames(beat_times, sr=sample_rate)
        beat_frames = beat_frames[beat_frames < len(onset_env)]
        if len(beat_frames) > 0:
            beat_strengths = onset_env[beat_frames]
            beat_strength = float(np.mean(beat_strengths))
        else:
            beat_strength = 0.0
            beat_strengths = np.array([])
    else:
        beat_strength = 0.0
        beat_strengths = np.array([])

    # Time signature via autocorrelation des beat strengths + floor 4/4
    signature, sig_conf = "4/4", 0.5
    if len(beat_strengths) >= 24:
        x = beat_strengths - np.mean(beat_strengths)
        if np.std(x) > 0:
            autocorr = np.correlate(x, x, mode="full")
            mid = len(autocorr) // 2
            base = autocorr[mid]
            scores: dict[str, float] = {}
            for sig, k in _METER_CANDIDATES.items():
                if mid + k < len(autocorr) and base > 0:
                    scores[sig] = float(autocorr[mid + k] / base)
            if scores:
                scores["4/4"] = scores.get("4/4", 0.0) * 1.3 + 0.05
                signature = max(scores, key=lambda s: scores[s])
                raw = scores[signature]
                sig_conf = float(np.clip(raw, 0.0, 1.0))
                # Floor : si signal trop faible, on retombe sur 4/4 par defaut
                if sig_conf < 0.15 and signature != "4/4":
                    signature = "4/4"
                    sig_conf = 0.3

    return (
        round(onset_density, 2),
        round(beat_strength, 3),
        signature,
        round(sig_conf, 2),
    )


def _ioi_comb_tempo(mono: np.ndarray, sample_rate: int) -> tuple[float, float]:
    """3e detecteur : comb-filter sur intervalles inter-onsets.

    Retourne (bpm, confidence). 0.0/0.0 si insuffisant."""
    import librosa
    onsets_s = librosa.onset.onset_detect(y=mono, sr=sample_rate, units="time")
    if len(onsets_s) < 10:
        return 0.0, 0.0
    iois = np.diff(onsets_s)
    iois = iois[(iois > 0.05) & (iois < 2.0)]  # 30 a 1200 BPM en theorie
    if len(iois) < 5:
        return 0.0, 0.0

    # Pour chaque BPM candidat, score = somme ponderee des IOIs matchant
    # k * period pour k=1..4 (le tempo vrai a des harmoniques entieres)
    bpm_range = np.arange(60.0, 220.0, 0.5)
    tol = 0.06
    scores = np.zeros_like(bpm_range)
    for i, bpm in enumerate(bpm_range):
        period = 60.0 / bpm
        for k in (1, 2, 3, 4):
            target = k * period
            matches = np.abs(iois - target) / target < tol
            scores[i] += matches.sum() * (1.0 / k)  # downweight harmoniques superieures

    if scores.max() == 0:
        return 0.0, 0.0
    best_idx = int(np.argmax(scores))
    best_bpm = float(bpm_range[best_idx])
    confidence = float(scores[best_idx] / len(iois))
    return best_bpm, min(1.0, confidence)


def _half_normalize(bpm: float) -> float:
    """Ramene un tempo dans la fenetre 'naturelle' 80-180 si possible.

    Utilise pour le clustering harmonique : on considere que 99 et 198
    sont equivalents pour decider du cluster."""
    while bpm < 80 and bpm > 0:
        bpm *= 2
    while bpm > 180:
        bpm /= 2
    return bpm


def _cluster_consensus(
    detections: list[tuple[str, float]],
) -> tuple[float, float, list[float], list[tuple[str, float]]]:
    """Vote majoritaire entre detecteurs, avec equivalence harmonique.

    Retourne (bpm_gagnant, confidence, all_distinct_bpms, breakdown)."""
    valid = [(name, b) for name, b in detections if b > 0]
    if not valid:
        return 0.0, 0.0, [], []

    # Cluster par equivalence harmonique : on compare les versions normalisees
    clusters: list[dict] = []  # {key: float, members: list[(name, bpm)]}
    for name, bpm in valid:
        norm = _half_normalize(bpm)
        matched = False
        for cl in clusters:
            if _close(norm, cl["key"]):
                cl["members"].append((name, bpm))
                # mise a jour cle (moyenne des normalises)
                cl["key"] = float(np.mean([_half_normalize(b) for _, b in cl["members"]]))
                matched = True
                break
        if not matched:
            clusters.append({"key": norm, "members": [(name, bpm)]})

    # Le cluster gagnant = le plus vote ; en cas d'egalite, celui dont la
    # cle est dans la zone naturelle 80-180
    def rank(cl: dict) -> tuple[int, int, float]:
        nat = 1 if 80 <= cl["key"] <= 180 else 0
        return (len(cl["members"]), nat, -abs(cl["key"] - 130))

    clusters.sort(key=rank, reverse=True)
    winner = clusters[0]

    # Au sein du cluster, choisir la valeur la plus representee (ou la
    # mediane si toutes uniques). On prefere la valeur en zone naturelle.
    members_bpms = [b for _, b in winner["members"]]
    in_natural = [b for b in members_bpms if 80 <= b <= 180]
    if in_natural:
        chosen = float(np.median(in_natural))
    else:
        chosen = float(np.median(members_bpms))

    confidence = len(winner["members"]) / len(valid)
    all_distinct = sorted({round(b, 1) for _, b in valid})
    return round(chosen, 1), round(confidence, 2), all_distinct, winner["members"]


def analyze(
    data: np.ndarray,
    sample_rate: int,
    start_bpm: float = 140.0,
    override_bpm: float | None = None,
) -> BeatReport:
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import librosa

        mono = to_mono(data)

        # --- 3 detecteurs independants ---
        try:
            t_bt, beats_frames = librosa.beat.beat_track(
                y=mono, sr=sample_rate, start_bpm=start_bpm,
            )
            tempo_bt = float(np.atleast_1d(t_bt)[0])
        except Exception:
            tempo_bt, beats_frames = 0.0, np.array([])

        try:
            t_ft = librosa.feature.tempo(y=mono, sr=sample_rate, aggregate=np.median)
            tempo_ft = float(np.atleast_1d(t_ft)[0])
        except Exception:
            tempo_ft = 0.0

        tempo_ioi, conf_ioi = _ioi_comb_tempo(mono, sample_rate)

        beat_times = librosa.frames_to_time(beats_frames, sr=sample_rate)

    # Demi-temps : si beat_track < 90, on rapelle qu'il est probablement halftime
    half_corrected = False
    tempo_bt_corrected = tempo_bt
    if 0 < tempo_bt < 90.0:
        tempo_bt_corrected = tempo_bt * 2.0
        half_corrected = True

    # Vote consensus
    detections = [
        ("beat_track", tempo_bt_corrected),
        ("librosa.tempo", tempo_ft),
        ("ioi_comb", tempo_ioi),
    ]
    consensus_bpm, consensus_conf, all_distinct, _ = _cluster_consensus(detections)

    # Override : tempo manuel prime, mais on garde les candidats auto
    if override_bpm and override_bpm > 0:
        period = 60.0 / float(override_bpm)
        import warnings as _w
        with _w.catch_warnings():
            _w.simplefilter("ignore")
            import librosa as _lr
            onset_env = _lr.onset.onset_strength(y=mono, sr=sample_rate)
            window = min(int(_lr.time_to_frames(5.0, sr=sample_rate)), len(onset_env))
            first_idx = int(np.argmax(onset_env[:window])) if window > 0 else 0
            phase_s = float(_lr.frames_to_time(first_idx, sr=sample_rate)) % period
        duration = len(mono) / sample_rate
        beat_times = np.arange(phase_s, duration, period)

        # Confiance dans l'override = accord avec consensus auto
        if consensus_bpm > 0 and _close(_half_normalize(override_bpm),
                                        _half_normalize(consensus_bpm)):
            override_conf = 1.0
        elif consensus_bpm > 0:
            override_conf = 0.7
        else:
            override_conf = 0.85

        density, strength, sig, sig_conf = _enrich_rhythm(mono, sample_rate, beat_times)
        return BeatReport(
            tempo_bpm=round(float(override_bpm), 1),
            beat_count=len(beat_times),
            beat_times_s=[round(float(t), 3) for t in beat_times],
            half_time_corrected=False,
            manual_override=True,
            confidence=round(override_conf, 2),
            candidates_bpm=all_distinct,
            onset_density_per_s=density,
            beat_strength=strength,
            time_signature=sig,
            time_signature_confidence=sig_conf,
        )

    density, strength, sig, sig_conf = _enrich_rhythm(mono, sample_rate, beat_times)
    return BeatReport(
        tempo_bpm=consensus_bpm if consensus_bpm > 0 else round(tempo_bt_corrected, 1),
        beat_count=len(beat_times),
        beat_times_s=[round(float(t), 3) for t in beat_times],
        half_time_corrected=half_corrected,
        manual_override=False,
        confidence=consensus_conf,
        candidates_bpm=all_distinct,
        onset_density_per_s=density,
        beat_strength=strength,
        time_signature=sig,
        time_signature_confidence=sig_conf,
    )

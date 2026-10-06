"""Draft de bank Digitakt II depuis un morceau de reference (Phase 7.B).

1 morceau = 1 bank. Chaque section de la structure devient un pattern
(<= 16 patterns, <= 128 pas = 8 mesures), reparti sur la grille fixe des
16 tracks de la doctrine (`digitakt/doctrine.md`) :

    1 kick / 2 rumble / 3 clap / 4 hat ferme / 5 hat ouvert / 6 ride /
    7-8 percs / 9 basse / 10 lead / 11 atmo / 12-13 Id1-Id2 / 14 vocal /
    15 FX / 16 reserve

Pipeline :
1. Une STFT par stem Demucs (drums / bass / other / vocals), fallback mix.
2. Pour chaque track : enveloppes onset + energie dans sa bande, agregees
   par pas de double-croche sur la grille issue des `beat_times`.
3. Calage sur le kick (phase dans le temps), puis premier temps de la
   mesure (changements d'activite des tracks + clap sur 2 et 4).
4. Structure deduite des tracks : decoupe sur une grille de 4 mesures la ou
   l'ensemble des tracks actives change, labels deduits du contenu.
5. Pour chaque section : repliage des pas actifs sur la longueur du pattern,
   seuillage en trigs (notes estimees par chroma pour basse / lead). Deux
   sections au contenu proche partagent le meme slot (ordre de jeu = chaine).
6. Partition de mutes : activite de chaque track par phrase de N mesures.

Ce n'est PAS une transcription : c'est un point de depart pour bootstraper une
bank. Id1 / Id2 (12-13) restent vides, c'est a l'oreille de les choisir.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from .types import (
    DigitaktBank,
    DigitaktPattern,
    DigitaktPhrase,
    DigitaktSection,
    DigitaktTrack,
    DigitaktTrig,
)

_N_FFT = 2048
_HOP = 512
_MAX_STEPS = 128
_MAX_PATTERNS = 16
_SILENT_STEM_DBFS = -45.0   # stem quasi muet (ex. vocals d'un instrumental)
_ACTIVE_DB = -12.0          # actif si energie de phrase > max de la track - 12 dB
_LOW_CONTRAST = 0.3         # relief (max - mediane) / max sous lequel = son tenu
_SECTION_GRID = 4           # structure decoupee sur une grille de 4 mesures
_CLAP_WEIGHT = 0.5          # poids du clap sur 2 et 4 dans le choix du premier temps
_CHANGE_MIN = 0.25          # saut d'activite minimal (0-1) compte comme changement
_REUSE_SIM = 0.3            # similarite de grille (trigs bruites) pour reutiliser un slot


@dataclass(frozen=True)
class TrackSpec:
    """Role fixe d'une track et comment le detecter."""
    index: int
    role: str
    stem: str | None            # drums / bass / other / vocals / None
    lo: float = 0.0
    hi: float = 0.0
    kind: str = "hit"           # hit / tonal / rumble / sustain / fx / none
    base_note: int = 60         # note MIDI de base (60 = pitch d'origine du sample)
    exclude: tuple[int, ...] = ()  # tracks dont les pas sont exclus


TRACKS: tuple[TrackSpec, ...] = (
    TrackSpec(1, "Kick", "drums", 30, 120),
    TrackSpec(2, "Rumble", "drums", 30, 90, kind="rumble", exclude=(1,)),
    TrackSpec(3, "Clap / snare", "drums", 300, 3000, exclude=(1,)),
    TrackSpec(4, "Hat ferme", "drums", 7000, 16000),
    TrackSpec(5, "Hat ouvert", "drums", 5000, 12000),
    TrackSpec(6, "Ride", "drums", 3000, 6000),
    TrackSpec(7, "Perc A", "drums", 120, 400, exclude=(1, 3)),
    TrackSpec(8, "Perc B", "drums", 400, 1500, exclude=(3,)),
    TrackSpec(9, "Basse", "bass", 40, 400, kind="tonal", base_note=36),
    TrackSpec(10, "Lead", "other", 300, 4000, kind="tonal", base_note=60),
    TrackSpec(11, "Atmo", "other", 100, 8000, kind="sustain"),
    TrackSpec(12, "Id1", None, kind="none"),
    TrackSpec(13, "Id2", None, kind="none"),
    TrackSpec(14, "Vocal", "vocals", 200, 5000),
    TrackSpec(15, "FX", None, kind="fx"),
    TrackSpec(16, "Reserve", None, kind="none"),
)
_HAT_FAMILY = (4, 5, 6)


@dataclass
class StepFeatures:
    """Features agregees par pas de grille, pour toutes les tracks."""
    step_times: np.ndarray                 # debut de chaque pas (s), n_steps + 1 bornes
    onset: dict[int, np.ndarray]           # track -> (n_steps,)
    energy: dict[int, np.ndarray]          # track -> (n_steps,)
    chroma: dict[int, np.ndarray]          # track tonale -> (n_steps, 12)


# --- grille ------------------------------------------------------------------

def retrack_beats(y: np.ndarray, sr: int, start_bpm: float) -> list[float]:
    """Re-suit les beats sur la bande kick du stem drums.

    La grille du sidecar peut etre un tempo constant legerement faux (ex.
    152 BPM pour des kicks a 0,406 s = 147,8 BPM) : sur 128 pas, la derive
    rend le repliage illisible. Le beat tracker cale sur le kick suit le
    tempo reel, beat par beat."""
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import librosa

        spec = np.abs(librosa.stft(y, n_fft=_N_FFT, hop_length=_HOP)) ** 2
        freqs = librosa.fft_frequencies(sr=sr, n_fft=_N_FFT)
        env = librosa.onset.onset_strength(
            S=librosa.power_to_db(spec[(freqs >= 30) & (freqs < 120)], ref=np.max),
            sr=sr)
        _, beats = librosa.beat.beat_track(
            onset_envelope=env, sr=sr, hop_length=_HOP,
            start_bpm=start_bpm if start_bpm > 0 else 140, tightness=200, units="time")
    return [float(t) for t in beats]


def median_bpm(beat_times: list[float]) -> float:
    """Tempo reel = 60 / intervalle median entre beats."""
    if len(beat_times) < 2:
        return 0.0
    return 60.0 / float(np.median(np.diff(beat_times)))


def step_grid(beat_times: list[float], beats_per_bar: int, steps_per_bar: int) -> np.ndarray:
    """Bornes des pas : chaque intervalle de beat est subdivise regulierement.

    Retourne n_beats_utilises * (steps_per_bar / beats_per_bar) + 1 bornes,
    tronque a un nombre entier de mesures."""
    beats = np.asarray([t for t in beat_times if t >= 0], dtype=float)
    per_beat = steps_per_bar // beats_per_bar
    n_bars = (len(beats) - 1) // beats_per_bar
    if n_bars < 1:
        return np.zeros(0)
    beats = beats[: n_bars * beats_per_bar + 1]
    frac = np.arange(per_beat) / per_beat
    starts = (beats[:-1, None] + np.diff(beats)[:, None] * frac[None, :]).ravel()
    return np.append(starts, beats[-1])


def _reduce_to_steps(values: np.ndarray, frame_times: np.ndarray,
                     bounds: np.ndarray, how: str) -> np.ndarray:
    """Agrege une serie par frame sur les pas (max pour onset, mean energie)."""
    n_steps = len(bounds) - 1
    out = np.zeros(n_steps)
    if values.size == 0 or n_steps < 1:
        return out
    idx = np.searchsorted(bounds, frame_times[: len(values)], side="right") - 1
    valid = (idx >= 0) & (idx < n_steps)
    idx, vals = idx[valid], values[: len(frame_times)][valid]
    if how == "max":
        np.maximum.at(out, idx, vals)
    else:
        np.add.at(out, idx, vals)
        counts = np.bincount(idx, minlength=n_steps)
        out = out / np.maximum(counts, 1)
    return out


def stem_features(stems: dict[str, tuple[np.ndarray, int]],
                  bounds: np.ndarray) -> StepFeatures:
    """Calcule onset / energie / chroma par pas pour chaque track (1 STFT/stem)."""
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import librosa

        onset: dict[int, np.ndarray] = {}
        energy: dict[int, np.ndarray] = {}
        chroma: dict[int, np.ndarray] = {}
        for stem, (y, sr) in stems.items():
            if y.size == 0:
                continue
            rms_db = 20 * np.log10(float(np.sqrt(np.mean(y ** 2))) + 1e-12)
            if rms_db < _SILENT_STEM_DBFS:
                continue
            spec = np.abs(librosa.stft(y, n_fft=_N_FFT, hop_length=_HOP))
            power = spec ** 2
            freqs = librosa.fft_frequencies(sr=sr, n_fft=_N_FFT)
            times = librosa.frames_to_time(np.arange(spec.shape[1]), sr=sr,
                                           hop_length=_HOP)
            stem_chroma: np.ndarray | None = None
            for spec_t in TRACKS:
                if spec_t.stem != stem:
                    continue
                rows = (freqs >= spec_t.lo) & (freqs < spec_t.hi)
                if not rows.any():
                    continue
                band = power[rows]
                env = librosa.onset.onset_strength(
                    S=librosa.power_to_db(band, ref=np.max), sr=sr)
                onset[spec_t.index] = _reduce_to_steps(env, times, bounds, "max")
                energy[spec_t.index] = _reduce_to_steps(
                    band.sum(axis=0), times, bounds, "mean")
                if spec_t.kind == "tonal":
                    if stem_chroma is None:
                        stem_chroma = librosa.feature.chroma_stft(S=power, sr=sr)
                    chroma[spec_t.index] = np.stack(
                        [_reduce_to_steps(c, times, bounds, "mean")
                         for c in stem_chroma], axis=1)
    return StepFeatures(bounds, onset, energy, chroma)


def kick_shift(kick_onset: np.ndarray, steps_per_bar: int) -> int:
    """Pas (mod mesure) ou le kick est le plus fort → devient le pas 0."""
    n = (kick_onset.size // steps_per_bar) * steps_per_bar
    if n == 0:
        return 0
    folded = kick_onset[:n].reshape(-1, steps_per_bar).sum(axis=0)
    # sur un four-on-floor les 4 temps se valent : on ne corrige que la phase
    # a l'interieur d'un temps (la mesure reste calee sur les beats)
    per_beat = max(1, steps_per_bar // 4)
    best = int(np.argmax(folded))
    return best % per_beat


def shift_features(feat: StepFeatures, shift: int) -> StepFeatures:
    """Retire les `shift` premiers pas pour que la mesure demarre sur le kick."""
    if shift <= 0:
        return feat
    return StepFeatures(
        feat.step_times[shift:],
        {k: v[shift:] for k, v in feat.onset.items()},
        {k: v[shift:] for k, v in feat.energy.items()},
        {k: v[shift:] for k, v in feat.chroma.items()},
    )


def _beat_level(energy: np.ndarray, per_beat: int, n_beats: int) -> np.ndarray:
    """Niveau par temps ramene sur 0-1 (-24 dB sous le max de la track = 0)."""
    e = energy[: n_beats * per_beat].reshape(n_beats, per_beat).mean(axis=1)
    ref = float(e.max())
    if ref <= 0:
        return np.zeros(n_beats)
    db = 10 * np.log10(np.maximum(e, 1e-20) / ref)
    return np.clip((db + 24.0) / 24.0, 0.0, 1.0)


def beat_changes(energy: dict[int, np.ndarray], per_beat: int, n_beats: int,
                 window: int) -> np.ndarray:
    """Force des changements d'activite par temps, sommee sur les tracks.

    Pour chaque track : |niveau moyen des `window` temps apres - avant|. Le
    niveau etant lineaire dans le melange, l'ecart culmine pile sur la bascule ;
    on ne garde que les maxima locaux (un clap sur 2 et 4 donne la meme moyenne
    des deux cotes, donc pas de faux changement)."""
    out = np.zeros(n_beats)
    if n_beats <= 2 * window:
        return out
    for e in energy.values():
        x = _beat_level(e, per_beat, n_beats)
        c = np.concatenate([[0.0], np.cumsum(x)])
        b = np.arange(window, n_beats - window + 1)
        d = np.zeros(n_beats)
        d[b] = np.abs((c[b + window] - c[b]) - (c[b] - c[b - window])) / window
        left = np.concatenate([[0.0], d[:-1]])
        right = np.concatenate([d[1:], [0.0]])
        peaks = (d >= left) & (d > right) & (d >= _CHANGE_MIN)
        out += np.where(peaks, d, 0.0)
    return out


def downbeat_offset(feat: StepFeatures, beats_per_bar: int, steps_per_bar: int) -> int:
    """Temps (0..beats_per_bar-1) sur lequel demarre la mesure.

    `kick_shift` ne fixe que la phase dans le temps : sur un four-on-floor les
    4 temps se valent. On garde le decalage qui aligne le mieux les changements
    d'activite des tracks sur les debuts de mesure, plus le clap sur 2 et 4."""
    per_beat = max(1, steps_per_bar // beats_per_bar)
    n_beats = (len(feat.step_times) - 1) // per_beat
    if n_beats < 4 * beats_per_bar:
        return 0
    change = beat_changes(feat.energy, per_beat, n_beats, 2 * beats_per_bar)
    total = float(change.sum())
    scores = np.array([change[k::beats_per_bar].sum() for k in range(beats_per_bar)])
    scores = scores / total if total > 0 else scores
    clap = feat.onset.get(3)
    if clap is not None and beats_per_bar == 4:
        on_beat = clap[: n_beats * per_beat].reshape(n_beats, per_beat)[:, 0]
        pos = np.array([on_beat[k::4].sum() for k in range(4)])
        if pos.sum() > 0:
            for k in range(4):
                back = pos[(k + 1) % 4] + pos[(k + 3) % 4]
                scores[k] += _CLAP_WEIGHT * (back - pos[k] - pos[(k + 2) % 4]) / pos.sum()
    return int(np.argmax(scores))


# --- sections & activite -------------------------------------------------------

Section = tuple[int, int, str, frozenset[int]]   # bar debut, bar fin, label, tracks


def _majority(bar_on: dict[int, np.ndarray], b0: int, b1: int) -> frozenset[int]:
    """Tracks actives sur au moins la moitie des mesures [b0, b1)."""
    return frozenset(i for i, on in bar_on.items() if on[b0:b1].mean() >= 0.5)


def detect_sections(bar_on: dict[int, np.ndarray], n_bars: int,
                    grid: int = _SECTION_GRID) -> list[tuple[int, int, frozenset[int]]]:
    """Decoupe la ou l'ensemble des tracks actives change, sur une grille de
    `grid` mesures, <= 16 sections.

    1. Phase de la grille : le decalage (0..grid-1) qui porte le plus de
       bascules de tracks (un morceau peut demarrer par une mesure d'anacrouse).
    2. Blocs de `grid` mesures, tracks actives a la majorite ; blocs voisins
       identiques fusionnes.
    3. Un bloc isole qui ne differe de ses deux voisins (identiques) que d'une
       track est absorbe : c'est un mute, pas une section.
    4. Au-dela de 16, fusion de la paire voisine la plus proche en contenu."""
    if n_bars < 1:
        return []
    if not bar_on:
        return [(0, n_bars, frozenset())]
    idxs = sorted(bar_on)
    m = np.stack([bar_on[i][:n_bars] for i in idxs], axis=1)
    flips = np.zeros(n_bars)
    flips[1:] = (m[1:] != m[:-1]).sum(axis=1)
    offset = int(np.argmax([flips[o::grid].sum() for o in range(grid)]))
    cuts = sorted({0, n_bars} | set(range(offset, n_bars, grid)))
    blocks = [(a, b, _majority(bar_on, a, b)) for a, b in zip(cuts[:-1], cuts[1:])]

    merged: list[tuple[int, int, frozenset[int]]] = []
    for blk in blocks:
        if merged and merged[-1][2] == blk[2]:
            merged[-1] = (merged[-1][0], blk[1], blk[2])
        else:
            merged.append(blk)

    i = 1
    while i < len(merged) - 1:
        prev, cur, nxt = merged[i - 1], merged[i], merged[i + 1]
        if prev[2] == nxt[2] and cur[1] - cur[0] <= grid and len(cur[2] ^ prev[2]) <= 1:
            merged[i - 1:i + 2] = [(prev[0], nxt[1], prev[2])]
        else:
            i += 1

    while len(merged) > _MAX_PATTERNS:
        cost = [(len(merged[k][2] ^ merged[k + 1][2]),
                 merged[k + 1][1] - merged[k][0], k) for k in range(len(merged) - 1)]
        _, _, k = min(cost)
        a, b = merged[k][0], merged[k + 1][1]
        merged[k:k + 2] = [(a, b, _majority(bar_on, a, b))]
    # une fusion peut rendre deux voisines identiques
    out: list[tuple[int, int, frozenset[int]]] = []
    for part in merged:
        if out and out[-1][2] == part[2]:
            out[-1] = (out[-1][0], part[1], part[2])
        else:
            out.append(part)
    return out


def label_sections(parts: list[tuple[int, int, frozenset[int]]]) -> list[Section]:
    """Labels deduits du contenu : sans kick = breakdown (intro / outro en
    bord de morceau), le plus de tracks = peak, moins au debut = intro, moins
    a la fin = outro, sinon main."""
    if not parts:
        return []
    full = max(len(p[2]) for p in parts)
    last = len(parts) - 1
    out: list[Section] = []
    for i, (b0, b1, act) in enumerate(parts):
        if 1 not in act:
            label = "intro" if i == 0 else "outro" if i == last else "breakdown"
        elif len(act) >= full - (1 if full >= 4 else 0):
            label = "peak"
        elif i == 0:
            label = "intro"
        elif i == last:
            label = "outro"
        else:
            label = "main"
        out.append((b0, b1, label, act))
    return out


def pattern_bars(section_bars: int, steps_per_bar: int) -> int:
    """Plus grande longueur 8/4/2/1 mesures qui tient dans la section et 128 pas."""
    for p in (8, 4, 2, 1):
        if p <= section_bars and p * steps_per_bar <= _MAX_STEPS:
            return p
    return 1


def bar_activity(energy: np.ndarray, steps_per_bar: int, n_bars: int) -> np.ndarray:
    """Energie moyenne par mesure."""
    e = energy[: n_bars * steps_per_bar]
    if e.size < n_bars * steps_per_bar:
        e = np.pad(e, (0, n_bars * steps_per_bar - e.size))
    return e.reshape(n_bars, steps_per_bar).mean(axis=1)


def active_mask(per_unit: np.ndarray, threshold_db: float = _ACTIVE_DB) -> np.ndarray:
    """Actif si l'energie de l'unite est a moins de |threshold_db| du max."""
    ref = float(per_unit.max()) if per_unit.size else 0.0
    if ref <= 0:
        return np.zeros(per_unit.shape, dtype=bool)
    db = 10 * np.log10(np.maximum(per_unit, 1e-20) / ref)
    return db > threshold_db


# --- repliage & trigs ----------------------------------------------------------

def fold_steps(values: np.ndarray, bars: list[int], steps_per_bar: int,
               p_bars: int) -> np.ndarray:
    """Moyenne des mesures `bars` repliees modulo `p_bars` → (p_bars * spb,).
    Accepte aussi des valeurs 2D (n_steps, k) pour le chroma."""
    shape = (p_bars * steps_per_bar,) + values.shape[1:]
    acc = np.zeros(shape)
    counts = np.zeros(p_bars)
    for b in bars:
        chunk = values[b * steps_per_bar:(b + 1) * steps_per_bar]
        if len(chunk) < steps_per_bar:
            continue
        slot = b % p_bars
        acc[slot * steps_per_bar:(slot + 1) * steps_per_bar] += chunk
        counts[slot] += 1
    for slot in range(p_bars):
        if counts[slot]:
            acc[slot * steps_per_bar:(slot + 1) * steps_per_bar] /= counts[slot]
        elif counts.any():  # mesure jamais vue : recopie une mesure remplie
            src = int(np.argmax(counts > 0))
            acc[slot * steps_per_bar:(slot + 1) * steps_per_bar] = \
                acc[src * steps_per_bar:(src + 1) * steps_per_bar]
    return acc


def pick_hits(pattern: np.ndarray, threshold: float) -> tuple[list[int], np.ndarray]:
    """Pas au-dessus du seuil relatif apres etirement robuste.

    Plancher = mediane (le fond continu), plafond = 95e percentile : un seul
    pic aberrant ne doit pas ecraser les autres hits. Si le relief est trop
    faible (son tenu, bruit), un seul trig au pas 0."""
    if pattern.size == 0 or float(pattern.max()) <= 0:
        return [], np.zeros_like(pattern)
    lo = float(np.median(pattern))
    hi = float(np.percentile(pattern, 95))
    if hi <= lo:
        hi = float(pattern.max())
    if hi <= lo:
        return [0], np.zeros_like(pattern)
    stretched = np.clip((pattern - lo) / (hi - lo), 0.0, 1.0)
    contrast = (hi - lo) / hi
    if contrast < _LOW_CONTRAST:
        return [0], stretched
    return [int(i) for i in np.where(stretched >= threshold)[0]], stretched


def _velocity(v: float) -> int:
    return int(np.clip(40 + v * 87, 1, 127))


def classify_hats(hits: list[int], energy: dict[int, np.ndarray]) -> dict[int, list[int]]:
    """Repartit les hits de la famille hats sur 4 (ferme) / 5 (ouvert) / 6 (ride).

    - ouvert : l'energie 5-12 kHz tient encore au pas suivant (decroissance lente)
    - ride   : 3-6 kHz domine 7-16 kHz
    - sinon  : ferme"""
    out: dict[int, list[int]] = {4: [], 5: [], 6: []}
    e_closed, e_open, e_ride = energy.get(4), energy.get(5), energy.get(6)
    n = len(e_closed) if e_closed is not None else 0
    for s in hits:
        if e_open is not None and n and e_open[s] > 0 and \
                e_open[(s + 1) % n] / e_open[s] > 0.75:
            out[5].append(s)
        elif e_ride is not None and e_closed is not None and \
                e_ride[s] > 1.5 * e_closed[s]:
            out[6].append(s)
        else:
            out[4].append(s)
    return out


# --- assemblage --------------------------------------------------------------

def build_bank(
    slug: str,
    fields: dict[str, str],
    bpm: float,
    time_signature: str,
    beats_per_bar: int,
    feat: StepFeatures,
    from_stems: bool,
    phrase_bars: int = 8,
    threshold: float = 0.5,
) -> DigitaktBank:
    """Assemble la bank a partir des features par pas (deja calees sur le
    premier temps de la mesure)."""
    spb = beats_per_bar * 4
    n_steps = len(feat.step_times) - 1
    n_bars = n_steps // spb
    bar_times = feat.step_times[::spb][: n_bars + 1]

    # activite par mesure, pour chaque track detectable
    bar_on: dict[int, np.ndarray] = {}
    for idx, e in feat.energy.items():
        per_bar = bar_activity(e, spb, n_bars)
        bar_on[idx] = active_mask(per_bar)
    sections = label_sections(detect_sections(bar_on, n_bars))

    # une section reprend le slot d'une section precedente si memes tracks
    # actives et grilles proches (comme une chaine de patterns sur la DT)
    patterns: list[DigitaktPattern] = []
    slot_act: dict[int, frozenset[int]] = {}
    section_slots: list[int] = []
    for b0, b1, label, act in sections:
        candidate = _section_pattern(len(patterns) + 1, label, b0, b1, feat, bar_on,
                                     bar_times, spb, threshold)
        reuse = next((q.slot for q in patterns if slot_act[q.slot] == act
                      and pattern_similarity(q, candidate) >= _REUSE_SIM), None)
        if reuse is None:
            patterns.append(candidate)
            slot_act[candidate.slot] = act
            reuse = candidate.slot
        section_slots.append(reuse)

    # drop = retour du kick apres une section sans kick
    drops = [k for k in range(1, len(sections))
             if 1 in sections[k][3] and 1 not in sections[k - 1][3]]
    _add_fx(patterns, section_slots, drops, spb)
    mutes = _mute_partition(bar_on, bar_times, sections, section_slots, phrase_bars,
                            patterns)
    out_sections = [
        DigitaktSection(
            index=k, label=label, bar=b0, bars=b1 - b0,
            start_s=round(float(bar_times[b0]), 2), end_s=round(float(bar_times[b1]), 2),
            pattern_slot=section_slots[k], active=sorted(act),
        )
        for k, (b0, b1, label, act) in enumerate(sections)
    ]
    return DigitaktBank(
        slug=slug, artist=fields.get("artist", ""), title=fields.get("title", ""),
        bpm=round(bpm, 1), time_signature=time_signature, steps_per_bar=spb,
        from_stems=from_stems, phrase_bars=phrase_bars,
        bar_times_s=[round(float(t), 3) for t in bar_times], patterns=patterns,
        sections=out_sections, mutes=mutes,
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )


def _section_pattern(slot: int, label: str, b0: int, b1: int, feat: StepFeatures,
                     bar_on: dict[int, np.ndarray], bar_times: np.ndarray, spb: int,
                     threshold: float) -> DigitaktPattern:
    """Replie une section [b0, b1) sur la longueur de son pattern."""
    p_bars = pattern_bars(b1 - b0, spb)
    length = p_bars * spb
    hits_by_track: dict[int, tuple[list[int], np.ndarray]] = {}
    levels: dict[int, float] = {}
    for spec in TRACKS:
        if spec.index not in feat.energy:
            continue
        on = bar_on[spec.index][b0:b1]
        levels[spec.index] = float(on.mean()) if on.size else 0.0
        bars = [b for b in range(b0, b1) if bar_on[spec.index][b]]
        if len(bars) < max(1, (b1 - b0) // 4):
            continue
        # repliage relatif au debut de section : le pas 0 = 1er temps de la section
        rel = [b - b0 for b in bars]
        src = feat.energy if spec.kind in ("rumble", "sustain") else feat.onset
        values = src[spec.index][b0 * spb:b1 * spb]
        pattern = fold_steps(values, rel, spb, p_bars)
        hits_by_track[spec.index] = pick_hits(
            pattern, threshold if spec.kind != "rumble" else 0.6)

    # exclusions et famille hats
    hat_hits = sorted({s for i in _HAT_FAMILY if i in hits_by_track
                       for s in hits_by_track[i][0]})
    if hat_hits:
        fold_e = {i: fold_steps(feat.energy[i][b0 * spb:b1 * spb],
                                list(range(b1 - b0)), spb, p_bars)
                  for i in _HAT_FAMILY if i in feat.energy}
        split = classify_hats(hat_hits, fold_e)
        ref = next(iter(hits_by_track[i][1] for i in _HAT_FAMILY
                        if i in hits_by_track))
        for i in _HAT_FAMILY:
            hits_by_track[i] = (split[i], ref)

    tracks: list[DigitaktTrack] = []
    for spec in TRACKS:
        trigs: list[DigitaktTrig] = []
        source = spec.stem or ""
        if spec.index in hits_by_track:
            steps, stretched = hits_by_track[spec.index]
            blocked = {s for j in spec.exclude if j in hits_by_track
                       for s in hits_by_track[j][0]}
            if spec.kind == "sustain":
                steps = [0] if steps else []
            chroma = None
            if spec.kind == "tonal" and spec.index in feat.chroma:
                chroma = fold_steps(feat.chroma[spec.index][b0 * spb:b1 * spb],
                                    list(range(b1 - b0)), spb, p_bars)
            for s in steps:
                if s in blocked or s >= length:
                    continue
                note = None
                if chroma is not None:
                    note = spec.base_note + int(np.argmax(chroma[s]))
                trigs.append(DigitaktTrig(
                    step=s, velocity=_velocity(float(stretched[s])), note=note))
        elif spec.kind == "fx":
            source = "structure (heuristique)"
        tracks.append(DigitaktTrack(
            index=spec.index, role=spec.role,
            source=f"{source} {spec.lo:.0f}-{spec.hi:.0f} Hz" if spec.stem else source,
            active=bool(trigs), level=round(min(1.0, levels.get(spec.index, 0.0)), 2),
            trigs=trigs,
        ))
    return DigitaktPattern(
        slot=slot, label=label,
        start_s=round(float(bar_times[b0]), 2), end_s=round(float(bar_times[b1]), 2),
        bars=p_bars, steps=length, repeats=round((b1 - b0) / p_bars, 1),
        tracks=tracks,
    )


def pattern_similarity(a: DigitaktPattern, b: DigitaktPattern) -> float:
    """0-1 : Jaccard moyen des pas par track, sur l'union des tracks jouees
    (une track absente d'un cote compte 0), grilles repliees sur la longueur
    la plus courte."""
    n = min(a.steps, b.steps)
    sa = {t.index: {tr.step % n for tr in t.trigs} for t in a.tracks if t.trigs}
    sb = {t.index: {tr.step % n for tr in t.trigs} for t in b.tracks if t.trigs}
    keys = set(sa) | set(sb)
    if not keys:
        return 1.0
    return float(np.mean([len(sa.get(k, set()) & sb.get(k, set()))
                          / len(sa.get(k, set()) | sb.get(k, set())) for k in keys]))


def _add_fx(patterns: list[DigitaktPattern], section_slots: list[int],
            drops: list[int], spb: int) -> None:
    """Track 15 : impact au pas 0 d'un drop, riser sur la derniere mesure avant.

    Le riser est figure par un trig par temps a velocite croissante : a
    remplacer par la recette de la doctrine (LFO one-shot ou p-locks, FILL).
    Un slot reutilise porte ses FX a chaque passage, comme sur la DT."""
    by_slot = {p.slot: p for p in patterns}
    for k in drops:
        drop = by_slot[section_slots[k]]
        prev = by_slot[section_slots[k - 1]]
        last = prev.steps - spb
        beat = spb // 4 if spb >= 4 else 1
        n = spb // beat
        riser = [DigitaktTrig(step=last + j * beat, velocity=int(50 + 77 * (j + 1) / n))
                 for j in range(n)]
        for pat, trigs in ((drop, [DigitaktTrig(step=0, velocity=127)]), (prev, riser)):
            fx = pat.tracks[14]
            merged = {t.step: t for t in fx.trigs}
            merged.update({t.step: t for t in trigs})
            fx.trigs = [merged[s] for s in sorted(merged)]
            fx.active = True


def _mute_partition(bar_on: dict[int, np.ndarray], bar_times: np.ndarray,
                    sections: list[Section], section_slots: list[int],
                    phrase_bars: int, patterns: list[DigitaktPattern]
                    ) -> list[DigitaktPhrase]:
    """Par phrase : tracks actives (majorite des mesures) et pattern en cours.

    Les phrases repartent a chaque debut de section : une phrase ne chevauche
    jamais deux patterns (une bascule de pattern tombe en debut de phrase)."""
    by_slot = {p.slot: p for p in patterns}
    out: list[DigitaktPhrase] = []
    for (s0, s1, _label, _act), slot in zip(sections, section_slots):
        pat_tracks = {t.index for t in by_slot[slot].tracks if t.trigs}
        for b in range(s0, s1, phrase_bars):
            end = min(b + phrase_bars, s1)
            active = sorted(
                i for i, on in bar_on.items()
                if i in pat_tracks and on[b:end].mean() >= 0.5
            )
            if 15 in pat_tracks:
                active = sorted(set(active) | {15})
            out.append(DigitaktPhrase(start_s=round(float(bar_times[b]), 2), bar=b,
                                      pattern_slot=slot, active=active))
    return out


# --- rendus ------------------------------------------------------------------

def grid_line(track: DigitaktTrack, steps: int) -> str:
    """`x...x...` par page de 16 pas, separees par un espace."""
    on = {t.step for t in track.trigs}
    cells = "".join("x" if s in on else "." for s in range(steps))
    return " ".join(cells[i:i + 16] for i in range(0, steps, 16))


def render_markdown(bank: DigitaktBank) -> str:
    """Note Obsidian : resume, partition de mutes, grilles par pattern."""
    name = f"{bank.artist} — {bank.title}" if bank.artist else bank.slug
    lines = [
        "---",
        "tags: [digitakt, bank, draft]",
        f"slug: {bank.slug}",
        f"bpm: {bank.bpm}",
        f"generated: {bank.generated_at}",
        "---",
        "",
        f"# Bank — {name}",
        "",
        f"Draft genere par `digitakt.py` ({'stems Demucs' if bank.from_stems else 'mix, plus bruite'}), "
        f"{bank.bpm} BPM, {bank.time_signature}. Grille des tracks : "
        "[[../../digitakt/doctrine|doctrine]]. Point de depart, pas une transcription.",
        "",
        "## Patterns",
        "",
        "| Slot | Section | Debut | Mesures | Tours | Tracks actives |",
        "|---|---|---|---|---|---|",
    ]
    for p in bank.patterns:
        act = " ".join(str(t.index) for t in p.tracks if t.trigs) or "-"
        lines.append(f"| {p.slot:02d} | {p.label} | {_mmss(p.start_s)} | {p.bars} "
                     f"| x{p.repeats} | {act} |")
    lines += ["", "## Structure (ordre de jeu)", "",
              "Chaine : " + " - ".join(f"{c:02d}" for c in bank.chain), "",
              "| Section | Debut | Mesures | Slot | Tracks actives |", "|---|---|---|---|---|"]
    for sec in bank.sections:
        act = " ".join(str(i) for i in sec.active) or "-"
        lines.append(f"| {sec.label} | {_mmss(sec.start_s)} | {sec.bars} "
                     f"| {sec.pattern_slot:02d} | {act} |")
    lines += ["", f"## Partition de mutes (phrases de {bank.phrase_bars} mesures)", "",
              "```", "temps  pat  " + "".join(f"{i:<3d}" for i in range(1, 17))]
    for ph in bank.mutes:
        row = "".join(("x  " if i in ph.active else ".  ") for i in range(1, 17))
        lines.append(f"{_mmss(ph.start_s)}  {ph.pattern_slot:02d}   {row}")
    lines += ["```", ""]
    for p in bank.patterns:
        lines += [f"## Pattern {p.slot:02d} — {p.label} ({_mmss(p.start_s)}, "
                  f"{p.bars} mesure(s), x{p.repeats})", "", "```"]
        for t in p.tracks:
            if not t.trigs:
                continue
            notes = ""
            if any(tr.note is not None for tr in t.trigs):
                notes = "  " + " ".join(_note_name(tr.note) for tr in t.trigs
                                        if tr.note is not None)
            lines.append(f"{t.index:02d} {t.role:<13} {grid_line(t, p.steps)}{notes}")
        lines += ["```", ""]
    lines.append("#digitakt #bank")
    return "\n".join(lines) + "\n"


def write_pattern_midi(pattern: DigitaktPattern, bpm: float, out_path: Path,
                       ppq: int = 480) -> None:
    """Un .mid par pattern, canal = track - 1 (Digitakt : canaux auto 1-16).

    Drums a la note 60 (pitch d'origine du sample), tonales a la note estimee."""
    import mido

    ticks_per_step = ppq // 4
    mid = mido.MidiFile(ticks_per_beat=ppq)
    trk = mido.MidiTrack()
    mid.tracks.append(trk)
    trk.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm or 120), time=0))
    trk.append(mido.MetaMessage("track_name", name=f"pattern {pattern.slot:02d}", time=0))
    events: list[tuple[int, int, Any]] = []
    for t in pattern.tracks:
        for tr in t.trigs:
            note = tr.note if tr.note is not None else 60
            on = tr.step * ticks_per_step
            events.append((on, 1, mido.Message("note_on", channel=t.index - 1,
                                               note=note, velocity=tr.velocity)))
            events.append((on + ticks_per_step // 2, 0,
                           mido.Message("note_off", channel=t.index - 1,
                                        note=note, velocity=0)))
    events.append((pattern.steps * ticks_per_step, 2, mido.MetaMessage("end_of_track")))
    events.sort(key=lambda e: (e[0], e[1]))
    prev = 0
    for tick, _prio, msg in events:
        msg.time = tick - prev
        prev = tick
        trk.append(msg)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    mid.save(str(out_path))


_NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


def _note_name(note: int) -> str:
    return f"{_NOTE_NAMES[note % 12]}{note // 12 - 1}"


def _mmss(seconds: float) -> str:
    return f"{int(seconds) // 60}:{int(seconds) % 60:02d}"

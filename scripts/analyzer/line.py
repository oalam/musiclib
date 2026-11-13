"""Niveau sur la ligne inclinee (doctrine-samples, « Niveaux » et « Pre-mastering »).

Equivalent automatique du pas a pas Pro-Q 4 de
`digitakt/kb/tutos/maison-premaster-samples.md` :

- spectre aux maxima maintenus (Freeze de Pro-Q) : FFT de 8192 points, maximum
  par bin sur toutes les trames, lisse au 1/6 d'octave ;
- incline de +4,5 dB/oct autour de 1 kHz ;
- le « haut du spectre » est le maximum de cette courbe entre 20 Hz et 20 kHz.

La ligne s'etalonne sur un kick de reference : sa valeur, mesuree apres le
meme traitement, est la ligne. Le gain d'un son est `ligne + decalage - haut`,
borne pour que la crete reste sous le plafond (-6 dBFS).

Traitements automatiques (ceux qui ne demandent pas d'ecoute, plus le
passe-haut de la famille, choix du 2026-11-13) : coupure sous 20 Hz, passe-haut
de la famille (valeur basse de la table « Par track »), mono sous 120 Hz (sauf
grave, entierement mono), gain sur la ligne, plafond de crete.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf
import soxr
from pydantic import BaseModel
from scipy import signal

TARGET_SR = 48000        # frequence native de la DT2
# Version du traitement : a incrementer quand le rendu change (reglages,
# algorithme), pour que l'export reecrive les fichiers deja ecrits.
LINE_VERSION = 1
TILT_DB_OCT = 4.5        # inclinaison de l'analyseur (doctrine-samples)
TILT_PIVOT_HZ = 1000.0   # frequence ou l'inclinaison vaut 0 dB
N_FFT = 8192
HOP = 1024
SMOOTH_OCT = 1 / 6       # lissage du spectre (Resolution High de Pro-Q, approx.)
# Poids d'une bande lissee : puissance sommee / nb_bins**(1 - BAND_WEIGHT).
# 0 = moyenne (sous-estime les sons bruites face a Pro-Q), 1 = somme (les
# surestime). 0,75 ajuste le 2026-11-13 sur 4 sons poses sur la ligne a la main
# dans Live + Pro-Q 4 (CP 909 1, HH 909 2/3/4 slr PRE MASTER) : ecarts -0,5 a
# +1,7 dB par rapport au kick de reference, ecart quadratique moyen 0,9 dB.
BAND_WEIGHT = 0.75
F_LO, F_HI = 20.0, 20000.0
CEILING_DB = -6.0        # plafond de crete, tous les sons
SUBSONIC_HZ = 20.0       # coupure sous 20 Hz, tout le monde
SIDE_HP_HZ = 120.0       # mono sous 120 Hz pour les sons stereo
# boucles : mono sous 150 Hz (doctrine-samples, tracks 7-8 et 13)
SIDE_HP_BY_CODE = {"BR": 150.0, "DL": 150.0, "PL": 150.0, "BL": 150.0, "ML": 150.0}
HP_ORDER = 4             # 24 dB/oct, phase minimale (pas de pre-echo)

# Hub des reglages par code : passe-haut de la famille (valeur basse de la
# table « Par track : points de depart » de doctrine-samples), mono integral,
# decalage autour de la ligne (0 partout tant qu'il n'est pas fixe a l'oreille).
FAMILY: dict[str, tuple[float | None, bool, float]] = {
    # code: (passe-haut Hz, mono integral, decalage dB)
    "BD": (None, True, 0.0),
    "RM": (None, True, 0.0),
    "CP": (150.0, False, 0.0),
    "SD": (150.0, False, 0.0),
    "TM": (60.0, False, 0.0),
    "PC": (200.0, False, 0.0),
    "HH": (300.0, False, 0.0),
    "OH": (300.0, False, 0.0),
    "CY": (500.0, False, 0.0),
    "BR": (100.0, False, 0.0),
    "DL": (100.0, False, 0.0),
    "PL": (100.0, False, 0.0),
    "BS": (None, True, 0.0),
    "BL": (None, False, 0.0),   # mono sous 150 Hz, stereo gardee au-dessus (2026-11-13)
    "ST": (150.0, False, 0.0),
    "PD": (200.0, False, 0.0),
    "VX": (100.0, False, 0.0),
    "ML": (100.0, False, 0.0),
    "FX": (100.0, False, 0.0),
}


class LineError(ValueError):
    """Signal inexploitable pour la mesure de la ligne (vide, silencieux)."""


class LineResult(BaseModel):
    """Ce que le passage sur la ligne a fait a un son."""

    top_db: float          # haut du spectre incline, avant gain
    gain_db: float         # gain applique
    peak_db: float         # crete apres gain
    capped: bool           # gain borne par le plafond de crete


def _hp(y: np.ndarray, sr: int, hz: float) -> np.ndarray:
    sos = signal.butter(HP_ORDER, hz, btype="highpass", fs=sr, output="sos")
    return np.asarray(signal.sosfilt(sos, y, axis=0))


def premaster(y: np.ndarray, sr: int, code: str) -> np.ndarray:
    """Coupures et image stereo de la famille. `y` : (n,) ou (n, canaux).
    Rend (n,) pour un son mono ou un code entierement mono, (n, 2) sinon."""
    hp, full_mono, _ = FAMILY[code]
    if y.ndim == 2 and (full_mono or y.shape[1] == 1):
        y = y.mean(axis=1)
    y = _hp(y, sr, SUBSONIC_HZ)
    if hp:
        y = _hp(y, sr, hp)
    if y.ndim == 2:   # mono sous 120 Hz : passe-haut sur le side
        mid = (y[:, 0] + y[:, 1]) / 2
        side = _hp((y[:, 0] - y[:, 1]) / 2, sr, SIDE_HP_BY_CODE.get(code, SIDE_HP_HZ))
        y = np.stack([mid + side, mid - side], axis=1)
    return y


def spectrum_top(y: np.ndarray, sr: int) -> float:
    """Haut du spectre aux maxima maintenus, incline de +4,5 dB/oct (dB)."""
    mono = y.mean(axis=1) if y.ndim == 2 else y
    if mono.size == 0 or not np.any(mono):
        raise LineError("signal vide ou silencieux")
    if mono.size < N_FFT:
        mono = np.pad(mono, (0, N_FFT - mono.size))
    _, _, z = signal.stft(mono, fs=sr, window="hann", nperseg=N_FFT,
                          noverlap=N_FFT - HOP, boundary="zeros", padded=True)
    mag = np.abs(z).max(axis=1) * 2   # maxima maintenus ; *2 : spectre unilateral
    freqs = np.fft.rfftfreq(N_FFT, 1 / sr)
    band = (freqs >= F_LO) & (freqs <= min(F_HI, sr / 2))
    f, power = freqs[band], mag[band] ** 2
    # lissage en puissance sur une fenetre d'un 1/6 d'octave centree (poids BAND_WEIGHT)
    lo = np.searchsorted(f, f * 2 ** (-SMOOTH_OCT / 2))
    hi = np.searchsorted(f, f * 2 ** (SMOOTH_OCT / 2), side="right")
    csum = np.concatenate([[0.0], np.cumsum(power)])
    smooth = (csum[hi] - csum[lo]) / np.maximum(hi - lo, 1) ** (1 - BAND_WEIGHT)
    db = 10 * np.log10(np.maximum(smooth, 1e-20))
    db += TILT_DB_OCT * np.log2(f / TILT_PIVOT_HZ)
    return float(db.max())


def peak_db(y: np.ndarray) -> float:
    peak = float(np.abs(y).max()) if y.size else 0.0
    return 20 * np.log10(peak) if peak > 0 else -np.inf


def on_line(y: np.ndarray, sr: int, code: str, line_db: float,
            ceiling_db: float = CEILING_DB) -> tuple[np.ndarray, LineResult]:
    """Gain qui pose le haut du spectre sur `line_db` (+ decalage de la
    famille), borne par le plafond de crete."""
    top = spectrum_top(y, sr)
    want = line_db + FAMILY[code][2] - top
    room = ceiling_db - peak_db(y)
    gain = min(want, room)
    out = y * 10 ** (gain / 20)
    return out, LineResult(top_db=round(top, 2), gain_db=round(gain, 2),
                           peak_db=round(peak_db(out), 2), capped=want > room)


def load_shaped(path: Path, code: str, semitones: int = 0) -> np.ndarray:
    """Lit `path`, le transpose en varispeed de `semitones` (la duree suit,
    comme le pitch de la DT2), le passe a 48 kHz et applique les coupures et
    l'image stereo de la famille."""
    y, sr = sf.read(str(path), always_2d=True, dtype="float64")
    src_sr = sr * 2.0 ** (semitones / 12.0)
    if src_sr != TARGET_SR:
        y = soxr.resample(y, src_sr, TARGET_SR, quality="VHQ")
    return premaster(y, TARGET_SR, code)


def ref_line(ref: Path) -> float:
    """La ligne : haut du spectre incline du kick de reference, a son niveau."""
    try:
        return spectrum_top(load_shaped(ref, "BD"), TARGET_SR)
    except (RuntimeError, sf.LibsndfileError) as e:
        raise LineError(f"kick de reference illisible : {ref} ({e})") from e


def render(path: Path, code: str, line_db: float,
           semitones: int = 0) -> tuple[np.ndarray, LineResult]:
    """Son pret pour la DT2 : forme de la famille, puis gain sur la ligne."""
    return on_line(load_shaped(path, code, semitones), TARGET_SR, code, line_db)


def write_pcm16(out: Path, y: np.ndarray, sr: int = TARGET_SR) -> None:
    """WAV 16 bits avec dither TPDF (graine fixe : rendu identique d'un
    export a l'autre)."""
    rng = np.random.default_rng(0)
    lsb = 1 / 32768
    noise = (rng.random(y.shape) - rng.random(y.shape)) * lsb
    sf.write(str(out), np.clip(y + noise, -1.0, 1.0 - lsb), sr, subtype="PCM_16", format="WAV")

"""Saturations maison du sound design (Phase 8) : Overdrive et Dynamic Tube.

Emulations inspirees des devices d'Ableton Live (manuel Live 12, « Live
Audio Effect Reference ») : le manuel decrit le flux et le role des
parametres, pas le DSP ; les courbes ci-dessous en sont une interpretation.

Chaque device expose l'interface d'un plugin pedalboard : parametres en
attributs, `process(x, sr, reset)` et appel direct. Le moteur peut donc les
automatiser bloc par bloc comme les autres (`params_end`), l'etat interne
(filtres, suiveur d'enveloppe) etant garde d'un bloc a l'autre.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.signal import firwin, lfilter


def _one_pole(ms: float, sr: int) -> float:
    """Coefficient d'un lisseur du 1er ordre de constante de temps `ms`."""
    return math.exp(-1.0 / max(1.0, ms * sr / 1000.0))


def _follow(level: np.ndarray, attack: float, release: float, state: float) -> tuple[np.ndarray, float]:
    """Suiveur d'enveloppe a attaque / relache distinctes (boucle : recursion non lineaire)."""
    out = np.empty_like(level)
    env = state
    for i, v in enumerate(level):
        coef = attack if v > env else release
        env = coef * env + (1.0 - coef) * v
        out[i] = env
    return out, env


class _Filters:
    """Filtres pedalboard dont l'etat survit aux blocs (reset au premier)."""

    def __init__(self) -> None:
        import pedalboard
        self.pb = pedalboard

    @staticmethod
    def run(plugin: object, x: np.ndarray, sr: int, reset: bool) -> np.ndarray:
        return np.asarray(plugin.process(x, sr, reset=reset), dtype=np.float32)  # type: ignore[attr-defined]


class Overdrive(_Filters):
    """Pedale d'overdrive : passe-bande -> saturation -> tonalite -> dynamique -> dry/wet.

    - le passe-bande (`filter_hz`, `width_oct`) choisit la bande saturee ;
    - `drive` (%) : 0 % distord deja (gain de base +6 dB), 100 % = +42 dB ;
      courbe asymetrique (harmoniques paires, grain de pedale) ;
    - `tone` (%) : passe-bas apres la saturation, de 800 Hz a 20 kHz ;
    - `dynamics` (%) : 0 % = la saturation compresse et rattrape le niveau
      (son plat et dense), 100 % = l'enveloppe de l'entree est rendue ;
    - `dry_wet` (%) : melange avec le signal d'entree.
    """

    BIAS = 0.2               # decalage de la courbe : asymetrie, harmoniques paires
    ENV_MS = 10.0            # lissage des enveloppes de la dynamique

    def __init__(self, filter_hz: float = 1000.0, width_oct: float = 6.0, drive: float = 50.0,
                 tone: float = 50.0, dynamics: float = 50.0, dry_wet: float = 100.0) -> None:
        super().__init__()
        self.filter_hz, self.width_oct = filter_hz, width_oct
        self.drive, self.tone, self.dynamics, self.dry_wet = drive, tone, dynamics, dry_wet
        self._hp = self.pb.LadderFilter(mode=self.pb.LadderFilter.Mode.HPF12, cutoff_hz=100, resonance=0)
        self._lp = self.pb.LadderFilter(mode=self.pb.LadderFilter.Mode.LPF12, cutoff_hz=8000, resonance=0)
        self._tone = self.pb.LowpassFilter(cutoff_frequency_hz=8000)
        self._zi = np.zeros((2, 2, 1))   # (entree / sortie, canal, ordre)

    def process(self, x: np.ndarray, sr: int, reset: bool = True) -> np.ndarray:
        nyq = sr / 2 * 0.95
        half = 2.0 ** (self.width_oct / 2)
        self._hp.cutoff_hz = min(nyq, max(20.0, self.filter_hz / half))
        self._lp.cutoff_hz = min(nyq, max(40.0, self.filter_hz * half))
        self._tone.cutoff_frequency_hz = min(nyq, 800.0 * (20000.0 / 800.0) ** (self.tone / 100))
        band = self.run(self._lp, self.run(self._hp, x, sr, reset), sr, reset)

        # saturation pleine echelle : compresse et rattrape le niveau (dynamique 0 %)
        gain = 10.0 ** ((6.0 + 36.0 * self.drive / 100) / 20)
        b = self.BIAS
        shaped = (np.tanh(band * gain + b) - math.tanh(b)) / (1.0 + math.tanh(b))
        shaped = self.run(self._tone, shaped.astype(np.float32), sr, reset)

        # dynamique : rend l'enveloppe de la bande d'entree a la sortie saturee
        d = self.dynamics / 100
        if d > 0:
            if reset:
                self._zi[:] = 0.0
            a = _one_pole(self.ENV_MS, sr)
            env_in, self._zi[0] = lfilter([1 - a], [1, -a], np.abs(band), axis=1, zi=self._zi[0])
            env_out, self._zi[1] = lfilter([1 - a], [1, -a], np.abs(shaped), axis=1, zi=self._zi[1])
            ratio = np.clip((env_in + 1e-6) / (env_out + 1e-6), 0.0, 4.0)
            shaped = shaped * ratio ** d
        mix = self.dry_wet / 100
        return ((1 - mix) * x + mix * shaped).astype(np.float32)

    def __call__(self, x: np.ndarray, sr: int) -> np.ndarray:
        return self.process(x, sr, reset=True)


TUBE_MODELS = ["A", "B", "C"]
OVERSAMPLE = 4               # Hi-Quality : courbe du tube calculee a 4 x la frequence
_AA_TAPS = 64                # filtre anti-repliement (FIR, phase lineaire) : 0,33 ms de latence a 48 kHz


class _Oversampler:
    """Sur-echantillonnage x OVERSAMPLE autour d'une non-linearite, etat garde
    d'un bloc a l'autre (meme resultat par blocs que d'un seul tenant)."""

    def __init__(self) -> None:
        self.h = firwin(_AA_TAPS, 0.9 / OVERSAMPLE).astype(np.float64)
        self.reset()

    def reset(self) -> None:
        self.zi_up = np.zeros((2, _AA_TAPS - 1))
        self.zi_down = np.zeros((2, _AA_TAPS - 1))

    def up(self, x: np.ndarray) -> np.ndarray:
        stuffed = np.zeros((x.shape[0], x.shape[1] * OVERSAMPLE))
        stuffed[:, ::OVERSAMPLE] = x * OVERSAMPLE
        out, self.zi_up = lfilter(self.h, [1.0], stuffed, axis=1, zi=self.zi_up)
        return np.asarray(out)

    def down(self, x: np.ndarray) -> np.ndarray:
        out, self.zi_down = lfilter(self.h, [1.0], x, axis=1, zi=self.zi_down)
        return np.asarray(out)[:, ::OVERSAMPLE]


def _tube(u: np.ndarray, model: int) -> np.ndarray:
    """Courbe de transfert du tube : A lineaire sous un seuil, B douce, C asymetrique toujours."""
    if model == 0:   # A : propre sous 0,6, harmoniques brillantes au-dela
        a = np.abs(u)
        return np.where(a <= 0.6, u, np.sign(u) * (0.6 + 0.4 * np.tanh((a - 0.6) / 0.4)))
    if model == 1:   # B : saturation douce symetrique
        return np.tanh(u)
    # C : mauvais ampli, alternances inegales des le plus petit signal
    return np.where(u >= 0, (1 - np.exp(-3.0 * u)) / 3.0, 0.8 * np.tanh(u))


class DynamicTube(_Filters):
    """Saturation a lampe dont le bias suit l'enveloppe du signal.

    - `model` : A (propre si bias bas, s'allume au-dela d'un seuil), B, C
      (distord tout le temps) ;
    - `drive_db` : niveau envoye dans le tube ; `bias` (0..1) : pousse le
      point de repos dans la courbe (asymetrie, grain ; tres haut = degrade) ;
    - `envelope` (-3..3) : module le bias par l'enveloppe ; positif = plus de
      distorsion sur les forts, negatif = les forts restent propres
      (expansion) ; `attack_ms` / `release_ms` : vitesse du suiveur ;
    - `tone` (0..1) : 0,5 neutre ; plus haut, la distorsion porte sur les
      aigus (aigus accentues avant le tube, rendus apres), plus bas sur le
      grave / medium ;
    - `output_db` : niveau de sortie ;
    - `hi_quality` : 1 = courbe calculee a 4 x la frequence d'echantillonnage
      (moins de repliement sur les aigus satures, 0,33 ms de latence).
    """

    TONE_HZ = 1200.0          # pivot de la pre- / desaccentuation
    TONE_DB = 12.0            # amplitude de l'accentuation a tone = 0 ou 1

    def __init__(self, model: float = 1, drive_db: float = 0.0, bias: float = 0.2, envelope: float = 0.0,
                 attack_ms: float = 10.0, release_ms: float = 100.0, tone: float = 0.5,
                 output_db: float = 0.0, hi_quality: float = 0) -> None:
        super().__init__()
        self.hi_quality = hi_quality
        self._os = _Oversampler()
        self.model, self.drive_db, self.bias, self.envelope = model, drive_db, bias, envelope
        self.attack_ms, self.release_ms, self.tone, self.output_db = attack_ms, release_ms, tone, output_db
        self._pre = self.pb.HighShelfFilter(cutoff_frequency_hz=self.TONE_HZ, gain_db=0.0)
        self._post = self.pb.HighShelfFilter(cutoff_frequency_hz=self.TONE_HZ, gain_db=0.0)
        self._dc = self.pb.HighpassFilter(cutoff_frequency_hz=10.0)
        self._env = 0.0

    def process(self, x: np.ndarray, sr: int, reset: bool = True) -> np.ndarray:
        tilt = (self.tone - 0.5) * 2 * self.TONE_DB
        self._pre.gain_db, self._post.gain_db = tilt, -tilt
        u = self.run(self._pre, x, sr, reset) * 10.0 ** (self.drive_db / 20)

        bias = np.full(u.shape[1], 0.8 * self.bias)
        if self.envelope:
            if reset:
                self._env = 0.0
            env, self._env = _follow(np.max(np.abs(x), axis=0), _one_pole(self.attack_ms, sr),
                                     _one_pole(self.release_ms, sr), self._env)
            bias = np.clip(bias + 0.3 * self.envelope * env, -1.5, 1.5)
        model = int(round(self.model))
        if round(self.hi_quality):
            # signal sur-echantillonne ; bias (lent) tenu, sans filtrage : pas de
            # transitoire du point de repos au premier bloc
            if reset:
                self._os.reset()
            hi_bias = np.repeat(bias, OVERSAMPLE)
            y = self._os.down(_tube(self._os.up(u) + hi_bias, model) - _tube(hi_bias, model))
        else:
            y = _tube(u + bias, model) - _tube(bias, model)   # point de repos retire
        y = self.run(self._dc, y.astype(np.float32), sr, reset)
        y = self.run(self._post, y, sr, reset)
        return (y * 10.0 ** (self.output_db / 20)).astype(np.float32)

    def __call__(self, x: np.ndarray, sr: int) -> np.ndarray:
        return self.process(x, sr, reset=True)

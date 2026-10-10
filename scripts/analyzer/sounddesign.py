"""Moteur de sound design (Phase 8) : traitements = chaines de plugins.

Un **traitement** (ex. `rumble`) prepare un signal d'entree a partir d'un
sample de la library (ex. un kick sequence sur N mesures), puis le fait
passer dans des **chaines paralleles** de **devices** (plugins pedalboard ou
devices maison numpy), sommees puis envoyees dans la chaine **master**.

```
source ──prepare──▶ entree ─┬─▶ chaine "Kick"   : [highpass] ──────────┐
                            └─▶ chaine "Rumble" : [reverb, lowpass, …] ─┴─▶ master : [limiter] ─▶ boucle
```

Un **preset** (JSON du vault, `library/sounddesign/presets/<traitement>/`)
fige la topologie et les valeurs : chaque device a un `bypass`, chaque
chaine un `mute` et un `gain_db`. Les parametres absents prennent la valeur
par defaut du catalogue (`DEVICES`).

Rendu en boucle sans couture : le motif est rejoue en pre-roll (au moins
4 s) pour que reverbs et compresseurs soient dans leur regime de croisiere,
puis seule la derniere boucle est gardee. Sortie stereo 48 kHz (frequence
native de la Digitakt II), crete normalisee.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

import numpy as np
from pydantic import BaseModel, Field

from analyzer import samples as smp

SR = 48_000
PREROLL_SECONDS = 4.0

Processor = Callable[[np.ndarray], np.ndarray]   # (2, n) -> (2, n)


class PresetError(ValueError):
    """Preset invalide : device, parametre ou valeur hors catalogue."""


class SourceError(ValueError):
    """Sample source illisible ou vide."""


# ---------------------------------------------------------------------------
# Modeles (serialises par l'API et les presets)
# ---------------------------------------------------------------------------

class ParamSpec(BaseModel):
    name: str
    label: str
    min: float
    max: float
    default: float
    unit: str = ""
    scale: Literal["lin", "log"] = "lin"   # rendu du potard dans le front
    step: float | None = None              # valeurs discretes (ex. 1 pour un entier)
    choices: list[str] | None = None       # libelles des valeurs 0..n-1 (selecteur, pas potard)
    help: str = ""


class DeviceSpec(BaseModel):
    type: str
    label: str
    help: str
    params: list[ParamSpec]


class Device(BaseModel):
    type: str
    params: dict[str, float] = Field(default_factory=dict)
    # automation (8.G) : valeur atteinte en fin de rendu, depuis `params` ;
    # vide = statique, omis a la serialisation (hash des rendus anterieurs inchange)
    params_end: dict[str, float] = Field(default_factory=dict, exclude_if=lambda v: not v)
    bypass: bool = False


class Chain(BaseModel):
    name: str
    mute: bool = False
    gain_db: float = 0.0
    devices: list[Device] = Field(default_factory=list)


class Preset(BaseModel):
    id: str
    treatment: str
    label: str
    description: str = ""
    settings: dict[str, float] = Field(default_factory=dict)
    chains: list[Chain]
    master: list[Device] = Field(default_factory=list)
    output_peak_db: float | None = -1.0   # None = pas de normalisation


class TreatmentSpec(BaseModel):
    id: str
    label: str
    summary: str
    source_hint: str                 # quel sample donner en entree
    settings: list[ParamSpec]
    notebook: str                    # note du vault (theorie, usage, ressources)
    code: str                        # code DT2 du rendu verse (samples.CODES), ex. RM
    sub: str = ""                    # sous-dossier fixe (FX/RISE) ; "" : herite de la source


class RenderRecord(BaseModel):
    """Sidecar d'un rendu : de quoi le rejouer a l'identique."""

    file: str                        # relatif a SOUNDDESIGN_OUT_DIR
    source: str
    preset: Preset                   # snapshot effectif (overrides compris)
    sr: int
    seconds: float
    created_at: str
    name: str = ""                   # nom DT2 propose ou saisi ("" : rendu anterieur a 8.E)
    sub: str = ""                    # sous-dossier herite de la source (DRUMS/RM/<sub>)
    versed: str | None = None        # cle du manifeste si verse dans le pack (rempli a la lecture)


# ---------------------------------------------------------------------------
# Catalogue des devices
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RenderContext:
    sr: int
    triggers: np.ndarray             # positions (echantillons) des coups de la source
    ramp: np.ndarray | None = None   # avancement 0 -> 1 de l'automation, par echantillon


PluginFactory = Callable[[dict[str, float]], object]   # parametres -> plugin pedalboard


@dataclass(frozen=True)
class _DeviceDef:
    spec: DeviceSpec
    build: Callable[[dict[str, float], RenderContext], Processor]
    plugin: PluginFactory | None = None   # pedalboard : automatisable (8.G)


def _p(name: str, label: str, lo: float, hi: float, default: float, unit: str = "",
       scale: Literal["lin", "log"] = "lin", step: float | None = None,
       help: str = "", choices: list[str] | None = None) -> ParamSpec:
    return ParamSpec(name=name, label=label, min=lo, max=hi, default=default,
                     unit=unit, scale=scale, step=step, help=help, choices=choices)


def _pedalboard(cls_name: str, mode: str | None = None) -> PluginFactory:
    """Fabrique d'un plugin pedalboard ; les noms de parametres sont ceux de pedalboard
    (ce sont aussi ses attributs, que l'automation modifie bloc par bloc).

    `mode` fige une valeur d'enum (ex. `LPF24` du ladder), non exposee en potard.
    """
    def plugin(params: dict[str, float]) -> object:
        import pedalboard
        cls = getattr(pedalboard, cls_name)
        kwargs: dict[str, object] = dict(params)
        if mode is not None:
            kwargs["mode"] = getattr(cls.Mode, mode)
        return cls(**kwargs)
    return plugin


def _pb(spec: DeviceSpec, plugin: PluginFactory) -> _DeviceDef:
    """Device pedalboard : rendu statique d'un seul tenant, automatisable."""
    def build(params: dict[str, float], ctx: RenderContext) -> Processor:
        p = plugin(params)
        return lambda x: np.asarray(p(x, ctx.sr), dtype=np.float32)  # type: ignore[operator]
    return _DeviceDef(spec, build, plugin)


def _duck(params: dict[str, float], ctx: RenderContext) -> Processor:
    """Sidechain sur les coups de la source : creux de `depth_db` a chaque coup."""
    sr = ctx.sr
    attack = max(1, int(params["attack_ms"] * sr / 1000))
    hold = int(params["hold_ms"] * sr / 1000)
    release = max(1, int(params["release_ms"] * sr / 1000))
    shape = np.concatenate([np.linspace(0.0, 1.0, attack, endpoint=False),
                            np.ones(hold), np.linspace(1.0, 0.0, release)])

    def process(x: np.ndarray) -> np.ndarray:
        # anticipation (8.E) : l'attaque se termine sur le coup, le creux est
        # complet quand le kick frappe ; une boucle commence et finit donc
        # dans le creux (pas de clic quand on la joue une fois)
        n = x.shape[1]
        amount = np.zeros(n)
        for t in ctx.triggers:
            start = int(t) - attack
            seg = shape[max(0, -start): max(0, n - start)]
            lo = max(0, start)
            np.maximum(amount[lo: lo + len(seg)], seg, out=amount[lo: lo + len(seg)])
        gain = 10.0 ** (-params["depth_db"] * amount / 20.0)
        return (x * gain).astype(np.float32)
    return process


def _width(params: dict[str, float], ctx: RenderContext) -> Processor:
    """Largeur stereo par mid/side : 0 = mono (sub propre en sound system), 1 = inchange."""
    def process(x: np.ndarray) -> np.ndarray:
        mid = (x[0] + x[1]) / 2
        side = (x[0] - x[1]) / 2 * params["width"]
        return np.stack([mid + side, mid - side]).astype(np.float32)
    return process


_HZ = dict(unit="Hz", scale="log")

# Types du device `filter` : libelle affiche -> mode du LadderFilter pedalboard
FILTER_MODES = {"LP12": "LPF12", "LP24": "LPF24", "HP12": "HPF12", "HP24": "HPF24",
                "BP12": "BPF12", "BP24": "BPF24"}


def _filter(params: dict[str, float]) -> object:
    """LadderFilter dont le mode vient du parametre `mode` (index de FILTER_MODES)."""
    import pedalboard
    mode = list(FILTER_MODES.values())[int(params["mode"])]
    return pedalboard.LadderFilter(mode=getattr(pedalboard.LadderFilter.Mode, mode),
                                   cutoff_hz=params["cutoff_hz"],
                                   resonance=params["resonance"], drive=params["drive"])


DEVICES: dict[str, _DeviceDef] = {d.spec.type: d for d in [
    _pb(DeviceSpec(type="gain", label="Gain", help="Volume en dB.",
                          params=[_p("gain_db", "Gain", -48, 24, 0, "dB")]),
        _pedalboard("Gain")),
    _pb(DeviceSpec(type="highpass", label="Passe-haut",
                          help="Filtre passe-haut 6 dB/oct : retire ce qui est sous la coupure.",
                          params=[_p("cutoff_frequency_hz", "Coupure", 10, 2000, 30, **_HZ)]),
        _pedalboard("HighpassFilter")),
    _pb(DeviceSpec(type="lowpass", label="Passe-bas",
                          help="Filtre passe-bas 6 dB/oct : retire ce qui est au-dessus de la coupure.",
                          params=[_p("cutoff_frequency_hz", "Coupure", 20, 20000, 200, **_HZ)]),
        _pedalboard("LowpassFilter")),
    _pb(DeviceSpec(type="ladder_lp", label="Ladder LP24",
                          help="Filtre ladder facon Moog, 24 dB/oct, resonance et drive.",
                          params=[_p("cutoff_hz", "Coupure", 20, 20000, 200, **_HZ),
                                  _p("resonance", "Resonance", 0, 1, 0.2),
                                  _p("drive", "Drive", 1, 10, 1)]),
        _pedalboard("LadderFilter", mode="LPF24")),
    _pb(DeviceSpec(type="filter", label="Filtre",
                          help="Filtre ladder multimode facon Auto Filter : type passe-bas, "
                               "passe-haut ou passe-bande, pente 12 ou 24 dB/oct, resonance "
                               "(accent autour de la coupure, sifflement vers 1) et drive.",
                          params=[_p("mode", "Type", 0, len(FILTER_MODES) - 1, 1, step=1,
                                     choices=list(FILTER_MODES)),
                                  _p("cutoff_hz", "Coupure", 20, 20000, 1000, **_HZ),
                                  _p("resonance", "Resonance", 0, 1, 0.3),
                                  _p("drive", "Drive", 1, 10, 1)]),
        _filter),
    _pb(DeviceSpec(type="low_shelf", label="Low shelf",
                          help="Plateau grave : monte ou baisse tout ce qui est sous la coupure.",
                          params=[_p("cutoff_frequency_hz", "Coupure", 20, 1000, 80, **_HZ),
                                  _p("gain_db", "Gain", -24, 24, 0, "dB"),
                                  _p("q", "Q", 0.1, 4, 0.707)]),
        _pedalboard("LowShelfFilter")),
    _pb(DeviceSpec(type="peak", label="Bande (peak)",
                          help="Cloche d'EQ : creuse ou accentue autour de la frequence.",
                          params=[_p("cutoff_frequency_hz", "Frequence", 20, 20000, 100, **_HZ),
                                  _p("gain_db", "Gain", -24, 24, 0, "dB"),
                                  _p("q", "Q", 0.1, 10, 1)]),
        _pedalboard("PeakFilter")),
    _pb(DeviceSpec(type="reverb", label="Reverb",
                          help="Reverb algorithmique (Freeverb). En rumble : 100 % wet, largeur 0.",
                          params=[_p("room_size", "Taille", 0, 1, 0.8),
                                  _p("damping", "Amortissement", 0, 1, 0.5),
                                  _p("wet_level", "Wet", 0, 1, 1),
                                  _p("dry_level", "Dry", 0, 1, 0),
                                  _p("width", "Largeur", 0, 1, 0)]),
        _pedalboard("Reverb")),
    _pb(DeviceSpec(type="distortion", label="Distorsion",
                          help="Saturation tanh : ajoute des harmoniques, rend le grave audible.",
                          params=[_p("drive_db", "Drive", 0, 60, 12, "dB")]),
        _pedalboard("Distortion")),
    _pb(DeviceSpec(type="clipping", label="Clipping",
                          help="Ecretage dur au seuil.",
                          params=[_p("threshold_db", "Seuil", -40, 0, -6, "dB")]),
        _pedalboard("Clipping")),
    _pb(DeviceSpec(type="bitcrush", label="Bitcrush",
                          help="Reduction de resolution : grain numerique.",
                          params=[_p("bit_depth", "Bits", 1, 24, 8, step=1)]),
        _pedalboard("Bitcrush")),
    _pb(DeviceSpec(type="compressor", label="Compresseur",
                          help="Compression classique (pas de sidechain externe : voir Duck).",
                          params=[_p("threshold_db", "Seuil", -60, 0, -18, "dB"),
                                  _p("ratio", "Ratio", 1, 30, 4),
                                  _p("attack_ms", "Attaque", 0.1, 200, 5, "ms", "log"),
                                  _p("release_ms", "Relache", 5, 2000, 100, "ms", "log")]),
        _pedalboard("Compressor")),
    _pb(DeviceSpec(type="limiter", label="Limiteur",
                          help="Limiteur de crete.",
                          params=[_p("threshold_db", "Seuil", -24, 0, -1, "dB"),
                                  _p("release_ms", "Relache", 1, 1000, 100, "ms", "log")]),
        _pedalboard("Limiter")),
    _pb(DeviceSpec(type="delay", label="Delay",
                          help="Echo simple avec reinjection.",
                          params=[_p("delay_seconds", "Temps", 0.001, 2, 0.25, "s", "log"),
                                  _p("feedback", "Feedback", 0, 0.95, 0.3),
                                  _p("mix", "Mix", 0, 1, 0.3)]),
        _pedalboard("Delay")),
    _DeviceDef(DeviceSpec(type="duck", label="Duck (sidechain)",
                          help="Baisse le volume a chaque coup de la source, comme un "
                               "compresseur en sidechain sur le kick : libere la place du kick.",
                          params=[_p("depth_db", "Profondeur", 0, 60, 24, "dB"),
                                  _p("attack_ms", "Attaque", 0, 50, 2, "ms"),
                                  _p("hold_ms", "Tenue", 0, 500, 40, "ms"),
                                  _p("release_ms", "Retour", 1, 2000, 180, "ms", "log")]),
               _duck),
    _DeviceDef(DeviceSpec(type="width", label="Largeur stereo",
                          help="Mid/side : 0 = mono, 1 = inchange. Le sub se garde mono.",
                          params=[_p("width", "Largeur", 0, 1, 0)]),
               _width),
]}


def device_specs() -> list[DeviceSpec]:
    return [d.spec for d in DEVICES.values()]


# ---------------------------------------------------------------------------
# Traitements
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Prepared:
    signal: np.ndarray               # (2, n) : pre-roll + boucle gardee
    loop_start: int                  # debut de la boucle gardee
    loop_len: int
    triggers: np.ndarray
    one_shot: bool = False           # un seul coup : queue coupee au silence + fondu
    ramp: np.ndarray | None = None   # automation (0 -> 1) ; None : lineaire sur la boucle gardee
    cut: bool = False                # arret net en fin de rendu (riser), fondu anti-clic


@dataclass(frozen=True)
class _Treatment:
    spec: TreatmentSpec
    prepare: Callable[[np.ndarray, dict[str, float]], Prepared]
    # le reglage demande-t-il un sample ? (riser sur bruit genere : non)
    needs_source: Callable[[dict[str, float]], bool] = lambda settings: True


def _sequence(source: np.ndarray, hits_per_loop: int, loop_len: int) -> Prepared:
    """Rejoue `source` `hits_per_loop` fois par boucle, pre-roll compris.

    Les coups sont places a l'identique dans chaque boucle (arrondi par
    boucle, pas de pas cumule) : le motif est strictement periodique, donc
    la boucle gardee se raccorde sans clic.
    """
    n_pre = max(1, math.ceil(PREROLL_SECONDS * SR / loop_len))
    total = (n_pre + 1) * loop_len
    in_loop = np.round(np.arange(hits_per_loop) * loop_len / hits_per_loop).astype(int)
    triggers = (np.arange(n_pre + 1)[:, np.newaxis] * loop_len + in_loop).ravel()
    out = np.zeros((2, total), dtype=np.float32)
    for t in triggers:
        seg = source[:, : total - t]
        out[:, t: t + seg.shape[1]] += seg
    # coup de la boucle suivante (non joue) : le duck anticipe creuse aussi la fin
    return Prepared(out, n_pre * loop_len, loop_len, np.append(triggers, total))


TAIL_DB = -60.0          # fin de la queue : sous la crete de 60 dB
FADE_OUT_MS = 20.0       # fondu de sortie d'un rendu « un coup »


def _single(source: np.ndarray, total: int) -> Prepared:
    """Un seul coup en 0, rendu sur `total` echantillons (la longueur choisie)."""
    out = np.zeros((2, total), dtype=np.float32)
    seg = source[:, :total]
    out[:, : seg.shape[1]] = seg
    return Prepared(out, 0, total, np.array([0]), one_shot=True)


def _trim_tail(x: np.ndarray) -> np.ndarray:
    """Coupe la queue sous TAIL_DB et termine par un fondu (cosinus) : pas de clic."""
    env = np.max(np.abs(x), axis=0)
    peak = float(env.max()) if env.size else 0.0
    if peak <= 0:
        return x[:, :1]
    above = np.nonzero(env >= peak * 10 ** (TAIL_DB / 20))[0]
    end = int(above[-1]) + 1
    fade = min(int(FADE_OUT_MS * SR / 1000), end // 4)
    out = x[:, :end].copy()
    if fade > 0:
        out[:, end - fade:] *= (0.5 * (1 + np.cos(np.linspace(0, np.pi, fade)))).astype(np.float32)
    return out


def _cut(x: np.ndarray) -> np.ndarray:
    """Arret net (riser) : seul un fondu de CUT_FADE_MS evite le clic."""
    fade = min(int(CUT_FADE_MS * SR / 1000), x.shape[1])
    out = x.copy()
    if fade > 0:
        out[:, -fade:] *= (0.5 * (1 + np.cos(np.linspace(0, np.pi, fade)))).astype(np.float32)
    return out


def _prepare_rumble(source: np.ndarray, settings: dict[str, float]) -> Prepared:
    if settings["one_shot"]:
        # une track DT2 est monophonique : le coup suivant coupe la queue,
        # inutile de rendre au-dela (1 temps a 150 BPM = 60 / 150 = 0,4 s)
        return _single(source, round(settings["length_beats"] * 60.0 / settings["bpm"] * SR))
    bar = 4 * 60.0 / settings["bpm"] * SR
    hits = int(settings["hits_per_bar"])
    bars = int(settings["bars"])
    return _sequence(source, hits * bars, round(bar * bars))


# --- Riser (8.G) -----------------------------------------------------------

RISER_SOURCES = ["Bruit blanc", "Bruit rose", "Sample"]
NO_SOURCE = np.zeros((2, 0), dtype=np.float32)   # source d'un rendu sans sample
CUT_FADE_MS = 5.0        # arret net du riser : fondu anti-clic seulement
NOISE_SEED = 8           # bruit reproductible : meme preset = meme fichier


def _noise(n: int, pink: bool) -> np.ndarray:
    """Bruit stereo (canaux independants) ; rose = -3 dB/oct par filtrage spectral."""
    rng = np.random.default_rng(NOISE_SEED)
    x = rng.standard_normal((2, n))
    if pink:
        spec = np.fft.rfft(x, axis=1)
        f = np.fft.rfftfreq(n)
        f[0] = f[1] if n > 1 else 1.0
        x = np.fft.irfft(spec / np.sqrt(f), n=n, axis=1)
    return (x / np.max(np.abs(x))).astype(np.float32)


def _shape(n: int, curve: float) -> np.ndarray:
    """Avancement 0 -> 1 sur n echantillons, `t ** curve` (1 = lineaire, 2 = lent puis vite)."""
    return (np.linspace(0.0, 1.0, n) ** curve) if n > 1 else np.ones(n)


def _prepare_riser(source: np.ndarray, settings: dict[str, float]) -> Prepared:
    """Bruit genere ou sample boucle, monte de `pitch_st` demi-tons (varispeed)
    sur `bars` mesures selon la courbe ; la meme courbe pilote l'automation."""
    n = round(settings["bars"] * 4 * 60.0 / settings["bpm"] * SR)
    ramp = _shape(n, settings["curve"])
    rate = 2.0 ** (settings["pitch_st"] * ramp / 12.0)
    phase = np.concatenate([[0.0], np.cumsum(rate[:-1])])
    need = int(math.ceil(phase[-1])) + 2
    mode = int(settings["source"])
    if mode < 2:
        material = _noise(need, pink=mode == 1)
    else:
        material = np.tile(source, (1, need // source.shape[1] + 1))[:, :need]
    idx = np.arange(need)
    signal = np.stack([np.interp(phase, idx, material[c]) for c in range(2)]).astype(np.float32)
    return Prepared(signal, 0, n, np.array([], dtype=int), ramp=ramp, cut=True)


TREATMENTS: dict[str, _Treatment] = {t.spec.id: t for t in [
    _Treatment(TreatmentSpec(
        id="rumble", label="Rumble",
        summary="Grondement grave colle au kick : reverb du kick filtree, saturee, "
                "puis creusee a chaque coup (sidechain).",
        source_hint="kick one-shot (court, attaque nette)",
        settings=[_p("bpm", "Tempo", 60, 220, 150, "BPM", step=1),
                  _p("bars", "Mesures", 1, 8, 1, step=1,
                     help="Longueur de la boucle rendue."),
                  _p("hits_per_bar", "Coups / mesure", 1, 8, 4, step=1,
                     help="4 = four on the floor."),
                  _p("one_shot", "Mode", 0, 1, 0, step=1, choices=["Boucle", "Un coup"],
                     help="Un coup : un seul kick et sa queue, a declencher sur chaque "
                          "kick (doctrine, track 2) ; mesures et coups ignores."),
                  _p("length_beats", "Longueur", 0.25, 4, 1, "temps", step=0.25,
                     help="Mode Un coup : duree du rendu en temps au tempo, puis fondu "
                          "de 20 ms. 1 temps = l'ecart entre deux kicks en 4/4.")],
        notebook="sounddesign/rumble.md",
        code="RM"),                      # -> DRUMS/RM/<sous-dossier du kick>, track 2
        _prepare_rumble),
    _Treatment(TreatmentSpec(
        id="riser", label="Riser",
        summary="Montee de transition (track 15) : bruit ou son tenu dont filtre, volume, "
                "envois et hauteur montent sur N mesures, puis arret net sur le temps.",
        source_hint="aucun (bruit genere) ou son tenu : nappe, drone, bruit du pack",
        settings=[_p("bpm", "Tempo", 60, 220, 150, "BPM", step=1),
                  _p("bars", "Mesures", 1, 16, 4, step=1,
                     help="Duree de la montee ; le rendu s'arrete net a la fin."),
                  _p("source", "Source", 0, len(RISER_SOURCES) - 1, 0, step=1,
                     choices=RISER_SOURCES,
                     help="Bruit genere, ou le sample en cours boucle sur la duree."),
                  _p("pitch_st", "Hauteur", 0, 24, 0, "demi-tons", step=1,
                     help="Montee de hauteur (varispeed) sur la duree, selon la courbe."),
                  _p("curve", "Courbe", 0.25, 4, 2,
                     help="Forme de la montee : 1 = lineaire, 2 = lente puis rapide "
                          "(tension en fin de montee), < 1 = rapide puis plateau.")],
        notebook="sounddesign/riser.md",
        code="FX", sub="RISE"),          # -> FX/RISE, track 15
        _prepare_riser, needs_source=lambda st: int(st["source"]) == 2),
]}


def needs_source(preset: Preset) -> bool:
    """Le rendu de ce preset demande-t-il un sample source ?"""
    treatment = TREATMENTS[preset.treatment]
    return treatment.needs_source(_resolve(treatment.spec.settings, preset.settings, preset.id))


def treatment_specs() -> list[TreatmentSpec]:
    return [t.spec for t in TREATMENTS.values()]


# ---------------------------------------------------------------------------
# Validation et presets
# ---------------------------------------------------------------------------

def _resolve(specs: list[ParamSpec], given: dict[str, float], where: str) -> dict[str, float]:
    """Valeurs completees par les defauts ; leve PresetError si inconnu ou hors bornes."""
    by_name = {s.name: s for s in specs}
    unknown = set(given) - set(by_name)
    if unknown:
        raise PresetError(f"{where} : parametre(s) inconnu(s) {sorted(unknown)}")
    out: dict[str, float] = {}
    for spec in specs:
        value = float(given.get(spec.name, spec.default))
        if not spec.min <= value <= spec.max:
            raise PresetError(f"{where} : {spec.name}={value} hors de "
                              f"[{spec.min}, {spec.max}]")
        if spec.choices is not None and value != int(value):
            raise PresetError(f"{where} : {spec.name}={value} doit etre un index de "
                              f"{spec.choices}")
        out[spec.name] = value
    return out


def _resolve_device(device: Device, where: str) -> dict[str, float]:
    if device.type not in DEVICES:
        raise PresetError(f"{where} : device inconnu {device.type!r}")
    return _resolve(DEVICES[device.type].spec.params, device.params, f"{where} ({device.type})")


def _resolve_end(device: Device, where: str) -> dict[str, float]:
    """Valeurs de fin d'automation, validees : device pedalboard, parametre continu, bornes."""
    if not device.params_end:
        return {}
    defn = DEVICES[device.type]
    where = f"{where} ({device.type}) : automation"
    if defn.plugin is None:
        raise PresetError(f"{where} non supportee par ce device")
    by_name = {s.name: s for s in defn.spec.params}
    for name, value in device.params_end.items():
        spec = by_name.get(name)
        if spec is None:
            raise PresetError(f"{where} : parametre inconnu {name!r}")
        if spec.choices is not None:
            raise PresetError(f"{where} : {name} est un selecteur, non automatisable")
        if not spec.min <= value <= spec.max:
            raise PresetError(f"{where} : {name}={value} hors de [{spec.min}, {spec.max}]")
    return dict(device.params_end)


def validate(preset: Preset) -> None:
    """Leve PresetError a la premiere incoherence ; ne modifie pas le preset."""
    if preset.treatment not in TREATMENTS:
        raise PresetError(f"traitement inconnu {preset.treatment!r}")
    _resolve(TREATMENTS[preset.treatment].spec.settings, preset.settings,
             f"{preset.id} : reglages")
    names = [c.name for c in preset.chains]
    if len(set(names)) != len(names):
        raise PresetError(f"{preset.id} : noms de chaines en double {names}")
    for chain in preset.chains:
        for i, device in enumerate(chain.devices):
            _resolve_device(device, f"{preset.id} : {chain.name}[{i}]")
            _resolve_end(device, f"{preset.id} : {chain.name}[{i}]")
    for i, device in enumerate(preset.master):
        _resolve_device(device, f"{preset.id} : master[{i}]")
        _resolve_end(device, f"{preset.id} : master[{i}]")


def load_presets(treatment: str, root: Path) -> list[Preset]:
    """Presets du traitement (`root/<traitement>/*.json`), valides, tries par id."""
    out = []
    for path in sorted((root / treatment).glob("*.json")):
        try:
            preset = Preset.model_validate_json(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            raise PresetError(f"{path.name} : {exc}") from exc
        if preset.treatment != treatment or preset.id != path.stem:
            raise PresetError(f"{path.name} : id / traitement incoherents avec le chemin")
        validate(preset)
        out.append(preset)
    return out


def save_preset(preset: Preset, root: Path) -> Path:
    """Ecrit (ou remplace) `root/<traitement>/<id>.json` apres validation."""
    validate(preset)
    path = root / preset.treatment / f"{preset.id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(preset.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Rendu
# ---------------------------------------------------------------------------

def load_source(path: Path) -> np.ndarray:
    """Sample en (2, n) float32 a SR (mono duplique, multicanal tronque)."""
    from analyzer.audio_loader import load_audio
    try:
        data, sr = load_audio(path)
    except Exception as exc:   # soundfile / librosa : erreurs heterogenes
        raise SourceError(f"{path} : illisible ({exc})") from exc
    data = np.atleast_2d(data.T) if data.ndim == 2 else data[np.newaxis, :]
    if data.shape[0] == 1:
        data = np.repeat(data, 2, axis=0)
    data = data[:2]
    if sr != SR:
        import librosa
        data = librosa.resample(data, orig_sr=sr, target_sr=SR)
    if data.shape[1] == 0 or not np.any(data):
        raise SourceError(f"{path} : sample vide ou muet")
    return np.ascontiguousarray(data, dtype=np.float32)


AUTOMATION_BLOCK = 256   # echantillons (5 ms a 48 kHz) entre deux mises a jour


def _value_at(spec: ParamSpec, start: float, end: float, t: float) -> float:
    """Interpolation debut -> fin ; geometrique pour un potard log (frequences)."""
    if spec.scale == "log" and start > 0 and end > 0:
        v = start * (end / start) ** t
    else:
        v = start + (end - start) * t
    return round(v / spec.step) * spec.step if spec.step else v


def _automated(device: Device, params: dict[str, float], end: dict[str, float],
               ctx: RenderContext, n: int) -> Processor:
    """Plugin pedalboard rendu par blocs, ses attributs suivant `ctx.ramp`.

    L'etat interne (queues de reverb, filtres) est garde d'un bloc a l'autre
    (`reset=False`) : sans automation, le resultat est identique au rendu
    d'un seul tenant.
    """
    defn = DEVICES[device.type]
    assert defn.plugin is not None
    plugin = defn.plugin(params)
    specs = {s.name: s for s in defn.spec.params}
    ramp = ctx.ramp if ctx.ramp is not None else np.linspace(0.0, 1.0, n)

    def process(x: np.ndarray) -> np.ndarray:
        out = np.empty_like(x)
        for lo in range(0, x.shape[1], AUTOMATION_BLOCK):
            hi = min(x.shape[1], lo + AUTOMATION_BLOCK)
            t = float(ramp[min(lo, len(ramp) - 1)])
            for name, stop in end.items():
                setattr(plugin, name, _value_at(specs[name], params[name], stop, t))
            out[:, lo:hi] = plugin.process(x[:, lo:hi], ctx.sr, reset=lo == 0)  # type: ignore[attr-defined]
        return out
    return process


def _run_devices(devices: list[Device], x: np.ndarray, ctx: RenderContext) -> np.ndarray:
    for device in devices:
        if device.bypass:
            continue
        params = _resolve_device(device, device.type)
        end = _resolve_end(device, device.type)
        if end:
            x = _automated(device, params, end, ctx, x.shape[1])(x)
        else:
            x = DEVICES[device.type].build(params, ctx)(x)
    return x


def render(preset: Preset, source: np.ndarray) -> np.ndarray:
    """Boucle rendue (2, loop_len) a SR ; chaines mutees et devices bypasses ignores."""
    validate(preset)
    treatment = TREATMENTS[preset.treatment]
    settings = _resolve(treatment.spec.settings, preset.settings, preset.id)
    prep = treatment.prepare(source, settings)
    ramp = prep.ramp
    if ramp is None:   # automation lineaire sur la boucle gardee, fixe pendant le pre-roll
        ramp = np.zeros(prep.signal.shape[1])
        ramp[prep.loop_start: prep.loop_start + prep.loop_len] = np.linspace(0.0, 1.0, prep.loop_len)
        ramp[prep.loop_start + prep.loop_len:] = 1.0
    ctx = RenderContext(sr=SR, triggers=prep.triggers, ramp=ramp)

    mix = np.zeros_like(prep.signal)
    for chain in preset.chains:
        if chain.mute:
            continue
        out = _run_devices(chain.devices, prep.signal.copy(), ctx)
        mix += out * np.float32(10.0 ** (chain.gain_db / 20.0))
    mix = _run_devices(preset.master, mix, ctx)

    loop = mix[:, prep.loop_start: prep.loop_start + prep.loop_len]
    if prep.one_shot:
        loop = _trim_tail(loop)
    if prep.cut:
        loop = _cut(loop)
    peak = float(np.max(np.abs(loop))) if loop.size else 0.0
    if preset.output_peak_db is not None and peak > 0:
        loop = loop * np.float32(10.0 ** (preset.output_peak_db / 20.0) / peak)
    return np.ascontiguousarray(loop, dtype=np.float32)


# ---------------------------------------------------------------------------
# Nom DT2 et rangement du rendu (8.E)

NAME_RX = r"^[A-Za-z0-9#][A-Za-z0-9 #._+-]*$"   # nom DT2 saisi : pas de / ni de \\


def propose_name(source_name: str, source_code: str, code: str, bpm: float | None) -> str:
    """Nom DT2 du rendu : code du traitement et tempo a la place du code de la
    source, note / description / pack gardes (`samples.NAME_MAX` au plus).

    `BD C Punch 01 dbr` -> RM a 150 BPM -> `RM 150 C Punch dbr` : le numero de
    variante part d'abord, puis la description est tronquee.
    """
    words = source_name.split()
    body, pack = words[1:-1], words[-1:]
    if source_code in smp.TEMPO and body and body[0].isdigit():
        body = body[1:]                      # tempo de la source remplace par celui du rendu
    head = [code, *([str(round(bpm))] if bpm else [])]
    note = body[:1] if body and re.fullmatch(r"[A-G]#?", body[0]) else []
    rest = body[len(note):]
    name = " ".join([*head, *note, *rest, *pack])
    if len(name) <= smp.NAME_MAX:
        return name
    rest = [w for w in rest if not w.isdigit()] or rest
    fixed = " ".join([*head, *note])
    budget = smp.NAME_MAX - len(fixed) - sum(len(w) + 1 for w in pack) - 1
    desc = " ".join(rest)[:max(budget, 0)].rstrip()
    return " ".join(w for w in [fixed, desc, *pack] if w)


def target(source: str, manifest: smp.Manifest, treatment: str,
           bpm: float | None) -> tuple[str, str]:
    """(nom DT2 propose, sous-dossier) d'un rendu de `source` (relatif a Samples/).

    Le sous-dossier est celui du traitement s'il en fixe un (riser : FX/RISE),
    sinon celui de la source s'il existe pour le code du traitement (kick de
    DRUMS/BD/CLEAN -> DRUMS/RM/CLEAN), sinon la racine. Sans source (bruit
    genere), le nom est `<CODE> <BPM> <traitement> Noise`. Le nom est rendu
    unique dans le dossier cible (rendus deja verses compris).
    """
    spec = TREATMENTS[treatment].spec
    code = spec.code
    if not source:   # rendu sans sample (bruit genere) : `FX 150 Rise Noise`
        folder = smp.folder_of("", code, spec.sub)
        taken = {e.name for e in manifest.entries if e.folder == folder}
        head = " ".join([code, *([str(round(bpm))] if bpm else [])])
        return smp.unique_name(f"{head} {spec.label[:4]} Noise", taken), spec.sub
    entry = next((e for e in manifest.entries if e.source == source), None)
    reserve = next((r for r in manifest.reserve if r.source == source), None)
    found = entry or reserve
    src_code = found.code if found else (smp.code_of(source, None) or "")
    src_sub = found.sub if found else ""
    sub = spec.sub or (src_sub if smp.has_sub(code, src_sub) else "")
    pack = found.pack if found else smp.pack_of(source)
    src_name = entry.name if entry else smp.short_name(source, src_code or code, pack)
    name = propose_name(src_name, src_code, code, bpm)
    folder = smp.folder_of("", code, sub)
    taken = {e.name for e in manifest.entries if e.folder == folder}
    return smp.unique_name(name, taken), sub


def output_name(name: str, preset: Preset) -> str:
    """`<nom DT2> <hash>.wav` : meme nom + meme preset effectif = meme fichier."""
    digest = hashlib.sha1(preset.model_dump_json().encode()).hexdigest()[:6]
    return f"{name} {digest}.wav"


def write_render(audio: np.ndarray, source_label: str, preset: Preset, out_root: Path,
                 name: str, sub: str = "") -> RenderRecord:
    """Ecrit `<out_root>/<traitement>/<nom> <hash>.wav` (24 bits) et son sidecar `.json`."""
    import soundfile as sf
    if not re.fullmatch(NAME_RX, name) or len(name) > smp.NAME_MAX:
        raise PresetError(f"nom DT2 invalide (1 a {smp.NAME_MAX} caracteres, sans /) : {name!r}")
    path = out_root / preset.treatment / output_name(name, preset)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), audio.T, SR, subtype="PCM_24")
    record = RenderRecord(
        file=path.relative_to(out_root).as_posix(), source=source_label, preset=preset,
        sr=SR, seconds=round(audio.shape[1] / SR, 4),
        created_at=datetime.now().isoformat(timespec="seconds"), name=name, sub=sub)
    path.with_suffix(".json").write_text(record.model_dump_json(indent=2) + "\n",
                                         encoding="utf-8")
    return record


def encode_wav(audio: np.ndarray) -> bytes:
    """Rendu en WAV 24 bits en memoire (ecoute sans ecriture disque)."""
    import io

    import soundfile as sf
    buf = io.BytesIO()
    sf.write(buf, audio.T, SR, format="WAV", subtype="PCM_24")
    return buf.getvalue()


def list_renders(out_root: Path, treatment: str | None = None) -> list[RenderRecord]:
    """Rendus ecrits (sidecars lisibles dont le wav existe), du plus recent au plus ancien."""
    pattern = f"{treatment}/*.json" if treatment else "*/*.json"
    records = []
    for sidecar in out_root.glob(pattern):
        try:
            record = RenderRecord.model_validate_json(sidecar.read_text(encoding="utf-8"))
        except ValueError:
            continue   # sidecar etranger ou corrompu : ignore, pas bloquant pour la liste
        if (out_root / record.file).is_file():
            records.append(record)
    return sorted(records, key=lambda r: (r.created_at, r.file), reverse=True)


def mark_versed(records: list[RenderRecord], samples_root: Path) -> list[RenderRecord]:
    """Renseigne `versed` pour les rendus deja copies dans le pack."""
    for record in records:
        key = verse_key(record)
        record.versed = key if (samples_root / key).is_file() else None
    return records


VERSE_PACK = "SoundDesign"   # pack des rendus verses sous <MEDIA>/Samples (Phase 8.D)


def verse_key(record: RenderRecord) -> str:
    """Cle du manifeste (relative a Samples/) : `SoundDesign/<traitement>/<fichier>`."""
    return f"{VERSE_PACK}/{record.file}"


def verse(record: RenderRecord, out_root: Path, samples_root: Path,
          overrides: dict[str, smp.Override]) -> str:
    """Copie le rendu dans le pack SoundDesign et le range par override.

    Seule ecriture sous `<MEDIA>/Samples` (lecture seule sinon). L'override
    (code du traitement, sous-dossier, nom DT2) range le fichier a la
    reanalyse, sans dependre de son nom (DRUMS/RM/CLEAN). Idempotent : un
    fichier deja verse a l'identique n'est pas recopie. `overrides` est
    modifie en place, a enregistrer par l'appelant.
    """
    import shutil
    if not record.name:
        raise PresetError(f"rendu sans nom DT2 (anterieur a 8.E) : {record.file}, a re-rendre")
    key = verse_key(record)
    src = out_root / record.file
    dest = samples_root / key
    if not (dest.exists() and dest.stat().st_size == src.stat().st_size):
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    smp.set_override(overrides, key, code=TREATMENTS[record.preset.treatment].spec.code,
                     sub=record.sub, name=record.name)
    return key


def with_overrides(preset: Preset, settings: dict[str, float], mute: list[str],
                   bypass: list[tuple[str, int]]) -> Preset:
    """Copie du preset avec reglages, mutes de chaines et bypass (`chaine`, index) appliques."""
    data = json.loads(preset.model_dump_json())
    data["settings"].update(settings)
    chains = {c["name"]: c for c in data["chains"]}
    for name in mute:
        if name not in chains:
            raise PresetError(f"chaine inconnue {name!r} (connues : {sorted(chains)})")
        chains[name]["mute"] = True
    for name, index in bypass:
        devices = data["master"] if name == "master" else chains.get(name, {}).get("devices")
        if devices is None or not 0 <= index < len(devices):
            raise PresetError(f"device introuvable {name}:{index}")
        devices[index]["bypass"] = True
    updated = Preset.model_validate(data)
    validate(updated)
    return updated

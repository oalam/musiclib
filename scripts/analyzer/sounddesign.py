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
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

import numpy as np
from pydantic import BaseModel, Field

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
    verse_words: str                 # mots du nom verse qui rangent le rendu (samples.code_of)


class RenderRecord(BaseModel):
    """Sidecar d'un rendu : de quoi le rejouer a l'identique."""

    file: str                        # relatif a SOUNDDESIGN_OUT_DIR
    source: str
    preset: Preset                   # snapshot effectif (overrides compris)
    sr: int
    seconds: float
    created_at: str
    versed: str | None = None        # cle du manifeste si verse dans le pack (rempli a la lecture)


# ---------------------------------------------------------------------------
# Catalogue des devices
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RenderContext:
    sr: int
    triggers: np.ndarray             # positions (echantillons) des coups de la source


@dataclass(frozen=True)
class _DeviceDef:
    spec: DeviceSpec
    build: Callable[[dict[str, float], RenderContext], Processor]


def _p(name: str, label: str, lo: float, hi: float, default: float, unit: str = "",
       scale: Literal["lin", "log"] = "lin", step: float | None = None,
       help: str = "", choices: list[str] | None = None) -> ParamSpec:
    return ParamSpec(name=name, label=label, min=lo, max=hi, default=default,
                     unit=unit, scale=scale, step=step, help=help, choices=choices)


def _pedalboard(cls_name: str, mode: str | None = None
                ) -> Callable[[dict[str, float], RenderContext], Processor]:
    """Fabrique d'un plugin pedalboard ; les noms de parametres sont ceux de pedalboard.

    `mode` fige une valeur d'enum (ex. `LPF24` du ladder), non exposee en potard.
    """
    def build(params: dict[str, float], ctx: RenderContext) -> Processor:
        import pedalboard
        cls = getattr(pedalboard, cls_name)
        kwargs: dict[str, object] = dict(params)
        if mode is not None:
            kwargs["mode"] = getattr(cls.Mode, mode)
        plugin = cls(**kwargs)
        return lambda x: np.asarray(plugin(x, ctx.sr), dtype=np.float32)
    return build


def _duck(params: dict[str, float], ctx: RenderContext) -> Processor:
    """Sidechain sur les coups de la source : creux de `depth_db` a chaque coup."""
    sr = ctx.sr
    attack = max(1, int(params["attack_ms"] * sr / 1000))
    hold = int(params["hold_ms"] * sr / 1000)
    release = max(1, int(params["release_ms"] * sr / 1000))
    shape = np.concatenate([np.linspace(0.0, 1.0, attack, endpoint=False),
                            np.ones(hold), np.linspace(1.0, 0.0, release)])

    def process(x: np.ndarray) -> np.ndarray:
        n = x.shape[1]
        amount = np.zeros(n)
        for t in ctx.triggers:
            seg = shape[: max(0, n - int(t))]
            np.maximum(amount[int(t): int(t) + len(seg)], seg,
                       out=amount[int(t): int(t) + len(seg)])
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


def _filter(params: dict[str, float], ctx: RenderContext) -> Processor:
    """LadderFilter dont le mode vient du parametre `mode` (index de FILTER_MODES)."""
    import pedalboard
    mode = list(FILTER_MODES.values())[int(params["mode"])]
    plugin = pedalboard.LadderFilter(mode=getattr(pedalboard.LadderFilter.Mode, mode),
                                     cutoff_hz=params["cutoff_hz"],
                                     resonance=params["resonance"], drive=params["drive"])
    return lambda x: np.asarray(plugin(x, ctx.sr), dtype=np.float32)


DEVICES: dict[str, _DeviceDef] = {d.spec.type: d for d in [
    _DeviceDef(DeviceSpec(type="gain", label="Gain", help="Volume en dB.",
                          params=[_p("gain_db", "Gain", -48, 24, 0, "dB")]),
               _pedalboard("Gain")),
    _DeviceDef(DeviceSpec(type="highpass", label="Passe-haut",
                          help="Filtre passe-haut 6 dB/oct : retire ce qui est sous la coupure.",
                          params=[_p("cutoff_frequency_hz", "Coupure", 10, 2000, 30, **_HZ)]),
               _pedalboard("HighpassFilter")),
    _DeviceDef(DeviceSpec(type="lowpass", label="Passe-bas",
                          help="Filtre passe-bas 6 dB/oct : retire ce qui est au-dessus de la coupure.",
                          params=[_p("cutoff_frequency_hz", "Coupure", 20, 20000, 200, **_HZ)]),
               _pedalboard("LowpassFilter")),
    _DeviceDef(DeviceSpec(type="ladder_lp", label="Ladder LP24",
                          help="Filtre ladder facon Moog, 24 dB/oct, resonance et drive.",
                          params=[_p("cutoff_hz", "Coupure", 20, 20000, 200, **_HZ),
                                  _p("resonance", "Resonance", 0, 1, 0.2),
                                  _p("drive", "Drive", 1, 10, 1)]),
               _pedalboard("LadderFilter", mode="LPF24")),
    _DeviceDef(DeviceSpec(type="filter", label="Filtre",
                          help="Filtre ladder multimode facon Auto Filter : type passe-bas, "
                               "passe-haut ou passe-bande, pente 12 ou 24 dB/oct, resonance "
                               "(accent autour de la coupure, sifflement vers 1) et drive.",
                          params=[_p("mode", "Type", 0, len(FILTER_MODES) - 1, 1, step=1,
                                     choices=list(FILTER_MODES)),
                                  _p("cutoff_hz", "Coupure", 20, 20000, 1000, **_HZ),
                                  _p("resonance", "Resonance", 0, 1, 0.3),
                                  _p("drive", "Drive", 1, 10, 1)]),
               _filter),
    _DeviceDef(DeviceSpec(type="low_shelf", label="Low shelf",
                          help="Plateau grave : monte ou baisse tout ce qui est sous la coupure.",
                          params=[_p("cutoff_frequency_hz", "Coupure", 20, 1000, 80, **_HZ),
                                  _p("gain_db", "Gain", -24, 24, 0, "dB"),
                                  _p("q", "Q", 0.1, 4, 0.707)]),
               _pedalboard("LowShelfFilter")),
    _DeviceDef(DeviceSpec(type="peak", label="Bande (peak)",
                          help="Cloche d'EQ : creuse ou accentue autour de la frequence.",
                          params=[_p("cutoff_frequency_hz", "Frequence", 20, 20000, 100, **_HZ),
                                  _p("gain_db", "Gain", -24, 24, 0, "dB"),
                                  _p("q", "Q", 0.1, 10, 1)]),
               _pedalboard("PeakFilter")),
    _DeviceDef(DeviceSpec(type="reverb", label="Reverb",
                          help="Reverb algorithmique (Freeverb). En rumble : 100 % wet, largeur 0.",
                          params=[_p("room_size", "Taille", 0, 1, 0.8),
                                  _p("damping", "Amortissement", 0, 1, 0.5),
                                  _p("wet_level", "Wet", 0, 1, 1),
                                  _p("dry_level", "Dry", 0, 1, 0),
                                  _p("width", "Largeur", 0, 1, 0)]),
               _pedalboard("Reverb")),
    _DeviceDef(DeviceSpec(type="distortion", label="Distorsion",
                          help="Saturation tanh : ajoute des harmoniques, rend le grave audible.",
                          params=[_p("drive_db", "Drive", 0, 60, 12, "dB")]),
               _pedalboard("Distortion")),
    _DeviceDef(DeviceSpec(type="clipping", label="Clipping",
                          help="Ecretage dur au seuil.",
                          params=[_p("threshold_db", "Seuil", -40, 0, -6, "dB")]),
               _pedalboard("Clipping")),
    _DeviceDef(DeviceSpec(type="bitcrush", label="Bitcrush",
                          help="Reduction de resolution : grain numerique.",
                          params=[_p("bit_depth", "Bits", 1, 24, 8, step=1)]),
               _pedalboard("Bitcrush")),
    _DeviceDef(DeviceSpec(type="compressor", label="Compresseur",
                          help="Compression classique (pas de sidechain externe : voir Duck).",
                          params=[_p("threshold_db", "Seuil", -60, 0, -18, "dB"),
                                  _p("ratio", "Ratio", 1, 30, 4),
                                  _p("attack_ms", "Attaque", 0.1, 200, 5, "ms", "log"),
                                  _p("release_ms", "Relache", 5, 2000, 100, "ms", "log")]),
               _pedalboard("Compressor")),
    _DeviceDef(DeviceSpec(type="limiter", label="Limiteur",
                          help="Limiteur de crete.",
                          params=[_p("threshold_db", "Seuil", -24, 0, -1, "dB"),
                                  _p("release_ms", "Relache", 1, 1000, 100, "ms", "log")]),
               _pedalboard("Limiter")),
    _DeviceDef(DeviceSpec(type="delay", label="Delay",
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


@dataclass(frozen=True)
class _Treatment:
    spec: TreatmentSpec
    prepare: Callable[[np.ndarray, dict[str, float]], Prepared]


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
    return Prepared(out, n_pre * loop_len, loop_len, triggers)


def _prepare_rumble(source: np.ndarray, settings: dict[str, float]) -> Prepared:
    bar = 4 * 60.0 / settings["bpm"] * SR
    hits = int(settings["hits_per_bar"])
    bars = int(settings["bars"])
    return _sequence(source, hits * bars, round(bar * bars))


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
                     help="4 = four on the floor.")],
        notebook="sounddesign/rumble.md",
        verse_words="bass loop"),        # -> LOOPS/BL (tempo garde dans le nom DT2)
        _prepare_rumble),
]}


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
    for i, device in enumerate(preset.master):
        _resolve_device(device, f"{preset.id} : master[{i}]")


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


def _run_devices(devices: list[Device], x: np.ndarray, ctx: RenderContext) -> np.ndarray:
    for device in devices:
        if device.bypass:
            continue
        params = _resolve_device(device, device.type)
        x = DEVICES[device.type].build(params, ctx)(x)
    return x


def render(preset: Preset, source: np.ndarray) -> np.ndarray:
    """Boucle rendue (2, loop_len) a SR ; chaines mutees et devices bypasses ignores."""
    validate(preset)
    treatment = TREATMENTS[preset.treatment]
    settings = _resolve(treatment.spec.settings, preset.settings, preset.id)
    prep = treatment.prepare(source, settings)
    ctx = RenderContext(sr=SR, triggers=prep.triggers)

    mix = np.zeros_like(prep.signal)
    for chain in preset.chains:
        if chain.mute:
            continue
        out = _run_devices(chain.devices, prep.signal.copy(), ctx)
        mix += out * np.float32(10.0 ** (chain.gain_db / 20.0))
    mix = _run_devices(preset.master, mix, ctx)

    loop = mix[:, prep.loop_start: prep.loop_start + prep.loop_len]
    peak = float(np.max(np.abs(loop))) if loop.size else 0.0
    if preset.output_peak_db is not None and peak > 0:
        loop = loop * np.float32(10.0 ** (preset.output_peak_db / 20.0) / peak)
    return np.ascontiguousarray(loop, dtype=np.float32)


def output_name(source: Path, preset: Preset) -> str:
    """Nom stable : meme source + meme preset effectif = meme fichier (rejouable)."""
    from library_md import slugify
    digest = hashlib.sha1(preset.model_dump_json().encode()).hexdigest()[:6]
    bpm = preset.settings.get("bpm")
    tempo = f"_{int(bpm)}bpm" if bpm is not None else ""
    return f"{slugify(source.stem)}__{preset.id}{tempo}_{digest}.wav"


def write_render(audio: np.ndarray, source: Path, source_label: str, preset: Preset,
                 out_root: Path) -> RenderRecord:
    """Ecrit `<out_root>/<traitement>/<nom>.wav` (24 bits) et son sidecar `.json`."""
    import soundfile as sf
    path = out_root / preset.treatment / output_name(source, preset)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), audio.T, SR, subtype="PCM_24")
    record = RenderRecord(
        file=path.relative_to(out_root).as_posix(), source=source_label, preset=preset,
        sr=SR, seconds=round(audio.shape[1] / SR, 4),
        created_at=datetime.now().isoformat(timespec="seconds"))
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
    """Cle du manifeste (relative a Samples/) d'un rendu verse.

    Nom sans le sample source (un kick dans le nom le rangerait en BD) :
    `<traitement> <mots de rangement> <preset> <bpm>bpm <hash>.wav`.
    """
    spec = TREATMENTS[record.preset.treatment].spec
    stem = Path(record.file).stem
    digest = stem.rsplit("_", 1)[-1]
    bpm = record.preset.settings.get("bpm")
    tempo = f" {int(bpm)}bpm" if bpm is not None else ""
    return f"{VERSE_PACK}/{spec.id}/{spec.id} {spec.verse_words} {record.preset.id}{tempo} {digest}.wav"


def verse(record: RenderRecord, out_root: Path, samples_root: Path) -> str:
    """Copie le rendu dans le pack SoundDesign de la bibliotheque de samples.

    Seule ecriture sous `<MEDIA>/Samples` (lecture seule sinon). Idempotent :
    un fichier deja verse a l'identique n'est pas recopie. La reanalyse de la
    bibliotheque le classe ensuite comme un sample de pack.
    """
    import shutil
    key = verse_key(record)
    src = out_root / record.file
    dest = samples_root / key
    if dest.exists() and dest.stat().st_size == src.stat().st_size:
        return key
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
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

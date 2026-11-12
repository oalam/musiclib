"""Configuration matérielle et dispositions (`config/default.yaml`), validée par Pydantic."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator

from mk_brain.arp import (
    GATE_MAX,
    GATE_MIN,
    MAX_OCTAVES,
    MOTIF_NAME_MAX,
    MOTIF_OFF,
    PROGRESSION_MAX,
    PROGRESSION_OFF,
    ArpBars,
    ArpChord,
    ArpInversion,
    ArpOrder,
    parse_motif,
)
from mk_brain.repeat import DIVISION_TICKS

DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "config" / "default.yaml"

Byte = Annotated[int, Field(ge=0, le=255)]
RGB = tuple[Byte, Byte, Byte]


class ConfigError(Exception):
    """Fichier de configuration illisible ou invalide."""


class MidiConfig(BaseModel):
    port_hint: str = "Digitakt"
    auto_channel: int = Field(16, ge=1, le=16)
    program_channel: int = Field(10, ge=1, le=16)  # canal des Program Change de la DT2
    # DT2 OUTPUT CH = TRACK CH : ses boutons sortent sur le canal de la track active, le Pi
    # suit la track (vérifié le 2026-11-09) ; False = AUTO CH, valeur à la track de la MK2
    knobs_on_track_channel: bool = True
    # FX CONTROL CH de la DT2 : délai, reverb, chorus, compresseur (encodeurs `fx`)
    fx_channel: int = Field(9, ge=1, le=16)


class VelocityConfig(BaseModel):
    window_ms: float = Field(2.0, ge=0)
    threshold: int = Field(200, ge=0, lt=4095)
    full_scale: int = Field(2500, gt=0, le=4095)
    gamma: float = Field(0.6, gt=0)
    min: int = Field(1, ge=1, le=127)
    max: int = Field(127, ge=1, le=127)

    @model_validator(mode="after")
    def _bounds(self) -> VelocityConfig:
        if self.full_scale <= self.threshold:
            raise ValueError("full_scale doit dépasser threshold")
        if self.min > self.max:
            raise ValueError("min doit être ≤ max")
        return self


class LedConfig(BaseModel):
    dim: float = Field(0.15, ge=0, le=1)
    selected: float = Field(0.5, ge=0, le=1)  # live : pad de la track sélectionnée, au repos
    phrase: RGB = (0, 255, 0)  # LED GROUP du compteur de phrases
    phrase_warn: RGB = (255, 110, 0)  # bloc en cours, dernière mesure avant un cap
    bank: RGB = (255, 255, 255)  # design : LED GROUP de la banque choisie (2026-11-09)
    perform_idle: RGB = (0, 0, 40)  # SOLO : pad hors du groupe, bleu très faible (2026-11-10)
    perform_on: RGB = (0, 255, 0)  # SOLO : pad du groupe, vert vif
    preset: RGB = (255, 255, 255)  # ARPG, PATTERN tenu : emplacement de preset occupé (slice 14)


class AftertouchConfig(BaseModel):
    """Pression d'un pad tenu → aftertouch de canal de sa track (slice 10)."""

    delay_ms: float = Field(120.0, ge=0)  # après la note : la frappe elle-même n'en envoie pas
    threshold: int = Field(2350, ge=0, lt=4095)  # pression d'un pad simplement tenu, sur 4095
    full_scale: int = Field(3000, gt=0, le=4095)  # pression qui donne 127
    interval_ms: float = Field(10.0, ge=0)  # au plus un message par canal sur ce délai

    @model_validator(mode="after")
    def _bounds(self) -> AftertouchConfig:
        if self.full_scale <= self.threshold:
            raise ValueError("aftertouch : full_scale doit dépasser threshold")
        return self


class PlayConfig(BaseModel):
    """Réglages de départ de la session ; modifiables à la MK2, jamais réécrits."""

    quantize: Literal["off", "1/16", "1/8"] = "1/16"
    swing: int = Field(50, ge=50, le=75)
    repeat: Literal["1/4", "1/8", "1/8T", "1/16", "1/16T", "1/32", "1/32T", "1/64"] = "1/16"
    phrase: Literal[32, 64] = 32  # longueur de phrase sans banque du projet (6.B)
    horizon_ms: float = Field(20.0, gt=0)  # envoi confié à l'ordonnanceur ce délai avant la cible
    tap_debounce_ms: float = Field(150.0, ge=0)  # SOLO, MUTE, SELECT : rebond ignoré


PRESET_SLOTS = 16  # un emplacement par pad (slice 14)


class ArpPreset(BaseModel):
    """Preset d'arpège (slice 13) : les cinq réglages rappelés d'un coup."""

    order: ArpOrder
    octaves: int = Field(ge=1, le=MAX_OCTAVES)
    gate: int = Field(ge=GATE_MIN, le=GATE_MAX)
    division: str
    motif: str = MOTIF_OFF
    chord: ArpChord = "off"  # slice 15 ; absent d'un preset d'avant : pas d'accord
    progression: str = PROGRESSION_OFF  # slice 16, idem
    bars: ArpBars = "1"
    inversion: ArpInversion = "off"  # slice 21, idem

    @field_validator("division")
    @classmethod
    def _division(cls, division: str) -> str:
        if division not in DIVISION_TICKS:
            raise ValueError(f"division {division!r} inconnue ({', '.join(DIVISION_TICKS)})")
        return division


class ArpConfig(BaseModel):
    """Arpégiateur (slice 11) : réglages de départ ; modifiables à la MK2, jamais réécrits."""

    order: ArpOrder = "up"
    octaves: int = Field(1, ge=1, le=MAX_OCTAVES)
    gate: int = Field(50, ge=GATE_MIN, le=GATE_MAX)  # durée d'une note, en % de la division
    # course des encodeurs de la config (PATTERN tenu), en unités brutes par valeur : bien plus
    # longue que celle d'un CC (`encoders.raw_per_step`), ces réglages n'ont que 3 à 19 valeurs
    raw_per_choice: int = Field(24, ge=1)  # ORD, OCT, MOT, INV, CHD, PRG et BAR
    raw_per_gate_step: int = Field(12, ge=1)  # GATE, par pas de 5 %
    # motifs (slice 12) : nom → 16 pas (x note, X accent, . silence, - liée), ordre du fichier
    motifs: dict[str, str] = {}
    motif: str = MOTIF_OFF  # motif de départ : un nom de `motifs`, ou OFF
    chord: ArpChord = "off"  # accord de départ (slice 15) : off, tri, 7th, sus2, sus4, pwr
    # progressions (slice 16) : nom → degrés 1-7 depuis le pad tenu, ordre du fichier
    progressions: dict[str, list[int]] = {}
    progression: str = PROGRESSION_OFF  # progression de départ : un nom, ou OFF
    bars: ArpBars = "1"  # durée de chaque accord, en mesures
    inversion: ArpInversion = "off"  # renversement de départ (slice 21) : off, 1, 2, fix

    @field_validator("progressions")
    @classmethod
    def _progressions(cls, progressions: dict[str, list[int]]) -> dict[str, list[int]]:
        for name, degrees in progressions.items():
            if name == PROGRESSION_OFF or not 1 <= len(name) <= MOTIF_NAME_MAX:
                raise ValueError(
                    f"progression {name!r} : nom de 1 à {MOTIF_NAME_MAX} caractères, OFF réservé"
                )
            if not 1 <= len(degrees) <= PROGRESSION_MAX or any(not 1 <= d <= 7 for d in degrees):
                raise ValueError(f"progression {name!r} : 1 à {PROGRESSION_MAX} degrés, de 1 à 7")
        return progressions

    @property
    def progression_names(self) -> list[str]:
        """Choix de l'encodeur PRG : OFF, puis les progressions dans l'ordre du fichier."""
        return [PROGRESSION_OFF, *self.progressions]

    def knows(self, preset: ArpPreset) -> bool:
        """Motif et progression du preset présents dans la config."""
        return (preset.motif == MOTIF_OFF or preset.motif in self.motifs) and (
            preset.progression in self.progression_names
        )

    unaccented: int = Field(70, ge=1, le=100)  # vélocité d'un pas `x`, en % de celle du pad
    presets: dict[str, ArpPreset] = {}  # slice 13 : nom → réglages, ordre du fichier

    @field_validator("motifs")
    @classmethod
    def _motifs(cls, motifs: dict[str, str]) -> dict[str, str]:
        for name in motifs:
            if name == MOTIF_OFF or not 1 <= len(name) <= MOTIF_NAME_MAX:
                raise ValueError(
                    f"motif {name!r} : nom de 1 à {MOTIF_NAME_MAX} caractères, {MOTIF_OFF} réservé"
                )
        return {name: parse_motif(text) for name, text in motifs.items()}

    @model_validator(mode="after")
    def _motif(self) -> ArpConfig:
        if self.motif != MOTIF_OFF and self.motif not in self.motifs:
            raise ValueError(f"arp.motif {self.motif!r} : absent de arp.motifs")
        if self.progression not in self.progression_names:
            raise ValueError(f"arp.progression {self.progression!r} : absente de arp.progressions")
        for name, preset in self.presets.items():
            if not 1 <= len(name) <= MOTIF_NAME_MAX:
                raise ValueError(f"preset {name!r} : nom de 1 à {MOTIF_NAME_MAX} caractères")
            if re.fullmatch(r"U\d\d", name):
                raise ValueError(f"preset {name!r} : U01 à U16 réservés aux presets sauvés")
            if not self.knows(preset):
                raise ValueError(f"preset {name!r} : motif ou progression absents de la config")
        if len(self.presets) > PRESET_SLOTS:
            raise ValueError(f"arp.presets : {len(self.presets)} presets, {PRESET_SLOTS} au plus")
        return self

    @property
    def motif_names(self) -> list[str]:
        """Choix de l'encodeur MOT : OFF, puis les motifs dans l'ordre du fichier."""
        return [MOTIF_OFF, *self.motifs]


PITCH_BEND = 128  # identifiant du pitch bend parmi les paramètres (hors des CC 0-127)


class Encoder(BaseModel):
    name: str = Field(max_length=4)
    cc: int | None = Field(None, ge=0, le=127)
    pitchbend: bool = False  # message pitch bend au lieu d'un CC
    bipolar: bool = False  # jauge depuis le centre (pan, tune, pitch bend)
    fx: bool = False  # réglage global de la DT2 : CC sur `midi.fx_channel`, pas sur la track
    max: int = Field(127, ge=1, le=127)  # plafond des valeurs envoyées par l'encodeur

    @model_validator(mode="after")
    def _target(self) -> Encoder:
        if (self.cc is None) == (not self.pitchbend):
            raise ValueError(f"encodeur {self.name} : un CC ou pitchbend, pas les deux")
        if self.fx and self.cc is None:
            raise ValueError(f"encodeur {self.name} : fx demande un CC")
        return self

    @property
    def param(self) -> int:
        """CC, ou PITCH_BEND."""
        return PITCH_BEND if self.cc is None else self.cc


class EncoderAccel(BaseModel):
    """Accélération des encodeurs de CC : geste rapide, course courte (SPEC, Encodeurs)."""

    raw_per_step: int = Field(4, ge=1)  # unités brutes par cran de CC à pleine vitesse
    slow: float = Field(300.0, gt=0)  # unités brutes / s : en dessous, pas lent
    fast: float = Field(1500.0, gt=0)  # au-dessus, pas rapide ; entre les deux, interpolation
    window_ms: float = Field(40.0, gt=0)  # fenêtre de mesure de la vitesse

    @model_validator(mode="after")
    def _ordered(self) -> EncoderAccel:
        if self.fast <= self.slow:
            raise ValueError("encoders.accel : fast doit dépasser slow")
        return self


class EncodersConfig(BaseModel):
    """Pages de 8 encodeurs, les mêmes pour toutes les tracks (SPEC, Encodeurs)."""

    pages: list[list[Encoder]]
    mute_cc: int = Field(94, ge=0, le=127)
    # unités brutes de la MK2 par cran de CC ; 15 : potard DT2, 17 crans par quart de tour
    # avec `accel` : pas du geste lent
    raw_per_step: int = Field(15, ge=1)
    accel: EncoderAccel | None = None  # absent : course fixe

    @model_validator(mode="after")
    def _fast_is_shorter(self) -> EncodersConfig:
        if self.accel is not None and self.accel.raw_per_step > self.raw_per_step:
            raise ValueError("encoders.accel.raw_per_step : au plus encoders.raw_per_step")
        return self

    @field_validator("pages")
    @classmethod
    def _eight(cls, v: list[list[Encoder]]) -> list[list[Encoder]]:
        if not v or any(len(p) != 8 for p in v):
            raise ValueError("encoders.pages : au moins une page, 8 encodeurs par page")
        return v


class Roles(BaseModel):
    tonique: RGB
    tierce: RGB
    quinte: RGB


Family = Literal["chromatique", "gamme"]
Mode = Literal[
    "eolien",
    "phrygien",
    "dorien",
    "mineur-harmonique",
    "phrygien-dominant",
    "penta-mineure",
    "chromatique",
]  # modes d'une banque de projet (SPEC, Formalisme du front matter)


class Layout(BaseModel):
    # groupe historique (B-H, template DT2 Pads) ; None pour les gammes ajoutées ensuite
    group: Literal["B", "C", "D", "E", "F", "G", "H"] | None = None
    name: str
    kind: Literal["chromatique", "gamme"]
    family: Family
    mode: Mode | None = None  # mode d'une banque de projet que cette disposition joue
    base: int = Field(60, ge=0, le=127)
    intervals: list[int] = []

    @model_validator(mode="after")
    def _scale(self) -> Layout:
        if self.kind == "gamme":
            iv = self.intervals
            if not iv or iv[0] != 0 or iv != sorted(set(iv)) or iv[-1] > 11:
                raise ValueError(f"{self.name} : intervalles 0-11 croissants depuis 0")
        return self


class MpcPad(BaseModel):
    """Un pad du mode MPC (slice 8) : la tranche `note` sur le canal de la track `track`."""

    pad: int = Field(ge=1, le=16)
    track: int = Field(ge=1, le=16)
    note: int = Field(ge=0, le=127)
    label: str = Field(max_length=4)
    color: RGB


class Config(BaseModel):
    midi: MidiConfig = MidiConfig()
    velocity: VelocityConfig = VelocityConfig()
    aftertouch: AftertouchConfig = AftertouchConfig()
    leds: LedConfig = LedConfig()
    play: PlayConfig = PlayConfig()
    arp: ArpConfig = ArpConfig()
    encoders: EncodersConfig
    roles: Roles
    families: dict[Family, RGB]
    track_colors: dict[int, RGB]
    track_names: dict[int, Annotated[str, Field(max_length=5)]] = {}
    layouts: list[Layout]
    mpc: list[MpcPad]

    @field_validator("track_names")
    @classmethod
    def _names(cls, v: dict[int, str]) -> dict[int, str]:
        if not set(v) <= set(range(1, 17)):
            raise ValueError("track_names : tracks de 1 à 16")
        return v

    @field_validator("track_colors")
    @classmethod
    def _tracks(cls, v: dict[int, RGB]) -> dict[int, RGB]:
        if sorted(v) != list(range(1, 17)):
            raise ValueError("track_colors : les 16 tracks, de 1 à 16")
        return v

    @model_validator(mode="after")
    def _groups(self) -> Config:
        if [lay.group for lay in self.layouts[:7]] != list("BCDEFGH"):
            raise ValueError("layouts : un par groupe, dans l'ordre B-H, en tête")
        if any(lay.group is not None for lay in self.layouts[7:]):
            raise ValueError("layouts : au-delà de H, gammes sans groupe")
        names = [lay.name for lay in self.layouts]
        if len(set(names)) != len(names):
            raise ValueError("layouts : noms en double")
        if sorted(p.pad for p in self.mpc) != list(range(1, 17)):
            raise ValueError("mpc : les 16 pads, une fois chacun")
        auto = [p.pad for p in self.mpc if p.track == self.midi.auto_channel]
        if auto:
            raise ValueError(f"mpc : pads {auto} sur la track de l'AUTO CHANNEL")
        missing = {lay.family for lay in self.layouts} - set(self.families)
        if missing:
            raise ValueError(f"families : couleur manquante pour {sorted(missing)}")
        modes = [lay.mode for lay in self.layouts if lay.mode is not None]
        if len(set(modes)) != len(modes):
            raise ValueError("layouts : un mode au plus par disposition")
        return self

    def mpc_pad(self, pad: int) -> MpcPad:
        return next(p for p in self.mpc if p.pad == pad)

    def scale(self, mode: Mode) -> Layout:
        """Disposition qui porte les intervalles et la famille du mode `mode`."""
        for lay in self.layouts:
            if lay.mode == mode:
                return lay
        raise ConfigError(f"layouts : aucune disposition pour le mode {mode!r}")


def load_config(path: Path = DEFAULT_CONFIG) -> Config:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        return Config.model_validate(raw)
    except (OSError, yaml.YAMLError, ValidationError) as exc:
        raise ConfigError(f"{path} : {exc}") from exc

"""Configuration matérielle et dispositions (`config/default.yaml`), validée par Pydantic."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator

from mk_brain.arp import (
    GATE_MAX,
    GATE_MIN,
    GATE_STEP,
    MAX_OCTAVES,
    MOTIF_NAME_MAX,
    MOTIF_OFF,
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


class ArpPreset(BaseModel):
    """Preset d'arpège (slice 13) : les cinq réglages rappelés d'un coup."""

    order: ArpOrder
    octaves: int = Field(ge=1, le=MAX_OCTAVES)
    gate: int = Field(ge=GATE_MIN, le=GATE_MAX, multiple_of=GATE_STEP)
    division: str
    motif: str = MOTIF_OFF

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
    raw_per_choice: int = Field(24, ge=1)  # ORD, OCT, MOT et PRE
    raw_per_gate_step: int = Field(12, ge=1)  # GATE, par pas de 5 %
    # motifs (slice 12) : nom → 16 pas (x note, X accent, . silence, - liée), ordre du fichier
    motifs: dict[str, str] = {}
    motif: str = MOTIF_OFF  # motif de départ : un nom de `motifs`, ou OFF
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
        for name, preset in self.presets.items():
            if not 1 <= len(name) <= MOTIF_NAME_MAX:
                raise ValueError(f"preset {name!r} : nom de 1 à {MOTIF_NAME_MAX} caractères")
            if preset.motif != MOTIF_OFF and preset.motif not in self.motifs:
                raise ValueError(f"preset {name!r} : motif {preset.motif!r} absent de arp.motifs")
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

    @model_validator(mode="after")
    def _target(self) -> Encoder:
        if (self.cc is None) == (not self.pitchbend):
            raise ValueError(f"encodeur {self.name} : un CC ou pitchbend, pas les deux")
        return self

    @property
    def param(self) -> int:
        """CC, ou PITCH_BEND."""
        return PITCH_BEND if self.cc is None else self.cc


class EncodersConfig(BaseModel):
    """Pages de 8 encodeurs, les mêmes pour toutes les tracks (SPEC, Encodeurs)."""

    pages: list[list[Encoder]]
    mute_cc: int = Field(94, ge=0, le=127)
    raw_per_step: int = Field(4, ge=1)  # unités brutes de la MK2 par cran de CC

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

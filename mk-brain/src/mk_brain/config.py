"""Configuration matérielle et dispositions (`config/default.yaml`), validée par Pydantic."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator

DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "config" / "default.yaml"

Byte = Annotated[int, Field(ge=0, le=255)]
RGB = tuple[Byte, Byte, Byte]


class ConfigError(Exception):
    """Fichier de configuration illisible ou invalide."""


class MidiConfig(BaseModel):
    port_hint: str = "Digitakt"
    auto_channel: int = Field(16, ge=1, le=16)
    program_channel: int = Field(10, ge=1, le=16)  # canal des Program Change de la DT2


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
    phrase: RGB = (0, 255, 0)  # LED GROUP du compteur de phrases


class PlayConfig(BaseModel):
    """Réglages de départ de la session ; modifiables à la MK2, jamais réécrits."""

    quantize: Literal["off", "1/16", "1/8"] = "1/16"
    swing: int = Field(50, ge=50, le=75)
    repeat: Literal["1/4", "1/8", "1/8T", "1/16", "1/16T", "1/32", "1/32T", "1/64"] = "1/16"
    phrase: Literal[32, 64] = 32  # longueur de phrase ; par banque avec les projets (slice 6)
    horizon_ms: float = Field(20.0, gt=0)  # envoi confié à l'ordonnanceur ce délai avant la cible


class Encoder(BaseModel):
    name: str = Field(max_length=4)
    cc: int = Field(ge=0, le=127)


class EncodersConfig(BaseModel):
    """Page unique des 8 encodeurs, la même pour toutes les tracks (SPEC, Encodeurs)."""

    page: list[Encoder]
    mute_cc: int = Field(94, ge=0, le=127)
    raw_per_step: int = Field(4, ge=1)  # unités brutes de la MK2 par cran de CC

    @field_validator("page")
    @classmethod
    def _eight(cls, v: list[Encoder]) -> list[Encoder]:
        if len(v) != 8:
            raise ValueError("encoders.page : exactement 8 encodeurs")
        return v


class Roles(BaseModel):
    tonique: RGB
    tierce: RGB
    quinte: RGB
    hors_gamme: RGB


Family = Literal["rythmique", "chromatique", "mineur", "majeur"]


class Layout(BaseModel):
    group: Literal["A", "B", "C", "D", "E", "F", "G", "H"]
    name: str
    kind: Literal["rythmique", "chromatique", "gamme"]
    family: Family
    base: int = Field(60, ge=0, le=127)
    intervals: list[int] = []

    @model_validator(mode="after")
    def _scale(self) -> Layout:
        if self.kind == "gamme":
            iv = self.intervals
            if not iv or iv[0] != 0 or iv != sorted(set(iv)) or iv[-1] > 11:
                raise ValueError(f"groupe {self.group} : intervalles 0-11 croissants depuis 0")
        return self


class Config(BaseModel):
    midi: MidiConfig = MidiConfig()
    velocity: VelocityConfig = VelocityConfig()
    leds: LedConfig = LedConfig()
    play: PlayConfig = PlayConfig()
    encoders: EncodersConfig
    roles: Roles
    families: dict[Family, RGB]
    track_colors: dict[int, RGB]
    layouts: list[Layout]

    @field_validator("track_colors")
    @classmethod
    def _tracks(cls, v: dict[int, RGB]) -> dict[int, RGB]:
        if sorted(v) != list(range(1, 17)):
            raise ValueError("track_colors : les 16 tracks, de 1 à 16")
        return v

    @model_validator(mode="after")
    def _groups(self) -> Config:
        if [lay.group for lay in self.layouts] != list("ABCDEFGH"):
            raise ValueError("layouts : un par groupe, dans l'ordre A-H")
        missing = {lay.family for lay in self.layouts} - set(self.families)
        if missing:
            raise ValueError(f"families : couleur manquante pour {sorted(missing)}")
        return self


def load_config(path: Path = DEFAULT_CONFIG) -> Config:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        return Config.model_validate(raw)
    except (OSError, yaml.YAMLError, ValidationError) as exc:
        raise ConfigError(f"{path} : {exc}") from exc

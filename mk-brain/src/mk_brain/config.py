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


class PlayConfig(BaseModel):
    """Réglages de départ de la session ; modifiables à la MK2, jamais réécrits."""

    quantize: Literal["off", "1/16", "1/8"] = "1/16"
    swing: int = Field(50, ge=50, le=75)
    repeat: Literal["1/4", "1/8", "1/8T", "1/16", "1/16T", "1/32", "1/32T", "1/64"] = "1/16"
    horizon_ms: float = Field(20.0, gt=0)  # envoi confié à l'ordonnanceur ce délai avant la cible


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

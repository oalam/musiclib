"""Projet de set (`projects/<set>.yaml`) : fiche de chaque banque, validée par Pydantic.

Schéma de la SPEC (Projets). Avancé à la slice 5.D pour le mode design : le
fichier est encore écrit à la main ; à la slice 6, `mk-brain convert` le
générera depuis le front matter `mkbrain:` de la doctrine du set.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from mk_brain.config import Mode
from mk_brain.layouts import NOTE_NAMES

PROJECTS = Path(__file__).resolve().parents[2] / "projects"
DEFAULT_PROJECT = PROJECTS / "solaris.yaml"

FLATS = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}
BANK_KEY = re.compile(r"^[A-H]-[A-Z0-9]+$")


class ProjectError(Exception):
    """Projet illisible ou invalide."""


class Bank(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    desc: str
    tempo: float = Field(gt=0)
    tonique: str
    mode: Mode
    phrase: Literal[32, 64] | None = None  # None : celle des `defaults`

    @field_validator("tonique")
    @classmethod
    def _note(cls, v: str) -> str:
        name = FLATS.get(v, v)
        if name not in NOTE_NAMES:
            raise ValueError(f"tonique illisible : {v!r} (C, C#, Db… B)")
        return name

    @property
    def tonic(self) -> int:
        """Classe de hauteur de la tonique, 0 = C."""
        return NOTE_NAMES.index(self.tonique)


class Defaults(BaseModel):
    model_config = ConfigDict(extra="forbid")

    phrase: Literal[32, 64] = 32


class Project(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    defaults: Defaults = Defaults()
    banks: dict[str, Bank]

    @field_validator("banks")
    @classmethod
    def _keys(cls, v: dict[str, Bank]) -> dict[str, Bank]:
        bad = [k for k in v if not BANK_KEY.match(k)]
        if bad:
            raise ValueError(f"banques : clé {bad[0]!r}, attendu lettre A-H, tiret, nom (E-TRIBE)")
        letters = [k[0] for k in v]
        if len(set(letters)) != len(letters):
            raise ValueError("banques : une seule clé par lettre")
        return v

    def bank(self, index: int) -> tuple[str, Bank] | None:
        """Banque de la lettre `index` (0 = A), ou None si le projet n'en a pas."""
        letter = "ABCDEFGH"[index]
        for key, bank in self.banks.items():
            if key[0] == letter:
                return key, bank
        return None

    def phrase(self, bank: Bank) -> Literal[32, 64]:
        return bank.phrase or self.defaults.phrase


def load_project(path: Path = DEFAULT_PROJECT) -> Project:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        return Project.model_validate(raw)
    except (OSError, yaml.YAMLError, ValidationError) as exc:
        raise ProjectError(f"{path} : {exc}") from exc

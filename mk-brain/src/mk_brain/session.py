"""Derniers réglages de la session, par projet (`state/session-<projet>.json`).

Demandé le 2026-11-09 : banque, pattern, track, faders retrouvés au
redémarrage. Sauvé au plus toutes les 2 s après un changement et à l'arrêt
(une coupure du Pi perd au plus 2 s). Rien n'est envoyé à la DT2 à la
restauration : les faders reviennent hors prise, les mutes à l'affichage
seulement (la DT2 a pu changer entre-temps).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from mk_brain.selection import STATE

STATE_DIR = STATE.parent
SAVE_EVERY_NS = 2_000_000_000


class FaderValue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    track: int = Field(ge=1, le=16)
    param: int = Field(ge=0, le=128)  # CC, ou PITCH_BEND (non sauvé : ressort)
    value: int = Field(ge=0, le=127)


class Session(BaseModel):
    """Réglages repris au démarrage ; fichier illisible ou hors bornes : session neuve."""

    model_config = ConfigDict(extra="ignore")

    design_bank: int | None = Field(None, ge=0, le=7)  # avant la slice 8 : banque du design
    layout: str | None = None  # nom de la disposition du clavier (avant : son groupe B-H)
    octave: int = 0
    bank: int | None = Field(None, ge=0, le=7)  # banque courante (PC reçu ou GROUP), 0 = A
    program: int | None = Field(None, ge=0, le=127)  # dernier PC reçu : pattern et banque live
    track: int = Field(1, ge=1, le=16)
    page: int = Field(0, ge=0)
    faders: list[FaderValue] = []
    muted: list[int] = []  # tracks mutées (affichage seulement)
    division: str | None = None  # division du repeat et de l'arpège
    arp_order: str | None = None  # arpégiateur (slice 11) ; hors bornes : valeur de la config
    arp_octaves: int | None = None
    arp_gate: int | None = None
    arp_preset: str | None = None  # dernier preset rappelé (slice 13)
    arp_chord: str | None = None  # accord (slice 15)
    arp_progression: str | None = None  # progression et durée d'un accord (slice 16)
    arp_bars: str | None = None
    arp_inversion: str | None = None  # renversement (slice 21)
    arp_motif: str | None = None  # motif (slice 12), par son nom ; disparu : celui de la config


def session_path(project: str, directory: Path = STATE_DIR) -> Path:
    return directory / f"session-{project}.json"


def load_session(project: str, directory: Path = STATE_DIR) -> Session | None:
    """Session sauvée, ou None (absente ou illisible : on repart à neuf)."""
    try:
        raw = json.loads(session_path(project, directory).read_text(encoding="utf-8"))
        return Session.model_validate(raw)
    except (OSError, json.JSONDecodeError, ValidationError):
        return None


def save_session(project: str, session: Session, directory: Path = STATE_DIR) -> None:
    """Écriture atomique (fichier temporaire puis renommage) ; un échec n'arrête pas le jeu."""
    path = session_path(project, directory)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(session.model_dump_json(indent=1), encoding="utf-8")
        os.replace(tmp, path)
    except OSError:
        pass

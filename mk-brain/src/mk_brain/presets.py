"""Banque des presets d'arpège sauvés depuis la MK2 (slice 14, `state/arp-presets.json`).

Une banque pour tous les projets : emplacement 1-16 → réglages. Seuls les
emplacements écrits depuis la machine sont dans le fichier ; les autres
viennent de `arp.presets` de la config. Écrit à chaque sauvegarde.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from pydantic import BaseModel, ValidationError

from mk_brain.arp import MOTIF_OFF
from mk_brain.config import PRESET_SLOTS, ArpConfig, ArpPreset
from mk_brain.session import STATE_DIR

PATH = STATE_DIR / "arp-presets.json"


class PresetBank(BaseModel):
    slots: dict[int, ArpPreset] = {}


def user_name(slot: int) -> str:
    """Nom affiché d'un emplacement sauvé depuis la MK2 : U01 à U16."""
    return f"U{slot:02d}"


def usable(arp: ArpConfig, slots: dict[int, ArpPreset]) -> dict[int, ArpPreset]:
    """Emplacements valides : numéro 1-16, motif encore présent dans la config."""
    return {
        n: p
        for n, p in sorted(slots.items())
        if 1 <= n <= PRESET_SLOTS and (p.motif == MOTIF_OFF or p.motif in arp.motifs)
    }


def load_bank(arp: ArpConfig, path: Path = PATH) -> dict[int, ArpPreset]:
    """Emplacements sauvés ; fichier absent ou illisible : aucun (la config seule)."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return usable(arp, PresetBank.model_validate(raw).slots)
    except (OSError, json.JSONDecodeError, ValidationError):
        return {}


def save_bank(slots: dict[int, ArpPreset], path: Path = PATH) -> None:
    """Écriture atomique (fichier temporaire puis renommage) ; un échec n'arrête pas le jeu."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(PresetBank(slots=slots).model_dump_json(indent=1), encoding="utf-8")
        os.replace(tmp, path)
    except OSError:
        pass

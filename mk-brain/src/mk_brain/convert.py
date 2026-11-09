"""Doctrine d'un set (front matter `mkbrain:`) + lives JSON → `projects/<set>.yaml` (Mac).

Slice 6.A (SPEC, Projets). Le front matter fait foi pour mk-brain ; les
`banks`, `keys` et `tempos` du lives JSON qu'il référence sont recoupés, et
toute divergence lève `ProjectError` avec la ligne de la banque fautive
(décidé le 2026-11-09), pour que les deux sources ne dérivent pas en
silence. Le projet est validé par `Project` avant d'être écrit ; le commit
se fait à la main.

    mk-brain convert digitakt/doctrine-dt2-solaris.md
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError

from mk_brain.project import PROJECTS, Defaults, Project, ProjectError, note_name

# abréviations de mode des `keys` du lives JSON (« A# phrg ») ; une autre lève
# ProjectError, à ajouter ici le jour où un set l'emploie
JSON_MODES = {"m": "eolien", "phrg": "phrygien"}

HEADER = (
    "# GÉNÉRÉ par `mk-brain convert {doctrine}` : ne pas éditer à la main.\n"
    "# Source : front matter `mkbrain:` de la doctrine, recoupé avec {live}.\n"
)


class FrontMatter(BaseModel):
    """Bloc `mkbrain:` ; les fiches de banque sont validées ensuite par `Project`."""

    model_config = ConfigDict(extra="forbid")

    live: str  # lives JSON, relatif à la racine du vault (parent de digitakt/)
    defaults: Defaults = Defaults()
    banks: dict[str, dict[str, Any]]


def _where(doctrine: Path, text: str, key: str) -> str:
    """`doctrine:ligne` de la déclaration de la banque `key`, sinon la doctrine seule."""
    m = re.search(rf"^\s+{re.escape(key)}:", text, re.MULTILINE)
    return f"{doctrine}:{text.count(chr(10), 0, m.start()) + 1}" if m else str(doctrine)


def read_front_matter(doctrine: Path) -> tuple[FrontMatter, str]:
    """Bloc `mkbrain:` de la doctrine, et son texte brut pour situer les erreurs."""
    try:
        text = doctrine.read_text(encoding="utf-8")
    except OSError as exc:
        raise ProjectError(f"{doctrine} : {exc}") from exc
    end = text.find("\n---", 4)
    if not text.startswith("---\n") or end == -1:
        raise ProjectError(f"{doctrine} : pas de front matter entre deux lignes ---")
    try:
        raw = yaml.safe_load(text[4:end]) or {}
    except yaml.YAMLError as exc:
        raise ProjectError(f"{doctrine} : front matter illisible : {exc}") from exc
    if not isinstance(raw, dict) or "mkbrain" not in raw:
        raise ProjectError(f"{doctrine} : pas de clé `mkbrain:` dans le front matter")
    try:
        return FrontMatter.model_validate(raw["mkbrain"]), text
    except ValidationError as exc:
        raise ProjectError(f"{doctrine} : mkbrain : {exc}") from exc


def check_live(project: Project, live: dict[str, Any], doctrine: Path, text: str) -> None:
    """Banques connues du JSON, tonalités et tempos identiques ; sinon ProjectError."""
    known = live.get("banks", [])
    for key in project.banks:
        if key not in known:
            raise ProjectError(f"{_where(doctrine, text, key)} : banque {key} absente du JSON")
    for key, value in live.get("keys", {}).items():
        bank = project.banks.get(key)
        if bank is None:
            raise ProjectError(f"{doctrine} : le JSON donne la tonalité de {key}, sans fiche")
        tonic, _, abbr = str(value).partition(" ")
        try:
            json_key = (note_name(tonic), JSON_MODES[abbr])
        except (ValueError, KeyError) as exc:
            raise ProjectError(f"JSON : tonalité {value!r} de {key} illisible") from exc
        if (bank.tonique, bank.mode) != json_key:
            raise ProjectError(
                f"{_where(doctrine, text, key)} : {key} en {bank.tonique} {bank.mode}, "
                f"le JSON dit {value!r}"
            )
    for key, tempo in live.get("tempos", {}).items():
        bank = project.banks.get(key)
        if bank is not None and bank.tempo != tempo:  # 0-KIT : dossier technique, ignoré
            raise ProjectError(
                f"{_where(doctrine, text, key)} : {key} à {bank.tempo:g} BPM, le JSON dit {tempo:g}"
            )


def convert(doctrine: Path) -> Project:
    """Projet résolu depuis la doctrine et le lives JSON qu'elle référence."""
    front, text = read_front_matter(doctrine)
    live_path = doctrine.resolve().parents[1] / front.live
    try:
        live = json.loads(live_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProjectError(f"{live_path} : {exc}") from exc
    raw = {"name": live.get("name", ""), "defaults": front.defaults, "banks": front.banks}
    try:
        project = Project.model_validate(raw)
    except ValidationError as exc:
        raise ProjectError(f"{doctrine} : mkbrain : {exc}") from exc
    check_live(project, live, doctrine, text)
    return project


def dump(project: Project, doctrine: str, live: str) -> str:
    """Texte YAML du projet, avec l'en-tête « généré » ; stable d'un run à l'autre."""
    body = yaml.safe_dump(
        project.model_dump(exclude_none=True), sort_keys=False, allow_unicode=True, width=100
    )
    return HEADER.format(doctrine=doctrine, live=live) + body


def write_project(doctrine: Path, out_dir: Path = PROJECTS) -> Path:
    """Convertit et écrit `out_dir/<set>.yaml` ; rejouable, même sortie à source égale."""
    front, _ = read_front_matter(doctrine)
    project = convert(doctrine)
    if not project.name:
        raise ProjectError(f"{front.live} : pas de `name`, nom du projet inconnu")
    rel = doctrine.resolve().relative_to(doctrine.resolve().parents[1])
    out = out_dir / f"{project.name}.yaml"
    out.write_text(dump(project, str(rel), front.live), encoding="utf-8")
    return out

"""Sélection de projet (slice 6.C, SPEC « Démarrage et choix du projet »).

Liste `projects/*.yaml` avec le nom, la date du dernier commit et le nombre
de banques ; un projet illisible reste dans la liste, marqué, et ne se
charge pas. Le dernier projet joué est présélectionné : son nom est gardé
dans `state/last_project` (local, ignoré par git).
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from mk_brain.project import PROJECTS, Project, ProjectError, load_project

STATE = Path(__file__).resolve().parents[2] / "state" / "last_project"
GIT_TIMEOUT_S = 2.0


@dataclass(frozen=True, slots=True)
class Entry:
    name: str  # nom du fichier sans `.yaml`
    path: Path
    date: str  # AAAA-MM-JJ : dernier commit, sinon modification du fichier
    project: Project | None  # None : illisible
    error: str = ""

    @property
    def banks(self) -> int:
        return 0 if self.project is None else len(self.project.banks)


def commit_date(path: Path) -> str:
    """Date du dernier commit du fichier ; date de modification hors git ou sans commit."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", path.name],
            cwd=path.parent,
            capture_output=True,
            text=True,
            timeout=GIT_TIMEOUT_S,
            check=False,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        out = ""
    return out or date.fromtimestamp(path.stat().st_mtime).isoformat()


def list_projects(directory: Path = PROJECTS) -> list[Entry]:
    """Projets du dossier, par nom ; chaque fichier est validé au passage."""
    entries = []
    for path in sorted(directory.glob("*.yaml")):
        try:
            entries.append(Entry(path.stem, path, commit_date(path), load_project(path)))
        except ProjectError as exc:
            entries.append(Entry(path.stem, path, commit_date(path), None, str(exc)))
    return entries


def read_last(state: Path = STATE) -> str | None:
    try:
        return state.read_text(encoding="utf-8").strip() or None
    except OSError:
        return None


def write_last(name: str, state: Path = STATE) -> None:
    """Retient le projet chargé ; un échec d'écriture n'empêche pas de jouer."""
    try:
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_text(name + "\n", encoding="utf-8")
    except OSError:
        pass


class Selector:
    """Liste à l'encodeur maître ; le dernier joué présélectionné."""

    def __init__(self, entries: list[Entry], last: str | None = None, sync: str = "") -> None:
        self.entries = entries
        self.sync = sync  # statut de la synchro du démarrage, en haut à droite
        names = [e.name for e in entries]
        self.index = names.index(last) if last in names else 0

    def scroll(self, delta: int) -> None:
        if self.entries:
            self.index = max(0, min(len(self.entries) - 1, self.index + delta))

    @property
    def current(self) -> Entry | None:
        return self.entries[self.index] if self.entries else None

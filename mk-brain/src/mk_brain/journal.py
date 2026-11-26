"""Journal de session (slice 25.A, SPEC « Slice 25 »).

Exemple : `solaris` armé par REC à l'écran de sélection, puis chargé ; le dossier
`state/sessions/2026-11-26-2130-solaris/` reçoit `journal.jsonl`, une ligne JSON par
événement :

    {"t_ns":…,"kind":"pattern","bar":33,"tick":0,"pattern":"B03","bank":"B","program":18}
    {"t_ns":…,"kind":"mute","bar":41,"tick":12,"track":9,"on":true,"src":"mk2"}

- La boucle MIDI n'attend jamais le disque : `write` empile, un fil dédié écrit.
- Vidé sur la carte toutes les 2 s (`FLUSH_S`) : une coupure de courant perd 2 s au plus.
- Un disque plein ou absent n'arrête pas le jeu : `failed` passe à vrai, le reste est jeté.
- Projets armés : `state/rec-sessions.json`, retenus d'un démarrage à l'autre.
"""

from __future__ import annotations

import contextlib
import json
import os
import queue
import shutil
import threading
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import IO, Literal

from pydantic import BaseModel, ConfigDict, ValidationError

from mk_brain.boot import COMMIT_ENV
from mk_brain.clock import TICKS_PER_BAR
from mk_brain.session import STATE_DIR

SESSIONS = STATE_DIR / "sessions"
ARMED = STATE_DIR / "rec-sessions.json"
JOURNAL = "journal.jsonl"
FLUSH_S = 2.0
CLOSE_TIMEOUT_S = 5.0

Kind = Literal["session", "transport", "bar", "pattern", "mute", "cc", "note", "geste"]
Fields = dict[str, object]
# prise du moteur : (événement, ticks depuis le Start ou None à l'arrêt, contenu)
Sink = Callable[[Kind, int | None, Fields], None]


class Line(BaseModel):
    """Une ligne du journal : instant, position (None transport arrêté), puis le contenu."""

    model_config = ConfigDict(extra="allow")

    t_ns: int
    kind: Kind
    bar: int | None = None  # mesure depuis le Start, base 1
    tick: int | None = None  # tick dans la mesure, 0-95


class Header(BaseModel):
    """En-tête : première ligne, événement `session`."""

    project: str
    version: str
    commit: str
    date: str  # horloge du Pi : sans réseau au démarrage, elle peut retarder


class Armed(BaseModel):
    """Projets dont la session est enregistrée (armés par REC à la sélection)."""

    projects: list[str] = []


def load_armed(path: Path = ARMED) -> set[str]:
    """Projets armés ; fichier absent ou illisible : aucun."""
    try:
        return set(Armed.model_validate_json(path.read_text(encoding="utf-8")).projects)
    except (OSError, ValidationError):
        return set()


def save_armed(projects: set[str], path: Path = ARMED) -> None:
    """Écriture atomique ; un échec n'empêche pas de jouer."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(Armed(projects=sorted(projects)).model_dump_json(), encoding="utf-8")
        os.replace(tmp, path)
    except OSError:
        pass


def free_gb(path: Path = STATE_DIR) -> float | None:
    """Espace libre du disque de `state/`, en Go ; None s'il ne se lit pas."""
    with contextlib.suppress(OSError):
        while not path.exists() and path != path.parent:
            path = path.parent
        return shutil.disk_usage(path).free / 1e9
    return None


def session_dir(project: str, when: datetime, root: Path = SESSIONS) -> Path:
    """`<date>-<heure>-<set>` ; deux sessions dans la même minute : suffixe `-2`, `-3`…"""
    base = f"{when:%Y-%m-%d-%H%M}-{project}"
    path, n = root / base, 1
    while path.exists():
        n += 1
        path = root / f"{base}-{n}"
    return path


def encode(t_ns: int, kind: Kind, ticks: int | None, fields: Fields) -> str:
    bar = None if ticks is None else ticks // TICKS_PER_BAR + 1
    tick = None if ticks is None else ticks % TICKS_PER_BAR
    return Line(t_ns=t_ns, kind=kind, bar=bar, tick=tick, **fields).model_dump_json()


_Item = tuple[int, Kind, int | None, Fields]


class Journal:
    """Écrit `journal.jsonl` derrière une file ; `write` est la prise donnée au moteur."""

    def __init__(
        self,
        directory: Path,
        header: Header,
        flush_s: float = FLUSH_S,
        now: Callable[[], int] = time.perf_counter_ns,
    ) -> None:
        self.directory = directory
        self.failed = False
        self._flush_s = flush_s
        self._now = now
        self._queue: queue.SimpleQueue[_Item | None] = queue.SimpleQueue()
        self.write("session", None, header.model_dump())
        self._thread = threading.Thread(target=self._run, name="journal", daemon=True)
        self._thread.start()

    def write(self, kind: Kind, ticks: int | None, fields: Fields) -> None:
        """Empile un événement, horodaté ici ; ne touche jamais le disque."""
        self._queue.put((self._now(), kind, ticks, fields))

    def close(self) -> None:
        """Vide la file sur le disque et arrête le fil."""
        self._queue.put(None)
        self._thread.join(CLOSE_TIMEOUT_S)

    def _open(self) -> IO[str] | None:
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            return (self.directory / JOURNAL).open("a", encoding="utf-8")
        except OSError:
            self.failed = True
            return None

    def _sync(self, file: IO[str]) -> None:
        file.flush()
        os.fsync(file.fileno())

    def _run(self) -> None:
        file = self._open()
        last = time.monotonic()
        while True:
            item: _Item | Literal["idle"] | None
            try:
                item = self._queue.get(timeout=self._flush_s)
            except queue.Empty:
                item = "idle"  # rien depuis 2 s : seulement vider
            if item is None:
                break
            if file is None or self.failed:
                continue  # disque en panne : la file se vide sans rien écrire
            try:
                if item != "idle":
                    file.write(encode(*item) + "\n")
                if time.monotonic() - last >= self._flush_s:
                    self._sync(file)
                    last = time.monotonic()
            except (OSError, ValidationError, TypeError):
                self.failed = True
        if file is not None:
            with contextlib.suppress(OSError):
                if not self.failed:
                    self._sync(file)
                file.close()


def open_journal(
    project: str, version: str, root: Path = SESSIONS, when: datetime | None = None
) -> Journal:
    """Ouvre la session d'un projet armé ; le dossier est créé par le fil d'écriture."""
    when = when or datetime.now()
    header = Header(
        project=project,
        version=version,
        commit=os.environ.get(COMMIT_ENV, ""),
        date=when.isoformat(timespec="seconds"),
    )
    return Journal(session_dir(project, when, root), header)


def read_journal(path: Path) -> list[Line]:
    """Lignes d'un journal ; une dernière ligne coupée par une panne est ignorée."""
    lines: list[Line] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        try:
            lines.append(Line.model_validate(json.loads(raw)))
        except (json.JSONDecodeError, ValidationError):
            continue
    return lines

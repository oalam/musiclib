"""Synchro des réglages appris entre le Mac et le Pi (`state/`, par SSH).

Le Mac sert à travailler, le Pi au live : `play` lancé sur le Mac échange avec le Pi,
au lancement et à l'arrêt, les sessions par projet (`session-<projet>.json`, valeurs
des faders apprises de la DT2 comprises) et la banque de presets d'arpège
(`arp-presets.json`). Le reste de `state/` (retour arrière du Pi, dernier projet) ne
voyage pas.

- Fichier entier, jamais de fusion (décidé le 2026-11-12).
- Qui a changé : comparé à l'empreinte de la dernière synchro (`state/sync-base.json`,
  sur le Mac), pas aux dates. Le Pi n'a pas d'horloge sauvegardée : hors ligne, ses
  dates ne valent rien. Un seul côté a changé : il est copié vers l'autre.
- Les deux ont changé (conflit) : le plus récent gagne, à dates égales le Mac ; la
  ligne de compte rendu le dit.
- Un fichier absent d'un côté y est copié ; une suppression ne se propage pas.
- Le service du Pi est arrêté le temps de l'échange, puis relancé : en marche, il
  garde sa session en mémoire et la réécrit à l'arrêt, par-dessus ce qu'on vient de
  copier. Arrêté d'abord, il écrit sa session avant qu'on la lise.
- Pi injoignable : `SyncError`, à l'appelant de continuer sans synchro.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, ValidationError

from mk_brain.session import STATE_DIR

NAME = re.compile(r"(session-[\w.-]+|arp-presets)\.json")  # ce qui voyage, rien d'autre
BASE = "sync-base.json"
SERVICE = "mk-brain"
# Sur le Pi : service arrêté (il écrit sa session), puis empreinte, date et nom de chaque
# fichier concerné, une ligne par fichier.
LISTING = (
    "sudo -n systemctl stop "
    + SERVICE
    + " && cd {dir} && for f in session-*.json arp-presets.json; do "
    '[ -f "$f" ] && echo "$(sha256sum < "$f" | cut -c1-64) $(stat -c %Y "$f") $f"; '
    "done; true"
)


class SyncError(Exception):
    """Pi injoignable, ou copie en échec."""


@dataclass(frozen=True, slots=True)
class Stamp:
    digest: str
    mtime: int


class Remote(Protocol):
    def listing(self) -> dict[str, Stamp]:
        """Arrête le service du Pi et rend ses fichiers."""
        ...

    def release(self) -> None:
        """Relance le service du Pi."""
        ...

    def push(self, source: Path, name: str) -> None: ...
    def pull(self, name: str, target: Path) -> None: ...


class SyncBase(BaseModel):
    """Empreinte de chaque fichier à la dernière synchro."""

    digests: dict[str, str] = {}


def parse_listing(text: str) -> dict[str, Stamp]:
    """Lignes `empreinte date nom` ; tout nom inattendu est ignoré."""
    found: dict[str, Stamp] = {}
    for line in text.splitlines():
        parts = line.split(" ", 2)
        if len(parts) == 3 and NAME.fullmatch(parts[2]) and parts[1].isdigit():
            found[parts[2]] = Stamp(parts[0], int(parts[1]))
    return found


class SshRemote:
    """Le Pi par `ssh` et `scp`, sans mot de passe (clé) ni question (`BatchMode`)."""

    def __init__(self, host: str, directory: str, timeout_s: float) -> None:
        self.host = host
        self.directory = directory
        self.timeout_s = timeout_s
        self._options = ["-o", "BatchMode=yes", "-o", f"ConnectTimeout={max(1, round(timeout_s))}"]

    def _run(self, command: list[str]) -> str:
        try:
            done = subprocess.run(
                command, capture_output=True, text=True, timeout=self.timeout_s + 5, check=True
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise SyncError(f"{command[0]} {self.host} : {exc}") from exc
        return done.stdout

    def listing(self) -> dict[str, Stamp]:
        script = LISTING.format(dir=self.directory)
        return parse_listing(self._run(["ssh", *self._options, self.host, script]))

    def release(self) -> None:
        # `--no-block` : sans lui, `start` attend le lancement (`sync.sh`, plus de 8 s mesurées)
        self._run(
            ["ssh", *self._options, self.host, f"sudo -n systemctl start --no-block {SERVICE}"]
        )

    def push(self, source: Path, name: str) -> None:
        target = f"{self.host}:{self.directory}/{name}"
        self._run(["scp", "-q", "-p", *self._options, str(source), target])

    def pull(self, name: str, target: Path) -> None:
        source = f"{self.host}:{self.directory}/{name}"
        self._run(["scp", "-q", "-p", *self._options, source, str(target)])


def local_listing(directory: Path) -> dict[str, Stamp]:
    found: dict[str, Stamp] = {}
    if not directory.is_dir():
        return found
    for path in sorted(directory.iterdir()):
        if path.is_file() and NAME.fullmatch(path.name):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            found[path.name] = Stamp(digest, int(path.stat().st_mtime))
    return found


def _load_base(directory: Path) -> dict[str, str]:
    try:
        raw = json.loads((directory / BASE).read_text(encoding="utf-8"))
        return SyncBase.model_validate(raw).digests
    except (OSError, json.JSONDecodeError, ValidationError):
        return {}


def _save_base(directory: Path, digests: dict[str, str]) -> None:
    tmp = directory / (BASE + ".tmp")
    tmp.write_text(SyncBase(digests=digests).model_dump_json(indent=1), encoding="utf-8")
    os.replace(tmp, directory / BASE)


def decide(here: Stamp | None, there: Stamp | None, base: str | None) -> tuple[str, bool]:
    """Sens de la copie (`push`, `pull` ou `` si rien à faire) et conflit ou non."""
    if here is None or there is None:
        return ("pull" if here is None else "push") if here != there else "", False
    if here.digest == there.digest:
        return "", False
    if here.digest == base:
        return "pull", False
    if there.digest == base:
        return "push", False
    return ("pull" if there.mtime > here.mtime else "push"), True


def sync_state(remote: Remote, directory: Path = STATE_DIR) -> list[str]:
    """Échange les fichiers concernés avec le Pi ; rend une ligne par fichier copié."""
    there = remote.listing()
    directory.mkdir(parents=True, exist_ok=True)
    here = local_listing(directory)
    base = _load_base(directory)
    digests: dict[str, str] = {}
    report: list[str] = []
    try:
        try:
            for name in sorted(set(here) | set(there)):
                mine, theirs = here.get(name), there.get(name)
                way, conflict = decide(mine, theirs, base.get(name))
                path = directory / name
                if way == "push" and mine is not None:
                    remote.push(path, name)
                    digests[name] = mine.digest
                elif way == "pull" and theirs is not None:
                    tmp = path.with_suffix(".pull")
                    remote.pull(name, tmp)
                    os.replace(tmp, path)
                    digests[name] = theirs.digest
                elif mine is not None:
                    digests[name] = mine.digest
                if way:
                    arrow = "Mac -> Pi" if way == "push" else "Pi -> Mac"
                    note = " (modifié des deux côtés : le plus récent gagne)" if conflict else ""
                    report.append(f"{name} : {arrow}{note}")
        finally:  # ce qui est déjà copié reste acquis si une copie échoue ensuite
            try:
                _save_base(directory, {**base, **digests})
            except OSError as exc:
                raise SyncError(f"{BASE} : {exc}") from exc
    except SyncError:
        with contextlib.suppress(SyncError):  # l'échec de la copie est l'erreur à rendre
            remote.release()
        raise
    try:
        remote.release()
    except SyncError as exc:  # les copies sont faites : le dire, sans perdre le compte rendu
        report.append(f"service du Pi non relancé ({exc})")
    return report

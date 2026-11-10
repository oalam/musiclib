"""Démarrage sur le Pi (slice 7, SPEC « Service et retour arrière »).

Le service lance `mk-brain play` avec le commit courant dans
`MKBRAIN_COMMIT`. Quand la boucle principale tourne, `mark_ready` écrit ce
commit dans `state/last_good` et efface `state/fails` : `deploy/sync.sh` sait
alors à quel commit revenir si un code tiré ensuite ne démarre pas.
`read_sync` lit le statut de synchro écrit par `sync.sh`, affiché sur
l'écran de sélection. Hors service (Mac, tests), rien n'est écrit ni lu.
"""

from __future__ import annotations

import os
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parents[2] / "state"
SYNC_FILE = Path("/run/mk-brain/sync")
COMMIT_ENV = "MKBRAIN_COMMIT"


def mark_ready(state_dir: Path = STATE_DIR, commit: str | None = None) -> bool:
    """Retient le commit qui démarre ; False hors service ou si l'écriture échoue."""
    commit = commit if commit is not None else os.environ.get(COMMIT_ENV, "")
    if not commit:
        return False
    try:
        state_dir.mkdir(parents=True, exist_ok=True)
        (state_dir / "last_good").write_text(commit + "\n", encoding="utf-8")
        (state_dir / "fails").unlink(missing_ok=True)
    except OSError:
        return False
    return True


def read_sync(path: Path = SYNC_FILE) -> str:
    """Statut de la synchro du démarrage (`sync a1b2c3d`…), vide s'il n'y en a pas."""
    try:
        return path.read_text(encoding="utf-8").strip()[:20]
    except OSError:
        return ""

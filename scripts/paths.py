"""Hub unique des chemins de la library (vault vs disque media).

Deux racines :

- **Vault** (`music/library/`) : metadonnees texte versionnees — `library.md`,
  sidecars `quality/`, cache `artists/`, banks Digitakt (`.json`/`.md`),
  catalogue samples. Toujours disponible.
- **Media** (`MUSIC_MEDIA_ROOT`, defaut `/Volumes/xtreme`) : binaires lourds sur
  le SSD externe, dedie au son.

```
<MEDIA_ROOT>/
├── .music-media          # marqueur : prouve qu'on est sur le bon disque
├── Mix/                  # tracks pour le mix (Rekordbox)
│   ├── audio/            # <slug>.{flac,m4a,mp3} (+ sous-dossiers de style)
│   ├── stems/<slug>/     # Demucs
│   └── visuals/          # PNG Phase 5 + _index.md
└── Live/                 # materiel de set live
    ├── renoise/          # .xrns
    ├── grooves/          # .mid / .tidal
    └── digitakt/<slug>/  # pNN.mid
```

La colonne `file` de library.md (`[[audio/<slug>.flac]]`) est relative a
`MIX_DIR`. Le vault garde des symlinks `library/audio` et `library/visuals`
vers le disque pour qu'Obsidian resolve les wikilinks et les embeds.

Les modules importent ces constantes au lieu de recalculer leurs chemins ;
les commandes qui lisent ou ecrivent du media appellent `require_media()`.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent

# --- Vault : metadonnees -------------------------------------------------
LIBRARY = VAULT_ROOT / "library"
LIBRARY_FILE = LIBRARY / "library.md"
QUALITY_DIR = LIBRARY / "quality"
ARTISTS_DIR = LIBRARY / "artists"
DIGITAKT_DIR = LIBRARY / "digitakt"
SAMPLES_CATALOG = LIBRARY / "samples" / "catalog.csv"

# --- Disque media --------------------------------------------------------
MEDIA_ROOT = Path(os.environ.get("MUSIC_MEDIA_ROOT", "/Volumes/xtreme"))
MEDIA_MARKER = MEDIA_ROOT / ".music-media"

MIX_DIR = MEDIA_ROOT / "Mix"
AUDIO_DIR = MIX_DIR / "audio"
STEMS_DIR = MIX_DIR / "stems"
VISUALS_DIR = MIX_DIR / "visuals"

LIVE_DIR = MEDIA_ROOT / "Live"
RENOISE_DIR = LIVE_DIR / "renoise"
GROOVES_DIR = LIVE_DIR / "grooves"
DIGITAKT_MIDI_DIR = LIVE_DIR / "digitakt"

# Conteneurs lus par Rekordbox : tout le reste (opus, ogg, webm) est
# transcode en FLAC a l'acquisition.
REKORDBOX_EXTS = (".flac", ".m4a", ".mp3")

_FILE_REF_RE = re.compile(r"\[\[(.+?)\]\]")


class MediaRootUnavailable(RuntimeError):
    """Le disque media n'est pas monte (ou n'est pas le bon disque)."""


def media_available() -> bool:
    return MEDIA_MARKER.exists()


def require_media() -> Path:
    """Leve `MediaRootUnavailable` si le disque media est absent."""
    if not media_available():
        raise MediaRootUnavailable(
            f"disque media introuvable : {MEDIA_MARKER} absent. Brancher le "
            f"SSD ou definir MUSIC_MEDIA_ROOT."
        )
    return MEDIA_ROOT


def media_ok() -> bool:
    """Garde des CLI media : message clair sur stderr plutot qu'une trace."""
    try:
        require_media()
    except MediaRootUnavailable as exc:
        print(f"[media] {exc}", file=sys.stderr)
        return False
    return True


def file_ref(entry: dict[str, str]) -> str | None:
    """Chemin relatif a MIX_DIR extrait du wikilink `file` (`audio/x.flac`)."""
    match = _FILE_REF_RE.search(entry.get("file", ""))
    return match.group(1) if match else None


def resolve_audio(entry: dict[str, str]) -> Path | None:
    """Chemin absolu de l'audio d'une entree library.md, None si absent."""
    rel = file_ref(entry)
    if rel is None:
        return None
    p = MIX_DIR / rel
    return p if p.exists() else None


def mix_relative(path: Path) -> str:
    """Forme stockee (sidecar `file_path`, colonne `file`) : relative a MIX_DIR."""
    try:
        return path.resolve().relative_to(MIX_DIR.resolve()).as_posix()
    except ValueError:
        return str(path)

"""Lecture / ecriture du fichier unique `library/library.md`.

Format actuel : **table markdown** avec une ligne par morceau et une
colonne par champ. Permet un scan visuel rapide de la library.

Echappement dans les cellules :
- `|` -> `\\|` (sinon casse la table)
- `\\n` -> `<br>` (Obsidian rend correctement, parsing inverse propre)

Compatibilite ascendante : si on detecte l'ancien format (sections
`## Artist - Title` + listes `- **field**: value`), on le parse quand
meme et la prochaine ecriture migrera automatiquement vers la table.
Un backup `.backup-pre-table-YYYY-MM-DD` doit etre fait manuellement
avant la 1ere migration (voir SPEC.md).

Champs preserves (`PRESERVED_FIELDS`) : jamais ecrases lors d'une
re-execution automatique (edition manuelle protegee).
"""
from __future__ import annotations

import re
import unicodedata
from datetime import date
from pathlib import Path

# Champs preserves a chaque re-ecriture (edition humaine attendue)
PRESERVED_FIELDS: tuple[str, ...] = ("energy", "mood", "tags", "notes")

# Ordre canonique des champs (= colonnes de la table)
FIELD_ORDER: tuple[str, ...] = (
    "artist", "title", "bpm", "key", "duration", "year",
    "genre", "about", "quality", "quality_score", "band_profile",
    "groove_cluster",
    "source", "url", "buy_url",
    "file", "has_stems", "added", *PRESERVED_FIELDS,
)


def slugify(value: str) -> str:
    """Identifiant ASCII safe pour nom de fichier / slug d'entree."""
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    value = re.sub(r"[\s_-]+", "_", value)
    return value or "untitled"


# ---------------------------------------------------------------------------
# Echappement / desechappement pour cellules de table
# ---------------------------------------------------------------------------

def _escape_cell(value: str) -> str:
    if value is None:
        return ""
    s = str(value).replace("\r", "")
    s = s.replace("\\", "\\\\")
    s = s.replace("|", "\\|")
    s = s.replace("\n", "<br>")
    return s.strip()


def _unescape_cell(value: str) -> str:
    s = value.strip()
    s = s.replace("<br>", "\n")
    s = s.replace("\\|", "|")
    s = s.replace("\\\\", "\\")
    return s


# ---------------------------------------------------------------------------
# Parser nouveau format (table markdown)
# ---------------------------------------------------------------------------

_SPLIT_CELLS_RE = re.compile(r"(?<!\\)\|")  # split sur | non echappe


def _parse_table(text: str) -> dict[str, dict[str, str]] | None:
    """Parse format table. None si pas de table reconnaissable."""
    lines = text.splitlines()
    header_idx: int | None = None
    headers: list[str] = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        # Tente de parser comme header : doit contenir 'artist' ET 'title'
        cells = [c.strip() for c in _SPLIT_CELLS_RE.split(stripped.strip("|"))]
        lower = [c.lower() for c in cells]
        if "artist" in lower and "title" in lower:
            header_idx = i
            headers = lower
            break
    if header_idx is None:
        return None

    # La ligne suivante est attendue comme separateur ('|---|---|...')
    # On la skip si elle ressemble a ca
    body_start = header_idx + 1
    if body_start < len(lines):
        sep_line = lines[body_start].strip()
        if re.match(r"^\|[\s:|-]+\|?\s*$", sep_line):
            body_start += 1

    entries: dict[str, dict[str, str]] = {}
    for line in lines[body_start:]:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells_raw = _SPLIT_CELLS_RE.split(stripped.strip("|"))
        cells = [_unescape_cell(c) for c in cells_raw]
        if len(cells) != len(headers):
            continue
        fields = dict(zip(headers, cells))
        artist = fields.get("artist", "").strip()
        title = fields.get("title", "").strip()
        if not artist and not title:
            continue
        slug = f"{slugify(artist)}_-_{slugify(title)}"
        entries[slug] = fields
    return entries


# ---------------------------------------------------------------------------
# Parser ancien format (sections + listes a puces) — pour migration
# ---------------------------------------------------------------------------

_SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_FIELD_RE = re.compile(r"^-\s*\*\*([^*]+)\*\*\s*:\s*(.*)$")


def _parse_legacy_sections(text: str) -> dict[str, dict[str, str]]:
    entries: dict[str, dict[str, str]] = {}
    positions = [m.start() for m in _SECTION_RE.finditer(text)]
    if not positions:
        return entries
    positions.append(len(text))
    for i in range(len(positions) - 1):
        block = text[positions[i]:positions[i + 1]]
        header_match = _SECTION_RE.match(block)
        if not header_match:
            continue
        header = header_match.group(1)
        if " — " in header:
            artist, title = header.split(" — ", 1)
        elif " - " in header:
            artist, title = header.split(" - ", 1)
        else:
            artist, title = "unknown", header
        fields: dict[str, str] = {"artist": artist.strip(), "title": title.strip()}
        for line in block.splitlines()[1:]:
            m = _FIELD_RE.match(line)
            if m:
                fields[m.group(1).strip().lower()] = m.group(2).strip()
        slug = f"{slugify(fields['artist'])}_-_{slugify(fields['title'])}"
        entries[slug] = fields
    return entries


# ---------------------------------------------------------------------------
# API publique
# ---------------------------------------------------------------------------

def parse_library(path: Path) -> dict[str, dict[str, str]]:
    """Parse library.md (table prioritaire, fallback ancien format sections)."""
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    table = _parse_table(text)
    if table is not None and table:
        return table
    legacy = _parse_legacy_sections(text)
    if legacy:
        return legacy
    return table or {}


def write_library(path: Path, entries: dict[str, dict[str, str]]) -> None:
    """Reecrit `library.md` au format table markdown."""
    today = date.today().isoformat()
    sorted_entries = sorted(
        entries.items(),
        key=lambda kv: (
            kv[1].get("artist", "").lower(),
            kv[1].get("title", "").lower(),
        ),
    )

    lines = [
        "---",
        f"updated: {today}",
        f"count: {len(entries)}",
        "tags: [library]",
        "---",
        "",
        "# Library — morceaux pour les sets",
        "",
        "> Une ligne par morceau. **`energy`, `mood`, `tags`, `notes`** sont",
        "> preserves lors des re-runs automatiques : edite-les directement",
        "> dans la cellule correspondante. `<br>` dans une cellule = retour",
        "> a la ligne (rendu Obsidian).",
        "",
        "| " + " | ".join(FIELD_ORDER) + " |",
        "|" + "|".join("---" for _ in FIELD_ORDER) + "|",
    ]
    for _, fields in sorted_entries:
        row = "| " + " | ".join(
            _escape_cell(fields.get(key, "")) for key in FIELD_ORDER
        ) + " |"
        lines.append(row)

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_field(library_path: Path, slug: str, field: str, value: str) -> bool:
    entries = parse_library(library_path)
    if slug not in entries:
        return False
    entries[slug][field] = value
    write_library(library_path, entries)
    return True


def find_entry_by_file(
    library_path: Path,
    audio_filename: str,
) -> tuple[str, dict[str, str]] | None:
    entries = parse_library(library_path)
    for slug, fields in entries.items():
        file_ref = fields.get("file", "")
        if audio_filename in file_ref:
            return slug, fields
    return None

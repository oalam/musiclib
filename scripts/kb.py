#!/usr/bin/env python3
"""Base de connaissance Digitakt II (Phase 7.D, 7.F) : notes markdown + recherche.

Corpus = `digitakt/kb/*.md` + `digitakt/doctrine.md`, decoupes en sections
(titres `##` / `###`). Recherche plein texte sans index ni RAG : le corpus
tient en memoire, on le relit a chaque requete (les notes editees dans
Obsidian sont vues tout de suite).

Lien avec le manuel PDF (7.F) : le sommaire du PDF donne la page de chaque
paragraphe `§x.y` ; les references du frontmatter `manuel` et celles citees
dans le texte deviennent des liens vers cette page.

Usage:
    kb.py search "pattern modele"        # resultats en console
    kb.py toc                            # sommaire des fiches par lot
"""
from __future__ import annotations

import argparse
import functools
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel

VAULT_ROOT = Path(__file__).resolve().parent.parent
KB_DIR = VAULT_ROOT / "digitakt" / "kb"
DOCTRINE = VAULT_ROOT / "digitakt" / "doctrine.md"
KB_INDEX = KB_DIR / "_index.md"
MANUAL_PDF = VAULT_ROOT / "refs" / "Digitakt-2-User-Manual_ENG_OS1.17_260930.pdf"

_HEADING = re.compile(r"^(#{1,3})\s+(.+?)\s*$")
_SNIPPET_CHARS = 90
_HEADING_BONUS = 5
_SECTION_REF = re.compile(r"§(\d+(?:\.\d+)*)(?:\s*-\s*(\d+(?:\.\d+)*))?")
_DOCTRINE_BEFORE = re.compile(r"doctrine\]*\s*\(?\s*$", re.IGNORECASE)  # « doctrine §3 », « [[../doctrine]] (§3 »
_LOT_HEADING = re.compile(r"^##\s+Lot\s+(\d+)\s*[—–-]\s*(.+?)\s*$", re.MULTILINE)


class KbHit(BaseModel):
    """Une section qui contient tous les termes de la requete."""
    path: str          # relatif au vault, ex. digitakt/kb/fill.md
    title: str         # titre de la note
    heading: str       # titre de la section ("" = chapeau de la note)
    anchor: str        # ancre de la section dans la note rendue
    snippet: str       # extrait autour de la 1re occurrence
    score: float


class ManualRef(BaseModel):
    """Paragraphe du manuel et sa page (numero imprime = page du PDF)."""
    section: str       # ex. 11.7
    title: str         # titre du sommaire, ex. AMP PAGE
    page: int


class KbNote(BaseModel):
    path: str
    title: str
    markdown: str      # sans frontmatter
    manual: list[ManualRef] = []                 # references du frontmatter `manuel`
    manual_index: dict[str, ManualRef] = {}      # tous les § resolus (frontmatter + texte)


class KbEntry(BaseModel):
    path: str
    title: str
    ordre: int
    statut: str


class KbLot(BaseModel):
    number: int
    name: str
    notes: list[KbEntry]


@dataclass(frozen=True)
class KbSection:
    path: str
    title: str
    heading: str
    anchor: str
    body: str


def normalize(text: str) -> str:
    """Minuscules sans accents, pour comparer « modèle » et « modele »."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


def slugify(text: str) -> str:
    """Ancre de titre, identique a celle generee par le front."""
    return re.sub(r"[^a-z0-9]+", "-", normalize(text)).strip("-")


def strip_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            return text[end + 4:].lstrip("\n")
    return text


def parse_frontmatter(text: str) -> dict[str, str]:
    """Frontmatter plat `cle: valeur` (guillemets retires), {} si absent."""
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    out: dict[str, str] = {}
    for line in text[4:end].splitlines():
        key, sep, value = line.partition(":")
        if sep and key.strip() and not key.startswith(" "):
            out[key.strip()] = value.strip().strip('"').strip("'")
    return out


def corpus_files() -> list[Path]:
    files = sorted(KB_DIR.glob("*.md")) if KB_DIR.exists() else []
    return ([DOCTRINE] if DOCTRINE.exists() else []) + files


def split_sections(text: str, rel_path: str) -> list[KbSection]:
    """Decoupe une note en sections `##` / `###` (le `#` donne le titre)."""
    body = strip_frontmatter(text)
    title = Path(rel_path).stem
    sections: list[KbSection] = []
    heading, lines = "", []
    in_code = False

    def flush() -> None:
        content = "\n".join(lines).strip()
        if content or heading:
            sections.append(KbSection(rel_path, title, heading, slugify(heading), content))

    for line in body.splitlines():
        if line.startswith("```"):
            in_code = not in_code
        m = None if in_code else _HEADING.match(line)
        if m and len(m.group(1)) == 1:
            title = m.group(2)
            continue
        if m:
            flush()
            heading, lines = m.group(2), []
        else:
            lines.append(line)
    flush()
    return [s if s.title == title else KbSection(s.path, title, s.heading, s.anchor, s.body)
            for s in sections]


def load_corpus() -> list[KbSection]:
    out: list[KbSection] = []
    for f in corpus_files():
        out += split_sections(f.read_text(encoding="utf-8"),
                              f.relative_to(VAULT_ROOT).as_posix())
    return out


def _snippet(body: str, terms: list[str]) -> str:
    flat = " ".join(body.split())
    norm = normalize(flat)  # meme longueur que flat sur du texte latin
    pos = min((p for t in terms if (p := norm.find(t)) >= 0), default=0)
    start = max(0, pos - _SNIPPET_CHARS // 3)
    end = min(len(flat), start + _SNIPPET_CHARS * 2)
    return ("…" if start else "") + flat[start:end] + ("…" if end < len(flat) else "")


def search(query: str, sections: list[KbSection], limit: int = 20) -> list[KbHit]:
    """Sections contenant tous les termes ; score = occurrences, bonus titre."""
    terms = [t for t in normalize(query).split() if t]
    if not terms:
        return []
    hits: list[KbHit] = []
    for s in sections:
        head = normalize(f"{s.title} {s.heading}")
        text = normalize(s.body)
        if not all(t in head or t in text for t in terms):
            continue
        score = sum(text.count(t) + _HEADING_BONUS * head.count(t) for t in terms)
        hits.append(KbHit(path=s.path, title=s.title, heading=s.heading, anchor=s.anchor,
                          snippet=_snippet(s.body or s.heading, terms), score=score))
    hits.sort(key=lambda h: -h.score)
    return hits[:limit]


def outline_from_pdf(pdf: Path) -> dict[str, ManualRef]:
    """Sommaire du PDF -> {"10.8.6": ManualRef}, cle = numero en tete de titre."""
    from pypdf import PdfReader  # import local : seul le lien manuel en a besoin

    reader = PdfReader(pdf)
    out: dict[str, ManualRef] = {}

    def walk(items: list[Any]) -> None:
        for item in items:
            if isinstance(item, list):
                walk(item)
                continue
            title = str(item.title).strip()
            m = re.match(r"(\d+(?:\.\d+)*)\.?\s+(.*)", title)
            if m and m.group(1) not in out:
                out[m.group(1)] = ManualRef(section=m.group(1), title=m.group(2).strip(),
                                            page=reader.get_destination_page_number(item) + 1)

    walk(reader.outline)
    return out


@functools.lru_cache(maxsize=2)
def _cached_outline(pdf: Path, mtime: float) -> dict[str, ManualRef]:
    return outline_from_pdf(pdf)


def manual_outline() -> dict[str, ManualRef]:
    """Sommaire du manuel, lu une fois par version du fichier ; {} sans PDF."""
    if not MANUAL_PDF.exists():
        return {}
    return _cached_outline(MANUAL_PDF, MANUAL_PDF.stat().st_mtime)


def is_doctrine_ref(text: str, start: int, num: str, in_doctrine: bool) -> bool:
    """`doctrine §3` (ou `§3` a un niveau dans la doctrine) vise la doctrine, pas le manuel."""
    return (in_doctrine and "." not in num) or bool(_DOCTRINE_BEFORE.search(text[max(0, start - 30):start]))


def manual_refs(text: str, outline: dict[str, ManualRef],
                in_doctrine: bool = False) -> list[ManualRef]:
    """References `§x.y` (et bornes de plages `§12.6-12.9`) resolues, sans doublon."""
    seen: dict[str, ManualRef] = {}
    for m in _SECTION_REF.finditer(text):
        if is_doctrine_ref(text, m.start(), m.group(1), in_doctrine):
            continue
        for num in filter(None, m.groups()):
            ref = outline.get(num)
            if ref is not None and num not in seen:
                seen[num] = ref
    return list(seen.values())


def read_note(rel_path: str) -> KbNote | None:
    """Note du corpus uniquement (pas de chemin libre)."""
    allowed = {f.relative_to(VAULT_ROOT).as_posix(): f for f in corpus_files()}
    path = allowed.get(rel_path)
    if path is None:
        return None
    raw = path.read_text(encoding="utf-8")
    text = strip_frontmatter(raw)
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    outline = manual_outline()
    header = manual_refs(parse_frontmatter(raw).get("manuel", ""), outline)
    index = {r.section: r for r in header + manual_refs(text, outline, path == DOCTRINE)}
    return KbNote(path=rel_path, title=m.group(1).strip() if m else path.stem, markdown=text,
                  manual=header, manual_index=index)


def table_of_contents() -> list[KbLot]:
    """Fiches rangees par lot puis `ordre` ; noms des lots tires du hub `_index.md`."""
    names = ({int(n): name for n, name in _LOT_HEADING.findall(KB_INDEX.read_text(encoding="utf-8"))}
             if KB_INDEX.exists() else {})
    lots: dict[int, list[KbEntry]] = {}
    for f in corpus_files():
        if f == DOCTRINE:
            continue
        raw = f.read_text(encoding="utf-8")
        fm = parse_frontmatter(raw)
        if not fm.get("lot", "").isdigit():
            continue
        m = re.search(r"^#\s+(.+)$", strip_frontmatter(raw), re.MULTILINE)
        lots.setdefault(int(fm["lot"]), []).append(KbEntry(
            path=f.relative_to(VAULT_ROOT).as_posix(),
            title=fm.get("theme") or (m.group(1).strip() if m else f.stem),
            ordre=int(fm["ordre"]) if fm.get("ordre", "").isdigit() else 0,
            statut=fm.get("statut", "")))
    return [KbLot(number=n, name=names.get(n, f"Lot {n}"),
                  notes=sorted(entries, key=lambda e: (e.ordre, e.title)))
            for n, entries in sorted(lots.items())]


def main() -> int:
    parser = argparse.ArgumentParser(description="Base de connaissance Digitakt II.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_search = sub.add_parser("search", help="Recherche plein texte")
    p_search.add_argument("query")
    p_search.add_argument("--limit", type=int, default=10)
    sub.add_parser("toc", help="Sommaire des fiches par lot")
    args = parser.parse_args()

    if args.cmd == "search":
        for h in search(args.query, load_corpus(), args.limit):
            print(f"{h.score:5.0f}  {h.path}#{h.anchor}  {h.heading or h.title}")
            print(f"       {h.snippet}")
    elif args.cmd == "toc":
        for lot in table_of_contents():
            print(f"Lot {lot.number} — {lot.name}")
            for e in lot.notes:
                print(f"  {e.ordre:2d}  {e.title}  ({e.path}, {e.statut})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

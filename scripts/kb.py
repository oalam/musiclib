#!/usr/bin/env python3
"""Base de connaissance Digitakt II (Phase 7.D) : notes markdown + recherche.

Corpus = `digitakt/kb/*.md` + `digitakt/doctrine.md`, decoupes en sections
(titres `##` / `###`). Recherche plein texte sans index ni RAG : le corpus
tient en memoire, on le relit a chaque requete (les notes editees dans
Obsidian sont vues tout de suite).

Usage:
    kb.py search "pattern modele"        # resultats en console
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel

VAULT_ROOT = Path(__file__).resolve().parent.parent
KB_DIR = VAULT_ROOT / "digitakt" / "kb"
DOCTRINE = VAULT_ROOT / "digitakt" / "doctrine.md"

_HEADING = re.compile(r"^(#{1,3})\s+(.+?)\s*$")
_SNIPPET_CHARS = 90
_HEADING_BONUS = 5


class KbHit(BaseModel):
    """Une section qui contient tous les termes de la requete."""
    path: str          # relatif au vault, ex. digitakt/kb/fill.md
    title: str         # titre de la note
    heading: str       # titre de la section ("" = chapeau de la note)
    anchor: str        # ancre de la section dans la note rendue
    snippet: str       # extrait autour de la 1re occurrence
    score: float


class KbNote(BaseModel):
    path: str
    title: str
    markdown: str      # sans frontmatter


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


def read_note(rel_path: str) -> KbNote | None:
    """Note du corpus uniquement (pas de chemin libre)."""
    allowed = {f.relative_to(VAULT_ROOT).as_posix(): f for f in corpus_files()}
    path = allowed.get(rel_path)
    if path is None:
        return None
    text = strip_frontmatter(path.read_text(encoding="utf-8"))
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return KbNote(path=rel_path, title=m.group(1).strip() if m else path.stem, markdown=text)


def main() -> int:
    parser = argparse.ArgumentParser(description="Base de connaissance Digitakt II.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_search = sub.add_parser("search", help="Recherche plein texte")
    p_search.add_argument("query")
    p_search.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    if args.cmd == "search":
        for h in search(args.query, load_corpus(), args.limit):
            print(f"{h.score:5.0f}  {h.path}#{h.anchor}  {h.heading or h.title}")
            print(f"       {h.snippet}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

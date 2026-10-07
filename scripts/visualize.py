#!/usr/bin/env python3
"""Genere une PNG signature pour chaque track de la library.

Format : 1200x320 px, header + waveform RMS + mel-spectrogram + bande
de structure colorée + cue points overlay. Stocké dans
`<MEDIA>/Mix/visuals/<slug>.png`.

Usage:
    visualize.py                 # toute la library
    visualize.py SLUG [SLUG ...] # tracks spécifiques par slug
    visualize.py --force         # regenere meme si PNG existe
"""
from __future__ import annotations

import argparse
import json
import sys

from analyzer.visualize import render_track, write_index_md
from library_md import parse_library

from paths import LIBRARY_FILE, QUALITY_DIR, VISUALS_DIR, media_ok
from paths import resolve_audio as _resolve_audio_path



def _load_sidecar(slug: str) -> dict | None:
    path = QUALITY_DIR / f"{slug}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def render_one(slug: str, entry: dict[str, str], force: bool) -> str:
    """Retourne un message de status pour ce slug."""
    out_path = VISUALS_DIR / f"{slug}.png"
    if out_path.exists() and not force:
        return f"  skip   {slug} (existe deja, --force pour ecraser)"

    audio = _resolve_audio_path(entry)
    if not audio:
        return f"  miss   {slug} (audio introuvable)"

    sidecar = _load_sidecar(slug) or {}
    try:
        render_track(audio, entry, sidecar, out_path)
    except Exception as exc:  # noqa: BLE001
        return f"  ERROR  {slug} : {exc}"
    return f"  ok     {slug} -> {out_path}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("slugs", nargs="*", help="Slugs a renderiser (sinon : tout)")
    parser.add_argument("--force", action="store_true",
                        help="Regenere meme si la PNG existe deja")
    args = parser.parse_args()
    if not media_ok():
        return 2

    entries = parse_library(LIBRARY_FILE)
    if not entries:
        print("[ERROR] library.md vide ou introuvable", file=sys.stderr)
        return 1

    if args.slugs:
        targets = [(s, entries[s]) for s in args.slugs if s in entries]
        unknown = [s for s in args.slugs if s not in entries]
        for s in unknown:
            print(f"  skip   {s} (slug inconnu)", file=sys.stderr)
    else:
        targets = sorted(entries.items())

    if not targets:
        print("Aucun slug a traiter.")
        return 1

    print(f"[visualize] {len(targets)} track(s) -> {VISUALS_DIR}/")
    for slug, entry in targets:
        print(render_one(slug, entry, args.force))

    # Genere un index Markdown qui embarque toutes les PNG (browse Obsidian)
    if not args.slugs:  # uniquement quand on a fait toute la library
        index_path = write_index_md(entries, VISUALS_DIR)
        print(f"[index] {index_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

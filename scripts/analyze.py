#!/usr/bin/env python3
"""Analyse audiophile d'un fichier audio.

Pipeline Phase 1 :
- metadata ffprobe (codec / bitrate / sr / bit depth)
- peak / true peak / clipping
- LUFS integre + loudness range
- crest factor
- bandwidth + fake-lossless detection
- score audiophile pondere

Usage:
    analyze.py FILE [FILE ...]
    analyze.py --all              # tous les morceaux de library/audio/
    analyze.py --json FILE        # JSON sur stdout
    analyze.py --update-library   # ecrit aussi quality_score dans library.md

Les rapports JSON sont sauves dans `library/quality/<slug>.json`.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from analyzer.pipeline import analyze_file as _analyze
from analyzer.report import render_terminal, save_sidecar
from analyzer.types import QualityReport
from library_md import find_entry_by_file, update_field

from paths import AUDIO_DIR, LIBRARY_FILE, QUALITY_DIR, VAULT_ROOT, media_ok, mix_relative

KNOWN_EXTS = (".flac", ".opus", ".m4a", ".mp3", ".ogg", ".wav", ".aiff", ".webm")


def analyze_file(path: Path, with_structure: bool = True) -> QualityReport:
    """Wrapper qui resout artist/title/slug/bpm depuis library.md avant analyse."""
    entry = find_entry_by_file(LIBRARY_FILE, path.name)
    artist = entry[1].get("artist") if entry else None
    title = entry[1].get("title") if entry else None
    slug = entry[0] if entry else path.stem
    override_bpm: float | None = None
    if entry:
        raw_bpm = entry[1].get("bpm", "").strip()
        if raw_bpm:
            try:
                v = float(raw_bpm)
                if v > 0:
                    override_bpm = v
            except ValueError:
                pass
    file_path_str = mix_relative(path)
    return _analyze(
        path=path,
        slug=slug,
        artist=artist,
        title=title,
        with_structure=with_structure,
        file_path_str=file_path_str,
        override_bpm=override_bpm,
    )


def resolve_files(args_files: list[str], all_flag: bool) -> list[Path]:
    if all_flag:
        if not AUDIO_DIR.exists():
            return []
        # rglob : les fichiers sont ranges dans des sous-dossiers par style
        return sorted(
            p for p in AUDIO_DIR.rglob("*")
            if p.is_file() and p.suffix.lower() in KNOWN_EXTS
        )
    files: list[Path] = []
    for arg in args_files:
        p = Path(arg)
        if p.is_absolute() and p.exists():
            files.append(p)
            continue
        # Resolution relative : cwd, puis library/audio/
        relative = Path.cwd() / arg
        if relative.exists():
            files.append(relative)
            continue
        in_lib = AUDIO_DIR / arg
        if in_lib.exists():
            files.append(in_lib)
            continue
        print(f"[ERROR] introuvable : {arg}", file=sys.stderr)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyse audiophile d'un fichier audio.")
    parser.add_argument("files", nargs="*", help="Fichiers a analyser.")
    parser.add_argument("--all", action="store_true",
                        help="Analyser tous les fichiers de library/audio/.")
    parser.add_argument("--json", action="store_true",
                        help="Imprime le JSON sur stdout (pas de rapport texte).")
    parser.add_argument("--no-sidecar", action="store_true",
                        help="Ne pas ecrire le JSON dans library/quality/.")
    parser.add_argument("--update-library", action="store_true", default=True,
                        help="Ecrit quality_score dans library.md (defaut: on).")
    parser.add_argument("--no-update-library", dest="update_library",
                        action="store_false")
    parser.add_argument("--quick", action="store_true",
                        help="Phase 1 seulement (skip beats / structure / cues).")
    args = parser.parse_args()

    if args.all and not media_ok():
        return 2
    files = resolve_files(args.files, args.all)
    if not files:
        if not args.files and not args.all:
            parser.print_help()
        return 1

    exit_code = 0
    for path in files:
        try:
            report = analyze_file(path, with_structure=not args.quick)
        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] {path}: {exc}", file=sys.stderr)
            exit_code = 1
            continue

        if not args.no_sidecar:
            sidecar = save_sidecar(report, QUALITY_DIR)
            if not args.json:
                print(f"[sidecar] {sidecar.relative_to(VAULT_ROOT)}")

        if args.update_library:
            updated = update_field(
                LIBRARY_FILE, report.slug, "quality_score",
                f"{report.quality.score:.1f}",
            )
            if report.frequency_bands:
                from analyzer.frequency_bands import to_compact_string
                update_field(
                    LIBRARY_FILE, report.slug, "band_profile",
                    to_compact_string(report.frequency_bands),
                )
            if not args.json:
                msg = "library.md mis a jour" if updated else "library.md : pas d'entree, skip"
                print(f"[library] {msg}")

        if args.json:
            print(report.model_dump_json(indent=2))
        else:
            print(render_terminal(report))
            print()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())

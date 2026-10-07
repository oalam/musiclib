#!/usr/bin/env python3
"""Demucs stems separation (Phase 6.B).

Pour chaque track de la library, separe en 4 stems via Demucs (Meta) :
- drums.wav  : kicks, snares, hats
- bass.wav   : basses (sub + bass guitare/synth)
- other.wav  : melodie / harmonie / FX
- vocals.wav : voix (si presentes)

Sortie : `<MEDIA>/Mix/stems/<slug>/{drums,bass,other,vocals}.wav`. Met a jour
le champ `has_stems` dans library.md.

Usage:
    stems.py [SLUG ...]   # tracks specifiques (sinon prompt)
    stems.py --all        # toute la library
    stems.py --model X    # demucs model name (defaut htdemucs)
    stems.py --force      # re-genere meme si stems existent

CPU recommande : 30-60s par track sur M1/M2. GPU detecte auto."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from library_md import parse_library, update_field

from paths import LIBRARY_FILE, STEMS_DIR, media_ok
from paths import resolve_audio as _resolve_audio_path

STEM_NAMES = ("drums", "bass", "other", "vocals")


def _autodetect_device() -> str:
    """Detecte CUDA / MPS (Apple Silicon GPU) / fallback CPU."""
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
        if torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass
    return "cpu"


def _stems_exist(slug: str) -> bool:
    return all((STEMS_DIR / slug / f"{s}.wav").exists() for s in STEM_NAMES)


def separate(
    audio_path: Path,
    slug: str,
    model: str = "htdemucs",
    device: str = "auto",
) -> dict[str, Path]:
    """Lance demucs et aplatit la sortie en STEMS_DIR/<slug>/<stem>.wav.

    Demucs ecrit toujours dans `<out>/<model>/<audio_stem>/<stem>.wav` (le
    `--filename` ne contourne pas le sous-dossier modele). On move/rename
    apres coup pour garder l'arborescence simple.

    `device` = "auto" / "cpu" / "cuda" / "mps" (Apple Silicon GPU)."""
    out_dir = STEMS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    if device == "auto":
        device = _autodetect_device()
    cmd = [
        sys.executable, "-m", "demucs.separate",
        "-n", model,
        "-d", device,
        "--out", str(out_dir),
        str(audio_path),
    ]
    subprocess.run(cmd, check=True)

    # Demucs ecrit dans <out>/<model>/<audio_stem>/{stem}.wav
    src_dir = out_dir / model / audio_path.stem
    if not src_dir.exists():
        raise FileNotFoundError(
            f"Sortie demucs introuvable a {src_dir} (slug={slug})"
        )

    dest_dir = out_dir / slug
    dest_dir.mkdir(parents=True, exist_ok=True)
    result: dict[str, Path] = {}
    for stem in STEM_NAMES:
        src = src_dir / f"{stem}.wav"
        dst = dest_dir / f"{stem}.wav"
        if src.exists():
            if dst.exists():
                dst.unlink()
            src.rename(dst)
            result[stem] = dst

    # Cleanup : remove now-empty intermediate dirs
    try:
        src_dir.rmdir()
    except OSError:
        pass
    try:
        (out_dir / model).rmdir()
    except OSError:
        pass

    return result


def process_one(
    slug: str,
    entry: dict[str, str],
    force: bool,
    model: str,
    device: str,
    cleanup: bool,
) -> str:
    audio = _resolve_audio_path(entry)
    if not audio:
        return f"  miss   {slug} (audio introuvable)"
    already_exists = _stems_exist(slug)
    if already_exists and not force and not cleanup:
        update_field(LIBRARY_FILE, slug, "has_stems", "yes")
        return f"  skip   {slug} (stems existent, --force pour re-generer)"

    if not already_exists or force:
        print(f"  proc   {slug} ...")
        try:
            separate(audio, slug, model=model, device=device)
        except subprocess.CalledProcessError as exc:
            return f"  ERROR  {slug} : demucs a echoue ({exc})"

    has_stems_value = "yes"
    cleanup_summary = ""
    if cleanup:
        from analyzer.stems_cleanup import cleanup_techno
        try:
            actions = cleanup_techno(STEMS_DIR / slug)
            has_stems_value = "cleaned"
            cleanup_summary = "  | " + ", ".join(f"{k}:{v}" for k, v in actions.items())
        except Exception as exc:  # noqa: BLE001
            cleanup_summary = f"  [warn] cleanup echec : {exc}"

    update_field(LIBRARY_FILE, slug, "has_stems", has_stems_value)
    return f"  ok     {slug} -> {STEMS_DIR / slug}/*.wav{cleanup_summary}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("slugs", nargs="*", help="Slugs a traiter (sinon : tout)")
    parser.add_argument("--all", action="store_true",
                        help="Traiter toute la library")
    parser.add_argument("--force", action="store_true",
                        help="Regenere meme si stems existent")
    parser.add_argument("--model", default="htdemucs",
                        help="Modele Demucs (defaut htdemucs)")
    parser.add_argument("--device", default="auto",
                        choices=("auto", "cpu", "cuda", "mps"),
                        help="Device : auto (defaut, CUDA > MPS > CPU), "
                             "ou force cpu/cuda/mps")
    parser.add_argument("--cleanup", action="store_true",
                        help="Applique le post-processing techno-aware "
                             "apres demucs (highpass bass 60Hz, lowpass 500Hz, "
                             "merge vocals si silence). A activer pour tribe/techno.")
    args = parser.parse_args()
    if not media_ok():
        return 2

    entries = parse_library(LIBRARY_FILE)
    if not entries:
        print("[ERROR] library.md vide", file=sys.stderr)
        return 1

    if args.slugs:
        targets = [(s, entries[s]) for s in args.slugs if s in entries]
        for s in args.slugs:
            if s not in entries:
                print(f"  skip   {s} (slug inconnu)", file=sys.stderr)
    elif args.all:
        targets = sorted(entries.items())
    else:
        parser.print_help()
        return 1

    actual_device = _autodetect_device() if args.device == "auto" else args.device
    print(f"[stems] {len(targets)} track(s) — modele {args.model} — device {actual_device}")
    if actual_device == "cpu":
        print("        CPU ~30-60s/track\n")
    elif actual_device == "mps":
        print("        Apple Silicon GPU (MPS) ~5-15s/track\n")
    else:
        print()
    for slug, entry in targets:
        print(process_one(slug, entry, args.force, args.model, args.device, args.cleanup))
    return 0


if __name__ == "__main__":
    sys.exit(main())

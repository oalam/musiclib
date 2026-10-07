#!/usr/bin/env python3
"""Migration one-shot : media de `library/` vers le disque externe (cf. paths.py).

Rejouable : chaque etape saute ce qui est deja fait.

    migrate_media.py              # copie + transcodage + reecriture des refs
    migrate_media.py --dry-run    # affiche le plan sans rien ecrire
    migrate_media.py --cleanup    # apres verification : supprime les copies
                                  # du vault et pose les symlinks Obsidian

Etapes :
  1. rsync vault -> disque (audio, stems, visuals, renoise, grooves, MIDI Digitakt)
  2. transcodage opus/ogg/webm -> FLAC sur le disque (Rekordbox), tags conserves
  3. library.md : `[[audio/x.opus]]` -> `[[audio/x.flac]]`
  4. sidecars quality/ : `file_path` relatif a Mix/ (`audio/x.flac`)
  5. m3u de sets/ : chemins absolus vers le disque
  6. verification : chaque fichier source a son equivalent sur le disque
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from paths import (
    AUDIO_DIR,
    DIGITAKT_DIR,
    DIGITAKT_MIDI_DIR,
    GROOVES_DIR,
    LIBRARY,
    LIBRARY_FILE,
    MEDIA_MARKER,
    MEDIA_ROOT,
    MIX_DIR,
    QUALITY_DIR,
    RENOISE_DIR,
    REKORDBOX_EXTS,
    STEMS_DIR,
    VAULT_ROOT,
    VISUALS_DIR,
)

SETS_DIR = VAULT_ROOT / "sets"
TRANSCODE_EXTS = (".opus", ".ogg", ".webm")

# (source vault, destination disque, symlink dans le vault apres cleanup)
MOVES: list[tuple[Path, Path, bool]] = [
    (LIBRARY / "audio", AUDIO_DIR, True),
    (LIBRARY / "stems", STEMS_DIR, False),
    (LIBRARY / "visuals", VISUALS_DIR, True),
    (LIBRARY / "renoise", RENOISE_DIR, False),
    (LIBRARY / "grooves", GROOVES_DIR, False),
]


class MigrationError(RuntimeError):
    """Etape de migration en echec (disque absent, verification KO...)."""


def _midi_moves() -> list[tuple[Path, Path, bool]]:
    return [(d, DIGITAKT_MIDI_DIR / d.name, False)
            for d in sorted(DIGITAKT_DIR.iterdir()) if d.is_dir()]


def _all_moves() -> list[tuple[Path, Path, bool]]:
    return MOVES + _midi_moves()


def step_copy(dry: bool) -> None:
    for src, dst, _ in _all_moves():
        if not src.exists() or src.is_symlink():
            continue
        print(f"[copy] {src.relative_to(VAULT_ROOT)} -> {dst}")
        if dry:
            continue
        dst.mkdir(parents=True, exist_ok=True)
        subprocess.check_call(["rsync", "-a", "--exclude", ".DS_Store",
                               f"{src}/", f"{dst}/"])


def _flac_target(path: Path) -> Path:
    return path.with_suffix(".flac")


def step_transcode(dry: bool) -> list[Path]:
    """Transcode sur le disque ; renvoie les sources supprimees apres succes."""
    todo = sorted(p for p in AUDIO_DIR.rglob("*")
                  if p.is_file() and p.suffix.lower() in TRANSCODE_EXTS)
    print(f"[flac] {len(todo)} fichier(s) a transcoder")
    done: list[Path] = []
    for src in todo:
        dst = _flac_target(src)
        if dry:
            continue
        if not dst.exists():
            tmp = dst.with_suffix(".tmp.flac")
            subprocess.check_call([
                "ffmpeg", "-v", "error", "-y", "-i", str(src),
                "-map", "0:a", "-map_metadata", "0:s:a:0",
                "-c:a", "flac", "-sample_fmt", "s16", str(tmp),
            ])
            tmp.rename(dst)
        src.unlink()
        done.append(src)
        print(f"  ok  {dst.relative_to(MIX_DIR)}")
    return done


def _swap_ext(rel: str) -> str:
    """`audio/x.opus` -> `audio/x.flac` si le FLAC existe sur le disque."""
    p = Path(rel)
    if p.suffix.lower() in TRANSCODE_EXTS and (MIX_DIR / p.with_suffix(".flac")).exists():
        return p.with_suffix(".flac").as_posix()
    return rel


def step_library_md(dry: bool) -> None:
    text = LIBRARY_FILE.read_text(encoding="utf-8")
    new = re.sub(r"\[\[(audio/[^\]]+)\]\]",
                 lambda m: f"[[{_swap_ext(m.group(1))}]]", text)
    n = sum(a != b for a, b in zip(text.splitlines(), new.splitlines()))
    print(f"[library.md] {n} ligne(s) reecrite(s)")
    if not dry and new != text:
        LIBRARY_FILE.write_text(new, encoding="utf-8")


def step_sidecars(dry: bool) -> None:
    n = 0
    for f in sorted(QUALITY_DIR.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        old = str(data.get("file_path") or "")
        rel = old.removeprefix("library/")
        new = _swap_ext(rel) if rel.startswith("audio/") else old
        if new != old:
            n += 1
            if not dry:
                data["file_path"] = new
                f.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                             encoding="utf-8")
    print(f"[sidecars] {n} file_path reecrit(s)")


def step_m3u(dry: bool) -> None:
    old_root = f"{LIBRARY}/"
    for f in sorted(SETS_DIR.glob("*.m3u*")):
        lines = f.read_text(encoding="utf-8").splitlines()
        out = []
        for line in lines:
            if line.startswith(old_root):
                line = str(MIX_DIR / _swap_ext(line.removeprefix(old_root)))
            out.append(line)
        if out != lines:
            print(f"[m3u] {f.name}")
            if not dry:
                f.write_text("\n".join(out) + "\n", encoding="utf-8")


def step_verify() -> int:
    """Nombre de fichiers source sans equivalent sur le disque."""
    missing = 0
    for src, dst, _ in _all_moves():
        if not src.exists() or src.is_symlink():
            continue
        for p in src.rglob("*"):
            if not p.is_file() or p.name == ".DS_Store":
                continue
            target = dst / p.relative_to(src)
            if p.suffix.lower() in TRANSCODE_EXTS:
                ok = _flac_target(target).exists()
            else:
                ok = target.exists() and target.stat().st_size == p.stat().st_size
            if not ok:
                missing += 1
                print(f"  manquant : {target}", file=sys.stderr)
    print(f"[verify] {missing} fichier(s) manquant(s)")
    return missing


def step_cleanup() -> None:
    if step_verify():
        raise MigrationError("verification KO : cleanup annule")
    for src, dst, link in _all_moves():
        if src.is_symlink() or not src.exists():
            continue
        shutil.rmtree(src)
        if link:
            src.symlink_to(dst, target_is_directory=True)
            print(f"[link] {src.relative_to(VAULT_ROOT)} -> {dst}")
        else:
            print(f"[rm] {src.relative_to(VAULT_ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--cleanup", action="store_true",
                        help="Supprime les copies du vault et pose les symlinks.")
    args = parser.parse_args()

    if not MEDIA_ROOT.is_dir():
        print(f"[media] {MEDIA_ROOT} non monte", file=sys.stderr)
        return 2
    if not args.dry_run:
        MEDIA_MARKER.touch()

    if args.cleanup:
        try:
            step_cleanup()
        except MigrationError as exc:
            print(f"[cleanup] {exc}", file=sys.stderr)
            return 1
        return 0

    step_copy(args.dry_run)
    if not args.dry_run:
        step_transcode(dry=False)
    step_library_md(args.dry_run)
    step_sidecars(args.dry_run)
    step_m3u(args.dry_run)
    if not args.dry_run:
        step_verify()
    print(f"[rekordbox] formats cibles : {', '.join(REKORDBOX_EXTS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

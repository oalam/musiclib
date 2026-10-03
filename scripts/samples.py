#!/usr/bin/env python3
"""Catalogue de banques de samples wav : dedoublonnage + copie selective.

Le dedoublonnage se fait sur le contenu audio decode (PCM), pas sur les
octets du fichier : Maschine et Maschine 2 livrent les memes sons avec des
en-tetes differents (chunk PAD, taille fmt), un hash de fichier les rate.
Seuls les fichiers de meme format (frames, samplerate, canaux) sont lus.

Commandes:
    samples.py scan ROOT [ROOT ...] [--out catalog.csv]
        # l'ordre des ROOT fixe la priorite : en cas de doublon, l'exemplaire
        # du premier ROOT est garde dans le catalogue, les autres vont
        # dans <out>.duplicates.csv
    samples.py copy catalog.csv --dest DIR [--source S] [--category GLOB]
        [--name GLOB] [--max-duration SEC] [--marked] [--dry-run]
        # copie dans DIR/<source>/<category>/<name> ; rejouable (saute les
        # fichiers deja presents avec la meme taille)
"""
from __future__ import annotations

import argparse
import csv
import fnmatch
import hashlib
import shutil
import sys
from collections import defaultdict
from collections.abc import Iterable, Iterator
from pathlib import Path

import soundfile as sf
from pydantic import BaseModel

VAULT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = VAULT_ROOT / "library" / "samples" / "catalog.csv"

AUDIO_EXTS = {".wav", ".aif", ".aiff"}
MARK_VALUES = {"x", "1", "oui", "yes", "y"}
FIELDS = [
    "keep", "source", "category", "name", "duration_s", "samplerate",
    "channels", "subtype", "size_kb", "duplicates", "audio_hash", "path", "duplicate_of",
]


class SamplesError(Exception):
    """Erreur de catalogue (fichier absent, colonne manquante...)."""


class Sample(BaseModel):
    keep: str = ""
    source: str
    category: str
    name: str
    duration_s: float
    samplerate: int
    channels: int
    subtype: str
    size_kb: int
    duplicates: int = 0
    audio_hash: str = ""
    path: str
    duplicate_of: str = ""


def category_of(rel: Path) -> str:
    """Categorie deduite du dossier relatif a la source.

    Pour les arborescences NI (``Samples/Drums/Kick/x.wav``), on retire le
    prefixe ``Samples`` et on garde deux niveaux ; sinon le dossier parent.
    """
    parts = list(rel.parent.parts)
    if parts and parts[0].lower() == "samples":
        parts = parts[1:]
    return "/".join(parts[:2]) if parts else "-"


def iter_audio(root: Path) -> Iterator[Path]:
    for p in sorted(root.rglob("*")):
        if p.suffix.lower() in AUDIO_EXTS and p.is_file() and not p.name.startswith("._"):
            yield p


def probe(path: Path, root: Path) -> Sample | None:
    try:
        info = sf.info(str(path))
    except (RuntimeError, sf.LibsndfileError) as exc:
        print(f"  [skip] {path}: {exc}", file=sys.stderr)
        return None
    rel = path.relative_to(root)
    return Sample(
        source=root.name,
        category=category_of(rel),
        name=path.name,
        duration_s=round(info.frames / info.samplerate, 3) if info.samplerate else 0.0,
        samplerate=info.samplerate,
        channels=info.channels,
        subtype=info.subtype,
        size_kb=path.stat().st_size // 1024,
        path=str(path),
    )


def audio_hash(path: Path) -> str:
    """SHA1 du PCM decode en int32 (insensible aux en-tetes et a la profondeur)."""
    data, _ = sf.read(path, dtype="int32", always_2d=True)
    return hashlib.sha1(data.tobytes()).hexdigest()


def dedupe(samples: list[Sample]) -> tuple[list[Sample], list[Sample]]:
    """Separe uniques et doublons ; l'ordre d'entree fixe la priorite."""
    by_format: dict[tuple[int, int, int], list[Sample]] = defaultdict(list)
    for s in samples:
        frames = round(s.duration_s * s.samplerate)
        by_format[(frames, s.samplerate, s.channels)].append(s)

    candidates = [g for g in by_format.values() if len(g) > 1]
    total = sum(len(g) for g in candidates)
    done = 0
    for group in candidates:
        for s in group:
            try:
                s.audio_hash = audio_hash(Path(s.path))
            except (RuntimeError, sf.LibsndfileError) as exc:
                print(f"  [hash-fail] {s.path}: {exc}", file=sys.stderr)
                s.audio_hash = f"unreadable:{s.path}"
            done += 1
            if done % 1000 == 0:
                print(f"  hash {done}/{total}", file=sys.stderr)

    uniques: list[Sample] = []
    dups: list[Sample] = []
    first: dict[str, Sample] = {}
    for s in samples:
        if not s.audio_hash:
            uniques.append(s)
            continue
        keeper = first.get(s.audio_hash)
        if keeper is None:
            first[s.audio_hash] = s
            uniques.append(s)
        else:
            keeper.duplicates += 1
            s.duplicate_of = keeper.path
            dups.append(s)
    return uniques, dups


def write_csv(path: Path, rows: Iterable[Sample]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r.model_dump())


def read_csv(path: Path) -> list[Sample]:
    if not path.exists():
        raise SamplesError(f"catalogue introuvable : {path}")
    with path.open(newline="", encoding="utf-8") as fh:
        return [Sample.model_validate(row) for row in csv.DictReader(fh)]


def select(
    rows: list[Sample],
    source: str | None = None,
    category: str | None = None,
    name: str | None = None,
    max_duration: float | None = None,
    marked: bool = False,
) -> list[Sample]:
    out = []
    for r in rows:
        if marked and r.keep.strip().lower() not in MARK_VALUES:
            continue
        if source and source.lower() not in r.source.lower():
            continue
        if category and not fnmatch.fnmatch(r.category.lower(), category.lower()):
            continue
        if name and not fnmatch.fnmatch(r.name.lower(), name.lower()):
            continue
        if max_duration is not None and r.duration_s > max_duration:
            continue
        out.append(r)
    return out


def copy_samples(rows: list[Sample], dest: Path, dry_run: bool = False) -> tuple[int, int]:
    """Copie idempotente ; renvoie (copies, deja presents)."""
    copied = skipped = 0
    for r in rows:
        src = Path(r.path)
        target = dest / r.source / r.category / r.name
        if target.exists() and target.stat().st_size == src.stat().st_size:
            skipped += 1
            continue
        if dry_run:
            print(f"  {src} -> {target}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
        copied += 1
    return copied, skipped


def cmd_scan(args: argparse.Namespace) -> int:
    samples: list[Sample] = []
    for root in args.roots:
        if not root.is_dir():
            raise SamplesError(f"dossier introuvable : {root}")
        print(f"scan {root}", file=sys.stderr)
        n0 = len(samples)
        samples.extend(s for p in iter_audio(root) if (s := probe(p, root)))
        print(f"  {len(samples) - n0} fichiers", file=sys.stderr)

    uniques, dups = dedupe(samples)
    write_csv(args.out, uniques)
    dup_path = args.out.with_suffix(".duplicates.csv")
    write_csv(dup_path, dups)

    size_u = sum(s.size_kb for s in uniques) / 1024 / 1024
    size_d = sum(s.size_kb for s in dups) / 1024 / 1024
    print(f"\n{len(samples)} fichiers = {len(uniques)} uniques + {len(dups)} doublons")
    print(f"volume : {size_u:.1f} Go uniques, {size_d:.1f} Go de doublons")
    by_source: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for s in uniques:
        by_source[s.source][0] += 1
    for s in dups:
        by_source[s.source][1] += 1
    for src, (u, d) in by_source.items():
        print(f"  {src}: {u} uniques, {d} doublons")
    print(f"catalogue : {args.out}\ndoublons  : {dup_path}")
    return 0


def cmd_copy(args: argparse.Namespace) -> int:
    rows = select(
        read_csv(args.catalog), args.source, args.category, args.name,
        args.max_duration, args.marked,
    )
    size = sum(r.size_kb for r in rows) / 1024
    print(f"{len(rows)} samples selectionnes ({size:.0f} Mo)")
    copied, skipped = copy_samples(rows, args.dest, args.dry_run)
    verb = "a copier" if args.dry_run else "copies"
    print(f"{copied} {verb}, {skipped} deja presents -> {args.dest}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    sc = sub.add_parser("scan", help="scanne, dedoublonne, ecrit le catalogue")
    sc.add_argument("roots", nargs="+", type=Path)
    sc.add_argument("--out", type=Path, default=DEFAULT_CATALOG)
    sc.set_defaults(func=cmd_scan)

    cp = sub.add_parser("copy", help="copie une selection du catalogue")
    cp.add_argument("catalog", type=Path, nargs="?", default=DEFAULT_CATALOG)
    cp.add_argument("--dest", type=Path, required=True)
    cp.add_argument("--source", help="sous-chaine du nom de source")
    cp.add_argument("--category", help="glob, ex. 'drums/kick' ou 'loops/*'")
    cp.add_argument("--name", help="glob sur le nom de fichier")
    cp.add_argument("--max-duration", type=float)
    cp.add_argument("--marked", action="store_true",
                    help="seulement les lignes dont keep vaut x/1/oui")
    cp.add_argument("--dry-run", action="store_true")
    cp.set_defaults(func=cmd_copy)

    args = ap.parse_args(argv)
    try:
        return int(args.func(args))
    except SamplesError as exc:
        print(f"erreur : {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

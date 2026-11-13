#!/usr/bin/env python3
"""Migration one-shot : packs ranges sous `<MEDIA>/Samples/packs/` (2026-11-06).

Les chemins sources du vault (`Grey Forge/x.wav`) deviennent
`packs/Grey Forge/x.wav` quand le fichier n'existe plus a la racine de
`<MEDIA>/Samples` mais existe sous `packs/`. Rejouable : un chemin deja
prefixe, ou introuvable sous `packs/`, n'est pas touche.

    migrate_packs.py            # reecrit les fichiers (copie .bak avant)
    migrate_packs.py --dry-run  # compte ce qui changerait, sans rien ecrire

Champs reecrits :
  - manifest.json : entries[].source / parent, reserve[].source,
    unclassified[], trashed[] (les kits de trashed_kits restent logiques) ;
  - overrides.json : cles (fichier ou dossier `909/`) et parent ;
  - export.json, lives/*.export.json : source de chaque entree ;
  - lives/*.json (hors index) : items[].source / parent.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from paths import LIBRARY, SAMPLES_META_DIR, SAMPLES_SRC_DIR, media_ok

PACKS = "packs"
LIVES_DIR = LIBRARY / "lives"

Fix = Callable[[str], str]


def make_fix(root: Path) -> Fix:
    """Fonction qui prefixe un chemin source par `packs/` si le fichier (ou le
    dossier, cle `909/`) n'est plus a la racine mais existe sous packs/."""
    def fix(rel: str) -> str:
        if not rel or rel.startswith(PACKS + "/") or rel.startswith("/"):
            return rel
        bare = rel.rstrip("/")
        if (root / bare).exists() or not (root / PACKS / bare).exists():
            return rel
        return f"{PACKS}/{rel}"
    return fix


def _fix_keys(obj: dict[str, Any], keys: tuple[str, ...], fix: Fix) -> int:
    n = 0
    for k in keys:
        v = obj.get(k)
        if isinstance(v, str) and fix(v) != v:
            obj[k] = fix(v)
            n += 1
    return n


def migrate_manifest(data: dict[str, Any], fix: Fix) -> int:
    n = sum(_fix_keys(e, ("source", "parent"), fix) for e in data.get("entries", []))
    n += sum(_fix_keys(r, ("source",), fix) for r in data.get("reserve", []))
    for key in ("unclassified", "trashed"):
        old = data.get(key, [])
        data[key] = [fix(s) for s in old]
        n += sum(a != b for a, b in zip(old, data[key], strict=True))
    return n


def migrate_overrides(data: dict[str, Any], fix: Fix) -> tuple[dict[str, Any], int]:
    out: dict[str, Any] = {}
    n = 0
    for k, v in data.items():
        nk = fix(k)
        n += nk != k
        if isinstance(v, dict):
            n += _fix_keys(v, ("parent",), fix)
        out[nk] = v
    return out, n


def migrate_index(data: dict[str, Any], fix: Fix) -> int:
    return sum(_fix_keys(v, ("source",), fix) for v in data.values() if isinstance(v, dict))


def migrate_live(data: dict[str, Any], fix: Fix) -> int:
    return sum(_fix_keys(it, ("source", "parent"), fix) for it in data.get("items", []))


def run(root: Path, meta: Path, lives: Path, dry_run: bool) -> dict[str, int]:
    """Migre les fichiers du vault ; renvoie le nombre de chemins changes par fichier."""
    fix = make_fix(root)
    report: dict[str, int] = {}
    targets: list[Path] = [meta / "manifest.json", meta / "overrides.json", meta / "export.json"]
    targets += sorted(lives.glob("*.json")) if lives.is_dir() else []
    for path in targets:
        if not path.is_file():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if path.name == "manifest.json":
            n = migrate_manifest(data, fix)
        elif path.name == "overrides.json":
            data, n = migrate_overrides(data, fix)
        elif path.name == "export.json" or path.name.endswith(".export.json"):
            n = migrate_index(data, fix)
        else:
            n = migrate_live(data, fix)
        report[str(path)] = n
        if n and not dry_run:
            shutil.copy2(path, path.with_suffix(path.suffix + ".bak"))
            text = json.dumps(data, ensure_ascii=False, indent=1)
            tmp = path.with_suffix(".tmp")
            tmp.write_text(text + "\n", encoding="utf-8")
            tmp.replace(path)
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    if not media_ok():
        print(f"disque media absent : {SAMPLES_SRC_DIR}", file=sys.stderr)
        return 1
    for path, n in run(SAMPLES_SRC_DIR, SAMPLES_META_DIR, LIVES_DIR, args.dry_run).items():
        print(f"{n:6} {'a changer' if args.dry_run else 'changes'}  {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

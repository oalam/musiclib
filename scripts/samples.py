#!/usr/bin/env python3
"""Bibliotheque de samples DT2 : classement et pre-selection (Phase 7.J1).

Lit la copie des packs (`<MEDIA>/Samples`, jamais modifiee), classe chaque
wav en famille / code, nomme les candidats pour l'ecran de la DT2 et ecrit
le manifeste. Rejouable : les decisions d'ecoute (`keep` / `drop`) du
manifeste precedent sont conservees.

Usage:
    samples.py                 # (re)construit le manifeste et affiche la grille
    samples.py --dry-run       # grille seulement, rien n'est ecrit
    samples.py --report        # grille du manifeste existant
    samples.py --unclassified  # liste les fichiers sans code (a corriger
                               # dans overrides.json)

Fichiers (vault) :
    library/samples/manifest.json   # candidats, noms, statut, selection
    library/samples/overrides.json  # corrections manuelles, cle = chemin source :
        {"rthm/x.wav": {"family": "TRIBE", "code": "BD", "name": "BD Fat 01 rth",
                        "exclude": false}}
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from analyzer.samples import (
    CODES,
    FAMILIES,
    Manifest,
    Override,
    SampleError,
    build_manifest,
    grid,
)
from paths import SAMPLES_META_DIR, SAMPLES_SRC_DIR, media_ok

MANIFEST_FILE = SAMPLES_META_DIR / "manifest.json"
OVERRIDES_FILE = SAMPLES_META_DIR / "overrides.json"


def load_overrides(path: Path) -> dict[str, Override]:
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SampleError(f"{path} : JSON invalide ({exc})") from exc
    return {k: Override.model_validate(v) for k, v in raw.items()}


def load_manifest(path: Path) -> Manifest | None:
    if not path.exists():
        return None
    return Manifest.model_validate_json(path.read_text(encoding="utf-8"))


def render_grid(m: Manifest) -> str:
    """Tableau candidats/retenus par famille x code, totaux en bout de ligne."""
    g = grid(m)
    codes = [c for c in CODES if any(c in g[f] for f in g)]
    lines = ["fam        " + " ".join(f"{c:>7}" for c in codes) + "    total"]
    tot_n = tot_s = 0
    for fam in FAMILIES:
        if fam not in g:
            continue
        cells = g[fam]
        n = sum(v[0] for v in cells.values())
        s = sum(v[1] for v in cells.values())
        tot_n, tot_s = tot_n + n, tot_s + s
        row = " ".join(f"{(f'{cells[c][1]}/{cells[c][0]}' if c in cells else '.'):>7}" for c in codes)
        lines.append(f"{fam:10} {row}  {s:>4}/{n}")
    lines.append(f"retenus/candidats : {tot_s}/{tot_n} ; fichiers sources : {m.total} ; "
                 f"non classes : {len(m.unclassified)}")
    if m.folded:
        lines.append("cases repliees dans UNIVERSEL : " + ", ".join(m.folded))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="n'ecrit pas le manifeste")
    ap.add_argument("--report", action="store_true", help="grille du manifeste existant")
    ap.add_argument("--unclassified", action="store_true", help="liste les fichiers sans code")
    ap.add_argument("--source", type=Path, default=SAMPLES_SRC_DIR)
    args = ap.parse_args(argv)

    try:
        previous = load_manifest(MANIFEST_FILE)
        if args.report or args.unclassified:
            if previous is None:
                print(f"pas de manifeste : {MANIFEST_FILE}", file=sys.stderr)
                return 1
            print("\n".join(previous.unclassified) if args.unclassified else render_grid(previous))
            return 0

        if args.source == SAMPLES_SRC_DIR and not media_ok():
            return 1
        if not args.source.is_dir():
            print(f"source introuvable : {args.source}", file=sys.stderr)
            return 1
        manifest = build_manifest(args.source, load_overrides(OVERRIDES_FILE), previous)
    except SampleError as exc:
        print(f"[samples] {exc}", file=sys.stderr)
        return 1

    print(render_grid(manifest))
    if not args.dry_run:
        MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST_FILE.write_text(manifest.model_dump_json(indent=1) + "\n", encoding="utf-8")
        print(f"manifeste : {MANIFEST_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

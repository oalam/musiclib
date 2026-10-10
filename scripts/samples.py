#!/usr/bin/env python3
"""Bibliotheque de samples DT2 : classement, pre-selection et export (Phase 7.J).

Lit la copie des packs (`<MEDIA>/Samples`, jamais modifiee), classe chaque
wav en famille / code / sous-categorie, range les candidats par dossier final
du +Drive (`DRUMS/BD/HARD`, `LOOPS/BR`... : 7.J8), nomme les candidats pour l'ecran de la DT2 et ecrit
le manifeste. Chaque candidat est mesure (pre-filtre 7.J2 : drapeaux muet,
faible, sature, blanc, long, illisible) et les candidats a defauts passent en
fin de case ; les one-shots BD / BS / PD sans note dans le nom recoivent
leur note mesuree (7.J7). Rejouable : les decisions d'ecoute (`keep` / `drop`, prises dans
le front) et les mesures du manifeste precedent sont conservees.

Usage:
    samples.py                 # (re)construit le manifeste et affiche la grille
    samples.py --dry-run       # grille seulement, rien n'est ecrit
    samples.py --no-measure    # sans pre-filtre qualite ni note (pas de lecture audio)
    samples.py --report        # grille du manifeste existant
    samples.py --unclassified  # liste les fichiers sans code (a corriger
                               # dans overrides.json)
    samples.py --tag-report    # mots de dossiers frequents hors du dictionnaire
                               # de tags inferes (7.J6)
    samples.py --export        # copie les retenus vers <MEDIA>/Live/samples (7.J3)
    samples.py --export --dry-run   # bilan de l'export sans rien ecrire

Fichiers (vault) :
    library/samples/manifest.json   # candidats, noms, statut, selection
    library/samples/export.json     # fichiers ecrits par l'export (seuls retirables)
    library/samples/overrides.json  # corrections manuelles, cle = chemin source :
        {"rthm/x.wav": {"family": "TRIBE", "code": "BD", "sub": "HARD", "name": "BD Fat 01 rth",
                        "exclude": false, "tags": ["acid"], "stars": 4,
                        "trash": false}}
        tags, etoiles et corbeille (7.J4) sont poses depuis le front ; `exclude`
        ignore le fichier, `trash` le garde visible dans la corbeille. Une cle
        terminee par `/` vise un kit ou un pack (7.J5) : tags herites par ses
        fichiers, `trash` l'exclut d'un bloc :
        {"rthm/packs/neurotek/": {"tags": ["tribe"], "trash": true}}
        `no_auto` (fichier ou prefixe) masque des tags inferes des dossiers (7.J6).
        `family` ne range plus (7.J8) : elle donne le tag de genre ou SAMPLE ;
        `sub` force la sous-categorie ("" = racine du code).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from analyzer.samples import (
    BRANCHES,
    ExportReport,
    Manifest,
    Override,
    SampleError,
    build_manifest,
    check_sub,
    export,
    folder_of,
    has_sub,
    grid,
    measure,
    measure_note,
    register_subs,
    tag_report,
)
from paths import DT2_SAMPLES_DIR, SAMPLES_META_DIR, SAMPLES_SRC_DIR, media_ok

MANIFEST_FILE = SAMPLES_META_DIR / "manifest.json"
OVERRIDES_FILE = SAMPLES_META_DIR / "overrides.json"
EXPORT_INDEX_FILE = SAMPLES_META_DIR / "export.json"
FOLDERS_FILE = SAMPLES_META_DIR / "folders.json"  # sous-dossiers manuels (7.K)


def load_overrides(path: Path) -> dict[str, Override]:
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SampleError(f"{path} : JSON invalide ({exc})") from exc
    return {k: Override.model_validate(v) for k, v in raw.items()}


def load_manual_subs(path: Path) -> dict[str, list[str]]:
    """Sous-dossiers manuels `{"BD": ["RUMBLE"]}`, enregistres dans SUBS."""
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SampleError(f"{path} : JSON invalide ({exc})") from exc
    manual = {str(c): [str(x) for x in subs] for c, subs in raw.items()}
    register_subs(manual)
    return manual


def add_manual_sub(path: Path, code: str, sub: str) -> str:
    """Cree le sous-dossier `sub` de `code` (rejouable, sans effet s'il existe
    deja) ; renvoie le dossier final, ex. `DRUMS/BD/RUMBLE`."""
    name = check_sub(code, sub)
    manual = load_manual_subs(path)
    if not has_sub(code, name):
        manual.setdefault(code, []).append(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(dict(sorted(manual.items())), ensure_ascii=False, indent=1) + "\n",
                       encoding="utf-8")
        tmp.replace(path)
        register_subs(manual)
    return folder_of("", code, name)


def save_overrides(overrides: dict[str, Override], path: Path) -> None:
    """Ecrit les overrides (cle triee, champs par defaut omis), atomique."""
    data = {k: v.model_dump(exclude_defaults=True) for k, v in sorted(overrides.items())}
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    tmp.replace(path)


def load_manifest(path: Path) -> Manifest | None:
    if not path.exists():
        return None
    return Manifest.model_validate_json(path.read_text(encoding="utf-8"))


def save_manifest(m: Manifest, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(m.model_dump_json(indent=1) + "\n", encoding="utf-8")
    tmp.replace(path)   # ecriture atomique : le front ecrit pendant l'ecoute


def render_grid(m: Manifest) -> str:
    """Arbre retenus/candidats par branche puis dossier final, total par branche."""
    g = grid(m)
    lines: list[str] = []
    tot_n = tot_s = 0
    for branch in BRANCHES:
        cells = {f: v for f, v in g.items() if f.split("/")[0] == branch}
        if not cells:
            continue
        n = sum(v[0] for v in cells.values())
        s = sum(v[1] for v in cells.values())
        tot_n, tot_s = tot_n + n, tot_s + s
        lines.append(f"{branch:22} {s:>5}/{n}")
        lines += [f"  {f.split('/', 1)[1] if '/' in f else '.':20} {v[1]:>5}/{v[0]}"
                  for f, v in cells.items()]
    lines.append(f"retenus/candidats : {tot_s}/{tot_n} ; fichiers sources : {m.total} ; "
                 f"non classes : {len(m.unclassified)} ; corbeille : {len(m.trashed)}")
    flagged = Counter(f for e in m.entries for f in e.flags or [])
    if flagged:
        lines.append("drapeaux qualite : " + ", ".join(f"{f} {n}" for f, n in flagged.most_common()))
    if m.folded:
        lines.append("sous-categories remontees a la racine : " + ", ".join(m.folded))
    return "\n".join(lines)


def render_export(r: ExportReport) -> str:
    verb = "a copier" if r.dry_run else "copies"
    gone = "a retirer" if r.dry_run else "retires"
    lines = [f"export{' (simulation)' if r.dry_run else ''} -> {r.dest}",
             f"{r.files} retenus ({r.bytes / 1e6:.0f} Mo) : {len(r.copied)} {verb}, "
             f"{r.unchanged} inchanges, {len(r.removed)} {gone}"]
    if r.missing:
        lines.append(f"sources absentes ({len(r.missing)}) : " + ", ".join(r.missing[:5]))
    if r.conflicts:
        lines.append(f"fichiers poses a la main, non ecrases ({len(r.conflicts)}) : "
                     + ", ".join(r.conflicts[:5]))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="n'ecrit pas le manifeste")
    ap.add_argument("--report", action="store_true", help="grille du manifeste existant")
    ap.add_argument("--unclassified", action="store_true", help="liste les fichiers sans code")
    ap.add_argument("--tag-report", action="store_true",
                    help="mots de dossiers frequents non couverts par les tags inferes")
    ap.add_argument("--export", action="store_true",
                    help="copie les retenus du manifeste vers --dest (avec --dry-run : bilan)")
    ap.add_argument("--dest", type=Path, default=DT2_SAMPLES_DIR)
    ap.add_argument("--no-measure", action="store_true",
                    help="saute la mesure qualite des nouveaux candidats")
    ap.add_argument("--source", type=Path, default=SAMPLES_SRC_DIR)
    args = ap.parse_args(argv)

    try:
        load_manual_subs(FOLDERS_FILE)
        previous = load_manifest(MANIFEST_FILE)
        if args.export:
            if previous is None:
                print(f"pas de manifeste : {MANIFEST_FILE}", file=sys.stderr)
                return 1
            if args.source == SAMPLES_SRC_DIR and not media_ok():
                return 1
            print(render_export(export(previous, args.source, args.dest, EXPORT_INDEX_FILE,
                                       dry_run=args.dry_run)))
            return 0
        if args.tag_report:
            if previous is None:
                print(f"pas de manifeste : {MANIFEST_FILE}", file=sys.stderr)
                return 1
            srcs = ([e.source for e in previous.entries] + [r.source for r in previous.reserve]
                    + previous.unclassified)
            print("\n".join(f"{n:6} {w}" for w, n in tag_report(srcs)))
            return 0
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
        manifest = build_manifest(args.source, load_overrides(OVERRIDES_FILE), previous,
                                  measure_fn=None if args.no_measure else measure,
                                  note_fn=None if args.no_measure else measure_note)
    except SampleError as exc:
        print(f"[samples] {exc}", file=sys.stderr)
        return 1

    print(render_grid(manifest))
    if not args.dry_run:
        save_manifest(manifest, MANIFEST_FILE)
        print(f"manifeste : {MANIFEST_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

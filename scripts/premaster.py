#!/usr/bin/env python3
"""Import de samples de pack sur la ligne inclinee (doctrine-samples, « Niveaux »).

Chaque son est mis en forme pour le pack perso (`/Users/tom/Documents/samples/solaris`) :
48 kHz / 24 bits, coupure sous 20 Hz, passe-haut de la famille, mono sous
120 Hz (grave entierement mono), gain qui pose le haut de son spectre incline
(+4,5 dB/oct) sur la ligne du kick de reference, crete au plus a -6 dBFS. Pas
de normalisation. Le reste (debut, fin, creux) se fait a l'oreille dans Live
(`digitakt/kb/tutos/maison-premaster-samples.md`).

Sortie : `<DEST>/NN NOM/<CODE> <desc> <pack>.wav` (arbre numerote, noms de 18
caracteres), plus `<DEST>/_import.tsv` (source, cible, gain, crete, plafond).
Rejouable : les fichiers cibles sont reecrits a l'identique.

Usage:
    premaster.py ref REF.wav                      # valeur de la ligne du kick de reference
    premaster.py import SRC DEST --ref REF.wav    # importe tout SRC (dossiers Serum : Kick, Hat...)
    premaster.py import SRC DEST --ref REF.wav --pack sr2 --dry-run
    premaster.py apply ROOT --ref REF.wav --code ML FICHIER...   # sons deja dans le pack

`apply` traite des fichiers du pack (ROOT = racine solaris) : l'original part
dans `ROOT/_backup/<date>/<chemin>` et sert de source aux passages suivants
(rejouable sans double filtrage) ; le resultat va dans le dossier du code,
prefixe de code mis a jour (`BL 145 Deep 1 slr` -> `18 MELO LOOP/ML 145 Deep 1 slr`).
"""
from __future__ import annotations

import argparse
import csv
import shutil
from datetime import date
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from pydantic import BaseModel

from analyzer.line import FAMILY, TARGET_SR, LineError, load_shaped, on_line
from analyzer.line import ref_line as _ref_line
from analyzer.samples import EXPORT_FOLDERS, NAME_MAX, unique_name

SUBTYPE = "PCM_24"
AUDIO_EXT = {".wav", ".flac", ".aif", ".aiff"}
# Dossiers de pack -> code de la doctrine (Serum 2, Factory Non-Tonal/Drum)
FOLDER_CODES = {"kick": "BD", "clap": "CP", "snare": "SD", "tom": "TM",
                "perc": "PC", "conga": "PC", "cowbell": "PC", "rim": "PC",
                "shaker": "PC", "cymbal": "CY", "hat": "HH"}
OPEN_WORDS = ("open", " oh")   # dans un dossier Hat : charleston ouverte
# mots qui redisent le code, retires du nom (le code est deja en tete)
CODE_WORDS = {"kick", "clap", "snare", "tom", "perc", "percussion", "cymbal", "hat",
              "closed", "open", "oh", "hh", "bd", "sd", "cp"}


class PremasterError(ValueError):
    """Source ou reference inexploitable."""


class ImportRow(BaseModel):
    source: str
    dest: str
    code: str
    gain_db: float
    peak_db: float
    capped: bool


def code_of(rel: Path) -> str | None:
    """Code d'un fichier d'apres son premier dossier (`Hat/Open Hat 1.flac` -> OH)."""
    if len(rel.parts) < 2:
        return None
    code = FOLDER_CODES.get(rel.parts[0].lower())
    if code == "HH" and any(w in f" {rel.stem.lower()}" for w in OPEN_WORDS):
        return "OH"
    return code


def import_name(rel: Path, code: str, pack: str) -> str:
    """`<CODE> <desc> <pack>`, NAME_MAX caracteres : le nom de la source sans
    les mots qui redisent le code, machines gardees (`808 Snare C 01` ->
    `SD 808 C 01 sr2`)."""
    toks = re.findall(r"[A-Za-z0-9]+", rel.stem)
    words = [t for t in toks if t.lower() not in CODE_WORDS] or toks
    budget = NAME_MAX - len(code) - len(pack) - 2
    desc = " ".join(words)[:budget].rstrip()
    return f"{code} {desc} {pack}"


def load(path: Path, code: str) -> np.ndarray:
    """Lit, met en forme (famille) et passe a 48 kHz."""
    return load_shaped(path, code)


def ref_line(ref: Path) -> float:
    """Ligne = haut du spectre incline du kick de reference, a son niveau."""
    try:
        return _ref_line(ref)
    except LineError as e:
        raise PremasterError(str(e)) from e


def plan(src: Path, pack: str) -> list[tuple[Path, str, str]]:
    """(source, code, chemin cible relatif), dans l'ordre du disque, noms uniques."""
    taken: dict[str, set[str]] = {}
    out = []
    for path in sorted(p for p in src.rglob("*") if p.suffix.lower() in AUDIO_EXT):
        rel = path.relative_to(src)
        code = code_of(rel)
        if code is None:
            continue
        folder = EXPORT_FOLDERS[code]
        name = unique_name(import_name(rel, code, pack), taken.setdefault(folder, set()))
        taken[folder].add(name)
        out.append((path, code, f"{folder}/{name}.wav"))
    return out


def run_import(src: Path, dest: Path, ref: Path, pack: str,
               dry_run: bool = False) -> list[ImportRow]:
    line = ref_line(ref)
    rows = []
    for path, code, rel_dest in plan(src, pack):
        try:
            y, res = on_line(load(path, code), TARGET_SR, code, line)
        except (LineError, RuntimeError) as e:
            print(f"  ignore {path.relative_to(src)} : {e}", file=sys.stderr)
            continue
        if not dry_run:
            out = dest / rel_dest
            out.parent.mkdir(parents=True, exist_ok=True)
            sf.write(out, y, TARGET_SR, subtype=SUBTYPE)
        rows.append(ImportRow(source=str(path.relative_to(src)), dest=rel_dest, code=code,
                              gain_db=res.gain_db, peak_db=res.peak_db, capped=res.capped))
    if not dry_run:
        with open(dest / "_import.tsv", "w", newline="") as f:
            w = csv.writer(f, delimiter="\t")
            w.writerow(ImportRow.model_fields)
            w.writerows([list(r.model_dump().values()) for r in rows])
    return rows


def apply(root: Path, ref: Path, code: str, files: list[Path],
          day: str | None = None) -> list[ImportRow]:
    """Met des sons du pack sur la ligne avec les reglages de `code`, en place."""
    if code not in EXPORT_FOLDERS:
        raise PremasterError(f"code inconnu : {code}")
    line = ref_line(ref)
    backup = root / "_backup" / (day or date.today().isoformat())
    rows = []
    for f in files:
        rel = f.resolve().relative_to(root.resolve())
        saved = backup / rel
        if not saved.exists():
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(f), saved)
        y, res = on_line(load(saved, code), TARGET_SR, code, line)
        words = rel.stem.split(" ", 1)
        stem = f"{code} {words[1]}" if len(words) == 2 and words[0] in EXPORT_FOLDERS else rel.stem
        out = root / EXPORT_FOLDERS[code] / f"{stem}.wav"
        out.parent.mkdir(parents=True, exist_ok=True)
        sf.write(out, y, TARGET_SR, subtype=SUBTYPE)
        if f.exists() and f.resolve() != out.resolve():
            f.unlink()
        rows.append(ImportRow(source=str(rel), dest=str(out.relative_to(root)), code=code,
                              gain_db=res.gain_db, peak_db=res.peak_db, capped=res.capped))
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_ref = sub.add_parser("ref", help="valeur de la ligne du kick de reference")
    p_ref.add_argument("ref", type=Path)
    p_imp = sub.add_parser("import", help="importe un dossier de pack sur la ligne")
    p_imp.add_argument("src", type=Path)
    p_imp.add_argument("dest", type=Path)
    p_imp.add_argument("--ref", type=Path, required=True)
    p_imp.add_argument("--pack", default="sr2", help="tag de pack en fin de nom (defaut sr2)")
    p_imp.add_argument("--dry-run", action="store_true")
    p_app = sub.add_parser("apply", help="met des sons du pack sur la ligne, en place")
    p_app.add_argument("root", type=Path)
    p_app.add_argument("files", type=Path, nargs="+")
    p_app.add_argument("--ref", type=Path, required=True)
    p_app.add_argument("--code", required=True)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "ref":
            print(f"ligne = {ref_line(a.ref):.2f} dB (echelle interne)")
            return 0
        if a.cmd == "apply":
            for r in apply(a.root, a.ref, a.code, a.files):
                print(f"{r.source} -> {r.dest}  gain {r.gain_db:+.1f} dB  crete {r.peak_db:.1f}"
                      f"{'  (plafond)' if r.capped else ''}")
            return 0
        rows = run_import(a.src, a.dest, a.ref, a.pack, a.dry_run)
    except PremasterError as e:
        print(f"erreur : {e}", file=sys.stderr)
        return 1
    by_code: dict[str, list[ImportRow]] = {}
    for r in rows:
        by_code.setdefault(r.code, []).append(r)
    for code, rs in sorted(by_code.items(), key=lambda kv: list(FAMILY).index(kv[0])):
        gains = [r.gain_db for r in rs]
        print(f"{code}  {len(rs):3d} sons  gain {min(gains):+6.1f} a {max(gains):+6.1f} dB"
              f"  plafond atteint {sum(r.capped for r in rs)}")
    print(f"{len(rows)} sons {'(simulation)' if a.dry_run else f'ecrits dans {a.dest}'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

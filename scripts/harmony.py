#!/usr/bin/env python3
"""Gamme et accords d'une track de la library (Phase 7.H).

Source preferee : stems Demucs (other = contenu tonal, bass = fondamentale) ;
repli sur le mix (composante harmonique). Grille de mesures : celle de la bank
Digitakt si elle existe (recalee sur le kick, premier temps corrige), sinon les
beats du sidecar regroupes par mesure.

Usage:
    harmony.py <slug>
    harmony.py --all                     # toutes les tracks avec sidecar

Sorties :
    library/quality/<slug>.json          # bloc `harmony` du sidecar
    library/digitakt/<slug>.md           # section Harmonie de la note de bank (si bank)
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from analyzer import harmony
from analyzer.digitakt import render_markdown
from analyzer.infer import load_sidecar
from analyzer.rhythm_signature import _SIG_CONF_THRESHOLD, beats_per_bar
from analyzer.types import DigitaktBank
from digitakt import DIGITAKT_DIR, LIBRARY_FILE, QUALITY_DIR, VAULT_ROOT, DigitaktSourceError, load_sources
from library_md import parse_library


def _grid(sidecar: dict[str, Any], bank: DigitaktBank | None) -> tuple[list[float], list[tuple[str, float, float]]]:
    """Debuts de mesure et sections : bank si possible, sinon sidecar."""
    if bank is not None and len(bank.bar_times_s) > 1:
        sections = [(s.label, s.start_s, s.end_s) for s in bank.sections]
        return list(bank.bar_times_s), sections
    beats = sidecar.get("beats") or {}
    beat_times = beats.get("beat_times_s") or []
    bpb = beats_per_bar(beats.get("time_signature", "4/4"))
    if bpb != 4 and float(beats.get("time_signature_confidence") or 0) < _SIG_CONF_THRESHOLD:
        bpb = 4
    bars = [float(t) for t in beat_times[::bpb]]
    segs = (sidecar.get("structure") or {}).get("segments") or []
    return bars, [(s["label"], float(s["start_s"]), float(s["end_s"])) for s in segs]


def process(slug: str, entries: dict[str, dict[str, str]]) -> int:
    sidecar = load_sidecar(QUALITY_DIR, slug)
    if not sidecar:
        print(f"[ERROR] pas de sidecar pour {slug} (lance analyze.py {slug}).", file=sys.stderr)
        return 1
    bank_path = DIGITAKT_DIR / f"{slug}.json"
    bank = DigitaktBank.model_validate_json(bank_path.read_text(encoding="utf-8")) if bank_path.exists() else None
    bars, sections = _grid(sidecar, bank)
    if len(bars) < 2:
        print(f"[ERROR] pas de grille de mesures pour {slug}.", file=sys.stderr)
        return 1
    try:
        stems, from_stems = load_sources(slug, entries.get(slug, {}))
    except DigitaktSourceError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    tonal, sr = stems["other"]
    bass = stems["bass"][0] if from_stems else None
    result = harmony.analyze(tonal, sr, bars, sections, "stems" if from_stems else "mix", bass)

    sidecar["harmony"] = result.model_dump()
    sidecar_path = QUALITY_DIR / f"{slug}.json"
    sidecar_path.write_text(json.dumps(sidecar, indent=2, ensure_ascii=False), encoding="utf-8")
    written = [sidecar_path]
    if bank is not None:
        md_path = DIGITAKT_DIR / f"{slug}.md"
        md_path.write_text(render_markdown(bank, result), encoding="utf-8")
        written.append(md_path)

    sc = result.scale
    named = sum(c.label != "N" for c in result.chords)
    print(f"Harmonie {slug} : {sc.label} (score {sc.score}, marge {sc.margin}, "
          f"{result.source}) ; {named}/{len(result.chords)} mesures avec accord")
    print(f"  DT2 : {harmony.keyboard_setup(sc)}")
    for p in result.progression:
        print(f"  {p.label:<10} {' - '.join(p.chords) or '-'}")
    for path in written:
        print(f"[export] {path.relative_to(VAULT_ROOT)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Gamme et accords par mesure d'une track.")
    parser.add_argument("slug", nargs="?", help="Slug de la track")
    parser.add_argument("--all", action="store_true", help="Traite toutes les tracks qui ont un sidecar.")
    args = parser.parse_args()
    if not args.slug and not args.all:
        parser.error("donner un slug ou --all")
    entries = parse_library(LIBRARY_FILE)
    slugs = sorted(p.stem for p in QUALITY_DIR.glob("*.json")) if args.all else [args.slug]
    rc = 0
    for slug in slugs:
        rc |= process(slug, entries)
    return rc


if __name__ == "__main__":
    sys.exit(main())

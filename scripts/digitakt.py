#!/usr/bin/env python3
"""Draft de bank Digitakt II depuis une track de la library (Phase 7.B).

1 morceau = 1 bank : chaque section devient un pattern (<= 128 pas), reparti
sur la grille fixe des 16 tracks de `digitakt/doctrine.md`. Source preferee :
les stems Demucs (`stems.py <slug> --cleanup`), fallback mix avec warning.

Usage:
    digitakt.py <slug> [--phrase-bars 8] [--threshold 0.5] [--no-midi]
    digitakt.py --all                    # toutes les tracks avec sidecar

Sorties :
    library/digitakt/<slug>.json         # DigitaktBank (Pydantic) → front
    library/digitakt/<slug>.md           # note Obsidian : mutes + grilles
    library/digitakt/<slug>/pNN.mid      # 1 .mid par pattern, canal = track
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from analyzer.audio_loader import load_audio, to_mono
from analyzer.digitakt import (
    build_bank,
    downbeat_offset,
    kick_shift,
    median_bpm,
    retrack_beats,
    render_markdown,
    shift_features,
    stem_features,
    step_grid,
    write_pattern_midi,
)
from analyzer.infer import load_sidecar
from analyzer.rhythm_signature import _SIG_CONF_THRESHOLD, beats_per_bar
from library_md import parse_library
from stems import _resolve_audio_path

VAULT_ROOT = Path(__file__).resolve().parent.parent
LIBRARY = VAULT_ROOT / "library"
LIBRARY_FILE = LIBRARY / "library.md"
QUALITY_DIR = LIBRARY / "quality"
STEMS_DIR = LIBRARY / "stems"
DIGITAKT_DIR = LIBRARY / "digitakt"
_STEMS = ("drums", "bass", "other", "vocals")


class DigitaktSourceError(Exception):
    """Ni sidecar exploitable, ni audio pour construire la bank."""


def _load_sources(slug: str, entry: dict[str, str]) -> tuple[dict[str, tuple[np.ndarray, int]], bool]:
    """Stems Demucs si presents, sinon le mix route sur tous les roles."""
    stem_dir = STEMS_DIR / slug
    if (stem_dir / "drums.wav").exists():
        out: dict[str, tuple[np.ndarray, int]] = {}
        for name in _STEMS:
            path = stem_dir / f"{name}.wav"
            if path.exists():
                data, sr = load_audio(path)
                out[name] = (to_mono(data), sr)
        return out, True
    mix = _resolve_audio_path(entry)
    if mix is None or not mix.exists():
        raise DigitaktSourceError(f"ni stems ni audio pour {slug}")
    data, sr = load_audio(mix)
    mono = to_mono(data)
    # pas de vocals sur le mix : trop de faux positifs
    return {name: (mono, sr) for name in ("drums", "bass", "other")}, False


def process(slug: str, entries: dict[str, dict[str, str]], phrase_bars: int,
            threshold: float, midi: bool) -> int:
    entry = entries.get(slug, {})
    sidecar = load_sidecar(QUALITY_DIR, slug)
    beats = (sidecar or {}).get("beats") or {}
    beat_times = beats.get("beat_times_s") or []
    if not beat_times:
        print(f"[ERROR] pas de beats pour {slug} (lance analyze.py {slug}).",
              file=sys.stderr)
        return 1
    bpm = float(entry.get("bpm") or beats.get("tempo_bpm") or 0)
    time_sig = beats.get("time_signature", "4/4")
    bpb = beats_per_bar(time_sig)
    if bpb != 4 and float(beats.get("time_signature_confidence") or 0) < _SIG_CONF_THRESHOLD:
        bpb, time_sig = 4, "4/4"
    spb = bpb * 4

    try:
        stems, from_stems = _load_sources(slug, entry)
    except DigitaktSourceError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    if not from_stems:
        print(f"[warn] pas de stems pour {slug} : detection depuis le mix "
              f"(lance stems.py {slug} --cleanup pour un meilleur rendu).")

    drums_y, drums_sr = stems["drums"]
    beat_times = retrack_beats(drums_y, drums_sr, bpm) or beat_times
    tracked = median_bpm(beat_times)
    if bpm <= 0 or abs(tracked - bpm) / bpm > 0.02:
        print(f"[info] tempo recale sur le kick : {bpm:.1f} -> {tracked:.1f} BPM")
        bpm = tracked

    bounds = step_grid(beat_times, bpb, spb)
    feat = stem_features(stems, bounds)
    if 1 in feat.onset:
        feat = shift_features(feat, kick_shift(feat.onset[1], spb))
    beat_off = downbeat_offset(feat, bpb, spb)
    if beat_off:
        print(f"[info] premier temps de la mesure : decalage de {beat_off} temps")
        feat = shift_features(feat, beat_off * (spb // bpb))
    bank = build_bank(slug, entry, bpm, time_sig, bpb, feat, from_stems,
                      phrase_bars, threshold)

    DIGITAKT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = DIGITAKT_DIR / f"{slug}.json"
    json_path.write_text(bank.model_dump_json(indent=2), encoding="utf-8")
    md_path = DIGITAKT_DIR / f"{slug}.md"
    md_path.write_text(render_markdown(bank), encoding="utf-8")
    written = [json_path, md_path]
    if midi:
        for p in bank.patterns:
            out = DIGITAKT_DIR / slug / f"p{p.slot:02d}.mid"
            write_pattern_midi(p, bank.bpm, out)
            written.append(out)

    print(f"Bank {slug} : {len(bank.patterns)} pattern(s), {bank.bpm} BPM, "
          f"{'stems' if from_stems else 'mix'}")
    for p in bank.patterns:
        act = " ".join(str(t.index) for t in p.tracks if t.trigs)
        print(f"  {p.slot:02d} {p.label:<10} {p.bars} mes. x{p.repeats:<5} tracks: {act}")
    print(f"  chaine : {' '.join(f'{c:02d}' for c in bank.chain)} "
          f"({len(bank.sections)} sections)")
    for path in written[:2]:
        print(f"[export] {path.relative_to(VAULT_ROOT)}")
    if midi:
        print(f"[export] {len(bank.patterns)} .mid dans "
              f"{(DIGITAKT_DIR / slug).relative_to(VAULT_ROOT)}/")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Draft de bank Digitakt II (patterns 16 tracks) depuis une track.")
    parser.add_argument("slug", nargs="?", help="Slug de la track")
    parser.add_argument("--all", action="store_true",
                        help="Traite toutes les tracks qui ont un sidecar.")
    parser.add_argument("--phrase-bars", type=int, default=8, choices=(4, 8, 16, 32),
                        help="Taille des phrases de la partition de mutes (defaut 8).")
    parser.add_argument("--threshold", type=float, default=0.5,
                        help="Seuil relatif d'un trig (0-1, defaut 0.5).")
    parser.add_argument("--no-midi", dest="midi", action="store_false",
                        help="Ne pas ecrire les .mid par pattern.")
    args = parser.parse_args()
    if not args.slug and not args.all:
        parser.error("donner un slug ou --all")

    entries = parse_library(LIBRARY_FILE)
    slugs = sorted(p.stem for p in QUALITY_DIR.glob("*.json")) if args.all else [args.slug]
    rc = 0
    for slug in slugs:
        rc |= process(slug, entries, args.phrase_bars, args.threshold, args.midi)
    return rc


if __name__ == "__main__":
    sys.exit(main())

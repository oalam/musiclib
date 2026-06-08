#!/usr/bin/env python3
"""Extraction de groove jouable depuis une track (Phase 6.D).

Transcrit le pattern rythmique d'une track en hits discrets kick / snare / hat,
quantifies sur une grille, et l'exporte en deux formats :
- `.mid`  : clip MIDI batterie (GM : kick=36, snare=38, hat=42) → Renoise / DAW
- `.tidal`: pattern mininotation TidalCycles → collable dans un live set

Source preferee : le stem `drums.wav` isole par Demucs (`stems.py`), bien plus
propre qu'un mix complet. Fallback sur le mix si pas de stem (avec warning).

Partage le coeur de `analyzer/rhythm_signature.py` (decoupage en bandes,
repliage sur la grille via les beats), mais seuille en hits discrets.

Usage:
    groove.py <slug> [--steps 16|32] [--bars N] [--format both|mid|tidal]
    groove.py <slug> --threshold 0.25     # sensibilite des hits

Sortie : `library/grooves/<slug>.{mid,tidal}`.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from analyzer.audio_loader import load_audio, to_mono
from analyzer.infer import load_sidecar
from analyzer.rhythm_signature import (
    _SIG_CONF_THRESHOLD,
    band_envelopes,
    beats_per_bar,
)
from library_md import parse_library
from stems import _resolve_audio_path

VAULT_ROOT = Path(__file__).resolve().parent.parent
LIBRARY = VAULT_ROOT / "library"
LIBRARY_FILE = LIBRARY / "library.md"
QUALITY_DIR = LIBRARY / "quality"
STEMS_DIR = LIBRARY / "stems"
GROOVES_DIR = LIBRARY / "grooves"

# Bande de rhythm_signature → (note GM, nom sample Tidal)
_VOICES: dict[str, tuple[int, str]] = {
    "sub": (36, "bd"),   # kick
    "mid": (38, "sn"),   # snare / clap
    "high": (42, "hh"),  # hi-hat
}
_PPQ = 480  # ticks par noire


def _resolve_source(slug: str, entries: dict[str, dict[str, str]]) -> tuple[Path, bool]:
    """Retourne (chemin audio, from_stem). Prefere le stem drums Demucs.

    Le fallback mix reutilise `stems._resolve_audio_path` (parse le wikilink
    `[[audio/...]]` du champ `file`)."""
    drums = STEMS_DIR / slug / "drums.wav"
    if drums.exists():
        return drums, True
    mix = _resolve_audio_path(entries.get(slug, {}))
    if mix is not None:
        return mix, False
    raise FileNotFoundError(
        f"Aucune source pour {slug} : ni stem drums ni fichier mix trouve."
    )


def _fold_band(
    env: np.ndarray,
    frame_times: np.ndarray,
    bar_starts: np.ndarray,
    grid_len: int,
    bars_period: int,
    steps: int,
) -> np.ndarray:
    """Replie l'enveloppe continue d'une bande sur `grid_len` pas (periode de
    `bars_period` mesures). Retourne le pattern brut (somme d'energie/pas)."""
    pattern = np.zeros(grid_len)
    n_bars = len(bar_starts) - 1
    if n_bars < 1 or env.size == 0:
        return pattern
    n = min(len(env), len(frame_times))
    env = env[:n]
    frame_times = frame_times[:n]
    for bi in range(n_bars):
        t0 = float(bar_starts[bi])
        t1 = float(bar_starts[bi + 1])
        if t1 <= t0:
            continue
        offset = (bi % bars_period) * steps
        mask = (frame_times >= t0) & (frame_times < t1)
        if not mask.any():
            continue
        rel = (frame_times[mask] - t0) / (t1 - t0)
        idx = offset + np.clip((rel * steps).astype(int), 0, steps - 1)
        np.add.at(pattern, idx, env[mask])
    return pattern


def _stretch(pattern: np.ndarray) -> np.ndarray:
    """Min-max → [0, 1] (revele le relief des hits sur le plancher continu)."""
    if pattern.size == 0:
        return pattern
    lo, hi = float(pattern.min()), float(pattern.max())
    if hi - lo <= 0:
        return np.zeros_like(pattern)
    return (pattern - lo) / (hi - lo)


def _build_grids(
    mono: np.ndarray,
    sample_rate: int,
    beat_times: list[float],
    bpb: int,
    steps: int,
    bars: int,
    threshold: float,
    align: bool = True,
) -> dict[str, tuple[list[bool], list[int]]]:
    """Pour chaque voix : (hits booleens, velocites MIDI 1-127) sur grid_len.

    Replie l'enveloppe continue de la bande (robuste au jitter), l'etire en
    [0, 1], puis garde les pas au-dessus du seuil relatif. Comme la signature,
    cette approche fait ressortir un kick four-on-floor net la ou la detection
    d'onsets discrets se disperse entre pas adjacents.

    `align` : decale toutes les voix pour que le kick (sub) le plus fort tombe
    sur le pas 0 — le loop exporte demarre alors sur le « 1 »."""
    beats = np.asarray([t for t in beat_times if t >= 0], dtype=float)
    bar_starts = beats[::bpb]
    grid_len = steps * bars
    envelopes, frame_times = band_envelopes(mono, sample_rate)

    patterns: dict[str, np.ndarray] = {}
    for band in _VOICES:
        raw = _fold_band(envelopes.get(band, np.zeros(0)),
                         frame_times, bar_starts, grid_len, bars, steps)
        patterns[band] = _stretch(raw)

    shift = 0
    if align and patterns["sub"].size and patterns["sub"].max() > 0:
        shift = int(np.argmax(patterns["sub"]))

    grids: dict[str, tuple[list[bool], list[int]]] = {}
    for band, pat in patterns.items():
        if shift:
            pat = np.roll(pat, -shift)
        hits = [bool(v >= threshold) for v in pat]
        velocities = [
            int(np.clip(40 + float(v) * 87, 1, 127)) if h else 0
            for v, h in zip(pat, hits)
        ]
        grids[band] = (hits, velocities)
    return grids


def _write_midi(
    out_path: Path,
    grids: dict[str, tuple[list[bool], list[int]]],
    bpm: float,
    steps: int,
    bpb: int,
) -> None:
    import mido

    grid_len = len(next(iter(grids.values()))[0])
    ticks_per_step = max(1, int(round(_PPQ * bpb / steps)))

    mid = mido.MidiFile(ticks_per_beat=_PPQ)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.MetaMessage(
        "set_tempo", tempo=mido.bpm2tempo(bpm if bpm > 0 else 140), time=0,
    ))

    # Evenements absolus (tick, prio, message), puis conversion en delta.
    events: list[tuple[int, int, mido.Message]] = []
    for band, (hits, vels) in grids.items():
        note, _ = _VOICES[band]
        for i in range(grid_len):
            if not hits[i]:
                continue
            on_tick = i * ticks_per_step
            off_tick = on_tick + max(1, ticks_per_step // 2)
            events.append((on_tick, 1,
                           mido.Message("note_on", note=note,
                                        velocity=vels[i], channel=9)))
            events.append((off_tick, 0,
                           mido.Message("note_off", note=note,
                                        velocity=0, channel=9)))
    events.sort(key=lambda e: (e[0], e[1]))

    prev = 0
    for tick, _prio, msg in events:
        msg.time = max(0, tick - prev)
        prev = tick
        track.append(msg)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    mid.save(str(out_path))


def _write_tidal(
    out_path: Path,
    grids: dict[str, tuple[list[bool], list[int]]],
    slug: str,
    fields: dict[str, str],
    bpm: float,
    steps: int,
    bars: int,
    bpb: int,
) -> None:
    label = f"{fields.get('artist', '?')} — {fields.get('title', '?')}"
    lines: list[str] = [
        f"-- groove extrait de {label}",
        f"-- {bpm:.0f} BPM, {steps} pas/mesure, {bars} mesure(s)",
    ]
    if bpm > 0:
        # une mesure = un cycle Tidal : cps = bpm / 60 / beats_par_mesure
        lines.append(f"-- setcps ({bpm:.0f}/60/{bpb})")
    lines.append("d1 $ stack [")

    voice_lines: list[str] = []
    for band, (hits, _vels) in grids.items():
        _, sample = _VOICES[band]
        tokens = [sample if h else "~" for h in hits]
        voice_lines.append(f'  s "{" ".join(tokens)}"')
    lines.append(",\n".join(voice_lines))
    lines.append("  ]")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_groove(
    slug: str,
    steps: int,
    bars: int,
    fmt: str,
    threshold: float,
    align: bool = True,
) -> int:
    entries = parse_library(LIBRARY_FILE)
    fields = entries.get(slug, {})

    sidecar = load_sidecar(QUALITY_DIR, slug)
    beats = (sidecar or {}).get("beats") or {}
    beat_times = beats.get("beat_times_s") or []
    bpm = float(beats.get("tempo_bpm") or 0)
    time_sig = beats.get("time_signature", "4/4")
    sig_conf = float(beats.get("time_signature_confidence") or 0.5)
    if not beat_times:
        print(f"[ERROR] pas de beats pour {slug} (lance analyze.py {slug}).",
              file=sys.stderr)
        return 1

    bpb = beats_per_bar(time_sig)
    if bpb != 4 and sig_conf < _SIG_CONF_THRESHOLD:
        bpb = 4

    try:
        source, from_stem = _resolve_source(slug, entries)
    except FileNotFoundError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    if not from_stem:
        print(f"[warn] pas de stem drums pour {slug} : transcription depuis le "
              f"mix (plus bruitee). Lance stems.py {slug} pour un meilleur rendu.")

    data, sr = load_audio(source)
    mono = to_mono(data)
    grids = _build_grids(mono, sr, beat_times, bpb, steps, bars,
                         threshold, align)

    if all(not any(h) for h, _ in grids.values()):
        print(f"[warn] aucun hit detecte au seuil {threshold} "
              f"(essaie --threshold plus bas).")

    written: list[Path] = []
    if fmt in ("both", "mid"):
        out = GROOVES_DIR / f"{slug}.mid"
        _write_midi(out, grids, bpm, steps, bpb)
        written.append(out)
    if fmt in ("both", "tidal"):
        out = GROOVES_DIR / f"{slug}.tidal"
        _write_tidal(out, grids, slug, fields, bpm, steps, bars, bpb)
        written.append(out)

    src_label = "stem drums" if from_stem else "mix"
    print(f"Groove {slug} ({src_label}, {bpm:.0f} BPM, {steps}x{bars}) :")
    for band, (hits, _v) in grids.items():
        _, sample = _VOICES[band]
        viz = "".join("x" if h else "." for h in hits)
        print(f"  {sample:<3} {viz}")
    for p in written:
        print(f"[export] {p.relative_to(VAULT_ROOT)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extrait un groove jouable (.mid + .tidal) depuis une track.",
    )
    parser.add_argument("slug", help="Slug de la track (artist_-_title)")
    parser.add_argument("--steps", type=int, default=16, choices=(8, 16, 32),
                        help="Pas par mesure (defaut 16 = doubles-croches).")
    parser.add_argument("--bars", type=int, default=1,
                        help="Nombre de mesures du pattern exporte (defaut 1).")
    parser.add_argument("--format", choices=("both", "mid", "tidal"),
                        default="both", dest="fmt")
    parser.add_argument("--threshold", type=float, default=0.5,
                        help="Seuil relatif d'un hit sur le pattern etire "
                             "(0-1, defaut 0.5 = moitie haute du relief).")
    parser.add_argument("--no-align", dest="align", action="store_false",
                        help="Ne pas caler le pattern sur le kick le plus fort.")
    args = parser.parse_args()
    if args.bars < 1:
        print("[ERROR] --bars doit etre >= 1", file=sys.stderr)
        return 1
    return export_groove(args.slug, args.steps, args.bars, args.fmt,
                         args.threshold, args.align)


if __name__ == "__main__":
    sys.exit(main())

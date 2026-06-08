#!/usr/bin/env python3
"""Export XRNS (Renoise song) depuis 2 slugs + leurs stems, decoupes en slices.

Construit un song Renoise 3.5+ avec 8 tracks (4 stems de A + 4 stems de B).
Chaque stem est decoupe en slices a partir des segments structurels du
sidecar Phase 2 (`library/quality/<slug>.json`). La PatternSequence
enchaine N_A patterns pour A puis N_B patterns pour B, chaque pattern
declenchant la slice correspondante sur les 4 tracks concernees.

Approche template-clone (cf. memory `music-renoise-export`) : on part de
2 templates XRNS reels (`scripts/fixtures/one-sample.xrns` pour la base
structurelle, `sliced-sample.xrns` pour le format des SliceMarkers et
samples alias) plutot que de reconstruire le schema a la main.

Sans arguments, choisit automatiquement la meilleure paire compatible
parmi les slugs ayant des stems generes.

Usage:
    to_xrns.py                                  # auto-pick meilleure paire
    to_xrns.py SLUG_A SLUG_B                    # paire explicite
    to_xrns.py --bpm 165                        # override BPM song
    to_xrns.py -o sets/mix.xrns SLUG_A SLUG_B

Sortie par defaut : `library/renoise/<slug_a>__x__<slug_b>.xrns`."""
from __future__ import annotations

import argparse
import copy
import json
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

import soundfile as sf

from library_md import parse_library
from analyzer.compatibility import score_transition

VAULT_ROOT = Path(__file__).resolve().parent.parent
LIBRARY = VAULT_ROOT / "library"
STEMS_DIR = LIBRARY / "stems"
QUALITY_DIR = LIBRARY / "quality"
LIBRARY_FILE = LIBRARY / "library.md"
DEFAULT_OUTPUT_DIR = LIBRARY / "renoise"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
TEMPLATE_BASE = FIXTURES / "one-sample.xrns"
TEMPLATE_SLICED = FIXTURES / "sliced-sample.xrns"

STEM_NAMES = ("drums", "bass", "other", "vocals")
LINES_PER_BEAT = 4
MAX_PATTERN_LINES = 512  # limite Renoise
SLICE_BASE_NOTE = 36  # C-3 dans la notation Renoise (octave 3)

# "C-", "C#", "D-", ... + numero d'octave -> "C-3", "C#3", "D-3"
_NOTE_NAMES = ("C-", "C#", "D-", "D#", "E-", "F-", "F#", "G-", "G#", "A-", "A#", "B-")


class XrnsError(Exception):
    pass


# ---------------------------------------------------------------------------
# Selection de paire + validation
# ---------------------------------------------------------------------------

def _find_best_pair(entries: dict[str, dict[str, str]]) -> tuple[str, str]:
    candidates = {
        s: e for s, e in entries.items()
        if (STEMS_DIR / s).is_dir()
        and all((STEMS_DIR / s / f"{n}.wav").exists() for n in STEM_NAMES)
        and (QUALITY_DIR / f"{s}.json").exists()
        and e.get("bpm") and e.get("key")
    }
    if len(candidates) < 2:
        raise XrnsError(
            f"Moins de 2 slugs eligibles (stems + sidecar + bpm + key) : "
            f"{len(candidates)}"
        )
    slugs = list(candidates)
    best: tuple[float, str, str] = (-1.0, "", "")
    for i, a in enumerate(slugs):
        for b in slugs[i + 1:]:
            total = score_transition(candidates[a], candidates[b]).total
            if total > best[0]:
                best = (total, a, b)
    return best[1], best[2]


def _validate_inputs(slug: str) -> None:
    folder = STEMS_DIR / slug
    if not folder.is_dir():
        raise XrnsError(f"Pas de stems pour {slug} (dossier absent : {folder})")
    missing = [n for n in STEM_NAMES if not (folder / f"{n}.wav").exists()]
    if missing:
        raise XrnsError(f"Stems manquants pour {slug} : {missing}")
    if not (QUALITY_DIR / f"{slug}.json").exists():
        raise XrnsError(f"Sidecar Phase 2 absent pour {slug}")


def _track_label(entry: dict[str, str]) -> str:
    return f"{entry.get('artist', '?')} - {entry.get('title', '?')}"


# ---------------------------------------------------------------------------
# Segments depuis le sidecar
# ---------------------------------------------------------------------------

@dataclass
class Segment:
    start_s: float
    end_s: float
    label: str

    @property
    def duration_s(self) -> float:
        return self.end_s - self.start_s


def _read_segments(slug: str, fallback_duration_s: float) -> list[Segment]:
    """Segments structurels du sidecar, fallback sur 1 segment full si absent."""
    data = json.loads((QUALITY_DIR / f"{slug}.json").read_text(encoding="utf-8"))
    raw = data.get("structure", {}).get("segments", []) or []
    if not raw:
        return [Segment(0.0, fallback_duration_s, "full")]
    segs: list[Segment] = []
    for s in raw:
        segs.append(Segment(
            start_s=float(s.get("start_s", 0.0)),
            end_s=float(s.get("end_s", fallback_duration_s)),
            label=str(s.get("label") or "?"),
        ))
    # Garantir un ordre + clamp final sur la duree reelle
    segs.sort(key=lambda x: x.start_s)
    segs[-1] = Segment(segs[-1].start_s, fallback_duration_s, segs[-1].label)
    return segs


# ---------------------------------------------------------------------------
# Helpers notes / lignes
# ---------------------------------------------------------------------------

def _note_str(idx: int) -> str:
    """Index Renoise (0=C-0, 36=C-3) -> texte XML "C-3"."""
    return f"{_NOTE_NAMES[idx % 12]}{idx // 12}"


def _seconds_to_lines(duration_s: float, bpm: float) -> int:
    """Convertit duree -> lignes Renoise (clamp [1, 512])."""
    lines = round(duration_s * bpm * LINES_PER_BEAT / 60)
    return max(1, min(MAX_PATTERN_LINES, int(lines)))


def _set_text(parent: ET.Element, tag: str, text: str) -> None:
    el = parent.find(tag)
    if el is None:
        el = ET.SubElement(parent, tag)
    el.text = text


# ---------------------------------------------------------------------------
# Construction d'instrument slice (master + N alias)
# ---------------------------------------------------------------------------

def _make_slice_markers(positions: list[int]) -> ET.Element:
    container = ET.Element("SliceMarkers")
    for pos in positions:
        marker = ET.SubElement(container, "SliceMarker")
        ET.SubElement(marker, "SamplePosition").text = str(pos)
    return container


def _make_alias_sample(
    template_alias: ET.Element,
    name: str,
    base_note: int,
    length_frames: int,
) -> ET.Element:
    """Sample alias (pas de fichier audio embarque) pointant sur une slice."""
    new = copy.deepcopy(template_alias)
    _set_text(new, "Name", name)
    _set_text(new, "LoopEnd", str(length_frames))
    _set_text(new, "DisplayLength", str(length_frames))
    _set_text(new, "DisplayStart", "0")
    mapping = new.find("Mapping")
    if mapping is None:
        raise XrnsError("Template alias casse : pas de Mapping.")
    _set_text(mapping, "BaseNote", str(base_note))
    _set_text(mapping, "NoteStart", str(base_note))
    _set_text(mapping, "NoteEnd", str(base_note))
    return new


def _make_sliced_instrument(
    template_instrument: ET.Element,
    template_alias: ET.Element,
    name: str,
    abs_source_path: str,
    slice_positions: list[int],  # positions des markers (frames)
    total_frames: int,
) -> ET.Element:
    """Instrument complet : maitre slice + N alias samples (1 par marker)."""
    instr = copy.deepcopy(template_instrument)
    _set_text(instr, "Name", name)

    samples_el = instr.find("./SampleGenerator/Samples")
    if samples_el is None:
        raise XrnsError("Template casse : pas de Samples dans l'Instrument.")
    samples_el.clear()

    # Master sample : reproduit la structure du fixture slice (NoteStart=NoteEnd=36).
    master = copy.deepcopy(template_instrument.find("./SampleGenerator/Samples/Sample"))
    if master is None:
        raise XrnsError("Template casse : pas de Sample maitre.")
    _set_text(master, "Name", name)
    _set_text(master, "FileName", abs_source_path)
    _set_text(master, "LoopEnd", str(total_frames))
    _set_text(master, "DisplayLength", str(total_frames))
    _set_text(master, "DisplayStart", "0")
    mapping = master.find("Mapping")
    _set_text(mapping, "BaseNote", str(SLICE_BASE_NOTE))
    _set_text(mapping, "NoteStart", str(SLICE_BASE_NOTE))
    _set_text(mapping, "NoteEnd", str(SLICE_BASE_NOTE))
    # SliceMarkers : retire si present, recree avec nos positions
    for old in master.findall("SliceMarkers"):
        master.remove(old)
    if slice_positions:
        # Inserer SliceMarkers juste avant SingleSliceTriggerEnabled (cohesion template)
        marker_block = _make_slice_markers(slice_positions)
        insert_at = len(master)
        for i, child in enumerate(master):
            if child.tag == "SingleSliceTriggerEnabled":
                insert_at = i
                break
        master.insert(insert_at, marker_block)
    _set_text(master, "SingleSliceTriggerEnabled", "true")
    samples_el.append(master)

    # Alias samples : 1 par marker, segment [marker_i, marker_{i+1}) puis dernier
    # va jusqu'a total_frames.
    boundaries = [*slice_positions, total_frames]
    for i, pos in enumerate(slice_positions, start=1):
        next_pos = boundaries[i]
        length = max(1, next_pos - pos)
        alias = _make_alias_sample(
            template_alias,
            name=f"{name} (S#{i:02d})",
            base_note=SLICE_BASE_NOTE + i,
            length_frames=length,
        )
        samples_el.append(alias)

    return instr


# ---------------------------------------------------------------------------
# Construction des tracks et patterns
# ---------------------------------------------------------------------------

def _make_sequencer_track(template_track: ET.Element, name: str, color: str) -> ET.Element:
    new = copy.deepcopy(template_track)
    _set_text(new, "Name", name)
    _set_text(new, "Color", color)
    return new


def _make_pattern_track(
    template_pt: ET.Element,
    trigger: tuple[int, int, int] | None,  # (line, instrument_index, note_index) ou None
) -> ET.Element:
    """Clone une PatternTrack vide, y insere optionnellement une note de trigger."""
    new = copy.deepcopy(template_pt)
    for old in new.findall("Lines"):
        new.remove(old)
    if trigger is not None:
        line_idx, instr_idx, note_idx = trigger
        lines = ET.Element("Lines")
        line = ET.SubElement(lines, "Line", {"index": str(line_idx)})
        ncs = ET.SubElement(line, "NoteColumns")
        nc = ET.SubElement(ncs, "NoteColumn")
        ET.SubElement(nc, "Note").text = _note_str(note_idx)
        ET.SubElement(nc, "Instrument").text = f"{instr_idx:02X}"
        # Insertion avant AliasPatternIndex / ColorEnabled / Color
        insert_at = len(new)
        for i, child in enumerate(new):
            if child.tag in ("AliasPatternIndex", "ColorEnabled", "Color"):
                insert_at = i
                break
        new.insert(insert_at, lines)
    return new


def _make_pattern(
    template_pattern: ET.Element,
    template_pt: ET.Element,
    template_pmaster: ET.Element,
    template_psend: ET.Element,
    num_lines: int,
    triggers: dict[int, tuple[int, int]],  # track_idx -> (instr_idx, note_idx)
    num_tracks: int,
) -> ET.Element:
    """Pattern de num_lines lignes avec triggers en ligne 0 sur les tracks indiquees."""
    new = copy.deepcopy(template_pattern)
    _set_text(new, "NumberOfLines", str(num_lines))
    p_tracks = new.find("Tracks")
    p_tracks.clear()
    for i in range(num_tracks):
        if i in triggers:
            instr_idx, note_idx = triggers[i]
            trig = (0, instr_idx, note_idx)
        else:
            trig = None
        p_tracks.append(_make_pattern_track(template_pt, trig))
    p_tracks.append(copy.deepcopy(template_pmaster))
    p_tracks.append(copy.deepcopy(template_psend))
    return new


# ---------------------------------------------------------------------------
# Chargement templates
# ---------------------------------------------------------------------------

def _load_song_xml(xrns_path: Path) -> ET.ElementTree:
    if not xrns_path.exists():
        raise XrnsError(f"Template absent : {xrns_path}")
    with zipfile.ZipFile(xrns_path) as zf:
        with zf.open("Song.xml") as fh:
            return ET.parse(fh)


# ---------------------------------------------------------------------------
# Build complet du Song.xml
# ---------------------------------------------------------------------------

def _build_song_xml(
    *,
    song_name: str,
    bpm: float,
    stems_a: list[tuple[str, Path, list[Segment]]],  # (name, src, segments)
    stems_b: list[tuple[str, Path, list[Segment]]],
    track_specs: list[tuple[str, str]],
) -> bytes:
    base_tree = _load_song_xml(TEMPLATE_BASE)
    root = base_tree.getroot()

    # Templates extraits
    base_instrument_template = root.find("./Instruments/Instrument")
    if base_instrument_template is None:
        raise XrnsError("Template casse : pas d'Instrument dans one-sample.")
    base_instrument_template = copy.deepcopy(base_instrument_template)

    sliced_root = _load_song_xml(TEMPLATE_SLICED).getroot()
    alias_template = sliced_root.find("./Instruments/Instrument/SampleGenerator/Samples/Sample[2]")
    if alias_template is None:
        # ElementTree XPath ne supporte pas l'index 1-based partout : fallback manuel
        all_samples = sliced_root.findall("./Instruments/Instrument/SampleGenerator/Samples/Sample")
        if len(all_samples) < 2:
            raise XrnsError("Template sliced casse : pas d'alias Sample.")
        alias_template = all_samples[1]
    alias_template = copy.deepcopy(alias_template)

    # GlobalSongData
    gd = root.find("GlobalSongData")
    _set_text(gd, "BeatsPerMin", f"{bpm}")
    _set_text(gd, "SongName", song_name)
    _set_text(gd, "Artist", "oalam")

    # Instruments : 8 slices
    instruments_el = root.find("Instruments")
    instruments_el.clear()
    all_stems = [*stems_a, *stems_b]
    for name, src, segments in all_stems:
        info = sf.info(str(src))
        sr = info.samplerate
        total_frames = info.frames
        # Markers : positions des starts > 0 ; ignorer le premier segment qui demarre a 0
        positions = [int(round(seg.start_s * sr)) for seg in segments if seg.start_s > 0]
        # Clamp positions a total_frames-1 pour eviter overflow
        positions = sorted({min(p, total_frames - 1) for p in positions if p > 0})
        instr = _make_sliced_instrument(
            base_instrument_template,
            alias_template,
            name=name,
            abs_source_path=str(src),
            slice_positions=positions,
            total_frames=total_frames,
        )
        instruments_el.append(instr)

    # Tracks : 8 SequencerTrack + Master + Send
    tracks_el = root.find("Tracks")
    seq_template = copy.deepcopy(tracks_el.find("SequencerTrack"))
    master = copy.deepcopy(tracks_el.find("SequencerMasterTrack"))
    send = copy.deepcopy(tracks_el.find("SequencerSendTrack"))
    tracks_el.clear()
    for name, color in track_specs:
        tracks_el.append(_make_sequencer_track(seq_template, name, color))
    tracks_el.append(master)
    tracks_el.append(send)

    # Patterns : N_A patterns de A puis N_B patterns de B
    pool = root.find("./PatternPool")
    patterns_container = pool.find("Patterns")
    template_pattern = copy.deepcopy(patterns_container.find("Pattern"))
    pt_template = copy.deepcopy(template_pattern.find("./Tracks/PatternTrack"))
    pmaster_template = copy.deepcopy(template_pattern.find("./Tracks/PatternMasterTrack"))
    psend_template = copy.deepcopy(template_pattern.find("./Tracks/PatternSendTrack"))
    patterns_container.clear()

    num_tracks = len(track_specs)
    sections_a = stems_a[0][2]  # tous les stems de A ont les memes segments
    sections_b = stems_b[0][2]
    pattern_order: list[int] = []
    section_labels: list[str] = []

    for seg_idx, seg in enumerate(sections_a):
        lines = _seconds_to_lines(seg.duration_s, bpm)
        triggers = {
            track_idx: (track_idx, SLICE_BASE_NOTE + seg_idx)
            for track_idx in range(4)  # tracks A = 0..3
        }
        patt = _make_pattern(
            template_pattern, pt_template, pmaster_template, psend_template,
            lines, triggers, num_tracks,
        )
        patterns_container.append(patt)
        pattern_order.append(len(pattern_order))
        section_labels.append(f"A:{seg.label}")

    for seg_idx, seg in enumerate(sections_b):
        lines = _seconds_to_lines(seg.duration_s, bpm)
        triggers = {
            track_idx: (track_idx, SLICE_BASE_NOTE + seg_idx)
            for track_idx in range(4, 8)  # tracks B = 4..7
        }
        patt = _make_pattern(
            template_pattern, pt_template, pmaster_template, psend_template,
            lines, triggers, num_tracks,
        )
        patterns_container.append(patt)
        pattern_order.append(len(pattern_order))
        section_labels.append(f"B:{seg.label}")

    # PatternSequence : entrees dans l'ordre des patterns
    seq = root.find("PatternSequence")
    seq_entries = seq.find("SequenceEntries")
    entry_template = copy.deepcopy(seq_entries.find("SequenceEntry"))
    seq_entries.clear()
    for patt_idx, label in zip(pattern_order, section_labels, strict=True):
        entry = copy.deepcopy(entry_template)
        _set_text(entry, "Pattern", str(patt_idx))
        _set_text(entry, "SectionName", label)
        # Marquer chaque entree A_0 et B_0 comme debut de section pour la matrix
        _set_text(entry, "IsSectionStart", "true" if label.endswith(":intro") or patt_idx in (0, len(sections_a)) else "false")
        seq_entries.append(entry)

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


# ---------------------------------------------------------------------------
# ZIP packaging
# ---------------------------------------------------------------------------

def _sample_zip_path(instr_index: int, instr_name: str) -> str:
    return (
        f"SampleData/Instrument{instr_index:02d} ({instr_name})"
        f"/Sample00 ({instr_name}).wav"
    )


def write_xrns(
    output: Path,
    song_xml: bytes,
    stem_paths: list[tuple[int, str, Path]],
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("Song.xml", song_xml)
        for idx, name, src in stem_paths:
            zf.write(src, _sample_zip_path(idx, name))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export XRNS Renoise 3.5+ depuis 2 slugs + leurs stems, "
                    "decoupes en slices selon les segments du sidecar.",
    )
    parser.add_argument("slugs", nargs="*", help="0 ou 2 slugs (auto-pick sinon)")
    parser.add_argument("--bpm", type=float, help="Override BPM song")
    parser.add_argument("-o", "--output", type=Path, help="Chemin de sortie .xrns")
    args = parser.parse_args()

    if args.slugs and len(args.slugs) != 2:
        parser.error("Donne 0 ou 2 slugs (pas plus, pas un seul).")

    entries = parse_library(LIBRARY_FILE)

    if args.slugs:
        slug_a, slug_b = args.slugs
        for s in (slug_a, slug_b):
            if s not in entries:
                raise XrnsError(f"Slug introuvable dans library.md : {s}")
            _validate_inputs(s)
    else:
        slug_a, slug_b = _find_best_pair(entries)
        print(f"[auto-pick] {slug_a}  <->  {slug_b}")

    entry_a, entry_b = entries[slug_a], entries[slug_b]
    score = score_transition(entry_a, entry_b)
    print(f"  compat : total={score.total} | {' '.join(score.notes)}")

    bpm = args.bpm or float(entry_a.get("bpm") or 0)
    if bpm <= 0:
        raise XrnsError(f"BPM invalide pour {slug_a} : '{entry_a.get('bpm')}'")

    # Segments par stem (utilise la duree du WAV drums comme reference)
    def _build_stem_specs(prefix: str, slug: str) -> list[tuple[str, Path, list[Segment]]]:
        ref_wav = STEMS_DIR / slug / "drums.wav"
        duration_s = sf.info(str(ref_wav)).frames / sf.info(str(ref_wav)).samplerate
        segments = _read_segments(slug, duration_s)
        return [
            (f"{prefix}_{stem}", STEMS_DIR / slug / f"{stem}.wav", segments)
            for stem in STEM_NAMES
        ]

    stems_a = _build_stem_specs("A", slug_a)
    stems_b = _build_stem_specs("B", slug_b)
    print(f"  A : {len(stems_a[0][2])} sections -> {[s.label for s in stems_a[0][2]]}")
    print(f"  B : {len(stems_b[0][2])} sections -> {[s.label for s in stems_b[0][2]]}")

    song_name = f"{_track_label(entry_a)}  x  {_track_label(entry_b)}"

    colors_a = ["80,160,255", "100,180,220", "120,200,200", "140,210,180"]
    colors_b = ["255,160,80", "240,140,100", "220,120,120", "200,100,140"]
    track_specs: list[tuple[str, str]] = []
    stem_paths: list[tuple[int, str, Path]] = []
    for i, (name, src, _) in enumerate(stems_a):
        track_specs.append((name.replace("_", " "), colors_a[i]))
        stem_paths.append((len(stem_paths), name, src))
    for i, (name, src, _) in enumerate(stems_b):
        track_specs.append((name.replace("_", " "), colors_b[i]))
        stem_paths.append((len(stem_paths), name, src))

    song_xml = _build_song_xml(
        song_name=song_name,
        bpm=bpm,
        stems_a=stems_a,
        stems_b=stems_b,
        track_specs=track_specs,
    )

    output = args.output or DEFAULT_OUTPUT_DIR / f"{slug_a}__x__{slug_b}.xrns"
    write_xrns(output, song_xml, stem_paths)

    total_mb = sum(p.stat().st_size for _, _, p in stem_paths) / 1024 / 1024
    n_patterns = len(stems_a[0][2]) + len(stems_b[0][2])
    print(
        f"\n[ok] {output}\n"
        f"  song : {song_name}\n"
        f"  bpm  : {bpm} | patterns : {n_patterns} ({len(stems_a[0][2])} A + "
        f"{len(stems_b[0][2])} B)\n"
        f"  taille stems : {total_mb:.1f} MB"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except XrnsError as e:
        print(f"[error] {e}", file=sys.stderr)
        sys.exit(1)

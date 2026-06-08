"""Detection de cue points a partir des segments structurels et des beats.

Cue types emis :
- `intro_start`  : debut du premier segment audible (apres silence eventuel)
- `beat_entry`   : premier beat sur le 1er segment haute energie (ou 2eme segment)
- `drop`         : debut d'un segment 'peak' ou 'build' apres un 'breakdown'
- `breakdown`    : debut d'un segment 'breakdown' au milieu
- `outro`        : debut du dernier segment a energie chutee

Les cues sont alignes sur le beat le plus proche pour faciliter le mix.
"""
from __future__ import annotations

from .types import BeatReport, CuePoint, CuesReport, StructureReport


def _snap_to_beat(time_s: float, beats: list[float]) -> float:
    """Aligne sur le beat le plus proche (a +/- 0.5s max)."""
    if not beats:
        return time_s
    closest = min(beats, key=lambda b: abs(b - time_s))
    if abs(closest - time_s) < 0.5:
        return round(closest, 3)
    return round(time_s, 3)


def analyze(structure: StructureReport, beats: BeatReport) -> CuesReport:
    cues: list[CuePoint] = []
    if not structure.segments:
        return CuesReport(cues=cues)

    beat_times = beats.beat_times_s
    segments = structure.segments
    n = len(segments)

    # intro_start : debut du 1er segment
    first = segments[0]
    cues.append(CuePoint(
        time_s=round(first.start_s, 3),
        type="intro_start",
        confidence=0.9,
    ))

    # beat_entry : 1er segment a energie >= mediane (ou 2eme segment si intro low)
    high_energy_idx: int | None = None
    median_rms = sorted(s.rms_dbfs for s in segments)[len(segments) // 2]
    for i, seg in enumerate(segments):
        if seg.rms_dbfs >= median_rms and seg.label not in ("intro", "outro"):
            high_energy_idx = i
            break
    if high_energy_idx is not None and high_energy_idx > 0:
        target = segments[high_energy_idx].start_s
        cues.append(CuePoint(
            time_s=_snap_to_beat(target, beat_times),
            type="beat_entry",
            confidence=0.75,
        ))

    # drops + breakdowns dans le corps du morceau
    for i in range(1, n - 1):
        seg = segments[i]
        prev_seg = segments[i - 1]
        if seg.label == "peak" or (seg.label == "build" and prev_seg.label == "breakdown"):
            # transition montante = drop
            cues.append(CuePoint(
                time_s=_snap_to_beat(seg.start_s, beat_times),
                type="drop",
                confidence=0.6 if seg.label == "peak" else 0.5,
                label=seg.label,
            ))
        elif seg.label == "breakdown":
            cues.append(CuePoint(
                time_s=_snap_to_beat(seg.start_s, beat_times),
                type="breakdown",
                confidence=0.6,
            ))

    # outro
    last = segments[-1]
    if last.label == "outro":
        cues.append(CuePoint(
            time_s=_snap_to_beat(last.start_s, beat_times),
            type="outro",
            confidence=0.7,
        ))

    cues.sort(key=lambda c: c.time_s)
    return CuesReport(cues=cues)

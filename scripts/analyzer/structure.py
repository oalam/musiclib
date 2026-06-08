"""Segmentation structurelle du morceau.

Approche :
1. Features beat-synchrones : MFCC (timbre) + Chroma (harmonie) median-agreges
   sur chaque beat
2. Agglomerative clustering pour k segments contigus (librosa.segment.agglomerative)
3. Labellisation par energie relative + position : intro / build / peak /
   main / breakdown / outro

k adaptatif : ~30s par segment, borne [4, 15]. Resultat utile sur EDM /
DnB / techno bien structuree ; plus bruite sur ambient ou tribe peu
structure.
"""
from __future__ import annotations

import numpy as np

from .audio_loader import to_mono
from .types import Segment, StructureReport

MIN_SEGMENTS = 4
MAX_SEGMENTS = 15
TARGET_SEGMENT_DURATION_S = 30.0


def _adaptive_k(duration_s: float) -> int:
    raw = int(round(duration_s / TARGET_SEGMENT_DURATION_S))
    return max(MIN_SEGMENTS, min(MAX_SEGMENTS, raw))


def _segment_rms_dbfs(mono: np.ndarray, sr: int, start_s: float, end_s: float) -> float:
    a = int(max(0, start_s) * sr)
    b = int(min(len(mono), end_s * sr))
    if b <= a:
        return -100.0
    seg = mono[a:b].astype(np.float64)
    rms = float(np.sqrt(np.mean(seg ** 2)))
    if rms <= 0:
        return -100.0
    return float(20.0 * np.log10(rms))


def _label_segments(segments: list[Segment]) -> None:
    """Etiquette in-place selon energie relative + position."""
    if not segments:
        return
    rms_values = np.array([s.rms_dbfs for s in segments])
    median = float(np.median(rms_values))
    std = float(np.std(rms_values) + 1e-6)
    n = len(segments)

    for i, seg in enumerate(segments):
        z = (seg.rms_dbfs - median) / std
        is_first = i == 0
        is_last = i == n - 1
        prev_z = (segments[i - 1].rms_dbfs - median) / std if i > 0 else 0.0
        next_z = (segments[i + 1].rms_dbfs - median) / std if i < n - 1 else 0.0

        if is_first and z < -0.3:
            seg.label = "intro"
        elif is_last and z < -0.3:
            seg.label = "outro"
        elif z < -0.7:
            seg.label = "breakdown"
        elif z > 0.7:
            # Build = segment a energie haute precede d'une plus basse
            if prev_z < -0.3:
                seg.label = "build"
            else:
                seg.label = "peak"
        else:
            seg.label = "main"


def analyze(data: np.ndarray, sample_rate: int) -> StructureReport:
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import librosa

        mono = to_mono(data)
        duration = len(mono) / sample_rate
        k = _adaptive_k(duration)

        # Features beat-synchrones
        tempo, beats = librosa.beat.beat_track(y=mono, sr=sample_rate)
        if len(beats) < k + 2:
            # Pas assez de beats pour segmenter : decoupe lineaire
            edges = np.linspace(0, duration, k + 1)
        else:
            mfcc = librosa.feature.mfcc(y=mono, sr=sample_rate, n_mfcc=13)
            chroma = librosa.feature.chroma_cens(y=mono, sr=sample_rate)
            features = np.vstack([mfcc, chroma])
            sync = librosa.util.sync(features, beats, aggregate=np.median)
            boundaries = librosa.segment.agglomerative(sync, k=k)
            # librosa.util.sync(pad=True) ajoute un slot avant le 1er beat
            # et un apres le dernier -> sync.shape[1] = len(beats) + 1.
            # On etend beat_frames d'une frame synthetique de fin pour
            # supporter un boundary egal a len(beats).
            end_frame = int(librosa.time_to_frames(duration, sr=sample_rate))
            extended_beats = np.concatenate([beats, [end_frame]])
            safe_boundaries = np.clip(boundaries, 0, len(extended_beats) - 1)
            boundary_frames = extended_beats[safe_boundaries]
            boundary_times = librosa.frames_to_time(boundary_frames, sr=sample_rate)
            edges = np.concatenate(([0.0], boundary_times[1:], [duration]))

    edges = sorted(set(float(e) for e in edges))
    segments: list[Segment] = []
    for i in range(len(edges) - 1):
        s, e = edges[i], edges[i + 1]
        if e - s < 0.5:  # ignore segments < 500 ms (artefacts)
            continue
        rms_db = _segment_rms_dbfs(mono, sample_rate, s, e)
        segments.append(Segment(
            start_s=round(s, 2),
            end_s=round(e, 2),
            duration_s=round(e - s, 2),
            rms_dbfs=round(rms_db, 2),
            label="main",
        ))

    _label_segments(segments)
    segments = _merge_adjacent(segments, mono, sample_rate)
    return StructureReport(segments=segments, n_segments=len(segments))


def _merge_adjacent(
    segments: list[Segment],
    mono: np.ndarray,
    sample_rate: int,
) -> list[Segment]:
    """Fusionne les segments adjacents partageant le meme label (recalcule RMS)."""
    if not segments:
        return segments
    merged: list[Segment] = [segments[0]]
    for seg in segments[1:]:
        last = merged[-1]
        if seg.label == last.label:
            new_start = last.start_s
            new_end = seg.end_s
            merged[-1] = Segment(
                start_s=new_start,
                end_s=new_end,
                duration_s=round(new_end - new_start, 2),
                rms_dbfs=round(
                    _segment_rms_dbfs(mono, sample_rate, new_start, new_end), 2,
                ),
                label=last.label,
            )
        else:
            merged.append(seg)
    return merged

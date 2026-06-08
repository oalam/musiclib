"""Pipeline complet d'analyse audiophile (Phase 1 + Phase 2 optionnelle).

Reutilisable depuis analyze.py (CLI) et grab.py (--analyze-quality)."""
from __future__ import annotations

from datetime import date
from pathlib import Path

from . import (
    audio_loader,
    beat_tracking,
    cue_detection,
    dynamic,
    frequency_bands,
    loudness,
    metadata,
    rhythm_signature,
    scoring,
    signal,
    spectral,
    structure,
)
from .types import QualityReport


def analyze_file(
    path: Path,
    slug: str | None = None,
    artist: str | None = None,
    title: str | None = None,
    with_structure: bool = True,
    file_path_str: str | None = None,
    override_bpm: float | None = None,
) -> QualityReport:
    """Pipeline complet pour un fichier audio.

    Phase 1 (toujours) : metadata + signal + loudness + dynamic + spectral + score.
    Phase 2 (`with_structure=True`) : beats + structure + cues.
    Phase 6.A (toujours) : frequency_bands.

    `slug`, `artist`, `title`, `file_path_str` viennent typiquement de
    `library.md` (resolution par appelant).
    `override_bpm` : si fourni (ex: bpm corrige a la main dans library.md),
    court-circuite la detection librosa et calcule les beats sur grille
    reguliere alignee sur le 1er onset."""
    meta = metadata.probe(path)
    data, sr = audio_loader.load_audio(path)

    sig = signal.analyze(data)
    loud = loudness.analyze(data, sr)
    dyn = dynamic.analyze(sig)
    spec = spectral.analyze(data, sr, meta.is_lossless_container)
    score = scoring.compute(meta, sig, loud, dyn, spec)
    freq_bands = frequency_bands.analyze(data, sr)

    beats_report = None
    structure_report = None
    cues_report = None
    rhythm_sig = None
    if with_structure:
        beats_report = beat_tracking.analyze(data, sr, override_bpm=override_bpm)
        structure_report = structure.analyze(data, sr)
        cues_report = cue_detection.analyze(structure_report, beats_report)
        rhythm_sig = rhythm_signature.analyze(
            data, sr, beats_report.beat_times_s,
            beats_report.time_signature,
            beats_report.time_signature_confidence,
        )

    return QualityReport(
        file_path=file_path_str or str(path),
        slug=slug or path.stem,
        artist=artist,
        title=title,
        analyzed_at=date.today().isoformat(),
        metadata=meta,
        signal=sig,
        loudness=loud,
        dynamic=dyn,
        spectral=spec,
        quality=score,
        beats=beats_report,
        structure=structure_report,
        cues=cues_report,
        frequency_bands=freq_bands,
        rhythm_signature=rhythm_sig,
    )

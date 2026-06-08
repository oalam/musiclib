"""Rendu terminal + sauvegarde JSON sidecar."""
from __future__ import annotations

from pathlib import Path

from .types import QualityReport


def render_terminal(r: QualityReport) -> str:
    """Rendu lisible monospace pour stdout."""
    md = r.metadata
    sg = r.signal
    ld = r.loudness
    dy = r.dynamic
    sp = r.spectral
    qa = r.quality

    bitrate = f"{md.bitrate_kbps} kbps" if md.bitrate_kbps else "?"
    bit_depth = f"{md.bit_depth} bit" if md.bit_depth else "?"
    sr_khz = md.sample_rate_hz / 1000.0

    lines: list[str] = []
    header = f"{r.artist or '?'} — {r.title or '?'}"
    lines.append(f"=== {header}")
    lines.append(f"    {r.file_path}")
    lines.append("")
    lines.append("[Metadata]")
    lines.append(f"  codec      : {md.codec}  ({md.container})  {'LOSSLESS' if md.is_lossless_container else 'lossy'}")
    lines.append(f"  bitrate    : {bitrate}")
    lines.append(f"  sr / depth : {sr_khz:.1f} kHz / {bit_depth}")
    lines.append(f"  channels   : {md.channels}")
    lines.append(f"  duration   : {md.duration_s:.1f} s")
    if md.encoder:
        lines.append(f"  encoder    : {md.encoder}")
    lines.append("")
    lines.append("[Signal]")
    lines.append(f"  sample peak: {sg.sample_peak_dbfs:>7.2f} dBFS")
    lines.append(f"  true peak  : {sg.true_peak_dbfs:>7.2f} dBFS")
    lines.append(f"  RMS        : {sg.rms_dbfs:>7.2f} dBFS")
    lines.append(f"  clipping   : {sg.clipping_ratio * 100:.4f}%  ({sg.clipping_count} samples)")
    lines.append("")
    lines.append("[Loudness]")
    lines.append(f"  integrated : {ld.integrated_lufs:>7.2f} LUFS")
    lines.append(f"  range (LRA): {ld.loudness_range_lu:>7.2f} LU")
    lines.append("")
    lines.append("[Dynamic]")
    lines.append(f"  crest      : {dy.crest_factor_db:>7.2f} dB  ({dy.dynamic_rating})")
    lines.append("")
    lines.append("[Spectral]")
    lines.append(f"  bandwidth  : {sp.bandwidth_cutoff_hz:>7.0f} Hz")
    lines.append(f"  HF >16kHz  : {sp.high_freq_energy_ratio * 100:.2f}%")
    if sp.fake_lossless_probability > 0:
        lines.append(f"  fake-lossless prob : {sp.fake_lossless_probability * 100:.0f}%")
    lines.append("")
    lines.append(f"[Quality] {qa.score:>5.1f} / 100  —  {qa.rating}")
    for k, v in qa.components.items():
        lines.append(f"  {k:<10} : {v:>5.1f}")
    if qa.flags:
        lines.append(f"  flags      : {', '.join(qa.flags)}")

    if r.frequency_bands:
        fb = r.frequency_bands
        lines.append("")
        lines.append(f"[Bands] tonal: {fb.tonal_profile}")
        lines.append(
            f"  sub:{fb.sub_pct:>4.1f}%  bass:{fb.bass_pct:>4.1f}%  "
            f"lowmid:{fb.low_mid_pct:>4.1f}%  mid:{fb.mid_pct:>4.1f}%  "
            f"pres:{fb.presence_pct:>4.1f}%  high:{fb.high_pct:>4.1f}%  "
            f"air:{fb.air_pct:>4.1f}%"
        )

    if r.beats:
        lines.append("")
        tags: list[str] = []
        if r.beats.manual_override:
            tags.append("manual override")
        if r.beats.half_time_corrected:
            tags.append("half-time corrected")
        conf_str = f"conf={r.beats.confidence:.2f}"
        if r.beats.candidates_bpm:
            conf_str += f", candidates={r.beats.candidates_bpm}"
        tags.append(conf_str)
        suffix = "  (" + "; ".join(tags) + ")" if tags else ""
        lines.append(f"[Beats] tempo {r.beats.tempo_bpm} BPM  —  {r.beats.beat_count} beats{suffix}")
        lines.append(
            f"  signature: {r.beats.time_signature} (conf={r.beats.time_signature_confidence:.2f})"
            f"  |  onsets: {r.beats.onset_density_per_s:.2f}/s"
            f"  |  beat strength: {r.beats.beat_strength:.2f}"
        )

    if r.rhythm_signature and r.rhythm_signature.bars_used > 0:
        from .rhythm_signature import to_sparkline
        rs = r.rhythm_signature
        lines.append("")
        lines.append(
            f"[Rhythm signature] {rs.steps} pas/mesure  —  {rs.bars_used} mesures repliees"
        )
        lines.append(f"  bar : {to_sparkline(rs.bar_pattern)}")
        lines.append(f"  sub : {to_sparkline(rs.sub_pattern)}")
        lines.append(f"  mid : {to_sparkline(rs.mid_pattern)}")
        lines.append(f"  high: {to_sparkline(rs.high_pattern)}")
        lines.append(
            f"  syncope: {rs.syncopation:.2f}  |  pulse: {rs.pulse_clarity:.2f}"
            f"  |  swing: {rs.swing:.2f}"
        )

    if r.structure:
        lines.append("")
        lines.append(f"[Structure] {r.structure.n_segments} segments")
        for i, seg in enumerate(r.structure.segments):
            mm, ss = divmod(int(seg.start_s), 60)
            lines.append(
                f"  {i + 1:>2}. {mm:02d}:{ss:02d}  {seg.duration_s:>5.1f}s  "
                f"{seg.rms_dbfs:>6.1f} dBFS  {seg.label}"
            )

    if r.cues and r.cues.cues:
        lines.append("")
        lines.append(f"[Cues] {len(r.cues.cues)} points")
        for cue in r.cues.cues:
            mm, ss = divmod(int(cue.time_s), 60)
            cs = int((cue.time_s - int(cue.time_s)) * 100)
            tail = f"  ({cue.label})" if cue.label else ""
            lines.append(
                f"  {mm:02d}:{ss:02d}.{cs:02d}  {cue.type:<14}  conf={cue.confidence:.2f}{tail}"
            )

    return "\n".join(lines)


def save_sidecar(r: QualityReport, output_dir: Path) -> Path:
    """Sauvegarde un JSON sidecar `<slug>.json`."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{r.slug}.json"
    out_path.write_text(r.model_dump_json(indent=2), encoding="utf-8")
    return out_path

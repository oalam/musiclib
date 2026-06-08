"""Extraction de metadata audio via ffprobe."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .types import MetadataReport

LOSSLESS_CODECS = {"flac", "alac", "wav", "pcm_s16le", "pcm_s24le", "pcm_f32le", "ape", "wavpack"}


class FFprobeError(RuntimeError):
    """Echec d'extraction ffprobe."""


def probe(path: Path) -> MetadataReport:
    """Extrait codec / bitrate / sample rate / bit depth via ffprobe."""
    try:
        raw = subprocess.check_output(
            [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", "-show_streams", str(path),
            ],
            text=True,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as exc:
        raise FFprobeError(f"ffprobe a echoue pour {path}: {exc.stderr}") from exc

    data = json.loads(raw)
    audio_streams = [s for s in data.get("streams", []) if s.get("codec_type") == "audio"]
    if not audio_streams:
        raise FFprobeError(f"Aucun flux audio dans {path}")
    stream = audio_streams[0]
    fmt = data.get("format", {})

    codec = (stream.get("codec_name") or "unknown").lower()
    sample_rate = int(stream.get("sample_rate", 0))
    channels = int(stream.get("channels", 1))

    # Bit depth : present pour les codecs lossless / PCM
    bit_depth: int | None = None
    if "bits_per_raw_sample" in stream:
        try:
            bit_depth = int(stream["bits_per_raw_sample"])
        except (TypeError, ValueError):
            bit_depth = None
    elif "bits_per_sample" in stream:
        try:
            bps = int(stream["bits_per_sample"])
            bit_depth = bps if bps > 0 else None
        except (TypeError, ValueError):
            bit_depth = None

    # Bitrate : stream-level prefere, sinon format-level
    bitrate_kbps: int | None = None
    raw_br = stream.get("bit_rate") or fmt.get("bit_rate")
    if raw_br:
        try:
            bitrate_kbps = int(int(raw_br) / 1000)
        except (TypeError, ValueError):
            bitrate_kbps = None

    duration_s = 0.0
    if "duration" in fmt:
        try:
            duration_s = float(fmt["duration"])
        except (TypeError, ValueError):
            duration_s = 0.0
    elif "duration" in stream:
        try:
            duration_s = float(stream["duration"])
        except (TypeError, ValueError):
            duration_s = 0.0

    container = (fmt.get("format_name") or "").split(",")[0]
    encoder = (fmt.get("tags") or {}).get("encoder")

    return MetadataReport(
        codec=codec,
        bitrate_kbps=bitrate_kbps,
        sample_rate_hz=sample_rate,
        bit_depth=bit_depth,
        channels=channels,
        duration_s=duration_s,
        container=container,
        is_lossless_container=codec in LOSSLESS_CODECS,
        encoder=encoder,
    )

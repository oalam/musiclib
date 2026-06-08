"""Rendu PNG signature pour un track + index Markdown pour Obsidian.

Format de sortie : PNG 1200×320 px par track, lisible en mode 'aerial
view' pour scanner visuellement la library.

Layout (haut -> bas) :
- Header texte : Artist — Title | BPM | Camelot key | energy | LUFS | durée
- Waveform RMS (50px) : energie au fil du temps
- Mel-spectrogram en log-frequency, palette magma (150px)
- Bande structure (40px) : segments colores par label
- Marqueurs cue points : lignes verticales blanches avec labels

Les couleurs des segments structurels :
- intro      : gris clair
- build      : orange
- peak       : rouge
- main       : bleu
- breakdown  : violet
- outro      : gris fonce
"""
from __future__ import annotations

import warnings
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np


_SEGMENT_COLORS: dict[str, str] = {
    "intro":     "#bdbdbd",
    "build":     "#fb923c",
    "peak":      "#dc2626",
    "main":      "#3b82f6",
    "breakdown": "#a855f7",
    "outro":     "#525252",
}


def _format_header(entry: dict[str, str], sidecar: dict[str, Any]) -> str:
    artist = entry.get("artist", "?")
    title = entry.get("title", "?")
    bpm = entry.get("bpm", "?")
    key = entry.get("key", "?")
    energy = entry.get("energy", "?")
    duration = entry.get("duration", "?")
    lufs = ((sidecar.get("loudness") or {}).get("integrated_lufs"))
    lufs_str = f"{lufs:.1f} LUFS" if lufs is not None else ""
    tonal = ((sidecar.get("frequency_bands") or {}).get("tonal_profile"))

    # Camelot code si dispo
    try:
        from .keys import to_camelot
        camelot = to_camelot(key) or ""
        key_label = f"{key} ({camelot})" if camelot else key
    except Exception:
        key_label = key

    parts = [f"{artist} — {title}"]
    parts.append(f"BPM {bpm}")
    parts.append(f"key {key_label}")
    if energy:
        parts.append(f"energy {energy}")
    if lufs_str:
        parts.append(lufs_str)
    if tonal:
        parts.append(tonal)
    parts.append(duration)
    return "  |  ".join(parts)


def _compute_rms_curve(mono: np.ndarray, sr: int, hop_s: float = 0.1) -> tuple[np.ndarray, np.ndarray]:
    """Courbe RMS sous-echantillonnee a 10 Hz pour affichage waveform."""
    hop = max(1, int(hop_s * sr))
    n = len(mono) // hop
    if n == 0:
        return np.array([0.0]), np.array([0.0])
    chunks = mono[: n * hop].reshape(n, hop)
    rms = np.sqrt(np.mean(chunks.astype(np.float64) ** 2, axis=1))
    times = np.arange(n) * hop_s
    return times, rms.astype(np.float32)


def render_track(
    audio_path: Path,
    entry: dict[str, str],
    sidecar: dict[str, Any],
    output_path: Path,
) -> None:
    """Genere une PNG signature pour `audio_path` dans `output_path`."""
    import matplotlib
    matplotlib.use("Agg")  # headless, pas de fenetre
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    from .audio_loader import load_audio, to_mono

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import librosa
        import librosa.display

        data, sr = load_audio(audio_path)
        mono = to_mono(data)
        duration = len(mono) / sr

        # RMS curve
        rms_times, rms_values = _compute_rms_curve(mono, sr, hop_s=0.1)

        # Mel-spectrogram
        mel = librosa.feature.melspectrogram(
            y=mono, sr=sr, n_mels=128, fmax=sr // 2,
        )
        mel_db = librosa.power_to_db(mel, ref=np.max)

    # --- Layout matplotlib ---
    fig = plt.figure(figsize=(12.0, 3.2), dpi=100)
    gs = fig.add_gridspec(
        3, 1, height_ratios=[0.7, 3.0, 0.5],
        hspace=0.05, left=0.04, right=0.99, top=0.88, bottom=0.06,
    )
    fig.suptitle(
        _format_header(entry, sidecar), fontsize=10, y=0.96,
        x=0.04, ha="left", fontweight="bold",
    )

    # Row 0: waveform (RMS envelope)
    ax_wave = fig.add_subplot(gs[0])
    ax_wave.fill_between(rms_times, 0, rms_values, color="#0f172a", alpha=0.9)
    ax_wave.set_xlim(0, duration)
    ax_wave.set_ylim(0, max(rms_values.max() * 1.1, 0.01))
    ax_wave.set_xticks([])
    ax_wave.set_yticks([])
    for spine in ax_wave.spines.values():
        spine.set_visible(False)

    # Row 1: mel-spectrogram (palette magma)
    ax_spec = fig.add_subplot(gs[1])
    librosa.display.specshow(
        mel_db, sr=sr, x_axis="time", y_axis="mel",
        ax=ax_spec, cmap="magma", fmax=sr // 2,
    )
    ax_spec.set_xlabel("")
    ax_spec.set_ylabel("")
    ax_spec.tick_params(labelsize=7)

    # Overlay cue points sur le spectrogram
    cues = (sidecar.get("cues") or {}).get("cues") or []
    for cue in cues:
        t = cue.get("time_s", 0)
        cue_type = cue.get("type", "")
        ax_spec.axvline(t, color="white", linewidth=0.6, alpha=0.65)
        ax_spec.text(
            t, ax_spec.get_ylim()[1] * 0.92, cue_type[:5],
            color="white", fontsize=6, rotation=90,
            ha="right", va="top", alpha=0.85,
        )

    # Row 2: structure bands
    ax_struct = fig.add_subplot(gs[2])
    segments = (sidecar.get("structure") or {}).get("segments") or []
    for seg in segments:
        start = seg.get("start_s", 0)
        end = seg.get("end_s", duration)
        label = seg.get("label", "main")
        color = _SEGMENT_COLORS.get(label, "#9ca3af")
        ax_struct.add_patch(Rectangle(
            (start, 0), end - start, 1, color=color, alpha=0.8,
        ))
        seg_w = end - start
        if seg_w > duration * 0.05:  # label si segment > 5% du total
            ax_struct.text(
                (start + end) / 2, 0.5, label[:9],
                color="white", fontsize=7, ha="center", va="center",
                fontweight="bold",
            )
    ax_struct.set_xlim(0, duration)
    ax_struct.set_ylim(0, 1)
    ax_struct.set_xticks([])
    ax_struct.set_yticks([])
    for spine in ax_struct.spines.values():
        spine.set_visible(False)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Suppression des warnings matplotlib sur glyphs unicodes manquants
    # (emojis, math bold chars) — affectent juste le rendu d'un caractere
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        fig.savefig(str(output_path), dpi=100, facecolor="white")
    plt.close(fig)


def write_index_md(
    entries: dict[str, dict[str, str]],
    visuals_dir: Path,
) -> Path:
    """Genere `visuals_dir/_index.md` qui embarque toutes les PNG existantes.

    Une section par entree qui a un fichier PNG. Embed via wikilink Obsidian.
    Retourne le path de l'index."""
    lines = [
        "---",
        f"updated: {date.today().isoformat()}",
        f"count: {len(entries)}",
        "tags: [library, visuels]",
        "---",
        "",
        "# Visuels library",
        "",
        "> Genere par `scripts/visualize.py`. Scroller pour browser la library",
        "> en mode 'vue d'avion'. Chaque PNG = waveform + mel-spectrogram +",
        "> structure + cue points overlay.",
        "",
    ]
    sorted_items = sorted(
        entries.items(),
        key=lambda kv: (
            kv[1].get("artist", "").lower(),
            kv[1].get("title", "").lower(),
        ),
    )
    for slug, fields in sorted_items:
        artist = fields.get("artist", "?")
        title = fields.get("title", "?")
        png_path = visuals_dir / f"{slug}.png"
        if not png_path.exists():
            continue
        lines.append(f"## {artist} — {title}")
        lines.append("")
        lines.append(f"![[visuals/{slug}.png]]")
        lines.append("")

    visuals_dir.mkdir(parents=True, exist_ok=True)
    index_path = visuals_dir / "_index.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    return index_path

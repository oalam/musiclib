"""Inference des champs energy / mood / tags depuis les rapports d'analyse.

- `energy` : objectif, derive de BPM + LUFS + crest factor
- `mood`   : suggere, derive de mode (maj/min) + tempo + LUFS, avec marqueur `?`
- `tags`   : suggere, derive de genre yt-dlp + BPM range + bandwidth, avec `?`

Les suggestions (`mood`/`tags`) sont marquees d'un `?` final pour signaler
qu'elles sont a valider a l'oreille, pas mesurees."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_sidecar(quality_dir: Path, slug: str) -> dict[str, Any] | None:
    path = quality_dir / f"{slug}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _resolve_bpm(sidecar: dict[str, Any], entry: dict[str, str]) -> float:
    """Prefere le BPM de library.md (peut etre corrige a la main) au tempo librosa."""
    raw = entry.get("bpm", "").strip()
    if raw:
        try:
            v = float(raw)
            if v > 0:
                return v
        except ValueError:
            pass
    return float(((sidecar.get("beats") or {}).get("tempo_bpm")) or 0)


def _bpm_score(bpm: float) -> float:
    if bpm <= 0:
        return 5.0
    if bpm < 100:
        return 2.0
    if bpm < 130:
        return 4.0
    if bpm < 160:
        return 6.0
    if bpm < 180:
        return 7.5
    if bpm < 200:
        return 9.0
    return 9.5


def _lufs_score(lufs: float) -> float:
    if lufs >= -6:
        return 9.5
    if lufs >= -8:
        return 8.0
    if lufs >= -10:
        return 6.5
    if lufs >= -13:
        return 4.5
    if lufs >= -18:
        return 2.5
    return 1.0


def _crest_score(crest: float) -> float:
    """Crest bas = compressé = énergie loud."""
    if crest <= 5:
        return 9.0
    if crest <= 8:
        return 7.0
    if crest <= 11:
        return 5.0
    if crest <= 14:
        return 3.0
    return 2.0


def infer_energy(sidecar: dict[str, Any], entry: dict[str, str]) -> str:
    """Energie 0-10 derivee + label."""
    bpm = _resolve_bpm(sidecar, entry)
    lufs = float(((sidecar.get("loudness") or {}).get("integrated_lufs")) or -23)
    crest = float(((sidecar.get("dynamic") or {}).get("crest_factor_db")) or 12)
    raw = _bpm_score(bpm) * 0.50 + _lufs_score(lufs) * 0.30 + _crest_score(crest) * 0.20
    score = max(0.0, min(10.0, raw))
    if score >= 8.5:
        return "very_high"
    if score >= 7.0:
        return "high"
    if score >= 5.0:
        return "medium"
    if score >= 3.0:
        return "low"
    return "very_low"


def infer_mood(sidecar: dict[str, Any], entry: dict[str, str]) -> str:
    """Suggestion de mood (1-3 mots) suffixe d'un `?`."""
    bpm = _resolve_bpm(sidecar, entry)
    lufs = float(((sidecar.get("loudness") or {}).get("integrated_lufs")) or -23)
    key_str = entry.get("key")
    mode = "minor" if key_str and " minor" in key_str.lower() else (
        "major" if key_str and " major" in key_str.lower() else "unknown"
    )

    tags: list[str] = []
    # Mode -> couleur
    if mode == "minor":
        tags.append("dark")
    elif mode == "major":
        tags.append("uplifting")

    # Tempo -> intensite
    if bpm >= 170:
        tags.append("driving")
    elif bpm >= 140:
        tags.append("energetic")
    elif bpm > 0 and bpm < 100:
        tags.append("chill")

    # LUFS -> presence
    if lufs >= -7:
        tags.append("peak time")
    elif lufs <= -14:
        tags.append("intimate")

    if not tags:
        return ""
    return ", ".join(tags) + "?"


# BPM ranges -> genres typiques (heuristique large, single label par track)
_BPM_GENRES: list[tuple[float, float, str]] = [
    (60, 95, "downtempo"),
    (95, 115, "hip-hop"),
    (118, 128, "house"),
    (128, 140, "techno"),
    (140, 155, "dubstep"),
    (155, 165, "breakbeat"),
    (165, 180, "dnb"),
    (180, 210, "tribe"),
    (210, 260, "hardcore"),
]


def infer_genre(sidecar: dict[str, Any], entry: dict[str, str]) -> str:
    """Genre classification depuis BPM (library.md prioritaire) + genre yt-dlp existant.

    Sans `?` : les ranges BPM->genre sont bien etablis (DnB 170-180, tribe
    180+, etc.). A editer si la detection BPM librosa est fausse et que
    library.md n'a pas ete corrige."""
    bpm = _resolve_bpm(sidecar, entry)
    existing_genre = entry.get("genre", "")
    genres: list[str] = []

    # Genre yt-dlp d'abord (souvent vide, parfois precis sur SC)
    if existing_genre:
        for g in existing_genre.split(","):
            g = g.strip().lower()
            if g and g not in genres:
                genres.append(g)

    # Genre BPM-derive si pas deja present
    if bpm > 0:
        for lo, hi, name in _BPM_GENRES:
            if lo <= bpm < hi and name not in genres:
                genres.append(name)
                break

    return ", ".join(genres)


def infer_tags(sidecar: dict[str, Any]) -> str:
    """Tags techniques objectifs : lo-fi, half-time-suspect, etc. Sans `?`."""
    tags: list[str] = []
    bandwidth = float(((sidecar.get("spectral") or {}).get("bandwidth_cutoff_hz")) or 20000)
    half_corrected = bool(((sidecar.get("beats") or {}).get("half_time_corrected")) or False)

    if bandwidth < 14000:
        tags.append("lo-fi")
    if half_corrected:
        tags.append("half-time-suspect")

    return ", ".join(tags)

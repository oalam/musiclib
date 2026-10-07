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

from library_md import slugify


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


# Style -> fenetre de tempo plausible (hub, arbitre le 2026-10-07). Sert a
# corriger les erreurs d'octave de la detection (198.8 -> 99.4 en shatta).
# Mots-cles au format slug (tokens separes par `_`) ; rapport haut/bas < 2
# pour qu'une seule correction x2 / /2 tombe dans la fenetre. Styles trop
# larges (swing, tango, rock, folk, soul) volontairement absents, comme
# « roots » (titre de morceaux tekno).
STYLE_BPM_WINDOWS: list[tuple[tuple[str, ...], float, float]] = [
    (("reggae", "dub", "one_drop"), 60, 95),
    (("shatta", "dancehall", "reggaeton", "latino", "afro", "afrobeat",
      "afrobeats", "dembow", "baile_funk", "kuduro"), 85, 115),
    (("hip_hop", "hiphop", "rap", "slow", "rb", "rnb"), 60, 110),
    (("disco", "funk", "house", "techouse", "tech_house"), 110, 130),
    (("techno", "hard_techno"), 125, 150),
    (("dubstep",), 135, 150),
    (("dnb", "drum_bass", "drum_and_bass", "drum_n_bass", "jungle",
      "footwork"), 160, 180),
    (("tribe", "tekno", "mental_tekno", "mentaltekno", "acidcore", "acid_core",
      "hardtek"), 160, 210),
    (("hardcore",), 180, 250),
]


def _has_keyword(tokens: list[str], keyword: str) -> bool:
    kw = keyword.split("_")
    return any(tokens[i:i + len(kw)] == kw for i in range(len(tokens) - len(kw) + 1))


def style_window(texts: list[str]) -> tuple[str, float, float] | None:
    """Premier texte (ordre de priorite) qui designe un style sans ambiguite.

    Un texte qui matche plusieurs fenetres differentes (« dancehall dubstep
    remix ») est ignore ; on passe au suivant. Retourne (mot-cle, lo, hi)."""
    for text in texts:
        tokens = slugify(text).split("_") if text else []
        found: dict[tuple[float, float], str] = {}
        for kws, lo, hi in STYLE_BPM_WINDOWS:
            for kw in kws:
                if _has_keyword(tokens, kw):
                    found.setdefault((lo, hi), kw)
        if len(found) == 1:
            (lo, hi), kw = next(iter(found.items()))
            return kw, lo, hi
    return None


def fold_bpm(bpm: float, lo: float, hi: float) -> float | None:
    """Ramene `bpm` dans [lo, hi] par x2 / /2 ; None si aucune octave n'y tombe."""
    if bpm <= 0:
        return None
    for factor in (1.0, 0.5, 2.0, 0.25, 4.0):
        candidate = bpm * factor
        if lo <= candidate <= hi:
            return round(candidate, 1)
    return None


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

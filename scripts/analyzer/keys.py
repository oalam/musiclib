"""Conversion key musicale -> Camelot Wheel + scoring de compatibilite harmonique.

Camelot Wheel : systeme de notation utilise en DJing harmonique.
12 positions x 2 modes (A=minor, B=major). Mix harmoniques :
- meme code : parfait (8A -> 8A)
- meme nombre, lettre opposee : relatif maj/min (8A -> 8B)
- +/-1 sur la roue, meme lettre : quinte/quarte (8A -> 7A, 9A)
- +/-2 sur la roue : possible avec transition energetique
"""
from __future__ import annotations

import re

# Mapping (note, mode) -> Camelot code.
# Notes normalisees minuscules, sharps avec '#', plats avec 'b'.
_CAMELOT_MAP: dict[tuple[str, str], str] = {
    # Mineur (A)
    ("g#", "minor"): "1A", ("ab", "minor"): "1A",
    ("d#", "minor"): "2A", ("eb", "minor"): "2A",
    ("a#", "minor"): "3A", ("bb", "minor"): "3A",
    ("f",  "minor"): "4A",
    ("c",  "minor"): "5A",
    ("g",  "minor"): "6A",
    ("d",  "minor"): "7A",
    ("a",  "minor"): "8A",
    ("e",  "minor"): "9A",
    ("b",  "minor"): "10A",
    ("f#", "minor"): "11A", ("gb", "minor"): "11A",
    ("c#", "minor"): "12A", ("db", "minor"): "12A",
    # Majeur (B)
    ("b",  "major"): "1B",
    ("f#", "major"): "2B",  ("gb", "major"): "2B",
    ("c#", "major"): "3B",  ("db", "major"): "3B",
    ("g#", "major"): "4B",  ("ab", "major"): "4B",
    ("d#", "major"): "5B",  ("eb", "major"): "5B",
    ("a#", "major"): "6B",  ("bb", "major"): "6B",
    ("f",  "major"): "7B",
    ("c",  "major"): "8B",
    ("g",  "major"): "9B",
    ("d",  "major"): "10B",
    ("a",  "major"): "11B",
    ("e",  "major"): "12B",
}

_KEY_RE = re.compile(
    r"^\s*([a-g])([#b]?)\s*(major|minor|maj|min|m|M)?\s*$"
)


def to_camelot(key_str: str | None) -> str | None:
    """Parse 'A minor' / 'C# major' / 'Eb min' / 'F' -> '8A' / '3B' / etc.

    Si pas de mode specifie, on suppose majeur. Retourne None si la chaine
    n'est pas parsable."""
    if not key_str:
        return None
    match = _KEY_RE.match(key_str.strip().lower())
    if not match:
        return None
    note = match.group(1) + (match.group(2) or "")
    mode_raw = (match.group(3) or "major").lower()
    if mode_raw in ("minor", "min", "m"):
        mode = "minor"
    else:
        mode = "major"
    return _CAMELOT_MAP.get((note, mode))


def key_compatibility(key_a: str | None, key_b: str | None) -> float:
    """Score de compatibilite harmonique entre deux keys [0, 1]."""
    ca = to_camelot(key_a)
    cb = to_camelot(key_b)
    if not ca or not cb:
        return 0.0
    na, la = int(ca[:-1]), ca[-1]
    nb, lb = int(cb[:-1]), cb[-1]
    if na == nb and la == lb:
        return 1.0
    if na == nb and la != lb:
        return 0.9  # relatif majeur/mineur
    if la == lb:
        # Distance circulaire sur la roue (1..12)
        diff = min(abs(na - nb), 12 - abs(na - nb))
        if diff == 1:
            return 0.85  # quinte / quarte
        if diff == 2:
            return 0.55  # encore mixable avec boost energetique
    return 0.0

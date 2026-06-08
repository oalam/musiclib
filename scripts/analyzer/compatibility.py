"""Compatibilite de mix entre deux morceaux : BPM + key + energie -> score.

Sert de coeur a :
- la recommandation d'enchainement (`setbuilder.py compatible <slug>`)
- la generation de playlist (`setbuilder.py playlist`)
"""
from __future__ import annotations

from dataclasses import dataclass

from .keys import key_compatibility, to_camelot

# Mapping `energy` libre du frontmatter library.md -> echelle 1-5.
_ENERGY_MAP: dict[str, int] = {
    "very_low": 1, "tres bas": 1, "verylow": 1,
    "low": 2, "bas": 2, "soft": 2, "calme": 2,
    "medium": 3, "mid": 3, "moyen": 3, "med": 3,
    "high": 4, "haut": 4, "fort": 4,
    "very_high": 5, "tres haut": 5, "peak": 5, "max": 5, "veryhigh": 5,
}


@dataclass
class TransitionScore:
    """Detail du score d'enchainement entre A -> B."""
    bpm: float
    key: float
    energy: float
    total: float
    notes: list[str]


def parse_energy(value: str | None) -> float | None:
    """Parse `energy` (mot ou nombre 0-10) -> 1-5. None si non interpretable."""
    if not value:
        return None
    v = value.strip().lower()
    if v in _ENERGY_MAP:
        return float(_ENERGY_MAP[v])
    # Numerique ?
    try:
        n = float(v)
    except ValueError:
        return None
    # 0-10 -> 1-5 lineaire
    return max(1.0, min(5.0, 1.0 + n / 2.5))


def parse_bpm(value: str | None) -> float | None:
    if not value:
        return None
    try:
        bpm = float(value)
    except ValueError:
        return None
    return bpm if bpm > 0 else None


def bpm_compatibility(a: float, b: float) -> tuple[float, str]:
    """Score [0, 1] + label texte du type de mix."""
    if a <= 0 or b <= 0:
        return 0.0, "n/a"
    ratio = b / a
    if 0.97 <= ratio <= 1.03:
        return 1.0, "direct"
    if 0.94 <= ratio <= 1.06:
        return 0.85, "tempo nudge"
    # Half / double time : 2x ou 0.5x avec tolerance 4%
    for k, label in [(2.0, "double-time"), (0.5, "half-time")]:
        if abs(ratio - k) / k <= 0.04:
            return 0.7, label
    if 0.90 <= ratio <= 1.10:
        return 0.5, "pitch shift"
    return 0.0, "incompatible"


def energy_compatibility(
    a: float | None,
    b: float | None,
    direction: str,
) -> tuple[float, str]:
    """direction = 'maintain' | 'rising' | 'falling'.

    `rising` et `falling` interdisent les sauts > 1 cran dans le mauvais
    sens (score 0 = veto), evitant les creux/plateaux dans un build-up."""
    if a is None or b is None:
        return 0.5, "inconnu"
    delta = b - a
    if direction == "rising":
        if delta >= 1:
            return 1.0, f"+{delta:.0f}"
        if delta >= 0:
            return 0.8, f"~{delta:+.0f}"
        if delta >= -1:
            return 0.4, f"{delta:+.0f}"
        if delta >= -2:
            return 0.15, f"{delta:+.0f}"  # forte penalite
        return 0.0, f"{delta:+.0f}"  # veto >2 crans de chute
    if direction == "falling":
        if delta <= -1:
            return 1.0, f"{delta:+.0f}"
        if delta <= 0:
            return 0.8, f"~{delta:+.0f}"
        if delta <= 1:
            return 0.4, f"+{delta:+.0f}"
        if delta <= 2:
            return 0.15, f"+{delta:+.0f}"
        return 0.0, f"+{delta:+.0f}"
    # maintain
    abs_d = abs(delta)
    if abs_d <= 0.5:
        return 1.0, "egal"
    if abs_d <= 1.5:
        return 0.7, f"{delta:+.0f}"
    return 0.3, f"{delta:+.0f}"


def score_transition(
    from_track: dict[str, str],
    to_track: dict[str, str],
    direction: str = "maintain",
    weights: tuple[float, float, float] = (0.5, 0.3, 0.2),
) -> TransitionScore:
    """Score global d'enchainement from -> to.

    Poids par defaut : BPM 50% / key 30% / energie 20%.
    """
    bpm_a = parse_bpm(from_track.get("bpm"))
    bpm_b = parse_bpm(to_track.get("bpm"))
    bpm_s, bpm_lbl = bpm_compatibility(bpm_a or 0, bpm_b or 0)

    key_a = from_track.get("key")
    key_b = to_track.get("key")
    key_s = key_compatibility(key_a, key_b)
    ca = to_camelot(key_a)
    cb = to_camelot(key_b)
    key_lbl = (
        f"{ca or '?'}->{cb or '?'}"
        if (ca or cb)
        else "n/a"
    )

    en_a = parse_energy(from_track.get("energy"))
    en_b = parse_energy(to_track.get("energy"))
    en_s, en_lbl = energy_compatibility(en_a, en_b, direction)

    w_bpm, w_key, w_en = weights
    total = bpm_s * w_bpm + key_s * w_key + en_s * w_en

    # Veto hard : sous rising/falling, une chute/montee trop violente
    # d'energie (en_s == 0) annule la transition meme si BPM+key sont bons.
    if direction in ("rising", "falling") and en_s == 0.0:
        total = 0.0

    return TransitionScore(
        bpm=round(bpm_s, 2),
        key=round(key_s, 2),
        energy=round(en_s, 2),
        total=round(total, 3),
        notes=[f"bpm:{bpm_lbl}", f"key:{key_lbl}", f"energy:{en_lbl}"],
    )

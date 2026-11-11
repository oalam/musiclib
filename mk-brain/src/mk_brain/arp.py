"""Arpégiateur (slices 11 à 15) : ordre des notes tenues, octaves, motifs, accords."""

from __future__ import annotations

from collections.abc import Sequence, Set
from typing import Literal

ArpOrder = Literal["up", "down", "updown", "played", "random"]
ORDERS: tuple[ArpOrder, ...] = ("up", "down", "updown", "played", "random")
ORDER_LABELS: dict[ArpOrder, str] = {  # écran : 4 lettres
    "up": "UP",
    "down": "DOWN",
    "updown": "UPDN",
    "played": "PLAY",
    "random": "RAND",
}
MAX_OCTAVES = 3
GATE_MIN, GATE_MAX, GATE_STEP = 10, 100, 5  # durée d'une note, en % de la division

# Accords (slice 15) : un pad = un accord pris dans la gamme. Pour chaque note de l'accord,
# les candidates en demi-tons au-dessus de la fondamentale, la première dans la gamme gagne.
ArpChord = Literal["off", "tri", "7th", "sus2", "sus4", "pwr"]
CHORDS: tuple[ArpChord, ...] = ("off", "tri", "7th", "sus2", "sus4", "pwr")
CHORD_LABELS: dict[ArpChord, str] = {
    "off": "OFF",
    "tri": "TRI",
    "7th": "7TH",
    "sus2": "SUS2",
    "sus4": "SUS4",
    "pwr": "PWR",
}
_SECOND, _THIRD, _FOURTH = (2, 1, 3), (3, 4), (5, 6, 4)
_FIFTH, _SEVENTH, _OCTAVE = (7, 6, 8), (10, 11, 9), (12,)
CHORD_TONES: dict[ArpChord, tuple[tuple[int, ...], ...]] = {
    "off": (),
    "tri": (_THIRD, _FIFTH),
    "7th": (_THIRD, _FIFTH, _SEVENTH),
    "sus2": (_SECOND, _FIFTH),
    "sus4": (_FOURTH, _FIFTH),
    "pwr": (_FIFTH, _OCTAVE),
}

MOTIF_STEPS = 16
MOTIF_OFF = "OFF"  # pas de motif : une note par division, sans atténuation
MOTIF_NAME_MAX = 4  # largeur de la case de l'écran
NOTE, ACCENT, REST, TIE = "x", "X", ".", "-"  # un caractère par pas du motif

Held = tuple[int, int]  # (pad, note)


class MotifError(ValueError):
    """Motif d'arpège mal écrit (longueur, caractère inconnu, aucune note)."""


def parse_motif(text: str) -> str:
    """Motif de la config → ses 16 pas, sans les espaces qui séparent les temps."""
    steps = "".join(text.split())
    if len(steps) != MOTIF_STEPS:
        raise MotifError(f"motif {text!r} : {len(steps)} pas, {MOTIF_STEPS} attendus")
    unknown = sorted(set(steps) - {NOTE, ACCENT, REST, TIE})
    if unknown:
        raise MotifError(f"motif {text!r} : pas inconnus {''.join(unknown)!r}")
    if NOTE not in steps and ACCENT not in steps:
        raise MotifError(f"motif {text!r} : aucune note")
    return steps


def ties_after(steps: str, index: int) -> int:
    """Nombre de pas liés qui prolongent la note du pas `index` (le motif boucle)."""
    n = 0
    while n < MOTIF_STEPS - 1 and steps[(index + n + 1) % MOTIF_STEPS] == TIE:
        n += 1
    return n


def sequence(held: Sequence[Held], order: ArpOrder, octaves: int) -> list[Held]:
    """Un tour d'arpège : les notes tenues (dans l'ordre d'appui) sur `octaves` octaves.

    `played` et `random` gardent l'ordre d'appui, octave après octave (le tirage se fait
    à l'appel) ; `updown` ne répète ni le sommet ni la base. Notes au-delà de 127 écartées."""
    wide = [
        (pad, note + 12 * o) for o in range(octaves) for pad, note in held if note + 12 * o < 128
    ]
    if order in ("played", "random"):
        return wide
    up = sorted(wide, key=lambda k: (k[1], k[0]))
    if order == "up":
        return up
    if order == "down":
        return up[::-1]
    return up + up[-2:0:-1]


def chord(note: int, kind: ArpChord, scale: Set[int]) -> list[int]:
    """Notes de l'accord `kind` sur la fondamentale `note`, prises dans `scale` (classes de
    hauteur 0-11) : la première candidate dans la gamme, sinon la première tout court."""
    tones = [note]
    for candidates in CHORD_TONES[kind]:
        tones.append(
            note + next((c for c in candidates if (note + c) % 12 in scale), candidates[0])
        )
    return tones


def spread(held: Sequence[Held], kind: ArpChord, scale: Set[int]) -> list[Held]:
    """Pads tenus → notes de leurs accords, dans l'ordre d'appui ; une même note une seule
    fois (le premier pad qui l'apporte la garde), rien au-delà de 127."""
    out: list[Held] = []
    seen: set[int] = set()
    for pad, note in held:
        for tone in chord(note, kind, scale):
            if tone < 128 and tone not in seen:
                seen.add(tone)
                out.append((pad, tone))
    return out

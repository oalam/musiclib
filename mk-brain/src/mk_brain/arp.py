"""Arpégiateur (slices 11 et 12) : ordre des notes tenues, étendue en octaves, motifs."""

from __future__ import annotations

from collections.abc import Sequence
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

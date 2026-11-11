"""Arpégiateur (slice 11) : ordre des notes tenues, étendue en octaves."""

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

Held = tuple[int, int]  # (pad, note)


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

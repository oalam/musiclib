"""Quantize « nearest » et swing, en ticks depuis le Start (24 par noire)."""

from __future__ import annotations

import math
from typing import Literal

from mk_brain.clock import TICKS_PER_STEP

QuantizeMode = Literal["off", "1/16", "1/8"]
QUANTIZE_CYCLE: tuple[QuantizeMode, ...] = ("off", "1/16", "1/8")
GRID_TICKS: dict[QuantizeMode, int] = {"1/16": 6, "1/8": 12}
SWING_MIN, SWING_MAX = 50, 75


def nearest(ticks: float, grid: float) -> tuple[float, bool]:
    """Pas visé et envoi immédiat ou non.

    Frappe dans la première moitié après un pas (3 ticks en 1/16) : immédiat,
    sinon pas suivant (SPEC, Quantize).
    """
    base = math.floor(ticks / grid) * grid
    if ticks - base < grid / 2:
        return base, True
    return base + grid, False


def swing_offset(position: float, swing: int) -> float:
    """Retard en ticks d'un 16ᵉ impair : à 75 %, le 16ᵉ tombe aux 3/4 de la croche."""
    step = position / TICKS_PER_STEP
    if step != int(step) or int(step) % 2 == 0:
        return 0.0
    return swing / 100 * 2 * TICKS_PER_STEP - TICKS_PER_STEP


def clamp_swing(value: int) -> int:
    return max(SWING_MIN, min(SWING_MAX, value))

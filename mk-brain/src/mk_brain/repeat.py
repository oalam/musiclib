"""Note repeat : divisions en ticks (24 par noire), dans l'ordre des 8 boutons d'écran."""

from __future__ import annotations

DIVISIONS: tuple[tuple[str, float], ...] = (
    ("1/4", 24),
    ("1/8", 12),
    ("1/8T", 8),
    ("1/16", 6),
    ("1/16T", 4),
    ("1/32", 3),
    ("1/32T", 2),
    ("1/64", 1.5),
)
DIVISION_TICKS: dict[str, float] = dict(DIVISIONS)
GATE = 0.5  # durée de chaque coup = moitié de la division (note off)

from __future__ import annotations

from mk_brain.quantize import clamp_swing, nearest, swing_offset


def test_nearest_half_grid_rule() -> None:
    assert nearest(6, 6) == (6, True)
    assert nearest(8.9, 6) == (6, True)  # < 3 ticks après : immédiat
    assert nearest(9, 6) == (12, False)
    assert nearest(17, 12) == (12, True)
    assert nearest(18, 12) == (24, False)


def test_swing_only_odd_sixteenths() -> None:
    assert swing_offset(6, 75) == 3  # 0,75 × 12 − 6
    assert swing_offset(12, 75) == 0
    assert swing_offset(6, 50) == 0
    assert swing_offset(7, 75) == 0  # hors grille


def test_clamp_swing() -> None:
    assert (clamp_swing(40), clamp_swing(60), clamp_swing(90)) == (50, 60, 75)

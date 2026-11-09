from __future__ import annotations

from mk_brain.repeat import DIVISION_TICKS, DIVISIONS


def test_eight_divisions_in_ticks() -> None:
    assert len(DIVISIONS) == 8
    assert DIVISION_TICKS["1/16"] == 6 and DIVISION_TICKS["1/16T"] == 4
    assert DIVISION_TICKS["1/64"] == 1.5

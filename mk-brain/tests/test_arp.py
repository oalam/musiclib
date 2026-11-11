from __future__ import annotations

from mk_brain.arp import sequence

HELD = [(5, 65), (1, 58), (3, 61)]  # (pad, note), dans l'ordre d'appui


def test_orders_over_one_octave() -> None:
    assert [n for _, n in sequence(HELD, "up", 1)] == [58, 61, 65]
    assert [n for _, n in sequence(HELD, "down", 1)] == [65, 61, 58]
    assert [n for _, n in sequence(HELD, "updown", 1)] == [58, 61, 65, 61]
    assert sequence(HELD, "played", 1) == HELD
    assert sequence(HELD, "random", 1) == HELD  # le tirage se fait à l'appel


def test_octaves_stack_and_keep_the_pad() -> None:
    assert sequence(HELD, "up", 2) == [(1, 58), (3, 61), (5, 65), (1, 70), (3, 73), (5, 77)]
    assert [n for _, n in sequence(HELD, "played", 2)] == [65, 58, 61, 77, 70, 73]
    assert [n for _, n in sequence([(1, 60)], "updown", 1)] == [60]
    assert [n for _, n in sequence([(1, 60), (2, 64)], "updown", 1)] == [60, 64]


def test_notes_above_127_are_dropped() -> None:
    assert [n for _, n in sequence([(1, 120)], "up", 3)] == [120]

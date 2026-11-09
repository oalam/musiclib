from __future__ import annotations

from mk_brain.faders import DEFAULT_VALUE, Faders

PAGE = [("CUT", 74), ("RES", 75), ("ENV", 77), ("DEC", 81)] + [("X", 100 + i) for i in range(4)]


def make() -> Faders:
    return Faders(PAGE, mute_cc=94, raw_per_step=4)


def test_turn_accumulates_raw_units_and_clamps() -> None:
    f = make()
    assert f.turn(7, 1, 2) is None  # demi-cran : rien
    assert f.turn(7, 1, 2) == (74, DEFAULT_VALUE + 1)
    assert f.turn(7, 1, -8) == (74, DEFAULT_VALUE - 1)
    assert f.turn(7, 1, 4 * 200) == (74, 127)
    assert f.turn(7, 1, 4) is None  # déjà au maximum


def test_learns_from_dt2_and_marks_stale_on_pattern_change() -> None:
    f = make()
    f.received(7, 74, 20)  # bouton tourné sur la DT2
    view = f.view(7)[0]
    assert (view.value, view.known, view.stale) == (20, True, False)
    f.pattern_changed()
    assert f.view(7)[0].stale
    assert f.turn(7, 1, 4) == (74, 21)  # repart de la dernière valeur connue
    assert not f.view(7)[0].stale
    f.received(7, 99, 5)  # CC hors page : ignoré
    assert all(v.cc != 99 for v in f.view(7))


def test_mute_toggle_and_learn() -> None:
    f = make()
    assert f.toggle_mute(3) == (94, 127)
    assert f.toggle_mute(3) == (94, 0)
    f.received(3, 94, 127)  # muté sur la DT2
    assert f.muted[3]
    assert f.toggle_mute(3) == (94, 0)

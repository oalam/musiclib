from __future__ import annotations

from mk_brain.faders import DEFAULT_VALUE, Faders

PAGE = [("CUT", 74), ("RES", 75), ("ENV", 77), ("DEC", 81)] + [("X", 100 + i) for i in range(4)]


def make() -> Faders:
    return Faders([PAGE], mute_cc=94, raw_per_step=4)


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
    assert f.toggle_mute(3) == (94, 0)  # muter
    assert f.toggle_mute(3) == (94, 1)  # rouvrir
    f.received(3, 94, 0)  # muté sur la DT2 (elle envoie 0 = muté, 1 = ouvert)
    assert f.muted[3]
    f.received(3, 94, 1)  # rouvert
    assert not f.muted[3]
    assert f.toggle_mute(3) == (94, 0)


def test_pages_keep_values_and_learn_any_page() -> None:
    p2 = [("BR", 54)] + [("Y", 110 + i) for i in range(7)]
    f = Faders([PAGE, p2], mute_cc=94, raw_per_step=4)
    f.received(3, 54, 90)  # CC de la page 2, appris page 1 affichée
    f.turn(3, 1, 8)  # CUT
    f.page_index = 1
    assert (f.view(3)[0].name, f.view(3)[0].value) == ("BR", 90)
    assert f.turn(3, 1, 4) == (54, 91)
    f.page_index = 0
    assert f.view(3)[0].value == DEFAULT_VALUE + 2

from __future__ import annotations

from mk_brain.loop import Loop, PadOff, PadOn, Param, Setting


def _on(hit: int) -> PadOn:
    return PadOn(hit, 1, "note", 0, 60, 100, 2000)


def test_due_wraps_and_skips_the_lap_of_recording() -> None:
    loop = Loop(1)  # 96 ticks
    g = loop.open("pad T01")
    hit = loop.new_hit(g)
    loop.add(g, 10.0, _on(hit), ahead=True)
    loop.add(g, 20.0, PadOff(hit), ahead=True)
    loop.rebuild()
    assert loop.due(0, 96, True) == []  # tour 0 : la main vient de le jouer
    assert [(at, type(a)) for at, a, _ in loop.due(96, 288, True)] == [
        (106.0, PadOn),
        (116.0, PadOff),
        (202.0, PadOn),
        (212.0, PadOff),
    ]
    assert loop.due(96, 288, False) == []  # l'autre file
    assert [at for at, _, _ in loop.due(106.0, 116.0, True)] == [106.0]  # borne haute exclue


def test_undo_redo_follow_recording_order_and_new_gesture_clears_redo() -> None:
    loop = Loop(1)
    for label, pos in (("a", 50.0), ("b", 10.0), ("c", 30.0)):
        loop.add(loop.open(label), pos, Setting("motif", label))
    undone = [loop.undo(), loop.undo()]
    assert [g.label for g in undone if g is not None] == ["c", "b"]  # pas l'ordre des positions
    redone = loop.redo()
    assert redone is not None and redone.label == "b"
    loop.open("d")
    assert loop.redo() is None
    assert [g.label for g in loop.gestures] == ["a", "b", "d"]
    loop.undo(), loop.undo(), loop.undo()
    assert loop.undo() is None


def test_one_value_per_tick_and_parameter() -> None:
    loop = Loop(1)
    g = loop.open("CUT T10")
    for pos, value in ((10.1, 40), (10.5, 41), (10.9, 42), (11.2, 43)):
        loop.add(g, pos, Param(10, 74, value), key=("cc", 10, 74), dedupe=True, mask=True)
    assert [e.action for e in g.events] == [Param(10, 74, 42), Param(10, 74, 43)]


def test_newer_encoder_gesture_replaces_older_on_its_span_until_undone() -> None:
    loop = Loop(1)
    key = ("cc", 10, 74)
    old = loop.open("CUT T10")
    for pos in (10.0, 30.0, 60.0):
        loop.add(old, pos, Param(10, 74, int(pos)), key=key, dedupe=True, mask=True)
    new = loop.open("CUT T10")  # un tour plus tard, de 20 à 40
    loop.add(new, 96 + 20.0, Param(10, 74, 1), key=key, dedupe=True, mask=True)
    loop.add(new, 96 + 40.0, Param(10, 74, 2), key=key, dedupe=True, mask=True)
    loop.rebuild()
    values = [a.value for _, a, _ in loop.due(192, 288, False) if isinstance(a, Param)]
    assert values == [10, 1, 2, 60]  # le 30 de l'ancien geste est couvert
    loop.undo()
    values = [a.value for _, a, _ in loop.due(192, 288, False) if isinstance(a, Param)]
    assert values == [10, 30, 60]


def test_touched_settings_follow_active_gestures() -> None:
    loop = Loop(2)
    loop.add(loop.open("ARP MOT"), 5.0, Setting("motif", "CINQ"))
    assert loop.touched() == {"motif"}
    loop.undo()
    assert loop.touched() == set()

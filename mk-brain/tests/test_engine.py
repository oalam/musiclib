from __future__ import annotations

from mk_brain.config import Config
from mk_brain.engine import Engine, NoteOff, NoteOn
from mk_brain.hid_mk2 import ButtonEvent, PadEvent

PAD1 = 12  # index HID du pad 1 (constat slice 0)


def test_note_fires_after_window_with_peak(cfg: Config) -> None:
    eng = Engine(cfg)
    assert eng.handle(PadEvent(PAD1, True, 300), 0.0) == []
    assert eng.handle(PadEvent(PAD1, True, 2500), 0.001) == []
    out = eng.tick(0.0025)
    assert out == [NoteOn(15, 0, 127)]
    assert eng.handle(PadEvent(PAD1, True, 2000), 0.003) == []  # tenu : rien de plus
    assert eng.handle(PadEvent(PAD1, False, 0), 0.1) == [NoteOff(15, 0)]


def test_short_hit_fires_on_release(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.handle(PadEvent(PAD1, True, 2500), 0.0)
    assert eng.handle(PadEvent(PAD1, False, 0), 0.0005) == [NoteOn(15, 0, 127), NoteOff(15, 0)]


def test_group_changes_layout_and_note_off_keeps_note(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.handle(ButtonEvent("GROUP_C", True), 0.0)
    eng.handle(PadEvent(PAD1, True, 2500), 0.0)
    assert eng.tick(0.01) == [NoteOn(15, 60, 127)]
    eng.handle(ButtonEvent("GROUP_A", True), 0.02)
    assert eng.handle(PadEvent(PAD1, False, 0), 0.03) == [NoteOff(15, 60)]


def test_leds_lit_pad_and_active_group(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.handle(PadEvent(PAD1, True, 2500), 0.0)
    leds = eng.leds()
    assert leds.pads[PAD1] == cfg.track_colors[1]
    assert leds.pads[0] != cfg.track_colors[13]  # pad 13 au repos, atténué
    assert leds.groups[0] == cfg.families["rythmique"]
    assert not eng.leds_dirty

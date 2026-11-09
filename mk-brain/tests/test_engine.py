from __future__ import annotations

import pytest

from mk_brain.clock import ClockTracker
from mk_brain.config import Config
from mk_brain.engine import NOTE_OFF_MIN_NS, Engine, NoteOff, NoteOn, Timed
from mk_brain.hid_mk2 import BUTTONS, ButtonEvent, EncoderEvent, PadEvent

PAD1 = 12  # index HID du pad 1 (constat slice 0)
MS = 1_000_000
TICK = round(60e9 / (24 * 143))  # 143 BPM : 17 482 517 ns


def running_clock(ticks: int = 30) -> ClockTracker:
    """Horloge lancée : Start à t=0, tick k à k × TICK (le tick 0 suit le Start)."""
    c = ClockTracker()
    c.start(0)
    for k in range(ticks):
        c.tick(k * TICK)
    return c


def press(eng: Engine, t: int, pressure: int = 2500, pad: int = PAD1) -> list[Timed]:
    out = eng.handle(PadEvent(pad, True, pressure), t)
    return out + eng.tick(t + 3 * MS)


def btn(eng: Engine, name: str, pressed: bool = True) -> None:
    assert name in BUTTONS
    eng.handle(ButtonEvent(name, pressed), 0)


# --- slice 1, transport arrêté : immédiat -------------------------------------


def test_note_fires_after_window_with_peak(cfg: Config) -> None:
    eng = Engine(cfg)
    assert eng.handle(PadEvent(PAD1, True, 300), 0) == []
    assert eng.handle(PadEvent(PAD1, True, 2500), 1 * MS) == []
    assert eng.tick(int(2.5 * MS)) == [(int(2.5 * MS), NoteOn(15, 0, 127))]
    assert eng.handle(PadEvent(PAD1, True, 2000), 3 * MS) == []  # tenu : rien de plus
    assert eng.handle(PadEvent(PAD1, False, 0), 100 * MS) == [(100 * MS, NoteOff(15, 0))]


def test_short_hit_fires_on_release(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.handle(PadEvent(PAD1, True, 2500), 0)
    out = eng.handle(PadEvent(PAD1, False, 0), MS // 2)
    assert out == [(MS // 2, NoteOn(15, 0, 127)), (MS // 2 + NOTE_OFF_MIN_NS, NoteOff(15, 0))]


def test_group_changes_layout_and_note_off_keeps_note(cfg: Config) -> None:
    eng = Engine(cfg)
    btn(eng, "GROUP_C")
    assert press(eng, 0) == [(3 * MS, NoteOn(15, 60, 127))]
    btn(eng, "GROUP_A")
    assert eng.handle(PadEvent(PAD1, False, 0), 30 * MS) == [(30 * MS, NoteOff(15, 60))]


def test_leds_lit_pad_and_active_group(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.handle(PadEvent(PAD1, True, 2500), 0)
    leds = eng.leds()
    assert leds.pads[PAD1] == cfg.track_colors[1]
    assert leds.pads[0] != cfg.track_colors[13]  # pad 13 au repos, atténué
    assert leds.groups[0] == cfg.families["rythmique"]
    assert leds.buttons["GRID"] > 0  # quantize 1/16 par défaut
    assert not eng.leds_dirty


# --- slice 3 : quantize, swing, repeat ---------------------------------------


def test_quantize_late_hit_goes_to_next_step(cfg: Config) -> None:
    eng = Engine(cfg, running_clock())
    t = 10 * TICK  # 4 ticks après le pas 6 : au pas 12
    out = press(eng, t)
    assert len(out) == 1
    target, msg = out[0]
    assert msg == NoteOn(15, 0, 127)
    assert target == pytest.approx(12 * TICK, abs=MS // 100)


def test_quantize_early_hit_is_immediate(cfg: Config) -> None:
    eng = Engine(cfg, running_clock())
    t = 7 * TICK  # 1 tick après le pas 6
    assert press(eng, t) == [(t + 3 * MS, NoteOn(15, 0, 127))]


def test_grid_cycles_and_off_is_immediate(cfg: Config) -> None:
    eng = Engine(cfg, running_clock())
    modes = []
    for _ in range(2):
        btn(eng, "GRID")
        modes.append(eng.quantize)
    assert modes == ["1/8", "off"]
    t = 10 * TICK
    assert press(eng, t) == [(t + 3 * MS, NoteOn(15, 0, 127))]


def test_swing_delays_odd_sixteenth(cfg: Config) -> None:
    eng = Engine(cfg, running_clock())
    btn(eng, "SWING")
    eng.handle(EncoderEvent(0, 25, 0), 0)
    eng.handle(EncoderEvent(0, 5, 0), 0)
    assert eng.swing == 75  # borné
    (target, _), *_ = press(eng, 4 * TICK)  # vers le pas 6, 16ᵉ impair
    assert target == pytest.approx(9 * TICK, abs=MS // 100)  # 6 + 3 ticks à 75 %


def test_note_off_never_before_quantized_note_on(cfg: Config) -> None:
    eng = Engine(cfg, running_clock())
    press(eng, 10 * TICK)
    out = eng.handle(PadEvent(PAD1, False, 0), 10 * TICK + 4 * MS)
    assert out[0][0] >= 12 * TICK + NOTE_OFF_MIN_NS - 1


def test_repeat_hits_on_division_grid(cfg: Config) -> None:
    eng = Engine(cfg, running_clock(60))
    btn(eng, "NOTE_REPEAT")
    btn(eng, "DISPLAY_2")  # 1/8
    assert eng.division == "1/8"
    out = press(eng, 13 * TICK)  # 1 tick après le 12 : premier coup au 12 (immédiat)
    ons = [t for t, m in out if isinstance(m, NoteOn)]
    assert ons and ons[0] == 13 * TICK + 3 * MS  # en retard sur 12 : envoyé tout de suite
    later = eng.tick(23 * TICK)
    ons = [t for t, m in later if isinstance(m, NoteOn)]
    assert ons == [pytest.approx(24 * TICK, abs=MS // 100)]
    assert eng.handle(PadEvent(PAD1, False, 0), 25 * TICK) == []  # note offs déjà planifiés
    assert eng.tick(40 * TICK) == []


def test_repeat_lock_with_shift(cfg: Config) -> None:
    eng = Engine(cfg, running_clock())
    btn(eng, "SHIFT")
    btn(eng, "NOTE_REPEAT")
    btn(eng, "NOTE_REPEAT", False)
    assert eng.repeat_active and eng.repeat_locked
    assert "R1/16*" in eng.status()
    btn(eng, "NOTE_REPEAT")
    assert not eng.repeat_locked


def test_repeat_needs_running_transport(cfg: Config) -> None:
    eng = Engine(cfg)
    btn(eng, "NOTE_REPEAT")
    assert press(eng, 0) == [(3 * MS, NoteOn(15, 0, 127))]


# --- slice 4 : compteur de phrases -------------------------------------------


def advance(eng: Engine, start: int, end: int) -> None:
    """Fait avancer l'horloge du moteur de `start` à `end` (exclu) et lit l'état."""
    for k in range(start, end):
        eng.clock.tick(k * TICK)
    eng.tick((end - 1) * TICK)


def test_phrase_leds_follow_transport(cfg: Config) -> None:
    eng = Engine(cfg, running_clock(1))
    eng.on_start()
    advance(eng, 1, 9 * 96 + 1)  # mesure 10, temps 1 : blocs A et B
    st = eng.phrase_state
    assert st is not None and st.bar == 10
    leds = eng.leds()
    assert leds.groups[:3] == [cfg.leds.phrase, cfg.leds.phrase, (0, 0, 0)]
    assert leds.buttons["PLAY"] > 0  # pulse sur le 1
    eng.on_stop()
    eng.clock.stop(0)
    eng.tick(0)
    leds = eng.leds()
    assert leds.groups[0] == cfg.families["rythmique"]  # retour aux dispositions
    assert leds.buttons["PLAY"] == 0


def test_program_change_resets_at_next_bar(cfg: Config) -> None:
    eng = Engine(cfg, running_clock(1))
    eng.on_start()
    advance(eng, 1, 3 * 96 + 86 + 1)  # 10 clocks avant la 5ᵉ mesure
    eng.on_program_change(16 * 4 + 3)
    assert eng.log == ["PC E04 -> mesure 1 à la barre 5"]
    assert eng.phrase_state is not None and eng.phrase_state.bar == 4
    advance(eng, 3 * 96 + 87, 4 * 96 + 1)
    assert eng.phrase_state is not None and eng.phrase_state.bar == 1
    assert eng.phrase.pattern == "E04"


def test_program_change_ignored_when_stopped(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.on_program_change(5)
    assert eng.log == [] and not eng.phrase.pending


def test_shift_play_and_shift_group_recalibrate(cfg: Config) -> None:
    eng = Engine(cfg, running_clock(1))
    eng.on_start()
    advance(eng, 1, 2 * 96 + 41)  # mesure 3
    btn(eng, "SHIFT")
    btn(eng, "GROUP_C")
    assert eng.group == 0  # SHIFT + GROUP ne change pas la disposition
    advance(eng, 2 * 96 + 41, 3 * 96 + 1)
    assert eng.phrase_state is not None and eng.phrase_state.bar == 17
    btn(eng, "PLAY")
    advance(eng, 3 * 96 + 1, 4 * 96 + 1)
    assert eng.phrase_state is not None and eng.phrase_state.bar == 1
    btn(eng, "GROUP_H")  # bloc 8 = mesure 57, au-delà d'une phrase de 32 : ignoré
    assert not eng.phrase.pending

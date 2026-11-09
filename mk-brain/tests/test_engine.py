from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from mk_brain.clock import ClockTracker
from mk_brain.config import Config
from mk_brain.engine import DESIGN_GROUP, NOTE_OFF_MIN_NS, Engine, NoteOff, NoteOn, Timed
from mk_brain.hid_mk2 import BUTTONS, ButtonEvent, EncoderEvent, PadEvent
from mk_brain.layouts import scale
from mk_brain.project import Project
from mk_brain.selection import Entry, Selector
from mk_brain.session import Session

PAD1 = 12  # index HID du pad 1 (constat slice 0)
MS = 1_000_000
SECOND = 1_000_000_000
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


def btn(eng: Engine, name: str, pressed: bool = True, t: int = 0) -> None:
    assert name in BUTTONS
    eng.handle(ButtonEvent(name, pressed), t)


def group(eng: Engine) -> str:
    """Disposition en cours (fonction : mypy ne fige pas la valeur entre deux gestes)."""
    return eng.layout.group


def design(
    cfg: Config, clock: ClockTracker | None = None, project: Project | None = None
) -> Engine:
    """Moteur passé en design par le geste : SHIFT + CONTROL 1 s, appui maître."""
    eng = Engine(cfg, clock, project)
    btn(eng, "SHIFT")
    btn(eng, "CONTROL")
    eng.tick(SECOND)
    btn(eng, "SHIFT", False)
    btn(eng, "CONTROL", False)
    btn(eng, "MASTER_PUSH")
    btn(eng, "MASTER_PUSH", False)
    assert eng.design
    return eng


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


def test_pad_mode_changes_layout_and_note_off_keeps_note(cfg: Config) -> None:
    eng = design(cfg)
    btn(eng, "PAD_MODE")  # B → C
    assert press(eng, 0) == [(3 * MS, NoteOn(15, 60, 127))]
    for _ in range(6):
        btn(eng, "PAD_MODE")  # … → A
    assert eng.handle(PadEvent(PAD1, False, 0), 30 * MS) == [(30 * MS, NoteOff(15, 60))]


def test_leds_lit_pad_and_active_group(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.handle(PadEvent(PAD1, True, 2500), 0)
    leds = eng.leds()
    assert leds.pads[PAD1] == cfg.track_colors[1]
    assert leds.pads[0] != cfg.track_colors[13]  # pad 13 au repos, atténué
    assert leds.groups == [(0, 0, 0)] * 8  # live arrêté : GROUP sans rôle
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
    assert leds.groups == [(0, 0, 0)] * 8  # live arrêté : éteints
    assert leds.buttons["PLAY"] == 0


def test_program_change_resets_at_next_bar(cfg: Config) -> None:
    eng = Engine(cfg, running_clock(1))
    eng.on_start()
    advance(eng, 1, 3 * 96 + 86 + 1)  # 10 clocks avant la 5ᵉ mesure
    eng.on_program_change(16 * 4 + 3)
    assert eng.log == ["banque E (PC reçu)", "PC E04 -> mesure 1 à la barre 5"]
    assert eng.phrase_state is not None and eng.phrase_state.bar == 4
    advance(eng, 3 * 96 + 87, 4 * 96 + 1)
    assert eng.phrase_state is not None and eng.phrase_state.bar == 1
    assert eng.phrase.pattern == "E04"


def test_program_change_ignored_when_stopped(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.on_program_change(5)
    assert eng.log == ["banque A (PC reçu)"] and not eng.phrase.pending  # compteur inchangé


def test_shift_play_and_shift_group_recalibrate(cfg: Config) -> None:
    eng = Engine(cfg, running_clock(1))
    eng.on_start()
    advance(eng, 1, 2 * 96 + 41)  # mesure 3
    btn(eng, "SHIFT")
    btn(eng, "GROUP_C")
    assert eng.group == 1  # SHIFT + GROUP ne change pas la disposition
    advance(eng, 2 * 96 + 41, 3 * 96 + 1)
    assert eng.phrase_state is not None and eng.phrase_state.bar == 17
    btn(eng, "PLAY")
    advance(eng, 3 * 96 + 1, 4 * 96 + 1)
    assert eng.phrase_state is not None and eng.phrase_state.bar == 1
    btn(eng, "GROUP_H")  # bloc 8 = mesure 57, au-delà d'une phrase de 32 : ignoré
    assert not eng.phrase.pending


# --- slice 5.A : SELECT / MUTE / PATTERN + pad, encodeurs ---------------------

PAD7 = 10  # index HID du pad 7 (rangée 2 depuis le bas : index 8-11 = pads 5-8)


def test_select_then_encoder_sends_cc_on_track_channel(cfg: Config) -> None:
    eng = Engine(cfg)
    btn(eng, "SELECT")
    assert eng.handle(PadEvent(PAD7, True, 2500), 0) == []  # pas de note
    assert eng.handle(PadEvent(PAD7, False, 0), MS) == []
    btn(eng, "SELECT", False)
    assert eng.track == 7
    from mk_brain.engine import ControlChange

    assert eng.handle(EncoderEvent(2, 8, 0), 2 * MS) == [(2 * MS, ControlChange(6, 74, 66))]


def test_auto_channel_track_refused(cfg: Config) -> None:
    eng = Engine(cfg)
    btn(eng, "MUTE")
    assert eng.handle(PadEvent(3, True, 2500), 0) == []  # index 3 = pad 16
    eng.handle(PadEvent(3, False, 0), MS)
    btn(eng, "MUTE", False)
    btn(eng, "SELECT")
    eng.handle(PadEvent(3, True, 2500), 2 * MS)
    assert eng.track == 1 and "AUTO CHANNEL" in eng.last_control
    assert eng.leds().pads[3] == (0, 0, 0)


def test_mute_pad_sends_cc94(cfg: Config) -> None:
    from mk_brain.engine import ControlChange

    eng = Engine(cfg)
    btn(eng, "MUTE")
    assert eng.handle(PadEvent(PAD1, True, 2500), 0) == [(0, ControlChange(0, 94, 127))]
    assert eng.leds().pads[PAD1] == (0, 0, 0)  # muté : éteint pendant MUTE


def test_pattern_pad_needs_known_bank(cfg: Config) -> None:
    from mk_brain.engine import ProgramChange

    eng = Engine(cfg)
    btn(eng, "PATTERN")
    assert eng.handle(PadEvent(PAD7, True, 2500), 0) == []
    assert eng.last_control.startswith("bank?")
    btn(eng, "GROUP_B")  # PATTERN tenu : banque B, sans changer de disposition
    assert eng.group == 1 and eng.layout.group == "A" and eng.bank == 1
    assert eng.leds().groups[1] == cfg.families["chromatique"]
    assert eng.handle(PadEvent(PAD1, True, 2500), MS) == [(MS, ProgramChange(9, 16))]  # B01
    eng.handle(PadEvent(PAD1, False, 0), MS)
    eng.handle(PadEvent(PAD7, False, 0), MS)
    eng.on_program_change(16 * 4 + 3)  # E04 reçu, transport arrêté
    assert eng.log == ["banque E (PC reçu)"]
    assert eng.handle(PadEvent(PAD7, True, 2500), 2 * MS) == [
        (2 * MS, ProgramChange(9, 16 * 4 + 6))
    ]  # E07, canal 10


def test_dt2_knob_on_auto_channel_goes_to_selected_track(cfg: Config) -> None:
    from mk_brain.engine import ControlChange

    eng = Engine(cfg)
    eng.track = 7
    eng.on_control_change(15, 74, 74)  # bouton tourné sur la DT2 : arrive sur le canal 16
    eng.on_control_change(15, 94, 1)  # mute sur l'AUTO CHANNEL : track incertaine, ignoré
    assert not eng.faders.muted
    assert eng.handle(EncoderEvent(2, -4, 0), 0) == [(0, ControlChange(6, 74, 73))]  # sans saut


def test_program_change_marks_faders_stale_once(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.on_control_change(0, 74, 30)
    eng.on_program_change(3)
    assert eng.faders.view(1)[1].stale  # CUT, encodeur 2
    eng.handle(EncoderEvent(2, 4, 0), 0)
    eng.on_program_change(3)  # même pattern (PC du Stop) : rien ne change
    assert not eng.faders.view(1)[1].stale


# --- slice 5.B : modes live / design ---------------------------------------------


def test_live_pads_stay_rhythmic(cfg: Config) -> None:
    eng = Engine(cfg)
    btn(eng, "GROUP_C")
    btn(eng, "PAD_MODE")
    assert eng.layout.group == "A"
    assert press(eng, 0) == [(3 * MS, NoteOn(15, 0, 127))]


def test_design_starts_chromatic_with_own_quantize(cfg: Config) -> None:
    eng = design(cfg)
    assert (eng.layout.group, eng.quantize) == ("B", "off")
    btn(eng, "PAD_MODE")
    btn(eng, "GRID")
    assert (eng.layout.group, eng.quantize) == ("C", "1/16")
    eng.modes.mode = "live"
    assert (eng.layout.group, eng.quantize) == ("A", cfg.play.quantize)


def test_mode_switch_refused_in_live_while_running(cfg: Config) -> None:
    eng = Engine(cfg, running_clock(1))
    eng.on_start()
    btn(eng, "SHIFT")
    btn(eng, "CONTROL")
    eng.tick(SECOND)
    btn(eng, "MASTER_PUSH")
    assert not eng.design and eng.last_control.startswith("transport running")


def test_other_button_cancels_proposal(cfg: Config) -> None:
    eng = Engine(cfg)
    btn(eng, "SHIFT")
    btn(eng, "CONTROL")
    eng.tick(SECOND)
    assert eng.modes.pending == "design" and eng.leds().buttons["CONTROL"] > 0
    btn(eng, "GRID")
    btn(eng, "MASTER_PUSH")
    assert not eng.design and eng.last_control == "switch cancelled"


def test_design_encoders_on_auto_channel_with_rec_hint(cfg: Config) -> None:
    from mk_brain.engine import ControlChange

    eng = design(cfg)
    btn(eng, "SELECT")
    eng.handle(PadEvent(3, True, 2500), 0)  # index 3 = pad 16 : joignable en design
    btn(eng, "SELECT", False)
    assert eng.track == 16
    assert eng.handle(EncoderEvent(2, 4, 0), 0) == [(0, ControlChange(15, 74, 65))]
    assert eng.last_control.endswith("DT2 in LIVE REC?")
    eng.handle(EncoderEvent(2, 4, 0), 0)
    assert "LIVE REC" not in eng.last_control  # rappel une fois par passage en design


def test_live_selected_track_pad_stays_lit(cfg: Config) -> None:
    from mk_brain.layouts import scale

    eng = Engine(cfg)
    btn(eng, "SELECT")
    eng.handle(PadEvent(PAD7, True, 2500), 0)
    eng.handle(PadEvent(PAD7, False, 0), MS)
    btn(eng, "SELECT", False)
    pads = eng.leds().pads
    assert pads[PAD7] == scale(cfg.track_colors[7], cfg.leds.selected)
    assert pads[PAD1] == scale(cfg.track_colors[1], cfg.leds.dim)


def test_next_pattern_requested_then_announced(cfg: Config) -> None:
    eng = Engine(cfg, running_clock(1))
    eng.on_start()
    eng.on_program_change(16 * 4 + 3)  # E04 annoncé
    advance(eng, 1, 96 + 1)
    assert (eng.phrase.pattern, eng.next_pattern) == ("E04", None)
    btn(eng, "PATTERN")
    eng.handle(PadEvent(PAD7, True, 2500), 96 * TICK)
    assert eng.next_pattern == "E07"  # demandé, pas encore confirmé
    eng.on_program_change(16 * 4 + 6)
    assert eng.next_pattern == "E07"  # annoncé par la DT2, appliqué à la barre
    advance(eng, 96 + 1, 2 * 96 + 1)
    after: tuple[str | None, str | None] = (eng.phrase.pattern, eng.next_pattern)
    assert after == ("E07", None)


def test_program_change_when_stopped_sets_current_pattern(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.on_program_change(16 + 1)
    assert (eng.phrase.pattern, eng.next_pattern) == ("B02", None)


# --- slice 5.D : design, banques et menu ------------------------------------------


def turn_master(eng: Engine, delta: int) -> None:
    eng.handle(EncoderEvent(0, delta, 0), 0)


def test_design_group_is_bank(cfg: Config, project: Project) -> None:
    eng = design(cfg, project=project)
    assert eng.design_bank == 0  # pas de PC reçu : première banque
    btn(eng, "GROUP_E")
    assert eng.last_control == "E-TRIBE  Bb Phrygian"
    assert eng.layout.group == "D"  # disposition calée sur le mode de la banque
    eng.group = DESIGN_GROUP  # surcharge (PAD MODE, menu GAMME) : chromatique
    assert press(eng, 0) == [(3 * MS, NoteOn(15, 70, 127))]  # chromatique depuis A#
    leds = eng.leds()
    assert leds.groups[4] == cfg.leds.bank  # choisie : blanc plein
    assert leds.groups[0] == scale(cfg.families["gamme"], cfg.leds.dim)  # les autres : mode × dim
    from mk_brain.hid_mk2 import pad_label

    by_pad = {pad_label(i): rgb for i, rgb in enumerate(leds.pads)}
    assert by_pad[3] == (0, 0, 0)  # C : seconde majeure, hors la# phrygien, éteinte au repos
    assert by_pad[2] != (0, 0, 0)  # B : ♭2, dans la gamme
    assert leds.groups[7] == (0, 0, 0)  # pas de banque H
    btn(eng, "GROUP_H")
    assert (eng.design_bank, eng.last_control) == (4, "no bank H")
    assert group(eng) == "B"  # banque absente : la surcharge tient
    btn(eng, "GROUP_G")  # G-JOKER : chromatique sur la# (slice 6.A)
    assert eng.last_control == "G-JOKER  Bb Chroma"
    assert eng.leds().groups[6] == cfg.leds.bank  # choisie : blanc plein
    eng.handle(PadEvent(PAD1, False, 0), 10 * MS)
    assert press(eng, 20 * MS)[0][1] == NoteOn(15, 70, 127)  # chromatique depuis A#


def test_design_without_project(cfg: Config) -> None:
    eng = design(cfg)
    btn(eng, "GROUP_C")
    assert (eng.layout.group, eng.last_control) == ("B", "no project")
    assert eng.leds().groups == [(0, 0, 0)] * 8


def test_design_starts_on_dt2_bank(cfg: Config, project: Project) -> None:
    eng = Engine(cfg, project=project)
    eng.on_program_change(4 * 16 + 2)  # E03
    btn(eng, "SHIFT")
    btn(eng, "CONTROL")
    eng.tick(SECOND)
    btn(eng, "MASTER_PUSH")
    assert eng.design and eng.design_bank == 4


def test_menu_choose_and_validate(cfg: Config, project: Project) -> None:
    eng = design(cfg, project=project)
    btn(eng, "DISPLAY_1")  # GAMME
    assert eng.leds().buttons["DISPLAY_1"] > eng.leds().buttons["DISPLAY_2"]
    assert "DISPLAY_5" not in eng.leds().buttons  # 4 entrées, plus de BANK
    turn_master(eng, 1)  # A-HALF éolien : Aeolian au départ, Phrygian juste après
    assert eng.menu_view()[0] == ("GAMME", "Phrygian", True)
    assert eng.layout.group == "C"  # rien d'appliqué avant l'appui
    btn(eng, "MASTER_PUSH")
    assert (eng.layout.group, eng.menu, eng.last_control) == ("D", None, "Phrygian")
    btn(eng, "DISPLAY_3")  # QUANT : borné à la dernière valeur
    turn_master(eng, 9)
    btn(eng, "MASTER_PUSH")
    assert (eng.quantize, eng.last_control) == ("1/8", "Q 1/8")


def test_menu_same_button_closes_without_applying(cfg: Config, project: Project) -> None:
    eng = design(cfg, project=project)
    btn(eng, "DISPLAY_2")  # TRACK
    turn_master(eng, 4)
    btn(eng, "DISPLAY_2")
    btn(eng, "MASTER_PUSH")
    assert (eng.menu, eng.track) == (None, 1)
    btn(eng, "DISPLAY_7")  # pas d'entrée : rien d'ouvert
    assert eng.menu is None


def test_menu_phrase_design_only(cfg: Config, project: Project) -> None:
    eng = design(cfg, project=project)
    btn(eng, "DISPLAY_4")  # PHRASE
    turn_master(eng, 1)
    btn(eng, "MASTER_PUSH")
    assert eng.phrase.length == 64
    btn(eng, "GROUP_C")  # nouvelle banque : sa phrase
    assert eng.phrase.length == project.defaults.phrase
    btn(eng, "DISPLAY_4")  # PHRASE
    turn_master(eng, 1)
    btn(eng, "MASTER_PUSH")
    btn(eng, "SHIFT")
    btn(eng, "CONTROL")
    eng.tick(3 * SECOND)
    btn(eng, "MASTER_PUSH")  # retour en live : la phrase de la config
    assert not eng.design and eng.phrase.length == cfg.play.phrase


def test_hit_kept_with_note_for_screen(cfg: Config, project: Project) -> None:
    eng = design(cfg, project=project)
    btn(eng, "GROUP_E")
    press(eng, 0, pressure=2500)
    assert eng.last_hit is not None and eng.last_hit[1:3] == (70, 127)


def test_arrows_switch_encoder_page_and_pitch_bend(cfg: Config) -> None:
    from mk_brain.engine import ControlChange, PitchBend

    eng = Engine(cfg)
    btn(eng, "BROWSE_RIGHT")  # page 2 : LVL MW BC PB BR CHO TUNE PAN
    assert eng.handle(EncoderEvent(4, 8, 0), 0) == []  # PB sans SHIFT : rien
    assert eng.last_control == "PB: hold SHIFT"
    btn(eng, "SHIFT")
    assert eng.handle(EncoderEvent(4, 8, 0), 0) == [(0, PitchBend(0, 256))]  # PB : 64 → 66
    assert eng.faders.view(1)[3].value == 66
    assert eng.handle(ButtonEvent("SHIFT", False), MS) == [(MS, PitchBend(0, 0))]  # au centre
    assert eng.faders.view(1)[3].value == 64
    assert eng.handle(ButtonEvent("SHIFT", False), MS) == []  # une seule remise
    btn(eng, "SHIFT")
    eng.handle(EncoderEvent(4, 8, 0), 0)
    btn(eng, "SHIFT", False)
    assert eng.faders.view(1)[3].value == 64  # PB revenu au centre
    assert eng.handle(EncoderEvent(5, 4, 0), 0) == [(0, ControlChange(0, 54, 65))]  # BR
    btn(eng, "BROWSE_LEFT")
    assert eng.last_control == "page 1/3" and eng.leds().buttons["BROWSE_RIGHT"] > 0
    assert eng.handle(EncoderEvent(2, 4, 0), 0) == [(0, ControlChange(0, 74, 65))]  # CUT


def test_pattern_has_no_effect_in_design(cfg: Config, project: Project) -> None:
    eng = design(cfg, project=project)
    btn(eng, "PATTERN")
    assert press(eng, 0) == [(3 * MS, NoteOn(15, 65, 127))]  # la note joue (A-HALF, fa)
    btn(eng, "GROUP_E")  # GROUP choisit la banque, comme sans PATTERN
    assert eng.design_bank == 4 and eng.bank is None
    assert eng.leds().buttons["PATTERN"] == 0


def test_transport_arrows_shift_octave_in_design(cfg: Config, project: Project) -> None:
    eng = design(cfg, project=project)
    btn(eng, "GROUP_E")  # la#
    eng.group = DESIGN_GROUP  # chromatique depuis A#5 (70)
    btn(eng, "TRANSPORT_RIGHT")
    assert (eng.octave, eng.last_control) == (1, "octave +1")
    assert press(eng, 0) == [(3 * MS, NoteOn(15, 82, 127))]
    buttons = eng.leds().buttons
    assert buttons["TRANSPORT_RIGHT"] > buttons["TRANSPORT_LEFT"] > 0
    btn(eng, "TRANSPORT_RIGHT")  # 70 + 24 + 15 = 109 : passe
    btn(eng, "TRANSPORT_RIGHT")  # 70 + 36 + 15 = 121 : passe
    btn(eng, "TRANSPORT_RIGHT")  # 70 + 48 + 15 = 133 > 127 : refusé
    assert (eng.octave, eng.last_control) == (3, "octave limit +3")
    btn(eng, "GROUP_A")  # fa : 65 + 48 + 15 = 128 > 127, mais vers le bas ±4
    for _ in range(5):
        btn(eng, "TRANSPORT_LEFT")
    assert (eng.octave, eng.last_control) == (-4, "octave limit -4")
    btn(eng, "GROUP_C")  # nouvelle banque : retour sur sa tonique
    assert eng.octave == 0


def test_octave_bounded_by_midi_range(cfg: Config) -> None:
    from mk_brain.layouts import fits, shift_octave

    lay = cfg.layouts[1]  # chromatique depuis la base de la config
    assert fits(lay) and not fits(shift_octave(lay, 6)) and not fits(shift_octave(lay, -6))


def test_transport_arrows_ignored_in_live(cfg: Config) -> None:
    eng = Engine(cfg)
    btn(eng, "TRANSPORT_LEFT")
    assert eng.octave == 0
    assert eng.leds().buttons.get("TRANSPORT_LEFT", 0) == 0


# --- slice 6.B : contexte live suivi par Program Change -----------------------


def test_live_program_change_sets_bank_context_and_phrase_at_bar(
    cfg: Config, project: Project
) -> None:
    long_bank = project.model_copy(deep=True)
    long_bank.banks["E-TRIBE"].phrase = 64
    eng = Engine(cfg, running_clock(1), long_bank)
    eng.on_start()
    advance(eng, 1, 3 * 96 + 86 + 1)
    eng.on_program_change(16 * 4 + 3)  # E04
    assert eng.context is not None and eng.context[0] == "E-TRIBE"
    assert eng.phrase.length == 32  # pas avant la barre
    assert eng.announce is not None and eng.announce[2] is None
    eng.tick(5 * MS)
    assert eng.announce[2] == 5 * MS  # instant posé au tick
    advance(eng, 3 * 96 + 87, 4 * 96 + 1)
    assert eng.phrase.length == 64 and eng.phrase_state is not None
    assert eng.phrase_state.bar == 1


def test_live_program_change_stopped_applies_phrase_now(cfg: Config, project: Project) -> None:
    long_bank = project.model_copy(deep=True)
    long_bank.banks["C-GROOVE"].phrase = 64
    eng = Engine(cfg, project=long_bank)
    eng.on_program_change(2 * 16)  # C01
    assert eng.phrase.length == 64
    eng.on_program_change(7 * 16)  # H01 : banque absente du projet, phrase de la config
    assert eng.context is None and eng.phrase.length == cfg.play.phrase


def test_announce_only_on_bank_change(cfg: Config, project: Project) -> None:
    eng = Engine(cfg, project=project)
    eng.on_program_change(4 * 16 + 2)  # E03
    eng.announce = None
    eng.on_program_change(4 * 16 + 3)  # E04 : même banque
    assert eng.announce is None
    eng.on_program_change(5 * 16)  # F01
    assert eng.announce is not None and eng.announce[0] == "F-MENTAL"


def test_design_follows_dt2_bank_change(cfg: Config, project: Project) -> None:
    eng = design(cfg, project=project)
    eng.on_program_change(4 * 16)  # E01 reçu en design : banque E, comme GROUP E
    assert eng.context is not None and eng.context[0] == "E-TRIBE"
    assert eng.announce is None  # la fiche est déjà à l'écran en design
    btn(eng, "GROUP_A")  # choix à la main
    eng.on_program_change(4 * 16 + 1)  # E02 : même banque, le choix tient
    assert eng.context is not None and eng.context[0] == "A-HALF"
    eng.on_program_change(7 * 16)  # H01 : banque absente du projet, rien ne change
    assert eng.context is not None and eng.context[0] == "A-HALF"


# --- slice 6.C : sélection de projet --------------------------------------------


def _catalog(project: Project) -> Callable[[], Selector]:
    path = Path("solaris.yaml")
    entries = [
        Entry("broken", path, "2026-11-09", None, "illisible"),
        Entry("solaris", path, "2026-11-09", project),
    ]
    return lambda: Selector(entries, "solaris")


def test_selection_loads_preselected_project(cfg: Config, project: Project) -> None:
    eng = Engine(cfg, catalog=_catalog(project))
    eng.on_program_change(4 * 16)  # E01 reçu avant le chargement
    eng.open_selection()
    assert eng.selector is not None and eng.selector.index == 1
    btn(eng, "MASTER_PUSH")
    assert eng.selector is None and eng.project is project and eng.loaded == "solaris"
    assert eng.context is not None and eng.context[0] == "E-TRIBE"  # contexte repris du PC


def test_selection_scroll_and_invalid_refused(cfg: Config, project: Project) -> None:
    eng = Engine(cfg, catalog=_catalog(project))
    btn(eng, "SHIFT")
    btn(eng, "BROWSE_LEFT")
    assert eng.selector is not None
    btn(eng, "SHIFT", False)
    eng.handle(EncoderEvent(0, -1, 0), 0)
    btn(eng, "MASTER_PUSH")
    assert eng.selector is not None and eng.project is None  # « broken » ne se charge pas
    btn(eng, "SHIFT")
    btn(eng, "BROWSE_RIGHT")  # referme sans charger
    assert eng.selector is None and eng.faders.page_index == 0


def test_selection_refused_in_live_while_running(cfg: Config, project: Project) -> None:
    eng = Engine(cfg, running_clock(), project, _catalog(project))
    eng.on_start()
    eng.open_selection()
    assert eng.selector is None
    d = design(cfg, project=project)  # bascule faite à l'arrêt, puis Start
    d.clock, d.catalog = running_clock(), _catalog(project)
    d.open_selection()  # design : permise transport lancé
    assert d.selector is not None


def test_start_in_live_closes_selection(cfg: Config, project: Project) -> None:
    eng = Engine(cfg, catalog=_catalog(project))
    eng.open_selection()
    eng.clock = running_clock()
    eng.tick(0)
    assert eng.selector is None


def test_start_mode_from_config(cfg: Config, project: Project) -> None:
    start = cfg.model_copy(update={"play": cfg.play.model_copy(update={"mode": "design"})})
    eng = Engine(start, project=project)
    assert eng.design and eng.quantize == "off"
    assert eng.sheet is not None and eng.sheet[0] == "A-HALF"  # première banque du projet
    assert Engine(start).design  # sans projet aussi


# --- session : derniers réglages ---------------------------------------------------


def test_snapshot_restore_round_trip(cfg: Config, project: Project) -> None:
    eng = design(cfg, project=project)
    btn(eng, "GROUP_E")
    btn(eng, "TRANSPORT_RIGHT")  # octave +1
    btn(eng, "SELECT")
    eng.handle(PadEvent(PAD1 - 2, True, 2500), 0)  # pad 3
    btn(eng, "SELECT", False)
    eng.handle(EncoderEvent(5, 40, 0), 0)  # CUT de T03
    eng.on_program_change(4 * 16 + 3)  # E04
    eng.faders.muted[7] = True
    snap = eng.snapshot()

    fresh = Engine(cfg, project=project)
    fresh.restore(snap)
    assert fresh.snapshot() == snap
    assert fresh.phrase.pattern == "E04" and fresh.track == snap.track
    view = fresh.faders.view(snap.track)[4]
    assert view.stale and view.value == snap.faders[0].value  # hors prise : DT2 à confirmer


def test_restore_keeps_program_already_received(cfg: Config, project: Project) -> None:
    eng = Engine(cfg, project=project)
    eng.on_program_change(2 * 16)  # C01 reçu de la DT2
    eng.restore(Session(program=4 * 16 + 3, design_bank=7, group=9 % 8))
    assert eng.last_program == 2 * 16  # la DT2 l'emporte
    assert eng.design_bank is None  # banque H absente du projet : ignorée


def test_design_layout_follows_bank_mode_until_pad_mode(cfg: Config, project: Project) -> None:
    eng = design(cfg, project=project)
    assert group(eng) == "C"  # A-HALF éolien
    btn(eng, "GROUP_E")
    assert group(eng) == "D"  # E-TRIBE phrygien
    btn(eng, "PAD_MODE")  # surcharge
    assert group(eng) == "E"
    eng.on_program_change(4 * 16 + 1)  # même banque : la surcharge tient
    assert group(eng) == "E"
    eng.on_program_change(6 * 16)  # G-JOKER : chromatique
    assert group(eng) == "B"


def test_arrows_cycle_both_ways_and_levels_page_is_display_only(cfg: Config) -> None:
    eng = Engine(cfg)
    assert eng.faders.n_pages == 3
    btn(eng, "BROWSE_LEFT")  # de la page 1 vers la dernière, en boucle
    assert eng.faders.levels and eng.last_control == "page 3/3  levels"
    eng.on_control_change(2, 95, 100)  # LVL de T03 joué sur la DT2
    assert eng.handle(EncoderEvent(1, 8, 0), 0) == []  # affichage seul
    assert eng.last_control == "levels: display only"
    lv = eng.faders.levels_view()
    assert (lv[2].value, lv[2].known) == (100, True) and not lv[3].known
    btn(eng, "BROWSE_RIGHT")  # de la dernière vers la page 1
    assert eng.faders.page_index == 0

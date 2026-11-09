from __future__ import annotations

import pytest

from mk_brain.clock import ClockTracker
from mk_brain.config import Config
from mk_brain.engine import NOTE_OFF_MIN_NS, Engine, NoteOff, NoteOn, Timed
from mk_brain.hid_mk2 import BUTTONS, ButtonEvent, EncoderEvent, PadEvent
from mk_brain.project import Project

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

    assert eng.handle(EncoderEvent(1, 8, 0), 2 * MS) == [(2 * MS, ControlChange(6, 74, 66))]


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
    assert eng.last_control.startswith("banque ?")
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
    eng.on_control_change(15, 94, 127)  # mute sur l'AUTO CHANNEL : track incertaine, ignoré
    assert not eng.faders.muted
    assert eng.handle(EncoderEvent(1, -4, 0), 0) == [(0, ControlChange(6, 74, 73))]  # sans saut


def test_program_change_marks_faders_stale_once(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.on_control_change(0, 74, 30)
    eng.on_program_change(3)
    assert eng.faders.view(1)[0].stale
    eng.handle(EncoderEvent(1, 4, 0), 0)
    eng.on_program_change(3)  # même pattern (PC du Stop) : rien ne change
    assert not eng.faders.view(1)[0].stale


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
    assert not eng.design and eng.last_control.startswith("transport lancé")


def test_other_button_cancels_proposal(cfg: Config) -> None:
    eng = Engine(cfg)
    btn(eng, "SHIFT")
    btn(eng, "CONTROL")
    eng.tick(SECOND)
    assert eng.modes.pending == "design" and eng.leds().buttons["CONTROL"] > 0
    btn(eng, "GRID")
    btn(eng, "MASTER_PUSH")
    assert not eng.design and eng.last_control == "bascule annulée"


def test_design_encoders_on_auto_channel_with_rec_hint(cfg: Config) -> None:
    from mk_brain.engine import ControlChange

    eng = design(cfg)
    btn(eng, "SELECT")
    eng.handle(PadEvent(3, True, 2500), 0)  # index 3 = pad 16 : joignable en design
    btn(eng, "SELECT", False)
    assert eng.track == 16
    assert eng.handle(EncoderEvent(1, 4, 0), 0) == [(0, ControlChange(15, 74, 65))]
    assert eng.last_control.endswith("DT2 en LIVE REC ?")
    eng.handle(EncoderEvent(1, 4, 0), 0)
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
    assert eng.last_control == "E-TRIBE  A# phrygien"
    assert press(eng, 0) == [(3 * MS, NoteOn(15, 70, 127))]  # chromatique depuis A#
    leds = eng.leds()
    assert leds.groups[4] == cfg.families["gamme"]
    from mk_brain.hid_mk2 import pad_label

    by_pad = {pad_label(i): rgb for i, rgb in enumerate(leds.pads)}
    assert by_pad[3] == (0, 0, 0)  # C : seconde majeure, hors la# phrygien, éteinte au repos
    assert by_pad[2] != (0, 0, 0)  # B : ♭2, dans la gamme
    assert leds.groups[7] == (0, 0, 0)  # pas de banque H
    btn(eng, "GROUP_H")
    assert (eng.design_bank, eng.last_control) == (4, "pas de banque H")
    assert eng.layout.group == "B"  # GROUP ne change plus la disposition


def test_design_without_project(cfg: Config) -> None:
    eng = design(cfg)
    btn(eng, "GROUP_C")
    assert (eng.layout.group, eng.last_control) == ("B", "pas de projet")
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
    btn(eng, "DISPLAY_2")  # GAMME
    assert eng.leds().buttons["DISPLAY_2"] > eng.leds().buttons["DISPLAY_1"]
    turn_master(eng, 2)
    assert eng.menu_view()[1] == ("GAMME", "Phrygien", True)
    assert eng.layout.group == "B"  # rien d'appliqué avant l'appui
    btn(eng, "MASTER_PUSH")
    assert (eng.layout.group, eng.menu, eng.last_control) == ("D", None, "GAMME Phrygien")
    btn(eng, "DISPLAY_1")  # BANK : A → B, borné aux banques du projet
    turn_master(eng, 9)
    btn(eng, "MASTER_PUSH")
    assert eng.design_bank == 5 and eng.sheet is not None and eng.sheet[0] == "F-MENTAL"


def test_menu_same_button_closes_without_applying(cfg: Config, project: Project) -> None:
    eng = design(cfg, project=project)
    btn(eng, "DISPLAY_3")  # TRACK
    turn_master(eng, 4)
    btn(eng, "DISPLAY_3")
    btn(eng, "MASTER_PUSH")
    assert (eng.menu, eng.track) == (None, 1)
    btn(eng, "DISPLAY_7")  # pas d'entrée : rien d'ouvert
    assert eng.menu is None


def test_menu_phrase_design_only(cfg: Config, project: Project) -> None:
    eng = design(cfg, project=project)
    btn(eng, "DISPLAY_5")
    turn_master(eng, 1)
    btn(eng, "MASTER_PUSH")
    assert eng.phrase.length == 64
    btn(eng, "GROUP_C")  # nouvelle banque : sa phrase
    assert eng.phrase.length == project.defaults.phrase
    btn(eng, "DISPLAY_5")
    turn_master(eng, 1)
    btn(eng, "MASTER_PUSH")
    btn(eng, "SHIFT")
    btn(eng, "CONTROL")
    eng.tick(3 * SECOND)
    btn(eng, "MASTER_PUSH")  # retour en live : la phrase de la config
    assert not eng.design and eng.phrase.length == cfg.play.phrase

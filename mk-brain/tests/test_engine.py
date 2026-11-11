from __future__ import annotations

import random
from collections.abc import Callable, Iterable
from pathlib import Path

import pytest

from mk_brain.clock import ClockTracker
from mk_brain.config import Config
from mk_brain.engine import (
    KEYBOARD_GROUP,
    NOTE_OFF_MIN_NS,
    Engine,
    NoteOff,
    NoteOn,
    Timed,
)
from mk_brain.hid_mk2 import BUTTONS, LED_MAX, ButtonEvent, EncoderEvent, PadEvent, pad_label
from mk_brain.layouts import scale
from mk_brain.project import Project
from mk_brain.quantize import QUANTIZE_CYCLE
from mk_brain.selection import Entry, Selector
from mk_brain.session import Session

PAD1 = 12  # index HID du pad 1 (constat slice 0)
MS = 1_000_000
SECOND = 1_000_000_000
TICK = round(60e9 / (24 * 143))  # 143 BPM : 17 482 517 ns
CC_STEP = 15  # `encoders.raw_per_step` : unités brutes de la MK2 par cran de CC


def running_clock(ticks: int = 30) -> ClockTracker:
    """Horloge lancée : Start à t=0, tick k à k × TICK (le tick 0 suit le Start)."""
    c = ClockTracker()
    c.start(0)
    for k in range(ticks):
        c.tick(k * TICK)
    return c


def press(eng: Engine, t: int, pressure: int = 3000, pad: int = PAD1) -> list[Timed]:
    out = eng.handle(PadEvent(pad, True, pressure), t)
    return out + eng.tick(t + 3 * MS)


def btn(eng: Engine, name: str, pressed: bool = True, t: int = 0) -> None:
    assert name in BUTTONS
    eng.handle(ButtonEvent(name, pressed), t)


def group(eng: Engine) -> str | None:
    """Disposition en cours (fonction : mypy ne fige pas la valeur entre deux gestes)."""
    return eng.layout.group


def design(
    cfg: Config, clock: ClockTracker | None = None, project: Project | None = None
) -> Engine:
    """Moteur aux pads en clavier (PAD MODE) ; le nom rappelle l'ancien mode design."""
    eng = Engine(cfg, clock, project)
    btn(eng, "PAD_MODE")
    btn(eng, "PAD_MODE", False)
    assert eng.keyboard
    return eng


# --- slice 1, transport arrêté : immédiat -------------------------------------


def test_note_fires_after_window_with_peak(cfg: Config) -> None:
    eng = Engine(cfg)
    assert eng.handle(PadEvent(PAD1, True, 300), 0) == []
    assert eng.handle(PadEvent(PAD1, True, 3000), 1 * MS) == []
    assert eng.tick(int(2.5 * MS)) == [(int(2.5 * MS), NoteOn(0, 60, 127))]
    assert eng.handle(PadEvent(PAD1, True, 2000), 3 * MS) == []  # tenu : rien de plus
    assert eng.handle(PadEvent(PAD1, False, 0), 100 * MS) == [(100 * MS, NoteOff(0, 60))]


def test_short_hit_fires_on_release(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.handle(PadEvent(PAD1, True, 3000), 0)
    out = eng.handle(PadEvent(PAD1, False, 0), MS // 2)
    assert out == [(MS // 2, NoteOn(0, 60, 127)), (MS // 2 + NOTE_OFF_MIN_NS, NoteOff(0, 60))]


def test_pad_mode_toggles_mpc_keyboard_and_note_off_keeps_target(cfg: Config) -> None:
    eng = Engine(cfg)
    assert eng.mpc
    assert press(eng, 0) == [(3 * MS, NoteOn(0, 60, 127))]  # pad 1 = BD : T1, tranche 60
    btn(eng, "PAD_MODE")  # clavier pendant que le pad est tenu
    assert eng.keyboard and eng.leds().buttons["PAD_MODE"] == LED_MAX
    assert eng.handle(PadEvent(PAD1, False, 0), 30 * MS) == [(30 * MS, NoteOff(0, 60))]
    eng.track = 9
    assert press(eng, 40 * MS) == [(43 * MS, NoteOn(8, 60, 127))]  # chromatique C5 sur T9
    assert eng.last_control == "Chroma"  # le mode est à l'écran : seule la gamme en message
    eng.last_control = ""
    btn(eng, "PAD_MODE")
    assert eng.mpc and eng.last_control == ""  # pas de « MPC » en double


def test_leds_lit_pad_and_active_group(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.handle(PadEvent(PAD1, True, 3000), 0)
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
    assert msg == NoteOn(0, 60, 127)
    assert target == pytest.approx(12 * TICK, abs=MS // 100)


def test_quantize_early_hit_is_immediate(cfg: Config) -> None:
    eng = Engine(cfg, running_clock())
    t = 7 * TICK  # 1 tick après le pas 6
    assert press(eng, t) == [(t + 3 * MS, NoteOn(0, 60, 127))]


def test_grid_cycles_and_off_is_immediate(cfg: Config) -> None:
    eng = Engine(cfg, running_clock())
    modes = []
    for _ in range(2):
        btn(eng, "GRID")
        modes.append(eng.quantize)
    assert modes == ["1/8", "off"]
    t = 10 * TICK
    assert press(eng, t) == [(t + 3 * MS, NoteOn(0, 60, 127))]


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
    assert press(eng, 0) == [(3 * MS, NoteOn(0, 60, 127))]


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
    assert leds.buttons["PLAY"] > 0  # première moitié du temps : allumé
    advance(eng, 9 * 96 + 1, 9 * 96 + 13)  # seconde moitié du temps 1
    leds = eng.leds()
    assert leds.groups[:3] == [cfg.leds.phrase, (0, 0, 0), (0, 0, 0)]  # bloc en cours clignote
    assert leds.buttons["PLAY"] == 0  # PLAY clignote au tempo
    advance(eng, 9 * 96 + 13, 15 * 96 + 1)  # mesure 16 : dernière avant le cap
    st = eng.phrase_state
    assert st is not None and st.bar == 16 and st.blinking
    assert eng.leds().groups[:2] == [cfg.leds.phrase, cfg.leds.phrase_warn]  # orange
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
    assert eng.group == KEYBOARD_GROUP and eng.bank is None  # SHIFT + GROUP : recalage seul
    advance(eng, 2 * 96 + 41, 3 * 96 + 1)
    assert eng.phrase_state is not None and eng.phrase_state.bar == 17
    btn(eng, "PLAY")
    advance(eng, 3 * 96 + 1, 4 * 96 + 1)
    assert eng.phrase_state is not None and eng.phrase_state.bar == 1
    btn(eng, "GROUP_H")  # bloc 8 = mesure 57, au-delà d'une phrase de 32 : ignoré
    assert not eng.phrase.pending


# --- slice 5.A : SELECT / MUTE + pad, encodeurs ---------------------------------

PAD7 = 10  # index HID du pad 7 (rangée 2 depuis le bas : index 8-11 = pads 5-8)


def test_select_then_encoder_sends_cc_on_track_channel(cfg: Config) -> None:
    eng = Engine(cfg)
    btn(eng, "SELECT")
    assert eng.handle(PadEvent(PAD7, True, 2500), 0) == []  # pas de note
    assert eng.handle(PadEvent(PAD7, False, 0), MS) == []
    btn(eng, "SELECT", False)
    assert eng.track == 7
    from mk_brain.engine import ControlChange

    assert eng.handle(EncoderEvent(2, 2 * CC_STEP, 0), 2 * MS) == [
        (2 * MS, ControlChange(6, 54, 66))
    ]


def test_pad16_mute_refused_select_targets_active_track(cfg: Config) -> None:
    from mk_brain.engine import ControlChange

    eng = Engine(cfg)
    btn(eng, "MUTE")
    assert eng.handle(PadEvent(3, True, 2500), 0) == []  # index 3 = pad 16 : pas de mute
    assert eng.leds().pads[3] == (0, 0, 0)
    eng.handle(PadEvent(3, False, 0), MS)
    btn(eng, "MUTE", False)
    btn(eng, "SELECT")
    eng.handle(PadEvent(3, True, 2500), 300 * MS)  # au-delà de l'anti-rebond
    eng.handle(PadEvent(3, False, 0), 310 * MS)
    btn(eng, "SELECT", False)
    assert eng.track == 16 and eng.last_control == "T16 selected (DT2 active)"
    assert eng.handle(EncoderEvent(2, CC_STEP, 0), 0) == [(0, ControlChange(15, 54, 65))]


def test_mute_pad_sends_cc94(cfg: Config) -> None:
    from mk_brain.engine import ControlChange

    eng = Engine(cfg)
    btn(eng, "MUTE")
    assert eng.handle(PadEvent(PAD1, True, 2500), 0) == [(0, ControlChange(0, 94, 127))]
    assert eng.leds().pads[PAD1] == (0, 0, 0)  # muté : éteint pendant MUTE


def test_dt2_knob_on_auto_channel_goes_to_selected_track(cfg: Config) -> None:
    from mk_brain.engine import ControlChange

    midi = cfg.midi.model_copy(update={"knobs_on_track_channel": False})  # DT2 OUTPUT CH = AUTO
    eng = Engine(cfg.model_copy(update={"midi": midi}))
    eng.track = 7
    eng.on_control_change(15, 54, 74)  # bouton tourné sur la DT2 : arrive sur le canal 16
    eng.on_control_change(15, 94, 1)  # mute sur l'AUTO CHANNEL : track incertaine, ignoré
    assert not eng.faders.muted
    assert eng.handle(EncoderEvent(2, -CC_STEP, 0), 0) == [
        (0, ControlChange(6, 54, 73))
    ]  # sans saut


def test_program_change_marks_faders_stale_once(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.on_control_change(0, 54, 30)
    eng.on_program_change(3)
    assert eng.faders.view(1)[1].stale  # BR, encodeur 2
    eng.handle(EncoderEvent(2, CC_STEP, 0), 0)
    eng.on_program_change(3)  # même pattern (PC du Stop) : rien ne change
    assert not eng.faders.view(1)[1].stale


# --- slice 8 : MPC, mode unique ------------------------------------------------


def test_mpc_pads_play_slices_on_track_channels(cfg: Config) -> None:
    idx = {pad_label(i): i for i in range(16)}
    eng = Engine(cfg)
    assert press(eng, 0, pad=idx[12]) == [(3 * MS, NoteOn(4, 62, 127))]  # OH : T5, tranche 62
    leds = eng.leds()
    assert leds.pads[idx[12]] == cfg.mpc_pad(12).color  # frappé : plein
    assert leds.pads[idx[13]] == scale(cfg.mpc_pad(13).color, cfg.leds.dim)  # CR au repos
    btn(eng, "GROUP_C")  # banque choisie, les pads restent en MPC
    assert eng.mpc and eng.bank == 2


def test_one_quantize_for_both_layouts(cfg: Config) -> None:
    eng = Engine(cfg)
    assert eng.quantize == cfg.play.quantize
    btn(eng, "GRID")
    q = eng.quantize
    btn(eng, "PAD_MODE")
    assert eng.quantize == q and eng.layout.group == "B"  # clavier sans banque : chromatique


def test_control_no_longer_switches_mode(cfg: Config) -> None:
    eng = Engine(cfg)
    btn(eng, "SHIFT")
    btn(eng, "CONTROL")
    eng.tick(SECOND)
    btn(eng, "MASTER_PUSH")
    assert eng.mpc and "CONTROL" not in eng.leds().buttons


def test_modifier_held_shows_track_grid(cfg: Config) -> None:
    eng = Engine(cfg)
    btn(eng, "SELECT")
    eng.handle(PadEvent(PAD7, True, 2500), 0)
    eng.handle(PadEvent(PAD7, False, 0), MS)
    pads = eng.leds().pads
    assert pads[PAD7] == cfg.track_colors[7]  # pad n = track n pendant SELECT
    assert pads[PAD1] == (0, 0, 0)  # les autres éteints, comme sous MUTE
    btn(eng, "SELECT", False)
    assert eng.leds().pads[PAD7] == scale(cfg.mpc_pad(7).color, cfg.leds.dim)  # SD2 au repos


def test_program_change_when_stopped_sets_current_pattern(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.on_program_change(16 + 1)
    assert (eng.phrase.pattern, eng.next_pattern) == ("B02", None)


# --- slice 5.D : design, banques et menu ------------------------------------------


def turn_master(eng: Engine, delta: int) -> None:
    eng.handle(EncoderEvent(0, delta, 0), 0)


def test_design_group_is_bank(cfg: Config, project: Project) -> None:
    eng = design(cfg, project=project)
    assert eng.bank is None  # ni PC reçu ni GROUP
    btn(eng, "GROUP_E")
    assert eng.last_control == "E-TRIBE  Bb Phrygian"
    assert eng.layout.group == "D"  # disposition calée sur le mode de la banque
    eng.group = KEYBOARD_GROUP  # surcharge (PAD MODE, menu GAMME) : chromatique
    assert press(eng, 0) == [(3 * MS, NoteOn(0, 70, 127))]  # chromatique depuis A#
    leds = eng.leds()
    assert leds.groups[4] == cfg.leds.bank  # choisie : blanc plein
    assert leds.groups[0] == (0, 0, 0)  # les autres éteintes (slice 9)
    from mk_brain.hid_mk2 import pad_label

    by_pad = {pad_label(i): rgb for i, rgb in enumerate(leds.pads)}
    assert by_pad[3] == (0, 0, 0)  # C : seconde majeure, hors la# phrygien, éteinte au repos
    assert by_pad[2] != (0, 0, 0)  # B : ♭2, dans la gamme
    assert leds.groups[7] == (0, 0, 0)  # pas de banque H
    btn(eng, "GROUP_H")
    assert (eng.snapshot().bank, eng.last_control) == (7, "bank H (not in project)")
    assert group(eng) == "B"  # banque absente : la surcharge tient
    btn(eng, "GROUP_G")  # G-JOKER : chromatique sur la# (slice 6.A)
    assert eng.last_control == "G-JOKER  Bb Chroma"
    assert eng.leds().groups[6] == cfg.leds.bank  # choisie : blanc plein
    eng.handle(PadEvent(PAD1, False, 0), 10 * MS)
    assert press(eng, 20 * MS)[0][1] == NoteOn(0, 70, 127)  # chromatique depuis A#


def test_design_without_project(cfg: Config) -> None:
    eng = design(cfg)
    btn(eng, "GROUP_C")
    assert (eng.layout.group, eng.last_control, eng.bank) == ("B", "bank C", 2)
    assert eng.leds().groups[2] == cfg.leds.bank


def test_program_change_sets_current_bank(cfg: Config, project: Project) -> None:
    eng = Engine(cfg, project=project)
    eng.on_program_change(4 * 16 + 2)  # E03
    assert eng.bank == 4 and eng.layout.group == "D"  # clavier calé sur E-TRIBE phrygien


def test_menu_master_applies_on_turn(cfg: Config, project: Project) -> None:
    eng = design(cfg, project=project)
    btn(eng, "GROUP_A")
    assert eng.menu == 0  # focus sur GAMME au départ
    assert eng.leds().buttons["DISPLAY_1"] > eng.leds().buttons["DISPLAY_2"]
    assert "DISPLAY_5" not in eng.leds().buttons  # 4 entrées, plus de BANK
    turn_master(eng, 1)  # A-HALF éolien : Aeolian au départ, Phrygian juste après
    assert eng.menu_view()[0] == ("GAMME", "Phrygian", True)
    assert (eng.layout.group, eng.last_control) == ("D", "Phrygian")  # appliqué au cran
    turn_master(eng, -2)  # Aeolian, puis Chroma
    turn_master(eng, -1)  # en boucle : la dernière gamme
    assert eng.layout.name == cfg.layouts[-1].name
    btn(eng, "DISPLAY_3")  # QUANT : en boucle
    q = eng.quantize
    turn_master(eng, len(QUANTIZE_CYCLE))
    assert eng.quantize == q


def test_menu_push_cycles_focus(cfg: Config, project: Project) -> None:
    eng = design(cfg, project=project)
    btn(eng, "MASTER_PUSH")  # GAMME -> TRACK
    assert eng.menu == 1
    turn_master(eng, 4)
    assert eng.track == 5
    btn(eng, "MASTER_PUSH")
    btn(eng, "MASTER_PUSH")
    btn(eng, "MASTER_PUSH")  # QUANT, PHRASE, puis retour à GAMME
    assert eng.menu == 0
    btn(eng, "DISPLAY_7")  # pas d'entrée : focus inchangé
    assert eng.menu == 0


def test_menu_phrase_until_bank_change(cfg: Config, project: Project) -> None:
    eng = design(cfg, project=project)
    btn(eng, "DISPLAY_4")  # PHRASE
    turn_master(eng, 1)
    assert eng.phrase.length == 64
    btn(eng, "GROUP_C")  # nouvelle banque : sa phrase
    assert eng.phrase.length == project.defaults.phrase
    btn(eng, "DISPLAY_4")
    turn_master(eng, 1)
    eng.on_program_change(2 * 16 + 1)  # C02 : la banque choisie, la surcharge tient
    assert eng.phrase.length == 64


def test_hit_kept_with_note_for_screen(cfg: Config, project: Project) -> None:
    eng = design(cfg, project=project)
    btn(eng, "GROUP_E")
    press(eng, 0, pressure=3000)
    assert eng.last_hit is not None and eng.last_hit[1:3] == (70, 127)


def test_arrows_switch_encoder_page_and_pitch_bend(cfg: Config) -> None:
    from mk_brain.engine import ControlChange, PitchBend

    eng = Engine(cfg)
    btn(eng, "BROWSE_RIGHT")  # page 2 : LVL CUT RES ENV MW BC PB PAN
    assert eng.handle(EncoderEvent(7, 2 * CC_STEP, 0), 0) == []  # PB sans SHIFT : rien
    assert eng.last_control == "PB: hold SHIFT"
    btn(eng, "SHIFT")
    assert eng.handle(EncoderEvent(7, 2 * CC_STEP, 0), 0) == [
        (0, PitchBend(0, 256))
    ]  # PB : 64 → 66
    assert eng.faders.view(1)[6].value == 66
    assert eng.handle(ButtonEvent("SHIFT", False), MS) == [(MS, PitchBend(0, 0))]  # au centre
    assert eng.faders.view(1)[6].value == 64
    assert eng.handle(ButtonEvent("SHIFT", False), MS) == []  # une seule remise
    btn(eng, "SHIFT")
    eng.handle(EncoderEvent(7, 2 * CC_STEP, 0), 0)
    btn(eng, "SHIFT", False)
    assert eng.faders.view(1)[6].value == 64  # PB revenu au centre
    assert eng.handle(EncoderEvent(2, CC_STEP, 0), 0) == [(0, ControlChange(0, 74, 65))]  # CUT
    btn(eng, "BROWSE_LEFT")
    assert eng.last_control == "page 1/2" and eng.leds().buttons["BROWSE_RIGHT"] > 0
    assert eng.handle(EncoderEvent(2, CC_STEP, 0), 0) == [(0, ControlChange(0, 54, 65))]  # BR


def test_transport_arrows_shift_octave_in_design(cfg: Config, project: Project) -> None:
    eng = design(cfg, project=project)
    btn(eng, "GROUP_E")  # la#
    eng.group = KEYBOARD_GROUP  # chromatique depuis A#5 (70)
    btn(eng, "TRANSPORT_RIGHT")
    assert (eng.octave, eng.last_control) == (1, "octave +1")
    assert press(eng, 0) == [(3 * MS, NoteOn(0, 82, 127))]
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
    assert eng.sheet is not None and eng.sheet[0] == "E-TRIBE"
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
    assert eng.sheet is None and eng.phrase.length == cfg.play.phrase


def test_announce_only_on_bank_change(cfg: Config, project: Project) -> None:
    eng = Engine(cfg, project=project)
    eng.on_program_change(4 * 16 + 2)  # E03
    eng.announce = None
    eng.on_program_change(4 * 16 + 3)  # E04 : même banque
    assert eng.announce is None
    eng.on_program_change(5 * 16)  # F01
    assert eng.announce is not None and eng.announce[0] == "F-MENTAL"


def test_bank_follows_dt2_unless_same_pattern_bank(cfg: Config, project: Project) -> None:
    eng = design(cfg, project=project)
    eng.on_program_change(4 * 16)  # E01 : banque E, comme GROUP E, annoncée
    assert eng.sheet is not None and eng.sheet[0] == "E-TRIBE" and eng.announce is not None
    btn(eng, "GROUP_A")  # choix à la main
    eng.on_program_change(4 * 16 + 1)  # E02 : la DT2 reste en E, le choix tient
    assert eng.sheet is not None and eng.sheet[0] == "A-HALF"
    eng.on_program_change(7 * 16)  # H01 : la DT2 passe en H, absente du projet
    assert eng.bank == 7 and eng.sheet is None and group(eng) == "C"  # disposition gardée


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
    assert eng.sheet is not None and eng.sheet[0] == "E-TRIBE"  # contexte repris du PC


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


def test_selection_refused_while_running(cfg: Config, project: Project) -> None:
    eng = Engine(cfg, running_clock(), project, _catalog(project))
    eng.on_start()
    eng.open_selection()
    assert eng.selector is None and eng.last_control == "transport running: no project change"


def test_start_in_live_closes_selection(cfg: Config, project: Project) -> None:
    eng = Engine(cfg, catalog=_catalog(project))
    eng.open_selection()
    eng.clock = running_clock()
    eng.tick(0)
    assert eng.selector is None


def test_starts_in_mpc_without_bank(cfg: Config, project: Project) -> None:
    eng = Engine(cfg, project=project)
    assert eng.mpc and eng.bank is None and eng.quantize == cfg.play.quantize


# --- session : derniers réglages ---------------------------------------------------


def test_snapshot_restore_round_trip(cfg: Config, project: Project) -> None:
    eng = design(cfg, project=project)
    btn(eng, "GROUP_E")
    btn(eng, "TRANSPORT_RIGHT")  # octave +1
    btn(eng, "SELECT")
    eng.handle(PadEvent(PAD1 - 2, True, 2500), 0)  # pad 3
    btn(eng, "SELECT", False)
    eng.handle(EncoderEvent(5, 10 * CC_STEP, 0), 0)  # CUT de T03
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
    eng.restore(Session(program=4 * 16 + 3, bank=7))
    assert eng.last_program == 2 * 16 and eng.bank == 2  # la DT2 l'emporte


def test_restore_session_from_before_slice_8(cfg: Config, project: Project) -> None:
    old = Session.model_validate({"design_bank": 4, "group": 1, "octave": 0, "track": 3})
    eng = Engine(cfg, project=project)
    eng.restore(old)
    assert eng.bank == 4 and group(eng) == "D" and eng.track == 3


def test_session_keeps_layout_by_name_or_old_group(cfg: Config, project: Project) -> None:
    eng = design(cfg, project=project)
    btn(eng, "GROUP_A")
    turn_master(eng, -2)  # Aeolian, Chroma, puis en boucle la dernière gamme (sans groupe)
    snap = eng.snapshot()
    assert snap.layout == cfg.layouts[-1].name
    fresh = Engine(cfg, project=project)
    fresh.restore(snap)
    assert fresh.layout.name == cfg.layouts[-1].name
    old = Engine(cfg, project=project)
    old.restore(Session(layout="E", bank=0))  # session d'avant : la lettre du groupe
    assert group(old) == "E"


def test_keyboard_layout_follows_bank_mode_until_gamme(cfg: Config, project: Project) -> None:
    eng = design(cfg, project=project)
    assert group(eng) == "B"  # sans banque : chromatique
    btn(eng, "GROUP_E")
    assert group(eng) == "D"  # E-TRIBE phrygien
    btn(eng, "DISPLAY_1")  # GAMME : surcharge
    turn_master(eng, 1)
    assert group(eng) == "E"
    eng.on_program_change(4 * 16 + 1)  # la DT2 en E, déjà choisie : la surcharge tient
    assert group(eng) == "E"
    eng.on_program_change(6 * 16)  # G-JOKER : chromatique
    assert group(eng) == "B"


def test_arrows_cycle_both_ways(cfg: Config) -> None:
    eng = Engine(cfg)
    btn(eng, "BROWSE_LEFT")  # de la page 1 vers la dernière, en boucle
    assert eng.faders.page_index == 1 and eng.last_control == "page 2/2"
    btn(eng, "BROWSE_RIGHT")  # de la dernière vers la page 1
    assert eng.faders.page_index == 0


def test_dt2_knob_on_track_channel_selects_track(cfg: Config) -> None:
    eng = Engine(cfg)  # DT2 OUTPUT CH = TRACK CH
    eng.on_control_change(3, 54, 112)  # BR tourné sur la track 4 active
    assert eng.track == 4 and eng.last_control == "T04 selected (DT2)"
    assert eng.faders.view(4)[1].value == 112
    eng.on_control_change(6, 94, 1)  # mute de la track 7 : pas de sélection
    assert eng.track == 4 and eng.faders.muted[7]
    eng.on_control_change(15, 54, 90)  # track 16 (AUTO CHANNEL) : suivie aussi
    assert eng.track == 16 and eng.faders.view(16)[1].value == 90


# --- slice 9 : perform (SOLO), SHIFT + pad joue ------------------------------------


def test_shift_pad_plays_and_pad_mode_leaves_solo(cfg: Config) -> None:
    eng = Engine(cfg)
    btn(eng, "SHIFT")
    assert press(eng, 0, pad=PAD7)[0][1] == NoteOn(2, 61, 127)  # plus de perform par SHIFT
    btn(eng, "SHIFT", False)
    eng.handle(PadEvent(PAD7, False, 0), 10 * MS)
    btn(eng, "SOLO")
    btn(eng, "SOLO", False)
    btn(eng, "PAD_MODE")  # sort de SOLO sans basculer la disposition
    assert (eng.perform_lock, eng.mpc, eng.mode_name) == (False, True, "MPC")
    btn(eng, "PAD_MODE", False)
    btn(eng, "PAD_MODE")
    assert eng.mode_name == "KEYS"


def test_solo_locks_perform_taps_toggle_tracks(cfg: Config) -> None:
    from mk_brain.engine import ControlChange

    eng = Engine(cfg)
    eng.track = 9
    btn(eng, "SOLO")
    assert eng.perform_lock and eng.leds().buttons["SOLO"] == LED_MAX
    assert press(eng, 0, pad=PAD7) == []  # pad 7 : T7 (grille, pas la table mpc), pas de note
    eng.handle(PadEvent(PAD7, False, 0), MS)
    assert press(eng, 2 * MS, pad=PAD1) == []  # pad 1 : T1 ajoutée
    eng.handle(PadEvent(PAD1, False, 0), 3 * MS)
    assert eng.perform_tracks == [7, 1] and eng.fader_track == 7
    by_pad = {pad_label(i): rgb for i, rgb in enumerate(eng.leds().pads)}
    assert by_pad[7] == by_pad[1] == cfg.leds.perform_on  # groupe : vert vif
    assert by_pad[2] == by_pad[16] == cfg.leds.perform_idle  # les autres : bleu faible
    assert eng.handle(EncoderEvent(2, 2 * CC_STEP, 0), 4 * MS) == [
        (4 * MS, ControlChange(6, 54, 66)),
        (4 * MS, ControlChange(0, 54, 66)),
    ]
    press(eng, 500 * MS, pad=PAD7)  # second tap (après l'anti-rebond) : T7 retirée
    eng.handle(PadEvent(PAD7, False, 0), 600 * MS)
    assert eng.perform_tracks == [1]
    btn(eng, "SOLO")  # sortie : groupe vidé, pads rejoués
    assert not eng.perform_lock and eng.perform_tracks == [] and eng.fader_track == 9
    assert press(eng, 700 * MS, pad=PAD7)[0][1] == NoteOn(2, 61, 127)


def test_solo_lock_keyboard_pad16_refused(cfg: Config) -> None:
    eng = design(cfg)
    btn(eng, "SOLO")
    assert press(eng, 0, pad=3) == []  # pad 16 : AUTO CHANNEL, ni note ni groupe
    assert eng.perform_tracks == []


def test_solo_tap_ignores_release_bounces(cfg: Config) -> None:
    eng = Engine(cfg)
    btn(eng, "SOLO")
    eng.handle(PadEvent(PAD7, True, 2500), 0)  # tap : T7 ajoutée
    eng.handle(PadEvent(PAD7, False, 0), 200 * MS)
    eng.handle(PadEvent(PAD7, True, 600), 205 * MS)  # rebonds en levant le doigt
    eng.handle(PadEvent(PAD7, False, 0), 210 * MS)
    eng.handle(PadEvent(PAD7, True, 600), 215 * MS)
    eng.handle(PadEvent(PAD7, False, 0), 220 * MS)
    assert eng.perform_tracks == [7]
    eng.handle(PadEvent(PAD7, True, 2500), 500 * MS)  # vrai second tap : retirée
    assert eng.perform_tracks == []


def test_solo_pitch_bend_with_shift_recenters_group(cfg: Config) -> None:
    from mk_brain.engine import PitchBend

    eng = Engine(cfg)
    btn(eng, "BROWSE_RIGHT")  # page 2 : PB en encodeur 7
    btn(eng, "SOLO")
    for pad in (PAD1, PAD7):  # T1 et T7
        eng.handle(PadEvent(pad, True, 2500), 0)
        eng.handle(PadEvent(pad, False, 0), MS)
    assert eng.handle(EncoderEvent(7, 2 * CC_STEP, 0), 2 * MS) == []  # sans SHIFT : rien
    btn(eng, "SHIFT")
    assert eng.handle(EncoderEvent(7, 2 * CC_STEP, 0), 3 * MS) == [
        (3 * MS, PitchBend(0, 256)),
        (3 * MS, PitchBend(6, 256)),
    ]
    assert eng.handle(ButtonEvent("SHIFT", False), 4 * MS) == [
        (4 * MS, PitchBend(0, 0)),
        (4 * MS, PitchBend(6, 0)),
    ]


def test_mute_tap_ignores_release_bounces(cfg: Config) -> None:
    from mk_brain.engine import ControlChange

    eng = Engine(cfg)
    btn(eng, "MUTE")
    assert eng.handle(PadEvent(PAD7, True, 2500), 0) == [(0, ControlChange(6, 94, 127))]
    eng.handle(PadEvent(PAD7, False, 0), 200 * MS)
    assert eng.handle(PadEvent(PAD7, True, 600), 205 * MS) == []  # rebond : pas de démute
    eng.handle(PadEvent(PAD7, False, 0), 210 * MS)
    assert eng.faders.muted[7]
    assert eng.handle(PadEvent(PAD7, True, 2500), 500 * MS) == [(500 * MS, ControlChange(6, 94, 0))]


def _hold_shift_erase(eng: Engine, t: int = 0) -> None:
    eng.handle(ButtonEvent("SHIFT", True), t)
    eng.handle(ButtonEvent("ERASE", True), t)


def test_shift_erase_held_two_seconds_requests_poweroff(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.poweroff_enabled = True
    _hold_shift_erase(eng)
    assert eng.last_control == "POWER OFF: hold 2 s"
    eng.tick(2 * SECOND - 1)
    assert not eng.poweroff
    eng.tick(2 * SECOND)
    assert eng.poweroff


def test_shift_erase_released_early_cancels_poweroff(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.poweroff_enabled = True
    _hold_shift_erase(eng)
    eng.handle(ButtonEvent("ERASE", False), SECOND)
    assert eng.last_control == "power off cancelled"
    eng.tick(3 * SECOND)
    assert not eng.poweroff


def test_shift_erase_ignored_outside_service(cfg: Config) -> None:
    eng = Engine(cfg)
    _hold_shift_erase(eng)
    eng.tick(3 * SECOND)
    assert not eng.poweroff
    assert eng.last_control == ""


def test_held_modifier_is_the_displayed_mode(cfg: Config) -> None:
    eng = Engine(cfg)
    btn(eng, "MUTE")
    assert eng.mode_name == "MUTE"
    btn(eng, "MUTE", False)
    btn(eng, "SELECT")
    assert eng.mode_name == "SELECT"
    btn(eng, "SELECT", False)
    btn(eng, "SOLO")
    assert eng.mode_name == "SOLO" and eng.last_control == ""  # pas de « SOLO » en double


def test_shift_turn_is_temporary_and_cumulative(cfg: Config) -> None:
    from mk_brain.engine import ControlChange

    eng = Engine(cfg)
    step = cfg.encoders.raw_per_step
    (_, cc1), (_, cc2) = eng.faders.page[0], eng.faders.page[1]
    eng.handle(EncoderEvent(1, 3 * step, 0), 0)  # hors SHIFT : réglage gardé
    kept = eng.faders.value(1, cc1)
    start2 = eng.faders.value(1, cc2)
    btn(eng, "SHIFT")
    eng.handle(EncoderEvent(1, 5 * step, 0), 0)
    eng.handle(EncoderEvent(1, 2 * step, 0), 0)  # second geste : la valeur d'avant reste la 1re
    eng.handle(EncoderEvent(2, -4 * step, 0), 0)
    assert eng.faders.value(1, cc1) == kept + 7
    out = eng.handle(ButtonEvent("SHIFT", False), MS)
    assert {m for _, m in out} == {ControlChange(0, cc1, kept), ControlChange(0, cc2, start2)}
    assert (eng.faders.value(1, cc1), eng.faders.value(1, cc2)) == (kept, start2)
    assert eng.handle(ButtonEvent("SHIFT", True), 2 * MS) == []
    assert eng.handle(ButtonEvent("SHIFT", False), 3 * MS) == []  # rien à rendre


# --- slice 10 : aftertouch ----------------------------------------------------


def test_held_pad_pressure_sends_channel_aftertouch(cfg: Config) -> None:
    """Pad tenu : pas d'aftertouch à la frappe, puis la pression au-dessus du seuil,
    au plus un message par intervalle, et 0 au relâché."""
    from mk_brain.engine import Aftertouch

    at = cfg.aftertouch
    eng = Engine(cfg)
    assert press(eng, 0, pressure=3000) == [(3 * MS, NoteOn(0, 60, 127))]  # frappe seule
    late = 3 * MS + int(at.delay_ms * 1e6)
    assert eng.handle(PadEvent(PAD1, True, at.threshold), late) == []  # tenu sans appuyer
    full = eng.handle(PadEvent(PAD1, True, at.full_scale), late + MS)
    assert full == [(late + MS, Aftertouch(0, 127))]
    assert eng.handle(PadEvent(PAD1, True, at.threshold + 100), late + 2 * MS) == []  # trop tôt
    after = late + MS + int(at.interval_ms * 1e6)
    ((t, msg),) = eng.handle(PadEvent(PAD1, True, at.threshold + 100), after)
    assert t == after and isinstance(msg, Aftertouch) and 0 < msg.value < 127
    out = eng.handle(PadEvent(PAD1, False, 0), after + MS)  # relâché : retour à 0 immédiat
    assert (after + MS, Aftertouch(0, 0)) in out and NoteOff(0, 60) in [m for _, m in out]
    assert eng.tick(after + SECOND) == []


def test_keyboard_aftertouch_takes_strongest_pad(cfg: Config) -> None:
    from mk_brain.engine import Aftertouch

    at = cfg.aftertouch
    eng = design(cfg)
    channel = eng.track - 1
    press(eng, 0, pressure=at.threshold)  # frappes sous le seuil : rien avant la suite
    press(eng, 0, pressure=at.threshold, pad=PAD7)
    late = SECOND
    span = at.full_scale - at.threshold
    eng.handle(PadEvent(PAD1, True, at.threshold + span // 4), late)
    out = eng.handle(PadEvent(PAD7, True, at.full_scale), late + 20 * MS)
    assert out == [(late + 20 * MS, Aftertouch(channel, 127))]
    out = eng.handle(PadEvent(PAD7, False, 0), late + 40 * MS)  # reste le pad le plus léger
    values = [m.value for _, m in out if isinstance(m, Aftertouch)]
    assert values == [round(127 / 4)]


# --- slice 11 : arpégiateur ----------------------------------------------------


def _index(pad: int) -> int:
    """Index HID du pad imprimé `pad`."""
    return next(i for i in range(16) if pad_label(i) == pad)


def arp(cfg: Config, clock: ClockTracker | None = None) -> Engine:
    """Moteur en mode ARPG (PATTERN), horloge lancée par défaut."""
    eng = Engine(cfg, clock or running_clock(80))
    btn(eng, "PATTERN")
    btn(eng, "PATTERN", False)
    return eng


def _ons(out: list[Timed]) -> list[int]:
    return [m.note for _, m in out if isinstance(m, NoteOn)]


def test_pattern_enters_arpg_tap_leaves_and_pad_mode_goes_to_mpc(cfg: Config) -> None:
    eng = arp(cfg)
    assert eng.mode_name == "ARPG" and eng.keyboard and not eng.arp_menu
    assert eng.leds().buttons["PATTERN"] == LED_MAX
    btn(eng, "PATTERN", t=SECOND)  # appui bref : sortie vers le clavier, au relâché
    assert eng.arp and eng.arp_menu
    btn(eng, "PATTERN", False, t=SECOND + 100 * MS)
    assert eng.mode_name == "KEYS" and not eng.arp_menu
    assert 0 < eng.leds().buttons["PATTERN"] < LED_MAX
    btn(eng, "PATTERN", t=2 * SECOND)
    btn(eng, "PATTERN", False, t=2 * SECOND + 100 * MS)  # l'appui qui entre ne sort pas
    btn(eng, "PAD_MODE")
    assert eng.mode_name == "MPC" and not eng.arp


def test_pattern_held_is_the_arp_config(cfg: Config) -> None:
    """PATTERN tenu : config à l'écran, encodeurs 1-3 sur l'arpège ; relâché, le mode
    reste (appui long ou réglage fait) et les encodeurs retrouvent la track."""
    eng = arp(cfg)
    step = cfg.arp.raw_per_choice
    btn(eng, "PATTERN", t=SECOND)
    assert eng.handle(EncoderEvent(2, step, 0), SECOND) == [] and eng.arp_octaves == 2
    btn(eng, "PATTERN", False, t=SECOND + 100 * MS)  # bref, mais un réglage a été fait
    assert eng.arp and not eng.arp_menu
    assert eng.handle(EncoderEvent(1, cfg.encoders.raw_per_step, 0), 2 * SECOND) != []
    btn(eng, "PATTERN", t=3 * SECOND)
    btn(eng, "PATTERN", False, t=4 * SECOND)  # tenu 1 s sans rien régler : simple regard
    assert eng.arp


def test_arp_plays_held_pads_one_per_division(cfg: Config) -> None:
    """Trois pads tenus : montant, une note par double croche, note off à mi-division."""
    eng = arp(cfg)
    pads = [_index(p) for p in (1, 3, 5)]
    notes = [eng.target(p)[1] for p in (1, 3, 5)]
    t = 13 * TICK  # 1 tick après le 12 : première note tout de suite
    first = press(eng, t, pad=pads[0])
    assert first == [
        (t + 3 * MS, NoteOn(0, notes[0], 127)),
        (pytest.approx(15 * TICK, abs=MS // 100), NoteOff(0, notes[0])),
    ]
    assert _ons(press(eng, t, pad=pads[1]) + press(eng, t, pad=pads[2])) == []  # pas d'accord
    played: list[tuple[float, int]] = []
    for k in (18, 24, 30, 36):
        out = eng.tick(k * TICK - 10 * MS)
        played += [(tt / TICK, m.note) for tt, m in out if isinstance(m, NoteOn)]
    assert [n for _, n in played] == [notes[1], notes[2], notes[0], notes[1]]
    assert [pos for pos, _ in played] == pytest.approx([18, 24, 30, 36], abs=0.01)


def test_arp_release_stops_and_hold_keeps(cfg: Config) -> None:
    eng = arp(cfg)
    a, b = _index(1), _index(3)
    press(eng, 13 * TICK, pad=a)
    eng.handle(PadEvent(a, False, 0), 14 * TICK)
    assert eng.tick(18 * TICK) == []  # relâché, sans maintien : l'arpège s'arrête
    btn(eng, "NOTE_REPEAT")  # maintien
    assert eng.arp_hold and not eng.repeat_active
    assert eng.leds().buttons["NOTE_REPEAT"] == LED_MAX
    press(eng, 19 * TICK, pad=a)
    eng.handle(PadEvent(a, False, 0), 20 * TICK)
    note_a, note_b = eng.target(1)[1], eng.target(3)[1]
    assert _ons(eng.tick(24 * TICK - 10 * MS)) == [note_a]  # tient pad relâché
    press(eng, 25 * TICK, pad=b)  # aucun pad tenu : la nouvelle note remplace
    assert _ons(eng.tick(30 * TICK - 10 * MS) + eng.tick(36 * TICK - 10 * MS)) == [note_b, note_b]
    btn(eng, "NOTE_REPEAT", False)
    btn(eng, "NOTE_REPEAT")  # maintien coupé, pad b encore tenu : il reste
    assert _ons(eng.tick(42 * TICK - 10 * MS)) == [note_b]
    eng.handle(PadEvent(b, False, 0), 43 * TICK)
    assert eng.tick(48 * TICK) == []


def test_arp_gate_full_ends_before_next_note(cfg: Config) -> None:
    eng = arp(cfg)
    eng.arp_gate = 100
    out = press(eng, 13 * TICK, pad=_index(1))
    off = next(t for t, m in out if isinstance(m, NoteOff))
    assert off == pytest.approx(18 * TICK - NOTE_OFF_MIN_NS, abs=MS // 100)


def test_arp_needs_running_transport_and_stops_with_it(cfg: Config) -> None:
    eng = arp(cfg, ClockTracker())  # transport arrêté : le clavier joue
    note = eng.target(1)[1]
    assert press(eng, 0, pad=_index(1)) == [(3 * MS, NoteOn(0, note, 127))]
    eng = arp(cfg)
    btn(eng, "NOTE_REPEAT")
    press(eng, 13 * TICK, pad=_index(1))
    eng.on_stop()
    assert eng.tick(18 * TICK) == []


def test_arp_config_encoders_and_division_buttons(cfg: Config) -> None:
    eng = arp(cfg)
    btn(eng, "DISPLAY_2")  # divisions : tout le temps en ARPG, PATTERN tenu ou non
    assert eng.division == "1/8"
    btn(eng, "PATTERN", t=SECOND)
    step, gate_step = cfg.arp.raw_per_choice, cfg.arp.raw_per_gate_step
    assert eng.handle(EncoderEvent(2, step - 1, 0), 0) == [] and eng.arp_octaves == 1
    eng.handle(EncoderEvent(2, 1, 0), 0)  # la course s'accumule : une valeur par `step`
    assert eng.arp_octaves == 2
    eng.handle(EncoderEvent(2, 5 * step, 0), 0)
    assert eng.arp_octaves == 3  # borné
    eng.handle(EncoderEvent(3, -gate_step, 0), 0)
    assert eng.arp_gate == 45 and eng.last_control == "ARP GATE 45%"
    eng.handle(EncoderEvent(1, 3 * step, 0), 0)
    assert eng.arp_order == "played"
    eng.handle(EncoderEvent(4, step, 0), 0)  # MOT : OFF, puis les motifs de la config
    assert eng.arp_motif == cfg.arp.motif_names[1] and eng.last_control == "ARP MOT GALO"
    eng.handle(EncoderEvent(4, -5 * step, 0), 0)
    assert eng.arp_motif == "OFF" and eng.arp_steps is None  # borné
    assert eng.handle(EncoderEvent(7, step, 0), 0) == []  # rien n'est envoyé à la DT2
    assert eng.arp_progression == cfg.arp.progression_names[1]
    eng.handle(EncoderEvent(8, 9 * step, 0), 0)
    assert eng.arp_bars == "4" and eng.last_control == "ARP BAR 4"  # borné
    btn(eng, "BROWSE_RIGHT")  # BROWSE : pages de son, comme partout
    assert eng.last_control == "page 2/2"


def test_arp_settings_survive_the_session(cfg: Config) -> None:
    eng = arp(cfg)
    eng.arp_order, eng.arp_octaves, eng.arp_gate, eng.division = "updown", 2, 80, "1/8T"
    other = Engine(cfg)
    other.restore(Session.model_validate(eng.snapshot().model_dump()))
    assert (other.arp_order, other.arp_octaves, other.arp_gate) == ("updown", 2, 80)
    assert other.division == "1/8T" and not other.arp and other.arp_motif == "OFF"
    other.restore(Session(arp_order="zigzag", arp_octaves=9, arp_gate=0, division="1/5"))
    assert (other.arp_order, other.arp_octaves, other.arp_gate) == ("updown", 2, 80)
    eng.arp_motif = "LONG"
    other.restore(Session.model_validate(eng.snapshot().model_dump()))
    assert other.arp_motif == "LONG"
    other.restore(Session(arp_motif="DISPARU"))
    assert other.arp_motif == "LONG"


def _arp_notes(eng: Engine, positions: Iterable[int]) -> list[tuple[float, int, int]]:
    """(position en ticks, note, vélocité) des note on de l'arpège à ces positions."""
    played: list[tuple[float, int, int]] = []
    for k in positions:
        out = eng.tick(k * TICK - 10 * MS)
        played += [(tt / TICK, m.note, m.velocity) for tt, m in out if isinstance(m, NoteOn)]
    return played


def test_arp_motif_rests_wait_and_plain_steps_are_softer(cfg: Config) -> None:
    """Motif GALO (`X.xx`), calé sur la mesure : le silence ne consomme pas de note, les
    pas `x` partent à `arp.unaccented` % de la vélocité du pad, les `X` à la pression."""
    eng = arp(cfg)
    eng.arp_motif = "GALO"
    notes = [eng.target(p)[1] for p in (1, 3, 5)]
    soft = round(127 * cfg.arp.unaccented / 100)
    first = press(eng, 13 * TICK, pad=_index(1))  # position 12 : pas 2 du motif, un `x`
    assert [m for _, m in first if isinstance(m, NoteOn)] == [NoteOn(0, notes[0], soft)]
    press(eng, 13 * TICK, pad=_index(3))
    press(eng, 13 * TICK, pad=_index(5))
    played = _arp_notes(eng, (18, 24, 30, 36, 42))
    assert [(n, v) for _, n, v in played] == [
        (notes[1], soft),  # pas 3 : x
        (notes[2], 127),  # pas 4 : X
        (notes[0], soft),  # pas 5 : silence, la note attend le pas 6
        (notes[1], soft),  # pas 7 : x
    ]
    assert [pos for pos, _, _ in played] == pytest.approx([18, 24, 36, 42], abs=0.01)


def test_arp_motif_ties_lengthen_the_note(cfg: Config) -> None:
    """Motif LONG (`X--- x-x- …`), gate 50 % : la note dure ses pas liés plus son gate."""
    eng = arp(cfg)
    eng.arp_motif = "LONG"
    note = eng.target(1)[1]
    first = press(eng, 1 * TICK, pad=_index(1))  # position 0 : X suivi de 3 liées
    assert first == [
        (1 * TICK + 3 * MS, NoteOn(0, note, 127)),
        (pytest.approx(21 * TICK, abs=MS // 100), NoteOff(0, note)),  # 3 × 6 + 3 ticks
    ]
    assert _arp_notes(eng, (6, 12, 18)) == []  # pas liés : pas de nouvelle attaque
    out = eng.tick(24 * TICK - 10 * MS)  # pas 4 : x suivi d'une liée
    assert [m for _, m in out] == [
        NoteOn(0, note, round(127 * cfg.arp.unaccented / 100)),
        NoteOff(0, note),
    ]
    assert [t / TICK for t, _ in out] == pytest.approx([24, 33], abs=0.01)  # 6 + 3 ticks


def test_arp_short_motif_turns_against_the_bar(cfg: Config) -> None:
    """Motif CINQ (`X.xx.`, 5 pas) : le pas joué est la position modulo 5, pas modulo 16 ;
    l'accent tombe sur les pas 0, 5, 10, 15, 20 du transport."""
    eng = arp(cfg)
    eng.arp_motif = "CINQ"
    note = eng.target(1)[1]
    soft = round(127 * cfg.arp.unaccented / 100)
    first = press(eng, 1 * TICK, pad=_index(1))  # position 0 : X
    assert _ons(first) == [note]
    played = _arp_notes(eng, range(6, 132, 6))  # pas 1 à 21
    assert [round(pos / 6) for pos, _, _ in played] == [2, 3, 5, 7, 8, 10, 12, 13, 15, 17, 18, 20]
    assert [v for _, _, v in played] == [soft, soft, 127] * 4


class _FixedDraw(random.Random):
    """Tirage figé pour les pas `?`."""

    def __init__(self, draw: float) -> None:
        super().__init__()
        self._draw = draw

    def random(self) -> float:
        return self._draw


def test_arp_chance_step_plays_once_in_two(cfg: Config) -> None:
    """Motif HASA (`X.?x …`) : le pas `?` joue, atténué, si le tirage passe ; sinon c'est
    un silence et la note attend le pas suivant."""
    soft = round(127 * cfg.arp.unaccented / 100)
    for draw, expected in ((0.2, [(12, 1), (18, 0)]), (0.8, [(18, 1)])):
        eng = arp(cfg)
        eng.arp_motif = "HASA"
        eng._rng = _FixedDraw(draw)
        notes = [eng.target(p)[1] for p in (1, 3)]
        press(eng, 1 * TICK, pad=_index(1))  # position 0 : X
        press(eng, 1 * TICK, pad=_index(3))
        played = _arp_notes(eng, (12, 18))  # pas 2 : ?, pas 3 : x
        assert [(round(pos), n, v) for pos, n, v in played] == [
            (pos, notes[i], soft) for pos, i in expected
        ]


def test_arp_ratchet_replays_the_note_inside_the_step(cfg: Config) -> None:
    """Motif RATC (`X.xr …`), 1/16, gate 50 % : le pas `r` joue deux fois la même note,
    atténuée, chaque coup durant un quart de pas ; l'arpège n'avance que d'une note."""
    eng = arp(cfg)
    eng.arp_motif = "RATC"
    notes = [eng.target(p)[1] for p in (1, 3)]
    soft = round(127 * cfg.arp.unaccented / 100)
    press(eng, 13 * TICK, pad=_index(1))  # position 12 : pas 2, un `x`
    press(eng, 13 * TICK, pad=_index(3))
    out = eng.tick(18 * TICK - 10 * MS)  # pas 3 : r
    assert [m for _, m in out] == [
        NoteOn(0, notes[1], soft),
        NoteOff(0, notes[1]),
        NoteOn(0, notes[1], soft),
        NoteOff(0, notes[1]),
    ]
    assert [t / TICK for t, _ in out] == pytest.approx([18, 19.5, 21, 22.5], abs=0.01)
    assert [(n, v) for _, n, v in _arp_notes(eng, (24,))] == [(notes[0], 127)]  # pas 4 : X


def test_arp_preset_recalls_the_settings(cfg: Config) -> None:
    """PATTERN tenu, pad n : le preset s'applique d'un coup ; un réglage retouché ne
    l'affiche plus comme courant, le dernier rappelé reste connu et suit la session."""
    eng = arp(cfg)
    names = list(cfg.arp.presets)
    btn(eng, "PATTERN", t=SECOND)
    assert eng.arp_preset_shown is None
    assert press(eng, SECOND, pad=_index(1)) == []
    first = cfg.arp.presets[names[0]]
    assert (eng.arp_order, eng.arp_octaves, eng.arp_gate, eng.division, eng.arp_motif) == (
        first.order,
        first.octaves,
        first.gate,
        first.division,
        first.motif,
    )
    assert eng.arp_preset_shown == names[0] and eng.last_control == f"ARP PRE {names[0]}"
    eng.handle(EncoderEvent(3, cfg.arp.raw_per_gate_step, 0), 0)  # GATE retouché
    assert eng.arp_preset_shown is None and eng.arp_preset == names[0]
    other = Engine(cfg)
    other.restore(Session.model_validate(eng.snapshot().model_dump()))
    assert other.arp_preset == names[0] and other.arp_gate == eng.arp_gate
    other.restore(Session(arp_preset="DISPARU"))
    assert other.arp_preset == names[0]


def test_arp_inversion_moves_the_low_notes_up_and_fix_holds_the_register(cfg: Config) -> None:
    """Encodeur 5 INV, PATTERN tenu. `1` : la fondamentale passe au-dessus. `FIX` sous une
    progression : les accords restent dans l'octave au-dessus du pad tenu."""
    eng = arp(cfg, running_clock(300))
    eng.group = next(i for i, lay in enumerate(cfg.layouts) if lay.name == "Aeolian")
    eng.division, eng.arp_chord = "1/4", "tri"
    step = cfg.arp.raw_per_choice
    btn(eng, "PATTERN", t=0)
    eng.handle(EncoderEvent(5, step, 0), 0)
    assert eng.arp_view()[4] == ("INV", "1") and eng.last_control == "ARP INV 1"
    eng.handle(EncoderEvent(5, 99 * step, 0), 0)
    assert eng.arp_view()[4] == ("INV", "FIX") and eng._arp_current().inversion == "fix"
    btn(eng, "PATTERN", False, t=SECOND)
    eng.arp_inversion, root = "1", eng.target(1)[1]
    first = press(eng, 1 * TICK, pad=_index(1))
    played = _ons(first) + [n for _, n, _ in _arp_notes(eng, (24, 48))]
    assert played == [root + 3, root + 7, root + 12]  # do mineur, premier renversement
    eng.arp_inversion, eng.arp_progression, eng.arp_bars = "fix", "1637", "1/2"
    played = [n for _, n, _ in _arp_notes(eng, range(72, 216, 24))]
    assert played == [
        root,  # 6 : la bémol majeur ramené au-dessus du pad (do mib lab), une note
        *[root + 3, root + 7],  # 3 : mi bémol majeur
        *[root + 2, root + 5],  # 7 : si bémol majeur, ré en bas (ré fa sib)
        root,  # 1 : do mineur
    ]
    other = Engine(cfg)
    other.restore(Session.model_validate(eng.snapshot().model_dump()))
    assert other.arp_inversion == "fix"
    other.restore(Session(arp_inversion="3"))
    assert other.arp_inversion == "fix"


def test_arp_bank_pads_recall_and_shift_saves(cfg: Config) -> None:
    """PATTERN tenu : pad n = rappel de l'emplacement n, SHIFT + pad n = sauvegarde des
    réglages courants ; les pads ne jouent pas, le relâché de PATTERN ne sort pas du mode."""
    eng = arp(cfg)
    names = list(cfg.arp.presets)
    btn(eng, "PATTERN", t=SECOND)

    def tap(pad: int, t: int) -> None:
        assert press(eng, t, pad=_index(pad)) == []
        eng.handle(PadEvent(_index(pad), False, 0), t + MS)

    assert press(eng, SECOND, pad=_index(2)) == [] and eng.arp_preset_shown == names[1]
    eng.handle(PadEvent(_index(2), False, 0), SECOND + MS)
    assert eng._arp_notes == {}  # pas de note dans l'arpège
    dim = eng.leds().pads
    assert dim[_index(2)] == cfg.leds.preset and dim[_index(16)] == (0, 0, 0)  # courant, vide
    assert (0, 0, 0) != dim[_index(1)] != cfg.leds.preset  # occupé : faible
    tap(16, 2 * SECOND)  # emplacement vide : rien ne change
    assert eng.arp_preset_shown == names[1] and eng.last_control == "ARP PRE 16 empty"
    eng.handle(EncoderEvent(3, -cfg.arp.raw_per_gate_step, 0), 0)  # réglage à l'oreille
    mine = (eng.arp_order, eng.arp_octaves, eng.arp_gate, eng.division, eng.arp_motif)
    btn(eng, "SHIFT", t=3 * SECOND)
    tap(9, 3 * SECOND)
    btn(eng, "SHIFT", False, t=3 * SECOND)
    assert eng.arp_bank_dirty and list(eng.arp_user) == [9]
    assert eng.arp_preset_shown == "U09" and eng.last_control == "ARP PRE U09 saved"
    tap(1, 4 * SECOND)
    assert eng.arp_preset_shown == names[0]
    tap(9, 5 * SECOND)
    assert (eng.arp_order, eng.arp_octaves, eng.arp_gate, eng.division, eng.arp_motif) == mine
    btn(eng, "PATTERN", False, t=5 * SECOND + 100 * MS)
    assert eng.arp  # un rappel compte comme un réglage


def test_arp_bank_saved_slot_wins_over_config(cfg: Config) -> None:
    eng = arp(cfg)
    names = list(cfg.arp.presets)
    eng.arp_user = {1: cfg.arp.presets[names[3]], 12: cfg.arp.presets[names[4]]}
    assert list(eng.arp_bank) == ["U01", *names[1:], "U12"]
    btn(eng, "PATTERN", t=SECOND)
    press(eng, SECOND, pad=_index(1))
    assert eng.arp_preset_shown == "U01" and eng.arp_motif == cfg.arp.presets[names[3]].motif
    press(eng, 2 * SECOND, pad=_index(12))
    assert eng.arp_preset_shown == "U12"
    other = Engine(cfg)
    other.arp_user = dict(eng.arp_user)
    other.restore(Session.model_validate(eng.snapshot().model_dump()))
    assert other.arp_preset_shown == "U12"


def test_arp_chord_one_pad_plays_a_chord_in_the_scale(cfg: Config) -> None:
    """Encodeur 6 CHD, PATTERN tenu : un pad tenu donne son accord, pris dans la gamme du
    clavier ; gardé dans les presets et la session."""
    eng = arp(cfg)
    eng.group = next(i for i, lay in enumerate(cfg.layouts) if lay.name == "Aeolian")
    btn(eng, "PATTERN", t=SECOND)
    eng.handle(EncoderEvent(6, cfg.arp.raw_per_choice, 0), 0)
    assert eng.arp_chord == "tri" and eng.last_control == "ARP CHD TRI"
    btn(eng, "PATTERN", False, t=2 * SECOND)
    root = eng.target(1)[1]  # do : do mi bémol sol en éolien
    first = press(eng, 13 * TICK, pad=_index(1))
    played = _ons(first) + [n for _, n, _ in _arp_notes(eng, (18, 24, 30))]
    assert played == [root, root + 3, root + 7, root]
    eng.arp_chord = "7th"
    assert [n for _, n, _ in _arp_notes(eng, (36, 42, 48, 54))] == [
        root,
        root + 3,
        root + 7,
        root + 10,
    ]
    assert eng._arp_current().chord == "7th"
    other = Engine(cfg)
    other.restore(Session.model_validate(eng.snapshot().model_dump()))
    assert other.arp_chord == "7th"
    other.restore(Session(arp_chord="jazz"))
    assert other.arp_chord == "7th"


def test_arp_progression_moves_the_held_pad_through_the_scale(cfg: Config) -> None:
    """PRG 1637, BAR 1/2, sans accord : le pad tenu suit les degrés, un par demi-mesure
    (48 ticks), calé sur le transport ; 6 et 7 passent sous le pad."""
    eng = arp(cfg, running_clock(300))
    eng.group = next(i for i, lay in enumerate(cfg.layouts) if lay.name == "Aeolian")
    eng.division, eng.arp_progression, eng.arp_bars = "1/4", "1637", "1/2"
    root = eng.target(1)[1]  # do éolien
    first = press(eng, 1 * TICK, pad=_index(1))  # position 0 : degré 1
    played = _ons(first) + [n for _, n, _ in _arp_notes(eng, range(24, 216, 24))]
    assert played == [
        *[root] * 2,  # 1
        *[root - 4] * 2,  # 6 : la bémol, sous le pad
        *[root + 3] * 2,  # 3 : mi bémol
        *[root - 2] * 2,  # 7 : si bémol, sous le pad
        root,  # la boucle reprend
    ]
    assert eng._arp_current().progression == "1637"
    other = Engine(cfg)
    other.restore(Session.model_validate(eng.snapshot().model_dump()))
    assert (other.arp_progression, other.arp_bars) == ("1637", "1/2")
    other.restore(Session(arp_progression="2514", arp_bars="8"))
    assert (other.arp_progression, other.arp_bars) == ("1637", "1/2")


def test_arp_progression_restarts_the_chord_on_each_change(cfg: Config) -> None:
    eng = arp(cfg, running_clock(200))
    eng.group = next(i for i, lay in enumerate(cfg.layouts) if lay.name == "Aeolian")
    eng.division, eng.arp_progression, eng.arp_bars, eng.arp_chord = "1/4", "1637", "1/2", "tri"
    root = eng.target(1)[1]
    first = press(eng, 1 * TICK, pad=_index(1))
    played = _ons(first) + [n for _, n, _ in _arp_notes(eng, range(24, 120, 24))]
    # do mineur (2 notes), puis la bémol majeur depuis sa fondamentale
    assert played == [root, root + 3, root - 4, root, root + 3]


def test_arp_now_follows_the_chord_of_the_progression(cfg: Config) -> None:
    """Accord en cours pour l'écran : degrés, rang, notes sur le premier pad tenu ; rien
    sans progression, ni une fois l'arpège sorti."""
    eng = arp(cfg, running_clock(200))
    eng.group = next(i for i, lay in enumerate(cfg.layouts) if lay.name == "Aeolian")
    eng.division, eng.arp_bars, eng.arp_chord = "1/4", "1/2", "tri"
    root = eng.target(1)[1]
    assert eng.arp_now is None
    press(eng, 1 * TICK, pad=_index(1))
    assert eng.arp_now is None  # PRG OFF
    eng.arp_progression = "1637"
    _arp_notes(eng, range(24, 72, 24))  # jusqu'au 2e accord
    assert eng.arp_now == ([1, 6, 3, 7], 1, [root - 4, root, root + 3])
    eng._leave_arp()
    assert eng.arp_now is None

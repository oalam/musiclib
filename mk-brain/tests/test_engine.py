from __future__ import annotations

from collections.abc import Callable
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
    assert eng.handle(PadEvent(PAD1, True, 2500), 1 * MS) == []
    assert eng.tick(int(2.5 * MS)) == [(int(2.5 * MS), NoteOn(0, 60, 127))]
    assert eng.handle(PadEvent(PAD1, True, 2000), 3 * MS) == []  # tenu : rien de plus
    assert eng.handle(PadEvent(PAD1, False, 0), 100 * MS) == [(100 * MS, NoteOff(0, 60))]


def test_short_hit_fires_on_release(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.handle(PadEvent(PAD1, True, 2500), 0)
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
    btn(eng, "PAD_MODE")
    assert eng.mpc and eng.last_control == "MPC"


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

    assert eng.handle(EncoderEvent(2, 8, 0), 2 * MS) == [(2 * MS, ControlChange(6, 54, 66))]


def test_pad16_mute_refused_select_targets_active_track(cfg: Config) -> None:
    from mk_brain.engine import ControlChange

    eng = Engine(cfg)
    btn(eng, "MUTE")
    assert eng.handle(PadEvent(3, True, 2500), 0) == []  # index 3 = pad 16 : pas de mute
    assert eng.leds().pads[3] == (0, 0, 0)
    eng.handle(PadEvent(3, False, 0), MS)
    btn(eng, "MUTE", False)
    btn(eng, "SELECT")
    eng.handle(PadEvent(3, True, 2500), 2 * MS)
    eng.handle(PadEvent(3, False, 0), 3 * MS)
    btn(eng, "SELECT", False)
    assert eng.track == 16 and eng.last_control == "T16 selected (DT2 active)"
    assert eng.handle(EncoderEvent(2, 4, 0), 0) == [(0, ControlChange(15, 54, 65))]


def test_mute_pad_sends_cc94(cfg: Config) -> None:
    from mk_brain.engine import ControlChange

    eng = Engine(cfg)
    btn(eng, "MUTE")
    assert eng.handle(PadEvent(PAD1, True, 2500), 0) == [(0, ControlChange(0, 94, 127))]
    assert eng.leds().pads[PAD1] == (0, 0, 0)  # muté : éteint pendant MUTE


def test_pattern_button_unassigned(cfg: Config) -> None:
    """Slice 9 : la DT2 seule change de pattern ; PATTERN + pad joue, sans PC."""
    eng = Engine(cfg)
    btn(eng, "GROUP_B")  # GROUP seul : banque B, sans envoi
    assert eng.bank == 1 and eng.last_control == "bank B"
    btn(eng, "PATTERN")
    assert press(eng, 0, pad=PAD7) == [(3 * MS, NoteOn(2, 61, 127))]  # SD2 : T3 / 61
    assert eng.leds().buttons.get("PATTERN", 0) == 0  # non affecté : éteint


def test_dt2_knob_on_auto_channel_goes_to_selected_track(cfg: Config) -> None:
    from mk_brain.engine import ControlChange

    midi = cfg.midi.model_copy(update={"knobs_on_track_channel": False})  # DT2 OUTPUT CH = AUTO
    eng = Engine(cfg.model_copy(update={"midi": midi}))
    eng.track = 7
    eng.on_control_change(15, 54, 74)  # bouton tourné sur la DT2 : arrive sur le canal 16
    eng.on_control_change(15, 94, 1)  # mute sur l'AUTO CHANNEL : track incertaine, ignoré
    assert not eng.faders.muted
    assert eng.handle(EncoderEvent(2, -4, 0), 0) == [(0, ControlChange(6, 54, 73))]  # sans saut


def test_program_change_marks_faders_stale_once(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.on_control_change(0, 54, 30)
    eng.on_program_change(3)
    assert eng.faders.view(1)[1].stale  # BR, encodeur 2
    eng.handle(EncoderEvent(2, 4, 0), 0)
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
    assert pads[PAD1] == scale(cfg.track_colors[1], cfg.leds.dim)
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
    press(eng, 0, pressure=2500)
    assert eng.last_hit is not None and eng.last_hit[1:3] == (70, 127)


def test_arrows_switch_encoder_page_and_pitch_bend(cfg: Config) -> None:
    from mk_brain.engine import ControlChange, PitchBend

    eng = Engine(cfg)
    btn(eng, "BROWSE_RIGHT")  # page 2 : LVL CUT RES ENV MW BC PB PAN
    assert eng.handle(EncoderEvent(7, 8, 0), 0) == []  # PB sans SHIFT : rien
    assert eng.last_control == "PB: hold SHIFT"
    btn(eng, "SHIFT")
    assert eng.handle(EncoderEvent(7, 8, 0), 0) == [(0, PitchBend(0, 256))]  # PB : 64 → 66
    assert eng.faders.view(1)[6].value == 66
    assert eng.handle(ButtonEvent("SHIFT", False), MS) == [(MS, PitchBend(0, 0))]  # au centre
    assert eng.faders.view(1)[6].value == 64
    assert eng.handle(ButtonEvent("SHIFT", False), MS) == []  # une seule remise
    btn(eng, "SHIFT")
    eng.handle(EncoderEvent(7, 8, 0), 0)
    btn(eng, "SHIFT", False)
    assert eng.faders.view(1)[6].value == 64  # PB revenu au centre
    assert eng.handle(EncoderEvent(2, 4, 0), 0) == [(0, ControlChange(0, 74, 65))]  # CUT
    btn(eng, "BROWSE_LEFT")
    assert eng.last_control == "page 1/2" and eng.leds().buttons["BROWSE_RIGHT"] > 0
    assert eng.handle(EncoderEvent(2, 4, 0), 0) == [(0, ControlChange(0, 54, 65))]  # BR


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


# --- slice 9 : perform (SHIFT + pad tenu) ----------------------------------------


def test_perform_turns_pad_track_and_keeps_value_on_release(cfg: Config) -> None:
    from mk_brain.engine import ControlChange

    eng = Engine(cfg)
    eng.on_control_change(2, 54, 40)  # T3 : BR à 40 joué sur la DT2
    eng.track = 1
    btn(eng, "SHIFT")
    assert eng.handle(PadEvent(PAD7, True, 2500), 0) == []  # SD2 (T3) : pas de note
    assert eng.tick(10 * MS) == []
    btn(eng, "SHIFT", False)  # le pad tenu garde le perform
    assert (eng.perform_track, eng.fader_track) == (3, 3)
    assert eng.handle(EncoderEvent(2, 8, 0), MS) == [(MS, ControlChange(2, 54, 42))]
    assert eng.handle(PadEvent(PAD7, False, 0), 2 * MS) == []  # pas de retour
    assert eng.faders.view(3)[1].value == 42 and eng.perform_track is None
    assert eng.track == 1  # la track sélectionnée n'a pas bougé
    assert press(eng, 3 * MS, pad=PAD7)[0][1] == NoteOn(2, 61, 127)  # rejoue


def test_perform_two_pads_same_track_turned_once(cfg: Config) -> None:
    from mk_brain.engine import ControlChange

    eng = Engine(cfg)
    btn(eng, "SHIFT")
    eng.handle(PadEvent(PAD1, True, 2500), 0)  # BD : T1
    eng.handle(PadEvent(PAD1 + 1, True, 2500), 0)  # BD2 : T1
    assert eng.handle(EncoderEvent(2, 8, 0), MS) == [(MS, ControlChange(0, 54, 66))]  # une fois
    assert eng.handle(PadEvent(PAD1, False, 0), 2 * MS) == []
    assert eng.perform_track == 1  # BD2 tient encore T1
    assert eng.handle(PadEvent(PAD1 + 1, False, 0), 3 * MS) == []
    assert eng.perform_track is None and eng.fader_track == eng.track


def test_perform_keyboard_pad_n_is_track_n(cfg: Config) -> None:
    from mk_brain.engine import ControlChange

    eng = design(cfg)
    btn(eng, "SHIFT")
    eng.handle(PadEvent(PAD7, True, 2500), 0)
    assert eng.perform_track == 7
    assert eng.handle(EncoderEvent(2, 4, 0), MS) == [(MS, ControlChange(6, 54, 65))]
    eng.handle(PadEvent(PAD7, False, 0), MS)
    eng.handle(PadEvent(3, True, 2500), 2 * MS)  # pad 16 : AUTO CHANNEL refusé, sans note
    assert eng.perform_track is None and eng.tick(20 * MS) == []


def test_solo_locks_perform_taps_toggle_tracks(cfg: Config) -> None:
    from mk_brain.engine import ControlChange

    eng = Engine(cfg)
    eng.track = 9
    btn(eng, "SOLO")
    assert eng.perform_lock and eng.leds().buttons["SOLO"] == LED_MAX
    assert press(eng, 0, pad=PAD7) == []  # SD2 : T3 ajoutée, pas de note
    eng.handle(PadEvent(PAD7, False, 0), MS)
    assert press(eng, 2 * MS, pad=PAD1) == []  # BD : T1 ajoutée
    eng.handle(PadEvent(PAD1, False, 0), 3 * MS)
    assert eng.perform_tracks == [3, 1] and eng.fader_track == 3
    by_pad = {pad_label(i): rgb for i, rgb in enumerate(eng.leds().pads)}
    assert by_pad[7] == by_pad[1] == cfg.leds.perform_on  # groupe : vert vif
    assert by_pad[2] == by_pad[16] == cfg.leds.perform_idle  # les autres : bleu faible
    assert eng.handle(EncoderEvent(2, 8, 0), 4 * MS) == [
        (4 * MS, ControlChange(2, 54, 66)),
        (4 * MS, ControlChange(0, 54, 66)),
    ]
    press(eng, 5 * MS, pad=PAD7)  # second tap : T3 retirée
    eng.handle(PadEvent(PAD7, False, 0), 6 * MS)
    assert eng.perform_tracks == [1]
    btn(eng, "SOLO")  # sortie : groupe vidé, pads rejoués
    assert not eng.perform_lock and eng.perform_tracks == [] and eng.fader_track == 9
    assert press(eng, 7 * MS, pad=PAD7)[0][1] == NoteOn(2, 61, 127)


def test_solo_lock_keyboard_pad16_refused(cfg: Config) -> None:
    eng = design(cfg)
    btn(eng, "SOLO")
    assert press(eng, 0, pad=3) == []  # pad 16 : AUTO CHANNEL, ni note ni groupe
    assert eng.perform_tracks == []

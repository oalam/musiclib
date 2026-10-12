"""Tests du generateur acid (scripts/analyzer/acid.py, Phase 9.A).

Lancer :
    python -m pytest tests/test_acid.py
    python -m pytest tests/test_acid.py::test_locked_layer_kept_others_redrawn
"""
from __future__ import annotations

from pathlib import Path

import mido
import pytest
from pydantic import ValidationError

from analyzer import acid
from analyzer.acid import AcidParams, AcidSequence, AcidStep

F_SHARP_PHRYGIAN = AcidParams(root=6, scale="PHRYGIAN", type=11, density=14)


def _seq(steps: list[AcidStep], **kw: object) -> AcidSequence:
    pad = [AcidStep(on=False)] * (acid.SEQ_LEN - len(steps))
    return AcidSequence(seed=0, params=AcidParams(**kw), steps=steps + pad)  # type: ignore[arg-type]


def test_generate_is_reproducible():
    a = acid.generate(F_SHARP_PHRYGIAN, seed=3)
    b = acid.generate(F_SHARP_PHRYGIAN, seed=3)
    assert a == b
    assert a != acid.generate(F_SHARP_PHRYGIAN, seed=4)


@pytest.mark.parametrize("density", [1, 7, 16])
def test_density_counts_played_steps_per_bar(density):
    seq = acid.generate(AcidParams(density=density), seed=1)
    assert len(seq.steps) == 32
    for bar in (seq.steps[:16], seq.steps[16:]):
        assert sum(s.on for s in bar) == density
        assert bar[0].on


def test_notes_stay_in_scale():
    seq = acid.generate(F_SHARP_PHRYGIAN, seed=5)
    allowed = {(6 + i) % 12 for i in (0, 1, 3, 5, 7, 8, 10)}
    assert all(acid.step_note(seq.params, s) % 12 in allowed for s in seq.steps)


def test_type_widens_intervals():
    def mean_leap(t: int) -> float:
        leaps = []
        for seed in range(30):
            d = [s.degree for s in acid.generate(AcidParams(type=t), seed).steps]
            leaps += [abs(b - a) for a, b in zip(d, d[1:])]
        return sum(leaps) / len(leaps)
    assert mean_leap(1) < mean_leap(16)


def test_octaves_within_bounds():
    p = AcidParams(octave_low=0, octave_high=2)
    for seed in range(10):
        assert all(0 <= s.octave <= 2 for s in acid.generate(p, seed).steps)


def test_locked_layer_kept_others_redrawn():
    first = acid.generate(F_SHARP_PHRYGIAN, seed=1)
    second = acid.generate(F_SHARP_PHRYGIAN, seed=2, previous=first, locks=frozenset({"gate"}))
    assert [(s.on, s.gate) for s in second.steps] == [(s.on, s.gate) for s in first.steps]
    assert [s.degree for s in second.steps] != [s.degree for s in first.steps]
    # une couche non verrouillee ne depend que de la graine
    fresh = acid.generate(F_SHARP_PHRYGIAN, seed=2)
    assert [s.degree for s in second.steps] == [s.degree for s in fresh.steps]


def test_lock_without_previous_raises():
    with pytest.raises(acid.AcidError):
        acid.generate(AcidParams(), seed=0, locks=frozenset({"notes"}))


def test_params_validation():
    with pytest.raises(ValidationError):
        AcidParams(scale="NOPE")
    with pytest.raises(ValidationError):
        AcidParams(octave_low=1, octave_high=0)
    with pytest.raises(ValidationError):
        AcidParams(density=0)


def test_step_note_wraps_degrees_and_octaves():
    p = AcidParams(root=5, scale="AEOLIAN (MINOR)", base_note=36)  # F
    assert acid.step_note(p, AcidStep(degree=0)) == 41
    assert acid.step_note(p, AcidStep(degree=7)) == 53          # tonique une octave au-dessus
    assert acid.step_note(p, AcidStep(degree=-1)) == 39         # Eb sous la tonique
    assert acid.step_note(p, AcidStep(degree=2, octave=1)) == 41 + 3 + 12


def test_accent_velocity_contrast():
    assert acid.step_velocity(AcidParams(accent=0), AcidStep(accent=2)) == 80
    assert acid.step_velocity(AcidParams(accent=100), AcidStep(accent=2)) == 127
    assert acid.step_velocity(AcidParams(accent=100), AcidStep(accent=1)) == 104


@pytest.mark.parametrize("direction,expected", [
    ("forward", [2, 3, 4, 5]),
    ("backward", [5, 4, 3, 2]),
    ("pendulum", [2, 3, 4, 5, 4, 3]),
])
def test_play_order(direction, expected):
    assert acid.play_order(AcidParams(steps=4, offset=2, direction=direction)) == expected


def test_play_order_offset_wraps():
    assert acid.play_order(AcidParams(steps=3, offset=31)) == [31, 0, 1]
    assert acid.play_order(AcidParams(steps=32, offset=4))[:2] == [4, 5]


def test_sequence_of_16_steps_is_padded_to_32():
    steps = [{"degree": i} for i in range(16)]
    seq = AcidSequence.model_validate({"seed": 0, "params": {}, "steps": steps})
    assert [s.degree for s in seq.steps] == list(range(16)) * 2


def _arp(**kw: object) -> list[int]:
    p = AcidParams(mode="arp", scale="AEOLIAN (MINOR)", **kw)  # type: ignore[arg-type]
    return [s.degree for s in acid.generate(p, seed=1).steps]


def test_arp_up_follows_progression_one_chord_per_bar():
    d = _arp(progression=[0, 5], arp="up")
    assert d[:4] == [0, 2, 4, 0]                  # I : tonique, tierce, quinte
    assert d[16:20] == [-2, 0, 2, -2]             # VI pris sous la tonique (degre 5 - 7)


def test_arp_patterns_and_half_bar_chords():
    assert _arp(progression=[0], arp="down")[:3] == [4, 2, 0]
    assert _arp(progression=[0], arp="updown")[:4] == [0, 2, 4, 2]
    d = _arp(progression=[0, 3], chord_steps=8)
    assert d[8:11] == [3, 5, 7] and d[16:19] == [0, 2, 4]
    assert set(_arp(progression=[0], arp="random")) <= {0, 2, 4}


def test_arp_notes_stay_in_scale_and_lock_keeps_rhythm():
    p = AcidParams(mode="arp", root=6, scale="PHRYGIAN")
    first = acid.generate(p, seed=1)
    allowed = {(6 + i) % 12 for i in (0, 1, 3, 5, 7, 8, 10)}
    assert all(acid.step_note(p, s) % 12 in allowed for s in first.steps)
    again = acid.generate(p, seed=2, previous=first, locks=frozenset({"gate"}))
    assert [s.on for s in again.steps] == [s.on for s in first.steps]


def test_progressions_are_known_degrees():
    assert all(all(0 <= d <= 6 for d in prog) for prog in acid.PROGRESSIONS.values())


def test_swing_delays_odd_positions():
    seq = _seq([AcidStep(gate=0), AcidStep(gate=0)], swing=75, tie_mode=False)
    a, b = acid.render_notes(seq)
    assert a.start == 0
    assert b.start == 120 + 60  # 75 % : retard d'une demi double-croche


def test_tie_different_note_overlaps_as_slide():
    seq = _seq([AcidStep(degree=0, gate=2), AcidStep(degree=2, gate=1)])
    a, b = acid.render_notes(seq)
    assert a.slide and a.end == b.start == 120
    events = sorted(acid.note_events(seq, channel=0), key=lambda e: (e[0], e[1]))
    at_120 = [m.type for t, _, m in events if t == 120]
    assert at_120 == ["note_on", "note_off"]  # note_on avant le note_off : legato


def test_tie_same_note_extends():
    seq = _seq([AcidStep(gate=2), AcidStep(gate=1)])
    (n,) = acid.render_notes(seq)
    assert (n.start, n.end) == (0, 120 + 60)


def test_no_tie_when_mode_off():
    seq = _seq([AcidStep(gate=2), AcidStep(gate=1)], tie_mode=False)
    a, b = acid.render_notes(seq)
    assert not a.slide and a.end <= b.start


def test_gate_scales_length_and_same_note_never_overlaps():
    seq = _seq([AcidStep(gate=1), AcidStep(gate=1)], gate=200, tie_mode=False)
    a, b = acid.render_notes(seq)
    assert a.end == b.start == 120  # 0,5 pas x 200 % = 1 pas


def test_write_midi_one_bar(tmp_path: Path):
    seq = acid.generate(F_SHARP_PHRYGIAN, seed=3)
    out = tmp_path / "acid.mid"
    acid.write_midi(seq, out, bpm=145)
    mid = mido.MidiFile(str(out))
    assert mid.ticks_per_beat == 480
    total = sum(m.time for m in mid.tracks[0])
    assert total == 16 * 120
    ons = [m for m in mid.tracks[0] if m.type == "note_on"]
    offs = [m for m in mid.tracks[0] if m.type == "note_off"]
    assert len(ons) == len(offs) == len(acid.render_notes(seq))


def test_cli(tmp_path: Path):
    out = tmp_path / "x.mid"
    assert acid.main(["--root", "F#", "--scale", "PHRYGIAN", "--seed", "3", "-o", str(out)]) == 0
    assert out.exists()

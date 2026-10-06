"""Tests unitaires du draft de bank Digitakt (analyzer/digitakt.py).

Aucun audio reel : features par pas synthetiques.

Lancer (depuis scripts/) :
    python -m pytest tests/test_digitakt.py
    python -m pytest tests/test_digitakt.py::test_build_bank_four_on_floor
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from analyzer.digitakt import (
    StepFeatures,
    active_mask,
    build_bank,
    classify_hats,
    fold_steps,
    grid_line,
    kick_shift,
    median_bpm,
    pattern_bars,
    pick_hits,
    plan_sections,
    render_markdown,
    step_grid,
    write_pattern_midi,
)

SPB = 16


def _four_on_floor(n_bars: int) -> np.ndarray:
    v = np.full(n_bars * SPB, 1.0)
    v[::4] = 10.0
    return v


def test_step_grid_subdivides_beats():
    beats = [0.0, 0.5, 1.0, 1.5, 2.0]
    bounds = step_grid(beats, 4, 16)
    assert len(bounds) == 17
    assert np.isclose(bounds[1], 0.125)
    assert np.isclose(bounds[-1], 2.0)


def test_step_grid_too_short():
    assert step_grid([0.0, 0.5], 4, 16).size == 0


def test_median_bpm():
    beats = list(np.arange(0, 10, 60 / 148))
    assert abs(median_bpm(beats) - 148) < 0.1


def test_pattern_bars_caps_at_128_steps():
    assert pattern_bars(59, 16) == 8
    assert pattern_bars(5, 16) == 4
    assert pattern_bars(1, 16) == 1
    assert pattern_bars(32, 24) == 4  # 8 x 24 = 192 > 128


def test_plan_sections_merges_above_16():
    bar_times = np.arange(0, 41, dtype=float)
    segs = [{"start_s": i * 2, "end_s": i * 2 + 2, "label": "main", "rms_dbfs": -8}
            for i in range(20)]
    sections = plan_sections(segs, bar_times)
    assert len(sections) == 16
    assert sections[0][0] == 0 and sections[-1][1] == 40
    assert all(a[1] == b[0] for a, b in zip(sections, sections[1:]))


def test_plan_sections_fallback_without_structure():
    sections = plan_sections([], np.arange(0, 65, dtype=float))
    assert [(s[0], s[1]) for s in sections] == [(0, 32), (32, 64)]


def test_active_mask_threshold():
    mask = active_mask(np.array([1.0, 0.5, 0.01]))
    assert mask.tolist() == [True, True, False]


def test_fold_steps_averages_modulo():
    values = np.concatenate([np.full(SPB, 1.0), np.full(SPB, 3.0)] * 2)
    folded = fold_steps(values, [0, 1, 2, 3], SPB, 2)
    assert folded.shape == (32,)
    assert np.allclose(folded[:16], 1.0) and np.allclose(folded[16:], 3.0)


def test_pick_hits_four_on_floor_robust_to_outlier():
    pattern = _four_on_floor(2)
    pattern[0] = 100.0  # un pic aberrant ne doit pas masquer les autres kicks
    hits, _ = pick_hits(pattern, 0.5)
    assert hits == list(range(0, 32, 4))


def test_pick_hits_sustained_gives_single_trig():
    hits, _ = pick_hits(np.full(16, 5.0), 0.5)
    assert hits == [0]


def test_kick_shift_phase_within_beat():
    k = np.roll(_four_on_floor(4), 2)
    assert kick_shift(k, SPB) == 2


def test_classify_hats_open_and_closed():
    closed = np.ones(16)
    open_ = np.zeros(16)
    open_[2] = 1.0
    open_[3] = 0.9  # tient au pas suivant → ouvert
    out = classify_hats([0, 2], {4: closed, 5: open_, 6: np.zeros(16)})
    assert out[4] == [0] and out[5] == [2] and out[6] == []


def _features(n_bars: int) -> StepFeatures:
    n = n_bars * SPB
    kick = _four_on_floor(n_bars)
    return StepFeatures(
        step_times=np.linspace(0, n_bars * 2.0, n + 1),
        onset={1: kick},
        energy={1: kick},
        chroma={},
    )


def test_build_bank_four_on_floor():
    segs = [{"start_s": 0, "end_s": 32, "label": "main", "rms_dbfs": -8}]
    bank = build_bank("x", {"artist": "A", "title": "T"}, 120, "4/4", 4,
                      _features(16), segs, from_stems=True)
    assert len(bank.patterns) == 1
    p = bank.patterns[0]
    assert p.bars == 8 and p.steps == 128 and p.repeats == 2.0
    kick = p.tracks[0]
    assert kick.role == "Kick"
    assert [t.step for t in kick.trigs] == list(range(0, 128, 4))
    assert len(p.tracks) == 16
    assert all(1 in ph.active for ph in bank.mutes)


def test_build_bank_drop_adds_fx():
    segs = [{"start_s": 0, "end_s": 16, "label": "breakdown", "rms_dbfs": -16},
            {"start_s": 16, "end_s": 32, "label": "peak", "rms_dbfs": -7}]
    bank = build_bank("x", {}, 120, "4/4", 4, _features(16), segs, from_stems=True)
    fx_drop = bank.patterns[1].tracks[14]
    fx_before = bank.patterns[0].tracks[14]
    assert [t.step for t in fx_drop.trigs] == [0]
    assert len(fx_before.trigs) == 4
    vels = [t.velocity for t in fx_before.trigs]
    assert vels == sorted(vels)  # riser : velocite croissante


def test_render_and_midi(tmp_path: Path):
    segs = [{"start_s": 0, "end_s": 32, "label": "main", "rms_dbfs": -8}]
    bank = build_bank("x", {}, 120, "4/4", 4, _features(16), segs, from_stems=True)
    md = render_markdown(bank)
    assert "Partition de mutes" in md and "01 Kick" in md
    assert grid_line(bank.patterns[0].tracks[0], 16) == "x...x...x...x..."

    import mido

    out = tmp_path / "p01.mid"
    write_pattern_midi(bank.patterns[0], bank.bpm, out)
    notes = [m for m in mido.MidiFile(str(out)).tracks[0] if m.type == "note_on"]
    assert len(notes) == 32
    assert {m.channel for m in notes} == {0}  # track 1 → canal MIDI 1


def test_mute_phrases_restart_at_section_boundary():
    segs = [{"start_s": 0, "end_s": 10, "label": "intro", "rms_dbfs": -8},
            {"start_s": 10, "end_s": 32, "label": "main", "rms_dbfs": -8}]
    bank = build_bank("x", {}, 120, "4/4", 4, _features(16), segs, from_stems=True)
    # section 1 = mesures 0-5, section 2 = 5-16 : phrases a 0, puis 5 et 13
    assert [ph.bar for ph in bank.mutes] == [0, 5, 13]
    assert [ph.pattern_slot for ph in bank.mutes] == [1, 2, 2]

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
    beat_changes,
    build_bank,
    classify_hats,
    detect_sections,
    downbeat_offset,
    fold_steps,
    grid_line,
    kick_shift,
    label_sections,
    median_bpm,
    pattern_bars,
    pick_hits,
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


def _on(n_bars: int, *ranges: tuple[int, int]) -> np.ndarray:
    m = np.zeros(n_bars, dtype=bool)
    for a, b in ranges:
        m[a:b] = True
    return m


def test_detect_sections_cuts_where_tracks_change():
    bar_on = {1: _on(32, (8, 32)), 4: _on(32, (0, 16), (24, 32))}
    parts = detect_sections(bar_on, 32)
    assert [(a, b, sorted(act)) for a, b, act in parts] == [
        (0, 8, [4]), (8, 16, [1, 4]), (16, 24, [1]), (24, 32, [1, 4])]


def test_detect_sections_grid_follows_pickup_bar():
    # tout bascule aux mesures 1, 5, 9 : la grille de 4 demarre a la mesure 1
    bar_on = {1: _on(13, (1, 5), (9, 13)), 4: _on(13, (5, 13))}
    parts = detect_sections(bar_on, 13)
    assert [(a, b) for a, b, _ in parts] == [(0, 1), (1, 5), (5, 9), (9, 13)]


def test_detect_sections_absorbs_single_track_blip():
    bar_on = {1: _on(24, (0, 24)), 4: _on(24, (0, 8), (12, 24))}
    assert [(a, b) for a, b, _ in detect_sections(bar_on, 24)] == [(0, 24)]


def test_detect_sections_caps_at_16():
    bar_on = {i: _on(80, *[(k, k + 4) for k in range(0, 80, 4) if (k // 4) % 5 == i - 1])
              for i in range(1, 6)}
    parts = detect_sections(bar_on, 80)
    assert len(parts) == 16
    assert parts[0][0] == 0 and parts[-1][1] == 80
    assert all(x[1] == y[0] for x, y in zip(parts, parts[1:]))


def test_label_sections_from_content():
    f = frozenset
    parts = [(0, 8, f({4})), (8, 16, f({1, 3, 4, 9})), (16, 24, f({4, 11})),
             (24, 32, f({1, 2, 3, 4, 9})), (32, 40, f({1}))]
    assert [s[2] for s in label_sections(parts)] == [
        "intro", "peak", "breakdown", "peak", "outro"]


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


def _layered(n_bars: int, kick_bars: np.ndarray, hat_bars: np.ndarray) -> StepFeatures:
    """Kick four-on-floor + hats en contretemps, actifs par mesure selon les masques."""
    kick_on = np.repeat(kick_bars, SPB)
    hat_on = np.repeat(hat_bars, SPB)
    kick = np.where(kick_on, _four_on_floor(n_bars), 1e-6)
    hat_pat = np.full(n_bars * SPB, 1.0)
    hat_pat[2::4] = 10.0
    hat = np.where(hat_on, hat_pat, 1e-6)
    return StepFeatures(
        step_times=np.linspace(0, n_bars * 2.0, n_bars * SPB + 1),
        onset={1: kick, 4: hat}, energy={1: kick, 4: hat}, chroma={},
    )


def test_beat_changes_ignores_backbeat_clap():
    clap = np.zeros(32 * SPB)
    clap[4::8] = 10.0  # clap sur 2 et 4
    clap += 1e-6
    assert beat_changes({3: clap}, 4, 32 * 4, 8).sum() == 0


def test_downbeat_offset_from_track_entry():
    # les hats entrent au temps 33 (= 2e temps de la mesure 8) : la vraie
    # mesure demarre un temps apres la grille
    n_bars = 16
    feat = _features(n_bars)
    hat = np.full(n_bars * SPB, 1e-6)
    hat[33 * 4:] = 1.0
    feat.energy[4] = hat
    assert downbeat_offset(feat, 4, SPB) == 1


def test_downbeat_offset_clap_on_two_and_four():
    n_bars = 16
    feat = _features(n_bars)
    clap = np.full(n_bars * SPB, 1e-6)
    clap[0::8] = 10.0  # clap sur les temps 0 et 2 de la grille → la mesure demarre au temps 1 ou 3
    feat.onset[3] = clap
    assert downbeat_offset(feat, 4, SPB) in (1, 3)


def test_build_bank_four_on_floor():
    bank = build_bank("x", {"artist": "A", "title": "T"}, 120, "4/4", 4,
                      _features(16), from_stems=True)
    assert len(bank.patterns) == 1
    p = bank.patterns[0]
    assert p.bars == 8 and p.steps == 128 and p.repeats == 2.0
    kick = p.tracks[0]
    assert kick.role == "Kick"
    assert [t.step for t in kick.trigs] == list(range(0, 128, 4))
    assert len(p.tracks) == 16
    assert all(1 in ph.active for ph in bank.mutes)
    assert len(bank.bar_times_s) == 17 and bank.bar_times_s[1] == 2.0
    assert bank.chain == [1] and bank.sections[0].label == "peak"


def test_build_bank_reuses_slot_for_identical_sections():
    full = np.ones(24, dtype=bool)
    hats = _on(24, (0, 8), (16, 24))
    bank = build_bank("x", {}, 120, "4/4", 4, _layered(24, full, hats), from_stems=True)
    assert [(s.bar, s.bars) for s in bank.sections] == [(0, 8), (8, 8), (16, 8)]
    assert bank.chain == [1, 2, 1]
    assert len(bank.patterns) == 2
    assert '"chain":[1,2,1]' in bank.model_dump_json()


def test_build_bank_drop_adds_fx():
    kick = _on(16, (8, 16))
    bank = build_bank("x", {}, 120, "4/4", 4,
                      _layered(16, kick, np.ones(16, dtype=bool)), from_stems=True)
    assert [s.label for s in bank.sections] == ["intro", "peak"]
    fx_drop = bank.patterns[1].tracks[14]
    fx_before = bank.patterns[0].tracks[14]
    assert [t.step for t in fx_drop.trigs] == [0]
    assert len(fx_before.trigs) == 4
    vels = [t.velocity for t in fx_before.trigs]
    assert vels == sorted(vels)  # riser : velocite croissante


def test_render_and_midi(tmp_path: Path):
    bank = build_bank("x", {}, 120, "4/4", 4, _features(16), from_stems=True)
    md = render_markdown(bank)
    assert "Partition de mutes" in md and "01 Kick" in md and "Chaine : 01" in md
    assert grid_line(bank.patterns[0].tracks[0], 16) == "x...x...x...x..."

    import mido

    out = tmp_path / "p01.mid"
    write_pattern_midi(bank.patterns[0], bank.bpm, out)
    notes = [m for m in mido.MidiFile(str(out)).tracks[0] if m.type == "note_on"]
    assert len(notes) == 32
    assert {m.channel for m in notes} == {0}  # track 1 → canal MIDI 1


def test_mute_phrases_restart_at_section_boundary():
    kick = _on(16, (4, 16))
    bank = build_bank("x", {}, 120, "4/4", 4,
                      _layered(16, kick, np.ones(16, dtype=bool)), from_stems=True)
    # section 1 = mesures 0-4, section 2 = 4-16 : phrases a 0, puis 4 et 12
    assert [ph.bar for ph in bank.mutes] == [0, 4, 12]
    assert [ph.pattern_slot for ph in bank.mutes] == [1, 2, 2]

"""Tests de l'analyse harmonique (scripts/analyzer/harmony.py), sur profils synthetiques.

Lancer :
    python -m pytest tests/test_harmony.py
    python -m pytest tests/test_harmony.py::test_detect_scale_aeolian_from_bass_tonic
"""
from __future__ import annotations

import numpy as np

from analyzer import harmony


def _profile(notes: dict[int, float]) -> np.ndarray:
    p = np.full(12, 0.02)
    for n, w in notes.items():
        p[n] = w
    return p


# F mineur naturel : F G Ab Bb C Db Eb, fondamentale F appuyee
F_MINOR = _profile({5: 1.0, 7: 0.5, 8: 0.7, 10: 0.5, 0: 0.8, 1: 0.4, 3: 0.5})


def test_detect_scale_aeolian_from_bass_tonic():
    bass = _profile({5: 1.0, 0: 0.3})
    res = harmony.detect_scale(F_MINOR, bass)
    assert (res.root_name, res.scale) == ("F", "AEOLIAN (MINOR)")
    assert res.label == "F mineur (éolien)"
    assert res.notes == ["F", "G", "G#", "A#", "C", "C#", "D#"]
    assert res.margin > 0 and len(res.candidates) == 4


def test_relative_major_wins_when_bass_sits_on_its_tonic():
    # memes notes que F mineur, mais tout repose sur Ab : Ab majeur
    prof = _profile({8: 1.0, 10: 0.5, 0: 0.7, 1: 0.5, 3: 0.8, 5: 0.5, 7: 0.4})
    res = harmony.detect_scale(prof, _profile({8: 1.0}))
    assert (res.root_name, res.scale) == ("G#", "IONIAN (MAJOR)")


def test_pentatonic_minor_when_only_five_notes():
    prof = _profile({9: 1.0, 0: 0.7, 2: 0.6, 4: 0.8, 7: 0.6})   # A C D E G
    res = harmony.detect_scale(prof, _profile({9: 1.0}))
    assert (res.root_name, res.scale) == ("A", "PENTATONIC MINOR")


def test_detect_chord_triads_and_power_chord():
    assert harmony.detect_chord(_profile({5: 1.0, 8: 0.8, 0: 0.9}))[0] == "Fm"
    assert harmony.detect_chord(_profile({0: 1.0, 4: 0.8, 7: 0.9}))[0] == "C"
    assert harmony.detect_chord(_profile({2: 1.0, 9: 0.9}))[0] == "D5"
    assert harmony.detect_chord(np.zeros(12))[0] == "N"


def test_bass_decides_between_sus2_and_sus4():
    # C D G = Csus2 = Gsus4 : la basse sur G tranche
    chroma = _profile({0: 0.9, 2: 0.9, 7: 0.9})
    assert harmony.detect_chord(chroma, _profile({7: 1.0}))[0] == "Gsus4"
    assert harmony.detect_chord(chroma, _profile({0: 1.0}))[0] == "Csus2"


def test_bar_chords_marks_silent_bars_and_progression_dedupes():
    times = np.arange(0, 8, 0.5)                      # 16 trames, 2 s par mesure
    chroma = np.zeros((12, 16))
    chroma[[5, 8, 0], 0:4] = 1.0                      # mesure 0 : Fm
    chroma[[5, 8, 0], 4:8] = 1.0                      # mesure 1 : Fm
    chroma[[1, 5, 8], 8:12] = 1.0                     # mesure 2 : Db
    # mesure 3 : silence
    chords = harmony.bar_chords(chroma, times, [0.0, 2.0, 4.0, 6.0, 8.0])
    assert [c.label for c in chords] == ["Fm", "Fm", "C#", "N"]
    prog = harmony.progression(chords, [("intro", 0.0, 4.0), ("drop", 4.0, 8.0)])
    assert [(p.label, p.chords) for p in prog] == [("intro", ["Fm"]), ("drop", ["C#"])]


def test_keyboard_setup_uses_dt2_names():
    res = harmony.detect_scale(F_MINOR, _profile({5: 1.0}))
    assert harmony.keyboard_setup(res) == "KB SCALE = AEOLIAN (MINOR), ROOT NOTE = F"


def test_peak_profile_ignores_flat_noise_floor():
    chroma = np.full((12, 4), 0.5)
    chroma[[5, 0, 8], :] = 1.0          # F C Ab dominent un plancher plat
    prof = harmony.peak_profile(chroma)
    assert set(np.flatnonzero(prof)) == {0, 5, 8}
    assert harmony.peak_profile(np.zeros((12, 0))).tolist() == [0.0] * 12


def test_low_margin_flags_uncertain_scale():
    # notes de C majeur, C et A (relatif mineur) egalement appuyes : fondamentale ambigue
    ambiguous = _profile({0: 1.0, 2: 0.5, 4: 0.6, 5: 0.5, 7: 0.6, 9: 1.0, 11: 0.4})
    assert harmony.detect_scale(ambiguous).uncertain
    assert not harmony.detect_scale(F_MINOR, _profile({5: 1.0})).uncertain

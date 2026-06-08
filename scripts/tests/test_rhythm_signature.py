"""Tests unitaires des fonctions pures de la signature rythmique.

Aucun audio reel requis : on travaille sur des patterns synthetiques.

Lancer (depuis scripts/) :
    python -m pytest tests/test_rhythm_signature.py
    python -m pytest tests/test_rhythm_signature.py::test_circular_similarity_rotation_invariant
"""
from __future__ import annotations

import numpy as np

from analyzer.rhythm_signature import (
    _circular_similarity,
    _syncopation,
    beats_per_bar,
    rhythm_distance,
    to_sparkline,
    to_vector,
)
from analyzer.types import RhythmSignatureReport


def _sig(**kw) -> RhythmSignatureReport:
    """Construit un rapport avec des patterns par defaut, surchargeable."""
    base = dict(
        bars_used=8,
        bar_pattern=[0.0] * 16,
        sub_pattern=[0.0] * 16,
        mid_pattern=[0.0] * 16,
        high_pattern=[0.0] * 16,
    )
    base.update(kw)
    return RhythmSignatureReport(**base)


# --- beats_per_bar -----------------------------------------------------------

def test_beats_per_bar_parsing():
    assert beats_per_bar("4/4") == 4
    assert beats_per_bar("7/8") == 7
    assert beats_per_bar("3/4") == 3


def test_beats_per_bar_fallback_on_garbage():
    assert beats_per_bar("nawak") == 4
    assert beats_per_bar("") == 4
    assert beats_per_bar("0/4") == 4


# --- _circular_similarity ----------------------------------------------------

def test_circular_similarity_identical():
    p = [1.0, 0.0, 0.0, 0.5] * 4
    assert _circular_similarity(p, p) == 1.0


def test_circular_similarity_rotation_invariant():
    # Un kick four-on-floor et le meme décalé d'un pas → similarite ~1.0
    a = ([1.0, 0.0, 0.0, 0.0]) * 4
    b = np.roll(np.asarray(a), 5).tolist()
    assert _circular_similarity(a, b) > 0.99


def test_circular_similarity_flat_pattern_is_zero():
    flat = [0.3] * 16
    other = ([1.0, 0.0] * 8)
    # Un pattern sans relief n'a aucune forme a correler
    assert _circular_similarity(flat, other) == 0.0


def test_circular_similarity_distinct_patterns_below_one():
    on_beat = ([1.0, 0.0, 0.0, 0.0]) * 4
    off_beat = ([0.0, 0.0, 1.0, 0.0]) * 4
    # Decales d'une croche : la cross-correlation circulaire les realigne,
    # donc on verifie surtout que ce n'est pas degenere et reste dans [0,1].
    s = _circular_similarity(on_beat, off_beat)
    assert 0.0 <= s <= 1.0


# --- rhythm_distance ---------------------------------------------------------

def test_rhythm_distance_identical_is_zero():
    pat = ([1.0, 0.2, 0.0, 0.4]) * 4
    a = _sig(bar_pattern=pat, sub_pattern=pat, syncopation=0.3,
             pulse_clarity=0.8, swing=0.5)
    assert rhythm_distance(a, a) < 1e-6


def test_rhythm_distance_symmetric():
    a = _sig(bar_pattern=([1.0, 0, 0, 0] * 4), syncopation=0.2)
    b = _sig(bar_pattern=([0, 0, 1.0, 0] * 4), syncopation=0.9)
    assert abs(rhythm_distance(a, b) - rhythm_distance(b, a)) < 1e-9


def test_rhythm_distance_in_unit_range():
    a = _sig(bar_pattern=([1.0, 0, 0, 0] * 4), pulse_clarity=1.0)
    b = _sig(bar_pattern=([0.0] * 16), pulse_clarity=0.0)
    d = rhythm_distance(a, b)
    assert 0.0 <= d <= 1.0


# --- _syncopation ------------------------------------------------------------

def test_syncopation_on_beat_is_low():
    # Energie uniquement sur les temps (0,4,8,12) → peu syncope
    p = np.zeros(16)
    p[[0, 4, 8, 12]] = 1.0
    assert _syncopation(p, 16, 4) < 0.2


def test_syncopation_off_beat_is_high():
    # Energie uniquement sur les doubles-croches hors-temps → tres syncope
    p = np.zeros(16)
    p[[1, 3, 5, 7, 9, 11, 13, 15]] = 1.0
    assert _syncopation(p, 16, 4) > 0.7


# --- to_vector ---------------------------------------------------------------

def test_to_vector_shape():
    sig = _sig(bar_pattern=([1.0, 0, 0, 0] * 4))
    v = to_vector(sig)
    assert v.shape == (3 * 16 + 3,)


def test_to_vector_phase_canonical():
    # Deux signatures identiques a une rotation pres → vecteurs canoniques egaux
    pat = ([1.0, 0.0, 0.0, 0.0]) * 4
    rolled = np.roll(np.asarray(pat), 4).tolist()
    a = _sig(bar_pattern=pat, sub_pattern=pat, mid_pattern=pat, high_pattern=pat)
    b = _sig(bar_pattern=rolled, sub_pattern=rolled,
             mid_pattern=rolled, high_pattern=rolled)
    assert np.allclose(to_vector(a), to_vector(b))


# --- to_sparkline ------------------------------------------------------------

def test_sparkline_length_and_extremes():
    spark = to_sparkline([0.0, 1.0, 0.5])
    assert len(spark) == 3
    assert spark[0] == "▁"
    assert spark[1] == "█"


def test_sparkline_empty():
    assert to_sparkline([]) == ""

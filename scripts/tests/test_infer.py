"""Tests de la fenetre de tempo par style (analyzer/infer.py, STYLE_BPM_WINDOWS).

Lancer (depuis scripts/) :
    python -m pytest tests/test_infer.py
"""
from __future__ import annotations

import pytest

from analyzer.infer import STYLE_BPM_WINDOWS, fold_bpm, style_window


def test_fenetres_sans_ambiguite_d_octave():
    for _kws, lo, hi in STYLE_BPM_WINDOWS:
        assert hi / lo < 2


@pytest.mark.parametrize(("texts", "expected"), [
    (["shatta"], ("shatta", 85, 115)),
    (["Mental Tekno live"], ("tekno", 160, 210)),  # 1er mot-cle de la table
    (["", "Drum & Bass"], ("drum_bass", 160, 180)),
    (["R&B & Soul"], ("soul", 60, 110)),  # deux mots-cles, meme fenetre
    (["Roots Reggae"], ("reggae", 60, 95)),
    (["dub"], ("dub", 60, 95)),
    (["dubstep"], ("dubstep", 135, 150)),  # pas confondu avec dub
    (["janes_fifty", "Dancehall Dubstep remix", "techno"], ("techno", 125, 150)),
    (["mariage", "Alternative Rock"], None),
])
def test_style_window(texts: list[str], expected: tuple[str, float, float] | None):
    assert style_window(texts) == expected


@pytest.mark.parametrize(("bpm", "lo", "hi", "expected"), [
    (198.8, 85, 115, 99.4),   # Shatta Mad
    (72.0, 135, 150, 144.0),  # dubstep detecte a mi-tempo
    (99.0, 160, 210, 198.0),  # tribe detectee a mi-tempo
    (180.0, 160, 210, 180.0),
    (120.0, 135, 150, None),  # aucune octave plausible
    (0.0, 60, 95, None),
])
def test_fold_bpm(bpm: float, lo: float, hi: float, expected: float | None):
    assert fold_bpm(bpm, lo, hi) == expected

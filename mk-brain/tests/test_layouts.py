from __future__ import annotations

import pytest

from mk_brain.config import Config, VelocityConfig
from mk_brain.layouts import LayoutError, pad_color, pad_note, velocity


def test_chromatic_and_scales(cfg: Config) -> None:
    b, c, h = cfg.layouts[0], cfg.layouts[1], cfg.layouts[6]
    assert [pad_note(b, p) for p in (1, 16)] == [60, 75]
    # éolien, fiche controleur-maschine : 60 62 63 65 67 68 70 72…
    assert [pad_note(c, p) for p in range(1, 9)] == [60, 62, 63, 65, 67, 68, 70, 72]
    assert pad_note(c, 16) == 86  # 2 octaves (14 pads) puis 84, 86
    assert [pad_note(h, p) for p in range(1, 8)] == [60, 63, 65, 67, 70, 72, 75]


def test_pad_out_of_range(cfg: Config) -> None:
    with pytest.raises(LayoutError):
        pad_note(cfg.layouts[0], 17)


def test_colors_by_role(cfg: Config) -> None:
    c, b, g = cfg.layouts[1], cfg.layouts[0], cfg.layouts[5]
    assert pad_color(cfg, c, 1) == cfg.roles.tonique
    assert pad_color(cfg, c, 3) == cfg.roles.tierce  # 63
    assert pad_color(cfg, c, 5) == cfg.roles.quinte  # 67
    assert pad_color(cfg, c, 2) == cfg.families["gamme"]
    assert pad_color(cfg, b, 1) == cfg.roles.tonique
    assert pad_color(cfg, b, 4) == cfg.families["chromatique"]  # 63 : pas de tierce en chromatique
    assert pad_color(cfg, g, 3) == cfg.roles.tierce  # tierce majeure 64
    assert pad_color(cfg, g, 2) == cfg.families["gamme"]  # plus de famille majeure


def test_velocity_curve() -> None:
    v = VelocityConfig(threshold=200, full_scale=2500, gamma=1.0, min=1, max=127)
    assert velocity(v, 200) == 1
    assert velocity(v, 2500) == 127
    assert velocity(v, 4000) == 127
    assert velocity(v, 1350) == 64  # 1 + 126 × (1150 / 2300) = 1 + 63
    soft = VelocityConfig(gamma=0.6)
    assert velocity(soft, 1350) > 64


def test_describe_note(cfg: Config) -> None:
    from mk_brain.layouts import describe_note, note_name

    assert note_name(60) == "C5"  # convention Elektron
    assert describe_note(cfg.layouts[1], 3, 63) == "pad 3 -> b3 (D#5, 63)"


# --- slice 5.D : dispositions calées sur une banque ---------------------------


def test_chromatic_follows_bank_scale(cfg: Config) -> None:
    from mk_brain.layouts import for_bank

    chroma = for_bank(cfg.layouts[0], cfg.scale("eolien"), 10)  # la# mineur
    from mk_brain.layouts import in_scale

    assert pad_note(chroma, 1) == 70  # A#5 : tonique dans l'octave de C5 (60 = C5)
    assert pad_color(cfg, chroma, 1) == cfg.roles.tonique
    white = cfg.families["chromatique"]
    assert [pad_color(cfg, chroma, p) for p in (2, 4, 8)] == [white] * 3  # seule la tonique
    assert [in_scale(chroma, p) for p in (2, 3, 4, 5, 8)] == [False, True, True, False, True]
    assert in_scale(cfg.layouts[0], 2)  # sans banque : tout dans la gamme


def test_scale_layout_moves_to_tonic(cfg: Config) -> None:
    from mk_brain.layouts import for_bank

    phryg = for_bank(cfg.layouts[2], cfg.scale("phrygien"), 5)  # fa phrygien
    assert [pad_note(phryg, p) for p in (1, 2, 8)] == [65, 66, 77]

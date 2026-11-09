from __future__ import annotations

import pytest

from mk_brain.config import Config, VelocityConfig
from mk_brain.layouts import LayoutError, pad_color, pad_note, velocity


def test_rhythm_pad_n_is_track_n(cfg: Config) -> None:
    a = cfg.layouts[0]
    assert [pad_note(a, p) for p in range(1, 17)] == list(range(16))


def test_chromatic_and_scales(cfg: Config) -> None:
    b, c, h = cfg.layouts[1], cfg.layouts[2], cfg.layouts[7]
    assert [pad_note(b, p) for p in (1, 16)] == [60, 75]
    # éolien, fiche controleur-maschine : 60 62 63 65 67 68 70 72…
    assert [pad_note(c, p) for p in range(1, 9)] == [60, 62, 63, 65, 67, 68, 70, 72]
    assert pad_note(c, 16) == 86  # 2 octaves (14 pads) puis 84, 86
    assert [pad_note(h, p) for p in range(1, 8)] == [60, 63, 65, 67, 70, 72, 75]


def test_pad_out_of_range(cfg: Config) -> None:
    with pytest.raises(LayoutError):
        pad_note(cfg.layouts[0], 17)


def test_colors_by_role(cfg: Config) -> None:
    c, b, g = cfg.layouts[2], cfg.layouts[1], cfg.layouts[6]
    assert pad_color(cfg, c, 1) == cfg.roles.tonique
    assert pad_color(cfg, c, 3) == cfg.roles.tierce  # 63
    assert pad_color(cfg, c, 5) == cfg.roles.quinte  # 67
    assert pad_color(cfg, c, 2) == cfg.families["mineur"]
    assert pad_color(cfg, b, 2) == cfg.roles.hors_gamme  # 61 en chromatique
    assert pad_color(cfg, g, 3) == cfg.roles.tierce  # tierce majeure 64
    assert pad_color(cfg, g, 2) == cfg.families["majeur"]
    assert pad_color(cfg, cfg.layouts[0], 1) == cfg.track_colors[1]


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
    assert describe_note(cfg.layouts[0], 9, 8) == "pad 9 -> track 9"
    assert describe_note(cfg.layouts[2], 3, 63) == "pad 3 -> b3 (D#5, 63)"


# --- slice 5.D : dispositions calées sur une banque ---------------------------


def test_chromatic_follows_bank_scale(cfg: Config) -> None:
    from mk_brain.layouts import for_bank

    chroma = for_bank(cfg.layouts[1], cfg.scale("eolien"), 10)  # la# mineur
    assert pad_note(chroma, 1) == 70  # A#4 : tonique dans l'octave de C5
    assert pad_color(cfg, chroma, 1) == cfg.roles.tonique
    assert pad_color(cfg, chroma, 2) == cfg.roles.hors_gamme  # B : seconde mineure
    assert pad_color(cfg, chroma, 4) == cfg.roles.tierce  # C# : tierce mineure
    assert pad_color(cfg, chroma, 5) == cfg.roles.hors_gamme  # D : tierce majeure, hors gamme
    assert pad_color(cfg, chroma, 8) == cfg.roles.quinte  # F
    assert pad_color(cfg, chroma, 3) == cfg.families["mineur"]  # C : seconde


def test_scale_layout_moves_to_tonic_rhythm_untouched(cfg: Config) -> None:
    from mk_brain.layouts import for_bank

    phryg = for_bank(cfg.layouts[3], cfg.scale("phrygien"), 5)  # fa phrygien
    assert [pad_note(phryg, p) for p in (1, 2, 8)] == [65, 66, 77]
    assert for_bank(cfg.layouts[0], cfg.scale("eolien"), 5) == cfg.layouts[0]

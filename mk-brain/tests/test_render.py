from __future__ import annotations

from PIL import Image
from test_engine import MS, PAD1, SECOND, advance, running_clock

from mk_brain import render
from mk_brain.config import Config
from mk_brain.display import big_text_image, image_to_frame
from mk_brain.engine import Engine
from mk_brain.hid_mk2 import ButtonEvent, EncoderEvent, PadEvent


def same(a: Image.Image, b: Image.Image) -> bool:
    return image_to_frame(a) == image_to_frame(b)


def at_bar(cfg: Config, bar: int) -> Engine:
    """Transport lancé, mesure `bar` de la phrase, temps 1."""
    eng = Engine(cfg, running_clock(1))
    eng.on_start()
    advance(eng, 1, (bar - 1) * 96 + 1)
    return eng


def test_right_shows_faders_by_default(cfg: Config) -> None:
    eng = at_bar(cfg, 3)
    img = render.right(eng, 0)
    assert not same(img, big_text_image("-1", size=60)) and img.getbbox() is not None


def test_countdown_overlay_before_cap(cfg: Config) -> None:
    eng = at_bar(cfg, 15)  # cap 16 : -2
    assert same(render.right(eng, 0), big_text_image("-2", size=60))


def test_repeat_division_beats_countdown(cfg: Config) -> None:
    eng = at_bar(cfg, 16)
    eng.handle(ButtonEvent("NOTE_REPEAT", True), 0)
    assert same(render.right(eng, 0), big_text_image(eng.division, size=44))


def test_pad_hit_overlay_lasts_one_second(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.handle(PadEvent(PAD1, True, 2500), 0)
    eng.tick(3 * MS)
    assert same(render.right(eng, 3 * MS), big_text_image("T01 127", size=32))
    assert not same(render.right(eng, 3 * MS + SECOND), big_text_image("T01 127", size=32))


def test_touched_column_is_inverted(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.handle(EncoderEvent(3, 4, 0), 0)
    img = render.right(eng, 0)
    assert img.getpixel((2 * render.COL + 1, 13))  # colonne 3 : fond allumé
    assert not img.getpixel((3 * render.COL + 1, 13))
    assert not render.right(eng, SECOND).getpixel((2 * render.COL + 1, 13))


def test_mode_proposal_has_top_priority(cfg: Config) -> None:
    eng = at_bar(cfg, 15)
    eng.modes.pending = "design"
    assert not same(render.right(eng, 0), big_text_image("-2", size=60))


def test_live_left_tail_inverts_bar(cfg: Config) -> None:
    assert not render.live_left(at_bar(cfg, 20)).getpixel((250, 41))
    assert render.live_left(at_bar(cfg, 30)).getpixel((250, 41))  # 4 dernières mesures


def test_live_left_stopped_and_warning(cfg: Config) -> None:
    eng = Engine(cfg)
    assert not same(render.live_left(eng), render.live_left(eng, "pas de clock"))

from __future__ import annotations

from test_engine import MS, PAD1, SECOND, advance, design, running_clock

from mk_brain import render
from mk_brain.config import Config
from mk_brain.display import HEIGHT, WIDTH
from mk_brain.engine import Engine
from mk_brain.hid_mk2 import ButtonEvent, EncoderEvent, PadEvent

BAND_PIXEL = (WIDTH - 2, 2)  # coin du bandeau droit, hors texte


def at_bar(cfg: Config, bar: int) -> Engine:
    """Transport lancé, mesure `bar` de la phrase."""
    eng = Engine(cfg, running_clock(1))
    eng.on_start()
    advance(eng, 1, (bar - 1) * 96 + 10)
    return eng


def test_countdown_inverts_right_band(cfg: Config) -> None:
    assert not render.right(at_bar(cfg, 14), 0).getpixel(BAND_PIXEL)
    assert render.right(at_bar(cfg, 15), 0).getpixel(BAND_PIXEL)  # cap 16 : -2


def test_tail_inverts_progress_bar(cfg: Config) -> None:
    probe = (1, 25)  # à gauche de la barre de progression
    assert not render.right(at_bar(cfg, 20), 0).getpixel(probe)
    assert render.right(at_bar(cfg, 29), 0).getpixel(probe)  # 4 dernières mesures


def test_repeat_shows_divisions_under_display_buttons(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.handle(ButtonEvent("NOTE_REPEAT", True), 0)
    assert eng.division == "1/16"  # 4e division : 4e case du bandeau gauche, inversée
    img = render.left(eng, 0)
    assert img.getpixel((3 * render.COL + 1, 1)) and not img.getpixel((1, 1))


def test_touched_column_is_inverted_above_its_encoder(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.handle(EncoderEvent(6, 4, 0), 0)  # encodeur 6 : 2e colonne de l'écran droit
    probe = (render.COL + 1, render.BAND + 2)
    assert render.right(eng, 0).getpixel(probe)
    assert not render.left(eng, 0).getpixel(probe)
    assert not render.right(eng, SECOND).getpixel(probe)


def test_pad_hit_shown_in_design_only(cfg: Config) -> None:
    live = Engine(cfg)
    before = render.left(live, 0).tobytes()
    live.handle(PadEvent(PAD1, True, 2500), 0)
    live.tick(3 * MS)
    assert render.left(live, 3 * MS).tobytes() == before  # live : les LED suffisent
    eng = design(cfg)
    before = render.left(eng, 0).tobytes()
    eng.handle(PadEvent(PAD1, True, 2500), 0)
    eng.tick(3 * MS)
    assert render.left(eng, 3 * MS).tobytes() != before
    assert render.left(eng, 3 * MS + SECOND).tobytes() == before


def test_mute_strip_open_muted_and_selected(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.faders.muted[3] = True
    img = render.left(eng, 0)
    cell = WIDTH // 16
    assert img.getpixel((cell // 2, 32))  # track 1 ouverte : case pleine
    assert not img.getpixel((2 * cell + cell // 2, 32))  # track 3 mutée : case vide
    assert img.getpixel((cell // 2, 37))  # track 1 sélectionnée : soulignée
    assert not img.getpixel((cell + cell // 2, 37))


def test_design_left_is_framed(cfg: Config) -> None:
    corner = (0, HEIGHT - 1)
    assert not render.left(Engine(cfg), 0).getpixel(corner)
    assert render.left(design(cfg), 0).getpixel(corner)


def test_mode_proposal_takes_right_screen(cfg: Config) -> None:
    eng = at_bar(cfg, 15)
    eng.modes.pending = "design"
    assert not render.right(eng, 0).getpixel(BAND_PIXEL)


def test_track_code_shown_next_to_track(cfg: Config) -> None:
    assert cfg.track_names[1] == "BD"  # grille de la doctrine §1
    with_name = render.left(Engine(cfg), 0).tobytes()
    bare = cfg.model_copy(update={"track_names": {}})
    assert render.left(Engine(bare), 0).tobytes() != with_name

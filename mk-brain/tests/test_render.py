from __future__ import annotations

from test_engine import MS, PAD1, SECOND, advance, design, running_clock

from mk_brain import render
from mk_brain.config import Config
from mk_brain.display import HEIGHT, WIDTH
from mk_brain.engine import Engine
from mk_brain.hid_mk2 import ButtonEvent, EncoderEvent, PadEvent
from mk_brain.project import Project

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


def test_pad_hit_shown_in_both_layouts(cfg: Config) -> None:
    mpc = Engine(cfg)
    before = render.left(mpc, 0).tobytes()
    mpc.handle(PadEvent(PAD1, True, 2500), 0)
    mpc.tick(3 * MS)
    assert render.left(mpc, 3 * MS).tobytes() != before  # MPC : label, track, tranche
    assert render.left(mpc, 3 * MS + SECOND).tobytes() == before  # retombé sur les mutes
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
    x0, cell = render.TAG_W, (WIDTH - render.TAG_W) // 16  # à droite de l'étiquette du mode
    assert img.getpixel((x0 + cell // 2, 32))  # track 1 ouverte : case pleine
    assert not img.getpixel((x0 + 2 * cell + cell // 2, 32))  # track 3 mutée : case vide
    assert img.getpixel((x0 + cell // 2, 37))  # track 1 sélectionnée : soulignée
    assert not img.getpixel((x0 + cell + cell // 2, 37))


def test_mode_tag_always_shown(cfg: Config) -> None:
    """MPC, KEYS ou SOLO en bas à gauche, même NOTE REPEAT tenu."""
    eng = Engine(cfg)
    tag = (2, render.TAG_TOP, render.TAG_W - 4, render.BAND - 3)
    mpc = render.left(eng, 0).crop(tag).tobytes()
    eng.handle(ButtonEvent("SOLO", True), 0)
    solo = render.left(eng, 0).crop(tag).tobytes()
    eng.handle(ButtonEvent("NOTE_REPEAT", True), 0)
    assert render.left(eng, 0).crop(tag).tobytes() == solo != mpc
    eng.handle(ButtonEvent("NOTE_REPEAT", False), 0)
    eng.handle(ButtonEvent("PAD_MODE", True), 0)  # sort de SOLO, toujours en MPC
    assert eng.mode_name == "MPC" and render.left(eng, 0).crop(tag).tobytes() == mpc


def test_design_left_is_framed(cfg: Config) -> None:
    corner = (0, HEIGHT - 1)
    assert not render.left(Engine(cfg), 0).getpixel(corner)
    assert render.left(design(cfg), 0).getpixel(corner)


def test_track_code_shown_next_to_track(cfg: Config) -> None:
    assert cfg.track_names[1] == "BD"  # grille de la doctrine §1
    with_name = render.left(Engine(cfg), 0).tobytes()
    bare = cfg.model_copy(update={"track_names": {}})
    assert render.left(Engine(bare), 0).tobytes() != with_name


# --- slice 5.D : menu du design -----------------------------------------------


def test_keyboard_uses_mpc_bands_with_frame(cfg: Config, project: Project) -> None:
    """Slice 9 : le clavier reprend les bandeaux du MPC ; seul le cadre les distingue."""
    mpc = Engine(cfg, project=project)
    kbd = design(cfg, project=project)
    left_mpc, left_kbd = render.left(mpc, 0), render.left(kbd, 0)
    assert left_kbd.getpixel((0, 0)) and not left_mpc.getpixel((0, 0))  # cadre
    inner = (render.TAG_W, 1, render.WIDTH - 1, render.BAND)  # hors étiquette du mode
    assert left_kbd.crop(inner).tobytes() == left_mpc.crop(inner).tobytes()
    assert render.right(kbd, 0).tobytes() == render.right(mpc, 0).tobytes()


def test_design_hit_shows_note_and_degree(cfg: Config, project: Project) -> None:
    from test_engine import btn, press

    from mk_brain.layouts import degree_name, flat_note

    eng = design(cfg, project=project)
    btn(eng, "GROUP_E")
    eng.group = 0  # chromatique (surcharge de la disposition phrygienne)
    assert (flat_note(70), degree_name(eng.layout, 73)) == ("Bb5", "minor 3rd")
    assert degree_name(eng.layout, 72) == "2nd, out of scale"
    quiet = render.left(eng, 0).tobytes()
    press(eng, 0, pressure=600)
    assert render.left(eng, 10 * MS).tobytes() != quiet  # bandeau de frappe
    assert render.left(eng, 2 * SECOND).tobytes() == quiet  # retombé sur les mutes


def test_ascii_text_strips_accents() -> None:
    assert render.ascii_text("Cœur du set, ça s'ouvre, bémol") == "Coeur du set, ca s'ouvre, bemol"


def test_live_right_shows_tonic_then_announce_for_two_seconds(
    cfg: Config, project: Project
) -> None:
    eng = Engine(cfg, project=project)
    plain = render.right(eng, 0).tobytes()
    eng.on_program_change(4 * 16)  # E01 : E-TRIBE annoncée
    eng.tick(0)
    announced = render.right(eng, 10 * MS).tobytes()
    assert announced != plain
    after = render.right(eng, 3 * SECOND).tobytes()
    assert after not in (plain, announced)  # tonique et mode en haut à droite


def test_selection_takes_both_screens(cfg: Config, project: Project) -> None:
    from test_engine import _catalog

    eng = Engine(cfg, catalog=_catalog(project))
    left, right = render.left(eng, 0).tobytes(), render.right(eng, 0).tobytes()
    eng.open_selection()
    assert render.left(eng, 0).tobytes() != left
    assert render.right(eng, 0).tobytes() != right


def test_selection_shows_sync_status(cfg: Config, project: Project) -> None:
    from test_engine import _catalog

    eng = Engine(cfg, catalog=_catalog(project))
    eng.open_selection()
    assert eng.selector is not None
    plain = render.left(eng, 0).tobytes()
    eng.selector.sync = "sync a1b2c3d"
    assert render.left(eng, 0).tobytes() != plain  # statut en haut à droite

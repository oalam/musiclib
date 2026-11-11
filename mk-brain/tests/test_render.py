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
    eng.handle(
        EncoderEvent(6, cfg.encoders.raw_per_step, 0), 0
    )  # encodeur 6 : 2e colonne de l'écran droit
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


def _cell(track: int) -> int:
    """Abscisse du centre de la case de mute de `track`."""
    return render._mute_x0(track) + 5


def test_mute_strip_open_muted_and_selected(cfg: Config) -> None:
    eng = Engine(cfg)
    eng.faders.muted[3] = True
    img = render.left(eng, 0)
    mid, under = render.MUTE_TOP + 4, render.MUTE_BOTTOM + 2
    assert img.getpixel((_cell(1), mid))  # track 1 ouverte : case pleine
    assert not img.getpixel((_cell(3), mid))  # track 3 mutée : case vide
    assert img.getpixel((_cell(1), under))  # track 1 sélectionnée : soulignée
    assert not img.getpixel((_cell(2), under))


def test_mute_strip_marks_playing_sixteenth(cfg: Config) -> None:
    """Carré intérieur, en inverse de sa case, sur la double croche en cours."""
    mid = render.MUTE_TOP + 4
    eng = at_bar(cfg, 3)  # 10 ticks dans la mesure : 2e double croche
    eng.faders.muted[3] = True
    img = render.left(eng, 0)
    assert not img.getpixel((_cell(2), mid)) and img.getpixel((_cell(1), mid))
    advance(eng, 2 * 96 + 10, 2 * 96 + 16)  # 3e double croche, case mutée
    assert render.left(eng, 0).getpixel((_cell(3), mid))
    assert render.left(Engine(cfg), 0).getpixel((_cell(2), mid))  # à l'arrêt : rien


def test_mute_strip_dotted_line_between_beats(cfg: Config) -> None:
    """Pointillé vertical entre les cases 4/5, 8/9 et 12/13, à 1 px de chaque case,
    dépassant de la rangée ; rien entre les autres cases."""
    img = render.left(Engine(cfg), 0)
    top, bottom = render.BEAT_LINE
    for track in (5, 9, 13):
        x = render._mute_x0(track) - 2
        column = [bool(img.getpixel((x, y))) for y in range(top, bottom + 1)]
        assert column == [i % 2 == 0 for i in range(len(column))]
        assert not img.getpixel((x - 1, render.MUTE_TOP + 4))
        assert not img.getpixel((x + 1, render.MUTE_TOP + 4))
    for track in (2, 6, 16):
        assert not img.getpixel((render._mute_x0(track) - 2, top))
    assert render._mute_x0(16) + 10 < WIDTH


def test_mode_tag_always_shown(cfg: Config) -> None:
    """MPC, KEYS ou SOLO en haut à droite de l'écran droit ; NOTE REPEAT tenu : sous
    les divisions."""
    eng = Engine(cfg)
    mpc = render.right(eng, 0).crop(render.TAG_BOX).tobytes()
    eng.handle(ButtonEvent("SOLO", True), 0)
    solo = render.right(eng, 0).crop(render.TAG_BOX).tobytes()
    assert solo != mpc
    eng.handle(ButtonEvent("NOTE_REPEAT", True), 0)
    held = render.right(eng, 0).crop(render.TAG_BOX_REPEAT)
    assert held.getpixel((1, 1)) and held.tobytes() != mpc
    eng.handle(ButtonEvent("NOTE_REPEAT", False), 0)
    eng.handle(ButtonEvent("PAD_MODE", True), 0)  # sort de SOLO, toujours en MPC
    assert eng.mode_name == "MPC"
    assert render.right(eng, 0).crop(render.TAG_BOX).tobytes() == mpc


def test_design_left_is_framed(cfg: Config) -> None:
    corner = (0, HEIGHT - 1)
    assert not render.left(Engine(cfg), 0).getpixel(corner)
    assert render.left(design(cfg), 0).getpixel(corner)


def test_dt2_column_pattern_inverted_and_track(cfg: Config) -> None:
    """Colonne DT2 : pattern noir sur blanc, puis `TR 11`, la track sélectionnée."""
    eng = Engine(cfg)
    column = (0, render.PATTERN_H, render.COLUMN - 3, render.BAND)
    one = render.left(eng, 0)
    assert one.getpixel((1, 1))  # fond blanc du pattern
    eng.track = 11
    assert render.left(eng, 0).crop(column).tobytes() != one.crop(column).tobytes()


# --- slice 5.D : menu du design -----------------------------------------------


def test_keyboard_uses_mpc_bands_with_frame(cfg: Config, project: Project) -> None:
    """Slice 9 : le clavier reprend les bandeaux du MPC ; seul le cadre les distingue."""
    mpc = Engine(cfg, project=project)
    kbd = design(cfg, project=project)
    left_mpc, left_kbd = render.left(mpc, 0), render.left(kbd, 0)
    corner = (WIDTH - 1, 0)
    assert left_kbd.getpixel(corner) and not left_mpc.getpixel(corner)  # cadre
    inner = (1, 1, WIDTH - 1, render.BAND)
    assert left_kbd.crop(inner).tobytes() == left_mpc.crop(inner).tobytes()
    beside_tag = (0, 0, render.TAG_BOX[0] - 2, HEIGHT)  # hors étiquette du mode
    right_kbd, right_mpc = render.right(kbd, 0), render.right(mpc, 0)
    assert right_kbd.crop(beside_tag).tobytes() == right_mpc.crop(beside_tag).tobytes()


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


def test_live_announce_for_two_seconds_then_bank_and_tonic_on_the_left(
    cfg: Config, project: Project
) -> None:
    eng = Engine(cfg, project=project)
    plain, bare = render.right(eng, 0).tobytes(), render.left(eng, 0).tobytes()
    eng.on_program_change(4 * 16)  # E01 : E-TRIBE annoncée
    eng.tick(0)
    assert render.right(eng, 10 * MS).tobytes() != plain
    assert render.right(eng, 3 * SECOND).tobytes() == plain  # annonce retombée
    assert render.left(eng, 3 * SECOND).tobytes() != bare  # pattern, banque et tonalité


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


def test_font_cache_keeps_the_same_pixels() -> None:
    """Le cache de texte (rendu trop lent sur le Pi) ne change aucun pixel."""
    from PIL import Image, ImageDraw, ImageFont

    cached = render._font(16)
    assert cached is render._font(16)
    images = []
    for font in (ImageFont.load_default(size=16), cached, cached):
        img = Image.new("1", (120, 30))
        d = ImageDraw.Draw(img)
        d.text((3, 2), "PHR 01", font=font, fill=1)
        images.append((img.tobytes(), d.textbbox((0, 0), "PHR 01", font=font)))
        assert d.textlength("PHR 01", font=font) == d.textlength("PHR 01", font=cached)
    assert images[0] == images[1] == images[2]
    assert any(key[:2] == ("getmask2", "PHR 01") for key in cached._cache)  # type: ignore[union-attr]


def test_arp_config_shows_divisions_and_settings(cfg: Config) -> None:
    """PATTERN tenu en ARPG : divisions en haut des deux écrans, ORD / OCT / GATE sur le
    gauche ; relâché, les écrans principaux reviennent."""
    eng = Engine(cfg)
    keys = render.left(eng, 0).tobytes()
    eng.handle(ButtonEvent("PATTERN", True), 0)
    menu = render.left(eng, 0)
    assert menu.tobytes() != keys
    before = menu.crop((0, render.BAND + 1, WIDTH, HEIGHT)).tobytes()
    eng.arp_octaves = 3
    assert render.left(eng, 0).crop((0, render.BAND + 1, WIDTH, HEIGHT)).tobytes() != before
    top = render.right(eng, 0).crop((0, 0, WIDTH, render.BAND)).tobytes()
    under = (0, render.BAND + 1, WIDTH, HEIGHT)
    empty = render.right(eng, 0).crop(under).tobytes()
    eng.arp_motif = "GALO"  # le motif choisi : son nom à gauche, ses 16 pas à droite
    galop = render.right(eng, 0).crop(under).tobytes()
    eng.arp_motif = "LONG"
    long = render.right(eng, 0).crop(under).tobytes()
    eng.handle(EncoderEvent(5, cfg.arp.raw_per_choice, 0), 0)  # PRE : le nom du preset
    assert len({empty, galop, long, render.right(eng, 0).crop(under).tobytes()}) == 4
    eng.handle(ButtonEvent("PATTERN", False), SECOND)
    assert eng.arp and render.right(eng, 0).crop((0, 0, WIDTH, render.BAND)).tobytes() != top

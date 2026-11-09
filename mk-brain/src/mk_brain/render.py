"""Pages d'écran (slice 5.C) : images Pillow 1 bit tirées de l'état du moteur.

Pur : le moteur et l'instant sont passés par l'appelant, rien n'est envoyé.
Disposition (revue le 2026-11-09 à l'essai) : chaque écran a un bandeau
(deux tiers supérieurs) et, dessous, 4 colonnes de 64 px, une au-dessus de
chaque encodeur (1-4 sous l'écran gauche, 5-8 sous le droit) : nom et jauge
sur une ligne, sans valeur ; jauge en pointillé tant qu'elle est hors prise.
- Bandeau gauche : pattern en cours (et prochain) et track sélectionnée en
  gros ; dessous, les 16 mutes, remplacés un instant par une alerte ou le
  dernier geste. Pas de tempo, quantize ni swing (décidé à l'essai).
- Bandeau droit : mesure / longueur, phrase, cap ; barre de progression,
  inversée dans les 4 dernières mesures ; compte à rebours `-2` / `-1` en
  bandeau inversé.
- NOTE REPEAT : les 8 divisions dans les deux bandeaux, chacune sous son
  bouton d'écran, la division choisie inversée.
- Bascule de mode proposée : l'écran droit entier.
- Design (slice 5.D) : les entrées du menu sous leurs boutons d'écran
  (BANK, GAMME, TRACK, QUANT à gauche, PHRASE à droite), l'entrée ouverte
  inversée avec la valeur en cours de choix ; dessous, `DESIGN` et les
  mutes (ou le dernier geste) à gauche ; à droite la fiche de la banque
  (clé, tempo, tonique, mode) et la phrase en petit.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont

from mk_brain.display import HEIGHT, WIDTH, new_image, text_image
from mk_brain.engine import MENU
from mk_brain.phrase import BLOCK_BARS
from mk_brain.repeat import DIVISIONS

if TYPE_CHECKING:
    from mk_brain.engine import Engine

OVERLAY_NS = 1_000_000_000  # frappe d'un pad, colonne touchée : 1 s
MESSAGE_NS = 1_500_000_000  # dernier geste de contrôle dans le bandeau gauche
BAND = 40  # hauteur du bandeau (deux tiers supérieurs) ; faders dessous
COLS = 4  # colonnes de fader par écran
COL = WIDTH // COLS
SMALL = 12
BIG = 30  # pattern et track sélectionnée
BAR = 24  # mesure / longueur
DIVISION = 20
COUNTDOWN = 40

Font = ImageFont.FreeTypeFont | ImageFont.ImageFont
Box = tuple[int, int, int, int]


def _font(size: int) -> Font:
    return ImageFont.load_default(size=size)


def _bold(d: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font: Font, ink: int) -> None:
    for dx in (0, 1):
        d.text((xy[0] + dx, xy[1]), text, font=font, fill=ink)


def _centered(d: ImageDraw.ImageDraw, box: Box, text: str, font: Font, ink: int) -> None:
    left, top, right, bottom = d.textbbox((0, 0), text, font=font)
    x = box[0] + (box[2] - box[0] - (right - left)) // 2 - left
    y = box[1] + (box[3] - box[1] - (bottom - top)) // 2 - top
    d.text((x, y), text, font=font, fill=ink)


def _fit(d: ImageDraw.ImageDraw, text: str, width: int, sizes: tuple[int, ...] = (16, 12)) -> Font:
    for size in sizes:
        font = _font(size)
        if d.textlength(text, font=font) <= width:
            return font
    return _font(sizes[-1])


def _showing_repeat(engine: Engine) -> bool:
    return engine.repeat_active and (engine.repeat_held or engine.repeating)


def _repeat_band(d: ImageDraw.ImageDraw, engine: Engine, screen: int) -> None:
    """Les 4 divisions des boutons d'écran au-dessus de cet écran, la choisie inversée."""
    font = _font(DIVISION)
    for i in range(COLS):
        name = DIVISIONS[screen * COLS + i][0]
        box = (i * COL, 0, (i + 1) * COL - 2, BAND - 2)
        chosen = name == engine.division
        if chosen:
            d.rectangle(box, fill=1)
        _centered(d, box, name, font, 0 if chosen else 1)


def _mute_strip(d: ImageDraw.ImageDraw, engine: Engine, left: int = 0) -> None:
    """16 cases, une par track : pleine = ouverte, vide = mutée ; track sélectionnée soulignée.
    La track de l'AUTO CHANNEL (pas de mute par son canal) n'a qu'un point."""
    cell = (WIDTH - left) // 16
    top, bottom = 29, 35
    for t in range(1, 17):
        x0, x1 = left + (t - 1) * cell + 2, left + t * cell - 3
        if t == engine.cfg.midi.auto_channel:
            d.point(((x0 + x1) // 2, (top + bottom) // 2), fill=1)
        elif engine.faders.muted.get(t):
            d.rectangle((x0, top, x1, bottom), outline=1)
        else:
            d.rectangle((x0, top, x1, bottom), fill=1)
        if t == engine.track:
            d.rectangle((x0 - 1, bottom + 2, x1 + 1, bottom + 3), fill=1)


MENU_TOP = 23  # hauteur des entrées du menu en design


def _menu_band(d: ImageDraw.ImageDraw, engine: Engine, screen: int) -> None:
    """Design : les entrées du menu sous les boutons d'écran de cet écran."""
    view = engine.menu_view()
    small = _font(SMALL)
    for i in range(COLS):
        k = screen * COLS + i
        if k >= len(MENU):
            continue
        name, value, opened = view[k]
        box = (i * COL, 0, (i + 1) * COL - 2, MENU_TOP)
        ink = 1
        if opened:
            d.rectangle(box, fill=1)
            ink = 0
        _centered(d, (box[0], 2, box[2], 11), name, small, ink)  # sous le cadre du design
        font = _fit(d, value, COL - 6, (16, 12, 10, 9))
        _centered(d, (box[0], 12, box[2], MENU_TOP), value, font, ink)


def _design_left(
    d: ImageDraw.ImageDraw, engine: Engine, now: int, message: tuple[str, int] | None, warn: str
) -> None:
    """Menu 1-4 en haut ; dessous `DESIGN`, puis mutes ou dernier geste / frappe."""
    _menu_band(d, engine, 0)
    small = _font(SMALL)
    _bold(d, (3, 25), "DESIGN", small, 1)
    left = 8 + int(d.textlength("DESIGN", font=small))
    recent: list[tuple[int, str]] = []
    if message is not None and now - message[1] < MESSAGE_NS:
        recent.append((message[1], message[0]))
    hit = engine.last_hit
    if hit is not None and now - hit[2] < OVERLAY_NS:
        recent.append((hit[2], f"pad {hit[0]}  vel {hit[1]}"))
    text = warn or (max(recent)[1] if recent else "")
    if text:
        d.text((left, 25), text, font=_fit(d, text, WIDTH - left - 4, (12,)), fill=1)
    else:
        _mute_strip(d, engine, left)


def _design_right(d: ImageDraw.ImageDraw, engine: Engine) -> None:
    """PHRASE sous le bouton 5, fiche de la banque à côté ; phrase en petit dessous."""
    _menu_band(d, engine, 1)
    small, mid = _font(SMALL), _font(16)
    sheet = engine.sheet
    if sheet is None:
        d.text((COL + 6, 4), "pas de projet", font=mid, fill=1)
    else:
        key, bank = sheet
        _bold(d, (COL + 6, -3), f"{key}  {bank.tempo:g}", mid, 1)
        d.text((COL + 6, 12), f"{bank.tonique} {bank.mode}", font=small, fill=1)
    st = engine.phrase_state
    length = engine.phrase.length
    bar = "--" if st is None else str(st.bar)
    text = f"{bar} / {length}" + ("" if st is None else f"  cap {st.cap} : -{st.to_cap}")
    d.text((3, 24), text, font=small, fill=1)
    top, bottom, left, right = 28, 34, 140, WIDTH - 3
    d.rectangle((left, top, right, bottom), outline=1)
    if st is not None:
        d.rectangle((left, top, left + round((right - left) * st.bar / length), bottom), fill=1)


def _left_band(
    d: ImageDraw.ImageDraw, engine: Engine, now: int, message: tuple[str, int] | None, warn: str
) -> None:
    """Pattern en cours (et prochain) et track sélectionnée en gros ; mutes dessous.
    Tempo, quantize et swing ne sont pas affichés (LED GRID et SWING, écran de la DT2)."""
    big, mid = _font(BIG), _font(16)
    track = f"T{engine.track:02d}"
    tw = int(d.textlength(track, font=big))
    _bold(d, (WIDTH - tw - 4, -6), track, big, 1)
    name = engine.cfg.track_names.get(engine.track, "")  # code de la grille (doctrine §1)
    if name:
        nw = int(d.textlength(name, font=mid))
        _bold(d, (WIDTH - tw - nw - 12, 1), name, mid, 1)
    current = engine.phrase.pattern or "---"
    _bold(d, (3, -6), current, big, 1)
    nxt = engine.next_pattern
    if nxt is not None:
        x = 8 + int(d.textlength(current, font=big))
        _bold(d, (x, 1), f"> {nxt}", mid, 1)
    # bande des mutes, ou alerte / dernier geste
    text = warn
    if not text and message is not None and now - message[1] < MESSAGE_NS:
        text = message[0]
    if text:
        _bold(d, (3, 23), text, _fit(d, text, WIDTH - 8, (12,)), 1)
    else:
        _mute_strip(d, engine)


def _right_band(d: ImageDraw.ImageDraw, engine: Engine) -> None:
    small = _font(SMALL)
    st = engine.phrase_state
    if st is not None and st.countdown is not None:  # bandeau inversé, compte à rebours
        d.rectangle((0, 0, WIDTH - 1, BAND - 1), fill=1)
        for dx in (0, 1):  # gras, centré dans la moitié gauche
            box = (dx, 0, WIDTH // 2 + dx, BAND - 1)
            _centered(d, box, str(st.countdown), _font(COUNTDOWN), 0)
        d.text((WIDTH // 2 + 8, 4), f"cap {st.cap}", font=_font(16), fill=0)
        d.text((WIDTH // 2 + 8, 22), f"{st.bar} / {st.length}", font=_font(16), fill=0)
        return
    bar = "--" if st is None else str(st.bar)
    _bold(d, (3, -4), f"{bar} / {engine.phrase.length}", _font(BAR), 1)
    if st is not None:
        d.text((150, -3), f"phrase {st.phrase}", font=small, fill=1)
        d.text((150, 9), f"cap {st.cap} : -{st.to_cap}", font=small, fill=1)
    # barre : une case par mesure, séparateurs tous les 8 ; 4 dernières en vidéo inverse
    length = engine.phrase.length
    top, bottom, left, right = 27, 35, 2, WIDTH - 3
    cell = (right - left) / length
    tail = st is not None and st.tail
    if tail:
        d.rectangle((0, top - 3, WIDTH - 1, bottom + 3), fill=1)
    ink = 0 if tail else 1
    d.rectangle((left, top, right, bottom), outline=ink)
    if st is not None:
        d.rectangle((left, top, left + round(cell * st.bar), bottom), fill=ink)
    for b in range(BLOCK_BARS, length, BLOCK_BARS):
        x = left + round(cell * b)
        d.line((x, top - 2, x, bottom + 2), fill=ink)


def _faders(d: ImageDraw.ImageDraw, engine: Engine, now: int, screen: int) -> None:
    """Les 4 faders au-dessus des encodeurs de cet écran."""
    small = _font(SMALL)
    touched = None
    if engine.last_touch is not None and now - engine.last_touch[1] < OVERLAY_NS:
        touched = engine.last_touch[0] - 1
    page = engine.cfg.encoders.page
    views = engine.faders.view(engine.track)
    for i in range(COLS):
        k = screen * COLS + i
        f = views[k]
        x = i * COL
        ink = 1
        if k == touched:
            d.rectangle((x, BAND + 1, x + COL - 2, HEIGHT - 1), fill=1)
            ink = 0
        _centered(d, (x + 2, BAND + 1, x + 30, HEIGHT - 1), f.name, small, ink)
        top, bottom, left, right = BAND + 7, BAND + 17, x + 33, x + COL - 5
        d.rectangle((left, top, right, bottom), outline=ink)
        end = left + round((right - left) * f.value / 127)
        if page[k].bipolar:  # pan : depuis le centre (64)
            mid = (left + right) // 2
            fill: Box = (min(mid, end), top, max(mid, end), bottom)
            d.line((mid, top - 2, mid, bottom + 2), fill=ink)
        else:
            fill = (left, top, end, bottom)
        if f.stale:  # hors prise : remplissage en pointillé
            pts = [
                (px, py)
                for px in range(fill[0], fill[2] + 1)
                for py in range(top, bottom + 1)
                if (px + py) % 2 == 0
            ]
            d.point(pts, fill=ink)
        else:
            d.rectangle(fill, fill=ink)


def left(
    engine: Engine, now: int, message: tuple[str, int] | None = None, warn: str = ""
) -> Image.Image:
    """Écran gauche : bandeau de contexte, faders 1-4. Cadre en design (jamais confondu)."""
    img = new_image()
    d = ImageDraw.Draw(img)
    if _showing_repeat(engine):
        _repeat_band(d, engine, 0)
    elif engine.design:
        _design_left(d, engine, now, message, warn)
    else:
        _left_band(d, engine, now, message, warn)
    d.line((0, BAND, WIDTH - 1, BAND), fill=1)
    _faders(d, engine, now, 0)
    if engine.design:
        d.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), outline=1)
    return img


def right(engine: Engine, now: int) -> Image.Image:
    """Écran droit : bandeau de phrase, faders 5-8 ; bascule de mode proposée en plein écran."""
    pending = engine.modes.pending
    if pending is not None:
        lines = ["", f"-> {pending.upper()} ?", "appui encodeur maître", "autre bouton : annuler"]
        return text_image(lines, bold=frozenset({1}))
    img = new_image()
    d = ImageDraw.Draw(img)
    if _showing_repeat(engine):
        _repeat_band(d, engine, 1)
    elif engine.design:
        _design_right(d, engine)
    else:
        _right_band(d, engine)
    d.line((0, BAND, WIDTH - 1, BAND), fill=1)
    _faders(d, engine, now, 1)
    return img

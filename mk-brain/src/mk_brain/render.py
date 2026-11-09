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
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont

from mk_brain.display import HEIGHT, WIDTH, new_image, text_image
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


def _mute_strip(d: ImageDraw.ImageDraw, engine: Engine) -> None:
    """16 cases, une par track : pleine = ouverte, vide = mutée ; track sélectionnée soulignée.
    La track de l'AUTO CHANNEL (pas de mute par son canal) n'a qu'un point."""
    cell = WIDTH // 16
    top, bottom = 29, 35
    for t in range(1, 17):
        x0, x1 = (t - 1) * cell + 2, t * cell - 3
        if t == engine.cfg.midi.auto_channel:
            d.point(((x0 + x1) // 2, (top + bottom) // 2), fill=1)
        elif engine.faders.muted.get(t):
            d.rectangle((x0, top, x1, bottom), outline=1)
        else:
            d.rectangle((x0, top, x1, bottom), fill=1)
        if t == engine.track:
            d.rectangle((x0 - 1, bottom + 2, x1 + 1, bottom + 3), fill=1)


def _left_band(
    d: ImageDraw.ImageDraw, engine: Engine, now: int, message: tuple[str, int] | None, warn: str
) -> None:
    """Pattern en cours (et prochain) et track sélectionnée en gros ; mutes dessous.
    Tempo, quantize et swing ne sont pas affichés (LED GRID et SWING, écran de la DT2)."""
    big, mid = _font(BIG), _font(16)
    track = f"T{engine.track:02d}"
    tw = int(d.textlength(track, font=big))
    _bold(d, (WIDTH - tw - 4, -6), track, big, 1)
    if engine.design:
        lay = engine.layout
        _bold(d, (3, -3), "DESIGN", mid, 1)
        d.text((3, 12), f"{lay.group} {lay.name}  -> AUTO", font=_font(SMALL), fill=1)
    else:
        current = engine.phrase.pattern or "---"
        _bold(d, (3, -6), current, big, 1)
        nxt = engine.next_pattern
        if nxt is not None:
            x = 8 + int(d.textlength(current, font=big))
            _bold(d, (x, 1), f"> {nxt}", mid, 1)
    # bande des mutes, ou alerte / geste / frappe en design, le plus récent
    recent: list[tuple[int, str]] = []
    if message is not None and now - message[1] < MESSAGE_NS:
        recent.append((message[1], message[0]))
    hit = engine.last_hit
    if engine.design and hit is not None and now - hit[2] < OVERLAY_NS:
        recent.append((hit[2], f"pad {hit[0]}  vel {hit[1]}"))
    text = warn or (max(recent)[1] if recent else "")
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
    else:
        _right_band(d, engine)
    d.line((0, BAND, WIDTH - 1, BAND), fill=1)
    _faders(d, engine, now, 1)
    return img

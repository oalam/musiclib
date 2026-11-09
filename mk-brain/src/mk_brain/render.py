"""Pages d'écran (slice 5.C) : images Pillow 1 bit tirées de l'état du moteur.

Pur : le moteur et l'instant sont passés par l'appelant, rien n'est envoyé.
Disposition (revue le 2026-11-09 à l'essai) : chaque écran a un bandeau
(tiers supérieur) et, dessous, 4 colonnes de 64 px, une au-dessus de chaque
encodeur (1-4 sous l'écran gauche, 5-8 sous le droit).
- Bandeau gauche : pattern, BPM, transport, quantize, swing ; puis track
  sélectionnée, ou dernier geste / frappe, ou alerte.
- Bandeau droit : mesure / longueur, phrase, cap ; barre de progression,
  inversée dans les 4 dernières mesures ; compte à rebours `-2` / `-1` en
  bandeau inversé.
- NOTE REPEAT : les 8 divisions dans les deux bandeaux, chacune sous son
  bouton d'écran, la division choisie inversée.
- Bascule de mode proposée : l'écran droit entier.
Les symboles (lecture, arrêt) sont dessinés : la police intégrée ne les a pas.
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
BAND = 21  # hauteur du bandeau (tiers supérieur)
COLS = 4  # colonnes de fader par écran
COL = WIDTH // COLS
SMALL = 12
VALUE = 18
DIVISION = 16
COUNTDOWN = 26

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


def _transport(d: ImageDraw.ImageDraw, x: int, y: int, running: bool) -> None:
    if running:
        d.polygon([(x, y), (x, y + 8), (x + 7, y + 4)], fill=1)
    else:
        d.rectangle((x, y + 1, x + 6, y + 7), fill=1)


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


def _left_band(
    d: ImageDraw.ImageDraw, engine: Engine, now: int, message: tuple[str, int] | None, warn: str
) -> None:
    small = _font(SMALL)
    q = "Qoff" if engine.quantize == "off" else f"Q{engine.quantize[2:]}"
    if engine.design:
        lay = engine.layout
        _bold(d, (3, -3), f"DESIGN  {lay.group} {lay.name}", small, 1)
        d.text((190, -3), q, font=small, fill=1)
    else:
        bpm = f"{engine.clock.bpm:5.1f}" if engine.clock.bpm else "--.-"
        d.text((3, -3), engine.phrase.pattern or "---", font=small, fill=1)
        d.text((50, -3), bpm, font=small, fill=1)
        _transport(d, 96, 0, engine.phrase_state is not None)
        d.text((120, -3), f"{q}  SW{engine.swing}", font=small, fill=1)
    # 2e ligne : alerte > frappe ou geste le plus récent > track sélectionnée
    track = engine.track
    if engine.design:
        line = f"T{track:02d}  -> AUTO ch{engine.cfg.midi.auto_channel}"
    else:
        line = f"T{track:02d}  ch{track}" + ("  MUTE" if engine.faders.muted.get(track) else "")
    recent: list[tuple[int, str]] = []
    if message is not None and now - message[1] < MESSAGE_NS:
        recent.append((message[1], message[0]))
    hit = engine.last_hit
    if hit is not None and now - hit[2] < OVERLAY_NS:
        pad, vel, at = hit
        label = f"T{pad:02d}" if engine.layout.kind == "rythmique" else f"pad {pad}"
        recent.append((at, f"{label}  vel {vel}"))
    if recent:
        line = max(recent)[1]
    if warn:
        _bold(d, (3, 8), warn, small, 1)
    else:
        d.text((3, 8), line, font=small, fill=1)


def _right_band(d: ImageDraw.ImageDraw, engine: Engine) -> None:
    small = _font(SMALL)
    st = engine.phrase_state
    if st is not None and st.countdown is not None:  # bandeau inversé, compte à rebours
        d.rectangle((0, 0, WIDTH - 1, BAND - 1), fill=1)
        for dx in (0, 1):  # gras, centré dans le bandeau
            _centered(d, (4 + dx, 0, 64 + dx, BAND - 1), str(st.countdown), _font(COUNTDOWN), 0)
        d.text((70, 1), f"cap {st.cap}     {st.bar} / {st.length}", font=small, fill=0)
        return
    if st is None:
        _bold(d, (3, -3), f"-- / {engine.phrase.length}", small, 1)
    else:
        _bold(d, (3, -3), f"{st.bar} / {st.length}", small, 1)
        d.text((80, -3), f"phrase {st.phrase}", font=small, fill=1)
        d.text((165, -3), f"cap {st.cap} : -{st.to_cap}", font=small, fill=1)
    # barre : une case par mesure, séparateurs tous les 8 ; 4 dernières en vidéo inverse
    length = engine.phrase.length
    top, bottom, left, right = 12, 17, 2, WIDTH - 3
    cell = (right - left) / length
    tail = st is not None and st.tail
    if tail:
        d.rectangle((0, top - 2, WIDTH - 1, bottom + 2), fill=1)
    ink = 0 if tail else 1
    d.rectangle((left, top, right, bottom), outline=ink)
    if st is not None:
        d.rectangle((left, top, left + round(cell * st.bar), bottom), fill=ink)
    for b in range(BLOCK_BARS, length, BLOCK_BARS):
        x = left + round(cell * b)
        d.line((x, top - 2, x, bottom + 2), fill=ink)


def _faders(d: ImageDraw.ImageDraw, engine: Engine, now: int, screen: int) -> None:
    """Les 4 faders au-dessus des encodeurs de cet écran."""
    small, value_font = _font(SMALL), _font(VALUE)
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
        d.text((x + 4, BAND + 1), f.name, font=small, fill=ink)
        _bold(d, (x + 4, BAND + 9), f"{'~' if f.stale else ''}{f.value}", value_font, ink)
        top, bottom, left, right = 55, 61, x + 4, x + COL - 7
        d.rectangle((left, top, right, bottom), outline=ink)
        end = left + round((right - left) * f.value / 127)
        if page[k].bipolar:  # pan : depuis le centre (64)
            mid = (left + right) // 2
            d.rectangle((min(mid, end), top, max(mid, end), bottom), fill=ink)
            d.line((mid, top - 2, mid, bottom + 2), fill=ink)
        else:
            d.rectangle((left, top, end, bottom), fill=ink)


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

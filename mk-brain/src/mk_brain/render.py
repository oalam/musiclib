"""Pages d'écran (slice 5.C) : images Pillow 1 bit tirées de l'état du moteur.

Pur : le moteur et l'instant sont passés par l'appelant, rien n'est envoyé.
- `live_left` : contexte et phrase (pattern, BPM, transport, quantize, swing,
  mesure / longueur en gros, barre de 8 blocs, temps, mesures avant le cap).
- `right` : les 8 faders de la track sélectionnée, ou une superposition
  temporaire par ordre de priorité (SPEC, Écrans) : bascule de mode,
  division du note repeat, compte à rebours `-2` / `-1`, frappe d'un pad.
Les symboles (lecture, arrêt, temps) sont dessinés : la police intégrée ne
les a pas.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont

from mk_brain.display import HEIGHT, WIDTH, big_text_image, new_image, text_image
from mk_brain.phrase import BLOCK_BARS

if TYPE_CHECKING:
    from mk_brain.engine import Engine

OVERLAY_NS = 1_000_000_000  # frappe d'un pad, colonne touchée : 1 s
MESSAGE_NS = 1_500_000_000  # message de contrôle dans l'en-tête de droite
SMALL = 13
VALUE = 12  # « ~127 » tient dans une colonne de 32 px
BIG = 30
COL = WIDTH // 8


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    return ImageFont.load_default(size=size)


def _transport(d: ImageDraw.ImageDraw, x: int, y: int, running: bool) -> None:
    if running:
        d.polygon([(x, y), (x, y + 8), (x + 7, y + 4)], fill=1)
    else:
        d.rectangle((x, y + 1, x + 6, y + 7), fill=1)


def live_left(engine: Engine, warn: str = "") -> Image.Image:
    """Écran gauche en live : lisible d'un coup d'œil ; `warn` en bas (clock, Transfer)."""
    img = new_image()
    d = ImageDraw.Draw(img)
    small, big = _font(SMALL), _font(BIG)
    clock = engine.clock
    st = engine.phrase_state
    q = "Qoff" if engine.quantize == "off" else f"Q{engine.quantize[2:]}"
    pattern = engine.phrase.pattern or "---"
    bpm = f"{clock.bpm:5.1f}" if clock.bpm else "--.-"
    d.text((2, -3), pattern, font=small, fill=1)
    d.text((70, -3), bpm, font=small, fill=1)
    _transport(d, 114, 1, st is not None)
    d.text((140, -3), f"{q}  SW{engine.swing}", font=small, fill=1)

    bar = "--" if st is None else f"{st.bar} / {st.length}"
    d.text((2, 6), bar, font=big, fill=1)
    if st is not None:
        d.text((150, 9), f"phrase {st.phrase}", font=small, fill=1)

    # barre : une case par mesure, séparateurs tous les 8 ; 4 dernières en vidéo inverse
    length = engine.phrase.length
    top, bottom, left, right = 43, 51, 2, WIDTH - 3
    cell = (right - left) / length
    if st is not None and st.tail:
        d.rectangle((left - 2, top - 2, right + 2, bottom + 2), fill=1)
    ink = 0 if st is not None and st.tail else 1
    d.rectangle((left, top, right, bottom), outline=ink)
    if st is not None:
        d.rectangle((left, top, left + round(cell * st.bar), bottom), fill=ink)
    for b in range(BLOCK_BARS, length, BLOCK_BARS):
        x = left + round(cell * b)
        d.line((x, top - 2, x, bottom + 2), fill=ink)

    if st is not None:
        for i in range(4):  # temps de la mesure
            box = (4 + i * 14, 55, 12 + i * 14, 63)
            d.ellipse(box, fill=1 if i + 1 == st.beat else 0, outline=1)
        d.text((150, 23), f"cap {st.cap} : -{st.to_cap}", font=small, fill=1)
    if warn:
        for dx in (0, 1):  # gras : alerte
            d.text((70 + dx, 50), warn, font=small, fill=1)
    return img


def _faders(engine: Engine, now: int, message: tuple[str, int] | None) -> Image.Image:
    img = new_image()
    d = ImageDraw.Draw(img)
    small, value_font = _font(SMALL), _font(VALUE)
    track = engine.track
    if engine.design:
        head = f"T{track:02d}  -> AUTO ch{engine.cfg.midi.auto_channel}"
    else:
        head = f"T{track:02d}  ch{track}"
        if engine.faders.muted.get(track):
            head += "  MUTE"
    if message is not None and now - message[1] < MESSAGE_NS:
        head = message[0]
    d.text((2, -3), head, font=small, fill=1)
    touched = None
    if engine.last_touch is not None and now - engine.last_touch[1] < OVERLAY_NS:
        touched = engine.last_touch[0] - 1
    bipolar = {i for i, e in enumerate(engine.cfg.encoders.page) if e.bipolar}
    for i, f in enumerate(engine.faders.view(track)):
        x = i * COL
        ink = 1
        if i == touched:
            d.rectangle((x, 12, x + COL - 2, HEIGHT - 1), fill=1)
            ink = 0
        d.text((x + 3, 11), f.name, font=small, fill=ink)
        d.text((x + 2, 26), f"{'~' if f.stale else ''}{f.value}", font=value_font, fill=ink)
        top, bottom, left, right = 47, 59, x + 3, x + COL - 5
        d.rectangle((left, top, right, bottom), outline=ink)
        if i in bipolar:  # pan : depuis le centre (64)
            mid = (left + right) // 2
            end = left + round((right - left) * f.value / 127)
            d.rectangle((min(mid, end), top, max(mid, end), bottom), fill=ink)
            d.line((mid, top - 2, mid, bottom + 2), fill=ink)
        else:
            d.rectangle((left, top, left + round((right - left) * f.value / 127), bottom), fill=ink)
    return img


def right(engine: Engine, now: int, message: tuple[str, int] | None = None) -> Image.Image:
    """Écran droit : superposition la plus prioritaire, sinon les 8 faders."""
    pending = engine.modes.pending
    if pending is not None:
        lines = ["", f"-> {pending.upper()} ?", "appui encodeur maître", "autre bouton : annuler"]
        return text_image(lines, bold=frozenset({1}))
    if engine.repeat_active and (engine.repeat_held or engine.repeating):
        return big_text_image(engine.division, size=44)
    st = engine.phrase_state
    if st is not None and st.countdown is not None:
        return big_text_image(str(st.countdown), size=60)
    hit = engine.last_hit
    if hit is not None and now - hit[2] < OVERLAY_NS:
        pad, vel, _ = hit
        label = f"T{pad:02d}" if engine.layout.kind == "rythmique" else f"pad {pad}"
        return big_text_image(f"{label} {vel}", size=32)
    return _faders(engine, now, message)

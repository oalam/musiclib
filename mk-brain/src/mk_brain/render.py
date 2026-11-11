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
- Design (slice 5.D, revu le 2026-11-09) : icône `D` au coin haut gauche
  (le cadre reste), valeurs du menu sous les boutons 1-4 (GAMME, TRACK,
  QUANT, PHRASE) sans libellé, l'entrée ouverte inversée ; dessous, la
  frappe (`Bb4 tierce mineure` sur une barre de vélocité), une alerte, le
  dernier geste ou les mutes ; à droite la fiche de la banque et la
  phrase en petit.
- Live avec un projet (slice 6.B, provisoire jusqu'à l'essai) : tonique et
  mode de la banque du dernier PC en haut à droite du bandeau droit ; à un
  changement de banque, titre et description 2 s à la place du bandeau
  (le compte à rebours garde la priorité).
- Slice 9 : le clavier reprend les deux bandeaux du MPC ; une frappe y
  montre sa note et son degré sous le pattern, `oct +1` à droite, le cadre
  reste. Menu et fiche de banque du design retirés de l'écran. Sous SOLO,
  la première track du groupe et ses faders (`x2` si plusieurs). Le mode
  (MPC, KEYS, SOLO) toujours en bas à gauche du bandeau gauche, inversé.
- Revue du 2026-11-11 (v0.29.0), qui remplace ce qui précède pour les deux bandeaux :
  à gauche la colonne « écran de la DT2 » (pattern en noir sur blanc, `TR 12`), la
  banque et sa tonalité, les mutes toujours visibles avec la double croche en cours ;
  à droite `PHR 01` en noir sur blanc, mesure / longueur, cap, pattern suivant, le
  mode et, dessous, le tempo lissé ; pointillé à chaque tour de pattern dans la barre.
- Sélection de projet (slice 6.C) : liste à gauche, la ligne choisie en
  gros et inversée ; à droite le projet choisi (banques, date) et les gestes.
  Elle remplace les deux écrans entiers.
"""

from __future__ import annotations

import unicodedata
from functools import cache
from typing import TYPE_CHECKING, Any

from PIL import Image, ImageChops, ImageDraw, ImageFont

from mk_brain.display import HEIGHT, WIDTH, new_image, text_image
from mk_brain.layouts import FLAT_NAMES, degree_name, flat_note
from mk_brain.phrase import BLOCK_BARS
from mk_brain.repeat import DIVISIONS

if TYPE_CHECKING:
    from mk_brain.engine import Engine

OVERLAY_NS = 1_000_000_000  # frappe d'un pad, colonne touchée : 1 s
MESSAGE_NS = 1_500_000_000  # dernier geste de contrôle dans le bandeau gauche
ANNOUNCE_NS = 2_000_000_000  # titre et description d'une nouvelle banque (live)
BAND = 40  # hauteur du bandeau (deux tiers supérieurs) ; faders dessous
COLS = 4  # colonnes de fader par écran
COL = WIDTH // COLS
SMALL = 12
BIG = 30  # pattern et track sélectionnée
BAR = 24  # mesure / longueur
DIVISION = 20
COUNTDOWN = 40
FONT_CACHE = 2000  # textes retenus par taille de police avant remise à zéro

Font = ImageFont.FreeTypeFont | ImageFont.ImageFont
Box = tuple[int, int, int, int]


class _CachedFont(ImageFont.FreeTypeFont):
    """Police qui retient ses mesures et ses tracés de texte.

    Les mêmes chaînes reviennent d'une image à l'autre ; FreeType coûtait
    environ 80 ms par paire d'écrans sur le Pi 3B, dans la boucle qui lit les
    pads. Sous-classe et non enveloppe : Pillow teste `FreeTypeFont` avant
    d'appeler `getmask2`. Les masques rendus sont seulement lus par Pillow.
    """

    _cache: dict[tuple[Any, ...], Any]

    @classmethod
    def wrap(cls, font: ImageFont.FreeTypeFont) -> _CachedFont:
        cached = cls.__new__(cls)
        cached.__dict__.update(font.__dict__)
        cached._cache = {}
        return cached

    def _memo(self, method: str, text: Any, args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
        call = getattr(super(), method)
        try:
            key = (method, text, args, tuple(sorted(kwargs.items())))
            return self._cache[key]
        except KeyError:
            pass
        except TypeError:  # argument non hachable : pas de cache
            return call(text, *args, **kwargs)
        if len(self._cache) >= FONT_CACHE:
            self._cache.clear()
        value = self._cache[key] = call(text, *args, **kwargs)
        return value

    def getmask2(self, text: Any, *args: Any, **kwargs: Any) -> Any:
        return self._memo("getmask2", text, args, kwargs)

    def getbbox(self, text: Any, *args: Any, **kwargs: Any) -> Any:
        return self._memo("getbbox", text, args, kwargs)

    def getlength(self, text: Any, *args: Any, **kwargs: Any) -> Any:
        return self._memo("getlength", text, args, kwargs)


@cache
def _font(size: int) -> Font:
    font = ImageFont.load_default(size=size)
    return _CachedFont.wrap(font) if isinstance(font, ImageFont.FreeTypeFont) else font


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


def ascii_text(text: str) -> str:
    """Sans accents : la police de Pillow ne les a pas (`Cœur, ça` → `Coeur, ca`)."""
    text = text.replace("œ", "oe").replace("Œ", "OE").replace("æ", "ae").replace("Æ", "AE")
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def _wrap(d: ImageDraw.ImageDraw, text: str, font: Font, width: int, lines: int) -> list[str]:
    """Coupe aux mots en `lines` lignes au plus ; le reste est perdu (`...`)."""
    out: list[str] = []
    words = text.split()
    while words and len(out) < lines:
        line = words.pop(0)
        while words and d.textlength(f"{line} {words[0]}", font=font) <= width:
            line = f"{line} {words.pop(0)}"
        out.append(line)
    if words:
        out[-1] += " ..."
    return out


def _announcing(engine: Engine, now: int) -> bool:
    a = engine.announce
    return a is not None and a[2] is not None and now - a[2] < ANNOUNCE_NS


def _announce_band(d: ImageDraw.ImageDraw, engine: Engine) -> None:
    """Nouvelle banque : clé et titre en gras, description sur deux lignes."""
    assert engine.announce is not None
    key, bank, _ = engine.announce
    _bold(d, (3, -3), ascii_text(f"{key}  {bank.title}"), _font(16), 1)
    small = _font(SMALL)
    for i, line in enumerate(_wrap(d, ascii_text(bank.desc), small, WIDTH - 6, 2)):
        d.text((3, 14 + 12 * i), line, font=small, fill=1)


def _showing_repeat(engine: Engine) -> bool:
    """Divisions en haut des écrans : NOTE REPEAT en cours, ou config de l'arpège (PATTERN tenu)."""
    return engine.arp_menu or (engine.repeat_active and (engine.repeat_held or engine.repeating))


def _repeat_band(d: ImageDraw.ImageDraw, engine: Engine, screen: int) -> None:
    """Les 4 divisions des boutons d'écran au-dessus de cet écran, la choisie inversée."""
    font = _font(DIVISION)
    for i in range(COLS):
        name = DIVISIONS[screen * COLS + i][0]
        box = (i * COL, 0, (i + 1) * COL - 2, TAG_TOP - 2)  # place pour l'étiquette du mode
        chosen = name == engine.division
        if chosen:
            d.rectangle(box, fill=1)
        _centered(d, box, name, font, 0 if chosen else 1)


COLUMN = 46  # colonne « écran de la DT2 » (pattern, SMP, track), à gauche du bandeau gauche
MUTE_TOP, MUTE_BOTTOM = 26, 35  # cases des mutes, 10 px de haut
BEAT_LINE = (MUTE_TOP - 2, MUTE_BOTTOM + 3)  # pointillé entre deux temps, dépasse des cases
STEPS_PER_BAR = 16
STEPS_PER_BEAT = 4
TICKS_PER_STEP = 6  # 24 ticks par noire
PATTERN_BARS = 4  # un tour de pattern de 64 pas
TAG_W = 46  # étiquette du mode (MPC, KEYS, SOLO)
TAG_TOP = 25
TAG_BOX: Box = (WIDTH - TAG_W + 2, 1, WIDTH - 3, 12)  # en haut à droite du bandeau droit
TAG_BOX_REPEAT: Box = (2, TAG_TOP, TAG_W - 4, BAND - 3)  # NOTE REPEAT : sous les divisions


def _step(engine: Engine) -> int | None:
    """Double croche en cours dans la mesure (0-15), None à l'arrêt."""
    ticks = engine.clock.ticks_since_start
    return None if ticks is None else ticks // TICKS_PER_STEP % STEPS_PER_BAR


def _mute_x0(track: int, left: int = COLUMN) -> int:
    """Bord gauche de la case de `track`. Les 4 groupes d'un temps s'écartent de 1 px
    (-1, 0, +1, +2) : 3 px entre deux temps au lieu de 2, la place du pointillé."""
    cell = (WIDTH - left) // 16
    return left + (track - 1) * cell + 2 + (track - 1) // STEPS_PER_BEAT - 1


def _mute_strip(d: ImageDraw.ImageDraw, engine: Engine, left: int = COLUMN) -> None:
    """16 cases, une par track : pleine = ouverte, vide = mutée ; track sélectionnée soulignée.
    La track de l'AUTO CHANNEL (pas de mute par son canal) n'a qu'un point. Les 16 cases
    comptent aussi les doubles croches de la mesure : un carré intérieur, en inverse de sa
    case, marque celle qui joue. Un fin pointillé vertical sépare les temps (entre les
    cases 4/5, 8/9 et 12/13)."""
    cell = (WIDTH - left) // 16
    top, bottom = MUTE_TOP, MUTE_BOTTOM
    step = _step(engine)
    for t in range(1, 17):
        x0 = _mute_x0(t, left)
        x1 = x0 + cell - 3
        if t > 1 and t % STEPS_PER_BEAT == 1:  # nouveau temps : pointillé au milieu de l'écart
            d.point([(x0 - 2, y) for y in range(BEAT_LINE[0], BEAT_LINE[1] + 1, 2)], fill=1)
        full = False
        if t == engine.cfg.midi.auto_channel:
            d.point(((x0 + x1) // 2, (top + bottom) // 2), fill=1)
        elif engine.faders.muted.get(t):
            d.rectangle((x0, top, x1, bottom), outline=1)
        else:
            d.rectangle((x0, top, x1, bottom), fill=1)
            full = True
        if step == t - 1:
            d.rectangle((x0 + 2, top + 2, x1 - 2, bottom - 2), fill=0 if full else 1)
        if t == engine.track:
            d.rectangle((x0, bottom + 2, x1, bottom + 3), fill=1)


def _mode_tag(d: ImageDraw.ImageDraw, engine: Engine, box: Box = TAG_BOX, ink: int = 1) -> None:
    """Mode courant en vidéo inverse, toujours affiché (demandé le 2026-11-10), sur
    l'écran droit depuis le 2026-11-11. `ink` 0 : sur un bandeau lui-même inversé."""
    d.rectangle((box[0] - 2, box[1] - 1, box[2] + 2, box[3] + 1), fill=1 - ink)
    d.rectangle(box, fill=ink)
    name = engine.mode_name
    _centered(d, box, name, _fit(d, name, box[2] - box[0] - 4, (SMALL, 10)), 1 - ink)


def _hit_strip(img: Image.Image, engine: Engine, hit: tuple[int, int, int, int]) -> None:
    """Frappe du clavier : note en bémols et sa place dans la gamme, sur une barre de
    vélocité. Le texte s'inverse là où la barre est pleine (OU exclusif)."""
    _, note, vel, _ = hit
    lay = engine.layout
    name, role = flat_note(note), degree_name(lay, note)
    top, bottom, left, right = 3, 20, COLUMN + 2, WIDTH - 4
    bar = new_image()
    db = ImageDraw.Draw(bar)
    db.rectangle((left, top, left + round((right - left) * vel / 127), bottom), fill=1)
    text = new_image()
    dt = ImageDraw.Draw(text)
    big = _font(14)
    _bold(dt, (left + 4, top), name, big, 1)
    x = left + 14 + int(dt.textlength(name, font=big))
    role_font = _fit(dt, role, right - x - 4, (12, 10, 9))
    _centered(
        dt, (x, top, x + int(dt.textlength(role, font=role_font)), bottom), role, role_font, 1
    )
    box = (left, top, WIDTH - 1, bottom + 1)
    img.paste(ImageChops.logical_xor(bar, text).crop(box), box[:2])
    ImageDraw.Draw(img).rectangle((left, top, right, bottom), outline=1)


PATTERN_H = 22  # pattern noir sur blanc, en haut de la colonne DT2


def _dt2_column(d: ImageDraw.ImageDraw, engine: Engine) -> None:
    """Comme le coin de l'écran de la DT2 : pattern (noir sur blanc), puis `TR 12`, la
    track des faders (celle du perform s'il y en a un ; `x2 3` : groupe SOLO de 2 tracks)."""
    right = COLUMN - 4
    d.rectangle((0, 0, right, PATTERN_H - 1), fill=1)
    tracks = engine.perform_tracks
    head = f"x{len(tracks)}" if len(tracks) > 1 else "TR"
    lines = (
        (engine.phrase.pattern or "---", (0, 0, right, PATTERN_H - 1), _font(20), 0),
        (f"{head} {engine.fader_track}", (0, PATTERN_H + 1, right, BAND - 1), _font(14), 1),
    )
    for text, box, font, ink in lines:
        for dx in (0, 1):
            _centered(d, (box[0] + dx, box[1], box[2] + dx, box[3]), text, font, ink)


def _left_band(
    img: Image.Image,
    d: ImageDraw.ImageDraw,
    engine: Engine,
    now: int,
    message: tuple[str, int] | None,
    warn: str,
) -> None:
    """Colonne DT2 (pattern, track) ; à sa droite la banque et sa tonalité, remplacées
    un instant par une alerte, le dernier geste ou la frappe ;
    dessous les 16 mutes et la double croche en cours, toujours visibles. Même vue en MPC
    et en clavier (revu le 2026-11-11)."""
    _dt2_column(d, engine)
    _mute_strip(d, engine)
    x = COLUMN + 2
    text = warn
    hit = engine.last_hit
    recent_hit = hit is not None and now - hit[3] < OVERLAY_NS
    newer = hit is None or not recent_hit or (message is not None and message[1] >= hit[3])
    if not text and message is not None and now - message[1] < MESSAGE_NS and newer:
        text = message[0]
    if not text and recent_hit and hit is not None:
        if not engine.last_hit_mpc:
            _hit_strip(img, engine, hit)
            return
        entry = engine.cfg.mpc_pad(hit[0])
        text = f"{entry.label}  T{entry.track:02d}  {entry.note}  v{hit[2]}"
    if text:
        _bold(d, (x, 2), text, _fit(d, text, WIDTH - x - 4, (16, 12)), 1)
        return
    sheet = engine.sheet
    if sheet is not None:  # banque puis tonalité : `E-TRIBE  Bb Phrygian`
        bank = sheet[1]
        tonic = f"{FLAT_NAMES[bank.tonic]} {engine.cfg.scale(bank.mode).name}"
        line = ascii_text(f"{sheet[0]}  {tonic}")
        font = _fit(d, line, WIDTH - x - 6, (18, 16, 14, 12))
        top = int(d.textbbox((0, 0), line, font=font)[1])
        _bold(d, (x, 5 - top), line, font, 1)


def _right_band(d: ImageDraw.ImageDraw, engine: Engine, now: int) -> None:
    """Phrase en noir sur blanc dans le coin gauche (`PHR 01`), mesure / longueur en gros,
    mesures avant le cap et pattern suivant ; à droite le mode de la MK2 et, dessous, le
    tempo lissé. Sous le tout, la barre de la phrase : trait tous les 8 mesures, pointillé
    à chaque tour de pattern (4 mesures)."""
    st = engine.phrase_state
    if st is not None and st.countdown is not None:  # bandeau inversé, compte à rebours
        d.rectangle((0, 0, WIDTH - 1, BAND - 1), fill=1)
        for dx in (0, 1):  # gras, centré dans la moitié gauche
            box = (dx, 0, WIDTH // 2 + dx, BAND - 1)
            _centered(d, box, str(st.countdown), _font(COUNTDOWN), 0)
        d.text((WIDTH // 2 + 8, 4), f"to {st.cap}", font=_font(16), fill=0)
        d.text((WIDTH // 2 + 8, 22), f"{st.bar} / {st.length}", font=_font(16), fill=0)
        _mode_tag(d, engine, ink=0)
        return
    if _announcing(engine, now):
        _announce_band(d, engine)
        _mode_tag(d, engine)
        return
    # coin gauche, comme le pattern de l'écran gauche : phrase en noir sur blanc
    phrase = f"PHR {st.phrase:02d}" if st is not None else "PHR --"
    font = _font(16)
    edge = int(d.textlength(phrase, font=font)) + 8
    d.rectangle((0, 0, edge, PATTERN_H - 1), fill=1)
    for dx in (0, 1):
        _centered(d, (dx, 0, edge + dx, PATTERN_H - 1), phrase, font, 0)
    bar = "--" if st is None else str(st.bar)
    count = f"{bar} / {engine.phrase.length}"
    _bold(d, (edge + 6, -4), count, _font(BAR), 1)
    x = edge + 14 + int(d.textlength(count, font=_font(BAR)))
    room = TAG_BOX[0] - x - 3
    if st is not None:  # mesures avant le cap
        line = f"-{st.to_cap} to {st.cap}"
        d.text((x, -2), line, font=_fit(d, line, room, (SMALL, 10, 9)), fill=1)
    nxt = engine.next_pattern
    side = f"> {nxt}" if nxt is not None else ""  # pattern suivant, à la fin de la phrase
    if not side and engine.keyboard and engine.octave:
        side = f"oct {engine.octave:+d}"
    if side:
        _bold(d, (x, 11), side, _fit(d, side, room, (SMALL, 10, 9)), 1)
    bpm = engine.clock.bpm_smooth  # sous l'étiquette du mode, lissé sur une mesure
    if bpm is not None:
        tempo, font = f"{bpm:.1f}", _font(13)
        _bold(d, (WIDTH - 3 - int(d.textlength(tempo, font=font)), 10), tempo, font, 1)
    _mode_tag(d, engine)
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
    done = left + round(cell * st.bar) if st is not None else left
    for b in range(PATTERN_BARS, length, PATTERN_BARS):
        x = left + round(cell * b)
        if b % BLOCK_BARS == 0:
            d.line((x, top - 2, x, bottom + 2), fill=ink)
        else:  # tour de pattern : pointillé dans la barre, en inverse de son fond
            dots = [(x, y) for y in range(top + 2, bottom - 1, 2)]
            d.point(dots, fill=1 - ink if x <= done else ink)


def _arp_faders(d: ImageDraw.ImageDraw, engine: Engine, touched: int | None, screen: int) -> None:
    """Config de l'arpège : ORD, OCT et GATE au-dessus des encodeurs 1-3, en toutes lettres."""
    small = _font(SMALL)
    for k, (name, value) in enumerate(engine.arp_view()):
        if k // COLS != screen:
            continue
        x = k % COLS * COL
        ink = 1
        if k == touched:
            d.rectangle((x, BAND + 1, x + COL - 2, HEIGHT - 1), fill=1)
            ink = 0
        _centered(d, (x + 2, BAND + 1, x + 26, HEIGHT - 1), name, small, ink)
        box = (x + 30, BAND + 1, x + COL - 4, HEIGHT - 1)
        _centered(d, box, value, _fit(d, value, box[2] - box[0], (12, 10)), ink)


def _faders(d: ImageDraw.ImageDraw, engine: Engine, now: int, screen: int) -> None:
    """Les 4 faders au-dessus des encodeurs de cet écran."""
    small = _font(SMALL)
    touched = None
    if engine.last_touch is not None and now - engine.last_touch[1] < OVERLAY_NS:
        touched = engine.last_touch[0] - 1
    if engine.arp_menu:
        _arp_faders(d, engine, touched, screen)
        return
    page = engine.cfg.encoders.pages[engine.faders.page_index]
    views = engine.faders.view(engine.fader_track)
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


SELECT_ROWS = 3  # lignes de projets visibles, autour de la choisie


def _selection_left(engine: Engine) -> Image.Image:
    """Liste des projets : la choisie en gros, inversée ; les voisines en petit."""
    img = new_image()
    d = ImageDraw.Draw(img)
    sel = engine.selector
    assert sel is not None
    _bold(d, (3, -2), "PROJECTS", _font(SMALL), 1)
    if sel.sync:
        f = _font(SMALL)
        d.text((WIDTH - 3 - d.textlength(sel.sync, font=f), -2), sel.sync, font=f, fill=1)
    if not sel.entries:
        d.text((3, 24), "no project in projects/", font=_font(SMALL), fill=1)
        return img
    first = max(0, min(sel.index - 1, len(sel.entries) - SELECT_ROWS))
    y = 13
    for i in range(first, min(first + SELECT_ROWS, len(sel.entries))):
        e = sel.entries[i]
        name = e.name.upper() + ("  !" if e.project is None else "")
        if i == sel.index:
            d.rectangle((0, y, WIDTH - 1, y + 20), fill=1)
            _bold(d, (4, y), name, _font(18), 0)
            y += 22
        else:
            d.text((4, y), name, font=_font(SMALL), fill=1)
            y += 14
    return img


def _selection_right(engine: Engine) -> Image.Image:
    """Projet choisi : banques et date, ou l'erreur ; les gestes dessous."""
    sel = engine.selector
    assert sel is not None
    e = sel.current
    if e is None:
        lines = ["", "", "SHIFT + BROWSE: back"]
    elif e.project is None:
        lines = [
            e.name.upper(),
            "invalid project",
            ascii_text(e.error)[-40:],
            "SHIFT + BROWSE: back",
        ]
    else:
        lines = [
            e.name.upper(),
            f"{e.banks} banks   {e.date}",
            "push: load",
            "SHIFT + BROWSE: back",
        ]
    return text_image(lines, bold=frozenset({0}))


def left(
    engine: Engine, now: int, message: tuple[str, int] | None = None, warn: str = ""
) -> Image.Image:
    """Écran gauche : bandeau de contexte, faders 1-4. Cadre en clavier (jamais confondu)."""
    if engine.selector is not None:
        return _selection_left(engine)
    img = new_image()
    d = ImageDraw.Draw(img)
    if _showing_repeat(engine):
        _repeat_band(d, engine, 0)
    else:
        _left_band(img, d, engine, now, message, warn)
    d.line((0, BAND, WIDTH - 1, BAND), fill=1)
    _faders(d, engine, now, 0)
    if engine.keyboard:
        d.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), outline=1)
    return img


def right(engine: Engine, now: int) -> Image.Image:
    """Écran droit : bandeau de phrase (MPC et clavier), faders 5-8."""
    if engine.selector is not None:
        return _selection_right(engine)
    img = new_image()
    d = ImageDraw.Draw(img)
    if _showing_repeat(engine):
        _repeat_band(d, engine, 1)
        _mode_tag(d, engine, TAG_BOX_REPEAT)
    else:
        _right_band(d, engine, now)
    d.line((0, BAND, WIDTH - 1, BAND), fill=1)
    _faders(d, engine, now, 1)
    return img

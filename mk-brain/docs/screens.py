"""Captures du guide utilisateur : écrans et LED rendus par le vrai code, sans matériel.

Chaque scène pilote un `Engine` comme les tests (gestes, horloge simulée à
143 BPM) puis assemble les deux écrans 256 × 64 (`render.left` / `render.right`)
et, en dessous, les LED GROUP et les 16 pads (`Engine.leds`).

    .venv/bin/python docs/screens.py          # → docs/img/*.png
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from mk_brain import render
from mk_brain.clock import ClockTracker
from mk_brain.config import Config, load_config
from mk_brain.engine import Engine
from mk_brain.hid_mk2 import ButtonEvent, EncoderEvent, PadEvent, pad_label
from mk_brain.project import Project, load_project
from mk_brain.selection import Selector, list_projects

OUT = Path(__file__).parent / "img"
MS = 1_000_000
SECOND = 1_000_000_000
TICK = round(60e9 / (24 * 143))  # 143 BPM
ZOOM = 3
INK = (225, 235, 255)  # pixel allumé de l'écran
BACK = (14, 16, 22)
FRAME = (40, 44, 52)
PAD = 54
GAP = 8


def _index(pad: int) -> int:
    """Index HID du pad imprimé `pad` (inverse de `pad_label`)."""
    return next(i for i in range(16) if pad_label(i) == pad)


def btn(eng: Engine, name: str, pressed: bool = True, t: int = 0) -> None:
    eng.handle(ButtonEvent(name, pressed), t)


def hit(eng: Engine, pad: int, t: int, pressure: int = 2500) -> None:
    eng.handle(PadEvent(_index(pad), True, pressure), t)
    eng.tick(t + 3 * MS)


def running(eng: Engine, bar: int, program: int | None = None) -> int:
    """Start, PC éventuel au début, horloge jusqu'à la mesure `bar` ; rend l'instant atteint."""
    eng.clock.start(0)
    eng.on_start()
    end = (bar - 1) * 96 + 10
    for k in range(end):
        eng.clock.tick(k * TICK)
        if k == 20 and program is not None:
            eng.on_program_change(program)
        if k % 6 == 0:
            eng.tick(k * TICK)
    now = (end - 1) * TICK
    eng.tick(now)
    return now


def to_keyboard(eng: Engine) -> None:
    btn(eng, "PAD_MODE")
    btn(eng, "PAD_MODE", False)


def _boost(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    """LED atténuée encore visible à l'image (courbe perceptuelle)."""
    return tuple(round(255 * (c / 255) ** 0.45) for c in rgb)  # type: ignore[return-value]


def _screen(img: Image.Image) -> Image.Image:
    rgb = Image.new("RGB", img.size, BACK)
    rgb.paste(INK, mask=img.convert("L"))
    return rgb.resize((img.width * ZOOM, img.height * ZOOM), Image.Resampling.NEAREST)


def compose(eng: Engine, now: int, pads: bool = True) -> Image.Image:
    left, right = _screen(render.left(eng, now)), _screen(render.right(eng, now))
    w = left.width + right.width + 3 * GAP * 2
    h = left.height + 2 * GAP * 2
    leds = eng.leds()
    grid_w = 4 * PAD + 3 * GAP
    if pads:
        h += 26 + GAP + 4 * PAD + 3 * GAP + 2 * GAP
    out = Image.new("RGB", (w, h), FRAME)
    out.paste(left, (2 * GAP, 2 * GAP))
    out.paste(right, (left.width + 4 * GAP, 2 * GAP))
    if not pads:
        return out
    d = ImageDraw.Draw(out)
    font = ImageFont.load_default(13)
    y0 = left.height + 4 * GAP
    gx = (w - 8 * 34) // 2
    for g, rgb in enumerate(leds.groups):  # LED GROUP A-H
        x = gx + g * 34
        d.rounded_rectangle((x, y0, x + 28, y0 + 18), 4, fill=_boost(rgb), outline=(70, 74, 82))
        ink = (0, 0, 0) if sum(rgb) > 200 else (120, 124, 132)
        d.text((x + 10, y0 + 2), "ABCDEFGH"[g], fill=ink, font=font)
    px = (w - grid_w) // 2
    py = y0 + 26 + GAP
    for index, rgb in enumerate(leds.pads):  # index 0 = pad 13, en haut à gauche
        row, col = divmod(index, 4)
        x, y = px + col * (PAD + GAP), py + row * (PAD + GAP)
        d.rounded_rectangle((x, y, x + PAD, y + PAD), 6, fill=_boost(rgb), outline=(70, 74, 82))
        dark = sum(_boost(rgb)) > 380
        ink = (0, 0, 0) if dark else (150, 154, 162)
        d.text((x + 4, y + 2), str(pad_label(index)), fill=ink, font=font)
    return out


Scene = Callable[[Config, Project], tuple[Engine, int, bool]]


def selection(cfg: Config, project: Project) -> tuple[Engine, int, bool]:
    eng = Engine(cfg, catalog=lambda: Selector(list_projects(), "solaris"))
    eng.open_selection()
    return eng, 0, False


def live_stopped(cfg: Config, project: Project) -> tuple[Engine, int, bool]:
    eng = Engine(cfg, ClockTracker(), project)
    return eng, 0, True


def live_playing(cfg: Config, project: Project) -> tuple[Engine, int, bool]:
    eng = Engine(cfg, ClockTracker(), project)
    now = running(eng, 11, program=4 * 16 + 2)  # E03
    return eng, now + 3 * SECOND, True


def live_announce(cfg: Config, project: Project) -> tuple[Engine, int, bool]:
    eng = Engine(cfg, ClockTracker(), project)
    now = running(eng, 2, program=4 * 16)  # E01, annonce de la banque
    return eng, now, True


def live_countdown(cfg: Config, project: Project) -> tuple[Engine, int, bool]:
    eng = Engine(cfg, ClockTracker(), project)
    now = running(eng, 31, program=4 * 16 + 2)
    return eng, now + 3 * SECOND, True


def live_encoder(cfg: Config, project: Project) -> tuple[Engine, int, bool]:
    eng = Engine(cfg, ClockTracker(), project)
    now = running(eng, 5, program=4 * 16 + 2)
    btn(eng, "SELECT", t=now)
    hit(eng, 9, now)
    btn(eng, "SELECT", False, t=now)
    for _ in range(8):
        eng.handle(EncoderEvent(2, 4, 0), now)  # BR
    eng.handle(EncoderEvent(3, -12, 0), now)
    return eng, now + 100 * MS, True


def live_repeat(cfg: Config, project: Project) -> tuple[Engine, int, bool]:
    eng = Engine(cfg, ClockTracker(), project)
    now = running(eng, 9, program=4 * 16 + 2)
    btn(eng, "NOTE_REPEAT", t=now)
    hit(eng, 8, now, 1800)  # CH : T5
    return eng, now + 10 * MS, True


def live_mute(cfg: Config, project: Project) -> tuple[Engine, int, bool]:
    eng = Engine(cfg, ClockTracker(), project)
    now = running(eng, 17, program=4 * 16 + 2)
    for t in (9, 10, 11, 12, 13, 14):  # break percussif : seconde rangée coupée
        eng.faders.muted[t] = True
    btn(eng, "MUTE", t=now)
    return eng, now + 3 * SECOND, True


def mpc_hit(cfg: Config, project: Project) -> tuple[Engine, int, bool]:
    eng = Engine(cfg, ClockTracker(), project)
    now = running(eng, 6, program=4 * 16 + 2)
    hit(eng, 12, now, 1600)  # OH : T5, tranche 62
    return eng, now + 20 * MS, True


def design_chroma(cfg: Config, project: Project) -> tuple[Engine, int, bool]:
    eng = Engine(cfg, ClockTracker(), project)
    to_keyboard(eng)
    btn(eng, "SELECT")
    hit(eng, 13, 0)  # clavier sur la track 13 (Id2)
    btn(eng, "SELECT", False)
    btn(eng, "GROUP_E")
    eng.group = 0  # chromatique
    hit(eng, 4, 2 * SECOND, 1500)  # tierce mineure
    return eng, 2 * SECOND + 20 * MS, True


def design_scale(cfg: Config, project: Project) -> tuple[Engine, int, bool]:
    eng = Engine(cfg, ClockTracker(), project)
    to_keyboard(eng)
    btn(eng, "GROUP_A")  # banque A : disposition de son mode
    return eng, 3 * SECOND, True


def perform(cfg: Config, project: Project) -> tuple[Engine, int, bool]:
    eng = Engine(cfg, ClockTracker(), project)
    now = running(eng, 12, program=4 * 16 + 2)
    btn(eng, "SOLO", t=now)
    for pad in (3, 7):  # T3 et T7 dans le groupe
        eng.handle(PadEvent(_index(pad), True, 2500), now)
        eng.handle(PadEvent(_index(pad), False, 0), now)
    btn(eng, "BROWSE_RIGHT", t=now)  # page 2 : filtre
    for _ in range(6):
        eng.handle(EncoderEvent(2, 8, 0), now)  # CUT des deux tracks
    return eng, now + 3 * SECOND, True


def arpeggio(cfg: Config, project: Project) -> tuple[Engine, int, bool]:
    eng = Engine(cfg, ClockTracker(), project)
    now = running(eng, 12, program=4 * 16 + 2)
    btn(eng, "SELECT", t=now)
    hit(eng, 10, now)  # track 10 pour l'arpège
    eng.handle(PadEvent(_index(10), False, 0), now)
    btn(eng, "SELECT", False, t=now)
    btn(eng, "PATTERN", t=now)  # tenu : la config de l'arpège à l'écran
    eng.handle(EncoderEvent(5, 6 * cfg.arp.raw_per_choice, 0), now)  # PRE NAPP
    for pad in (1, 3, 5):
        hit(eng, pad, now)
    return eng, now + 3 * SECOND, True


SCENES: dict[str, Scene] = {
    "01-selection": selection,
    "02-mpc-arret": live_stopped,
    "03-mpc-annonce": live_announce,
    "04-mpc-jeu": live_playing,
    "05-mpc-frappe": mpc_hit,
    "06-compte-a-rebours": live_countdown,
    "07-encodeur": live_encoder,
    "08-repeat": live_repeat,
    "09-mute": live_mute,
    "10-clavier-chromatique": design_chroma,
    "11-clavier-gamme": design_scale,
    "12-perform": perform,
    "13-arpege": arpeggio,
}


def main() -> None:
    cfg = load_config()
    project = load_project()
    OUT.mkdir(exist_ok=True)
    for name, scene in SCENES.items():
        eng, now, pads = scene(cfg, project)
        compose(eng, now, pads).save(OUT / f"{name}.png")
        print(name)


if __name__ == "__main__":
    main()

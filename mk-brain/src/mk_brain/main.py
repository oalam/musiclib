"""CLI mk-brain : `spike` (slice 0, HID), `play` (slices 1-5, pads → DT2), `clock` (slice 2)."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING

from mk_brain import display, render
from mk_brain.clock import ClockTracker
from mk_brain.config import ConfigError
from mk_brain.hid_mk2 import (
    BUTTON_LEDS,
    BUTTONS,
    GROUPS,
    LED_MAX,
    N_ENCODERS,
    N_PADS,
    REPORT_PADS,
    TRANSPORT_LEDS,
    ButtonEvent,
    EncoderEvent,
    InputDecoder,
    LedState,
    Mk2Device,
    Mk2Error,
    PadEvent,
    enumerate_mk2,
    pad_label,
)
from mk_brain.midi_io import MidiError
from mk_brain.project import DEFAULT_PROJECT, ProjectError

if TYPE_CHECKING:
    pass

RAINBOW: list[tuple[int, int, int]] = [
    (255, 0, 0), (255, 128, 0), (255, 255, 0), (0, 255, 0),
    (0, 255, 255), (0, 0, 255), (128, 0, 255), (255, 0, 255),
]  # fmt: skip
OFF = (0, 0, 0)
FRAME_NS = 50_000_000  # écrans redessinés au plus toutes les 50 ms, envoyés s'ils changent


def cmd_list() -> int:
    infos = enumerate_mk2()
    if not infos:
        print("aucune MK2 en HID")
        return 1
    for info in infos:
        print(
            f"{info.get('product_string')} · interface {info.get('interface_number')} · "
            f"usage_page 0x{info.get('usage_page', 0):04x} · path {info.get('path')!r}"
        )
    return 0


def _show(dev: Mk2Device, screen: int, image: object) -> None:
    from PIL import Image

    assert isinstance(image, Image.Image)
    for report in display.frame_reports(screen, display.image_to_frame(image)):
        dev.write(report)


def _led_chase(dev: Mk2Device, step_s: float) -> None:
    """Allume chaque LED une à une, dans l'ordre des tables : vérifie leur position."""
    for name in [*BUTTON_LEDS, *TRANSPORT_LEDS]:
        dev.send_leds(LedState(LedState.off().pads, LedState.off().groups, {name: LED_MAX}))
        time.sleep(step_s)
    for g in range(len(GROUPS)):
        leds = LedState.off()
        leds.groups[g] = RAINBOW[g]
        dev.send_leds(leds)
        time.sleep(step_s)
    for p in range(N_PADS):
        leds = LedState.off()
        leds.pads[p] = RAINBOW[p % len(RAINBOW)]
        dev.send_leds(leds)
        time.sleep(step_s)


def cmd_spike(chase: bool, raw: bool, step_s: float) -> int:
    dev = Mk2Device.open()
    decoder = InputDecoder()
    leds = LedState.off()
    seen_buttons: set[str] = set()
    seen_pads: set[int] = set()
    seen_encoders: set[int] = set()
    held: set[int] = set()
    log: list[str] = ["spike slice 0", "touchez tout ; Ctrl-C = bilan"]
    last_raw_pads = b""
    screen_dirty = True
    last_draw = 0.0
    try:
        _show(dev, 0, display.mire(0))
        _show(dev, 1, display.mire(1))
        if chase:
            _led_chase(dev, step_s)
        dev.send_leds(leds)
        print("prêt : appuyez sur chaque bouton, pad et encodeur. Ctrl-C pour le bilan.")
        while True:
            report = dev.read(timeout_ms=10)
            if report and raw and (report[0] != REPORT_PADS or report != last_raw_pads):
                print("raw", report.hex(" "))
                if report[0] == REPORT_PADS:
                    last_raw_pads = report
            changed_leds = False
            for ev in decoder.feed(report):
                if isinstance(ev, ButtonEvent):
                    seen_buttons.add(ev.name)
                    leds.buttons[ev.name] = LED_MAX if ev.pressed else 0
                    if ev.name.startswith("GROUP_"):
                        g = GROUPS.index(ev.name[-1])
                        leds.groups[g] = RAINBOW[g] if ev.pressed else (0, 0, 0)
                    msg = f"{ev.name} {'on' if ev.pressed else 'off'}"
                    changed_leds = True
                elif isinstance(ev, EncoderEvent):
                    seen_encoders.add(ev.index)
                    who = "MAITRE" if ev.index == 0 else f"ENC{ev.index}"
                    msg = f"{who} {ev.delta:+d} ({ev.raw})"
                else:
                    assert isinstance(ev, PadEvent)
                    level = min(255, ev.pressure // 16)
                    leds.pads[ev.index] = (level, level // 2, 255 - level) if ev.pressed else OFF
                    changed_leds = True
                    if ev.pressed and ev.index in held:
                        continue  # pression qui varie : LED seulement, pas de log
                    (held.add if ev.pressed else held.discard)(ev.index)
                    seen_pads.add(ev.index)
                    msg = (
                        f"pad idx {ev.index} (label {pad_label(ev.index)}) "
                        f"{'on ' + str(ev.pressure) if ev.pressed else 'off'}"
                    )
                    changed_leds = True
                print(msg)
                log.append(msg)
                screen_dirty = True
            if changed_leds:
                dev.send_leds(leds)
            now = time.monotonic()
            if screen_dirty and now - last_draw > 0.05:
                _show(dev, 1, display.text_image(log))
                screen_dirty, last_draw = False, now
    except KeyboardInterrupt:
        pass
    finally:
        try:
            dev.send_leds(LedState.off())
            for s in range(display.N_DISPLAYS):
                _show(dev, s, display.new_image())
        finally:
            dev.close()

    print("\n--- bilan ---")
    print(f"boutons vus  {len(seen_buttons)}/{len(BUTTONS)}")
    print("  jamais vus :", ", ".join(b for b in BUTTONS if b not in seen_buttons) or "-")
    print(f"pads vus     {len(seen_pads)}/{N_PADS}")
    print("  jamais vus :", ", ".join(str(p) for p in range(N_PADS) if p not in seen_pads) or "-")
    print(f"encodeurs vus {len(seen_encoders)}/{N_ENCODERS + 1} (0 = maître)")
    print(
        "  jamais vus :",
        ", ".join(str(e) for e in range(N_ENCODERS + 1) if e not in seen_encoders) or "-",
    )
    return 0


def _clock_line(clock: ClockTracker) -> str:
    bpm = f"{clock.bpm:5.1f}" if clock.bpm else "  -- "
    pos = clock.position()
    return f"{bpm} bpm  {'>' if clock.running else '[]'}  {pos or '-'}"


def cmd_play(dry_run: bool, project_path: Path) -> int:
    from mk_brain.config import load_config
    from mk_brain.engine import Engine, MidiOut, Timed
    from mk_brain.layouts import describe_note
    from mk_brain.midi_io import Dt2In, Dt2Out, feed_engine
    from mk_brain.project import load_project
    from mk_brain.scheduler import Scheduler

    cfg = load_config()
    project = load_project(project_path)
    clock = ClockTracker()
    engine = Engine(cfg, clock, project)
    decoder = InputDecoder(pad_threshold=cfg.velocity.threshold)
    out = None if dry_run else Dt2Out.open(cfg.midi.port_hint)
    inp = None if dry_run else Dt2In.open(cfg.midi.port_hint)
    sched: Scheduler[MidiOut] | None = Scheduler(out.send) if out is not None else None
    dev = Mk2Device.open()
    last = "-"
    message: tuple[str, int] | None = None  # dernier geste de contrôle, 2e ligne du bandeau gauche
    shown: list[bytes] = [b"", b""]  # dernière image envoyée par écran
    last_draw = 0

    def emit(msgs: list[Timed]) -> None:
        nonlocal last
        for t, m in msgs:
            if sched is not None:
                sched.at(t, m)  # un seul fil écrit sur le port, même pour l'immédiat
        if msgs and engine.last_played is not None:
            pad, note, vel = engine.last_played
            text = f"{describe_note(engine.layout, pad, note)} vel {vel}"
            if text != last or engine.last_decision:
                last = text
                print(f"{last}   {engine.last_decision}")
                engine.last_decision = ""

    print(
        f"play : {'essai sans DT2' if dry_run else 'DT2'} ; mode live ; "
        "SHIFT + CONTROL 1 s puis appui maître = changer de mode ; "
        "SHIFT + PLAY / GROUP n = recalage de la phrase ; Ctrl-C"
    )
    try:
        if sched is not None:
            sched.start()
        _show(dev, 1, display.new_image())
        while True:
            report = dev.read(timeout_ms=1)
            now = time.perf_counter_ns()
            if inp is not None:
                for ev in inp.drain():
                    feed_engine(engine, ev)
                    if ev.kind in ("start", "stop"):
                        print(f"{ev.kind} {_clock_line(clock)}")
            for hid_ev in decoder.feed(report):
                emit(engine.handle(hid_ev, now))
            emit(engine.tick(now))
            if engine.last_control:
                last = engine.last_control
                message = (last, now)
                print(last)
                engine.last_control = ""
            for line in engine.log:
                print(f"{line}   ({_clock_line(clock)})")
            engine.log.clear()
            if engine.leds_dirty:
                dev.send_leds(engine.leds())
            if now - last_draw < FRAME_NS:
                continue
            last_draw = now
            warn = "TRANSFER OUVERT ?" if clock.transfer_suspected(now) else ""
            if clock.bpm is None and not dry_run:
                warn = warn or "pas de clock"
            left = render.left(engine, now, message, warn)  # cadre et bandeau DESIGN en design
            for screen, img in enumerate((left, render.right(engine, now))):
                frame = display.image_to_frame(img)
                if frame != shown[screen]:
                    for report in display.frame_reports(screen, frame):
                        dev.write(report)
                    shown[screen] = frame
    except KeyboardInterrupt:
        pass
    finally:
        try:
            dev.send_leds(LedState.off())
            for s in range(display.N_DISPLAYS):
                _show(dev, s, display.new_image())
        finally:
            dev.close()
            if sched is not None:
                sched.close()
            if out is not None:
                out.close()
            if inp is not None:
                inp.close()
    print(f"clock, écart d'arrivée des ticks à la prévision : {clock.prediction_error.summary()}")
    if sched is not None:
        print(f"envoi vs cible : {sched.errors.summary()} ; abandonnés : {sched.dropped}")
    return 0


def cmd_clock(bench_note: int | None, every: int) -> int:
    """Banc d'horloge : BPM, transport, gigue d'arrivée ; option envoi calé sur la grille."""
    from mk_brain.config import load_config
    from mk_brain.engine import MidiOut, NoteOff, NoteOn
    from mk_brain.midi_io import Dt2In, Dt2Out, feed_clock
    from mk_brain.scheduler import Scheduler

    cfg = load_config()
    channel = cfg.midi.auto_channel - 1
    clock = ClockTracker()
    inp = Dt2In.open(cfg.midi.port_hint)
    out = Dt2Out.open(cfg.midi.port_hint) if bench_note is not None else None
    sched: Scheduler[MidiOut] | None = Scheduler(out.send) if out is not None else None
    if sched is not None:
        sched.start()
    next_pos: int | None = None
    last_print = 0.0
    print(
        "clock : Ctrl-C pour le bilan"
        + (f" ; banc : note {bench_note} tous les {every} ticks" if sched else "")
    )
    try:
        while True:
            for ev in inp.drain():
                feed_clock(clock, ev)
                if ev.kind in ("start", "stop", "continue"):
                    print(ev.kind)
                    next_pos = None
            k = clock.ticks_since_start
            if sched is not None and bench_note is not None and k is not None:
                if next_pos is None:
                    next_pos = (k // every + 1) * every
                # confié 20 ms avant la cible, prise sur la droite de régression
                t = clock.position_time(next_pos)
                if t is not None and t - time.perf_counter_ns() < 20_000_000:
                    sched.at(int(t), NoteOn(channel, bench_note, 100))
                    sched.at(int(t) + 20_000_000, NoteOff(channel, bench_note))
                    next_pos += every
            now = time.monotonic()
            if now - last_print > 1.0:
                warn = (
                    "  TRANSFER OUVERT ?"
                    if clock.transfer_suspected(time.perf_counter_ns())
                    else ""
                )
                print(_clock_line(clock) + warn)
                last_print = now
            time.sleep(0.0005)
    except KeyboardInterrupt:
        pass
    finally:
        if sched is not None:
            sched.close()
        if out is not None:
            out.close()
        inp.close()
    print("\n--- bilan ---")
    print(f"BPM final : {clock.bpm}")
    print(f"arrivée des ticks vs prévision : {clock.prediction_error.summary()}")
    if sched is not None:
        print(f"envoi vs cible : {sched.errors.summary()} ; abandonnés : {sched.dropped}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mk-brain")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="lister les interfaces HID de la MK2")
    sp = sub.add_parser("spike", help="banc d'essai slice 0 : mire, LED, décodage")
    sp.add_argument("--no-chase", action="store_true", help="sauter le balayage des LED")
    sp.add_argument("--raw", action="store_true", help="afficher les rapports bruts en hexa")
    sp.add_argument("--step", type=float, default=0.15, help="pas du balayage LED (s)")
    pp = sub.add_parser("play", help="slice 1 : pads → notes DT2 sur l'AUTO CHANNEL")
    pp.add_argument("--dry-run", action="store_true", help="sans DT2 : notes affichées seulement")
    pp.add_argument(
        "--project", type=Path, default=DEFAULT_PROJECT, help="projet du set (banques du design)"
    )
    cp = sub.add_parser("clock", help="slice 2 : horloge DT2, BPM, gigue ; banc d'envoi")
    cp.add_argument("--bench-note", type=int, help="note envoyée sur la grille (ex. 3 = track 4)")
    cp.add_argument(
        "--every", type=int, default=24, help="intervalle du banc en ticks (24 = noire)"
    )
    args = parser.parse_args(argv)
    try:
        if args.cmd == "list":
            return cmd_list()
        if args.cmd == "play":
            return cmd_play(dry_run=args.dry_run, project_path=args.project)
        if args.cmd == "clock":
            return cmd_clock(bench_note=args.bench_note, every=args.every)
        return cmd_spike(chase=not args.no_chase, raw=args.raw, step_s=args.step)
    except (Mk2Error, ConfigError, MidiError, ProjectError) as exc:
        print(f"erreur : {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

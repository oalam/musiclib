"""CLI mk-brain : `spike` (slice 0, banc d'essai HID), `play` (slice 1, relais pads → DT2)."""

from __future__ import annotations

import argparse
import sys
import time

from mk_brain import display
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

RAINBOW: list[tuple[int, int, int]] = [
    (255, 0, 0), (255, 128, 0), (255, 255, 0), (0, 255, 0),
    (0, 255, 255), (0, 0, 255), (128, 0, 255), (255, 0, 255),
]  # fmt: skip
OFF = (0, 0, 0)


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


def cmd_play(dry_run: bool) -> int:
    from mk_brain.config import load_config
    from mk_brain.engine import Engine, MidiOut, NoteOn
    from mk_brain.midi_io import Dt2Out

    cfg = load_config()
    engine = Engine(cfg)
    decoder = InputDecoder(pad_threshold=cfg.velocity.threshold)
    out = None if dry_run else Dt2Out.open(cfg.midi.port_hint)
    dev = Mk2Device.open()
    last = "-"
    screen_dirty, last_draw = True, 0.0

    def emit(msgs: list[MidiOut]) -> None:
        nonlocal last, screen_dirty
        for m in msgs:
            if out is not None:
                out.send(m)
            if isinstance(m, NoteOn):
                last = f"note {m.note} vel {m.velocity} ch {m.channel + 1}"
                print(last)
                screen_dirty = True

    print(f"play : {'essai sans DT2' if dry_run else 'DT2'} ; GROUP A-H = disposition ; Ctrl-C")
    try:
        _show(dev, 1, display.new_image())
        while True:
            report = dev.read(timeout_ms=1)
            now = time.perf_counter()
            group = engine.group
            for ev in decoder.feed(report):
                emit(engine.handle(ev, now))
            emit(engine.tick(now))
            if engine.group != group:
                screen_dirty = True
            if engine.leds_dirty:
                dev.send_leds(engine.leds())
            if screen_dirty and now - last_draw > 0.05:
                lay = cfg.layouts[engine.group]
                lines = [
                    f"mk-brain  slice 1  {'ESSAI' if dry_run else 'DT2'}",
                    f"groupe {lay.group}  {lay.name}",
                    f"canal {cfg.midi.auto_channel}",
                    last,
                ]
                _show(dev, 0, display.text_image(lines))
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
            if out is not None:
                out.close()
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
    args = parser.parse_args(argv)
    try:
        if args.cmd == "list":
            return cmd_list()
        if args.cmd == "play":
            return cmd_play(dry_run=args.dry_run)
        return cmd_spike(chase=not args.no_chase, raw=args.raw, step_s=args.step)
    except (Mk2Error, ConfigError, MidiError) as exc:
        print(f"erreur : {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

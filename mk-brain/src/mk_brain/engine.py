"""Moteur : seul propriétaire de l'état, sans HID ni MIDI (testable à l'horloge simulée).

Rend des messages datés `(instant_ns, message)` que l'ordonnanceur envoie.
- Slice 1 : pads → notes ; GROUP A-H choisit la disposition (provisoire,
  l'affectation définitive des GROUP se décide à la slice 5).
- Slice 3 : quantize « nearest » (GRID), swing (SWING + encodeur maître),
  note repeat (NOTE REPEAT tenu, SHIFT + NOTE REPEAT verrouille, boutons
  d'écran 1-8 = division). Sans transport lancé : envoi immédiat, sans repeat.
"""

from __future__ import annotations

from dataclasses import dataclass

from mk_brain.clock import ClockTracker
from mk_brain.config import RGB, Config
from mk_brain.hid_mk2 import (
    GROUPS,
    LED_MAX,
    ButtonEvent,
    EncoderEvent,
    Event,
    LedState,
    PadEvent,
    pad_label,
)
from mk_brain.layouts import N_PADS, pad_color, pad_note, scale, velocity
from mk_brain.quantize import (
    GRID_TICKS,
    QUANTIZE_CYCLE,
    QuantizeMode,
    clamp_swing,
    nearest,
    swing_offset,
)
from mk_brain.repeat import DIVISION_TICKS, DIVISIONS, GATE

NOTE_OFF_MIN_NS = 5_000_000  # note off au moins 5 ms après sa note on


@dataclass(frozen=True, slots=True)
class NoteOn:
    channel: int  # 0-15, comme mido
    note: int
    velocity: int


@dataclass(frozen=True, slots=True)
class NoteOff:
    channel: int
    note: int


MidiOut = NoteOn | NoteOff
Timed = tuple[int, MidiOut]


@dataclass
class _Attack:
    start: int
    peak: int


@dataclass
class _Repeat:
    note: int
    next_pos: float


class Engine:
    def __init__(self, cfg: Config, clock: ClockTracker | None = None) -> None:
        self.cfg = cfg
        self.clock = clock or ClockTracker()
        self.channel = cfg.midi.auto_channel - 1
        self.group = 0
        self.quantize: QuantizeMode = cfg.play.quantize
        self.swing = cfg.play.swing
        self.division: str = cfg.play.repeat
        self.repeat_held = False
        self.repeat_locked = False
        self._held_buttons: set[str] = set()
        self._attacks: dict[int, _Attack] = {}  # pad 1-16 → attaque en cours de mesure
        self._sounding: dict[int, tuple[int, int]] = {}  # pad → (note, instant de la note on)
        self._repeats: dict[int, _Repeat] = {}
        self._pressure: dict[int, int] = {}
        self.leds_dirty = True
        self.last_played: tuple[int, int, int] | None = None  # (pad, note, vélocité)

    @property
    def repeat_active(self) -> bool:
        return self.repeat_held or self.repeat_locked

    # --- entrées ------------------------------------------------------------

    def handle(self, ev: Event, now: int) -> list[Timed]:
        if isinstance(ev, ButtonEvent):
            self._button(ev)
            return []
        if isinstance(ev, EncoderEvent):
            if ev.index == 0 and "SWING" in self._held_buttons:
                self.swing = clamp_swing(self.swing + ev.delta)
            return []
        return self._pad(pad_label(ev.index), ev, now)

    def _button(self, ev: ButtonEvent) -> None:
        name = ev.name
        if not ev.pressed:
            self._held_buttons.discard(name)
            if name == "NOTE_REPEAT":
                self.repeat_held = False
                if not self.repeat_locked:
                    self._repeats.clear()
                self.leds_dirty = True
            return
        self._held_buttons.add(name)
        if name.startswith("GROUP_"):
            self.group = GROUPS.index(name[-1])
        elif name == "GRID":
            i = QUANTIZE_CYCLE.index(self.quantize)
            self.quantize = QUANTIZE_CYCLE[(i + 1) % len(QUANTIZE_CYCLE)]
        elif name == "NOTE_REPEAT":
            if "SHIFT" in self._held_buttons:
                self.repeat_locked = not self.repeat_locked
                if not self.repeat_locked:
                    self._repeats.clear()
            else:
                self.repeat_held = True
        elif name.startswith("DISPLAY_") and self.repeat_active:
            self.division = DIVISIONS[int(name[-1]) - 1][0]
        else:
            return
        self.leds_dirty = True

    def _pad(self, pad: int, ev: PadEvent, now: int) -> list[Timed]:
        if ev.pressed:
            was_held = pad in self._pressure
            self._pressure[pad] = ev.pressure
            if pad in self._attacks:
                att = self._attacks[pad]
                att.peak = max(att.peak, ev.pressure)
            elif not was_held:  # pad tenu à la fin d'un repeat : pas de nouvelle frappe
                self._attacks[pad] = _Attack(now, ev.pressure)
                self.leds_dirty = True
            return self.tick(now)
        # relâché
        self._pressure.pop(pad, None)
        out: list[Timed] = []
        if pad in self._attacks:
            out += self._fire(pad, now)
        if self._repeats.pop(pad, None) is not None:
            self.leds_dirty = True
        if pad in self._sounding:
            note, on_at = self._sounding.pop(pad)
            out.append((max(now, on_at + NOTE_OFF_MIN_NS), NoteOff(self.channel, note)))
            self.leds_dirty = True
        return out

    # --- temps ----------------------------------------------------------------

    def tick(self, now: int) -> list[Timed]:
        """Attaques dont la fenêtre de vélocité est écoulée, coups de repeat à venir."""
        window = int(self.cfg.velocity.window_ms * 1e6)
        out: list[Timed] = []
        for pad in [p for p, a in self._attacks.items() if now - a.start >= window]:
            out += self._fire(pad, now)
        horizon = now + int(self.cfg.play.horizon_ms * 1e6)
        div = DIVISION_TICKS[self.division]
        for pad, rep in self._repeats.items():
            while (t := self._time_of(rep.next_pos)) is not None and t < horizon:
                vel = velocity(self.cfg.velocity, self._pressure.get(pad, 0))
                gate = self._time_of(rep.next_pos + div * GATE) or t + NOTE_OFF_MIN_NS
                out.append((max(t, now), NoteOn(self.channel, rep.note, vel)))
                out.append((max(gate, now + NOTE_OFF_MIN_NS), NoteOff(self.channel, rep.note)))
                self.last_played = (pad, rep.note, vel)
                rep.next_pos += div
        return out

    def _time_of(self, position: float) -> int | None:
        t = self.clock.position_time(position + swing_offset(position, self.swing))
        return None if t is None else int(t)

    def _fire(self, pad: int, now: int) -> list[Timed]:
        att = self._attacks.pop(pad)
        note = pad_note(self.cfg.layouts[self.group], pad)
        vel = velocity(self.cfg.velocity, att.peak)
        self.last_played = (pad, note, vel)
        ticks = self.clock.ticks_at(att.start)  # instant de la frappe, pas de la fin de fenêtre
        if ticks is None:  # transport arrêté : immédiat, pas de repeat
            self._sounding[pad] = (note, now)
            return [(now, NoteOn(self.channel, note, vel))]
        if self.repeat_active:
            pos, _ = nearest(ticks, DIVISION_TICKS[self.division])
            self._repeats[pad] = _Repeat(note, pos)
            return self.tick(now)
        target = now
        if self.quantize != "off":
            pos, immediate = nearest(ticks, GRID_TICKS[self.quantize])
            t = self._time_of(pos)
            if not immediate and t is not None:
                target = max(now, t)
        self._sounding[pad] = (note, target)
        return [(target, NoteOn(self.channel, note, vel))]

    # --- sorties ----------------------------------------------------------------

    def status(self) -> str:
        q = "Qoff" if self.quantize == "off" else f"Q{self.quantize[2:]}"
        rep = f"  R{self.division}{'*' if self.repeat_locked else ''}" if self.repeat_active else ""
        return f"{q}  SW{self.swing}{rep}"

    def leds(self) -> LedState:
        layout = self.cfg.layouts[self.group]
        dim = self.cfg.leds.dim
        lit = set(self._attacks) | set(self._sounding) | set(self._repeats)
        pads: list[RGB] = [(0, 0, 0)] * N_PADS
        for index in range(N_PADS):
            pad = pad_label(index)
            full = pad_color(self.cfg, layout, pad)
            pads[index] = full if pad in lit else scale(full, dim)
        groups = [
            scale(self.cfg.families[lay.family], 1.0 if g == self.group else dim)
            for g, lay in enumerate(self.cfg.layouts)
        ]
        low = round(LED_MAX * dim)
        buttons = {
            "GRID": LED_MAX if self.quantize != "off" else 0,
            "NOTE_REPEAT": LED_MAX if self.repeat_active else 0,
            "SWING": LED_MAX if self.swing > 50 else 0,
        }
        if self.repeat_active:
            for i, (name, _) in enumerate(DIVISIONS):
                buttons[f"DISPLAY_{i + 1}"] = LED_MAX if name == self.division else low
        self.leds_dirty = False
        return LedState(pads=pads, groups=groups, buttons=buttons)

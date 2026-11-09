"""Moteur : seul propriétaire de l'état, sans HID ni MIDI (testable à l'horloge simulée).

Slice 1 : relais pads → notes, sans horloge. GROUP A-H choisit la disposition
(comme le template DT2 Pads ; provisoire, l'affectation définitive des GROUP
se décide à la slice 5).
"""

from __future__ import annotations

from dataclasses import dataclass

from mk_brain.config import RGB, Config
from mk_brain.hid_mk2 import GROUPS, ButtonEvent, Event, LedState, PadEvent, pad_label
from mk_brain.layouts import N_PADS, pad_color, pad_note, scale, velocity


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


@dataclass
class _Attack:
    start: float
    peak: int


class Engine:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.channel = cfg.midi.auto_channel - 1
        self.group = 0
        self._attacks: dict[int, _Attack] = {}  # pad 1-16 → attaque en cours de mesure
        self._sounding: dict[int, int] = {}  # pad 1-16 → note envoyée (pour le note off)
        self.leds_dirty = True

    @property
    def layout_name(self) -> str:
        return self.cfg.layouts[self.group].name

    def handle(self, ev: Event, now: float) -> list[MidiOut]:
        if isinstance(ev, ButtonEvent):
            if ev.pressed and ev.name.startswith("GROUP_"):
                self.group = GROUPS.index(ev.name[-1])
                self.leds_dirty = True
            return []
        if isinstance(ev, PadEvent):
            return self._pad(pad_label(ev.index), ev, now)
        return []

    def _pad(self, pad: int, ev: PadEvent, now: float) -> list[MidiOut]:
        out: list[MidiOut] = []
        if ev.pressed:
            if pad in self._attacks:
                att = self._attacks[pad]
                att.peak = max(att.peak, ev.pressure)
            elif pad not in self._sounding:
                self._attacks[pad] = _Attack(now, ev.pressure)
                self.leds_dirty = True
            out += self.tick(now)
            return out
        # relâché : une attaque plus courte que la fenêtre part tout de suite
        if pad in self._attacks:
            out.append(self._fire(pad))
        if pad in self._sounding:
            out.append(NoteOff(self.channel, self._sounding.pop(pad)))
            self.leds_dirty = True
        return out

    def tick(self, now: float) -> list[MidiOut]:
        """Envoie les attaques dont la fenêtre de vélocité est écoulée."""
        window = self.cfg.velocity.window_ms / 1000
        due = [p for p, a in self._attacks.items() if now - a.start >= window]
        return [self._fire(p) for p in due]

    def _fire(self, pad: int) -> NoteOn:
        att = self._attacks.pop(pad)
        note = pad_note(self.cfg.layouts[self.group], pad)
        self._sounding[pad] = note
        return NoteOn(self.channel, note, velocity(self.cfg.velocity, att.peak))

    def leds(self) -> LedState:
        layout = self.cfg.layouts[self.group]
        dim = self.cfg.leds.dim
        lit = set(self._attacks) | set(self._sounding)
        pads: list[RGB] = [(0, 0, 0)] * N_PADS
        for index in range(N_PADS):
            pad = pad_label(index)
            full = pad_color(self.cfg, layout, pad)
            pads[index] = full if pad in lit else scale(full, dim)
        groups = [
            scale(self.cfg.families[lay.family], 1.0 if g == self.group else dim)
            for g, lay in enumerate(self.cfg.layouts)
        ]
        self.leds_dirty = False
        return LedState(pads=pads, groups=groups, buttons={})

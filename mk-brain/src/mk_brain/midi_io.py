"""Ports MIDI de la DT2 (mido + python-rtmidi : CoreMIDI sur Mac, ALSA sur Pi)."""

from __future__ import annotations

import queue
import time
from dataclasses import dataclass
from typing import Any, Literal

import mido

from mk_brain.clock import ClockTracker
from mk_brain.engine import MidiOut, NoteOff, NoteOn

InKind = Literal["clock", "start", "continue", "stop", "sysex", "program_change"]


@dataclass(frozen=True, slots=True)
class MidiIn:
    """Message reçu de la DT2, horodaté dans le callback rtmidi."""

    kind: InKind
    t_ns: int
    data: tuple[int, ...] = ()


class MidiError(Exception):
    """Backend absent ou port DT2 introuvable."""


def output_names() -> list[str]:
    try:
        return list(mido.get_output_names())
    except Exception as exc:  # backend rtmidi absent ou CoreMIDI en erreur
        raise MidiError(f"backend MIDI indisponible : {exc}") from exc


def input_names() -> list[str]:
    try:
        return list(mido.get_input_names())
    except Exception as exc:
        raise MidiError(f"backend MIDI indisponible : {exc}") from exc


def find_port(hint: str, names: list[str] | None = None) -> str:
    names = output_names() if names is None else names
    for name in names:
        if hint.lower() in name.lower():
            return name
    raise MidiError(f"aucun port contenant {hint!r} ; vus : {names or 'aucun'}")


class Dt2Out:
    def __init__(self, port: Any) -> None:
        self._port = port

    @classmethod
    def open(cls, hint: str) -> Dt2Out:
        name = find_port(hint)
        try:
            return cls(mido.open_output(name))
        except OSError as exc:
            raise MidiError(f"ouverture de {name!r} impossible : {exc}") from exc

    def send(self, msg: MidiOut) -> None:
        if isinstance(msg, NoteOn):
            m = mido.Message("note_on", channel=msg.channel, note=msg.note, velocity=msg.velocity)
        else:
            assert isinstance(msg, NoteOff)
            m = mido.Message("note_off", channel=msg.channel, note=msg.note, velocity=0)
        self._port.send(m)

    def close(self) -> None:
        self._port.close()


class Dt2In:
    """Entrée DT2 : le callback ne fait qu'horodater et empiler (fil MIDI in de la SPEC)."""

    KINDS: frozenset[str] = frozenset(InKind.__args__)  # type: ignore[attr-defined]

    def __init__(self, port: Any, inbox: queue.SimpleQueue[MidiIn]) -> None:
        self._port = port
        self.inbox = inbox

    @classmethod
    def open(cls, hint: str) -> Dt2In:
        name = find_port(hint, input_names())
        inbox: queue.SimpleQueue[MidiIn] = queue.SimpleQueue()

        def callback(msg: Any) -> None:
            t = time.perf_counter_ns()
            if msg.type in cls.KINDS:
                data: tuple[int, ...] = ()
                if msg.type == "sysex":
                    data = tuple(msg.data)
                elif msg.type == "program_change":
                    data = (msg.channel, msg.program)
                inbox.put(MidiIn(msg.type, t, data))

        try:
            return cls(mido.open_input(name, callback=callback), inbox)
        except OSError as exc:
            raise MidiError(f"ouverture de {name!r} impossible : {exc}") from exc

    def drain(self) -> list[MidiIn]:
        out: list[MidiIn] = []
        while True:
            try:
                out.append(self.inbox.get_nowait())
            except queue.Empty:
                return out

    def close(self) -> None:
        self._port.close()


def feed_clock(clock: ClockTracker, ev: MidiIn) -> None:
    if ev.kind == "clock":
        clock.tick(ev.t_ns)
    elif ev.kind == "start":
        clock.start(ev.t_ns)
    elif ev.kind == "continue":
        clock.cont(ev.t_ns)
    elif ev.kind == "stop":
        clock.stop(ev.t_ns)
    elif ev.kind == "sysex":
        clock.sysex(ev.data, ev.t_ns)

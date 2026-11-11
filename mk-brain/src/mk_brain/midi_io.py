"""Ports MIDI de la DT2 (mido + python-rtmidi : CoreMIDI sur Mac, ALSA sur Pi)."""

from __future__ import annotations

import queue
import time
from dataclasses import dataclass
from typing import Any, Literal

import mido

from mk_brain.clock import ClockTracker
from mk_brain.engine import (
    Aftertouch,
    ControlChange,
    Engine,
    MidiOut,
    NoteOff,
    NoteOn,
    PitchBend,
    ProgramChange,
)

InKind = Literal["clock", "start", "continue", "stop", "sysex", "program_change", "control_change"]


@dataclass(frozen=True, slots=True)
class MidiIn:
    """Message reçu de la DT2, horodaté dans le callback rtmidi."""

    kind: InKind
    t_ns: int
    data: tuple[int, ...] = ()


class MidiError(Exception):
    """Backend absent ou port DT2 inutilisable."""


class MidiPortNotFoundError(MidiError):
    """Aucun port MIDI ne porte le nom attendu : DT2 débranchée ou éteinte."""


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
    raise MidiPortNotFoundError(f"aucun port contenant {hint!r} ; vus : {names or 'aucun'}")


def to_mido(msg: MidiOut) -> Any:
    if isinstance(msg, NoteOn):
        return mido.Message("note_on", channel=msg.channel, note=msg.note, velocity=msg.velocity)
    if isinstance(msg, NoteOff):
        return mido.Message("note_off", channel=msg.channel, note=msg.note, velocity=0)
    if isinstance(msg, ControlChange):
        return mido.Message(
            "control_change", channel=msg.channel, control=msg.control, value=msg.value
        )
    if isinstance(msg, PitchBend):
        return mido.Message("pitchwheel", channel=msg.channel, pitch=msg.pitch)
    if isinstance(msg, Aftertouch):
        return mido.Message("aftertouch", channel=msg.channel, value=msg.value)
    assert isinstance(msg, ProgramChange)
    return mido.Message("program_change", channel=msg.channel, program=msg.program)


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
        self._port.send(to_mido(msg))

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
                elif msg.type == "control_change":
                    data = (msg.channel, msg.control, msg.value)
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


def feed_engine(engine: Engine, ev: MidiIn) -> None:
    """Horloge d'abord, puis transport et Program Change vers le moteur."""
    feed_clock(engine.clock, ev)
    if ev.kind == "start":
        engine.on_start()
    elif ev.kind == "stop":
        engine.on_stop()
    elif ev.kind == "program_change":
        engine.on_program_change(ev.data[1])
    elif ev.kind == "control_change":
        engine.on_control_change(*ev.data)

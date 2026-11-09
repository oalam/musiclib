from __future__ import annotations

import pytest

from mk_brain import midi_io
from mk_brain.config import Config
from mk_brain.engine import Engine, NoteOff, NoteOn


def test_find_port(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(midi_io, "output_names", lambda: ["IAC", "Elektron Digitakt II"])
    assert midi_io.find_port("digitakt") == "Elektron Digitakt II"
    with pytest.raises(midi_io.MidiError):
        midi_io.find_port("Syntakt")


class FakePort:
    def __init__(self) -> None:
        self.sent: list[object] = []

    def send(self, msg: object) -> None:
        self.sent.append(msg)

    def close(self) -> None:
        pass


def test_send_converts_to_mido() -> None:
    port = FakePort()
    out = midi_io.Dt2Out(port)
    out.send(NoteOn(15, 0, 100))
    out.send(NoteOff(15, 0))
    assert [str(m) for m in port.sent] == [
        "note_on channel=15 note=0 velocity=100 time=0",
        "note_off channel=15 note=0 velocity=0 time=0",
    ]


def test_feed_clock_dispatch() -> None:
    from mk_brain.clock import ClockTracker

    c = ClockTracker()
    midi_io.feed_clock(c, midi_io.MidiIn("start", 0))
    assert c.running
    midi_io.feed_clock(c, midi_io.MidiIn("sysex", 5, (0x00, 0x20, 0x3C)))
    assert c.transfer_suspected(10)
    midi_io.feed_clock(c, midi_io.MidiIn("stop", 10))
    assert not c.running


def test_feed_engine_dispatch(cfg: Config) -> None:
    eng = Engine(cfg)
    midi_io.feed_engine(eng, midi_io.MidiIn("start", 0))
    for k in range(100):
        midi_io.feed_engine(eng, midi_io.MidiIn("clock", k * 17_000_000))
    midi_io.feed_engine(eng, midi_io.MidiIn("program_change", 0, (0, 2)))
    assert eng.phrase.pending
    midi_io.feed_engine(eng, midi_io.MidiIn("stop", 0))
    assert not eng.phrase.pending and not eng.clock.running

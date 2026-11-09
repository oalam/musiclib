from __future__ import annotations

import pytest

from mk_brain import midi_io
from mk_brain.engine import NoteOff, NoteOn


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

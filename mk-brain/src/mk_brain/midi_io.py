"""Ports MIDI de la DT2 (mido + python-rtmidi : CoreMIDI sur Mac, ALSA sur Pi)."""

from __future__ import annotations

from typing import Any

import mido

from mk_brain.engine import MidiOut, NoteOff, NoteOn


class MidiError(Exception):
    """Backend absent ou port DT2 introuvable."""


def output_names() -> list[str]:
    try:
        return list(mido.get_output_names())
    except Exception as exc:  # backend rtmidi absent ou CoreMIDI en erreur
        raise MidiError(f"backend MIDI indisponible : {exc}") from exc


def find_port(hint: str) -> str:
    names = output_names()
    for name in names:
        if hint.lower() in name.lower():
            return name
    raise MidiError(f"aucun port de sortie contenant {hint!r} ; vus : {names or 'aucun'}")


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

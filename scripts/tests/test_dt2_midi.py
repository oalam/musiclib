"""Tests de l'envoi d'une track a la DT2 (scripts/dt2_midi.py), ports factices.

Lancer (depuis scripts/) :
    python -m pytest tests/test_dt2_midi.py
"""
from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import mido
import pytest

import dt2_midi
from analyzer.types import DigitaktBank, DigitaktTrack, DigitaktTrig
from dt2_midi import CLOCKS_PER_STEP, Dt2Sender, SendRequest


class FakePort:
    def __init__(self) -> None:
        self.sent: list[Any] = []
        self.closed = False

    def send(self, msg: Any) -> None:
        self.sent.append(msg)

    def close(self) -> None:
        self.closed = True


class FakeMidi:
    """Opener factice : garde le callback pour simuler la DT2."""

    def __init__(self) -> None:
        self.inport = FakePort()
        self.outport = FakePort()
        self.callback: Callable[[Any], None] | None = None
        self.opened = 0

    def __call__(self, name: str, callback: Callable[[Any], None]) -> tuple[FakePort, FakePort]:
        self.callback = callback
        self.opened += 1
        return self.inport, self.outport

    def feed(self, kind: str, n: int = 1) -> None:
        assert self.callback is not None
        for _ in range(n):
            self.callback(mido.Message(kind))


def _track() -> DigitaktTrack:
    return DigitaktTrack(index=9, role="bass", active=True, trigs=[
        DigitaktTrig(step=0, velocity=100, note=36),
        DigitaktTrig(step=2, velocity=80, note=None),
    ])


def _req(**kw: Any) -> SendRequest:
    return SendRequest(**({"slug": "s", "slot": 1, "track": 9, "port": "DT2", "channel": 10} | kw))


def _wait_finished(sender: Dt2Sender) -> None:
    for _ in range(100):  # timeout dans un thread a part
        cur = sender.current()
        if cur is not None and cur.status not in ("waiting", "sending"):
            return
        time.sleep(0.01)
    raise AssertionError("session non terminee")


def test_clock_schedule_canal_et_cadence():
    sched = dt2_midi.clock_schedule(_track(), channel=10)
    on0, off0 = sched[0][0], sched[CLOCKS_PER_STEP // 2][0]
    assert (on0.type, on0.note, on0.channel, on0.velocity) == ("note_on", 36, 9, 100)
    assert off0.type == "note_off" and off0.note == 36
    assert sched[2 * CLOCKS_PER_STEP][0].note == 60  # drum / note inconnue = 60


def test_clock_schedule_transpose_par_octave():
    sched = dt2_midi.clock_schedule(_track(), channel=10, octave=2)
    assert sched[0][0].note == 60 and sched[CLOCKS_PER_STEP // 2][0].note == 60
    assert sched[2 * CLOCKS_PER_STEP][0].note == 84
    with pytest.raises(dt2_midi.SendTargetError):
        dt2_midi.clock_schedule(_track(), channel=10, octave=-4)  # 36 - 48 < 0


def test_pick_track_refuse_les_cibles_vides():
    bank = DigitaktBank.model_validate({
        "slug": "s", "bpm": 150, "from_stems": True,
        "generated_at": "2026-10-07T00:00:00+00:00",
        "patterns": [{"slot": 1, "label": "intro", "start_s": 0, "end_s": 4, "bars": 1,
                      "steps": 16, "repeats": 1,
                      "tracks": [_track().model_dump(), {"index": 1, "role": "kick"}]}],
    })
    track, steps = dt2_midi.pick_track(bank, 1, 9)
    assert track.role == "bass" and steps == 16
    for slot, idx in ((2, 9), (1, 1), (1, 5)):
        with pytest.raises(dt2_midi.SendTargetError):
            dt2_midi.pick_track(bank, slot, idx)


def test_envoi_complet_cale_sur_les_clocks():
    fake = FakeMidi()
    sender = Dt2Sender(opener=fake)
    st = sender.start(_req(), _track(), steps=4)
    assert st.status == "waiting" and st.trigs == 2
    fake.feed("clock", 10)  # horloge avant le Start : ignoree
    assert fake.outport.sent == []
    fake.feed("start")
    fake.feed("clock")  # 1er clock apres le Start = pas 0
    assert [m.type for m in fake.outport.sent] == ["note_on"]
    fake.feed("clock", 4 * CLOCKS_PER_STEP - 1)
    cur = sender.current()
    assert cur is not None and cur.status == "done" and cur.step == 3
    assert [(m.type, m.note) for m in fake.outport.sent] == [
        ("note_on", 36), ("note_off", 36), ("note_on", 60), ("note_off", 60)]
    assert not fake.inport.closed  # ports gardes ouverts (clocks en continu)
    fake.feed("clock", 6)  # apres la fin : plus rien ne part
    assert len(fake.outport.sent) == 4


def test_stop_de_la_dt2_coupe_les_notes():
    fake = FakeMidi()
    sender = Dt2Sender(opener=fake)
    sender.start(_req(), _track(), steps=4)
    fake.feed("start")
    fake.feed("clock")  # note_on 36 en cours
    fake.feed("stop")
    cur = sender.current()
    assert cur is not None and cur.status == "cancelled"
    assert (fake.outport.sent[-1].type, fake.outport.sent[-1].note) == ("note_off", 36)


def test_un_seul_envoi_a_la_fois_puis_annulation():
    fake = FakeMidi()
    sender = Dt2Sender(opener=fake)
    sender.start(_req(), _track(), steps=4)
    with pytest.raises(dt2_midi.SendBusy):
        sender.start(_req(), _track(), steps=4)
    cur = sender.cancel()
    assert cur is not None and cur.status == "cancelled"
    sender.start(_req(), _track(), steps=4)  # relancable, meme port reutilise
    assert fake.opened == 1
    sender.cancel()
    sender.start(_req(port="AUTRE"), _track(), steps=4)  # changement de port
    assert fake.opened == 2
    sender.shutdown()
    assert fake.inport.closed and fake.outport.closed


def test_timeout_sans_start():
    fake = FakeMidi()
    sender = Dt2Sender(opener=fake, start_timeout_s=0.05)
    sender.start(_req(), _track(), steps=4)
    _wait_finished(sender)
    cur = sender.current()
    assert cur is not None and cur.status == "error" and "Start" in cur.detail


def test_port_non_ouvrable():
    def opener(name: str, cb: Callable[[Any], None]) -> tuple[FakePort, FakePort]:
        raise dt2_midi.MidiUnavailable(f"port MIDI non ouvrable : {name}")

    sender = Dt2Sender(opener=opener)
    with pytest.raises(dt2_midi.MidiUnavailable):
        sender.start(_req(), _track(), steps=4)
    cur = sender.current()
    assert cur is not None and cur.status == "error"


def test_sysex_elektron_leve_un_avertissement():
    fake = FakeMidi()
    sender = Dt2Sender(opener=fake)
    sender.start(_req(), _track(), steps=4)
    assert fake.callback is not None
    fake.callback(mido.Message("sysex", data=[0, 32, 60, 16, 0]))
    cur = sender.current()
    assert cur is not None and "Transfer" in cur.warning
    sender.cancel()


def test_second_start_du_preroll_relance_au_pas_0():
    fake = FakeMidi()
    sender = Dt2Sender(opener=fake)
    sender.start(_req(), _track(), steps=4)
    fake.feed("start")  # debut du decompte
    fake.feed("clock", 4 * CLOCKS_PER_STEP - 2)  # une mesure de decompte (tronquee)
    assert sender.current().status == "sending"  # type: ignore[union-attr]
    n = len(fake.outport.sent)
    fake.feed("start")  # vrai depart du sequenceur
    fake.feed("clock")
    assert (fake.outport.sent[n].type, fake.outport.sent[n].note) == ("note_on", 36)
    fake.feed("clock", 4 * CLOCKS_PER_STEP - 1)
    assert sender.current().status == "done"  # type: ignore[union-attr]

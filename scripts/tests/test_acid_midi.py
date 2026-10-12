"""Tests de la lecture temps reel d'une ligne acid (scripts/acid_midi.py, 9.B),
ports et horloge factices.

Lancer (depuis scripts/) :
    python -m pytest tests/test_acid_midi.py
    python -m pytest tests/test_acid_midi.py::test_dt2_target_loops_on_dt2_clock
"""
from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import mido
import pytest

import acid_midi
from acid_midi import AcidPlayer, InternalClock, PlayRequest
from analyzer import acid
from analyzer.acid import AcidParams, AcidSequence, AcidStep
from dt2_midi import MidiUnavailable
from test_dt2_midi import FakeMidi, FakePort


class FakeClock:
    def __init__(self, bpm: float, on_tick: Callable[[], None]) -> None:
        self.bpm = bpm
        self.on_tick = on_tick
        self.running = False

    def start(self) -> None:
        self.running = True

    def stop(self) -> None:
        self.running = False

    def set_bpm(self, bpm: float) -> None:
        self.bpm = bpm

    def tick(self, n: int = 1) -> None:
        for _ in range(n):
            self.on_tick()


class Rig:
    def __init__(self) -> None:
        self.midi = FakeMidi()
        self.out = FakePort()
        self.clocks: list[FakeClock] = []
        self.player = AcidPlayer(opener=self.midi, out_opener=self._open_out,
                                 clock_factory=self._clock)

    def _open_out(self, name: str) -> FakePort:
        return self.out

    def _clock(self, bpm: float, on_tick: Callable[[], None]) -> FakeClock:
        self.clocks.append(FakeClock(bpm, on_tick))
        return self.clocks[-1]


def _seq(steps: list[AcidStep], seed: int = 0, **kw: Any) -> AcidSequence:
    pad = [AcidStep(on=False)] * (acid.SEQ_LEN - len(steps))
    return AcidSequence(seed=seed, params=AcidParams(**kw), steps=steps + pad)


def _two_notes(seed: int = 0) -> AcidSequence:
    # pas 0 : tonique (C2 = 36), pas 4 : degre 2 (Eb2 = 39) ; longueur 0,5 pas = 3 clocks
    return _seq([AcidStep(), AcidStep(on=False), AcidStep(on=False), AcidStep(on=False),
                 AcidStep(degree=2)], seed=seed, tie_mode=False)


def _req(seq: AcidSequence, **kw: Any) -> PlayRequest:
    return PlayRequest(**({"sequence": seq, "target": "mac", "port": "IAC", "channel": 2} | kw))


def _notes(sent: list[Any]) -> list[tuple[str, int]]:
    return [(m.type, m.note) for m in sent if m.type in ("note_on", "note_off")]


def test_clock_schedule_converts_steps_to_clocks():
    sched, total = acid_midi.clock_schedule(_two_notes(), channel=1)
    assert total == 16 * 6
    assert [(m.type, m.note, m.channel) for m in sched[0]] == [("note_on", 36, 1)]
    assert [m.type for m in sched[3]] == ["note_off"]
    assert [(m.type, m.note) for m in sched[24]] == [("note_on", 39)]


def test_clock_schedule_slide_keeps_legato_and_cc():
    seq = _seq([AcidStep(gate=2), AcidStep(degree=2), AcidStep(degree=4)])
    sched, _ = acid_midi.clock_schedule(seq, channel=0, slide_cc=102)
    assert [(m.type, getattr(m, "value", None)) for m in sched[0]] == [
        ("control_change", 0), ("note_on", None)]
    # pas 1 atteint par un slide : CC 127, note_on, puis note_off de la note liee
    assert [m.type for m in sched[6]] == ["control_change", "note_on", "note_off"]
    assert sched[6][0].value == 127
    assert sched[12][0].type == "control_change" and sched[12][0].value == 0


def test_mac_target_plays_on_internal_clock_and_loops():
    rig = Rig()
    st = rig.player.play(_req(_two_notes(), bpm=150))
    assert st.status == "playing"
    clock = rig.clocks[0]
    assert clock.running and clock.bpm == 150
    clock.tick(96)
    assert _notes(rig.out.sent) == [("note_on", 36), ("note_off", 36),
                                    ("note_on", 39), ("note_off", 39)]
    clock.tick(1)  # debut du 2e tour
    assert _notes(rig.out.sent)[-1] == ("note_on", 36)
    assert rig.player.current().cycles == 1  # type: ignore[union-attr]
    assert rig.midi.opened == 0  # cible mac : sortie seule


def test_new_sequence_taken_at_next_cycle():
    rig = Rig()
    rig.player.play(_req(_two_notes(seed=1)))
    clock = rig.clocks[0]
    clock.tick(10)
    other = _seq([AcidStep(degree=4)], seed=2, tie_mode=False)  # G2 = 43
    st = rig.player.play(_req(other, bpm=170))
    assert st.pending and st.seed == 1
    assert len(rig.clocks) == 1 and clock.bpm == 170  # meme lecture, tempo change tout de suite
    clock.tick(86)
    assert ("note_on", 39) in _notes(rig.out.sent)  # fin de l'ancienne ligne jouee
    clock.tick(1)
    assert _notes(rig.out.sent)[-1] == ("note_on", 43)
    st = rig.player.current()
    assert st is not None and st.seed == 2 and not st.pending


def test_stop_cuts_held_notes():
    rig = Rig()
    rig.player.play(_req(_two_notes()))
    rig.clocks[0].tick(1)
    st = rig.player.stop()
    assert st is not None and st.status == "stopped"
    assert not rig.clocks[0].running
    assert _notes(rig.out.sent) == [("note_on", 36), ("note_off", 36)]
    rig.clocks[0].tick(30)  # plus rien apres l'arret
    assert len(_notes(rig.out.sent)) == 2


def test_panic_sends_all_notes_off_on_16_channels():
    rig = Rig()
    rig.player.play(_req(_two_notes()))
    rig.player.panic()
    ccs = [m for m in rig.out.sent if m.type == "control_change"]
    assert len(ccs) == 16 and {m.control for m in ccs} == {123}


def test_dt2_target_loops_on_dt2_clock():
    rig = Rig()
    st = rig.player.play(_req(_two_notes(), target="dt2", port="DT2", channel=10))
    assert st.status == "waiting" and rig.clocks == []
    rig.midi.feed("clock", 5)  # avant le Start : rien
    assert rig.midi.outport.sent == []
    rig.midi.feed("start")
    rig.midi.feed("clock", 97)
    sent = _notes(rig.midi.outport.sent)
    assert sent[:2] == [("note_on", 36), ("note_off", 36)] and sent[-1] == ("note_on", 36)
    assert all(m.channel == 9 for m in rig.midi.outport.sent)
    rig.midi.feed("stop")
    st = rig.player.current()
    assert st is not None and st.status == "waiting"
    assert _notes(rig.midi.outport.sent)[-1] == ("note_off", 36)  # note tenue coupee
    rig.midi.feed("start")  # relance au pas 0
    rig.midi.feed("clock")
    assert _notes(rig.midi.outport.sent)[-1] == ("note_on", 36)


def test_dt2_sysex_warning():
    rig = Rig()
    rig.player.play(_req(_two_notes(), target="dt2", port="DT2"))
    rig.midi.callback(mido.Message("sysex", data=[0]))  # type: ignore[misc]
    st = rig.player.current()
    assert st is not None and "Transfer" in st.warning


def test_port_error_reported():
    def broken(name: str) -> FakePort:
        raise MidiUnavailable("port MIDI non ouvrable : X")

    player = AcidPlayer(out_opener=broken, clock_factory=FakeClock)
    with pytest.raises(MidiUnavailable):
        player.play(_req(_two_notes()))
    st = player.current()
    assert st is not None and st.status == "error"


def test_changing_target_restarts():
    rig = Rig()
    rig.player.play(_req(_two_notes()))
    st = rig.player.play(_req(_two_notes(), target="dt2", port="DT2"))
    assert st.status == "waiting" and not rig.clocks[0].running
    assert rig.out.closed


def test_internal_clock_ticks_at_24_ppqn():
    ticks: list[float] = []
    clock = InternalClock(600, lambda: ticks.append(time.perf_counter()))  # 240 clocks/s
    clock.start()
    time.sleep(0.25)
    clock.stop()
    assert 40 <= len(ticks) <= 70


def test_generated_sequence_plays_whole_cycle():
    rig = Rig()
    seq = acid.generate(AcidParams(root=6, scale="PHRYGIAN", type=11, density=14), seed=3)
    rig.player.play(_req(seq))
    rig.clocks[0].tick(16 * 6 + 1)
    ons = [n for n in _notes(rig.out.sent) if n[0] == "note_on"]
    assert len(ons) == len(acid.render_notes(seq)) + 1


def test_mac_stops_after_bars():
    rig = Rig()
    st = rig.player.play(_req(_two_notes(), bars=2))
    assert st.bars == 2
    clock = rig.clocks[0]
    clock.tick(2 * 96)
    assert rig.player.current().status == "playing"  # type: ignore[union-attr]
    assert len([n for n in _notes(rig.out.sent) if n[0] == "note_on"]) == 4
    clock.tick(1)
    st = rig.player.current()
    assert st is not None and st.status == "done" and not clock.running
    clock.tick(20)  # plus rien apres la fin
    assert len([n for n in _notes(rig.out.sent) if n[0] == "note_on"]) == 4


def test_bars_count_whole_bars_even_with_short_loop():
    rig = Rig()
    seq = AcidSequence(seed=0, params=AcidParams(tie_mode=False, steps=4),
                       steps=[AcidStep()] + [AcidStep(on=False)] * (acid.SEQ_LEN - 1))
    rig.player.play(_req(seq, bars=1))
    rig.clocks[0].tick(96 + 1)
    assert len([n for n in _notes(rig.out.sent) if n[0] == "note_on"]) == 4  # 4 tours de 4 pas


def test_dt2_bars_counted_from_start():
    rig = Rig()
    rig.player.play(_req(_two_notes(), target="dt2", port="DT2", bars=1))
    rig.midi.feed("start")
    rig.midi.feed("clock", 97)
    st = rig.player.current()
    assert st is not None and st.status == "done"
    assert _notes(rig.midi.outport.sent)[-1][0] == "note_off"

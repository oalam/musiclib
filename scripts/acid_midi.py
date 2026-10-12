"""Lecture temps reel d'une ligne acid (Phase 9.B).

Deux cibles :
- **dt2** : la DT2 mene. Le lecteur attend son Start puis cale chaque pas
  sur son horloge (24 ppqn, 6 clocks par double-croche) et boucle jusqu'au
  Stop de la DT2 (retour en attente) ou a l'arret depuis le front. Notes sur
  l'AUTO CHANNEL ou le `CHAN` d'une track MIDI (reglages : [[digitakt/kb/midi-config]]).
- **mac** : horloge interne au BPM demande, sortie seule vers un port
  virtuel (bus IAC) ecoute par le VST.

Une nouvelle ligne envoyee pendant la lecture est prise au tour suivant
(debut de cycle) ; le BPM de la cible mac change tout de suite. Les ports
restent ouverts d'une lecture a l'autre (meme raison que `Dt2Sender`) et ne
sont fermes qu'au changement de port ou a `shutdown()`.

Usage :
    python acid_midi.py --port "IAC Driver Bus 1" --target mac --bpm 140 --root F# --scale PHRYGIAN --seed 3
"""
from __future__ import annotations

import argparse
import threading
import time
import uuid
from collections.abc import Callable
from typing import Any, Literal, Protocol

from pydantic import BaseModel, Field

from analyzer.acid import TICKS_PER_STEP, AcidSequence, play_order, render_notes
from dt2_midi import (CLOCKS_PER_STEP, SYSEX_WARNING, InPort, MidiUnavailable, OutPort,
                      PortOpener, close_ports, open_mido_ports)

Target = Literal["dt2", "mac"]
PlayerStatus = Literal["idle", "waiting", "playing", "stopped", "error"]
TICKS_PER_CLOCK = TICKS_PER_STEP // CLOCKS_PER_STEP  # 20 ticks acid par clock MIDI
ALL_NOTES_OFF = 123


class PlayRequest(BaseModel):
    sequence: AcidSequence
    target: Target
    port: str = Field(..., min_length=1)
    channel: int = Field(..., ge=1, le=16)
    bpm: float = Field(140, ge=40, le=300, description="horloge interne (cible mac)")
    slide_cc: int | None = Field(None, ge=0, le=127,
                                 description="CC de slide : 127 sur une note liee, 0 sinon")


class PlayerState(BaseModel):
    id: str
    target: Target
    port: str
    channel: int
    bpm: float
    seed: int
    status: PlayerStatus = "idle"
    step: int = -1          # pas de la sequence en cours de lecture
    cycles: int = 0         # tours complets joues
    pending: bool = False   # nouvelle ligne en attente du tour suivant
    detail: str = ""
    warning: str = ""


class Clock(Protocol):
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def set_bpm(self, bpm: float) -> None: ...


# (bpm, callback par clock) -> horloge
ClockFactory = Callable[[float, Callable[[], None]], Clock]
OutOpener = Callable[[str], OutPort]


class InternalClock:
    """24 ppqn dans un thread, echeances absolues (pas de derive cumulee)."""

    def __init__(self, bpm: float, on_tick: Callable[[], None]) -> None:
        self._bpm = bpm
        self._on_tick = on_tick
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def set_bpm(self, bpm: float) -> None:
        self._bpm = bpm

    def start(self) -> None:
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="acid-clock", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None and self._thread is not threading.current_thread():
            self._thread.join(timeout=1)
        self._thread = None

    def _run(self) -> None:
        deadline = time.perf_counter()
        while not self._stop.is_set():
            self._on_tick()
            deadline += 60 / (self._bpm * 24)
            delay = deadline - time.perf_counter()
            if delay > 0:
                self._stop.wait(delay)
            elif delay < -0.1:  # retard (machine chargee) : on se recale sans rattraper
                deadline = time.perf_counter()


def open_mido_output(name: str) -> OutPort:
    try:
        import mido
        from rtmidi import RtMidiError
    except ImportError as exc:
        raise MidiUnavailable(f"backend MIDI indisponible : {exc}") from exc
    try:
        port: OutPort = mido.open_output(name)
    except (OSError, RtMidiError) as exc:
        raise MidiUnavailable(f"port MIDI non ouvrable : {name} ({exc})") from exc
    return port


def clock_schedule(seq: AcidSequence, channel: int,
                   slide_cc: int | None = None) -> tuple[dict[int, list[Any]], int]:
    """(messages par clock, clocks par cycle). Cle `total` = note_off de fin de cycle.

    Ordre d'un meme clock : note_off normal, CC de slide, note_on, note_off
    d'une note liee (legato, comme `acid.note_events`)."""
    import mido

    events: list[tuple[int, int, Any]] = []
    notes = render_notes(seq)
    cc_value: int | None = None
    for i, n in enumerate(notes):
        on = round(n.start / TICKS_PER_CLOCK)
        value = 127 if i > 0 and notes[i - 1].slide else 0  # note atteinte par un slide
        if slide_cc is not None and value != cc_value:
            events.append((on, 1, mido.Message("control_change", channel=channel,
                                               control=slide_cc, value=value)))
            cc_value = value
        events.append((on, 2, mido.Message("note_on", channel=channel,
                                           note=n.note, velocity=n.velocity)))
        events.append((round(n.end / TICKS_PER_CLOCK), 3 if n.slide else 0,
                       mido.Message("note_off", channel=channel, note=n.note, velocity=0)))
    out: dict[int, list[Any]] = {}
    for clock, _prio, msg in sorted(events, key=lambda e: (e[0], e[1])):
        out.setdefault(clock, []).append(msg)
    return out, len(play_order(seq.params)) * CLOCKS_PER_STEP


class AcidPlayer:
    """Une lecture a la fois ; etat lu par polling depuis le front."""

    def __init__(self, opener: PortOpener = open_mido_ports,
                 out_opener: OutOpener = open_mido_output,
                 clock_factory: ClockFactory = InternalClock) -> None:
        self._opener = opener
        self._out_opener = out_opener
        self._clock_factory = clock_factory
        self._lock = threading.Lock()
        self._state: PlayerState | None = None
        self._in: InPort | None = None
        self._out: OutPort | None = None
        self._port_key: tuple[Target, str] | None = None
        self._clock_src: Clock | None = None
        self._schedule: dict[int, list[Any]] = {}
        self._total = 0
        self._order: list[int] = []
        self._pending: tuple[AcidSequence, dict[int, list[Any]], int] | None = None
        self._clock = 0
        self._sounding: set[int] = set()

    def current(self) -> PlayerState | None:
        with self._lock:
            return self._state.model_copy(deep=True) if self._state else None

    def play(self, req: PlayRequest) -> PlayerState:
        """Lance la lecture, ou remplace la ligne au tour suivant si la meme
        cible / port / canal joue deja."""
        schedule, total = clock_schedule(req.sequence, req.channel - 1, req.slide_cc)
        with self._lock:
            st = self._state
            same = (st is not None and st.status in ("waiting", "playing")
                    and (st.target, st.port, st.channel) == (req.target, req.port, req.channel))
            if same and st is not None:
                self._pending = (req.sequence, schedule, total)
                st.pending = True
                st.bpm = req.bpm
                if self._clock_src is not None:
                    self._clock_src.set_bpm(req.bpm)
                return st.model_copy(deep=True)
        self.stop("remplace par une nouvelle lecture")
        try:
            self._ensure_ports(req.target, req.port)
        except MidiUnavailable as exc:
            with self._lock:
                self._state = PlayerState(
                    id=uuid.uuid4().hex[:12], target=req.target, port=req.port,
                    channel=req.channel, bpm=req.bpm, seed=req.sequence.seed,
                    status="error", detail=str(exc))
            raise
        clock: Clock | None = None
        with self._lock:
            self._schedule, self._total = schedule, total
            self._order = play_order(req.sequence.params)
            self._pending = None
            self._clock = 0
            self._sounding = set()
            playing = req.target == "mac"
            self._state = PlayerState(
                id=uuid.uuid4().hex[:12], target=req.target, port=req.port,
                channel=req.channel, bpm=req.bpm, seed=req.sequence.seed,
                status="playing" if playing else "waiting",
                detail="lecture (horloge interne)" if playing else "en attente du Start de la DT2")
            if playing:
                clock = self._clock_src = self._clock_factory(req.bpm, self._tick)
        if clock is not None:
            clock.start()
        return self.current() or self._state

    def stop(self, detail: str = "arrete depuis le front") -> PlayerState | None:
        with self._lock:
            clock, self._clock_src = self._clock_src, None
        if clock is not None:
            clock.stop()  # hors verrou : le thread d'horloge le prend a chaque clock
        with self._lock:
            st = self._state
            if st is not None and st.status in ("waiting", "playing"):
                st.status, st.detail, st.step, st.pending = "stopped", detail, -1, False
                self._notes_off()
            self._pending = None
        return self.current()

    def panic(self) -> PlayerState | None:
        """All notes off (CC 123) sur les 16 canaux du port ouvert, en plus des notes tenues."""
        import mido

        with self._lock:
            if self._out is not None:
                self._notes_off()
                for ch in range(16):
                    self._out.send(mido.Message("control_change", channel=ch,
                                                control=ALL_NOTES_OFF, value=0))
        return self.current()

    def shutdown(self) -> None:
        self.stop("arret de l'API")
        self._close_ports()

    def _ensure_ports(self, target: Target, name: str) -> None:
        if self._port_key == (target, name) and self._out is not None:
            return
        self._close_ports()
        if target == "dt2":
            inport, outport = self._opener(name, self._on_message)
        else:
            inport, outport = None, self._out_opener(name)
        with self._lock:
            self._in, self._out, self._port_key = inport, outport, (target, name)

    def _close_ports(self) -> None:
        with self._lock:
            inport, outport = self._in, self._out
            self._in, self._out, self._port_key = None, None, None
        if inport is not None and outport is not None:
            close_ports((inport, outport))
        elif outport is not None:
            outport.close()

    def _notes_off(self) -> None:
        """Sous verrou : coupe les notes tenues."""
        import mido

        if self._out is None or self._state is None:
            return
        for note in sorted(self._sounding):
            self._out.send(mido.Message("note_off", channel=self._state.channel - 1,
                                        note=note, velocity=0))
        self._sounding = set()

    def _send(self, msgs: list[Any]) -> None:
        assert self._out is not None
        for m in msgs:
            self._out.send(m)
            if m.type == "note_on":
                self._sounding.add(m.note)
            elif m.type == "note_off":
                self._sounding.discard(m.note)

    def _on_message(self, msg: Any) -> None:
        """Messages de la DT2 (thread du backend MIDI)."""
        kind = getattr(msg, "type", "")
        if kind == "clock":
            self._tick()
            return
        with self._lock:
            st = self._state
            if st is None or st.status not in ("waiting", "playing"):
                return
            if kind == "start":  # aussi le second Start du PREROLL : reprise au pas 0
                self._notes_off()
                self._swap_pending()
                st.status, st.detail, st.step = "playing", "lecture (horloge de la DT2)", -1
                self._clock = 0
            elif kind == "stop":
                self._notes_off()
                st.status, st.detail, st.step = "waiting", "Stop de la DT2, en attente du Start", -1
            elif kind == "sysex":
                st.warning = SYSEX_WARNING

    def _swap_pending(self) -> None:
        if self._pending is not None and self._state is not None:
            seq, self._schedule, self._total = self._pending
            self._order = play_order(seq.params)
            self._state.seed = seq.seed
            self._state.pending = False
            self._pending = None

    def _tick(self) -> None:
        with self._lock:
            st = self._state
            if st is None or st.status != "playing" or self._out is None:
                return
            if self._clock >= self._total:
                self._send(self._schedule.get(self._total, []))
                self._swap_pending()
                self._clock = 0
                st.cycles += 1
            self._send(self._schedule.get(self._clock, []))
            st.step = self._order[self._clock // CLOCKS_PER_STEP]
            self._clock += 1


def main() -> int:
    from analyzer.acid import AcidParams, generate
    from analyzer.harmony import NOTE_NAMES, SCALES
    from dt2_midi import list_ports

    ap = argparse.ArgumentParser(description="Joue une ligne acid en boucle (9.B), Ctrl-C pour arreter.")
    ap.add_argument("--list-ports", action="store_true")
    ap.add_argument("--port")
    ap.add_argument("--target", choices=("dt2", "mac"), default="mac")
    ap.add_argument("--channel", type=int, default=1)
    ap.add_argument("--bpm", type=float, default=140)
    ap.add_argument("--root", default="C", choices=NOTE_NAMES)
    ap.add_argument("--scale", default="AEOLIAN (MINOR)", choices=sorted(SCALES))
    ap.add_argument("--type", type=int, default=8)
    ap.add_argument("--density", type=int, default=12)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    if args.list_ports or not args.port:
        print(list_ports().model_dump_json(indent=2))
        return 0
    seq = generate(AcidParams(root=NOTE_NAMES.index(args.root), scale=args.scale,
                              type=args.type, density=args.density), args.seed)
    player = AcidPlayer()
    player.play(PlayRequest(sequence=seq, target=args.target, port=args.port,
                            channel=args.channel, bpm=args.bpm))
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        player.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

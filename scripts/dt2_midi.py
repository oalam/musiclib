#!/usr/bin/env python3
"""Envoi d'une track d'un pattern de bank a la Digitakt II (Phase 7.E).

Aucun NRPN ne pose de trig sur un pas (annexe B) : on rejoue les notes de la
track sur l'AUTO CHANNEL pendant que la DT2 enregistre en LIVE RECORDING
(§10.2.3), une track a la fois. La DT2 mene : le script attend son Start MIDI
puis cale chaque pas sur son horloge (24 ppqn, 6 clocks par double-croche),
un seul passage du pattern. Un Stop de la DT2 avant la fin annule l'envoi ;
un nouveau Start le relance au pas 0 (second Start du PREROLL).

Reglages DT2 (fiche [[digitakt/kb/midi-config]]) : PORT CONFIG `INPUT FROM` et
`OUTPUT TO` = USB, `RECEIVE NOTES` = on ; SYNC `CLOCK SEND` et
`TRANSPORT SEND` = on ; CHANNELS `AUTO CHANNEL` = canal passe ici.

Usage:
    python dt2_midi.py --list-ports
    python dt2_midi.py <slug> --pattern 1 --track 3 --channel 10
    python dt2_midi.py <slug> --pattern 1 --track 3 --channel 10 --port "Elektron Digitakt II"
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
import time
import uuid
from collections.abc import Callable
from datetime import datetime
from typing import Any, Literal, Protocol

from pydantic import BaseModel, Field

from analyzer.digitakt import track_note_events
from analyzer.types import DigitaktBank, DigitaktTrack
from paths import DIGITAKT_DIR

CLOCKS_PER_STEP = 6  # 24 ppqn / 4 doubles-croches par temps
START_TIMEOUT_S = 120.0
DEFAULT_PORT_HINT = "Digitakt"

# Constate le 2026-10-07 : Transfer ouvert = flux sysex Elektron (~22/s) et
# la moitie des clocks USB perdus (58 BPM lus pour 120 affiches).
SYSEX_WARNING = ("trafic sysex Elektron recu : fermer Transfer, sinon des clocks "
                 "se perdent et les notes tombent trop lentement")

SendStatus = Literal["waiting", "sending", "done", "cancelled", "error"]


class MidiUnavailable(Exception):
    """Backend MIDI absent (python-rtmidi) ou port introuvable / non ouvrable."""


class SendBusy(Exception):
    """Un envoi est deja en cours (un seul a la fois)."""


class SendTargetError(Exception):
    """Bank, pattern ou track introuvable, ou track sans trig."""


class Dt2Ports(BaseModel):
    inputs: list[str] = []
    outputs: list[str] = []
    default: str | None = None  # port present en entree et en sortie, DT2 en priorite
    error: str | None = None


class SendRequest(BaseModel):
    slug: str
    slot: int = Field(..., ge=1, le=16)
    track: int = Field(..., ge=1, le=16)
    port: str = Field(..., min_length=1)
    channel: int = Field(..., ge=1, le=16, description="AUTO CHANNEL de la DT2 (1-16)")


class SendState(BaseModel):
    id: str
    request: SendRequest
    role: str
    steps: int
    trigs: int
    status: SendStatus = "waiting"
    step: int = -1  # dernier pas envoye
    detail: str = ""
    warning: str = ""  # sysex Elektron recu : Transfer ouvert, clocks perdus
    created_at: str
    finished_at: str | None = None


class InPort(Protocol):
    def close(self) -> None: ...


class OutPort(Protocol):
    def send(self, msg: Any) -> None: ...
    def close(self) -> None: ...


# (nom du port, callback des messages entrants) -> (entree, sortie)
PortOpener = Callable[[str, Callable[[Any], None]], tuple[InPort, OutPort]]


def list_ports() -> Dt2Ports:
    try:
        import mido

        inputs = list(mido.get_input_names())
        outputs = list(mido.get_output_names())
    except ImportError as exc:  # backend rtmidi absent
        return Dt2Ports(error=f"backend MIDI indisponible : {exc} (pip install python-rtmidi)")
    both = [p for p in outputs if p in inputs]
    default = next((p for p in both if DEFAULT_PORT_HINT.lower() in p.lower()),
                   both[0] if both else None)
    return Dt2Ports(inputs=inputs, outputs=outputs, default=default)


def open_mido_ports(name: str, callback: Callable[[Any], None]) -> tuple[InPort, OutPort]:
    try:
        import mido
        from rtmidi import RtMidiError
    except ImportError as exc:
        raise MidiUnavailable(f"backend MIDI indisponible : {exc}") from exc
    try:
        outport = mido.open_output(name)
        try:
            inport = mido.open_input(name, callback=callback)
        except (OSError, RtMidiError):
            outport.close()
            raise
    except (OSError, RtMidiError) as exc:  # mido : IOError sur un nom inconnu
        raise MidiUnavailable(f"port MIDI non ouvrable : {name} ({exc})") from exc
    return inport, outport


def load_bank(slug: str) -> DigitaktBank:
    path = DIGITAKT_DIR / f"{slug}.json"
    if not path.exists():
        raise SendTargetError(f"pas de bank pour {slug}")
    return DigitaktBank.model_validate(json.loads(path.read_text(encoding="utf-8")))


def pick_track(bank: DigitaktBank, slot: int, index: int) -> tuple[DigitaktTrack, int]:
    """(track, nb de pas du pattern) ; refuse une track sans trig."""
    pattern = next((p for p in bank.patterns if p.slot == slot), None)
    if pattern is None:
        raise SendTargetError(f"pattern {slot:02d} absent de la bank {bank.slug}")
    track = next((t for t in pattern.tracks if t.index == index), None)
    if track is None or not track.trigs:
        raise SendTargetError(f"track {index} sans trig dans le pattern {slot:02d}")
    return track, pattern.steps


def clock_schedule(track: DigitaktTrack, channel: int) -> dict[int, list[Any]]:
    """Messages a envoyer par clock (0 = premier clock apres le Start).

    Les note_off passent avant les note_on d'un meme clock (meme regle que le
    .mid de bank)."""
    out: dict[int, list[Any]] = {}
    events = sorted(track_note_events(track, CLOCKS_PER_STEP, channel=channel - 1),
                    key=lambda e: (e[0], e[1]))
    for tick, _prio, msg in events:
        out.setdefault(tick, []).append(msg)
    return out


class Dt2Sender:
    """Une session d'envoi a la fois ; l'etat est lu par polling depuis le front.

    Le callback des messages entrants tourne dans le thread du backend MIDI :
    les notes partent directement depuis ce callback (latence minimale).

    Les ports restent ouverts d'un envoi a l'autre et ne sont fermes qu'au
    changement de port ou a `shutdown()` : la DT2 envoie ses clocks en continu,
    et fermer l'entree pendant un callback interbloque CoreMIDI et python-rtmidi
    (constate le 2026-10-07 : API gelee en fin d'envoi)."""

    def __init__(self, opener: PortOpener = open_mido_ports,
                 start_timeout_s: float = START_TIMEOUT_S) -> None:
        self._opener = opener
        self._timeout = start_timeout_s
        self._lock = threading.Lock()
        self._state: SendState | None = None
        self._ports: tuple[InPort, OutPort] | None = None
        self._port_name: str | None = None
        self._schedule: dict[int, list[Any]] = {}
        self._total = 0
        self._clock = 0
        self._sounding: set[int] = set()
        self._timer: threading.Timer | None = None

    def current(self) -> SendState | None:
        with self._lock:
            return self._state.model_copy(deep=True) if self._state else None

    def start(self, req: SendRequest, track: DigitaktTrack, steps: int) -> SendState:
        with self._lock:
            if self._state is not None and self._state.status in ("waiting", "sending"):
                raise SendBusy("un envoi est deja en cours (l'annuler d'abord)")
            self._schedule = clock_schedule(track, req.channel)
            self._total = steps * CLOCKS_PER_STEP
            self._clock = 0
            self._sounding = set()
            self._state = SendState(
                id=uuid.uuid4().hex[:12], request=req, role=track.role, steps=steps,
                trigs=len(track.trigs), detail="en attente du Start de la DT2",
                created_at=datetime.now().isoformat(timespec="seconds"),
            )
        try:
            self._ensure_ports(req.port)
        except MidiUnavailable as exc:
            self._finish("error", str(exc))
            raise
        with self._lock:
            self._timer = threading.Timer(self._timeout, self._on_timeout)
            self._timer.daemon = True
            self._timer.start()
        return self.current() or self._state

    def _ensure_ports(self, name: str) -> None:
        """Ouvre le port au premier envoi, le reutilise ensuite."""
        if self._ports is not None and self._port_name == name:
            return
        old, self._ports, self._port_name = self._ports, None, None
        if old is not None:
            close_ports(old)
        ports = self._opener(name, self._on_message)
        with self._lock:
            self._ports, self._port_name = ports, name

    def shutdown(self) -> None:
        self._finish("cancelled", "arret de l'API")
        with self._lock:
            ports, self._ports, self._port_name = self._ports, None, None
        if ports is not None:
            close_ports(ports)

    def cancel(self) -> SendState | None:
        self._finish("cancelled", "annule depuis le front")
        return self.current()

    def _on_timeout(self) -> None:
        self._finish("error", f"aucun Start recu en {self._timeout:.0f} s "
                              "(TRANSPORT SEND / CLOCK SEND actives ?)", only_if="waiting")

    def _on_message(self, msg: Any) -> None:
        kind = getattr(msg, "type", "")
        if kind == "start":
            # avec PREROLL, la DT2 envoie un Start au debut du decompte puis un
            # second au vrai depart du sequenceur (constate le 2026-10-07) :
            # un Start pendant l'envoi le relance au pas 0
            with self._lock:
                st = self._state
                if st is None or st.status not in ("waiting", "sending"):
                    return
                if st.status == "sending" and self._ports is not None:
                    for note in sorted(self._sounding):
                        self._ports[1].send(_note_off(st.request.channel - 1, note))
                self._sounding = set()
                st.status = "sending"
                st.detail = "envoi en cours"
                st.step = -1
                self._clock = 0
            return
        if kind == "stop":
            self._finish("cancelled", "Stop recu de la DT2 avant la fin du pattern",
                         only_if="sending")
            return
        if kind == "sysex":
            with self._lock:
                if self._state is not None and self._state.status in ("waiting", "sending"):
                    self._state.warning = SYSEX_WARNING
            return
        if kind != "clock":
            return
        done = False
        with self._lock:
            if self._state is None or self._state.status != "sending" or self._ports is None:
                return
            out = self._ports[1]
            for m in self._schedule.get(self._clock, []):
                out.send(m)
                if m.type == "note_on":
                    self._sounding.add(m.note)
                else:
                    self._sounding.discard(m.note)
            self._state.step = self._clock // CLOCKS_PER_STEP
            self._clock += 1
            done = self._clock >= self._total
        if done:
            self._finish("done", "pattern envoye (un passage)", only_if="sending")

    def _finish(self, status: SendStatus, detail: str,
                only_if: SendStatus | None = None) -> None:
        """Clot la session et coupe les notes tenues ; les ports restent ouverts."""
        with self._lock:
            st = self._state
            if st is None or st.status not in ("waiting", "sending"):
                return
            if only_if is not None and st.status != only_if:
                return
            st.status = status
            st.detail = detail
            st.finished_at = datetime.now().isoformat(timespec="seconds")
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
            if self._ports is not None:
                for note in sorted(self._sounding):
                    self._ports[1].send(_note_off(st.request.channel - 1, note))
            self._sounding = set()


def _note_off(channel: int, note: int) -> Any:
    import mido

    return mido.Message("note_off", channel=channel, note=note, velocity=0)


def close_ports(ports: tuple[InPort, OutPort]) -> None:
    """Coupe le callback au niveau rtmidi puis ferme : le `close()` de mido
    reinstalle le callback avant `close_port`, ce qui interbloque si un clock
    arrive pendant la fermeture."""
    inport, outport = ports
    try:
        rt = getattr(inport, "_rt", None)
        if rt is not None:  # port mido : on court-circuite son close()
            rt.cancel_callback()
            time.sleep(0.05)  # laisse finir un callback en vol (il attend le GIL)
            rt.close_port()
            inport.closed = True  # type: ignore[attr-defined]
        else:
            inport.close()
    finally:
        outport.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Envoie une track de pattern a la DT2 (7.E).")
    parser.add_argument("slug", nargs="?")
    parser.add_argument("--pattern", type=int, default=1, help="slot du pattern (1-16)")
    parser.add_argument("--track", type=int, help="track (1-16)")
    parser.add_argument("--channel", type=int, help="AUTO CHANNEL de la DT2 (1-16)")
    parser.add_argument("--port", help="port MIDI (defaut : la DT2 si presente)")
    parser.add_argument("--list-ports", action="store_true")
    args = parser.parse_args()

    ports = list_ports()
    if args.list_ports:
        print(ports.model_dump_json(indent=2))
        return 0 if ports.error is None else 1
    if not args.slug or args.track is None or args.channel is None:
        parser.error("slug, --track et --channel requis (ou --list-ports)")
    port = args.port or ports.default
    if port is None:
        print(ports.error or "aucun port MIDI en entree + sortie", file=sys.stderr)
        return 1
    req = SendRequest(slug=args.slug, slot=args.pattern, track=args.track,
                      port=port, channel=args.channel)
    try:
        track, steps = pick_track(load_bank(req.slug), req.slot, req.track)
        sender = Dt2Sender()
        st = sender.start(req, track, steps)
    except (SendTargetError, MidiUnavailable) as exc:
        print(f"ERREUR : {exc}", file=sys.stderr)
        return 1
    print(f"T{req.track:02d} {st.role} · P{req.slot:02d} · {steps} pas · {st.trigs} trigs "
          f"· canal {req.channel} · {port}")
    print("Sur la DT2 : selectionner la track, LEN du pattern = "
          f"{steps} pas, puis [RECORD] + [PLAY]. Ctrl-C pour annuler.")
    try:
        while (cur := sender.current()) and cur.status in ("waiting", "sending"):
            time.sleep(0.1)
    except KeyboardInterrupt:
        sender.cancel()
    cur = sender.current()
    print(f"{cur.status if cur else '?'} : {cur.detail if cur else ''}")
    return 0 if cur and cur.status == "done" else 1


if __name__ == "__main__":
    raise SystemExit(main())

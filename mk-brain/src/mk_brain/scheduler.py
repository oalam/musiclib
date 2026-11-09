"""Ordonnanceur : envoie chaque message MIDI à son instant cible.

Fil dédié : sommeil jusqu'à `SPIN_NS` avant la cible, puis attente active qui
cède le GIL à chaque tour (`time.sleep(0)`) : sans ça, le callback MIDI qui
horodate les ticks attend son tour et la gigue d'arrivée triple (constaté à
la slice 2).
Chaque envoi mesure son écart (fin de `send` − cible), pour le banc de gigue.
"""

from __future__ import annotations

import heapq
import itertools
import sys
import threading
import time
from collections.abc import Callable

from mk_brain.clock import Stats

SPIN_NS = 2_000_000  # 2 ms d attente active (p99 0,012 ms mesuré seul sur Mac)
WAIT_CHUNK_NS = 2_000_000  # attentes longues découpées : macOS réveille tard (jusqu'à 3,6 ms)
SWITCH_INTERVAL_S = 0.0002  # bascule de fil Python : 0,2 ms au lieu de 5 ms
LATE_DROP_NS = 20_000_000  # plus de 20 ms de retard : on n'envoie plus


class Scheduler[M]:
    def __init__(self, send: Callable[[M], None]) -> None:
        self._send = send
        self._heap: list[tuple[int, int, M]] = []
        self._seq = itertools.count()
        self._cv = threading.Condition()
        self._stop = False
        self.errors = Stats()
        self.dropped = 0
        self._thread = threading.Thread(target=self._run, name="scheduler", daemon=True)

    def start(self) -> None:
        sys.setswitchinterval(SWITCH_INTERVAL_S)
        self._thread.start()

    def close(self) -> None:
        with self._cv:
            self._stop = True
            self._cv.notify()
        self._thread.join(timeout=1)

    def at(self, target_ns: int, msg: M) -> None:
        with self._cv:
            heapq.heappush(self._heap, (target_ns, next(self._seq), msg))
            self._cv.notify()

    def _run(self) -> None:
        while True:
            with self._cv:
                while not self._stop and not self._heap:
                    self._cv.wait()
                if self._stop:
                    return
                target = self._heap[0][0]
                wait = target - time.perf_counter_ns() - SPIN_NS
                if wait > 0:
                    # réveil anticipé si un envoi plus tôt arrive
                    self._cv.wait(timeout=min(wait, WAIT_CHUNK_NS) / 1e9)
                    continue
                _, _, msg = heapq.heappop(self._heap)
            while time.perf_counter_ns() < target:
                time.sleep(0)
            if time.perf_counter_ns() - target > LATE_DROP_NS:
                self.dropped += 1
                continue
            self._send(msg)
            self.errors.add(time.perf_counter_ns() - target)

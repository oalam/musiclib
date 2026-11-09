"""Ordonnanceur : envoie chaque message MIDI à son instant cible.

Fil dédié : sommeil jusqu'à `SPIN_NS` avant la cible, puis attente active.
Chaque envoi mesure son écart (fin de `send` − cible), pour le banc de gigue.
"""

from __future__ import annotations

import heapq
import itertools
import threading
import time
from collections.abc import Callable

from mk_brain.clock import Stats

SPIN_NS = 500_000  # 0,5 ms d'attente active
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
                    self._cv.wait(timeout=wait / 1e9)  # réveil anticipé si un envoi plus tôt arrive
                    continue
                _, _, msg = heapq.heappop(self._heap)
            while time.perf_counter_ns() < target:
                pass
            if time.perf_counter_ns() - target > LATE_DROP_NS:
                self.dropped += 1
                continue
            self._send(msg)
            self.errors.add(time.perf_counter_ns() - target)

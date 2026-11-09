"""Suivi de l'horloge MIDI de la DT2 : période, phase, BPM, transport, position.

Estimation par régression linéaire sur les 24 derniers ticks (une noire) :
pente = durée de tick, ordonnée = phase. Un tick prévu se place sur la
droite, pas sur le dernier tick reçu, pour ne pas recopier la gigue USB
(±1 ms, fiche midi-config). Temps en nanosecondes (`time.perf_counter_ns`).
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field

TICKS_PER_BEAT = 24
TICKS_PER_STEP = 6  # double-croche ; repris de scripts/dt2_midi.py (CLOCKS_PER_STEP)
TICKS_PER_BAR = 96  # 4/4
WINDOW = TICKS_PER_BEAT
MIN_POINTS = 8
STALL_NS = 250_000_000  # trou de plus de 250 ms : on repart de zéro
ELEKTRON_SYSEX_ID = (0x00, 0x20, 0x3C)
TRANSFER_HOLD_NS = 2_000_000_000


@dataclass(frozen=True, slots=True)
class Position:
    """Position depuis le Start, tout en base 1 : mesure, temps (1-4), pas (1-4)."""

    bar: int
    beat: int
    step: int

    def __str__(self) -> str:
        return f"{self.bar}.{self.beat}.{self.step}"


@dataclass
class Stats:
    """Écarts en nanosecondes ; résumé en millisecondes."""

    values: list[float] = field(default_factory=list)

    def add(self, x: float) -> None:
        self.values.append(x)

    def summary(self) -> str:
        v = self.values
        if not v:
            return "aucune mesure"
        a = sorted(abs(x) for x in v)
        mean = sum(v) / len(v)
        rms = math.sqrt(sum(x * x for x in v) / len(v))
        p99 = a[min(len(a) - 1, int(0.99 * len(a)))]
        ms = 1e-6
        return (
            f"n={len(v)} moyenne {mean * ms:+.3f} ms, rms {rms * ms:.3f} ms, "
            f"p99 |{p99 * ms:.3f}| ms, max |{a[-1] * ms:.3f}| ms"
        )


class ClockTracker:
    def __init__(self) -> None:
        self._points: deque[tuple[int, int]] = deque(maxlen=WINDOW + 1)  # (index, t_ns)
        self._index = -1  # compteur de ticks reçus depuis la création
        self._start_index: int | None = None  # index du tick 0 après Start
        self._fit: tuple[float, float, float] | None = None  # (x moyen, t moyen, pente)
        self.running = False
        self.prediction_error = Stats()
        self._last_elektron_sysex: int | None = None

    # --- entrées ------------------------------------------------------------

    def tick(self, t_ns: int) -> None:
        if self._points and t_ns - self._points[-1][1] > STALL_NS:
            self._points.clear()
            self._fit = None
        self._index += 1
        expected = self.tick_time(self._index)
        if expected is not None:
            self.prediction_error.add(t_ns - expected)
        self._points.append((self._index, t_ns))
        self._refit()
        if self.running and self._start_index is None:
            self._start_index = self._index

    def start(self, t_ns: int) -> None:
        """Start : le tick suivant est la position 0 (norme MIDI)."""
        self.running = True
        self._start_index = None

    def cont(self, t_ns: int) -> None:
        self.running = True

    def stop(self, t_ns: int) -> None:
        self.running = False

    def sysex(self, data: bytes | tuple[int, ...], t_ns: int) -> None:
        if tuple(data[:3]) == ELEKTRON_SYSEX_ID:
            self._last_elektron_sysex = t_ns

    # --- lecture --------------------------------------------------------------

    def _refit(self) -> None:
        n = len(self._points)
        if n < MIN_POINTS:
            self._fit = None
            return
        xm = sum(i for i, _ in self._points) / n
        tm = sum(t for _, t in self._points) / n
        sxx = sum((i - xm) ** 2 for i, _ in self._points)
        sxt = sum((i - xm) * (t - tm) for i, t in self._points)
        self._fit = (xm, tm, sxt / sxx)

    @property
    def period_ns(self) -> float | None:
        return self._fit[2] if self._fit else None

    @property
    def bpm(self) -> float | None:
        p = self.period_ns
        return round(60e9 / (TICKS_PER_BEAT * p), 1) if p else None

    def tick_time(self, index: float) -> float | None:
        """Instant prévu du tick d'index absolu `index`."""
        if self._fit is None:
            return None
        xm, tm, slope = self._fit
        return tm + (index - xm) * slope

    @property
    def ticks_since_start(self) -> int | None:
        if not self.running or self._start_index is None:
            return None
        return self._index - self._start_index

    def position(self) -> Position | None:
        k = self.ticks_since_start
        if k is None:
            return None
        return Position(
            bar=k // TICKS_PER_BAR + 1,
            beat=k % TICKS_PER_BAR // TICKS_PER_BEAT + 1,
            step=k % TICKS_PER_BEAT // TICKS_PER_STEP + 1,
        )

    def ticks_at(self, t_ns: int) -> float | None:
        """Position fractionnaire (ticks depuis le Start) à l'instant `t_ns`."""
        if self._fit is None or self._start_index is None or not self.running:
            return None
        xm, tm, slope = self._fit
        return xm + (t_ns - tm) / slope - self._start_index

    def position_time(self, ticks_since_start: float) -> float | None:
        """Instant prévu d'une position (en ticks depuis le Start)."""
        if self._start_index is None:
            return None
        return self.tick_time(self._start_index + ticks_since_start)

    def transfer_suspected(self, now_ns: int) -> bool:
        t = self._last_elektron_sysex
        return t is not None and now_ns - t < TRANSFER_HOLD_NS

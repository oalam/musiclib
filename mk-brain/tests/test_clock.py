from __future__ import annotations

import pytest

from mk_brain.clock import ClockTracker, Position, Stats

BPM_143_TICK_NS = 60e9 / (24 * 143)  # 17 482 517 ns


def feed(clock: ClockTracker, n: int, t0: float = 0.0, jitter: list[float] | None = None) -> float:
    t = t0
    for i in range(n):
        j = jitter[i % len(jitter)] if jitter else 0.0
        clock.tick(int(t + j))
        t += BPM_143_TICK_NS
    return t


def test_bpm_exact_and_with_usb_jitter() -> None:
    c = ClockTracker()
    feed(c, 48)
    assert c.bpm == 143.0
    j = ClockTracker()
    feed(j, 96, jitter=[1e6, -1e6, 0.5e6, -0.7e6, 0.0])  # ±1 ms
    assert j.bpm == pytest.approx(143.0, abs=0.1)


def test_prediction_smooths_jitter() -> None:
    c = ClockTracker()
    feed(c, 96, jitter=[1e6, -1e6, 0.5e6, -0.7e6, 0.0])
    t_next = c.tick_time(96)
    assert t_next is not None
    assert abs(t_next - 96 * BPM_143_TICK_NS) < 0.3e6  # cible SPEC : < 0,3 ms


def test_no_bpm_before_min_points() -> None:
    c = ClockTracker()
    feed(c, 3)
    assert c.bpm is None


def test_position_after_start() -> None:
    c = ClockTracker()
    t = feed(c, 30)
    assert c.position() is None  # clocks à l'arrêt : pas de position
    c.start(int(t))
    feed(c, 1, t0=t)
    assert c.position() == Position(1, 1, 1)
    feed(c, 96 + 24 + 6, t0=t + BPM_143_TICK_NS)
    assert str(c.position()) == "2.2.2"
    c.stop(0)
    assert c.position() is None


def test_position_time_on_grid() -> None:
    c = ClockTracker()
    c.start(0)
    feed(c, 30)
    t = c.position_time(48)
    assert t == pytest.approx(48 * BPM_143_TICK_NS, abs=1e3)


def test_stall_resets_window() -> None:
    c = ClockTracker()
    t = feed(c, 30)
    feed(c, 1, t0=t + 1e9)
    assert c.bpm is None


def test_transfer_detection() -> None:
    c = ClockTracker()
    c.sysex((0x00, 0x20, 0x3C, 0x10), 1_000)
    assert c.transfer_suspected(1_000_000)
    assert not c.transfer_suspected(3_000_000_000)
    c2 = ClockTracker()
    c2.sysex((0x7E, 0x00), 0)
    assert not c2.transfer_suspected(1)


def test_stats_summary() -> None:
    s = Stats()
    assert s.summary() == "aucune mesure"
    for x in (1e6, -1e6):
        s.add(x)
    assert "rms 1.000 ms" in s.summary()


def test_bpm_smooth_follows_a_tempo_change_within_a_bar() -> None:
    """Tempo affiché : lissé sur 96 ticks, plus lent à suivre que `bpm` (24 ticks)."""
    c = ClockTracker()
    assert c.bpm_smooth is None
    slow, fast = 60e9 / (24 * 143), 60e9 / (24 * 152)
    t = 0.0
    for _ in range(200):
        c.tick(round(t))
        t += slow
    assert c.bpm_smooth == 143.0
    for _ in range(30):  # une noire et quart au nouveau tempo
        c.tick(round(t))
        t += fast
    smooth = c.bpm_smooth
    assert c.bpm == 152.0 and smooth is not None and 143.0 < smooth < 152.0
    for _ in range(96):
        c.tick(round(t))
        t += fast
    assert c.bpm_smooth == 152.0

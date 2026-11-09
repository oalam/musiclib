from __future__ import annotations

import time

from mk_brain.scheduler import Scheduler


def test_sends_in_target_order_close_to_time() -> None:
    sent: list[str] = []
    s: Scheduler[str] = Scheduler(sent.append)
    s.start()
    now = time.perf_counter_ns()
    s.at(now + 6_000_000, "b")
    s.at(now + 3_000_000, "a")
    time.sleep(0.03)
    s.close()
    assert sent == ["a", "b"]
    assert all(0 <= e < 2_000_000 for e in s.errors.values)  # < 2 ms, large pour la CI


def test_late_message_dropped() -> None:
    sent: list[str] = []
    s: Scheduler[str] = Scheduler(sent.append)
    s.start()
    s.at(time.perf_counter_ns() - 50_000_000, "trop tard")
    time.sleep(0.01)
    s.close()
    assert sent == [] and s.dropped == 1

from __future__ import annotations

from mk_brain.clock import TICKS_PER_BAR
from mk_brain.phrase import PhraseCounter, pattern_label

BAR = TICKS_PER_BAR


def bar_of(c: PhraseCounter, abs_bar: int, tick_in_bar: int = 0) -> int:
    """Mesure de la phrase à la mesure absolue `abs_bar` (0 = première après le Start)."""
    return c.update(abs_bar * BAR + tick_in_bar).bar


def test_counts_from_start_and_wraps() -> None:
    c = PhraseCounter(32)
    st = c.update(0)
    assert (st.bar, st.phrase, st.beat, st.pulse) == (1, 1, 1, True)
    st = c.update(26 * BAR + 30)  # mesure 27, temps 2
    assert (st.bar, st.beat, st.pulse) == (27, 2, False)
    st = c.update(32 * BAR)
    assert (st.bar, st.phrase) == (1, 2)


def test_caps_tail_countdown_blocks() -> None:
    c = PhraseCounter(64)
    st = c.update(26 * BAR)  # mesure 27 : cap 32, 6 mesures avec celle-ci (32 − 27 + 1)
    assert (st.cap, st.to_cap, st.countdown, st.tail, st.blocks_lit) == (32, 6, None, False, 4)
    st = c.update(14 * BAR)  # mesure 15 : -2 avant le cap 16
    assert (st.cap, st.countdown, st.blinking) == (16, -2, False)
    st = c.update(15 * BAR)  # mesure 16 : -1, le bloc B clignote
    assert (st.countdown, st.blinking, st.blocks_lit) == (-1, True, 2)
    st = c.update(60 * BAR)  # mesure 61 : 4 dernières
    assert st.tail and st.cap == 64 and st.blocks_lit == 8


def test_reset_applies_at_next_bar_only() -> None:
    c = PhraseCounter(32)
    pc_tick = 5 * BAR + 86  # PC 10 clocks avant la mesure absolue 6 (mesure 7 du compteur)
    assert bar_of(c, 5, 86) == 6
    assert c.reset_next_bar(pc_tick, pattern="E04") == 6
    assert bar_of(c, 5, 95) == 6  # pas à la réception
    before = c.pattern
    st = c.update(6 * BAR)
    assert (before, st.bar, st.phrase, c.pattern) == (None, 1, 1, "E04")
    assert bar_of(c, 6 + 31) == 32
    assert bar_of(c, 6 + 32) == 1


def test_recalibrate_to_block() -> None:
    c = PhraseCounter(64)
    c.update(3 * BAR + 10)
    c.reset_next_bar(3 * BAR + 10, first_bar=17)  # SHIFT + GROUP C
    assert bar_of(c, 4) == 17
    assert bar_of(c, 4 + 47) == 64


def test_stop_cancels_pending_and_start_restarts() -> None:
    c = PhraseCounter(32)
    c.reset_next_bar(10 * BAR + 90, pattern="A02")
    c.stop()
    assert not c.pending
    assert bar_of(c, 11) == 12 and c.pattern is None
    c.start()
    assert bar_of(c, 0) == 1


def test_pattern_label() -> None:
    assert pattern_label(0) == "A01"
    assert pattern_label(16 * 4 + 3) == "E04"
    assert pattern_label(127) == "H16"

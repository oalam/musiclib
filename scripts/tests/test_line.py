"""Tests de analyzer/line.py : ligne inclinee, plafond, coupures."""
from __future__ import annotations

import numpy as np
import pytest

from analyzer import line
from analyzer.line import CEILING_DB, LineError, on_line, peak_db, premaster, spectrum_top

SR = 48000


def sine(hz: float, amp: float = 0.5, dur: float = 0.5) -> np.ndarray:
    t = np.arange(int(SR * dur)) / SR
    return amp * np.sin(2 * np.pi * hz * t)


def test_tilt_adds_4_5_db_per_octave(monkeypatch: pytest.MonkeyPatch) -> None:
    # 4 kHz = 2 octaves au-dessus du pivot (1 kHz) : +9 dB d'inclinaison
    tilted = spectrum_top(sine(4000), SR)
    monkeypatch.setattr(line, "TILT_DB_OCT", 0.0)
    assert tilted - spectrum_top(sine(4000), SR) == pytest.approx(9.0, abs=0.2)


def test_level_tracks_gain() -> None:
    y = sine(1000)
    assert spectrum_top(y * 0.5, SR) - spectrum_top(y, SR) == pytest.approx(-6.02, abs=0.05)


def test_silence_raises() -> None:
    with pytest.raises(LineError):
        spectrum_top(np.zeros(1000), SR)


def test_on_line_hits_line() -> None:
    y = sine(1000, amp=0.01)
    line = spectrum_top(y, SR) + 6
    out, res = on_line(y, SR, "CP", line)
    assert res.gain_db == pytest.approx(6.0, abs=0.01)
    assert not res.capped
    assert spectrum_top(out, SR) == pytest.approx(line, abs=0.05)


def test_on_line_capped_at_ceiling() -> None:
    y = sine(1000, amp=0.4)
    _, res = on_line(y, SR, "CP", spectrum_top(y, SR) + 20)
    assert res.capped
    assert res.peak_db == pytest.approx(CEILING_DB, abs=0.01)


def test_premaster_bass_mono_and_subsonic_cut() -> None:
    st = np.stack([sine(10), sine(10)], axis=1)
    out = premaster(st, SR, "BD")
    assert out.ndim == 1                    # grave : mono integral
    assert peak_db(out[SR // 4:]) < -25     # 10 Hz coupe


def test_premaster_side_is_mono_below_120() -> None:
    low = sine(60, dur=1.0)
    st = np.stack([low, -low], axis=1)      # tout dans le side
    out = premaster(st, SR, "OH")
    assert out.shape[1] == 2
    side = (out[:, 0] - out[:, 1]) / 2
    assert peak_db(side[SR // 2:]) < peak_db(low) - 20

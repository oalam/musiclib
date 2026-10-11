"""Tests des saturations maison (Overdrive, Dynamic Tube) et de leur branchement au moteur."""
from __future__ import annotations

import numpy as np
import pytest

from analyzer import saturation as sat
from analyzer import sounddesign as sd

SR = sd.SR


def _sine(freq: float = 200.0, amp: float = 0.5, seconds: float = 0.5) -> np.ndarray:
    t = np.arange(int(seconds * SR)) / SR
    x = amp * np.sin(2 * np.pi * freq * t)
    return np.stack([x, x]).astype(np.float32)


def _harmonics(x: np.ndarray, f0: float = 200.0) -> tuple[float, float, float]:
    """Energie de la fondamentale, des harmoniques paires (2, 4) et impaires (3, 5)."""
    spec = np.abs(np.fft.rfft(x[0, SR // 10:]))
    freqs = np.fft.rfftfreq(x.shape[1] - SR // 10, 1 / SR)
    def at(f: float) -> float:
        return float(spec[np.argmin(np.abs(freqs - f))])
    return at(f0), at(2 * f0) + at(4 * f0), at(3 * f0) + at(5 * f0)


def test_overdrive_adds_even_harmonics_and_drive_increases_them():
    soft = sat.Overdrive(drive=0, tone=100, dynamics=0, width_oct=9)(_sine(), SR)
    hard = sat.Overdrive(drive=100, tone=100, dynamics=0, width_oct=9)(_sine(), SR)
    f, even, odd = _harmonics(soft)
    assert even > 0.01 * f and odd > 0.01 * f            # 0 % distord deja, asymetrique
    fh, evenh, oddh = _harmonics(hard)
    assert (evenh + oddh) / fh > 2 * (even + odd) / f


def test_overdrive_dry_wet_zero_is_transparent():
    x = _sine()
    assert np.allclose(sat.Overdrive(dry_wet=0)(x, SR), x, atol=1e-6)


def test_overdrive_dynamics_keeps_transients():
    # coup fort puis queue faible : a 100 %, l'ecart fort / faible survit a la saturation
    x = np.concatenate([_sine(amp=0.9, seconds=0.2), _sine(amp=0.05, seconds=0.3)], axis=1)
    def contrast(d: float) -> float:
        y = sat.Overdrive(drive=80, dynamics=d, width_oct=9, tone=100)(x, SR)
        return float(np.abs(y[:, 2000:9000]).max() / np.abs(y[:, 15000:]).max())
    assert contrast(100) > 3 * contrast(0)


@pytest.mark.parametrize("model", [0, 1, 2])
def test_tube_models_are_silent_on_silence(model: int):
    y = sat.DynamicTube(model=model, bias=0.6)(np.zeros((2, 4800), dtype=np.float32), SR)
    assert np.abs(y).max() < 1e-4                         # point de repos retire, pas de DC


def test_tube_model_a_clean_when_quiet_c_always_dirty():
    quiet = _sine(amp=0.2)
    fa, ea, oa = _harmonics(sat.DynamicTube(model=0, bias=0)(quiet, SR))
    fc, ec, oc = _harmonics(sat.DynamicTube(model=2, bias=0)(quiet, SR))
    assert (ea + oa) / fa < 0.01 and (ec + oc) / fc > 0.05


def test_tube_envelope_dirties_loud_parts():
    x = _sine(amp=0.8)
    def dirt(env: float) -> float:
        f, e, o = _harmonics(sat.DynamicTube(model=1, bias=0, envelope=env, drive_db=6)(x, SR))
        return (e + o) / f
    assert dirt(3) > 2 * dirt(0)


def test_block_processing_matches_one_shot():
    x = _sine(seconds=0.2)
    for plugin in (sat.Overdrive(), sat.DynamicTube(envelope=1.5)):
        whole = plugin(x, SR)
        parts = [plugin.process(x[:, lo:lo + 256], SR, reset=lo == 0) for lo in range(0, x.shape[1], 256)]
        assert np.allclose(np.concatenate(parts, axis=1), whole, atol=1e-5)


def test_devices_in_catalogue_render_and_automate():
    specs = {d.type: d for d in sd.device_specs()}
    assert specs["overdrive"].automatable and specs["dynamic_tube"].automatable
    preset = sd.Preset.model_validate({
        "id": "o", "treatment": "variations", "label": "t",
        "settings": {"bpm": 150, "length_beats": 1, "slices": 0, "jitter": 0},
        "chains": [{"name": "Kick", "devices": [
            {"type": "overdrive", "params": {"drive": 0}, "params_end": {"drive": 100}},
            {"type": "dynamic_tube", "params": {"model": 2}},
        ]}],
    })
    audio = sd.render(preset, _sine(amp=0.8, seconds=0.3))
    assert audio.shape == (2, 4 * 19_200) and np.isfinite(audio).all()
    preset.chains[0].devices[1].params_end = {"model": 1}
    with pytest.raises(sd.PresetError, match="selecteur"):
        sd.validate(preset)


def _alias_ratio(y: np.ndarray, f0: float) -> float:
    """Energie hors harmoniques de f0 (repliement) sur energie totale, sous 20 kHz."""
    seg = y[0, SR // 10:]
    spec = np.abs(np.fft.rfft(seg * np.hanning(seg.size))) ** 2
    freqs = np.fft.rfftfreq(seg.size, 1 / SR)
    harmonic = np.zeros_like(freqs, dtype=bool)
    for k in range(1, int(20000 / f0) + 1):
        harmonic |= np.abs(freqs - k * f0) < 30
    band = freqs < 20000
    return float(spec[band & ~harmonic].sum() / spec[band].sum())


def test_tube_hi_quality_reduces_aliasing():
    x = _sine(freq=5000, amp=0.9)
    lo = sat.DynamicTube(model=1, drive_db=24)(x, SR)
    hi = sat.DynamicTube(model=1, drive_db=24, hi_quality=1)(x, SR)
    assert _alias_ratio(hi, 5000) < 0.3 * _alias_ratio(lo, 5000)


def test_tube_hi_quality_blocks_match_and_silence_stays_silent():
    x = _sine(seconds=0.2)
    plugin = sat.DynamicTube(hi_quality=1, envelope=1, bias=0.5)
    whole = plugin(x, SR)
    parts = [plugin.process(x[:, lo:lo + 256], SR, reset=lo == 0) for lo in range(0, x.shape[1], 256)]
    assert np.allclose(np.concatenate(parts, axis=1), whole, atol=1e-5)
    quiet = plugin(np.zeros((2, 4800), dtype=np.float32), SR)
    assert np.abs(quiet).max() < 1e-4


@pytest.mark.parametrize("curve", range(len(sat.SATURATOR_CURVES)))
def test_saturator_curves_are_odd_bounded_and_silent(curve: int):
    plugin = sat.Saturator(curve=curve, drive_db=12)
    assert np.abs(plugin(np.zeros((2, 2400), dtype=np.float32), SR)).max() < 1e-6
    u = np.linspace(-4, 4, 801)
    y = plugin._shape(u)
    assert np.allclose(y, -y[::-1], atol=1e-9)          # impaire : pas de DC, harmoniques impaires
    assert np.abs(y).max() <= 1.6
    f, even, odd = _harmonics(plugin(_sine(amp=0.8), SR))
    assert odd > 0.01 * f and even < 0.01 * f


def test_saturator_post_clip_caps_output_and_dry_wet_zero_is_transparent():
    x = _sine(amp=0.9)
    y = sat.Saturator(curve=5, drive_db=24, post_clip=2, output_db=-6)(x, SR)
    assert np.abs(y).max() <= 10 ** (-6 / 20) + 1e-6
    assert np.allclose(sat.Saturator(dry_wet=0, drive_db=24)(x, SR), x, atol=1e-6)


def test_saturator_color_moves_saturation_to_the_highs():
    x = _sine(freq=200, amp=0.5) + _sine(freq=4000, amp=0.2)
    def high_dirt(amt_hi: float) -> float:
        y = sat.Saturator(curve=3, drive_db=6, color=1, amt_hi=amt_hi)(x, SR)
        spec = np.abs(np.fft.rfft(y[0, SR // 10:]))
        freqs = np.fft.rfftfreq(y.shape[1] - SR // 10, 1 / SR)
        return float(spec[np.argmin(np.abs(freqs - 12000))])   # 3e harmonique du 4 kHz
    assert high_dirt(100) > 2 * high_dirt(0)


def test_saturator_hi_quality_and_blocks():
    x = _sine(freq=5000, amp=0.9)
    lo = sat.Saturator(curve=6, drive_db=18)(x, SR)
    hi = sat.Saturator(curve=6, drive_db=18, hi_quality=1)(x, SR)
    assert _alias_ratio(hi, 5000) < 0.5 * _alias_ratio(lo, 5000)
    plugin = sat.Saturator(curve=7, drive_db=6, color=1, amt_lo=50, hi_quality=1, ws_depth=0.5)
    whole = plugin(x[:, :9600], SR)
    parts = [plugin.process(x[:, lo:min(lo + 256, 9600)], SR, reset=lo == 0) for lo in range(0, 9600, 256)]
    assert np.allclose(np.concatenate(parts, axis=1), whole, atol=1e-5)

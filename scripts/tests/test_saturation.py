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

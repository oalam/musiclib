"""Tests du moteur de sound design (scripts/analyzer/sounddesign.py), sur kick synthetique.

Lancer :
    python -m pytest tests/test_sounddesign.py
    python -m pytest tests/test_sounddesign.py::test_rumble_loop_length_matches_tempo
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from analyzer import sounddesign as sd
from paths import SOUNDDESIGN_PRESETS_DIR


def _kick(sr: int = sd.SR) -> np.ndarray:
    """Kick synthetique : sinus a glissando 150 -> 50 Hz, decroissance 150 ms, (2, n)."""
    t = np.arange(int(0.3 * sr)) / sr
    freq = 50 + 100 * np.exp(-t / 0.03)
    wave = np.sin(2 * np.pi * np.cumsum(freq) / sr) * np.exp(-t / 0.15)
    return np.stack([wave, wave]).astype(np.float32)


def _preset(**chain_overrides: object) -> sd.Preset:
    rumble = {"name": "Rumble", "devices": [
        {"type": "reverb", "params": {"room_size": 0.8}},
        {"type": "lowpass", "params": {"cutoff_frequency_hz": 200}},
        {"type": "duck", "params": {"depth_db": 30}},
    ]}
    rumble.update(chain_overrides)
    return sd.Preset.model_validate({
        "id": "t", "treatment": "rumble", "label": "test",
        "settings": {"bpm": 150, "bars": 1, "hits_per_bar": 4},
        "chains": [{"name": "Kick", "devices": []}, rumble],
        "master": [{"type": "limiter"}],
    })


def test_rumble_loop_length_matches_tempo():
    # 150 BPM, 1 mesure de 4 temps : 4 * 60 / 150 = 1.6 s -> 76800 echantillons
    audio = sd.render(_preset(), _kick())
    assert audio.shape == (2, 76_800)
    assert np.max(np.abs(audio)) == pytest.approx(10 ** (-1 / 20), rel=1e-3)


def test_rumble_loop_is_seamless_at_odd_tempo():
    # 185 BPM : 62270 echantillons, non divisible par 4 ; le motif doit rester periodique
    preset = _preset()
    preset.settings["bpm"] = 185
    preset.chains[0].mute = True
    m = sd.render(preset, _kick()).mean(axis=0)
    second_diff = np.abs(m[2:] - 2 * m[1:-1] + m[:-2])
    seam = abs(m[0] - (2 * m[-1] - m[-2]))
    assert seam <= np.percentile(second_diff, 99.9) * 2


def test_all_chains_muted_gives_silence():
    preset = _preset(mute=True)
    preset.chains[0].mute = True
    audio = sd.render(preset, _kick())
    assert not np.any(audio)


def test_bypass_changes_render():
    base = sd.render(_preset(), _kick())
    preset = _preset()
    preset.chains[1].devices[1].bypass = True   # lowpass coupe
    bypassed = sd.render(preset, _kick())
    assert not np.allclose(base, bypassed)


def test_duck_dips_on_triggers():
    ctx = sd.RenderContext(sr=1000, triggers=np.array([100, 600]))
    duck = sd.DEVICES["duck"].build(
        {"depth_db": 20, "attack_ms": 0, "hold_ms": 10, "release_ms": 100}, ctx)
    out = duck(np.ones((2, 1000), dtype=np.float32))
    assert out[0, 50] == pytest.approx(1.0)
    assert out[0, 105] == pytest.approx(0.1, rel=1e-3)   # -20 dB pendant la tenue
    assert out[0, 400] == pytest.approx(1.0)             # revenu avant le coup suivant


def test_width_zero_is_mono():
    ctx = sd.RenderContext(sr=sd.SR, triggers=np.array([], dtype=int))
    x = np.stack([np.ones(10), -np.ones(10)]).astype(np.float32)
    out = sd.DEVICES["width"].build({"width": 0}, ctx)(x)
    assert np.allclose(out[0], out[1])


def test_validate_rejects_unknown_device_and_out_of_range():
    preset = _preset()
    preset.chains[1].devices[0] = sd.Device(type="fuzz")
    with pytest.raises(sd.PresetError, match="device inconnu"):
        sd.validate(preset)
    preset = _preset()
    preset.chains[1].devices[1].params["cutoff_frequency_hz"] = 1e6
    with pytest.raises(sd.PresetError, match="hors de"):
        sd.validate(preset)
    preset = _preset()
    preset.settings["swing"] = 0.5
    with pytest.raises(sd.PresetError, match="inconnu"):
        sd.validate(preset)


def test_with_overrides_applies_settings_mute_bypass():
    preset = sd.with_overrides(_preset(), {"bpm": 180}, ["Kick"], [("Rumble", 2), ("master", 0)])
    assert preset.settings["bpm"] == 180
    assert preset.chains[0].mute and preset.chains[1].devices[2].bypass
    assert preset.master[0].bypass
    with pytest.raises(sd.PresetError):
        sd.with_overrides(_preset(), {}, ["Nope"], [])


def test_save_and_load_presets_roundtrip(tmp_path: Path):
    sd.save_preset(_preset(), tmp_path)
    assert [p.id for p in sd.load_presets("rumble", tmp_path)] == ["t"]


def test_vault_presets_are_valid():
    presets = sd.load_presets("rumble", SOUNDDESIGN_PRESETS_DIR)
    assert {p.id for p in presets} >= {"deep", "gritty", "kick_rumble"}


def test_load_source_resamples_and_duplicates_mono(tmp_path: Path):
    path = tmp_path / "k.wav"
    sf.write(path, _kick(44_100)[0], 44_100)
    src = sd.load_source(path)
    assert src.shape[0] == 2 and abs(src.shape[1] - int(0.3 * sd.SR)) <= 1


def test_write_render_is_stable_and_has_sidecar(tmp_path: Path):
    preset = _preset()
    audio = sd.render(preset, _kick())
    rec1 = sd.write_render(audio, Path("KIK 1.wav"), "Samples/KIK 1.wav", preset, tmp_path)
    rec2 = sd.write_render(audio, Path("KIK 1.wav"), "Samples/KIK 1.wav", preset, tmp_path)
    assert rec1.file == rec2.file and rec1.file.startswith("rumble/kik_1__t_150bpm_")
    sidecar = sd.RenderRecord.model_validate_json(
        (tmp_path / rec1.file).with_suffix(".json").read_text())
    assert sidecar.preset == preset and sidecar.seconds == pytest.approx(1.6)


def _band_energy(x: np.ndarray, lo: float, hi: float) -> float:
    spectrum = np.abs(np.fft.rfft(x[0])) ** 2
    freqs = np.fft.rfftfreq(x.shape[1], 1 / sd.SR)
    return float(spectrum[(freqs >= lo) & (freqs < hi)].sum())


def _filtered(**params: float) -> np.ndarray:
    noise = np.random.default_rng(0).standard_normal((2, sd.SR)).astype(np.float32) * 0.1
    ctx = sd.RenderContext(sr=sd.SR, triggers=np.array([], dtype=int))
    full = {"mode": 1, "cutoff_hz": 1000, "resonance": 0.0, "drive": 1, **params}
    return sd.DEVICES["filter"].build(full, ctx)(noise)


def test_filter_type_selects_lp_hp_bp():
    modes = list(sd.FILTER_MODES)
    lp = _filtered(mode=modes.index("LP24"))
    hp = _filtered(mode=modes.index("HP24"))
    bp = _filtered(mode=modes.index("BP24"))
    assert _band_energy(lp, 50, 300) > 10 * _band_energy(lp, 5000, 20000)
    assert _band_energy(hp, 5000, 20000) > 10 * _band_energy(hp, 50, 300)
    assert _band_energy(bp, 700, 1400) > _band_energy(bp, 50, 300)
    assert _band_energy(bp, 700, 1400) > _band_energy(bp, 5000, 20000)


def test_filter_resonance_boosts_around_cutoff():
    flat = _filtered(resonance=0.0)
    peaky = _filtered(resonance=0.9)
    ratio = lambda x: _band_energy(x, 800, 1250) / _band_energy(x, 100, 400)  # noqa: E731
    assert ratio(peaky) > 2 * ratio(flat)


def test_filter_mode_must_be_an_index():
    preset = _preset()
    preset.chains[1].devices.append(sd.Device(type="filter", params={"mode": 1.5}))
    with pytest.raises(sd.PresetError, match="index"):
        sd.validate(preset)
    spec = next(p for p in sd.DEVICES["filter"].spec.params if p.name == "mode")
    assert spec.choices == ["LP12", "LP24", "HP12", "HP24", "BP12", "BP24"]

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
    rec1 = sd.write_render(audio, "Samples/KIK 1.wav", preset, tmp_path, "RM 150 Kik dbr", "SUB")
    rec2 = sd.write_render(audio, "Samples/KIK 1.wav", preset, tmp_path, "RM 150 Kik dbr", "SUB")
    assert rec1.file == rec2.file and rec1.file.startswith("rumble/RM 150 Kik dbr ")
    sidecar = sd.RenderRecord.model_validate_json(
        (tmp_path / rec1.file).with_suffix(".json").read_text())
    assert sidecar.preset == preset and sidecar.seconds == pytest.approx(1.6)
    assert (sidecar.name, sidecar.sub) == ("RM 150 Kik dbr", "SUB")
    with pytest.raises(sd.PresetError, match="nom DT2"):
        sd.write_render(audio, "x", preset, tmp_path, "a/b")


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


@pytest.mark.parametrize(("source", "code", "bpm", "expected"), [
    ("BD C Punch 01 dbr", "BD", 150, "RM 150 C Punch dbr"),   # 21 car. : le numero part
    ("BD Hard 03 hcf", "BD", 185, "RM 185 Hard 03 hcf"),      # 18 car. : tout tient
    ("BD Distorted Kick 05 xtr", "BD", 190, "RM 190 Distort xtr"),
    ("BR 117 Rumble j89", "BR", 175, "RM 175 Rumble j89"),     # tempo de la source remplace
])
def test_propose_name(source: str, code: str, bpm: int, expected: str):
    name = sd.propose_name(source, code, "RM", bpm)
    assert name == expected and len(name) <= 18


def _manifest(*entries: object) -> object:
    from analyzer.samples import Manifest
    return Manifest(source_root="x", total=len(entries), entries=list(entries))


def test_target_inherits_sub_and_stays_unique():
    from analyzer.samples import SampleEntry
    kick = SampleEntry(source="d/kick.wav", family="TECHNO", code="BD", pack="dbr",
                       name="BD C Punch 01 dbr", duration=0.3, rank=1, sub="CLEAN")
    twin = SampleEntry(source="SoundDesign/rumble/a.wav", family="UNIVERSEL", code="RM",
                       pack="sou", name="RM 150 C Punch dbr", duration=1.6, rank=1, sub="CLEAN")
    assert sd.target("d/kick.wav", _manifest(kick), "rumble", 150) == ("RM 150 C Punch dbr", "CLEAN", "RM")
    name, sub, _ = sd.target("d/kick.wav", _manifest(kick, twin), "rumble", 150)
    assert name != "RM 150 C Punch dbr" and sub == "CLEAN" and len(name) <= 18
    kick.sub = "RUMBLE"            # sous-dossier manuel du kick, inconnu de RM : racine
    assert sd.target("d/kick.wav", _manifest(kick), "rumble", 150)[1] == ""


def test_verse_copies_once_marks_and_ranges_in_rm(tmp_path: Path):
    from analyzer.samples import folder_of
    out, samples_root = tmp_path / "SoundDesign", tmp_path / "Samples"
    record = sd.write_render(sd.render(_preset(), _kick()), "x", _preset(), out,
                             "RM 150 C Punch dbr", "CLEAN")
    assert sd.mark_versed([record], samples_root)[0].versed is None
    overrides: dict = {}
    key = sd.verse(record, out, samples_root, overrides)
    assert key == f"SoundDesign/{record.file}"
    ov = overrides[key]
    assert folder_of("UNIVERSEL", ov.code, ov.sub) == "DRUMS/RM/CLEAN" and ov.name == record.name
    mtime = (samples_root / key).stat().st_mtime_ns
    assert sd.verse(record, out, samples_root, overrides) == key   # rejouable, pas de recopie
    assert (samples_root / key).stat().st_mtime_ns == mtime
    assert sd.mark_versed([record], samples_root)[0].versed == key
    old = record.model_copy(update={"name": ""})                  # rendu anterieur a 8.E
    with pytest.raises(sd.PresetError, match="re-rendre"):
        sd.verse(old, out, samples_root, overrides)


def test_versed_render_lands_in_drums_rm(tmp_path: Path):
    from analyzer.samples import build_manifest
    out, samples_root = tmp_path / "SoundDesign", tmp_path / "Samples"
    record = sd.write_render(sd.render(_preset(), _kick()), "x", _preset(), out,
                             "RM 150 C Punch dbr", "CLEAN")
    overrides: dict = {}
    key = sd.verse(record, out, samples_root, overrides)
    m = build_manifest(samples_root, overrides)     # mesures reelles : blanc / long exemptes
    entry = next(e for e in m.entries if e.source == key)
    assert (entry.folder, entry.name) == ("DRUMS/RM/CLEAN", "RM 150 C Punch dbr")
    assert not {"blanc", "long"} & set(entry.flags or [])


def test_loop_starts_and_ends_in_the_duck():
    # duck anticipe : le creux est complet sur le coup, la boucle jouee une
    # fois ne demarre ni ne s'arrete en plein grondement
    preset = _preset()
    preset.chains[0].mute = True
    m = np.abs(sd.render(preset, _kick()).mean(axis=0))
    rms = float(np.sqrt(np.mean(m ** 2)))
    assert m[0] < 0.1 * rms and m[-1] < 0.1 * rms


def test_one_shot_lasts_the_chosen_beats_with_faded_tail():
    # 150 BPM, 1 temps : 60 / 150 = 0,4 s -> 19200 echantillons ; 0,5 temps -> 9600
    preset = _preset()
    preset.settings["one_shot"] = 1
    audio = sd.render(preset, _kick())
    assert audio.shape[1] == 19_200
    assert np.all(audio[:, -1] == 0)                       # fondu jusqu'a zero
    preset.settings["length_beats"] = 0.5
    assert sd.render(preset, _kick()).shape[1] == 9_600


# --- Riser et automation (8.G) ----------------------------------------------

def _riser(source: int = 0, **settings: float) -> sd.Preset:
    return sd.Preset.model_validate({
        "id": "r", "treatment": "riser", "label": "test",
        "settings": {"bpm": 150, "bars": 2, "source": source, **settings},
        "chains": [{"name": "Sweep", "devices": [
            {"type": "filter", "params": {"mode": 0, "cutoff_hz": 200},
             "params_end": {"cutoff_hz": 12000}},
            {"type": "gain", "params": {"gain_db": -30}, "params_end": {"gain_db": 0}},
        ]}],
    })


def _quarters_rms(audio: np.ndarray) -> list[float]:
    q = audio.shape[1] // 4
    return [float(np.sqrt(np.mean(audio[:, i * q:(i + 1) * q] ** 2))) for i in range(4)]


def test_riser_on_noise_rises_and_stops_dead():
    # 150 BPM, 2 mesures : 2 * 4 * 60 / 150 = 3,2 s -> 153600 echantillons
    preset = _riser()
    assert not sd.needs_source(preset)
    audio = sd.render(preset, sd.NO_SOURCE)
    assert audio.shape == (2, 153_600)
    rms = _quarters_rms(audio)
    assert rms == sorted(rms) and rms[3] > 10 * rms[0]
    assert np.all(audio[:, -1] == 0)                         # fondu anti-clic de 5 ms
    assert np.max(np.abs(audio[:, -480:-240])) > 0.05        # mais la coupe reste nette
    assert np.array_equal(audio, sd.render(preset, sd.NO_SOURCE))   # bruit reproductible


def test_riser_filter_sweep_opens_the_spectrum():
    audio = sd.render(_riser(), sd.NO_SOURCE)
    q = audio.shape[1] // 4
    first, last = audio[:, :q], audio[:, -q:]
    def share(x: np.ndarray) -> float:
        return _band_energy(x, 4000, 20000) / _band_energy(x, 20, 20000)
    assert share(last) > 10 * share(first)


def test_riser_pitch_rise_on_sample_source():
    # sinus 220 Hz, +12 demi-tons : la fin est autour de 440 Hz
    t = np.arange(4800) / sd.SR
    sine = np.tile(np.sin(2 * np.pi * 220 * t).astype(np.float32), (2, 1))
    preset = _riser(source=2, pitch_st=12, curve=1)
    preset.chains[0].devices = []
    assert sd.needs_source(preset)
    audio = sd.render(preset, sine)
    tail = audio[0, -4800:]
    freqs = np.fft.rfftfreq(len(tail), 1 / sd.SR)
    assert abs(freqs[np.argmax(np.abs(np.fft.rfft(tail)))] - 440) < 25


def test_automation_without_end_matches_static_render():
    static = sd.render(_preset(), _kick())
    auto = _preset()
    auto.chains[1].devices[1].params_end = {"cutoff_frequency_hz": 200}   # fin = debut
    assert np.allclose(sd.render(auto, _kick()), static, atol=1e-6)


def test_automation_validation():
    preset = _riser()
    preset.chains[0].devices[0].params_end = {"mode": 2}
    with pytest.raises(sd.PresetError, match="selecteur"):
        sd.validate(preset)
    preset.chains[0].devices[0].params_end = {"cutoff_hz": 1e6}
    with pytest.raises(sd.PresetError, match="hors de"):
        sd.validate(preset)
    preset.chains[0].devices[0] = sd.Device(type="duck", params_end={"depth_db": 10})
    with pytest.raises(sd.PresetError, match="non supportee"):
        sd.validate(preset)


def test_static_preset_json_has_no_params_end():
    # hash des rendus rumble anterieurs a 8.G inchange
    assert "params_end" not in _preset().model_dump_json()


def test_riser_target_is_fx_rise():
    from analyzer.samples import Manifest, SampleEntry
    m = Manifest(source_root="x", total=0)
    assert sd.target("", m, "riser", 150) == ("FX 150 Rise Noise", "RISE", "FX")
    pad = SampleEntry(source="p/pad.wav", family="AMBIENT", code="PD", pack="nz",
                      name="PD C Warm 01 nz", duration=4.0, rank=1, sub="AMBIENT")
    name, sub, _ = sd.target("p/pad.wav", _manifest(pad), "riser", 150)
    assert sub == "RISE" and name.startswith("FX 150 ") and len(name) <= 18


# --- Variations en tranches (8.I) --------------------------------------------

def _variations(slices: int = 1, jitter: float = 0.0) -> sd.Preset:
    return sd.Preset.model_validate({
        "id": "v", "treatment": "variations", "label": "test",
        "settings": {"bpm": 150, "length_beats": 1, "slices": slices, "jitter": jitter},
        "chains": [{"name": "Kick", "devices": [
            {"type": "distortion", "params": {"drive_db": 0}, "params_end": {"drive_db": 30}},
        ]}],
    })


def test_variations_are_equal_slices_on_the_grid():
    # 8 tranches d'un temps a 150 BPM : 8 x 60 / 150 = 3,2 s -> 8 x 19200 echantillons
    audio = sd.render(_variations(), _kick())
    assert audio.shape == (2, 8 * 19_200)
    slices = audio.reshape(2, 8, 19_200)
    assert np.all(slices[:, :, -1] == 0)                    # chaque tranche finit en fondu
    assert np.all(np.abs(slices[:, :, :200]).max(axis=2) > 0.05)   # et commence par le coup


def test_variations_progress_and_levels_match():
    slices = sd.render(_variations(), _kick()).reshape(2, 8, 19_200)
    window = int(sd.LEVEL_WINDOW_MS * sd.SR / 1000)
    levels = np.sqrt(np.mean(slices[:, :, :window] ** 2, axis=(0, 2)))
    assert levels.max() / levels.min() < 1.05               # niveau egalise
    # plus de drive = plus d'harmoniques aigues
    def bright(x: np.ndarray) -> float:
        return _band_energy(x, 1000, 20000) / _band_energy(x, 20, 20000)
    assert bright(slices[:, 7]) > 3 * bright(slices[:, 0])


def test_variant_positions_progressive_with_bounded_jitter():
    assert np.allclose(sd.variant_positions(5, 0), [0, 0.25, 0.5, 0.75, 1])
    jit = sd.variant_positions(16, 1)
    assert np.all(np.abs(jit - np.arange(16) / 15) <= 0.5 / 15 + 1e-9)
    assert np.array_equal(jit, sd.variant_positions(16, 1))  # reproductible


def test_variations_target_keeps_source_code_and_tags_slices(tmp_path: Path):
    from analyzer.samples import SLICES_TAG, SampleEntry
    kick = SampleEntry(source="d/kick.wav", family="TECHNO", code="BD", pack="dbr",
                       name="BD C Punch 01 dbr", duration=0.3, rank=1, sub="CLEAN")
    preset = _variations()
    assert sd.slice_count(preset) == 8
    t = sd.target("d/kick.wav", _manifest(kick), "variations", 150, 8)
    assert t == ("BD V8 C Punch dbr", "CLEAN", "BD")
    out, samples_root = tmp_path / "SoundDesign", tmp_path / "Samples"
    record = sd.write_render(sd.render(preset, _kick()), "x", preset, out, t.name, t.sub, t.code)
    assert (record.code, record.slices) == ("BD", 8)
    overrides: dict = {}
    key = sd.verse(record, out, samples_root, overrides)
    assert (overrides[key].code, overrides[key].sub, overrides[key].tags) == ("BD", "CLEAN", [SLICES_TAG])
    assert sd.mark_versed([record], samples_root)[0].folder == "DRUMS/BD/CLEAN"


def test_versed_slices_are_not_flagged_long(tmp_path: Path):
    from analyzer.samples import build_manifest
    out, samples_root = tmp_path / "SoundDesign", tmp_path / "Samples"
    preset = _variations()
    record = sd.write_render(sd.render(preset, _kick()), "x", preset, out,
                             "BD V8 C Punch dbr", "CLEAN", "BD")
    overrides: dict = {}
    key = sd.verse(record, out, samples_root, overrides)
    entry = next(e for e in build_manifest(samples_root, overrides).entries if e.source == key)
    assert entry.folder == "DRUMS/BD/CLEAN" and "long" not in (entry.flags or [])


# --- Layering (8.J) ----------------------------------------------------------

def _click(delay_ms: float = 0.0) -> np.ndarray:
    """Clic aigu court precede de `delay_ms` de silence (couche d'attaque)."""
    n0 = int(delay_ms * sd.SR / 1000)
    t = np.arange(int(0.02 * sd.SR)) / sd.SR
    wave = np.cos(2 * np.pi * 3000 * t) * np.exp(-t / 0.003)
    x = np.concatenate([np.zeros(n0), wave])
    return np.stack([x, x]).astype(np.float32)


def _layered(offset_ms: float = 0.0, **layer: object) -> sd.Preset:
    return sd.Preset.model_validate({
        "id": "l", "treatment": "variations", "label": "test",
        "settings": {"bpm": 150, "length_beats": 1, "slices": 0, "jitter": 0},
        "chains": [{"name": "Kick", "devices": []},
                   {"name": "Click", "layer": 1, "offset_ms": offset_ms, **layer}],
        "output_peak_db": None,
    })


def test_neutral_layering_fields_keep_json_and_render():
    preset = _preset()
    assert "layer" not in preset.model_dump_json()
    assert np.array_equal(sd.render(preset, _kick()), sd.render(preset, _kick(), [_click()]))


def test_onset_and_alignment_put_attacks_together():
    assert sd.onset(_click(10)) == 480                       # 10 ms a 48 kHz
    ref = sd.onset(_kick())
    kick, click = sd.align_layers([_kick(), _click(10)], [0.0, 0.0])
    assert sd.onset(kick) == sd.onset(click) == ref          # silence initial de la couche coupe
    _, late = sd.align_layers([_kick(), _click(10)], [0.0, 5.0])
    assert sd.onset(late) == ref + 240                       # + 5 ms
    # avancer la couche de 5 ms sous son attaque : tout est retarde d'autant
    kick, early = sd.align_layers([_kick(), _click()], [0.0, -5.0])
    assert (sd.onset(kick), sd.onset(early)) == (240, 0)


def test_chain_reads_its_layer():
    preset = _layered()
    preset.chains[0].mute = True
    audio = sd.render(preset, _kick(), [_click()])[:, 19_200:]   # tranche 1 = source brute
    assert _band_energy(audio, 2000, 5000) > 10 * _band_energy(audio, 20, 200)
    with pytest.raises(sd.SourceError, match="couche 1"):
        sd.render(preset, _kick())


def test_chain_gain_end_blends_across_slices():
    # tranche 1 = source brute, puis couche du clic de -60 dB (tranche 2) a 0 dB (tranche 4)
    preset = _layered(gain_db=-60, gain_db_end=0)
    slices = sd.render(preset, _kick(), [_click()]).reshape(2, 4, 19_200)
    ratios = [_band_energy(slices[:, i], 2000, 5000) / _band_energy(slices[:, i], 20, 200)
              for i in range(1, 4)]
    assert ratios == sorted(ratios) and ratios[2] > 100 * ratios[0]


def test_layering_validation():
    for bad in ({"layer": 4}, {"offset_ms": 60}, {"gain_db_end": 40}):
        with pytest.raises(sd.PresetError):
            sd.validate(_layered(**bad))


def test_layers_change_render_file_name(tmp_path: Path):
    preset = _layered()
    a = sd.output_name("BD C Punch", preset)
    assert sd.output_name("BD C Punch", preset, ["k/click.wav"]) != a
    record = sd.write_render(np.zeros((2, 10), dtype=np.float32), "k/kick.wav", preset,
                             tmp_path, "BD L Punch", layers=["k/click.wav"])
    assert record.layers == ["k/click.wav"]


def test_variations_first_slice_is_the_raw_source():
    # tranche 1 = la source sans traitement (au niveau egalise pres), tranche 2 = variante sobre
    slices = sd.render(_variations(), _kick()).reshape(2, 8, 19_200)
    kick = _kick()[0]
    first = slices[0, 0, : kick.size - 1000]
    ref = kick[: first.size]
    assert abs(np.corrcoef(first, ref)[0, 1]) > 0.999
    assert not np.allclose(slices[0, 1, :1000] / np.abs(slices[0, 1]).max(),
                           slices[0, 0, :1000] / np.abs(slices[0, 0]).max(), atol=1e-3)

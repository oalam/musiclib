"""Classement des samples DT2 (analyzer/samples.py, samples.py) — Phase 7.J1."""
from __future__ import annotations

import json
import sys
import wave
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import samples as cli  # noqa: E402
from analyzer import samples as smp  # noqa: E402
from analyzer.samples import NAME_MAX, Override  # noqa: E402


def _wav(path: Path, seconds: float = 0.2, rate: int = 8000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"\x00\x00" * int(seconds * rate))


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    root = tmp_path / "Samples"
    for i in range(1, 6):
        _wav(root / "Hardcore free samples" / "Kicks" / f"Hard Kick {i:02d}.wav")
    _wav(root / "Hardcore free samples" / "Snare 01.wav")          # case de 1 -> repliee
    _wav(root / "909" / "clean" / "bd01.wav")
    _wav(root / "909" / "clean" / "bd02.wav")
    _wav(root / "rthm" / "kick" / "Long Kick.wav", seconds=5.0)    # > 4 s -> LP
    _wav(root / "elektron pack" / "Mega" / "Mono" / "Kick Chain 1.wav")
    _wav(root / "elektron pack" / "Mega" / "Stereo" / "Kick Chain 1.wav")
    _wav(root / "recorded" / "take.wav")
    _wav(root / "MPC_Kit" / "zzz01.wav")                           # non classe
    return root


def test_wav_duration_reads_header(tmp_path: Path) -> None:
    _wav(tmp_path / "a.wav", seconds=1.5)
    assert smp.wav_duration(tmp_path / "a.wav") == pytest.approx(1.5)
    (tmp_path / "b.wav").write_bytes(b"not a wav")
    assert smp.wav_duration(tmp_path / "b.wav") is None


@pytest.mark.parametrize("rel, family", [
    ("Vi Ta Lee /MILLENNIUM KICKS 3/x.wav", "HARDCORE"),
    ("Vi Ta Lee /DARKTECHNO/x.wav", "TECHNO"),
    ("rthm/loops/histibe/x.wav", "AUTRES"),
    ("rthm/loops/hardcore/x.wav", "HARDCORE"),
    ("Tribalism Vol 1/x.wav", "TRIBE"),
    ("minimoog synth/x.wav", "UNIVERSEL"),
    ("Native instrument/arcane/x.wav", "UNIVERSEL"),
    ("Native instrument/caribean/x.wav", "AUTRES"),
    ("recorded/x.wav", "SAMPLE"),
])
def test_family_rules(rel: str, family: str) -> None:
    assert smp.family_of(rel) == family


@pytest.mark.parametrize("rel, code", [
    ("rthm/packs/linndrum/Linn_TomHi_03_SP.wav", "TM"),
    ("909/clean/bd10.wav", "BD"),
    ("909/clean/sd05.wav", "SD"),
    ("Jungle 89  to 99/Breaks/Amen.wav", "BR"),
    ("x/OpenHH Willada.wav", "OH"),
    ("x/Closed Hihat 2.wav", "HH"),
    ("MPC_Kit/clk01.wav", None),
])
def test_code_rules(rel: str, code: str | None) -> None:
    assert smp.code_of(rel, 0.3) == code


def test_bpm_in_folder_does_not_make_a_loop() -> None:
    rel = "SAMPLES MEGABIT/95 BPM Industrial Techno Pack/Drums/Closed Hihat 28.wav"
    assert smp.code_of(rel, 0.3) == "HH"
    assert smp.code_of("x/Groovy thing 126 bpm.wav", 2.0) == "LP"


def test_long_drum_becomes_loop() -> None:
    assert smp.code_of("rthm/kick/Long Kick.wav", 5.0) == "LP"


@pytest.mark.parametrize("rel, code, pack, expected", [
    ("rthm/packs/neurotek/Kicks/DenseKick_SP_03.wav", "BD", "rth", "BD Dense 03 rth"),
    ("909/BPB Cassette 909/cassette 1/bd01.wav", "BD", "909", "BD Casset 01 909"),
    ("Jungle 89  to 99/Breaks/Amen 170 bpm.wav", "BR", "j89", "BR 170 Amen j89"),
    ("Vi Ta Lee /OVERDRIVE III/Vi Ta Lee - OVERDRIVE III - 02 XTRMRAW_OVERDRIVE3_KICK_G#_02.wav",
     "BD", "vtl", "BD G# Overd 02 vtl"),
])
def test_short_name(rel: str, code: str, pack: str, expected: str) -> None:
    name = smp.short_name(rel, code, pack)
    assert name == expected
    assert len(name) <= NAME_MAX


def test_unique_suffix_keeps_length() -> None:
    taken = {"BD Dense 03 rth"}
    name = smp._unique("BD Dense 03 rth", taken)
    assert name != "BD Dense 03 rth" and name.endswith(" rth") and len(name) <= NAME_MAX


def test_quota() -> None:
    assert smp.quota("HARDCORE", "BD") == 32
    assert smp.quota("TRIBE", "LP") == 32
    assert smp.quota("UNIVERSEL", "BD") == 32
    assert smp.quota("UNIVERSEL", "SD") == 16
    assert smp.quota("JUNGLE", "FX") == 8
    assert smp.quota("SAMPLE", "RS") is None


def test_build_manifest(tree: Path) -> None:
    m = smp.build_manifest(tree, {})
    by_src = {e.source: e for e in m.entries}
    # mono ecarte au profit de la stereo
    assert not any("/Mono/" in s for s in by_src)
    assert any("/Stereo/" in s for s in by_src)
    # case HARDCORE/SD (1 fichier) repliee dans UNIVERSEL
    assert by_src["Hardcore free samples/Snare 01.wav"].family == "UNIVERSEL"
    assert "HARDCORE/SD" in m.folded
    # HARDCORE/BD a 5 fichiers : reste en famille
    assert by_src["Hardcore free samples/Kicks/Hard Kick 01.wav"].family == "HARDCORE"
    assert by_src["rthm/kick/Long Kick.wav"].code == "LP"
    assert m.unclassified == ["MPC_Kit/zzz01.wav"]
    # SAMPLE n'est jamais replie ni plafonne
    assert by_src["recorded/take.wav"].family == "SAMPLE"
    assert all(e.selected for e in m.entries)          # tout tient dans les quotas
    names = [e.dest for e in m.entries]
    assert len(names) == len(set(names))


def test_overrides(tree: Path) -> None:
    ov = {
        "MPC_Kit/zzz01.wav": Override(code="PC", family="TRIBE", name="PC Zzz 01 mpc"),
        "909/clean/bd02.wav": Override(exclude=True),
    }
    m = smp.build_manifest(tree, ov)
    by_src = {e.source: e for e in m.entries}
    e = by_src["MPC_Kit/zzz01.wav"]
    # famille forcee : pas de repli meme seule dans sa case
    assert (e.family, e.code, e.name) == ("TRIBE", "PC", "PC Zzz 01 mpc")
    assert "909/clean/bd02.wav" not in by_src
    assert m.unclassified == []


def test_rerun_keeps_listening_decisions(tree: Path) -> None:
    first = smp.build_manifest(tree, {})
    for e in first.entries:
        if e.source.endswith("Hard Kick 01.wav"):
            e.status = "drop"
        if e.source.endswith("Hard Kick 02.wav"):
            e.status = "keep"
    second = smp.build_manifest(tree, {}, previous=first)
    by_src = {e.source: e for e in second.entries}
    assert by_src["Hardcore free samples/Kicks/Hard Kick 01.wav"].status == "drop"
    assert not by_src["Hardcore free samples/Kicks/Hard Kick 01.wav"].selected
    assert by_src["Hardcore free samples/Kicks/Hard Kick 02.wav"].selected


def test_select_keeps_exceed_quota() -> None:
    cell = [smp.SampleEntry(source=f"s{i}", family="JUNGLE", code="FX", pack="p",
                            name=f"FX {i}", duration=1.0, rank=i,
                            status="keep" if i < 10 else "pending")
            for i in range(1, 13)]
    smp.select(cell, 8)
    assert sum(e.selected for e in cell) == 9            # 9 keep, aucun pending
    assert not any(e.selected for e in cell if e.status == "pending")


def test_cli_writes_manifest(tree: Path, tmp_path: Path,
                             monkeypatch: pytest.MonkeyPatch,
                             capsys: pytest.CaptureFixture[str]) -> None:
    meta = tmp_path / "meta"
    monkeypatch.setattr(cli, "MANIFEST_FILE", meta / "manifest.json")
    monkeypatch.setattr(cli, "OVERRIDES_FILE", meta / "overrides.json")
    assert cli.main(["--source", str(tree), "--dry-run"]) == 0
    assert not (meta / "manifest.json").exists()
    assert cli.main(["--source", str(tree)]) == 0
    data = json.loads((meta / "manifest.json").read_text())
    assert data["unclassified"] == ["MPC_Kit/zzz01.wav"]
    assert cli.main(["--report"]) == 0
    assert "HARDCORE" in capsys.readouterr().out


def test_cli_rejects_bad_overrides(tree: Path, tmp_path: Path,
                                   monkeypatch: pytest.MonkeyPatch) -> None:
    bad = tmp_path / "overrides.json"
    bad.write_text("{oops")
    monkeypatch.setattr(cli, "MANIFEST_FILE", tmp_path / "manifest.json")
    monkeypatch.setattr(cli, "OVERRIDES_FILE", bad)
    assert cli.main(["--source", str(tree)]) == 1


@pytest.mark.integration
def test_real_samples_names_fit() -> None:
    from paths import SAMPLES_SRC_DIR, media_available
    if not media_available() or not SAMPLES_SRC_DIR.is_dir():
        pytest.skip("SSD media absent")
    m = smp.build_manifest(SAMPLES_SRC_DIR, {})
    assert all(len(e.name) <= NAME_MAX for e in m.entries)
    assert len({e.dest for e in m.entries}) == len(m.entries)


def test_bpm_folder_is_loop_fallback() -> None:
    assert smp.code_of("Music Radar/Cyclick/110bpm/WP_BeanGourd_110-01.wav", 2.0) == "PC"
    assert smp.code_of("Music Radar/Cyclick/110bpm/WP_Thing_110-01.wav", 2.0) == "LP"

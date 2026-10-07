"""Classement des samples DT2 (analyzer/samples.py, samples.py) — Phase 7.J1, 7.J2."""
from __future__ import annotations

import json
import sys
import wave
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

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
    assert smp.code_of("x/Groovy thing 126 bpm.wav", 2.0) == "DL"


def test_long_drum_becomes_loop() -> None:
    assert smp.code_of("rthm/kick/Long Kick.wav", 5.0) == "DL"


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
    assert smp.quota("TRIBE", "DL") == 32
    assert smp.quota("JUNGLE", "PL") == 16
    assert smp.quota("UNIVERSEL", "ML") == 8
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
    assert by_src["rthm/kick/Long Kick.wav"].code == "DL"
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
    m = smp.build_manifest(SAMPLES_SRC_DIR, {}, measure_fn=None)
    assert all(len(e.name) <= NAME_MAX for e in m.entries)
    assert len({e.dest for e in m.entries}) == len(m.entries)


def test_bpm_folder_is_loop_fallback() -> None:
    assert smp.code_of("Music Radar/Cyclick/110bpm/WP_BeanGourd_110-01.wav", 2.0) == "PC"
    assert smp.code_of("Music Radar/Cyclick/110bpm/WP_Thing_110-01.wav", 2.0) == "PL"


@pytest.mark.parametrize("rel, code", [
    ("rthm/loops/breakbeat/Think 170.wav", "BR"),
    ("Loops Pack/Drum Loops/Rolling 01.wav", "DL"),
    ("rthm/loops/hh loops/Hats 120 bpm.wav", "PL"),
    ("jungle dnb rthm/Tops/Top 03.wav", "PL"),
    ("Loops Pack/Synth Loops/Acid 140 bpm.wav", "ML"),
    ("Hardcore free samples/HSI/LS-HSI Hardcore Sequence Wet [142 BPM] 01-03.wav", "ML"),
    ("Loops Pack/Sample Packs/Reese Loop 01.wav", "BL"),
    ("Jungle 89  to 99/Pads/Groove Therapy Pad.wav", "PD"),
    ("x/loops/Vocal Loop 2.wav", "VX"),
    ("jungle dnb rthm/Builds/Build 04.wav", "FX"),
])
def test_loop_codes(rel: str, code: str) -> None:
    assert smp.code_of(rel, 4.0) == code


def test_loop_name_keeps_bpm_and_note() -> None:
    assert smp.short_name("Loops Pack/Synth Loops/Acid A 140 bpm.wav", "ML", "lpk") == "ML 140 A Acid lpk"


def test_name_without_room_for_desc() -> None:
    name = smp.short_name("instru/synth/170_F#_Synthloop 045_516.wav", "ML", "ins")
    assert name == "ML 170 F# 516 ins" and len(name) <= NAME_MAX


# --- Pre-filtre qualite (7.J2) ----------------------------------------------

def _tone(path: Path, seconds: float = 0.3, amp: float = 0.5, lead_s: float = 0.0,
          clip: bool = False, rate: int = 8000) -> Path:
    t = np.arange(int(seconds * rate)) / rate
    y = amp * np.sin(2 * np.pi * 100 * t)
    if clip:
        y = np.clip(4 * y, -1.0, 1.0)
    y = np.concatenate([np.zeros(int(lead_s * rate)), y])
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), y, rate, subtype="FLOAT")
    return path


@pytest.mark.parametrize(("kwargs", "code", "flags"), [
    ({}, "BD", []),
    ({"amp": 0.001}, "BD", ["muet"]),
    ({"amp": 0.05}, "BD", ["faible"]),
    ({"clip": True}, "BD", ["sature"]),
    ({"lead_s": 0.1}, "BD", ["blanc"]),
    ({"lead_s": 0.1}, "DL", []),                 # une boucle peut commencer par un silence
    ({"seconds": 3.0}, "SD", ["long"]),
    ({"seconds": 3.0}, "FX", []),
])
def test_measure_flags(tmp_path: Path, kwargs: dict[str, float], code: str,
                       flags: list[str]) -> None:
    assert smp.measure(_tone(tmp_path / "x.wav", **kwargs), code) == flags


def test_measure_unreadable(tmp_path: Path) -> None:
    bad = tmp_path / "bad.wav"
    bad.write_bytes(b"RIFF0000WAVEnope")
    assert smp.measure(bad, "BD") == ["illisible"]


def test_isolated_full_scale_peak_is_not_clipping() -> None:
    a = np.zeros(1000)
    a[10] = a[500] = 1.0
    assert smp.clipped_share(a) == 0.0
    a[600:610] = 1.0
    assert smp.clipped_share(a) == pytest.approx(0.01)


def test_flagged_candidates_go_last_and_measures_are_reused(tmp_path: Path) -> None:
    root = tmp_path / "Samples"
    _tone(root / "Hardcore free samples" / "Kicks" / "Kick 01.wav", amp=0.001)
    for i in range(2, 6):
        _tone(root / "Hardcore free samples" / "Kicks" / f"Kick {i:02d}.wav")
    first = smp.build_manifest(root, {})
    cell = smp.cell_of(first, "HARDCORE", "BD")
    assert cell[-1].source.endswith("Kick 01.wav")
    assert cell[-1].flags == ["muet"]
    assert [e.flags for e in cell[:-1]] == [[]] * 4

    def boom(path: Path, code: str) -> list[str]:
        raise AssertionError("mesure deja faite")
    second = smp.build_manifest(root, {}, previous=first, measure_fn=boom)
    assert [e.source for e in smp.cell_of(second, "HARDCORE", "BD")] == [e.source for e in cell]


def test_set_status_promotes_next_pending() -> None:
    m = smp.Manifest(source_root="x", total=20, entries=[
        smp.SampleEntry(source=f"s{i}", family="JUNGLE", code="FX", pack="p",
                        name=f"FX {i}", duration=1.0, rank=i) for i in range(1, 11)])
    smp.select(m.entries, 8)
    assert not m.entries[8].selected
    cell = smp.set_status(m, "s1", "drop")
    assert [e.source for e in cell if e.selected] == [f"s{i}" for i in range(2, 10)]
    with pytest.raises(smp.SampleError):
        smp.set_status(m, "absent", "keep")


def test_move_keeps_status_and_survives_rebuild(tree: Path, tmp_path: Path) -> None:
    m = smp.build_manifest(tree, {}, measure_fn=None)
    src = "Hardcore free samples/Kicks/Hard Kick 01.wav"
    old_cell, ov = smp.move(m, src, "TRIBE", "PC", tree, measure_fn=lambda p, c: [c])
    assert src not in {e.source for e in old_cell}
    e = next(x for x in m.entries if x.source == src)
    assert (e.family, e.code, e.status, e.flags) == ("TRIBE", "PC", "pending", ["PC"])
    assert e.name.startswith("PC ") and len(e.name) <= NAME_MAX
    assert e.selected
    # l'override replace le fichier dans sa nouvelle case au prochain passage
    again = smp.build_manifest(tree, {src: ov}, previous=m, measure_fn=None)
    e2 = next(x for x in again.entries if x.source == src)
    assert (e2.family, e2.code) == ("TRIBE", "PC")
    with pytest.raises(smp.SampleError):
        smp.move(m, src, "TRIBE", "ZZ", tree)
    with pytest.raises(smp.SampleError):
        smp.move(m, src, "POLKA", "BD", tree)


def test_moved_pending_lands_in_reserve_of_full_cell() -> None:
    m = smp.Manifest(source_root="x", total=10, entries=[
        smp.SampleEntry(source=f"s{i}", family="JUNGLE", code="FX", pack="p",
                        name=f"FX {i} p", duration=1.0, rank=i) for i in range(1, 10)]
        + [smp.SampleEntry(source="v", family="JUNGLE", code="VX", pack="p",
                           name="VX v p", duration=1.0, rank=1)])
    smp.select(m.entries[:9], 8)
    smp.move(m, "v", "JUNGLE", "FX", Path("/absent"), measure_fn=None)
    v = next(e for e in m.entries if e.source == "v")
    assert v.rank == 10 and not v.selected


def test_save_overrides_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "overrides.json"
    cli.save_overrides({"b.wav": Override(code="PC"), "a.wav": Override(exclude=True)}, path)
    assert json.loads(path.read_text()) == {"a.wav": {"exclude": True}, "b.wav": {"code": "PC"}}
    assert cli.load_overrides(path)["b.wav"].code == "PC"

"""Classement des samples DT2 (analyzer/samples.py, samples.py) — Phase 7.J1 a 7.J7."""
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
    _wav(root / "Hardcore free samples" / "Snare 01.wav")
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
    ("rthm/packs/neurotek/Kicks/x.wav", "TRIBE"),
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
    assert smp.code_of("rthm/packs/neurotek/Kicks/BreakApartKick_SP_01.wav", 0.38) == "BD"
    assert smp.code_of("Jungle 89  to 99/Breaks/Adrift Break.wav", 6.0) == "BR"
    # un "fill" de 0,3 s est une frappe
    assert smp.code_of("NI/caribean/oneshot/Drums/Percussion/Fill Papayera 1.wav", 0.28) == "PC"


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
    assert smp.quota("LOOPS/DL/150") == 32
    assert smp.quota("LOOPS/BR") == 32
    assert smp.quota("LOOPS/PL/SKIN") == 32
    assert smp.quota("LOOPS/ML/KEYS") == 16
    assert smp.quota("DRUMS/BD/HARD") == 16
    assert smp.quota("FX/RISE") == 16
    assert smp.quota("VX") == 16
    assert smp.quota("SAMPLE/BD") is None


@pytest.mark.parametrize("family, code, sub, folder", [
    ("HARDCORE", "BD", "HARD", "DRUMS/BD/HARD"),
    ("UNIVERSEL", "BD", "", "DRUMS/BD"),
    ("JUNGLE", "BR", "150", "LOOPS/BR/150"),
    ("AUTRES", "PD", "", "TONAL/PD"),
    ("UNIVERSEL", "FX", "RISE", "FX/RISE"),
    ("UNIVERSEL", "VX", "", "VX"),
    ("SAMPLE", "BD", "HARD", "SAMPLE/BD"),     # SAMPLE : pas de sous-categorie
    ("UNIVERSEL", "RS", "", "SAMPLE/RS"),
    ("UNIVERSEL", "HH", "HARD", "DRUMS/HH"),   # code sans sous-categorie
])
def test_folder_of(family: str, code: str, sub: str, folder: str) -> None:
    assert smp.folder_of(family, code, sub) == folder
    assert smp.folder_code(folder) == code


@pytest.mark.parametrize("rel, code, sub", [
    ("Hardcore free samples/Kicks/Kick 01.wav", "BD", "HARD"),
    ("909/clean/bd01.wav", "BD", "CLEAN"),
    ("Music Radar/Percussion/Conga Hit 02.wav", "PC", "SKIN"),
    ("instru/piano/Soft Piano C.wav", "ML", "KEYS"),
    ("rthm/loops/jungle/170_Think.wav", "BR", "150"),
    ("rthm/loops/jungle/Think.wav", "BR", ""),
    ("x/y/Thing.wav", "BD", ""),
    ("minimoog synth/Moog Bass 03.wav", "BS", "ANALOG"),
])
def test_sub_of(rel: str, code: str, sub: str) -> None:
    assert smp.sub_of(rel, code) == sub


@pytest.mark.parametrize("rel, dur, sub", [
    ("bass/oneshot/Invaders 01.wav", 0.3, "SHORT"),
    ("bass/oneshot/Invaders 02.wav", 1.1, "MID"),
    ("bass/oneshot/Invaders 03.wav", 4.0, "LONG"),
    ("bass/oneshot/Sub Invaders.wav", 4.0, "SUB"),      # le mot passe avant la duree
    ("bass/oneshot/Invaders 04.wav", None, ""),
])
def test_bass_sub_by_duration(rel: str, dur: float | None, sub: str) -> None:
    assert smp.sub_of(rel, "BS", dur) == sub
    assert sub == "" or sub in smp.SUBS["BS"]


@pytest.mark.parametrize("rel, code, dur, sub", [
    ("minimoog synth/Lead 03.wav", "ST", 1.0, "ANALOG"),
    ("x/oneshot/Bell Blip 02.wav", "ST", 0.3, "BELL"),
    ("x/oneshot/Weird 02.wav", "ST", 3.0, "LONG"),
    ("Jungle 89  to 99/Pads/Ambience 04.wav", "PD", 8.0, "AMBIENT"),
    ("Native instrument/lone forest/oneshot/Valley.wav", "PD", 2.5, "SHORT"),
    ("Native instrument/lone forest/oneshot/Dune.wav", "PD", 6.0, "LONG"),
])
def test_tonal_subs(rel: str, code: str, dur: float, sub: str) -> None:
    assert smp.sub_of(rel, code, dur) == sub


def test_cinematic_thumps_and_transitions_are_fx() -> None:
    assert smp.code_of("cinematic Noiiz/Low End Thumps/Thump 03.wav", 2.0) == "FX"
    assert smp.code_of("cinematic Noiiz/Transitions/Swoosh 01.wav", 3.0) == "FX"
    assert smp.sub_of("cinematic Noiiz/Transitions/Swoosh 01.wav", "FX") == "RISE"
    assert smp.sub_of("cinematic Noiiz/Low End Thumps/Thump 03.wav", "FX") == "HIT"


def test_target_folders() -> None:
    folders = smp.target_folders()
    assert folders[0] == "DRUMS/BD" and "DRUMS/BD/HARD" in folders
    assert "LOOPS/DL/180" in folders and "FX/RISE" in folders and "VX/MC" in folders
    assert not any(f.startswith("SAMPLE") for f in folders)


def test_build_manifest(tree: Path) -> None:
    m = smp.build_manifest(tree, {})
    by_src = {e.source: e for e in m.entries}
    # mono ecarte au profit de la stereo
    assert not any("/Mono/" in s for s in by_src)
    assert any("/Stereo/" in s for s in by_src)
    # BD/CLEAN (2 fichiers) remonte a la racine du code
    assert by_src["909/clean/bd01.wav"].folder == "DRUMS/BD"
    assert m.folded == ["DRUMS/BD/CLEAN"]
    # BD/HARD a 5 fichiers : reste ; la famille devient un tag de genre
    kick = by_src["Hardcore free samples/Kicks/Hard Kick 01.wav"]
    assert (kick.folder, kick.family) == ("DRUMS/BD/HARD", "HARDCORE")
    assert "hardcore" in kick.auto_tags
    assert by_src["Hardcore free samples/Snare 01.wav"].folder == "DRUMS/SD"
    assert by_src["rthm/kick/Long Kick.wav"].folder == "LOOPS/DL"
    assert m.unclassified == ["MPC_Kit/zzz01.wav"]
    # SAMPLE n'est jamais plafonne
    assert by_src["recorded/take.wav"].folder == "SAMPLE/RS"
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
    # famille forcee : genre du fichier, sans effet sur le dossier
    assert (e.family, e.folder, e.name) == ("TRIBE", "DRUMS/PC", "PC Zzz 01 mpc")
    assert "tribe" in e.auto_tags
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
    assert "BD/HARD" in capsys.readouterr().out


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
    m = smp.build_manifest(SAMPLES_SRC_DIR, {}, measure_fn=None, note_fn=None)
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
    ("Jungle 89  to 99/Pads/Groove Therapy Pad.wav", "ML"),    # LOOPS/ML/PADS (7.J8)
    ("x/loops/Vocal Loop 2.wav", "VX"),
    ("jungle dnb rthm/Builds/Build 04.wav", "FX"),
])
def test_loop_codes(rel: str, code: str) -> None:
    assert smp.code_of(rel, 4.0) == code


def test_loop_name_keeps_bpm_and_note() -> None:
    assert smp.short_name("Loops Pack/Synth Loops/Acid A 140 bpm.wav", "ML", "lpk") == "ML 140 A Acid lpk"


def test_name_without_room_for_desc() -> None:
    name = smp.short_name("instru/synth/170_F#_Synthloop 045_516.wav", "ML", "ins")
    assert name == "ML 170 F# 45 ins" and len(name) <= NAME_MAX


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
    cell = smp.cell_of(first, "DRUMS/BD/HARD")
    assert cell[-1].source.endswith("Kick 01.wav")
    assert cell[-1].flags == ["muet"]
    assert [e.flags for e in cell[:-1]] == [[]] * 4

    def boom(path: Path, code: str) -> list[str]:
        raise AssertionError("mesure deja faite")
    second = smp.build_manifest(root, {}, previous=first, measure_fn=boom)
    assert [e.source for e in smp.cell_of(second, "DRUMS/BD/HARD")] == [e.source for e in cell]


def test_set_status_promotes_next_pending() -> None:
    m = smp.Manifest(source_root="x", total=20, entries=[
        smp.SampleEntry(source=f"s{i}", family="JUNGLE", code="FX", pack="p",
                        name=f"FX {i}", duration=1.0, rank=i) for i in range(1, 19)])
    smp.select(m.entries, 16)
    assert not m.entries[16].selected
    cell = smp.set_status(m, "s1", "drop")
    assert [e.source for e in cell if e.selected] == [f"s{i}" for i in range(2, 18)]
    with pytest.raises(smp.SampleError):
        smp.set_status(m, "absent", "keep")


def test_move_keeps_status_and_survives_rebuild(tree: Path, tmp_path: Path) -> None:
    m = smp.build_manifest(tree, {}, measure_fn=None)
    src = "Hardcore free samples/Kicks/Hard Kick 01.wav"
    ovs: dict[str, Override] = {}
    smp.move(m, ovs, src, "PC", "SKIN", tree, measure_fn=lambda p, c: [c])
    assert src not in {e.source for e in smp.cell_of(m, "DRUMS/BD/HARD")}
    e = next(x for x in m.entries if x.source == src)
    assert (e.family, e.folder, e.status, e.flags) == ("HARDCORE", "DRUMS/PC/SKIN", "pending", ["PC"])
    assert e.name.startswith("PC ") and len(e.name) <= NAME_MAX
    assert e.selected
    # l'override replace le fichier dans sa nouvelle case au prochain passage,
    # sous-categorie forcee comprise (pas de repli, meme seule)
    assert ovs == {src: Override(code="PC", sub="SKIN")}
    again = smp.build_manifest(tree, ovs, previous=m, measure_fn=None)
    e2 = next(x for x in again.entries if x.source == src)
    assert e2.folder == "DRUMS/PC/SKIN"
    # racine forcee : la sous-categorie inferee ne revient pas
    smp.move(again, ovs, "Hardcore free samples/Kicks/Hard Kick 02.wav", "BD", "", tree,
             measure_fn=None)
    third = smp.build_manifest(tree, ovs, previous=again, measure_fn=None)
    assert {e.source: e.folder for e in third.entries}[
        "Hardcore free samples/Kicks/Hard Kick 02.wav"] == "DRUMS/BD"
    with pytest.raises(smp.SampleError):
        smp.move(m, ovs, src, "ZZ", "", tree)
    with pytest.raises(smp.SampleError):
        smp.move(m, ovs, src, "HH", "HARD", tree)


def test_moved_pending_lands_in_reserve_of_full_cell() -> None:
    m = smp.Manifest(source_root="x", total=10, entries=[
        smp.SampleEntry(source=f"s{i}", family="JUNGLE", code="FX", pack="p",
                        name=f"FX {i} p", duration=1.0, rank=i) for i in range(1, 18)]
        + [smp.SampleEntry(source="v", family="JUNGLE", code="VX", pack="p",
                           name="VX v p", duration=1.0, rank=1)])
    smp.select(m.entries[:17], 16)
    smp.move(m, {}, "v", "FX", "", Path("/absent"), measure_fn=None)
    v = next(e for e in m.entries if e.source == "v")
    assert v.rank == 18 and not v.selected


def test_save_overrides_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "overrides.json"
    cli.save_overrides({"b.wav": Override(code="PC"), "a.wav": Override(exclude=True)}, path)
    assert json.loads(path.read_text()) == {"a.wav": {"exclude": True}, "b.wav": {"code": "PC"}}
    assert cli.load_overrides(path)["b.wav"].code == "PC"



@pytest.mark.parametrize(("rel", "dur", "code"), [
    ("instru/piano/100_Cm_Lofipiano_SP_09_406.wav", 19.2, "ML"),
    ("rthm/loops/jungle dnb/170_HeavyBoiBeat_02_516.wav", 5.6, "DL"),
    ("instru/key/CPCT_120_C_Gamelan_01.wav", 4.0, "ML"),
    ("jungle/vb6_drm120_megadrive2.wav", 3.0, "DL"),
    ("instru/oneshot/170_F_BumbleBeeSynth_02_516.wav", 2.8, "ST"),   # dossier one-shot
    ("instru/piano/100_Cm_Piano_Hit.wav", 1.0, "ST"),                # trop court
    ("drums/Kick_120_Hard.wav", 0.4, "BD"),
])
def test_tempo_in_name_makes_a_loop(rel: str, dur: float, code: str) -> None:
    assert smp.code_of(rel, dur) == code


def test_loop_name_tempo_without_bpm_and_label_ids() -> None:
    assert smp.short_name("instru/key/CPCT_120_C_Gamelan_01.wav", "ML", "ins").startswith("ML 120 C ")
    name = smp.short_name("rthm/loops/jungle dnb/170_HeavyBoiBeat_02_516.wav", "DL", "rth")
    assert name.startswith("DL 170 ") and "516" not in name and name.endswith(" 02 rth")


def test_exact_duplicate_across_packs_keeps_classified_copy(tmp_path: Path) -> None:
    root = tmp_path / "Samples"
    _wav(root / "aaa copy" / "170_HeavyBoiBeat_02.wav", seconds=3.0)
    _wav(root / "aaa copy" / "zz9_Thing.wav", seconds=3.0)              # non classe...
    _wav(root / "rthm" / "loops" / "zz9_Thing.wav", seconds=3.0)        # ... double classe
    _wav(root / "rthm" / "loops" / "170_HeavyBoiBeat_02.wav", seconds=3.0)
    _wav(root / "rthm" / "loops" / "other" / "Unique Loop.wav", seconds=3.0)
    raws, unclassified, _, _ = smp.classify(root, {})
    srcs = sorted(r.source for r in raws) + unclassified
    assert "aaa copy/170_HeavyBoiBeat_02.wav" not in srcs
    assert "rthm/loops/170_HeavyBoiBeat_02.wav" in srcs
    assert "rthm/loops/zz9_Thing.wav" in srcs and "aaa copy/zz9_Thing.wav" not in srcs


@pytest.mark.parametrize(("stem", "tempo"), [
    ("120 sklep break", 120),
    ("02_cbdnb_bassdrum_fill_175_multitrack(2)", 175),
    ("hndnb_drums_full_loop07_176_multitrack", 176),
    ("wp_beangourd_110-01", None),            # Cyclick : tempo du dossier, pas du nom
    ("feedback rough bass 110hz top", None),
    ("kick_09_406", None),
])
def test_tempo_from_name(stem: str, tempo: int | None) -> None:
    assert smp.tempo_from_name(stem) == tempo


def test_long_kick_in_kicks_pack_stays_oneshot() -> None:
    mk = "Vi Ta Lee /MILLENNIUM KICKS 3/Vi Ta Lee - MILLENNIUM KICKS 3 - 45 XTRMRAW_MLNM3_KICK_A_045.wav"
    assert smp.code_of(mk, 4.8) == "BD"
    # les vraies boucles d'un dossier de kicks le disent dans leur nom
    assert smp.code_of("SAMPLES MEGABIT/Ultra Kicks Vol. 2/LS-UK2 Bonus Loop 14.wav", 1.8) == "DL"
    assert smp.code_of("Drumbrute kick/KIK DB 160 (16).wav", 3.0) == "DL"


def test_long_drum_in_oneshot_folder_stays_oneshot() -> None:
    assert smp.code_of("NI/arcane/one shot/Drums/Cymbal/Crash FourHundred.wav", 4.4) == "CY"
    assert smp.code_of("rthm/kick/Long Kick.wav", 5.0) == "DL"
    assert smp.code_of("rthm/packs/neurotek/Kicks/BreakApartKick_SP_01.wav", 0.38) == "BD"
    assert smp.code_of("Jungle 89  to 99/Breaks/Adrift Break.wav", 6.0) == "BR"
    # un "fill" de 0,3 s est une frappe
    assert smp.code_of("NI/caribean/oneshot/Drums/Percussion/Fill Papayera 1.wav", 0.28) == "PC"


@pytest.mark.parametrize(("tempo", "dur", "expected"), [
    (140.0, 3.429, 140),     # 2 mesures
    (70.0, 3.429, 140),      # librosa a la moitie
    (172.0, 11.163, 172),    # 8 mesures
    (128.0, 3.429, None),    # incoherent avec la duree
])
def test_snap_to_bars(tempo: float, dur: float, expected: int | None) -> None:
    assert smp.snap_to_bars(tempo, dur) == expected


def test_measured_bpm_named_and_cached(tree: Path) -> None:
    calls: list[str] = []

    def fake(path: Path, dur: float | None) -> tuple[int | None, bool]:
        calls.append(path.name)
        return 140, True
    first = smp.build_manifest(tree, {}, measure_fn=None, bpm_fn=fake)
    e = next(x for x in first.entries if x.source == "rthm/kick/Long Kick.wav")
    assert (e.bpm, e.bpm_est) == (140, True) and e.name.startswith("DL 140 ")
    assert calls == ["Long Kick.wav"]
    smp.build_manifest(tree, {}, previous=first, measure_fn=None, bpm_fn=fake)
    assert calls == ["Long Kick.wav"]


# --- Bibliotheque (7.J4) ----------------------------------------------------

def _cell_manifest(n: int = 20) -> smp.Manifest:
    m = smp.Manifest(source_root="x", total=n, entries=[
        smp.SampleEntry(source=f"s{i}", family="JUNGLE", code="FX", pack="p",
                        name=f"FX {i}", duration=1.0, rank=i) for i in range(1, n + 1)],
        unclassified=["MPC_Kit/zzz01.wav"])
    smp.select(m.entries, 16)
    return m


def test_stars_rank_rated_first_without_keeping() -> None:
    m = _cell_manifest()
    ovs: dict[str, Override] = {}
    smp.set_stars(m, ovs, "s20", 2)
    smp.set_stars(m, ovs, "s19", 5)
    cell = smp.cell_of(m, "FX")
    assert [e.source for e in cell[:3]] == ["s19", "s20", "s1"]
    assert cell[0].selected and cell[0].status == "pending"     # noter ne vaut pas garder
    assert not next(e for e in cell if e.source == "s15").selected
    smp.set_stars(m, ovs, "s19", None)
    assert ovs == {"s20": Override(stars=2)}
    with pytest.raises(smp.SampleError):
        smp.set_stars(m, ovs, "s1", 6)
    with pytest.raises(smp.SampleError):
        smp.set_stars(m, ovs, "absent", 3)


def test_tags_normalized_and_listed() -> None:
    m = _cell_manifest()
    ovs: dict[str, Override] = {}
    assert smp.set_tags(m, ovs, "s1", add=["  Acid  Line ", "dark", ""]) == ["acid line", "dark"]
    assert smp.set_tags(m, ovs, "MPC_Kit/zzz01.wav", add=["Tribe"]) == ["tribe"]
    assert smp.set_tags(m, ovs, "s1", remove=["DARK"]) == ["acid line"]
    assert m.entries[0].tags == ["acid line"]
    assert smp.all_tags(ovs) == ["acid line", "tribe"]
    loose = smp.loose(m, ovs, "unclassified")
    assert [(x.source, x.pack, x.tags) for x in loose] == [("MPC_Kit/zzz01.wav", "mpc", ["tribe"])]


def test_unclassified_gets_a_cell(tree: Path) -> None:
    m = smp.build_manifest(tree, {}, measure_fn=None)
    src = "MPC_Kit/zzz01.wav"
    assert src in m.unclassified
    ovs = {src: Override(tags=["perc"])}
    smp.move(m, ovs, src, "PC", "", tree, measure_fn=lambda p, c: [], bpm_fn=None)
    e = next(x for x in m.entries if x.source == src)
    assert (e.family, e.folder, e.status, e.tags, e.selected) == (
        "UNIVERSEL", "DRUMS/PC", "pending", ["perc"], True)
    assert src not in m.unclassified
    again = smp.build_manifest(tree, ovs, previous=m, measure_fn=None)
    assert any(x.source == src and x.code == "PC" for x in again.entries)


def test_trash_and_restore(tree: Path) -> None:
    m = smp.build_manifest(tree, {}, measure_fn=None)
    kick = "Hardcore free samples/Kicks/Hard Kick 01.wav"
    loose_src = "MPC_Kit/zzz01.wav"
    ovs: dict[str, Override] = {}
    smp.set_status(m, kick, "keep")
    smp.trash(m, ovs, kick)
    smp.trash(m, ovs, loose_src)
    assert m.trashed == [kick, loose_src]
    assert kick not in {e.source for e in m.entries} and loose_src not in m.unclassified
    # la corbeille survit a une reconstruction, et aux reclassements
    again = smp.build_manifest(tree, ovs, previous=m, measure_fn=None)
    assert again.trashed == [kick, loose_src] and loose_src not in again.unclassified
    with pytest.raises(smp.SampleError):
        smp.move(again, ovs, kick, "BD", "", tree)
    smp.restore(again, ovs, kick, tree, measure_fn=None, bpm_fn=None)
    smp.restore(again, ovs, loose_src, tree, measure_fn=None, bpm_fn=None)
    e = next(x for x in again.entries if x.source == kick)
    assert (e.family, e.folder, e.status) == ("HARDCORE", "DRUMS/BD/HARD", "pending")
    assert loose_src in again.unclassified and again.trashed == [] and ovs == {}
    with pytest.raises(smp.SampleError):
        smp.restore(again, ovs, kick, tree)


def test_rebuild_ranks_rated_first(tree: Path) -> None:
    last = "Hardcore free samples/Kicks/Hard Kick 05.wav"
    m = smp.build_manifest(tree, {last: Override(stars=1, tags=["x"])}, measure_fn=None)
    cell = smp.cell_of(m, "DRUMS/BD/HARD")
    assert (cell[0].source, cell[0].stars, cell[0].tags) == (last, 1, ["x"])


# --- Kits (7.J5) ---------------------------------------------------------------

@pytest.mark.parametrize(("rel", "kit"), [
    ("Native instrument/caribean/oneshot/Drums/Kick/K 1.wav", "Native instrument/caribean"),
    ("rthm/packs/neurotek/kick/bd.wav", "rthm/packs/neurotek"),
    ("rthm/loops/a.wav", "rthm/loops"),
    ("MPC_Kit/zzz01.wav", "MPC_Kit"),
    ("take.wav", ""),
])
def test_kit_of(rel: str, kit: str) -> None:
    assert smp.kit_of(rel) == kit


def _big_cell(tmp_path: Path, n: int = 60) -> Path:
    """Une case DRUMS/SD (quota 16 -> 48 candidats) qui deborde, sur deux kits."""
    root = tmp_path / "Samples"
    for i in range(n):
        kit = "A" if i % 2 else "B"
        _wav(root / "Hardcore free samples" / kit / f"Snare {i:02d}.wav")
    return root


def test_reserve_lists_files_beyond_cap_and_promotes(tmp_path: Path) -> None:
    root = _big_cell(tmp_path)
    m = smp.build_manifest(root, {}, measure_fn=None)
    assert (len(m.entries), len(m.reserve)) == (48, 12)
    spare = m.reserve[0].source
    assert smp.known(m, spare)
    rows = smp.overflow_of(m, "DRUMS/SD", "Hardcore free samples/" + spare.split("/")[1])
    assert rows and all(r.overflow and not r.selected for r in rows)
    ovs: dict[str, Override] = {}
    assert smp.promote(m, ovs, spare, root, measure_fn=lambda p, c: [], bpm_fn=None)
    smp.set_status(m, spare, "keep")
    assert spare not in {r.source for r in m.reserve}
    # garde : epingle, reste candidat a la reconstruction
    again = smp.build_manifest(root, ovs, previous=m, measure_fn=None)
    e = next(x for x in again.entries if x.source == spare)
    assert e.status == "keep" and e.selected and len(again.reserve) == 11
    # corbeille directe depuis la reserve
    other = again.reserve[0].source
    smp.trash(again, ovs, other)
    assert other in again.trashed and not smp.promote(again, ovs, other, root)


def test_kit_tags_are_inherited(tmp_path: Path) -> None:
    root = _big_cell(tmp_path)
    m = smp.build_manifest(root, {}, measure_fn=None)
    ovs: dict[str, Override] = {}
    kit = "Hardcore free samples/A"
    assert smp.set_kit_tags(m, ovs, kit, add=["Gabber", "acid"]) == ["acid", "gabber"]
    rows = [*m.entries, *m.reserve]
    assert all(r.tags == ["acid", "gabber"] for r in rows if smp.in_kit(r.source, kit))
    assert all(r.tags == [] for r in rows if not smp.in_kit(r.source, kit))
    src = next(r.source for r in m.entries if smp.in_kit(r.source, kit))
    assert smp.set_tags(m, ovs, src, add=["sec"]) == ["acid", "gabber", "sec"]
    assert smp.kit_tags(ovs) == {kit: ["acid", "gabber"]}
    again = smp.build_manifest(root, ovs, previous=m, measure_fn=None)
    assert next(x for x in again.entries if x.source == src).tags == ["acid", "gabber", "sec"]
    smp.set_kit_tags(again, ovs, kit, remove=["acid", "gabber"])
    assert f"{kit}/" not in ovs
    with pytest.raises(smp.SampleError):
        smp.set_kit_tags(again, ovs, "Hardcore free samples/Z", add=["x"])


def test_trash_and_restore_kit(tmp_path: Path) -> None:
    root = _big_cell(tmp_path)
    m = smp.build_manifest(root, {}, measure_fn=None)
    ovs: dict[str, Override] = {}
    kit = "Hardcore free samples/A"
    m = smp.trash_kit(m, ovs, kit, root, measure_fn=None, bpm_fn=None)
    assert m.trashed_kits == {kit: 30} and ovs[f"{kit}/"].trash
    assert not any(smp.in_kit(s, kit) for s in [e.source for e in m.entries]
                   + [r.source for r in m.reserve])
    assert len(m.entries) == 30 and not m.reserve      # B remonte de la reserve
    info = {k.kit: k for k in smp.kits(m)}
    assert info[kit].trashed_kit and info[kit].files == 30
    with pytest.raises(smp.SampleError):
        smp.trash_kit(m, ovs, kit, root, measure_fn=None, bpm_fn=None)
    m = smp.restore_kit(m, ovs, kit, root, measure_fn=None, bpm_fn=None)
    assert not m.trashed_kits and ovs == {} and len(m.entries) + len(m.reserve) == 60
    with pytest.raises(smp.SampleError):
        smp.restore_kit(m, ovs, kit, root)
    with pytest.raises(smp.SampleError):
        smp.trash_kit(m, ovs, "nope", root)


def test_kits_summary_and_loose_filter(tree: Path) -> None:
    m = smp.build_manifest(tree, {}, measure_fn=None)
    info = {k.kit: k for k in smp.kits(m)}
    assert info["Hardcore free samples/Kicks"].candidates == 5
    assert info["MPC_Kit"].unclassified == 1 and info["MPC_Kit"].pack == "MPC_Kit"
    assert [x.source for x in smp.loose(m, {}, "unclassified", kit="MPC_Kit")] == ["MPC_Kit/zzz01.wav"]
    assert smp.loose(m, {}, "unclassified", kit="909") == []


# --- Tags inferes (7.J6) -------------------------------------------------------

def test_auto_tags_from_folders_and_masking() -> None:
    src = "Jungle 89 to 99/Breaks/HiHats Classic/x.wav"
    assert smp.auto_tags_of({}, src) == ["breakbeat", "classic", "hat", "jungle"]
    ovs = {"Jungle 89 to 99/": Override(no_auto=["classic"]), src: Override(no_auto=["hat"])}
    assert smp.auto_tags_of(ovs, src) == ["breakbeat", "jungle"]
    assert smp.TAG_GROUP["jungle"] == "genre" and smp.TAG_GROUP["hat"] == "instrument"
    # le nom du fichier n'entre pas en compte, seulement les dossiers
    assert smp.auto_tags_of({}, "misc/kick snare.wav") == []


def test_tag_report_lists_uncovered_words() -> None:
    srcs = [f"Native instrument/caribean/oneshot/k{i}.wav" for i in range(3)]
    report = dict(smp.tag_report(srcs, min_files=3))
    assert report["native"] == 3 and "caribean" not in report


def test_build_manifest_fills_auto_tags(tree: Path) -> None:
    m = smp.build_manifest(tree, {}, measure_fn=None)
    e = next(x for x in m.entries if x.source.startswith("Hardcore free samples/Kicks/"))
    assert e.auto_tags == ["hardcore", "kick"]


def test_filter_facets_and_or(tmp_path: Path) -> None:
    root = _big_cell(tmp_path)
    _wav(root / "jungle dnb rthm" / "loops" / "170_break.wav", seconds=3.0)
    _wav(root / "MPC_Kit" / "zzz01.wav")
    m = smp.build_manifest(root, {}, measure_fn=None, bpm_fn=None)
    F = smp.SampleFilter
    assert not F().active()
    loops = smp.filter_manifest(m, F(kind="loop"), {})
    assert {e.code for e in loops.entries} == {"BR"} and loops.unclassified == []
    rhythm = smp.filter_manifest(m, F(section="rhythm", kits=["Hardcore free samples/A"]), {})
    assert len(rhythm.entries) + len(rhythm.reserve) == 30
    melodic = smp.filter_manifest(m, F(section="melodic"), {})
    assert melodic.entries == [] and melodic.reserve == []
    # OU dans la facette tags, ET avec le texte
    both = smp.filter_manifest(m, F(tags=["jungle", "hardcore"]), {})
    assert len(both.entries) + len(both.reserve) == 61
    text = smp.filter_manifest(m, F(tags=["jungle", "hardcore"], q="170"), {})
    assert [e.code for e in text.entries] == ["BR"]
    assert smp.filter_manifest(m, F(q="zzz"), {}).unclassified == ["MPC_Kit/zzz01.wav"]
    facets = {t: (g, n) for t, g, n in smp.facet_tags(m, {})}
    assert facets["hardcore"] == ("genre", 60) and facets["jungle"][0] == "genre"


# --- Tonalite (7.J7) --------------------------------------------------------

def _pitched(path: Path, hz: float, seconds: float = 0.8, rate: int = 22050) -> Path:
    """One-shot a fondamentale fixe, attaque franche et decroissance."""
    t = np.arange(int(seconds * rate)) / rate
    y = 0.8 * np.exp(-3 * t) * (np.sin(2 * np.pi * hz * t) + 0.3 * np.sin(4 * np.pi * hz * t))
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), y, rate, subtype="FLOAT")
    return path


@pytest.mark.parametrize(("hz", "code", "note"), [
    (55.0, "BD", "A"), (49.0, "BD", "G"), (41.2, "BS", "E"), (261.6, "PD", "C")])
def test_measure_note(tmp_path: Path, hz: float, code: str, note: str) -> None:
    got, got_hz = smp.measure_note(_pitched(tmp_path / "x.wav", hz), code)
    assert got == note and got_hz is not None and abs(got_hz - hz) / hz < 0.03


def test_measure_note_peak_check_bs_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """BD : pyin seul ; BS : note incertaine si le pic spectral diverge."""
    monkeypatch.setattr(smp, "spectral_peak", lambda *a: 70.0)   # C#, loin de A
    path = _pitched(tmp_path / "x.wav", 55.0)
    assert smp.measure_note(path, "BD")[0] == "A"
    note, hz = smp.measure_note(path, "BS")
    assert note is None and hz is not None


def test_measure_note_silence_and_unreadable(tmp_path: Path) -> None:
    _wav(tmp_path / "s.wav", seconds=0.5, rate=22050)
    assert smp.measure_note(tmp_path / "s.wav", "BD") == (None, None)
    bad = tmp_path / "bad.wav"
    bad.write_bytes(b"RIFFxxxx")
    assert smp.measure_note(bad, "BD") == (None, None)


def test_pitch_helpers() -> None:
    assert smp.pitch_class(440.0) == "A" and smp.pitch_class(51.9) == "G#"
    assert smp.sharp("Bb") == "A#" and smp.sharp("C#") == "C#"
    assert smp.name_note("x/LS-HK Bounce Kick 21 F#.wav", "BD") == "F#"
    assert smp.name_note("x/LS-HK Bounce Kick 21 F#.wav", "SD") is None


def test_measured_note_in_name() -> None:
    assert smp.short_name("p/Overd 02.wav", "BD", "vtl", note="G#") == "BD G# Overd 02 vtl"
    # la note du nom reste prioritaire
    assert smp.short_name("p/Kick A 02.wav", "BD", "vtl", note="G#").startswith("BD A ")


def test_build_manifest_notes(tree: Path) -> None:
    _wav(tree / "909" / "clean" / "bd03 Bb.wav")
    calls: list[str] = []

    def fake(path: Path, code: str) -> tuple[str | None, float | None]:
        calls.append(path.name)
        return ("G#", 51.5) if path.name == "bd01.wav" else (None, 80.0)
    first = smp.build_manifest(tree, {}, measure_fn=None, bpm_fn=None, note_fn=fake)
    by = {e.source.rsplit("/", 1)[-1]: e for e in first.entries}
    assert (by["bd01.wav"].note, by["bd01.wav"].note_src) == ("G#", "mesure")
    assert by["bd01.wav"].name.startswith("BD G# ")
    assert (by["bd02.wav"].note, by["bd02.wav"].note_hz, by["bd02.wav"].note_src) == (None, 80.0, "incertaine")
    assert by["bd03 Bb.wav"].note == "A#" and by["bd03 Bb.wav"].note_src == "nom"
    assert "bd03 Bb.wav" not in calls and "take.wav" not in calls
    # reprise du manifeste precedent : rien n'est remesure
    n = len(calls)
    again = smp.build_manifest(tree, {}, previous=first, measure_fn=None, bpm_fn=None, note_fn=fake)
    assert len(calls) == n and next(e for e in again.entries if e.source.endswith("bd01.wav")).note == "G#"


def test_move_remeasures_note(tree: Path) -> None:
    m = smp.build_manifest(tree, {}, measure_fn=None, bpm_fn=None, note_fn=None)
    src = "recorded/take.wav"
    smp.move(m, {}, src, "BS", "", tree, measure_fn=None, bpm_fn=None,
             note_fn=lambda p, c: ("E", 41.2))
    e = next(x for x in m.entries if x.source == src)
    assert (e.folder, e.note, e.note_src) == ("SAMPLE/BS", "E", "mesure") and e.name.startswith("BS E ")
    smp.move(m, {}, src, "FX", "", tree, measure_fn=None, bpm_fn=None, note_fn=None)
    assert (e.note, e.note_src) == (None, None) and e.name.startswith("FX ")


def test_filter_by_note_and_wheel() -> None:
    entries = [smp.SampleEntry(source=f"p/bd{i}.wav", family="JUNGLE", code="BD", pack="p",
                               name=f"BD {i}", duration=0.3, rank=i, note=n)
               for i, n in enumerate(["A", "G#", None], 1)]
    m = smp.Manifest(source_root="/x", total=5, entries=entries, unclassified=["p/u.wav"],
                     reserve=[smp.ReserveSample(source="p/Kick A 09.wav", family="JUNGLE",
                                                code="BD", pack="p", duration=0.3)])
    got = smp.filter_manifest(m, smp.SampleFilter(notes=["A", "C"]), {})
    assert [e.note for e in got.entries] == ["A"] and len(got.reserve) == 1
    assert got.unclassified == []
    wheel = dict(smp.facet_notes(m))
    assert list(wheel) == list(smp.PITCH_CLASSES)
    assert (wheel["A"], wheel["G#"], wheel["C"]) == (2, 1, 0)
    assert dict(smp.facet_notes(m, kit="q"))["A"] == 0  # roue du kit (7.K)
    assert dict(smp.facet_notes(m, kit="p"))["A"] == 2
    rows = smp.overflow_of(m, "DRUMS/BD")
    assert (rows[0].note, rows[0].note_src) == ("A", "nom")


# --- Export (7.J3) ----------------------------------------------------------

def _export_setup(tmp_path: Path) -> tuple[smp.Manifest, Path, Path, Path]:
    root = tmp_path / "Samples"
    for i in range(1, 4):
        _wav(root / "p" / f"fx{i}.wav", seconds=0.1 * i)
    m = smp.Manifest(source_root=str(root), total=3, entries=[
        smp.SampleEntry(source=f"p/fx{i}.wav", family="JUNGLE", code="FX", pack="p",
                        name=f"FX {i} p", duration=0.1 * i, rank=i, selected=i < 3)
        for i in range(1, 4)])
    return m, root, tmp_path / "Live" / "samples", tmp_path / "export.json"


def test_export_copies_selected_and_is_rerunnable(tmp_path: Path) -> None:
    m, root, dest, index = _export_setup(tmp_path)
    dry = smp.export(m, root, dest, index, dry_run=True)
    assert dry.copied == ["FX/FX 1 p.wav", "FX/FX 2 p.wav"] and dry.files == 2
    assert not dest.exists() and not index.exists()
    first = smp.export(m, root, dest, index)
    assert sorted(p.name for p in (dest / "FX").iterdir()) == ["FX 1 p.wav", "FX 2 p.wav"]
    assert (dest / "FX/FX 1 p.wav").read_bytes() == (root / "p/fx1.wav").read_bytes()
    assert first.bytes == sum((root / f"p/fx{i}.wav").stat().st_size for i in (1, 2))
    again = smp.export(m, root, dest, index)
    assert (again.copied, again.unchanged, again.removed) == ([], 2, [])


def test_export_removes_only_its_own_files(tmp_path: Path) -> None:
    m, root, dest, index = _export_setup(tmp_path)
    smp.export(m, root, dest, index)
    (dest / "FX/mine.wav").write_bytes(b"x")                 # pose a la main
    m.entries[0].selected = False
    m.entries[1].sub = "RISE"                                        # case changee
    r = smp.export(m, root, dest, index)
    assert r.removed == ["FX/FX 1 p.wav", "FX/FX 2 p.wav"]
    assert r.copied == ["FX/RISE/FX 2 p.wav"]
    assert sorted(p.name for p in (dest / "FX").iterdir() if p.is_file()) == ["mine.wav"]
    m.entries[1].sub = ""
    m.entries[0].selected = True
    (dest / "FX/FX 1 p.wav").write_bytes(b"autre")          # conflit : pas ecrase
    r = smp.export(m, root, dest, index)
    assert r.conflicts == ["FX/FX 1 p.wav"] and (dest / "FX/FX 1 p.wav").read_bytes() == b"autre"
    assert not (dest / "FX" / "RISE").exists()                       # case videe retiree


def test_export_resumes_interrupted_copy_and_reports_missing(tmp_path: Path) -> None:
    m, root, dest, index = _export_setup(tmp_path)
    (dest / "FX").mkdir(parents=True)
    (dest / "FX/FX 1 p.wav").write_bytes((root / "p/fx1.wav").read_bytes())
    (root / "p/fx2.wav").unlink()
    r = smp.export(m, root, dest, index)
    assert (r.unchanged, r.copied, r.missing, r.conflicts) == (1, [], ["p/fx2.wav"], [])
    assert list(smp.load_export_index(index)) == ["FX/FX 1 p.wav"]


def test_cli_export(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                    capsys: pytest.CaptureFixture[str]) -> None:
    m, root, dest, index = _export_setup(tmp_path)
    monkeypatch.setattr(cli, "MANIFEST_FILE", tmp_path / "manifest.json")
    monkeypatch.setattr(cli, "EXPORT_INDEX_FILE", index)
    cli.save_manifest(m, cli.MANIFEST_FILE)
    assert cli.main(["--export", "--dry-run", "--source", str(root), "--dest", str(dest)]) == 0
    assert "2 a copier" in capsys.readouterr().out and not dest.exists()
    assert cli.main(["--export", "--source", str(root), "--dest", str(dest)]) == 0
    assert "2 copies" in capsys.readouterr().out and (dest / "FX/FX 2 p.wav").exists()

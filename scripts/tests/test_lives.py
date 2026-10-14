"""Lives DT2 (Phase 7.L) : banques, 0-COMMON, noms, RAM, export rejouable."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from analyzer import lives as lv
from analyzer.samples import Manifest, ReserveSample, SampleEntry


def _wav(path: Path, seconds: float, sr: int = 44_100, channels: int = 2) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(path, np.zeros((int(seconds * sr), channels), dtype=np.float32), sr, subtype="PCM_24")


@pytest.fixture
def lib(tmp_path: Path) -> tuple[Manifest, Path]:
    root = tmp_path / "Samples"
    for rel in ("k/kick.wav", "k/hat.wav", "d/drone C.wav", "me/rec.wav", "SoundDesign/rumble/r.wav"):
        _wav(root / rel, 1.0)
    entries = [
        SampleEntry(source="k/kick.wav", family="TRIBE", code="BD", pack="k",
                    name="BD F Hard 01 k", duration=1.0, rank=1),
        SampleEntry(source="SoundDesign/rumble/r.wav", family="UNIVERSEL", code="RM", pack="sou",
                    name="RM 150 F Hard k", duration=1.0, rank=1, parent="k/kick.wav"),
        SampleEntry(source="k/hat.wav", family="TRIBE", code="HH", pack="k",
                    name="HH Tick k", duration=1.0, rank=1),
        SampleEntry(source="me/rec.wav", family="SAMPLE", code="BL", pack="me",
                    name="BL 168 AcidG1 me", duration=1.0, rank=1),
        SampleEntry(source="k/rs.wav", family="SAMPLE", code="RS", pack="k",
                    name="RS Take k", duration=1.0, rank=1),
    ]
    reserve = [ReserveSample(source="d/drone C.wav", family="AUTRES", code="PD", pack="drn",
                             duration=1.0)]
    m = Manifest(source_root=str(root), total=5, entries=entries, reserve=reserve,
                 unclassified=["x/loose.wav"])
    return m, root


def _live(tmp_path: Path) -> lv.Live:
    return lv.create_live(tmp_path / "lives", "solaris", ["A-HALF", "B-DNB"], pack="slr")


def test_create_validates_names(tmp_path: Path):
    with pytest.raises(lv.LiveError):
        lv.create_live(tmp_path, "Solaris", [])
    with pytest.raises(lv.LiveError):
        lv.create_live(tmp_path, "solaris", ["a-half"])
    with pytest.raises(lv.LiveError):
        lv.create_live(tmp_path, "solaris", [lv.COMMON])
    with pytest.raises(lv.LiveError):
        lv.create_live(tmp_path, "solaris", ["A", "A"])


def test_add_and_common(tmp_path: Path, lib: tuple[Manifest, Path]):
    m, root = lib
    live = _live(tmp_path)
    lv.add(live, m, ["k/kick.wav", "k/hat.wav"], "A-HALF", root)
    assert {it.folder for it in live.items} == {"A-HALF"}
    lv.add(live, m, ["k/kick.wav"], "B-DNB", root)
    kick = next(it for it in live.items if it.source == "k/kick.wav")
    assert kick.banks == ["A-HALF", "B-DNB"] and kick.folder == lv.COMMON
    assert kick.branch == "DRUMS"
    # retire d'une banque : le kick redescend dans l'autre
    lv.remove(live, ["k/kick.wav"], "A-HALF")
    assert kick.folder == "B-DNB"
    lv.remove(live, ["k/hat.wav"])
    assert [it.source for it in live.items] == ["k/kick.wav"]


def test_set_rumbles_and_banks_drop_them(tmp_path: Path):
    live = _live(tmp_path)
    lv.set_rumbles(live, "A-HALF", ["deep", " gritty ", "deep"])
    assert live.rumbles == {"A-HALF": ["deep", "gritty"]}          # dedoublonne, ordre garde
    for bad in (["Deep"], ["a/b"], [f"p{i}" for i in range(6)]):
        with pytest.raises(lv.LiveError):
            lv.set_rumbles(live, "A-HALF", bad)
    with pytest.raises(lv.LiveError):
        lv.set_rumbles(live, lv.COMMON, ["deep"])
    lv.set_rumbles(live, "B-DNB", ["deep"])
    lv.set_rumbles(live, "A-HALF", [])
    assert live.rumbles == {"B-DNB": ["deep"]}
    lv.set_banks(live, ["A-HALF"])
    assert live.rumbles == {}


def test_render_item_and_add_item(tmp_path: Path, lib: tuple[Manifest, Path]):
    _m, root = lib
    live = _live(tmp_path)
    item = lv.render_item("SoundDesign/rumble/r.wav", "RM", "RM F Hard 01 k", root, "k/kick.wav", "deep")
    assert (item.branch, item.parent, item.rumble, item.ram) == ("DRUMS", "k/kick.wav", "deep", 192_000)
    assert lv.add_item(live, item, "A-HALF") == (item, True) and live.items == [item] and item.banks == ["A-HALF"]
    assert lv.add_item(live, item.model_copy(), "A-HALF") == (item, False)   # deja dans la banque
    assert lv.add_item(live, item.model_copy(), "B-DNB") == (item, True) and item.folder == lv.COMMON
    # accordage herite du kick : note affichee, decalage, RAM au varispeed
    kick = lv.LiveItem(source="k/kick.wav", code="BD", branch="DRUMS", name="BD G Hard 01 k",
                       banks=["A-HALF"], note="F", shift=2)
    assert lv.untuned_name(kick) == "BD F Hard 01 k"
    lv.inherit_tuning(item, kick, root)
    assert (item.name, item.note, item.shift) == ("RM G Hard 01 k", "F", 2) and item.ram and item.ram < 192_000
    with pytest.raises(lv.LiveError):                                # branche SAMPLE : hors live
        lv.render_item("x.wav", "RS", "RS x", root, None)


def test_add_keeps_parent_of_a_render(tmp_path: Path, lib: tuple[Manifest, Path]):
    # un rumble verse garde la cle de son kick (8.L1) ; un sample ordinaire n'en a pas
    m, root = lib
    live = _live(tmp_path)
    lv.add(live, m, ["k/kick.wav", "SoundDesign/rumble/r.wav"], "A-HALF", root)
    by = {it.source: it for it in live.items}
    assert by["SoundDesign/rumble/r.wav"].parent == "k/kick.wav"
    assert by["k/kick.wav"].parent is None


def test_add_reserve_sample_and_live_pack(tmp_path: Path, lib: tuple[Manifest, Path]):
    m, root = lib
    live = _live(tmp_path)
    lv.add(live, m, ["d/drone C.wav", "me/rec.wav"], "A-HALF", root)
    drone, rec = live.items
    assert drone.branch == "TONAL" and drone.name.startswith("PD C ") and drone.name.endswith(" drn")
    assert rec.branch == "LOOPS" and rec.name == "BL 168 AcidG1 slr"   # pack du live
    assert len(drone.name) <= 18


def test_add_refuses_unusable(tmp_path: Path, lib: tuple[Manifest, Path]):
    m, root = lib
    live = _live(tmp_path)
    for src, bank in (("x/loose.wav", "A-HALF"), ("k/rs.wav", "A-HALF"), ("k/kick.wav", "Z")):
        with pytest.raises(lv.LiveError):
            lv.add(live, m, [src], bank, root)
    # tout ou rien : un sample refuse n'ajoute pas les autres
    with pytest.raises(lv.LiveError):
        lv.add(live, m, ["k/kick.wav", "x/loose.wav"], "A-HALF", root)
    assert live.items == []


def test_set_banks_drops_removed(tmp_path: Path, lib: tuple[Manifest, Path]):
    m, root = lib
    live = _live(tmp_path)
    lv.add(live, m, ["k/kick.wav"], "A-HALF", root)
    lv.add(live, m, ["k/kick.wav", "k/hat.wav"], "B-DNB", root)
    lv.set_banks(live, ["A-HALF"])
    assert [(it.source, it.banks) for it in live.items] == [("k/kick.wav", ["A-HALF"])]


def test_set_key_and_banks_drop_it(tmp_path: Path):
    live = _live(tmp_path)
    lv.set_key(live, "A-HALF", "  Fa   m ")
    lv.set_key(live, "B-DNB", "Sol m")
    lv.set_key(live, lv.COMMON, "Fa m")
    assert live.keys == {"A-HALF": "Fa m", "B-DNB": "Sol m", lv.COMMON: "Fa m"}
    lv.set_key(live, "B-DNB", "")
    assert "B-DNB" not in live.keys
    with pytest.raises(lv.LiveError):
        lv.set_key(live, "Z-NONE", "La m")
    with pytest.raises(lv.LiveError):
        lv.set_key(live, "A-HALF", "x" * (lv.KEY_MAX + 1))
    lv.set_banks(live, ["B-DNB"])
    assert live.keys == {lv.COMMON: "Fa m"}


def test_set_tempo_and_banks_drop_it(tmp_path: Path):
    live = _live(tmp_path)
    lv.set_tempo(live, "A-HALF", 165.04)
    lv.set_tempo(live, "B-DNB", 172)
    assert live.tempos == {"A-HALF": 165.0, "B-DNB": 172.0}
    lv.set_tempo(live, "B-DNB", None)
    assert "B-DNB" not in live.tempos
    with pytest.raises(lv.LiveError):
        lv.set_tempo(live, "A-HALF", 400)
    with pytest.raises(lv.LiveError):
        lv.set_tempo(live, "Z-NONE", 170)
    lv.set_banks(live, ["B-DNB"])
    assert live.tempos == {}


def test_ram_at_dt2_format(tmp_path: Path):
    _wav(tmp_path / "a.wav", 1.0, sr=44_100, channels=2)
    assert lv.ram_bytes(tmp_path / "a.wav") == 48_000 * 2 * 2   # 48 kHz / 16 bits, stereo
    (tmp_path / "bad.wav").write_bytes(b"RIFF")
    assert lv.ram_bytes(tmp_path / "bad.wav") is None


def test_summary_cap_and_ram(tmp_path: Path, lib: tuple[Manifest, Path]):
    m, root = lib
    live = _live(tmp_path)
    lv.add(live, m, ["k/kick.wav", "k/hat.wav"], "A-HALF", root)
    s = lv.summary(live)
    assert [(f.path, f.files) for f in s.folders] == [("A-HALF/DRUMS", 2)]
    assert s.ram == 2 * 48_000 * 2 * 2 and s.unknown_ram == 0
    live.items = live.items * (lv.LIVE_CAP // 2 + 1)
    assert lv.summary(live).folders[0].over_cap


def test_rename_and_unique_names(tmp_path: Path, lib: tuple[Manifest, Path]):
    m, root = lib
    live = _live(tmp_path)
    lv.add(live, m, ["k/kick.wav", "k/hat.wav"], "A-HALF", root)
    with pytest.raises(lv.LiveError):
        lv.rename(live, "k/kick.wav", "x" * 19)
    lv.rename(live, "k/hat.wav", "bd f hard 01 k")     # meme nom, casse differente
    assert sorted(lv.plan(live)) == ["A-HALF/DRUMS/BD F Hard 01 k.wav", "A-HALF/DRUMS/bd f hard 01 2 k.wav"]


def test_save_load_and_export(tmp_path: Path, lib: tuple[Manifest, Path]):
    m, root = lib
    meta, dest = tmp_path / "lives", tmp_path / "00-live"
    live = _live(tmp_path)
    lv.add(live, m, ["k/kick.wav", "d/drone C.wav"], "A-HALF", root)
    lv.save_live(live, meta)
    assert lv.list_lives(meta) == ["solaris"]
    live = lv.load_live(meta, "solaris")
    r = lv.export_live(live, root, dest, meta)
    assert sorted(r.copied) == ["A-HALF/DRUMS/BD F Hard 01 k.wav", "A-HALF/TONAL/PD C Drone drn.wav"]
    assert (dest / "solaris" / "A-HALF" / "DRUMS" / "BD F Hard 01 k.wav").is_file()
    assert lv.list_lives(meta) == ["solaris"]          # l'index d'export n'est pas un live
    # rejouable : le kick passe dans 0-COMMON, l'ancien fichier est retire
    lv.add(live, m, ["k/kick.wav"], "B-DNB", root)
    r = lv.export_live(live, root, dest, meta)
    assert r.copied == ["0-COMMON/DRUMS/BD F Hard 01 k.wav"] and r.unchanged == 1
    assert r.removed == ["A-HALF/DRUMS/BD F Hard 01 k.wav"]
    assert not (dest / "solaris" / "A-HALF" / "DRUMS").exists()
    with pytest.raises(lv.LiveError):
        lv.load_live(meta, "inconnu")


@pytest.mark.parametrize(("key", "root"), [
    ("Fa m", "F"), ("sol mineur", "G"), ("Si bémol", "A#"), ("si b", "A#"), ("Ré", "D"),
    ("fa dièse", "F#"), ("F#m", "F#"), ("Bb", "A#"), ("Dm", "D"), ("E", "E"), ("xx", None),
])
def test_key_root(key: str, root: str | None):
    assert lv.key_root(key) == root


def test_semitones_shortest_path():
    assert lv.semitones("D#", "F") == 2
    assert lv.semitones("A", "F") == -4
    assert lv.semitones("C", "F#") == -6          # egalite : on descend
    assert lv.semitones("F", "F") == 0


def test_tune_bank(tmp_path: Path, lib: tuple[Manifest, Path]):
    m, root = lib
    m.entries[0].note = "F"                        # kick en fa
    live = _live(tmp_path)
    lv.add(live, m, ["k/kick.wav", "k/hat.wav"], "A-HALF", root)
    kick = next(it for it in live.items if it.source == "k/kick.wav")
    ram = kick.ram
    with pytest.raises(lv.LiveError):              # pas de tonalite
        lv.tune_bank(live, m, "A-HALF", root)
    lv.set_key(live, "A-HALF", "Sol m")
    touched = lv.tune_bank(live, m, "A-HALF", root)
    assert [it.source for it in touched] == ["k/kick.wav"]      # le hat n'est pas accorde
    assert (kick.note, kick.shift, kick.name) == ("F", 2, "BD G Hard 01 k")
    assert ram is not None and kick.ram is not None and kick.ram < ram   # plus court en montant
    lv.set_key(live, "A-HALF", "Mi")
    lv.tune_bank(live, m, "A-HALF", root)
    assert (kick.shift, kick.name) == (-1, "BD E Hard 01 k")
    lv.tune_bank(live, m, "A-HALF", root, reset=True)
    assert (kick.shift, kick.name, kick.ram) == (0, "BD F Hard 01 k", ram)
    lv.set_key(live, "A-HALF", "??")
    with pytest.raises(lv.LiveError):
        lv.tune_bank(live, m, "A-HALF", root)


def test_export_tuned(tmp_path: Path, lib: tuple[Manifest, Path]):
    m, root = lib
    m.entries[0].note = "F"
    meta, dest = tmp_path / "lives", tmp_path / "00-live"
    live = _live(tmp_path)
    lv.add(live, m, ["k/kick.wav"], "A-HALF", root)
    lv.set_key(live, "A-HALF", "Fa")
    lv.export_live(live, root, dest, meta)
    out = dest / "solaris" / "A-HALF" / "DRUMS"
    lv.set_key(live, "A-HALF", "La")               # +4 demi-tons
    lv.tune_bank(live, m, "A-HALF", root)
    r = lv.export_live(live, root, dest, meta)
    assert r.copied == ["A-HALF/DRUMS/BD A Hard 01 k.wav"] and r.removed == ["A-HALF/DRUMS/BD F Hard 01 k.wav"]
    info = sf.info(str(out / "BD A Hard 01 k.wav"))
    assert info.samplerate == 44_100 and info.subtype == "PCM_24" and info.channels == 2
    assert info.frames == pytest.approx(44_100 / 2 ** (4 / 12), abs=2)
    r = lv.export_live(live, root, dest, meta)     # rejouable : rien a reecrire
    assert r.copied == [] and r.unchanged == 1


def test_renote_inserts_and_removes():
    assert lv._renote("BD Kick 03 rth", "A", "F") == "BD F Kick 03 rth"
    assert lv._renote("BD F Kick 03 rth", "F", None) == "BD Kick 03 rth"
    assert lv._renote("RM 168 Bb Sub me", "A#", "C") == "RM 168 C Sub me"
    assert lv._renote("BD Rounded Thing 07 rth", "C#", "F") == "BD F Rounde 07 rth"   # 18 caracteres


def test_tune_measures_missing_note(tmp_path: Path, lib: tuple[Manifest, Path],
                                    monkeypatch: pytest.MonkeyPatch):
    m, root = lib
    m.entries[0].name = "BD Hard 01 k"           # ni note au manifeste ni dans le nom
    monkeypatch.setattr(lv, "measure_note", lambda path, code: ("A", 55.0))
    live = _live(tmp_path)
    lv.add(live, m, ["k/kick.wav"], "A-HALF", root)
    lv.set_key(live, "A-HALF", "Fa m")
    lv.tune_bank(live, m, "A-HALF", root)
    kick = live.items[0]
    assert (kick.note, kick.shift, kick.name) == ("A", -4, "BD F Hard 01 k")
    lv.tune_bank(live, m, "A-HALF", root, reset=True)
    assert (kick.shift, kick.name) == (0, "BD Hard 01 k")


def test_tune_live_all_banks(tmp_path: Path, lib: tuple[Manifest, Path]):
    m, root = lib
    m.entries[0].note = "F"
    m.reserve[0].source = "d/drone C.wav"          # PD en C (nom du fichier)
    live = _live(tmp_path)
    lv.add(live, m, ["k/kick.wav"], "A-HALF", root)
    lv.add(live, m, ["d/drone C.wav"], "B-DNB", root)
    kick, drone = live.items
    lv.set_key(live, "A-HALF", "Sol m")
    lv.set_key(live, "B-DNB", "Ré")
    lv.tune_live(live, m, root)
    assert (kick.shift, drone.shift) == (2, 2)
    lv.set_key(live, "B-DNB", "")                  # banque sans tonalite : hauteur d'origine
    lv.tune_live(live, m, root)
    assert (kick.shift, drone.shift) == (2, 0)
    lv.set_key(live, "B-DNB", "??")                # tout ou rien
    with pytest.raises(lv.LiveError):
        lv.tune_live(live, m, root)
    assert kick.shift == 2
    lv.tune_live(live, m, root, reset=True)
    assert (kick.shift, drone.shift) == (0, 0)

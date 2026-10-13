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
    for rel in ("k/kick.wav", "k/hat.wav", "d/drone C.wav", "me/rec.wav"):
        _wav(root / rel, 1.0)
    entries = [
        SampleEntry(source="k/kick.wav", family="TRIBE", code="BD", pack="k",
                    name="BD F Hard 01 k", duration=1.0, rank=1),
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

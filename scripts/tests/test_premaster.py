"""Tests de premaster.py : codes, noms, import rejouable."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from analyzer.line import CEILING_DB
from premaster import apply, code_of, import_name, plan, run_import

SR = 44100


def write(path: Path, hz: float, amp: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    t = np.arange(SR // 4) / SR
    sf.write(path, amp * np.sin(2 * np.pi * hz * t) * np.exp(-t * 20), SR, subtype="PCM_16")


@pytest.mark.parametrize(("rel", "code"), [
    ("Kick/909 Kick Hi 2.flac", "BD"), ("Hat/808 Hat Open 01.flac", "OH"),
    ("Hat/808 Hat Closed 01.flac", "HH"), ("Conga/LM2 Conga Low.flac", "PC"),
    ("Rim/909 Rim.flac", "PC"), ("Other/x.flac", None), ("x.flac", None),
])
def test_code_of(rel: str, code: str | None) -> None:
    assert code_of(Path(rel)) == code


def test_import_name_keeps_machine_and_fits() -> None:
    assert import_name(Path("Snare/808 Snare C 01.flac"), "SD", "sr2") == "SD 808 C 01 sr2"
    assert len(import_name(Path("Tom/LM2 Tom Eprom Mid.flac"), "TM", "sr2")) <= 18


def test_plan_names_unique(tmp_path: Path) -> None:
    for n in ("Kerope Crash.flac", "Kerope Crash 2.flac"):
        write(tmp_path / "Cymbal" / n, 3000, 0.3)
    dests = [d for _, _, d in plan(tmp_path, "sr2")]
    assert len(set(dests)) == 2


def test_run_import_writes_48k_24bit_and_is_rerunnable(tmp_path: Path) -> None:
    src, dest = tmp_path / "src", tmp_path / "dest"
    ref = tmp_path / "ref.wav"
    write(ref, 55, 0.48)
    write(src / "Kick" / "Kick A.flac", 60, 0.9)
    write(src / "Clap" / "Clap B.flac", 1500, 0.05)
    rows = run_import(src, dest, ref, "sr2")
    assert {r.code for r in rows} == {"BD", "CP"}
    for r in rows:
        info = sf.info(dest / r.dest)
        assert (info.samplerate, info.subtype) == (48000, "PCM_24")
        assert r.peak_db <= CEILING_DB + 0.01
    first = (dest / rows[0].dest).read_bytes()
    run_import(src, dest, ref, "sr2")
    assert (dest / rows[0].dest).read_bytes() == first
    assert (dest / "_import.tsv").read_text().count("\n") == 3


def test_apply_moves_backs_up_and_is_rerunnable(tmp_path: Path) -> None:
    root = tmp_path / "solaris"
    ref = tmp_path / "ref.wav"
    write(ref, 55, 0.48)
    src = root / "14 BASS LOOP" / "BL 145 Deep 1 slr.wav"
    write(src, 800, 0.99)
    rows = apply(root, ref, "ML", [src], day="2026-11-13")
    out = root / "18 MELO LOOP" / "ML 145 Deep 1 slr.wav"
    assert rows[0].dest == "18 MELO LOOP/ML 145 Deep 1 slr.wav"
    assert out.exists() and not src.exists()
    assert (root / "_backup" / "2026-11-13" / "14 BASS LOOP" / "BL 145 Deep 1 slr.wav").exists()
    first = out.read_bytes()
    apply(root, ref, "ML", [src], day="2026-11-13")   # rejoue depuis l'original sauvegarde
    assert out.read_bytes() == first

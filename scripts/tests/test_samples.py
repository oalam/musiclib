"""Tests unitaires de samples.py (catalogue + dedoublonnage + copie).

Tout tourne sur tmp_path avec des wav synthetiques, aucun disque externe.

Lancer (depuis scripts/) :
    python -m pytest tests/test_samples.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf

import samples


def _wav(path: Path, seed: int, subtype: str = "PCM_24", frames: int = 4410) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    sf.write(path, rng.uniform(-0.5, 0.5, (frames, 2)), 44100, subtype=subtype)
    return path


def test_category_ni_retire_prefixe_samples():
    assert samples.category_of(Path("Samples/Drums/Kick/K1.wav")) == "Drums/Kick"
    assert samples.category_of(Path("Samples/Loops/Percussion/Djembe/x.wav")) == "Loops/Percussion"


def test_category_dossier_simple_et_racine():
    assert samples.category_of(Path("HauntedFX09/x.wav")) == "HauntedFX09"
    assert samples.category_of(Path("x.wav")) == "-"


def test_dedupe_contenu_identique_entetes_differents(tmp_path):
    a = _wav(tmp_path / "m2" / "Samples/Drums/Kick/K.wav", seed=1, subtype="PCM_24")
    # meme audio reecrit en float : octets differents, PCM identique a l'arrondi pres
    data, sr = sf.read(a, dtype="int32")
    b = tmp_path / "m1" / "Samples/Drums/Kick/K.wav"
    b.parent.mkdir(parents=True)
    sf.write(b, data, sr, subtype="PCM_32")
    other = _wav(tmp_path / "m1" / "Samples/Drums/Snare/S.wav", seed=2)

    rows = [samples.probe(p, tmp_path / r) for p, r in ((a, "m2"), (b, "m1"), (other, "m1"))]
    uniques, dups = samples.dedupe([r for r in rows if r])

    assert [u.source for u in uniques] == ["m2", "m1"]
    assert uniques[0].duplicates == 1
    assert len(dups) == 1 and dups[0].duplicate_of == str(a)


def test_scan_ecrit_catalogue_et_doublons(tmp_path):
    root = tmp_path / "lib"
    _wav(root / "Samples/Drums/Kick/K1.wav", seed=1)
    _wav(root / "Samples/Drums/Kick/K1 copy.wav", seed=1)
    _wav(root / "Samples/Drums/Hihat/H.wav", seed=3)
    out = tmp_path / "cat.csv"

    assert samples.main(["scan", str(root), "--out", str(out)]) == 0
    assert len(samples.read_csv(out)) == 2
    assert len(samples.read_csv(out.with_suffix(".duplicates.csv"))) == 1


def test_select_filtres():
    base = dict(duration_s=1.0, samplerate=44100, channels=2, subtype="PCM_24", size_kb=1)
    rows = [
        samples.Sample(source="Maschine 2 Library", category="Drums/Kick", name="Kick A.wav", path="a", **base),
        samples.Sample(source="Maschine 2 Library", category="Loops/Synth", name="Loop.wav", path="b", keep="x",
                       **{**base, "duration_s": 8.0}),
    ]
    assert [r.path for r in samples.select(rows, category="drums/*")] == ["a"]
    assert [r.path for r in samples.select(rows, max_duration=2)] == ["a"]
    assert [r.path for r in samples.select(rows, marked=True)] == ["b"]
    assert [r.path for r in samples.select(rows, source="maschine 2", name="kick*")] == ["a"]


def test_copy_idempotent(tmp_path):
    src = _wav(tmp_path / "src" / "K.wav", seed=1)
    row = samples.probe(src, tmp_path / "src")
    assert row is not None
    dest = tmp_path / "dest"

    assert samples.copy_samples([row], dest) == (1, 0)
    assert (dest / "src" / "K.wav").exists()
    assert samples.copy_samples([row], dest) == (0, 1)


def test_copy_catalogue_absent(tmp_path, capsys):
    rc = samples.main(["copy", str(tmp_path / "nope.csv"), "--dest", str(tmp_path)])
    assert rc == 1
    assert "introuvable" in capsys.readouterr().err


def test_target_garde_arborescence_complete(tmp_path):
    base = dict(category="x", name="Shaker1.WAV", duration_s=1.0, samplerate=44100,
                channels=1, subtype="PCM_16", size_kb=1)
    a = samples.Sample(source="Battery 3 Library",
                       path="/v/Battery 3 Library/Demo/Dragon Kit/Shaker1.WAV", **base)
    b = samples.Sample(source="Maschine 2 Library",
                       path="/v/Maschine 2 Library/Samples/Loops/Percussion/Djembe/D.wav", **base)
    dest = tmp_path / "d"
    assert samples.target_of(a, dest) == dest / "Battery 3 Library/Demo/Dragon Kit/Shaker1.WAV"
    assert samples.target_of(b, dest) == dest / "Maschine 2 Library/Loops/Percussion/Djembe/D.wav"

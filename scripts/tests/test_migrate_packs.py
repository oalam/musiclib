"""Migration des chemins vers <MEDIA>/Samples/packs/ (migrate_packs.py)."""
from __future__ import annotations

import json
from pathlib import Path

import migrate_packs as mp
from analyzer import samples as smp


def _disk(tmp_path: Path) -> Path:
    root = tmp_path / "Samples"
    for rel in ("packs/909/a/bd.wav", "packs/Grey Forge/k.wav", "recorded/x.wav"):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes(b"x")
    return root


def test_fix_prefixes_only_moved_paths(tmp_path: Path) -> None:
    fix = mp.make_fix(_disk(tmp_path))
    assert fix("909/a/bd.wav") == "packs/909/a/bd.wav"
    assert fix("909/") == "packs/909/"                      # cle de dossier
    assert fix("packs/909/a/bd.wav") == "packs/909/a/bd.wav"   # rejouable
    assert fix("recorded/x.wav") == "recorded/x.wav"         # reste a la racine
    assert fix("SoundDesign/v/x.wav") == "SoundDesign/v/x.wav"  # introuvable : intact


def test_run_rewrites_vault_files_and_is_rerunnable(tmp_path: Path) -> None:
    root = _disk(tmp_path)
    meta, lives = tmp_path / "meta", tmp_path / "lives"
    meta.mkdir()
    lives.mkdir()
    (meta / "manifest.json").write_text(json.dumps({
        "entries": [{"source": "909/a/bd.wav", "parent": None}],
        "reserve": [{"source": "Grey Forge/k.wav"}], "unclassified": ["recorded/x.wav"],
        "trashed": ["909/a/bd.wav"]}))
    (meta / "overrides.json").write_text(json.dumps({"909/": {"tags": ["techno"]},
                                                     "x/r.wav": {"parent": "909/a/bd.wav"}}))
    (lives / "solaris.json").write_text(json.dumps({"items": [{"source": "Grey Forge/k.wav"}]}))
    (lives / "solaris.export.json").write_text(json.dumps({"A/k.wav": {"source": "Grey Forge/k.wav"}}))
    report = mp.run(root, meta, lives, dry_run=False)
    assert sorted(report.values()) == [1, 1, 2, 3]
    m = json.loads((meta / "manifest.json").read_text())
    assert m["entries"][0]["source"] == "packs/909/a/bd.wav" and m["trashed"] == ["packs/909/a/bd.wav"]
    o = json.loads((meta / "overrides.json").read_text())
    assert list(o) == ["packs/909/", "x/r.wav"] and o["x/r.wav"]["parent"] == "packs/909/a/bd.wav"
    assert (meta / "manifest.json.bak").is_file()
    assert set(mp.run(root, meta, lives, dry_run=False).values()) == {0}


def test_rules_read_the_logical_path() -> None:
    """Les regles de classement ignorent le dossier de rangement packs/."""
    for old in ("Native instrument/arcane/one shot/Drums/Kick/Kick Airburst 1.wav",
                "909/BPB Cassette 909/cassette 1/bd01.wav"):
        new = "packs/" + old
        assert smp.logical(new) == old
        assert (smp.family_of(new), smp.pack_of(new), smp.kit_of(new)) == \
            (smp.family_of(old), smp.pack_of(old), smp.kit_of(old))
        assert smp.code_of(new, 0.3) == smp.code_of(old, 0.3)
        assert smp.short_name(new, "BD", smp.pack_of(new)) == smp.short_name(old, "BD", smp.pack_of(old))
        assert smp.in_kit(new, smp.kit_of(old))

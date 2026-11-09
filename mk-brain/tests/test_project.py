from __future__ import annotations

import json
from pathlib import Path

import pytest

from mk_brain.project import Project, ProjectError, load_project

SOLARIS_JSON = Path(__file__).resolve().parents[2] / "library" / "lives" / "solaris.json"
JSON_MODES = {"m": "eolien", "phrg": "phrygien"}


def test_solaris_banks(project: Project) -> None:
    assert [k[0] for k in project.banks] == list("ABCDEF")
    key, bank = project.bank(4) or ("", None)
    assert key == "E-TRIBE" and bank is not None
    assert (bank.tonique, bank.tonic, bank.mode) == ("A#", 10, "phrygien")
    assert project.phrase(bank) == 32  # defaults
    assert project.bank(6) is None  # G-JOKER pas encore dans le projet


@pytest.mark.skipif(not SOLARIS_JSON.exists(), reason="library/lives/solaris.json absent")
def test_solaris_matches_live_json(project: Project) -> None:
    """Doublon assumé jusqu'à `convert` (slice 6) : tonalités et tempos identiques au JSON."""
    live = json.loads(SOLARIS_JSON.read_text(encoding="utf-8"))
    for key, bank in project.banks.items():
        tonic, mode = live["keys"][key].split()
        assert (bank.tonique, bank.mode) == (tonic, JSON_MODES[mode]), key
        assert bank.tempo == live["tempos"][key], key


BANK = {"title": "T", "desc": "D", "tempo": 160, "tonique": "F", "mode": "eolien"}


def _load(tmp_path: Path, banks: dict[str, object], **extra: object) -> Project:
    path = tmp_path / "p.yaml"
    path.write_text(json.dumps({"name": "x", "banks": banks, **extra}), encoding="utf-8")
    return load_project(path)


def test_flat_tonic_and_bank_phrase(tmp_path: Path) -> None:
    p = _load(tmp_path, {"C-X": {**BANK, "tonique": "Bb", "phrase": 64}})
    bank = p.banks["C-X"]
    assert (bank.tonique, p.phrase(bank)) == ("A#", 64)


@pytest.mark.parametrize(
    "banks",
    [
        {"A-X": {**BANK, "tonique": "H"}},  # tonique illisible
        {"A-X": {**BANK, "mode": "lydien"}},  # mode inconnu
        {"A-X": {**BANK, "paliers": 2}},  # clé inconnue
        {"A-X": {k: v for k, v in BANK.items() if k != "desc"}},  # champ obligatoire
        {"I-X": BANK},  # lettre hors A-H
        {"A-X": BANK, "A-Y": BANK},  # deux clés pour A
    ],
)
def test_invalid_project_raises(tmp_path: Path, banks: dict[str, object]) -> None:
    with pytest.raises(ProjectError):
        _load(tmp_path, banks)


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(ProjectError):
        load_project(tmp_path / "absent.yaml")

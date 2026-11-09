from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from mk_brain.convert import convert, dump, write_project
from mk_brain.project import DEFAULT_PROJECT, ProjectError, load_project

VAULT = Path(__file__).resolve().parents[2]
SOLARIS_DOCTRINE = VAULT / "digitakt" / "doctrine-dt2-solaris.md"

FRONT = """---
tags: [live]
mkbrain:
  live: library/lives/x.json
  defaults: {{phrase: 64}}
  banks:
    A-HALF:
      title: Half
      desc: Ouverture
      tempo: 160
      tonique: F
      mode: eolien
    E-TRIBE:
      title: Tribe
      desc: Cœur
      tempo: 162
      tonique: {tonique}
      mode: phrygien{extra}
---

# Doctrine
"""

LIVE: dict[str, Any] = {
    "name": "x",
    "banks": ["A-HALF", "E-TRIBE", "G-JOKER"],
    "keys": {"A-HALF": "F m", "E-TRIBE": "A# phrg"},
    "tempos": {"A-HALF": 160, "E-TRIBE": 162, "0-KIT": 165.0},
}


def _vault(tmp_path: Path, tonique: str = "Bb", extra: str = "", **live: Any) -> Path:
    """Vault minimal : digitakt/doctrine-dt2-x.md + library/lives/x.json."""
    (tmp_path / "digitakt").mkdir()
    (tmp_path / "library" / "lives").mkdir(parents=True)
    (tmp_path / "library" / "lives" / "x.json").write_text(
        json.dumps({**LIVE, **live}), encoding="utf-8"
    )
    doctrine = tmp_path / "digitakt" / "doctrine-dt2-x.md"
    doctrine.write_text(FRONT.format(tonique=tonique, extra=extra), encoding="utf-8")
    return doctrine


def test_convert_flattens_front_matter(tmp_path: Path) -> None:
    p = convert(_vault(tmp_path))
    assert (p.name, p.defaults.phrase, list(p.banks)) == ("x", 64, ["A-HALF", "E-TRIBE"])
    assert p.banks["E-TRIBE"].tonique == "A#"  # Bb normalisé, recoupé avec « A# phrg »


def test_write_project_is_replayable(tmp_path: Path) -> None:
    doctrine = _vault(tmp_path)
    out_dir = tmp_path / "projects"
    out_dir.mkdir()
    out = write_project(doctrine, out_dir)
    first = out.read_text(encoding="utf-8")
    assert write_project(doctrine, out_dir).read_text(encoding="utf-8") == first
    assert first.startswith("# GÉNÉRÉ par `mk-brain convert digitakt/doctrine-dt2-x.md`")
    assert load_project(out).banks["A-HALF"].tempo == 160


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"tonique": "C"}, "doctrine-dt2-x.md:13 : E-TRIBE en C phrygien"),  # tonalité ≠ JSON
        ({"tempos": {"A-HALF": 158, "E-TRIBE": 162}}, "A-HALF à 160 BPM"),  # tempo ≠ JSON
        ({"banks": ["A-HALF"]}, "banque E-TRIBE absente du JSON"),
        ({"keys": {"A-HALF": "F m", "E-TRIBE": "A# phrg", "G-JOKER": "F m"}}, "sans fiche"),
        ({"keys": {"A-HALF": "F lyd"}}, "illisible"),  # abréviation inconnue
        ({"extra": "\n      paliers: 2"}, "paliers"),  # clé inconnue dans la fiche
        ({"tonique": "H"}, "tonique illisible"),
    ],
)
def test_divergence_raises(tmp_path: Path, kwargs: dict[str, Any], message: str) -> None:
    with pytest.raises(ProjectError, match=message):
        convert(_vault(tmp_path, **kwargs))


def test_missing_front_matter_raises(tmp_path: Path) -> None:
    doctrine = tmp_path / "d.md"
    doctrine.write_text("# Doctrine sans front matter\n", encoding="utf-8")
    with pytest.raises(ProjectError, match="front matter"):
        convert(doctrine)


@pytest.mark.skipif(not SOLARIS_DOCTRINE.exists(), reason="vault absent (Pi)")
def test_solaris_yaml_is_up_to_date() -> None:
    """projects/solaris.yaml commité = sortie de convert sur la doctrine actuelle."""
    expected = dump(
        convert(SOLARIS_DOCTRINE), "digitakt/doctrine-dt2-solaris.md", "library/lives/solaris.json"
    )
    assert DEFAULT_PROJECT.read_text(encoding="utf-8") == expected, (
        "projet périmé : relancer `mk-brain convert digitakt/doctrine-dt2-solaris.md`"
    )

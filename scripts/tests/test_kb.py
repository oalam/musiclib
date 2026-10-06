"""Tests de la base de connaissance Digitakt (scripts/kb.py) et de ses routes API.

Lancer (depuis scripts/) :
    python -m pytest tests/test_kb.py
    python -m pytest tests/test_kb.py::test_search_ignores_accents
"""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import api
import kb

NOTE = """---
tags: [digitakt, kb]
page: 42
---

# Trigs FILL

Chapeau de la note.

## Mode FILL

Maintenir [YES] + [PAGE] active le mode fill. Un trig conditionnel FILL ne
joue que pendant le fill.

## Conditions

```
## pas un titre dans un bloc de code
```
NOT FILL joue hors du fill. Voir aussi le pattern modèle.
"""


@pytest.fixture
def vault(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    kb_dir = tmp_path / "digitakt" / "kb"
    kb_dir.mkdir(parents=True)
    (kb_dir / "fill.md").write_text(NOTE, encoding="utf-8")
    (tmp_path / "digitakt" / "doctrine.md").write_text(
        "# Doctrine\n\n## Mutes\n\nLe mute est le vrai sequenceur.\n", encoding="utf-8")
    (tmp_path / "secret.md").write_text("# hors corpus\n", encoding="utf-8")
    monkeypatch.setattr(kb, "VAULT_ROOT", tmp_path)
    monkeypatch.setattr(kb, "KB_DIR", kb_dir)
    monkeypatch.setattr(kb, "DOCTRINE", tmp_path / "digitakt" / "doctrine.md")
    return tmp_path


def test_split_sections_by_headings():
    secs = kb.split_sections(NOTE, "digitakt/kb/fill.md")
    assert [s.heading for s in secs] == ["", "Mode FILL", "Conditions"]
    assert {s.title for s in secs} == {"Trigs FILL"}
    assert secs[1].anchor == "mode-fill"
    assert "pas un titre" in secs[2].body  # titre dans un bloc de code ignore
    assert "page: 42" not in secs[0].body


def test_search_requires_all_terms_and_ranks_heading(vault: Path):
    hits = kb.search("fill trig", kb.load_corpus())
    assert hits[0].heading == "Mode FILL"
    assert all(h.path == "digitakt/kb/fill.md" for h in hits)
    assert kb.search("fill sequenceur", kb.load_corpus()) == []


def test_search_ignores_accents(vault: Path):
    hits = kb.search("modele", kb.load_corpus())
    assert [h.heading for h in hits] == ["Conditions"]
    assert "modèle" in hits[0].snippet


def test_corpus_includes_doctrine(vault: Path):
    hits = kb.search("SÉQUENCEUR", kb.load_corpus())
    assert hits and hits[0].path == "digitakt/doctrine.md" and hits[0].anchor == "mutes"


def test_api_search_and_note(vault: Path):
    client = TestClient(api.create_app())
    res = client.get("/api/kb/search", params={"q": "fill"})
    assert res.status_code == 200 and res.json()[0]["path"] == "digitakt/kb/fill.md"
    note = client.get("/api/kb/note", params={"path": "digitakt/kb/fill.md"}).json()
    assert note["title"] == "Trigs FILL" and not note["markdown"].startswith("---")


def test_api_note_refuses_path_outside_corpus(vault: Path):
    client = TestClient(api.create_app())
    for path in ("secret.md", "../secret.md", "digitakt/kb/../../secret.md"):
        assert client.get("/api/kb/note", params={"path": path}).status_code == 404

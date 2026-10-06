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
lot: 2
ordre: 7
theme: FILL et conditions
manuel: "§10.8.4, §12.6-12.9 (p49)"
statut: draft
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
NOT FILL joue hors du fill. Voir aussi le pattern modèle (§17, §99.9).
"""

OUTLINE = {
    "10.8.4": kb.ManualRef(section="10.8.4", title="FILL MODE", page=49),
    "12.6": kb.ManualRef(section="12.6", title="COMPRESSOR", page=65),
    "12.9": kb.ManualRef(section="12.9", title="EXTERNAL", page=67),
    "17": kb.ManualRef(section="17", title="KEY COMBINATIONS", page=88),
}


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
    (kb_dir / "_index.md").write_text("# Hub\n\n## Lot 2 — Remplir les patterns\n", encoding="utf-8")
    monkeypatch.setattr(kb, "KB_INDEX", kb_dir / "_index.md")
    monkeypatch.setattr(kb, "MANUAL_PDF", tmp_path / "refs" / "manuel.pdf")
    monkeypatch.setattr(kb, "manual_outline", lambda: OUTLINE)
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


def test_api_manual_outline(vault: Path):
    client = TestClient(api.create_app())
    res = client.get("/api/manual/outline")
    assert res.status_code == 200 and res.json()["12.6"] == {
        "section": "12.6", "title": "COMPRESSOR", "page": 65}


def test_parse_frontmatter():
    fm = kb.parse_frontmatter(NOTE)
    assert fm["manuel"] == "§10.8.4, §12.6-12.9 (p49)" and fm["lot"] == "2"
    assert kb.parse_frontmatter("# sans frontmatter\n") == {}


def test_manual_refs_resolves_ranges_and_skips_unknown():
    refs = kb.manual_refs("§10.8.4, §12.6-12.9 et §10.8.4 encore, §99.9", OUTLINE)
    assert [(r.section, r.page) for r in refs] == [("10.8.4", 49), ("12.6", 65), ("12.9", 67)]


def test_manual_refs_skips_doctrine_sections():
    text = "voir la doctrine §17 puis §10.8.4 ; cf. §17 et §10.8.4"
    assert [r.section for r in kb.manual_refs(text, OUTLINE)] == ["10.8.4", "17"]
    assert [r.section for r in kb.manual_refs("cf. §17 et §10.8.4", OUTLINE, in_doctrine=True)] == ["10.8.4"]


def test_read_note_includes_manual_refs(vault: Path):
    note = kb.read_note("digitakt/kb/fill.md")
    assert note is not None
    assert [r.section for r in note.manual] == ["10.8.4", "12.6", "12.9"]
    assert set(note.manual_index) == {"10.8.4", "12.6", "12.9", "17"}  # §17 cite dans le texte


def test_table_of_contents_groups_by_lot(vault: Path):
    toc = kb.table_of_contents()
    assert [(lot.number, lot.name) for lot in toc] == [(2, "Remplir les patterns")]
    assert toc[0].notes[0].model_dump() == {
        "path": "digitakt/kb/fill.md", "title": "FILL et conditions", "ordre": 7, "statut": "draft"}


def test_outline_from_pdf(tmp_path: Path):
    from pypdf import PdfWriter

    writer = PdfWriter()
    for _ in range(3):
        writer.add_blank_page(width=100, height=100)
    parent = writer.add_outline_item("10. THE SEQUENCER", 1)
    writer.add_outline_item("10.8.6 TEMPORARY SAVE", 2, parent=parent)
    writer.add_outline_item("Introduction", 0)
    pdf = tmp_path / "m.pdf"
    with pdf.open("wb") as fh:
        writer.write(fh)
    outline = kb.outline_from_pdf(pdf)
    assert {k: (r.title, r.page) for k, r in outline.items()} == {
        "10": ("THE SEQUENCER", 2), "10.8.6": ("TEMPORARY SAVE", 3)}


def test_api_toc_and_manual(vault: Path):
    client = TestClient(api.create_app())
    assert client.get("/api/kb/toc").json()[0]["notes"][0]["path"] == "digitakt/kb/fill.md"
    assert client.get("/api/manual").status_code == 404
    (vault / "refs").mkdir()
    (vault / "refs" / "manuel.pdf").write_bytes(b"%PDF-1.4 fake")
    res = client.get("/api/manual")
    assert res.status_code == 200 and res.headers["content-type"] == "application/pdf"

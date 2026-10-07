"""Tests du decoupage search / ingest de grab.py (Phase 7.I).

yt-dlp, le telechargement et librosa sont remplaces par des fakes ; library.md
et le dossier audio vivent dans tmp_path.

Lancer (depuis scripts/) :
    python -m pytest tests/test_grab_search.py
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

import grab
from library_md import parse_library

LIBRARY = """---
count: 0
---

| slug | artist | title | file |
|---|---|---|---|
"""


def _cand(url: str, codec: str, abr: float, match: float = 1.0, **info: Any) -> grab.Candidate:
    fmt = {"acodec": codec, "abr": abr}
    return grab.Candidate(source="youtube", url=url, title=info.get("title", url),
                          info={"formats": [fmt], **info}, fmt=fmt, match=match)


def test_search_trie_par_score(monkeypatch: pytest.MonkeyPatch):
    cands = [_cand("a", "mp4a.40.2", 128), _cand("b", "opus", 160),
             _cand("c", "opus", 251, match=0.2)]
    monkeypatch.setattr(grab, "resolve_candidates", lambda q, search_n: cands)
    assert [c.url for c in grab.search("x")] == ["b", "a", "c"]


def test_candidate_info_serialisable():
    info = grab.candidate_info(_cand("u", "opus", 160.4, match=0.666,
                                     title="T", uploader="Up", duration=245))
    assert info.model_dump() == {
        "source": "youtube", "url": "u", "title": "T", "uploader": "Up",
        "duration_s": 245, "codec": "opus", "abr": 160, "quality": "257",  # 160.4 x 1.6 (opus)
        "match": 0.67, "score": 170.9}


@pytest.fixture
def media(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    mix = tmp_path / "Mix"
    (mix / "audio").mkdir(parents=True)
    lib = tmp_path / "library.md"
    lib.write_text(LIBRARY, encoding="utf-8")
    monkeypatch.setattr(grab, "MIX_DIR", mix)
    monkeypatch.setattr(grab, "AUDIO_DIR", mix / "audio")
    monkeypatch.setattr(grab, "LIBRARY_FILE", lib)
    monkeypatch.setattr(grab, "find_buy_url", lambda info, a, t: None)
    monkeypatch.setattr(grab, "write_tags", lambda *a: None)
    monkeypatch.setattr(grab, "analyze_audio", lambda p, start_bpm: (174.0, "A minor"))

    def fake_download(cand: grab.Candidate, out_stem: Path) -> Path:
        out_stem.parent.mkdir(parents=True, exist_ok=True)
        path = out_stem.with_suffix(".flac")
        path.write_bytes(b"x")
        return path

    monkeypatch.setattr(grab, "download_candidate", fake_download)
    return tmp_path


def test_ingest_url_etapes_et_library(media: Path, monkeypatch: pytest.MonkeyPatch):
    cand = _cand("https://yt/1", "opus", 160, title="Shatta Mad",
                 artist="Limitlezz", genre="Dancehall", duration=200)
    monkeypatch.setattr(grab, "resolve_candidates", lambda q, search_n: [cand])
    steps: list[str] = []
    res = grab.ingest("https://yt/1", grab.IngestOptions(), on_step=steps.append)

    assert steps == ["metadata", "download", "bpm_key", "library"]
    assert res.slug == "limitlezz_-_shatta_mad" and res.created
    assert res.audio_path == media / "Mix/audio/dancehall/limitlezz_-_shatta_mad.flac"
    entry = parse_library(media / "library.md")[res.slug]
    assert entry["bpm"] == "87.0"  # 174 / 2 : genre source Dancehall (85-115)
    assert entry["key"] == "A minor"
    assert "dancehall/limitlezz_-_shatta_mad.flac" in entry["file"]


def test_ingest_fichier_present_saute_le_telechargement(media: Path):
    existing = media / "Mix/audio/limitlezz_-_shatta_mad.flac"
    existing.write_bytes(b"old")
    cand = _cand("https://yt/1", "opus", 160, title="Shatta Mad", artist="Limitlezz")
    steps: list[str] = []
    res = grab.ingest(cand, grab.IngestOptions(), on_step=steps.append)
    assert steps == ["bpm_key", "library"]
    assert res.audio_path == existing and existing.read_bytes() == b"old"


def test_ingest_sans_candidat(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(grab, "resolve_candidates", lambda q, search_n: [])
    with pytest.raises(grab.GrabError):
        grab.ingest("https://yt/none", grab.IngestOptions())


@pytest.mark.parametrize(("info", "artist", "title"), [
    ({"title": "Limitlezz x Maureen - Shatta Mad (Clip Officiel)",
      "creator": "LIMITLEZZ , Maureen"}, "LIMITLEZZ, Maureen", "Shatta Mad"),
    ({"title": "Shatta Mad [Official Audio]", "artist": "Limitlezz"},
     "Limitlezz", "Shatta Mad"),
    ({"title": "Other Guy - Shatta Mad", "artist": "Limitlezz"},
     "Limitlezz", "Other Guy - Shatta Mad"),
])
def test_track_meta_nettoie_le_titre(monkeypatch: pytest.MonkeyPatch,
                                     info: dict[str, Any], artist: str, title: str):
    monkeypatch.setattr(grab, "find_buy_url", lambda info, a, t: None)
    meta = grab.track_meta(_cand("u", "opus", 160, **info), None)
    assert (meta.artist, meta.title) == (artist, title)


def test_download_erreur_lisible(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    import subprocess

    def fail(cmd: list[str], **kw: Any) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(cmd, 1, stderr=(
            "[info] x\nERROR: unable to download video data: HTTP Error 403: Forbidden\n"))

    monkeypatch.setattr(grab.subprocess, "run", fail)
    with pytest.raises(grab.GrabError, match="403.*brew upgrade yt-dlp"):
        grab.download_candidate(_cand("u", "opus", 160), tmp_path / "x")


def test_ingest_corrige_le_bpm_par_le_style(media: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(grab, "analyze_audio", lambda p, start_bpm: (198.8, "C minor"))
    cand = _cand("https://yt/1", "opus", 160, title="Shatta Mad (Clip Officiel)",
                 creator="LIMITLEZZ , Maureen")
    res = grab.ingest(cand, grab.IngestOptions(folder="shatta"))
    assert res.style_bpm == 99.4  # 198.8 / 2, fenetre shatta 85-115
    entry = parse_library(media / "library.md")[res.slug]
    assert entry["bpm"] == "99.4" and entry["genre"] == "shatta"


def test_ingest_sans_style_garde_le_bpm(media: Path):
    cand = _cand("https://yt/1", "opus", 160, title="Untitled", artist="X")
    res = grab.ingest(cand, grab.IngestOptions(folder="mariage"))
    assert res.style_bpm is None
    assert parse_library(media / "library.md")[res.slug]["bpm"] == "174.0"


def test_style_ignore_le_titre(media: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(grab, "analyze_audio", lambda p, start_bpm: (161.5, "A minor"))
    cand = _cand("https://yt/1", "opus", 160, title="Roots", artist="floxytek",
                 tags=["tekno", "free party"])
    res = grab.ingest(cand, grab.IngestOptions())
    assert res.style_bpm == 161.5  # style tekno (tags), pas « roots » du titre

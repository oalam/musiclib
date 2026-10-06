"""Tests de l'API locale du front (scripts/api.py), sur une library factice.

Lancer (depuis scripts/) :
    python -m pytest tests/test_api.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import api

SLUG = "artist_-_title"
LIBRARY = f"""---
count: 1
---

| slug | artist | title | bpm | key | file |
|---|---|---|---|---|---|
| {SLUG} | "Artist" | Title | 150.0 | A minor | [[audio/{SLUG}.opus]] |
"""


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    lib = tmp_path / "library.md"
    lib.write_text(LIBRARY, encoding="utf-8")
    audio = tmp_path / f"{SLUG}.opus"
    audio.write_bytes(b"x" * 1000)
    quality = tmp_path / "quality"
    quality.mkdir()
    (quality / f"{SLUG}.json").write_text(json.dumps({
        "beats": {"tempo_bpm": 150.0, "time_signature": "4/4",
                  "beat_times_s": [0.0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.2]},
        "structure": {"segments": [{"start_s": 0, "end_s": 10, "duration_s": 10,
                                    "rms_dbfs": -8, "label": "main"}]},
        "cues": {"cues": [{"time_s": 0, "type": "intro_start", "confidence": 0.9}]},
    }), encoding="utf-8")
    monkeypatch.setattr(api, "QUALITY_DIR", quality)
    monkeypatch.setattr(api, "STEMS_DIR", tmp_path / "stems")
    monkeypatch.setattr(api, "DIGITAKT_DIR", tmp_path / "digitakt")
    monkeypatch.setattr(api, "_resolve_audio_path",
                        lambda e: audio if SLUG in e.get("file", "") else None)
    return TestClient(api.create_app(library_file=lib))


def test_list_tracks(client: TestClient):
    tracks = client.get("/api/tracks").json()
    assert len(tracks) == 1
    t = tracks[0]
    assert t["slug"] == SLUG and t["artist"] == "Artist"  # guillemets retires
    assert t["has_audio"] is True and t["has_bank"] is False


def test_track_detail(client: TestClient):
    d = client.get(f"/api/tracks/{SLUG}").json()
    assert d["tempo_bpm"] == 150.0
    assert d["bar_times"] == [0.0, 1.6, 3.2]
    assert d["segments"][0]["label"] == "main"
    assert d["cues"][0]["type"] == "intro_start"


def test_audio_supports_range(client: TestClient):
    r = client.get(f"/api/tracks/{SLUG}/audio", headers={"Range": "bytes=0-99"})
    assert r.status_code == 206 and len(r.content) == 100


def test_unknown_slug_is_404(client: TestClient):
    assert client.get("/api/tracks/../../etc/audio").status_code == 404
    assert client.get("/api/tracks/nope/audio").status_code == 404


def test_bank_missing_then_present(client: TestClient):
    assert client.get(f"/api/tracks/{SLUG}/bank").status_code == 404
    api.DIGITAKT_DIR.mkdir()
    (api.DIGITAKT_DIR / f"{SLUG}.json").write_text(json.dumps({
        "slug": SLUG, "bpm": 150, "from_stems": True, "patterns": [],
        "generated_at": "2026-10-06T00:00:00+00:00",
    }), encoding="utf-8")
    assert client.get(f"/api/tracks/{SLUG}/bank").json()["bpm"] == 150

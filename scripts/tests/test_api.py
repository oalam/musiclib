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
    assert d["harmony"] is None and d["keyboard_setup"] is None


def test_track_detail_harmony(client: TestClient):
    path = api.QUALITY_DIR / f"{SLUG}.json"
    sidecar = json.loads(path.read_text(encoding="utf-8"))
    scale = {"root": 9, "root_name": "A", "scale": "AEOLIAN (MINOR)", "label": "A mineur (éolien)",
             "notes": ["A", "B", "C", "D", "E", "F", "G"], "score": 1.1}
    sidecar["harmony"] = {
        "analyzed_at": "2026-10-06", "source": "stems",
        "scale": {**scale, "margin": 0.2, "candidates": [scale]},
        "chords": [{"bar": 0, "start_s": 0.0, "end_s": 1.6, "label": "Am", "root": 9,
                    "quality": "min", "confidence": 0.9}],
        "progression": [{"label": "main", "start_s": 0.0, "end_s": 10.0, "chords": ["Am"]}],
    }
    path.write_text(json.dumps(sidecar), encoding="utf-8")
    d = client.get(f"/api/tracks/{SLUG}").json()
    assert d["harmony"]["scale"]["label"] == "A mineur (éolien)"
    assert d["harmony"]["chords"][0]["label"] == "Am"
    assert d["keyboard_setup"] == "KB SCALE = AEOLIAN (MINOR), ROOT NOTE = A"


def test_audio_supports_range(client: TestClient):
    r = client.get(f"/api/tracks/{SLUG}/audio", headers={"Range": "bytes=0-99"})
    assert r.status_code == 206 and len(r.content) == 100


def test_unknown_slug_is_404(client: TestClient):
    assert client.get("/api/tracks/../../etc/audio").status_code == 404
    assert client.get("/api/tracks/nope/audio").status_code == 404


def test_generate_bank_runs_harmony(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []

    def fake_bank(slug: str, entries: dict[str, dict[str, str]], **kw: object) -> int:
        calls.append("bank")
        api.DIGITAKT_DIR.mkdir(exist_ok=True)
        (api.DIGITAKT_DIR / f"{slug}.json").write_text(json.dumps({
            "slug": slug, "bpm": 150, "from_stems": True, "patterns": [],
            "generated_at": "2026-10-06T00:00:00+00:00",
        }), encoding="utf-8")
        return 0

    monkeypatch.setattr(api.digitakt, "process", fake_bank)
    monkeypatch.setattr(api.harmony, "process", lambda slug, entries: calls.append("harmony") or 1)
    r = client.post(f"/api/tracks/{SLUG}/bank")
    assert r.status_code == 200 and r.json()["bpm"] == 150  # echec harmonie : bank servie quand meme
    assert calls == ["bank", "harmony"]


def test_bank_missing_then_present(client: TestClient):
    assert client.get(f"/api/tracks/{SLUG}/bank").status_code == 404
    api.DIGITAKT_DIR.mkdir()
    (api.DIGITAKT_DIR / f"{SLUG}.json").write_text(json.dumps({
        "slug": SLUG, "bpm": 150, "from_stems": True, "patterns": [],
        "generated_at": "2026-10-06T00:00:00+00:00",
    }), encoding="utf-8")
    assert client.get(f"/api/tracks/{SLUG}/bank").json()["bpm"] == 150


# ---------------------------------------------------------------------------
# Ajout de morceau (7.I)
# ---------------------------------------------------------------------------

@pytest.fixture
def grab_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    lib = tmp_path / "library.md"
    lib.write_text(LIBRARY, encoding="utf-8")
    monkeypatch.setattr(api, "require_media", lambda: tmp_path)

    def runner(req, ctx) -> None:
        ctx.step("metadata")
        ctx.set_slug("x_-_y", created=True)

    return TestClient(api.create_app(library_file=lib, runner=runner))


def test_grab_search(grab_client: TestClient, monkeypatch: pytest.MonkeyPatch):
    import grab
    fmt = {"acodec": "opus", "abr": 160}
    cand = grab.Candidate(source="soundcloud", url="https://sc/1", title="T",
                          info={}, fmt=fmt, match=1.0)
    monkeypatch.setattr(grab, "search", lambda q, search_n: [cand])
    res = grab_client.post("/api/grab/search", json={"query": "Limitlezz x Maureen"})
    assert res.status_code == 200
    assert res.json()[0]["url"] == "https://sc/1"
    assert grab_client.post("/api/grab/search", json={"query": ""}).status_code == 422


def test_grab_job_puis_polling(grab_client: TestClient):
    res = grab_client.post("/api/grab", json={"url": "https://yt/1", "stems": True})
    assert res.status_code == 202
    job_id = res.json()["id"]
    for _ in range(200):
        job = grab_client.get(f"/api/jobs/{job_id}").json()
        if job["status"] == "done":
            break
    assert job["status"] == "done" and job["slug"] == "x_-_y"
    assert grab_client.get("/api/jobs/inconnu").status_code == 404


@pytest.mark.parametrize("body", [
    {"url": "pas une url"},
    {"url": "https://open.spotify.com/track/abc"},
    {"url": "https://yt/1", "bank": True, "analyze_quality": False},
    {"url": "https://yt/1", "folder": "../hors"},
])
def test_grab_requetes_refusees(grab_client: TestClient, body: dict[str, object]):
    assert grab_client.post("/api/grab", json=body).status_code == 422


def test_grab_sans_disque_media(grab_client: TestClient, monkeypatch: pytest.MonkeyPatch):
    def absent() -> None:
        raise api.MediaRootUnavailable("disque absent")
    monkeypatch.setattr(api, "require_media", absent)
    assert grab_client.post("/api/grab", json={"url": "https://yt/1"}).status_code == 503

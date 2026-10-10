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

| slug | artist | title | bpm | key | file | added | tags |
|---|---|---|---|---|---|---|---|
| {SLUG} | "Artist" | Title | 150.0 | A minor | [[audio/{SLUG}.opus]] | 2026-10-09 | lo-fi, tribe |
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
    assert t["added"] == "2026-10-09" and t["tags"] == "lo-fi, tribe"  # tri / filtre du front


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


# ---------------------------------------------------------------------------
# Envoi d'une track a la DT2 (7.E)
# ---------------------------------------------------------------------------

def test_dt2_send(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    from test_dt2_midi import FakeMidi

    lib = tmp_path / "library.md"
    lib.write_text(LIBRARY, encoding="utf-8")
    monkeypatch.setattr(api, "DIGITAKT_DIR", tmp_path / "digitakt")
    api.DIGITAKT_DIR.mkdir()
    (api.DIGITAKT_DIR / f"{SLUG}.json").write_text(json.dumps({
        "slug": SLUG, "bpm": 150, "from_stems": True,
        "generated_at": "2026-10-07T00:00:00+00:00",
        "patterns": [{"slot": 1, "label": "intro", "start_s": 0, "end_s": 4, "bars": 1,
                      "steps": 16, "repeats": 1, "tracks": [
                          {"index": 1, "role": "kick", "trigs": [{"step": 0}, {"step": 4}]}]}],
    }), encoding="utf-8")
    fake = FakeMidi()
    client = TestClient(api.create_app(library_file=lib, sender=api.dt2_midi.Dt2Sender(opener=fake)))
    body = {"slug": SLUG, "slot": 1, "track": 1, "port": "DT2", "channel": 10}

    assert client.get("/api/dt2/send").json() is None
    assert client.post("/api/dt2/send", json=body | {"track": 2}).status_code == 422
    assert client.post("/api/dt2/send", json=body | {"slug": "inconnu"}).status_code == 404
    assert client.post("/api/dt2/send", json=body | {"channel": 17}).status_code == 422
    assert client.post("/api/dt2/send", json=body | {"octave": 6}).status_code == 422
    r = client.post("/api/dt2/send", json=body)
    assert r.status_code == 202 and r.json()["status"] == "waiting" and r.json()["trigs"] == 2
    assert client.post("/api/dt2/send", json=body).status_code == 409
    fake.feed("start")
    fake.feed("clock")
    assert client.get("/api/dt2/send").json()["status"] == "sending"
    assert client.delete("/api/dt2/send").json()["status"] == "cancelled"


def test_dt2_ports(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(api.dt2_midi, "list_ports",
                        lambda: api.dt2_midi.Dt2Ports(inputs=["X"], outputs=["X"], default="X"))
    assert client.get("/api/dt2/ports").json()["default"] == "X"


# --- Samples DT2 (7.J2) -------------------------------------------------------

@pytest.fixture
def samples_client(tmp_path: Path) -> TestClient:
    from analyzer.samples import Manifest, SampleEntry, select

    src = tmp_path / "Samples"
    (src / "p").mkdir(parents=True)
    (src / "p" / "fx1.wav").write_bytes(b"RIFF" + b"x" * 100)
    entries = [SampleEntry(source=f"p/fx{i}.wav", family="JUNGLE", code="FX", pack="p",
                           name=f"FX {i}", duration=1.0, rank=i,
                           flags=["sature"] if i == 10 else [])
               for i in range(1, 19)]
    select(entries, 16)
    path = tmp_path / "manifest.json"
    api.samples.save_manifest(Manifest(source_root=str(src), total=18, entries=entries), path)
    lib = tmp_path / "library.md"
    lib.write_text(LIBRARY, encoding="utf-8")
    return TestClient(api.create_app(library_file=lib, samples_manifest=path, samples_src=src,
                                     samples_overrides=tmp_path / "overrides.json"))


def test_samples_cells(samples_client: TestClient):
    cells = samples_client.get("/api/samples").json()
    assert cells == [{"folder": "FX", "branch": "FX", "code": "FX", "sub": "", "quota": 16,
                      "candidates": 18, "selected": 16, "keep": 0, "drop": 0, "to_listen": 16,
                      "flagged": 1, "reserve": 0}]
    cell = samples_client.get("/api/samples/cell", params={"folder": "FX"}).json()
    assert [e["rank"] for e in cell] == list(range(1, 19))
    assert samples_client.get("/api/samples/cell", params={"folder": "DRUMS/BD"}).status_code == 404
    folders = samples_client.get("/api/samples/folders").json()
    assert folders[0] == "DRUMS/BD" and "FX/RISE" in folders


def _post(client: TestClient, path: str, **body: object):
    return client.post(f"/api/samples/{path}", json=body)


def test_samples_drop_promotes_next_and_persists(samples_client: TestClient):
    r = _post(samples_client, "status", sources=["p/fx1.wav"], status="drop")
    assert r.status_code == 200 and (r.json()[0]["drop"], r.json()[0]["selected"]) == (1, 16)
    cell = samples_client.get("/api/samples/cell", params={"folder": "FX"}).json()
    selected = [e["source"] for e in cell if e["selected"]]
    assert "p/fx1.wav" not in selected and "p/fx17.wav" in selected
    assert _post(samples_client, "status", sources=["p/absent.wav"], status="keep").status_code == 404
    assert _post(samples_client, "status", sources=["p/fx1.wav"], status="maybe").status_code == 422
    assert _post(samples_client, "status", sources=[], status="keep").status_code == 422


def test_samples_batch_is_all_or_nothing(samples_client: TestClient):
    r = _post(samples_client, "status", sources=["p/fx1.wav", "p/absent.wav"], status="keep")
    assert r.status_code == 404
    assert samples_client.get("/api/samples").json()[0]["keep"] == 0
    r = _post(samples_client, "status", sources=["p/fx1.wav", "p/fx2.wav", "p/fx1.wav"], status="keep")
    assert r.json()[0]["keep"] == 2


def test_samples_audio_only_from_manifest(samples_client: TestClient):
    assert samples_client.get("/api/samples/audio", params={"source": "p/fx1.wav"}).status_code == 200
    assert samples_client.get("/api/samples/audio", params={"source": "p/fx2.wav"}).status_code == 404
    assert samples_client.get("/api/samples/audio",
                              params={"source": "../library.md"}).status_code == 404


def test_samples_move_writes_override(samples_client: TestClient, tmp_path: Path):
    r = _post(samples_client, "move", sources=["p/fx1.wav"], code="FX", sub="RISE")
    assert r.status_code == 200
    cells = {c["folder"]: c for c in r.json()}
    assert cells["FX/RISE"]["selected"] == 1 and cells["FX/RISE"]["sub"] == "RISE"
    assert cells["FX"]["selected"] == 16          # le 17e monte
    assert json.loads((tmp_path / "overrides.json").read_text()) == {
        "p/fx1.wav": {"code": "FX", "sub": "RISE"}}
    assert _post(samples_client, "move", sources=["p/fx1.wav"], code="ZZ").status_code == 422
    assert _post(samples_client, "move", sources=["p/fx1.wav"],
                 code="VX", sub="RISE").status_code == 422


def test_samples_stars_tags_filter(samples_client: TestClient, tmp_path: Path):
    assert _post(samples_client, "stars", sources=["p/fx10.wav"], stars=4).status_code == 200
    assert _post(samples_client, "stars", sources=["p/fx1.wav"], stars=9).status_code == 422
    _post(samples_client, "tags", sources=["p/fx10.wav", "p/fx2.wav"], add=["Dark"])
    cell = samples_client.get("/api/samples/cell", params={"folder": "FX"}).json()
    assert (cell[0]["source"], cell[0]["stars"], cell[0]["tags"]) == ("p/fx10.wav", 4, ["dark"])
    assert samples_client.get("/api/samples/tags").json() == ["dark"]
    only = samples_client.get("/api/samples", params={"tags": "dark", "min_stars": 3}).json()
    assert [(c["candidates"], c["selected"]) for c in only] == [(1, 1)]
    two = samples_client.get("/api/samples", params={"tags": ["dark", "x"]}).json()
    assert [c["candidates"] for c in two] == [2]
    assert samples_client.get("/api/samples", params={"section": "rhythm"}).json() == []
    assert samples_client.get("/api/samples", params={"section": "solo"}).status_code == 422
    assert json.loads((tmp_path / "overrides.json").read_text()) == {
        "p/fx10.wav": {"stars": 4, "tags": ["dark"]}, "p/fx2.wav": {"tags": ["dark"]}}


def test_samples_trash_restore(samples_client: TestClient):
    r = _post(samples_client, "trash", sources=["p/fx1.wav"])
    assert r.json()[0]["candidates"] == 17
    trash = samples_client.get("/api/samples/loose", params={"which": "trash"}).json()
    assert [t["source"] for t in trash] == ["p/fx1.wav"]
    # toujours ecoutable depuis la corbeille
    assert samples_client.get("/api/samples/audio", params={"source": "p/fx1.wav"}).status_code == 200
    assert _post(samples_client, "status", sources=["p/fx1.wav"], status="keep").status_code == 404
    r = _post(samples_client, "restore", sources=["p/fx1.wav"])
    assert r.status_code == 200
    assert samples_client.get("/api/samples/loose", params={"which": "trash"}).json() == []
    assert samples_client.get("/api/samples/loose", params={"which": "x"}).status_code == 422


def test_samples_kit_view_reserve_and_tags(tmp_path: Path):
    from analyzer.samples import Manifest, ReserveSample, SampleEntry

    src = tmp_path / "Samples"
    path = tmp_path / "manifest.json"
    m = Manifest(
        source_root=str(src), total=3,
        entries=[SampleEntry(source="k/a/fx1.wav", family="JUNGLE", code="FX", pack="k",
                             name="FX 1", duration=1.0, rank=1, selected=True)],
        reserve=[ReserveSample(source="k/a/fx2.wav", family="JUNGLE", code="FX", pack="k",
                               duration=1.0),
                 ReserveSample(source="k/b/sd1.wav", family="JUNGLE", code="SD", pack="k",
                               duration=0.3)])
    api.samples.save_manifest(m, path)
    lib = tmp_path / "library.md"
    lib.write_text(LIBRARY, encoding="utf-8")
    client = TestClient(api.create_app(library_file=lib, samples_manifest=path, samples_src=src,
                                       samples_overrides=tmp_path / "overrides.json"))
    kits = client.get("/api/samples/kits").json()
    assert [(k["kit"], k["candidates"], k["reserve"]) for k in kits["kits"]] == [
        ("k/a", 1, 1), ("k/b", 0, 1)]
    # sans filtre kit : reserve comptee, case sans candidat absente ; avec : case SD visible
    assert [(c["code"], c["reserve"]) for c in client.get("/api/samples").json()] == [("FX", 1)]
    rows = client.get("/api/samples/cell", params={"folder": "FX", "overflow": True}).json()
    assert [r["overflow"] for r in rows] == [False, True]
    cells = {c["code"]: c for c in client.get("/api/samples", params={"kit": "k/b"}).json()}
    assert cells["SD"]["reserve"] == 1 and cells["SD"]["candidates"] == 0
    rows = client.get("/api/samples/cell", params={"folder": "FX", "kit": "k/a"}).json()
    assert [(r["source"], r["overflow"]) for r in rows] == [("k/a/fx1.wav", False), ("k/a/fx2.wav", True)]
    tree = client.get("/api/samples/kit/tree", params={"kit": "k"}).json()
    assert [(r["code"], r["source"], r["overflow"]) for r in tree["entries"]] == [
        ("SD", "k/b/sd1.wav", True), ("FX", "k/a/fx1.wav", False), ("FX", "k/a/fx2.wav", True)]
    assert tree["unclassified"] == []
    # vue par type (7.K) : tous les kits, ou un seul
    rows = client.get("/api/samples/tree", params={"codes": "FX"}).json()
    assert [(r["source"], r["overflow"]) for r in rows] == [("k/a/fx1.wav", False), ("k/a/fx2.wav", True)]
    assert client.get("/api/samples/tree", params={"codes": "FX", "kit": "k/b"}).json() == []
    # garder un fichier de la reserve le fait entrer comme candidat
    r = _post(client, "status", sources=["k/a/fx2.wav"], status="keep")
    assert r.status_code == 200 and r.json()[0]["keep"] == 1
    # tags de kit herites
    r = _post(client, "kit/tags", kit="k", add=["Acid"])
    assert r.status_code == 200
    assert client.get("/api/samples/kits").json()["tags"] == {"k": ["acid"]}
    cells = {c["code"]: c for c in client.get("/api/samples", params={"kit": "k", "tags": "acid"}).json()}
    assert cells["FX"]["candidates"] == 2 and cells["SD"]["reserve"] == 1
    assert _post(client, "kit/tags", kit="zz", add=["x"]).status_code == 422
    assert client.get("/api/samples", params={"kit": "k", "tags": "nope"}).json() == []
    facets = {x["tag"]: (x["group"], x["count"]) for x in client.get("/api/samples/facets").json()}
    assert facets["acid"] == ("genre", 3)
    tree = client.get("/api/samples/kit/tree", params={"kit": "k", "kind": "loop"}).json()
    assert tree["entries"] == []
    # roue chromatique et filtre par note (7.J7) : aucune note ici
    wheel = client.get("/api/samples/notes").json()
    assert len(wheel) == 12 and wheel[0] == {"note": "C", "count": 0}
    assert client.get("/api/samples", params={"notes": "A"}).json() == []
    assert client.get("/api/samples", params={"notes": "H"}).status_code == 422


def test_samples_export(tmp_path: Path):
    from analyzer.samples import Manifest, SampleEntry

    src = tmp_path / "Samples"
    (src / "p").mkdir(parents=True)
    (src / "p" / "fx1.wav").write_bytes(b"RIFF" + b"x" * 100)
    path = tmp_path / "manifest.json"
    api.samples.save_manifest(Manifest(source_root=str(src), total=1, entries=[
        SampleEntry(source="p/fx1.wav", family="JUNGLE", code="FX", pack="p", name="FX 1 p",
                    duration=1.0, rank=1, selected=True)]), path)
    lib = tmp_path / "library.md"
    lib.write_text(LIBRARY, encoding="utf-8")
    dest = tmp_path / "out"
    client = TestClient(api.create_app(library_file=lib, samples_manifest=path, samples_src=src,
                                       samples_overrides=tmp_path / "overrides.json",
                                       samples_export=dest,
                                       samples_export_index=tmp_path / "export.json"))
    dry = client.post("/api/samples/export", json={}).json()
    assert dry["dry_run"] and dry["copied"] == ["FX/FX 1 p.wav"] and not dest.exists()
    r = client.post("/api/samples/export", json={"dry_run": False}).json()
    assert r["files"] == 1 and (dest / "FX/FX 1 p.wav").exists()


def test_sample_folder_add(samples_client: TestClient, tmp_path: Path):
    """Sous-dossier manuel (7.K) : cree, rejouable, cible d'un rangement."""
    r = samples_client.post("/api/samples/folders", json={"code": "BD", "sub": "rumble"})
    assert r.status_code == 200 and "DRUMS/BD/RUMBLE" in r.json()
    again = samples_client.post("/api/samples/folders", json={"code": "BD", "sub": "RUMBLE"}).json()
    assert again.count("DRUMS/BD/RUMBLE") == 1
    assert samples_client.post("/api/samples/folders", json={"code": "ZZ", "sub": "AB"}).status_code == 422
    assert samples_client.post("/api/samples/folders", json={"code": "BD", "sub": "A B"}).status_code == 422
    assert samples_client.get("/api/samples/folders").json().count("DRUMS/BD/RUMBLE") == 1
    # rangement dans un sous-dossier manuel, persistant dans folders.json
    assert _post(samples_client, "move", sources=["p/fx1.wav"], code="FX", sub="XRAY").status_code == 422
    assert samples_client.post("/api/samples/folders", json={"code": "FX", "sub": "XRAY"}).status_code == 200
    r = _post(samples_client, "move", sources=["p/fx1.wav"], code="FX", sub="XRAY")
    assert r.status_code == 200 and "FX/XRAY" in {c["folder"] for c in r.json()}
    assert json.loads(api.samples.FOLDERS_FILE.read_text(encoding="utf-8")) == {"BD": ["RUMBLE"], "FX": ["XRAY"]}


def test_sample_rebuild(samples_client: TestClient, monkeypatch: pytest.MonkeyPatch):
    """Reanalyse depuis le front (7.K) : en arriere-plan, ecritures refusees pendant."""
    import threading
    import time

    gate = threading.Event()
    real = api.samples.build_manifest

    def slow(*args: object, **kwargs: object) -> object:
        gate.wait(5)
        return real(*args, **kwargs)

    monkeypatch.setattr(api.samples, "build_manifest", slow)
    monkeypatch.setattr(api.samples, "measure", lambda path, code: [])
    r = samples_client.post("/api/samples/rebuild")
    assert r.status_code == 202 and r.json()["status"] == "running"
    assert samples_client.post("/api/samples/rebuild").status_code == 409
    assert _post(samples_client, "status", sources=["p/fx1.wav"], status="keep").status_code == 409
    gate.set()
    for _ in range(100):
        state = samples_client.get("/api/samples/rebuild").json()
        if state["status"] != "running":
            break
        time.sleep(0.05)
    assert state["status"] == "done", state
    assert state["finished_at"] and state["candidates"] >= 1

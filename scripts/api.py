#!/usr/bin/env python3
"""API locale du front (Phase 7.C) : library, audio, structure, banks Digitakt,
base de connaissance (Phase 7.D).

Lecture seule sur la library, sauf la generation d'une bank (`POST .../bank`)
qui appelle `digitakt.py`. Ecoute sur 127.0.0.1 uniquement. Les fichiers ne
sont servis que pour un slug present dans library.md (pas de chemin libre).

Usage:
    python api.py                 # http://127.0.0.1:8765 (sert aussi web/dist)
    python api.py --port 9000

En dev du front : `npm run dev` dans web/ (proxy /api → 8765).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import digitakt
import kb
from analyzer.infer import load_sidecar
from analyzer.rhythm_signature import beats_per_bar
from analyzer.types import CuePoint, DigitaktBank, Segment
from library_md import parse_library
from stems import _resolve_audio_path

VAULT_ROOT = Path(__file__).resolve().parent.parent
LIBRARY_FILE = VAULT_ROOT / "library" / "library.md"
QUALITY_DIR = VAULT_ROOT / "library" / "quality"
STEMS_DIR = VAULT_ROOT / "library" / "stems"
DIGITAKT_DIR = VAULT_ROOT / "library" / "digitakt"
WEB_DIST = VAULT_ROOT / "web" / "dist"

_SUMMARY_FIELDS = ("artist", "title", "bpm", "key", "duration", "genre",
                   "energy", "mood", "quality_score", "groove_cluster")


class TrackSummary(BaseModel):
    slug: str
    artist: str = ""
    title: str = ""
    bpm: str = ""
    key: str = ""
    duration: str = ""
    genre: str = ""
    energy: str = ""
    mood: str = ""
    quality_score: str = ""
    groove_cluster: str = ""
    has_audio: bool = False
    has_stems: bool = False
    has_bank: bool = False


class TrackDetail(TrackSummary):
    tempo_bpm: float | None = None
    time_signature: str | None = None
    bar_times: list[float] = []  # grille du sidecar (repli si pas de bank)
    segments: list[Segment] = []
    cues: list[CuePoint] = []
    fields: dict[str, str] = {}


def _clean(value: str) -> str:
    return value.strip().strip('"')


def _summary(slug: str, entry: dict[str, str]) -> TrackSummary:
    data: dict[str, Any] = {k: _clean(entry.get(k, "")) for k in _SUMMARY_FIELDS}
    return TrackSummary(
        slug=slug,
        has_audio=_resolve_audio_path(entry) is not None,
        has_stems=(STEMS_DIR / slug / "drums.wav").exists(),
        has_bank=(DIGITAKT_DIR / f"{slug}.json").exists(),
        **data,
    )


def _bar_times(beats: dict[str, Any]) -> list[float]:
    """Debuts de mesure depuis les beats du sidecar (4/4 sauf signature confiante)."""
    bpb = beats_per_bar(beats.get("time_signature") or "4/4")
    if float(beats.get("time_signature_confidence") or 0) < 0.5:
        bpb = 4
    return [round(float(t), 3) for t in (beats.get("beat_times_s") or [])[::bpb]]


def create_app(library_file: Path = LIBRARY_FILE) -> FastAPI:
    app = FastAPI(title="music library", version="0.8.0")

    def entries() -> dict[str, dict[str, str]]:
        return parse_library(library_file)

    def entry_or_404(slug: str) -> dict[str, str]:
        entry = entries().get(slug)
        if entry is None:
            raise HTTPException(404, f"slug inconnu : {slug}")
        return entry

    @app.get("/api/tracks", response_model=list[TrackSummary])
    def list_tracks() -> list[TrackSummary]:
        return [_summary(slug, e) for slug, e in entries().items()]

    @app.get("/api/tracks/{slug}", response_model=TrackDetail)
    def track_detail(slug: str) -> TrackDetail:
        entry = entry_or_404(slug)
        sidecar = load_sidecar(QUALITY_DIR, slug) or {}
        beats = sidecar.get("beats") or {}
        return TrackDetail(
            **_summary(slug, entry).model_dump(),
            tempo_bpm=beats.get("tempo_bpm"),
            time_signature=beats.get("time_signature"),
            bar_times=_bar_times(beats),
            segments=((sidecar.get("structure") or {}).get("segments") or []),
            cues=((sidecar.get("cues") or {}).get("cues") or []),
            fields={k: _clean(v) for k, v in entry.items()},
        )

    @app.get("/api/tracks/{slug}/audio")
    def track_audio(slug: str) -> FileResponse:
        path = _resolve_audio_path(entry_or_404(slug))
        if path is None:
            raise HTTPException(404, f"pas d'audio pour {slug}")
        return FileResponse(path)  # gere les requetes Range (seek)

    @app.get("/api/tracks/{slug}/bank", response_model=DigitaktBank)
    def track_bank(slug: str) -> DigitaktBank:
        entry_or_404(slug)
        path = DIGITAKT_DIR / f"{slug}.json"
        if not path.exists():
            raise HTTPException(404, f"pas de bank pour {slug}")
        return DigitaktBank.model_validate(json.loads(path.read_text(encoding="utf-8")))

    @app.post("/api/tracks/{slug}/bank", response_model=DigitaktBank)
    def generate_bank(slug: str) -> DigitaktBank:
        all_entries = entries()
        if slug not in all_entries:
            raise HTTPException(404, f"slug inconnu : {slug}")
        rc = digitakt.process(slug, all_entries, phrase_bars=8, threshold=0.5, midi=True)
        if rc != 0:
            raise HTTPException(422, f"generation impossible pour {slug} "
                                     "(sidecar ou audio manquant, voir les logs)")
        return track_bank(slug)

    @app.get("/api/kb/search", response_model=list[kb.KbHit])
    def kb_search(q: str = Query(..., min_length=1, max_length=200),
                  limit: int = Query(20, ge=1, le=100)) -> list[kb.KbHit]:
        return kb.search(q, kb.load_corpus(), limit)

    @app.get("/api/kb/note", response_model=kb.KbNote)
    def kb_note(path: str) -> kb.KbNote:
        note = kb.read_note(path)
        if note is None:
            raise HTTPException(404, f"note hors base de connaissance : {path}")
        return note

    if WEB_DIST.exists():
        app.mount("/", StaticFiles(directory=WEB_DIST, html=True), name="web")
    return app


def main() -> int:
    import uvicorn

    parser = argparse.ArgumentParser(description="API locale du front music.")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    uvicorn.run(create_app(), host="127.0.0.1", port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""API locale du front (Phase 7.C) : library, audio, structure, banks Digitakt,
base de connaissance (Phase 7.D), ajout de morceaux (Phase 7.I), envoi d'une
track de pattern a la Digitakt II (Phase 7.E, `dt2_midi.py`), ecoute des
samples DT2 (Phase 7.J2, `samples.py`), leur export vers Transfer (7.J3) et
la vue par kit (7.J5 : filtre, tags et corbeille d'un kit entier) et la barre
de recherche (7.J6 : memes filtres sur toutes les lectures de samples ; 7.J7 :
filtre par note et roue chromatique `GET /api/samples/notes`).

Lecture seule sur la library, sauf la generation d'une bank (`POST .../bank`)
qui appelle `digitakt.py` puis `harmony.py` (7.H), et l'ajout d'un morceau
(`POST /api/grab`, job en arriere-plan, un a la fois, cf. `jobs.py`), et les
decisions d'ecoute et le rangement des samples (`POST /api/samples/...`,
manifeste et overrides.json), et l'export des samples retenus
(`POST /api/samples/export`, copie vers `<MEDIA>/Live/samples`). L'envoi
MIDI (`/api/dt2/send`) n'ecrit rien sur disque. Ecoute
sur 127.0.0.1 uniquement. Les fichiers ne sont servis que pour un slug present
dans library.md, et un sample que s'il figure au manifeste (pas de chemin libre).

Usage:
    python api.py                 # http://127.0.0.1:8765 (sert aussi web/dist)
    python api.py --port 9000

En dev du front : `npm run dev` dans web/ (proxy /api → 8765).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Annotated, Any, Literal

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import digitakt
import dt2_midi
import grab
import harmony
import kb
import samples
import stems
from analyzer.harmony import Harmony, keyboard_setup
from analyzer.infer import load_sidecar
from analyzer.rhythm_signature import beats_per_bar
from analyzer.samples import (
    PITCH_CLASSES,
    STARS_MAX,
    ExportReport,
    KitInfo,
    LooseSample,
    Override,
    SampleFilter,
    SampleEntry,
    SampleError,
    Status,
    all_tags,
    cell_of,
    folder_key,
    folder_parts,
    export,
    facet_notes,
    facet_tags,
    filter_manifest,
    in_kit,
    kit_rows,
    kit_tags,
    kits,
    known,
    loose,
    overflow_of,
    promote,
    quota,
    target_folders,
    restore_kit,
    set_kit_tags,
    set_stars,
    set_status,
    set_tags,
    trash_kit,
)
from analyzer.samples import move as move_sample
from analyzer.samples import restore as restore_sample
from analyzer.samples import trash as trash_sample
from analyzer.types import CuePoint, DigitaktBank, Segment
from jobs import GrabRequest, Job, JobContext, JobStore, Runner, StepFailed
from library_md import parse_library
from paths import (
    DIGITAKT_DIR,
    DT2_SAMPLES_DIR,
    LIBRARY_FILE,
    QUALITY_DIR,
    SAMPLES_SRC_DIR,
    STEMS_DIR,
    VAULT_ROOT,
    MediaRootUnavailable,
    require_media,
)
from paths import resolve_audio as _resolve_audio_path

WEB_DIST = VAULT_ROOT / "web" / "dist"

_SUMMARY_FIELDS = ("artist", "title", "bpm", "key", "duration", "genre",
                   "energy", "mood", "quality_score", "groove_cluster", "added", "tags")


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
    added: str = ""  # date d'ajout ISO (tri par date du front)
    tags: str = ""  # tags manuels de library.md, separes par des virgules
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
    harmony: Harmony | None = None  # Phase 7.H (harmony.py)
    keyboard_setup: str | None = None  # reglage DT2 de la gamme (§8.5.2)


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


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=300)
    search_n: int = Field(3, ge=1, le=5)


def run_grab(req: GrabRequest, ctx: JobContext) -> None:
    """Pipeline d'un job 7.I (ecrit dans library.md, le sidecar, les stems, la bank)."""
    require_media()
    result = grab.ingest(req.url, grab.IngestOptions(folder=req.folder), on_step=ctx.step)
    slug = result.slug
    ctx.set_slug(slug, result.created)
    if req.analyze_quality:
        ctx.step("quality")
        grab.run_quality_analysis(result.audio_path, slug, result.style_bpm)
    if req.stems:
        ctx.step("stems")
        entry = parse_library(LIBRARY_FILE).get(slug, {})
        msg = stems.process_one(slug, entry, force=False, model="htdemucs",
                                device="auto", cleanup=True).strip()
        if msg.startswith(("ERROR", "miss")):
            raise StepFailed(msg)
    if req.bank:
        ctx.step("bank")
        all_entries = parse_library(LIBRARY_FILE)
        if digitakt.process(slug, all_entries, phrase_bars=8, threshold=0.5, midi=True):
            raise StepFailed("generation de la bank impossible (voir les logs d'api.py)")
        ctx.step("harmony")
        if harmony.process(slug, all_entries):
            raise StepFailed("analyse harmonique impossible (voir les logs d'api.py)")


class SampleCell(BaseModel):
    """Case de la bibliotheque de samples = dossier final du +Drive (7.J8),
    vue d'ecoute (7.J2)."""
    folder: str         # DRUMS/BD/HARD, LOOPS/BR, FX/RISE, VX, SAMPLE/BD
    branch: str
    code: str
    sub: str            # "" = racine du code
    quota: int | None
    candidates: int
    selected: int
    keep: int
    drop: int
    to_listen: int      # retenus encore pending
    flagged: int        # candidats signales par le pre-filtre
    reserve: int = 0    # hors plafond (7.J5)


Sources = Annotated[list[Annotated[str, Field(min_length=1, max_length=500)]],
                    Field(min_length=1, max_length=2000)]
TagList = list[Annotated[str, Field(max_length=100)]]


class SampleDecision(BaseModel):
    sources: Sources
    status: Status


class SampleMove(BaseModel):
    sources: Sources
    code: str = Field(min_length=2, max_length=2)
    sub: str = Field(default="", max_length=10)     # "" = racine du code


class SampleBatch(BaseModel):
    """Corbeille / restauration d'une selection (7.J4)."""
    sources: Sources


class SampleStars(BaseModel):
    sources: Sources
    stars: int | None = Field(default=None, ge=1, le=STARS_MAX)   # None = retirer


KitPath = Annotated[str, Field(min_length=1, max_length=500)]


class SampleKit(BaseModel):
    """Kit ou pack (prefixe de chemin) mis a la corbeille / restaure (7.J5)."""
    kit: KitPath


class SampleKitTags(BaseModel):
    kit: KitPath
    add: TagList = Field(default_factory=list, max_length=20)
    remove: TagList = Field(default_factory=list, max_length=20)


class SampleKits(BaseModel):
    """Pads du front : bilan par kit, tags poses sur un kit ou un pack."""
    kits: list[KitInfo]
    tags: dict[str, list[str]]


class FacetTag(BaseModel):
    tag: str
    group: str          # genre, instrument, mot (inferes) ou manuel
    count: int


class FacetNote(BaseModel):
    """Part de la roue chromatique (7.J7) : note en dieses, fichiers."""
    note: str
    count: int


def sample_filter(q: Annotated[str | None, Query(max_length=200)] = None,
                  tags: Annotated[list[str] | None, Query(max_length=50)] = None,
                  kits: Annotated[list[str] | None, Query(max_length=50)] = None,
                  section: Literal["rhythm", "melodic"] | None = None,
                  codes: Annotated[list[str] | None, Query(max_length=30)] = None,
                  kind: Literal["oneshot", "loop"] | None = None,
                  min_stars: Annotated[int | None, Query(ge=1, le=STARS_MAX)] = None,
                  notes: Annotated[list[str] | None, Query(max_length=12)] = None) -> SampleFilter:
    """Barre de recherche (7.J6), commune a toutes les lectures de samples."""
    bad = sorted(set(notes or []) - set(PITCH_CLASSES))
    if bad:
        raise HTTPException(422, f"note inconnue : {', '.join(bad)}")
    return SampleFilter(q=q or None, tags=tags or [], kits=kits or [], section=section,
                        codes=codes or [], kind=kind, min_stars=min_stars, notes=notes or [])


SampleQuery = Annotated[SampleFilter, Depends(sample_filter)]


class SampleKitTree(BaseModel):
    """Arborescence d'un kit : fichiers classes (case finale) et non classes."""
    entries: list[SampleEntry]
    unclassified: list[LooseSample]


class SampleExport(BaseModel):
    dry_run: bool = True    # bilan d'abord, copie sur confirmation


class SampleTags(BaseModel):
    sources: Sources
    add: TagList = Field(default_factory=list, max_length=20)
    remove: TagList = Field(default_factory=list, max_length=20)


def _sample_cells(m: samples.Manifest, kit: str | None = None) -> list[SampleCell]:
    """Grille du manifeste (deja filtre par la barre de recherche) ; la reserve
    hors plafond est comptee ; avec `kit`, une case qui n'a que de la reserve
    du kit apparait."""
    cells: dict[str, list[SampleEntry]] = {}
    spare: dict[str, int] = {}
    for e in m.entries:
        if kit is not None and not in_kit(e.source, kit):
            continue
        cells.setdefault(e.folder, []).append(e)
    for r in m.reserve:
        if kit is not None and not in_kit(r.source, kit):
            continue
        if kit is not None:
            cells.setdefault(r.folder, [])
        if r.folder in cells:
            spare[r.folder] = spare.get(r.folder, 0) + 1
    out: list[SampleCell] = []
    for folder, es in sorted(cells.items(), key=lambda kv: folder_key(kv[0])):
        branch, code, sub = folder_parts(folder)
        out.append(SampleCell(
            folder=folder, branch=branch, code=code, sub=sub, quota=quota(folder),
            candidates=len(es),
            selected=sum(e.selected for e in es),
            keep=sum(e.status == "keep" for e in es),
            drop=sum(e.status == "drop" for e in es),
            to_listen=sum(e.selected and e.status == "pending" for e in es),
            flagged=sum(bool(e.flags) for e in es),
            reserve=spare.get(folder, 0),
        ))
    return out


def _validate_grab(req: GrabRequest) -> None:
    if not grab.is_url(req.url):
        raise HTTPException(422, "url attendue (choisir un candidat de la recherche)")
    if grab.is_spotify(req.url):
        raise HTTPException(422, "Spotify ne fournit pas l'audio : chercher le titre")
    if req.bank and not req.analyze_quality:
        raise HTTPException(422, "la bank exige l'analyse complete (beats du sidecar)")
    if req.folder:
        sub = Path(req.folder)
        if sub.is_absolute() or ".." in sub.parts:
            raise HTTPException(422, f"dossier invalide : {req.folder}")


def create_app(library_file: Path = LIBRARY_FILE, runner: Runner = run_grab,
               sender: dt2_midi.Dt2Sender | None = None,
               samples_manifest: Path = samples.MANIFEST_FILE,
               samples_src: Path = SAMPLES_SRC_DIR,
               samples_overrides: Path = samples.OVERRIDES_FILE,
               samples_export: Path = DT2_SAMPLES_DIR,
               samples_export_index: Path = samples.EXPORT_INDEX_FILE) -> FastAPI:
    app = FastAPI(title="music library", version="0.9.0")
    jobs = JobStore(runner)
    dt2 = sender or dt2_midi.Dt2Sender()
    app.router.on_shutdown.append(dt2.shutdown)
    app.router.on_shutdown.append(jobs.shutdown)

    samples_lock = threading.Lock()

    def manifest() -> samples.Manifest:
        m = samples.load_manifest(samples_manifest)
        if m is None:
            raise HTTPException(404, "pas de manifeste de samples (lancer samples.py)")
        return m

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
        harmony = Harmony.model_validate(sidecar["harmony"]) if sidecar.get("harmony") else None
        return TrackDetail(
            **_summary(slug, entry).model_dump(),
            tempo_bpm=beats.get("tempo_bpm"),
            time_signature=beats.get("time_signature"),
            bar_times=_bar_times(beats),
            segments=((sidecar.get("structure") or {}).get("segments") or []),
            cues=((sidecar.get("cues") or {}).get("cues") or []),
            fields={k: _clean(v) for k, v in entry.items()},
            harmony=harmony,
            keyboard_setup=keyboard_setup(harmony.scale) if harmony else None,
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
        # harmonie recalculee sur la grille de la nouvelle bank ; un echec
        # (logue) laisse la bank intacte et l'ancien bloc harmony en place
        harmony.process(slug, all_entries)
        return track_bank(slug)

    @app.post("/api/grab/search", response_model=list[grab.CandidateInfo])
    def grab_search(req: SearchRequest) -> list[grab.CandidateInfo]:
        """Candidats YT/SC tries par score (le premier est le choix par defaut)."""
        if grab.is_spotify(req.query):
            raise HTTPException(422, "Spotify ne fournit pas l'audio : chercher le titre")
        try:
            found = grab.search(req.query.strip(), search_n=req.search_n)
        except subprocess.CalledProcessError as exc:
            err = exc.stderr.strip() if isinstance(exc.stderr, str) else str(exc)
            raise HTTPException(502, f"yt-dlp a echoue : {err}") from exc
        return [grab.candidate_info(c) for c in found]

    @app.post("/api/grab", response_model=Job, status_code=202)
    def grab_start(req: GrabRequest) -> Job:
        """Lance l'acquisition + analyse en arriere-plan ; suivi par GET /api/jobs/{id}."""
        _validate_grab(req)
        try:
            require_media()
        except MediaRootUnavailable as exc:
            raise HTTPException(503, str(exc)) from exc
        return jobs.submit(req)

    @app.get("/api/jobs/{job_id}", response_model=Job)
    def job_status(job_id: str) -> Job:
        job = jobs.get(job_id)
        if job is None:
            raise HTTPException(404, f"job inconnu : {job_id}")
        return job

    @app.get("/api/dt2/ports", response_model=dt2_midi.Dt2Ports)
    def dt2_ports() -> dt2_midi.Dt2Ports:
        return dt2_midi.list_ports()

    @app.post("/api/dt2/send", response_model=dt2_midi.SendState, status_code=202)
    def dt2_send(req: dt2_midi.SendRequest) -> dt2_midi.SendState:
        """Arme l'envoi d'une track ; part au Start de la DT2 (suivi par GET)."""
        bank = track_bank(req.slug)  # 404 sans slug ni bank
        try:
            track, steps = dt2_midi.pick_track(bank, req.slot, req.track)
        except dt2_midi.SendTargetError as exc:
            raise HTTPException(422, str(exc)) from exc
        try:
            return dt2.start(req, track, steps)
        except dt2_midi.SendTargetError as exc:  # octave hors plage MIDI
            raise HTTPException(422, str(exc)) from exc
        except dt2_midi.SendBusy as exc:
            raise HTTPException(409, str(exc)) from exc
        except dt2_midi.MidiUnavailable as exc:
            raise HTTPException(503, str(exc)) from exc

    @app.get("/api/dt2/send", response_model=dt2_midi.SendState | None)
    def dt2_send_status() -> dt2_midi.SendState | None:
        return dt2.current()

    @app.delete("/api/dt2/send", response_model=dt2_midi.SendState | None)
    def dt2_send_cancel() -> dt2_midi.SendState | None:
        return dt2.cancel()

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

    @app.get("/api/kb/toc", response_model=list[kb.KbLot])
    def kb_toc() -> list[kb.KbLot]:
        return kb.table_of_contents()

    @app.get("/api/manual/outline", response_model=dict[str, kb.ManualRef])
    def manual_outline() -> dict[str, kb.ManualRef]:
        """Sommaire du manuel (§ -> page) pour les liens de la facade (7.G) ; {} sans PDF."""
        return kb.manual_outline()

    @app.get("/api/manual")
    def manual() -> FileResponse:
        """Manuel PDF local (chemin fixe), ouvert a la page voulue par `#page=N`."""
        if not kb.MANUAL_PDF.exists():
            raise HTTPException(404, "manuel PDF absent de refs/")
        return FileResponse(kb.MANUAL_PDF, media_type="application/pdf")

    def overrides() -> dict[str, Override]:
        return samples.load_overrides(samples_overrides)

    def view(f: SampleFilter) -> samples.Manifest:
        """Manifeste reduit par la barre de recherche."""
        return filter_manifest(manifest(), f, overrides())

    @app.get("/api/samples", response_model=list[SampleCell])
    def sample_cells(f: SampleQuery, kit: str | None = None) -> list[SampleCell]:
        return _sample_cells(view(f), kit or None)

    @app.get("/api/samples/facets", response_model=list[FacetTag])
    def sample_facets() -> list[FacetTag]:
        """Tags proposes par la barre de recherche, avec leur groupe (7.J6)."""
        return [FacetTag(tag=t, group=g, count=n) for t, g, n in facet_tags(manifest(), overrides())]

    @app.get("/api/samples/notes", response_model=list[FacetNote])
    def sample_notes() -> list[FacetNote]:
        """Roue chromatique : fichiers par note, candidats et reserve (7.J7)."""
        return [FacetNote(note=n, count=c) for n, c in facet_notes(manifest())]

    @app.get("/api/samples/cell", response_model=list[SampleEntry])
    def sample_cell(folder: str, f: SampleQuery, kit: str | None = None,
                    overflow: bool = False) -> list[SampleEntry]:
        """Candidats d'une case (dossier final) ; avec `kit`, ceux du kit puis
        sa reserve (lignes `overflow`) ; `overflow` ajoute toute la reserve."""
        m = view(f)
        cell = cell_of(m, folder)
        if kit:
            cell = [e for e in cell if in_kit(e.source, kit)] + overflow_of(m, folder, kit)
        elif overflow:
            cell = cell + overflow_of(m, folder)
        if not cell:
            raise HTTPException(404, f"case inconnue : {folder}")
        return cell

    @app.get("/api/samples/loose", response_model=list[LooseSample])
    def sample_loose(which: Literal["unclassified", "trash"], f: SampleQuery,
                     kit: str | None = None) -> list[LooseSample]:
        """Non classes ou corbeille (7.J4), d'un kit (7.J5)."""
        return loose(view(f), overrides(), which, kit or None)

    @app.get("/api/samples/kit/tree", response_model=SampleKitTree)
    def sample_kit_tree(kit: KitPath, f: SampleQuery) -> SampleKitTree:
        """Tous les fichiers d'un kit par case finale (candidats et hors
        plafond), puis ses non classes ; la corbeille n'y est pas."""
        m = view(f)
        return SampleKitTree(entries=kit_rows(m, kit), unclassified=loose(
            m, samples.load_overrides(samples_overrides), "unclassified", kit))

    @app.get("/api/samples/tree", response_model=list[SampleEntry])
    def sample_tree(f: SampleQuery, kit: str | None = None) -> list[SampleEntry]:
        """Arborescence par case des fichiers qui repondent au filtre (vue par
        type du front, 7.K : filtre d'instrument), reduite a un kit si donne."""
        return kit_rows(view(f), kit or None)

    @app.get("/api/samples/kits", response_model=SampleKits)
    def sample_kits(f: SampleQuery) -> SampleKits:
        """Bilan par kit pour les pads (7.J5), kits a la corbeille compris ;
        compteurs reduits par la barre de recherche."""
        return SampleKits(kits=kits(view(f)),
                          tags=kit_tags(samples.load_overrides(samples_overrides)))

    @app.get("/api/samples/folders", response_model=list[str])
    def sample_folders() -> list[str]:
        """Dossiers cibles d'un rangement (7.J8) : racine du code et sous-categories."""
        return target_folders()

    @app.get("/api/samples/tags", response_model=list[str])
    def sample_tags() -> list[str]:
        return all_tags(samples.load_overrides(samples_overrides))

    def edit(sources: list[str], op: Callable[[samples.Manifest, dict[str, Override], str], object],
             status_code: int = 404) -> list[SampleCell]:
        """Applique `op` a chaque source puis ecrit manifeste et overrides ; une
        erreur sur une source annule tout (rien n'est ecrit). Renvoie la grille."""
        with samples_lock:
            m = manifest()
            try:
                overrides = samples.load_overrides(samples_overrides)
                for src in dict.fromkeys(sources):
                    op(m, overrides, src)
            except SampleError as exc:
                raise HTTPException(status_code, str(exc)) from exc
            samples.save_manifest(m, samples_manifest)
            samples.save_overrides(overrides, samples_overrides)
        return _sample_cells(m)

    @app.post("/api/samples/status", response_model=list[SampleCell])
    def sample_status(req: SampleDecision) -> list[SampleCell]:
        """Decision d'ecoute ; la selection des cases est recalculee. Un fichier
        de la reserve devient d'abord candidat (7.J5)."""
        def op(m: samples.Manifest, ov: dict[str, Override], src: str) -> None:
            promote(m, ov, src, samples_src)
            set_status(m, src, req.status)
        return edit(req.sources, op)

    @app.post("/api/samples/move", response_model=list[SampleCell])
    def sample_move(req: SampleMove) -> list[SampleCell]:
        """Range des candidats ou des non classes dans une case (statut garde)
        et l'inscrit dans overrides.json."""
        return edit(req.sources, lambda m, ov, src: move_sample(
            m, ov, src, req.code, req.sub, samples_src), status_code=422)

    @app.post("/api/samples/stars", response_model=list[SampleCell])
    def sample_stars(req: SampleStars) -> list[SampleCell]:
        def op(m: samples.Manifest, ov: dict[str, Override], src: str) -> None:
            if req.stars is not None:
                promote(m, ov, src, samples_src)
            set_stars(m, ov, src, req.stars)
        return edit(req.sources, op)

    @app.post("/api/samples/tags", response_model=list[SampleCell])
    def sample_tags_edit(req: SampleTags) -> list[SampleCell]:
        return edit(req.sources, lambda m, ov, src: set_tags(m, ov, src, req.add, req.remove))

    @app.post("/api/samples/trash", response_model=list[SampleCell])
    def sample_trash(req: SampleBatch) -> list[SampleCell]:
        return edit(req.sources, trash_sample)

    @app.post("/api/samples/restore", response_model=list[SampleCell])
    def sample_restore(req: SampleBatch) -> list[SampleCell]:
        return edit(req.sources, lambda m, ov, src: restore_sample(m, ov, src, samples_src))

    def kit_edit(kit: str, rebuild: Callable[..., samples.Manifest]) -> list[SampleCell]:
        """Corbeille / restauration d'un kit : regle dans overrides.json puis
        reconstruction du manifeste (mesure des nouveaux candidats)."""
        media_or_503()
        with samples_lock:
            overrides = samples.load_overrides(samples_overrides)
            try:
                m = rebuild(manifest(), overrides, kit, samples_src)
            except SampleError as exc:
                raise HTTPException(422, str(exc)) from exc
            samples.save_manifest(m, samples_manifest)
            samples.save_overrides(overrides, samples_overrides)
        return _sample_cells(m)

    @app.post("/api/samples/kit/trash", response_model=list[SampleCell])
    def sample_kit_trash(req: SampleKit) -> list[SampleCell]:
        return kit_edit(req.kit, trash_kit)

    @app.post("/api/samples/kit/restore", response_model=list[SampleCell])
    def sample_kit_restore(req: SampleKit) -> list[SampleCell]:
        return kit_edit(req.kit, restore_kit)

    @app.post("/api/samples/kit/tags", response_model=list[SampleCell])
    def sample_kit_tags(req: SampleKitTags) -> list[SampleCell]:
        """Tags d'un kit ou d'un pack, herites par tous ses fichiers."""
        with samples_lock:
            m = manifest()
            overrides = samples.load_overrides(samples_overrides)
            try:
                set_kit_tags(m, overrides, req.kit, req.add, req.remove)
            except SampleError as exc:
                raise HTTPException(422, str(exc)) from exc
            samples.save_manifest(m, samples_manifest)
            samples.save_overrides(overrides, samples_overrides)
        return _sample_cells(m)

    def media_or_503() -> None:
        if samples_src == SAMPLES_SRC_DIR:
            try:
                require_media()
            except MediaRootUnavailable as exc:
                raise HTTPException(503, str(exc)) from exc

    @app.post("/api/samples/export", response_model=ExportReport)
    def sample_export(req: SampleExport) -> ExportReport:
        """Copie les retenus vers l'arborescence Transfer (7.J3) ; `dry_run` : bilan."""
        media_or_503()
        with samples_lock:
            try:
                return export(manifest(), samples_src, samples_export, samples_export_index,
                              dry_run=req.dry_run)
            except SampleError as exc:
                raise HTTPException(422, str(exc)) from exc

    @app.get("/api/samples/audio")
    def sample_audio(source: str) -> FileResponse:
        if not known(manifest(), source):
            raise HTTPException(404, f"sample hors manifeste : {source}")
        media_or_503()
        path = samples_src / source
        if not path.is_file():
            raise HTTPException(404, f"fichier absent : {source}")
        return FileResponse(path, media_type="audio/wav")

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

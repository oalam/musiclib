"""Jobs d'acquisition lances depuis le front (Phase 7.I).

Un seul worker : les jobs s'executent l'un apres l'autre (les suivants
attendent en `queued`), ce qui serialise les ecritures de library.md. L'etat
vit en memoire (perdu au redemarrage d'api.py) ; le front le suit par polling.

Pipeline d'un job : ingest (metadata, telechargement, bpm/key, library.md)
-> analyse complete (sidecar + visuel) -> stems Demucs (option) -> bank
Digitakt + harmonie (option). Les etapes sont annoncees des la creation.
"""
from __future__ import annotations

import threading
import uuid
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

Status = Literal["queued", "running", "done", "error", "skipped"]


class GrabRequest(BaseModel):
    url: str
    analyze_quality: bool = True
    stems: bool = False
    bank: bool = False
    folder: str | None = None


class JobStep(BaseModel):
    name: str
    label: str
    status: Status = "queued"
    detail: str = ""


class Job(BaseModel):
    id: str
    request: GrabRequest
    status: Status = "queued"
    steps: list[JobStep]
    slug: str | None = None
    created: bool | None = None  # True = nouvelle entree de library.md
    error: str = ""
    created_at: str
    finished_at: str | None = None


class StepFailed(Exception):
    """Une etape a echoue ; le message est remonte au front."""


STEP_LABELS: dict[str, str] = {
    "metadata": "Metadata de la source",
    "download": "Telechargement",
    "bpm_key": "BPM / tonalite",
    "library": "Entree library.md",
    "quality": "Analyse complete + visuel",
    "stems": "Stems Demucs",
    "bank": "Bank Digitakt",
    "harmony": "Harmonie",
}


def planned_steps(req: GrabRequest) -> list[str]:
    steps = ["metadata", "download", "bpm_key", "library"]
    if req.analyze_quality:
        steps.append("quality")
    if req.stems:
        steps.append("stems")
    if req.bank:
        steps += ["bank", "harmony"]
    return steps


class JobContext:
    """Passe au runner : demarre les etapes et ferme la precedente."""

    def __init__(self, job: Job, lock: threading.Lock) -> None:
        self._job = job
        self._lock = lock
        self._current: JobStep | None = None

    def step(self, name: str) -> None:
        with self._lock:
            if self._current is not None:
                self._current.status = "done"
            target = next((s for s in self._job.steps if s.name == name), None)
            if target is None:  # etape non prevue (ex. re-resolution d'URL)
                target = JobStep(name=name, label=STEP_LABELS.get(name, name))
                self._job.steps.append(target)
            # les etapes sautees entre la precedente et celle-ci (fichier deja
            # present, BPM force...) passent en `skipped`
            idx = self._job.steps.index(target)
            for s in self._job.steps[:idx]:
                if s.status == "queued":
                    s.status = "skipped"
            target.status = "running"
            self._current = target

    def set_slug(self, slug: str, created: bool) -> None:
        with self._lock:
            self._job.slug = slug
            self._job.created = created

    def fail(self, message: str) -> None:
        with self._lock:
            if self._current is not None:
                self._current.status = "error"
                self._current.detail = message

    def finish(self) -> None:
        with self._lock:
            if self._current is not None:
                self._current.status = "done"
            for s in self._job.steps:
                if s.status == "queued":
                    s.status = "skipped"


Runner = Callable[[GrabRequest, JobContext], None]


class JobStore:
    def __init__(self, runner: Runner) -> None:
        self._runner = runner
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()
        self._pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="grab")

    def submit(self, req: GrabRequest) -> Job:
        job = Job(
            id=uuid.uuid4().hex[:12], request=req,
            steps=[JobStep(name=n, label=STEP_LABELS[n]) for n in planned_steps(req)],
            created_at=datetime.now().isoformat(timespec="seconds"),
        )
        with self._lock:
            self._jobs[job.id] = job
        self._pool.submit(self._run, job)
        return self.get(job.id) or job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return job.model_copy(deep=True) if job else None

    def _run(self, job: Job) -> None:
        ctx = JobContext(job, self._lock)
        with self._lock:
            job.status = "running"
        try:
            self._runner(job.request, ctx)
        except Exception as exc:  # noqa: BLE001 -- tout echec est remonte au front
            message = str(exc) or type(exc).__name__
            ctx.fail(message)
            with self._lock:
                job.status = "error"
                job.error = message
        else:
            ctx.finish()
            with self._lock:
                job.status = "done"
        finally:
            with self._lock:
                job.finished_at = datetime.now().isoformat(timespec="seconds")

    def shutdown(self) -> None:
        self._pool.shutdown(wait=False, cancel_futures=True)

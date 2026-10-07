"""Tests de la file de jobs 7.I (scripts/jobs.py), runner factice.

Lancer (depuis scripts/) :
    python -m pytest tests/test_jobs.py
"""
from __future__ import annotations

import threading
import time

import pytest

from jobs import GrabRequest, Job, JobContext, JobStore, StepFailed, planned_steps


def _wait(store: JobStore, job_id: str, timeout: float = 2.0) -> Job:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        job = store.get(job_id)
        assert job is not None
        if job.status in ("done", "error"):
            return job
        time.sleep(0.01)
    raise AssertionError("job non termine")


def test_planned_steps_selon_options():
    base = ["metadata", "download", "bpm_key", "library"]
    assert planned_steps(GrabRequest(url="u", analyze_quality=False)) == base
    assert planned_steps(GrabRequest(url="u", stems=True, bank=True)) == [
        *base, "quality", "stems", "bank", "harmony"]


def test_job_reussi_etapes_et_sautees():
    def runner(req: GrabRequest, ctx: JobContext) -> None:
        ctx.step("metadata")
        ctx.step("bpm_key")  # fichier deja present : pas de telechargement
        ctx.step("library")
        ctx.set_slug("a_-_b", created=False)
        ctx.step("quality")

    store = JobStore(runner)
    job = _wait(store, store.submit(GrabRequest(url="https://x")).id)
    assert job.status == "done" and job.slug == "a_-_b" and job.created is False
    assert {s.name: s.status for s in job.steps} == {
        "metadata": "done", "download": "skipped", "bpm_key": "done",
        "library": "done", "quality": "done"}
    assert job.finished_at


def test_job_en_echec_remonte_l_etape():
    def runner(req: GrabRequest, ctx: JobContext) -> None:
        ctx.step("metadata")
        raise StepFailed("yt-dlp 403")

    store = JobStore(runner)
    job = _wait(store, store.submit(GrabRequest(url="https://x", analyze_quality=False)).id)
    assert job.status == "error" and job.error == "yt-dlp 403"
    assert job.steps[0].status == "error" and job.steps[0].detail == "yt-dlp 403"
    assert {s.status for s in job.steps[1:]} == {"queued"}


def test_jobs_serialises():
    release = threading.Event()
    running: list[int] = []
    peak = [0]

    def runner(req: GrabRequest, ctx: JobContext) -> None:
        running.append(1)
        peak[0] = max(peak[0], len(running))
        release.wait(1)
        running.pop()

    store = JobStore(runner)
    first = store.submit(GrabRequest(url="https://a"))
    second = store.submit(GrabRequest(url="https://b"))
    time.sleep(0.05)
    current = store.get(second.id)
    assert current is not None and current.status == "queued"
    release.set()
    assert _wait(store, first.id).status == "done"
    assert _wait(store, second.id).status == "done"
    assert peak[0] == 1


def test_get_renvoie_une_copie():
    store = JobStore(lambda req, ctx: None)
    job = store.submit(GrabRequest(url="https://x"))
    job.status = "error"
    assert _wait(store, job.id).status == "done"


@pytest.mark.parametrize("unknown", ["nope"])
def test_get_inconnu(unknown: str):
    assert JobStore(lambda req, ctx: None).get(unknown) is None

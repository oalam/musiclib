from __future__ import annotations

from pathlib import Path

import pytest

from mk_brain.boot import COMMIT_ENV, in_service, mark_ready, poweroff, read_sync


def test_mark_ready_keeps_commit_and_clears_fails(tmp_path: Path) -> None:
    (tmp_path / "fails").write_text("2\n")
    assert mark_ready(tmp_path, "abc123")
    assert (tmp_path / "last_good").read_text() == "abc123\n"
    assert not (tmp_path / "fails").exists()


def test_mark_ready_outside_service_writes_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(COMMIT_ENV, raising=False)
    assert not mark_ready(tmp_path)
    assert not (tmp_path / "last_good").exists()


def test_mark_ready_reads_commit_from_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(COMMIT_ENV, "def456")
    assert mark_ready(tmp_path)
    assert (tmp_path / "last_good").read_text() == "def456\n"


def test_read_sync(tmp_path: Path) -> None:
    assert read_sync(tmp_path / "absent") == ""
    (tmp_path / "sync").write_text("offline 2026-11-08\n")
    assert read_sync(tmp_path / "sync") == "offline 2026-11-08"


def test_in_service_follows_commit_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(COMMIT_ENV, raising=False)
    assert not in_service()
    monkeypatch.setenv(COMMIT_ENV, "a1b2c3d")
    assert in_service()


def test_poweroff_reports_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **kwargs: object) -> None:
        calls.append(cmd)
        raise OSError("sudo absent")

    monkeypatch.setattr("mk_brain.boot.subprocess.run", fake_run)
    assert not poweroff()
    assert calls == [["sudo", "systemctl", "poweroff"]]

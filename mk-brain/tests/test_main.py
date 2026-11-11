from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

from mk_brain import main as cli
from mk_brain.boot import EXIT_ERROR, EXIT_NO_HARDWARE
from mk_brain.hid_mk2 import Mk2NotFoundError, Mk2OpenError
from mk_brain.midi_io import MidiError, MidiPortNotFoundError

STOPPED_SH = Path(__file__).resolve().parents[1] / "deploy" / "stopped.sh"


def _play_raising(monkeypatch: pytest.MonkeyPatch, exc: Exception) -> int:
    def cmd_play(dry_run: bool, project_path: Path | None) -> int:
        raise exc

    monkeypatch.setattr(cli, "cmd_play", cmd_play)
    return cli.main(["play"])


@pytest.mark.parametrize(
    "exc", [Mk2NotFoundError("pas de MK2"), MidiPortNotFoundError("pas de DT2")]
)
def test_missing_hardware_has_its_own_exit_code(
    monkeypatch: pytest.MonkeyPatch, exc: Exception
) -> None:
    assert _play_raising(monkeypatch, exc) == EXIT_NO_HARDWARE


@pytest.mark.parametrize("exc", [Mk2OpenError("tenue"), MidiError("backend")])
def test_other_errors_keep_the_error_code(monkeypatch: pytest.MonkeyPatch, exc: Exception) -> None:
    assert _play_raising(monkeypatch, exc) == EXIT_ERROR


def _stopped(tmp_path: Path, result: str, code: str, status: str) -> str | None:
    """Lance une copie de deploy/stopped.sh ; rend le contenu de state/fails."""
    deploy = tmp_path / "deploy"
    deploy.mkdir(exist_ok=True)
    shutil.copy(STOPPED_SH, deploy / "stopped.sh")
    env = {**os.environ, "SERVICE_RESULT": result, "EXIT_CODE": code, "EXIT_STATUS": status}
    subprocess.run(["sh", str(deploy / "stopped.sh")], env=env, check=True)
    fails = tmp_path / "state" / "fails"
    return fails.read_text().strip() if fails.exists() else None


def test_stopped_counts_code_failures(tmp_path: Path) -> None:
    assert _stopped(tmp_path, "exit-code", "exited", str(EXIT_ERROR)) == "1"
    assert _stopped(tmp_path, "signal", "killed", "SEGV") == "2"


def test_stopped_ignores_success_and_missing_hardware(tmp_path: Path) -> None:
    assert _stopped(tmp_path, "success", "exited", "0") is None
    assert _stopped(tmp_path, "exit-code", "exited", str(EXIT_NO_HARDWARE)) is None

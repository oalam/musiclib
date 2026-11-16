from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path

import pytest

from mk_brain.state_sync import (
    BASE,
    Stamp,
    SyncError,
    decide,
    local_listing,
    parse_listing,
    sync_state,
)

SESSION = "session-solaris.json"


class FakePi:
    """Le Pi joué par un dossier."""

    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.down = False
        self.running = True

    def listing(self) -> dict[str, Stamp]:
        if self.down:
            raise SyncError("injoignable")
        self.running = False
        return local_listing(self.directory)

    def release(self) -> None:
        self.running = True

    def push(self, source: Path, name: str) -> None:
        shutil.copy2(source, self.directory / name)

    def pull(self, name: str, target: Path) -> None:
        shutil.copy2(self.directory / name, target)


@pytest.fixture
def mac(tmp_path: Path) -> Path:
    path = tmp_path / "mac"
    path.mkdir()
    return path


@pytest.fixture
def pi(tmp_path: Path) -> FakePi:
    path = tmp_path / "pi"
    path.mkdir()
    return FakePi(path)


def write(path: Path, text: str, mtime: int = 1000) -> None:
    path.write_text(text, encoding="utf-8")
    os.utime(path, (mtime, mtime))


def test_a_file_missing_on_one_side_is_copied(mac: Path, pi: FakePi) -> None:
    write(mac / SESSION, "mac")
    write(pi.directory / "arp-presets.json", "pi")
    assert sync_state(pi, mac) == ["arp-presets.json : Pi -> Mac", f"{SESSION} : Mac -> Pi"]
    assert (pi.directory / SESSION).read_text() == "mac"
    assert (mac / "arp-presets.json").read_text() == "pi"
    assert sync_state(pi, mac) == []  # plus rien à copier
    assert pi.running  # service relancé


def test_service_restarts_even_if_a_copy_fails(
    mac: Path, pi: FakePi, monkeypatch: pytest.MonkeyPatch
) -> None:
    def broken(source: Path, name: str) -> None:
        raise SyncError("scp")

    write(mac / SESSION, "mac")
    monkeypatch.setattr(pi, "push", broken)
    with pytest.raises(SyncError):
        sync_state(pi, mac)
    assert pi.running


def test_only_the_changed_side_wins_whatever_the_dates(mac: Path, pi: FakePi) -> None:
    write(mac / SESSION, "v1")
    sync_state(pi, mac)
    # live sur le Pi, hors ligne : son horloge retarde, sa date est plus ancienne
    write(pi.directory / SESSION, "live", mtime=10)
    assert sync_state(pi, mac) == [f"{SESSION} : Pi -> Mac"]
    assert (mac / SESSION).read_text() == "live"
    write(mac / SESSION, "travail", mtime=5)
    assert sync_state(pi, mac) == [f"{SESSION} : Mac -> Pi"]
    assert (pi.directory / SESSION).read_text() == "travail"


def test_conflict_the_newest_whole_file_wins(mac: Path, pi: FakePi) -> None:
    write(mac / SESSION, "v1")
    sync_state(pi, mac)
    write(mac / SESSION, "mac", mtime=2000)
    write(pi.directory / SESSION, "pi", mtime=3000)
    (line,) = sync_state(pi, mac)
    assert line.startswith(f"{SESSION} : Pi -> Mac (modifié des deux côtés")
    assert (mac / SESSION).read_text() == "pi"


def test_other_state_files_never_travel(mac: Path, pi: FakePi) -> None:
    for name in ("last_good", "fails", "last_project", BASE, "session-x.tmp"):
        write(mac / name, "local")
        write(pi.directory / name, "pi")
    assert sync_state(pi, mac) == []
    assert (pi.directory / "last_good").read_text() == "pi"
    assert (mac / "last_project").read_text() == "local"


def test_unreachable_pi_raises_and_touches_nothing(mac: Path, pi: FakePi) -> None:
    write(mac / SESSION, "mac")
    pi.down = True
    with pytest.raises(SyncError):
        sync_state(pi, mac)
    assert not (mac / BASE).exists()


def test_decide() -> None:
    a, b = Stamp("a", 1), Stamp("b", 1)
    assert decide(a, a, None) == ("", False)
    assert decide(None, None, None) == ("", False)
    assert decide(a, None, "a") == ("push", False)
    assert decide(None, b, None) == ("pull", False)
    assert decide(a, b, None) == ("push", True)  # jamais synchronisés, dates égales : le Mac


def test_parse_listing_keeps_expected_names_only() -> None:
    digest = hashlib.sha256(b"x").hexdigest()
    text = (
        f"{digest} 12 {SESSION}\n{digest} 12 ../../etc/passwd\n{digest} x arp-presets.json\nbruit"
    )
    assert parse_listing(text) == {SESSION: Stamp(digest, 12)}


def test_copies_are_reported_even_if_the_service_does_not_restart(
    mac: Path, pi: FakePi, monkeypatch: pytest.MonkeyPatch
) -> None:
    def stuck() -> None:
        raise SyncError("délai dépassé")

    write(mac / SESSION, "mac")
    monkeypatch.setattr(pi, "release", stuck)
    assert sync_state(pi, mac) == [
        f"{SESSION} : Mac -> Pi",
        "service du Pi non relancé (délai dépassé)",
    ]

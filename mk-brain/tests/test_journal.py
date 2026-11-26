from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from mk_brain.journal import (
    JOURNAL,
    Header,
    Journal,
    encode,
    free_gb,
    load_armed,
    open_journal,
    read_journal,
    save_armed,
    session_dir,
)

HEADER = Header(project="solaris", version="0.51.0", commit="abc", date="2026-11-26T21:30:00")


def test_encode_gives_bar_and_tick_from_ticks() -> None:
    line = json.loads(encode(5, "mute", 96 * 40 + 12, {"track": 9, "on": True, "src": "mk2"}))
    assert line == {
        "t_ns": 5, "kind": "mute", "bar": 41, "tick": 12, "track": 9, "on": True, "src": "mk2",
    }  # fmt: skip
    stopped = json.loads(encode(5, "cc", None, {"track": 1}))
    assert stopped["bar"] is None and stopped["tick"] is None


def test_journal_writes_header_then_events_in_order(tmp_path: Path) -> None:
    stamps = iter(range(100))
    journal = Journal(tmp_path / "s", HEADER, flush_s=0.01, now=lambda: next(stamps))
    journal.write("transport", None, {"action": "start"})
    journal.write("note", 97, {"track": 1, "note": 60, "vel": 100, "src": "arp"})
    journal.close()
    assert not journal.failed
    lines = read_journal(tmp_path / "s" / JOURNAL)
    assert [line.kind for line in lines] == ["session", "transport", "note"]
    assert [line.t_ns for line in lines] == [0, 1, 2]
    assert lines[0].model_extra == HEADER.model_dump()
    assert (lines[2].bar, lines[2].tick) == (2, 1)


def test_journal_survives_unwritable_directory(tmp_path: Path) -> None:
    blocker = tmp_path / "file"
    blocker.write_text("pas un dossier")
    journal = Journal(blocker / "s", HEADER, flush_s=0.01)
    journal.write("cc", 0, {"track": 1})  # ne lève pas : le jeu continue
    journal.close()
    assert journal.failed


def test_read_journal_skips_a_cut_last_line(tmp_path: Path) -> None:
    path = tmp_path / JOURNAL
    path.write_text(encode(1, "bar", 0, {"n": 1}) + '\n{"t_ns": 2, "kind": "ba')
    assert [line.kind for line in read_journal(path)] == ["bar"]


def test_session_dir_is_dated_and_never_reused(tmp_path: Path) -> None:
    when = datetime(2026, 11, 26, 21, 30)
    first = session_dir("solaris", when, tmp_path)
    assert first.name == "2026-11-26-2130-solaris"
    first.mkdir()
    assert session_dir("solaris", when, tmp_path).name == "2026-11-26-2130-solaris-2"


def test_open_journal_writes_the_session_header(tmp_path: Path) -> None:
    journal = open_journal("solaris", "0.51.0", tmp_path, datetime(2026, 11, 26, 21, 30))
    journal.close()
    (line,) = read_journal(journal.directory / JOURNAL)
    extra = line.model_extra or {}
    assert line.kind == "session" and extra["project"] == "solaris"
    assert extra["version"] == "0.51.0" and extra["date"] == "2026-11-26T21:30:00"


def test_armed_projects_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "state" / "rec-sessions.json"
    assert load_armed(path) == set()
    save_armed({"solaris", "bal"}, path)
    assert load_armed(path) == {"solaris", "bal"}
    path.write_text("illisible")
    assert load_armed(path) == set()


def test_free_gb_reads_the_nearest_existing_parent(tmp_path: Path) -> None:
    free = free_gb(tmp_path / "absent" / "encore")
    assert free is not None and free > 0

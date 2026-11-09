from __future__ import annotations

from pathlib import Path

from mk_brain.project import DEFAULT_PROJECT
from mk_brain.selection import Selector, list_projects, read_last, write_last


def _projects(tmp_path: Path) -> Path:
    (tmp_path / "solaris.yaml").write_text(DEFAULT_PROJECT.read_text(encoding="utf-8"))
    (tmp_path / "broken.yaml").write_text("name: broken\nbanks: {Z: {}}\n")
    return tmp_path


def test_list_projects_marks_invalid_and_dates(tmp_path: Path) -> None:
    entries = list_projects(_projects(tmp_path))
    assert [e.name for e in entries] == ["broken", "solaris"]
    broken, solaris = entries
    assert broken.project is None and broken.error and broken.banks == 0
    assert solaris.project is not None and solaris.banks == 7
    assert len(solaris.date) == 10  # hors git : date de modification


def test_last_played_preselected_and_scroll_bounded(tmp_path: Path) -> None:
    entries = list_projects(_projects(tmp_path))
    sel = Selector(entries, "solaris")
    assert sel.current is not None and sel.current.name == "solaris"
    sel.scroll(5)
    assert sel.index == 1
    sel.scroll(-9)
    assert sel.index == 0
    assert Selector(entries, "unknown").index == 0
    assert Selector([], None).current is None


def test_last_project_round_trip(tmp_path: Path) -> None:
    state = tmp_path / "state" / "last_project"
    assert read_last(state) is None
    write_last("solaris", state)
    assert read_last(state) == "solaris"

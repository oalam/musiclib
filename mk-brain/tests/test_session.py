from __future__ import annotations

from pathlib import Path

from mk_brain.session import FaderValue, Session, load_session, save_session


def test_save_then_load_round_trip(tmp_path: Path) -> None:
    s = Session(
        design_bank=4, program=67, track=3, faders=[FaderValue(track=3, param=74, value=90)]
    )
    save_session("solaris", s, tmp_path)
    assert load_session("solaris", tmp_path) == s
    assert not list(tmp_path.glob("*.tmp"))  # écriture atomique, rien ne traîne


def test_missing_or_invalid_session_is_none(tmp_path: Path) -> None:
    assert load_session("solaris", tmp_path) is None
    (tmp_path / "session-solaris.json").write_text('{"track": 42}')
    assert load_session("solaris", tmp_path) is None

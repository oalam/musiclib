"""Hub de chemins vault / disque media (paths.py) + choix de format dans grab."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import grab  # noqa: E402
import paths  # noqa: E402


@pytest.fixture
def media(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    mix = tmp_path / "Mix"
    (mix / "audio" / "swing").mkdir(parents=True)
    monkeypatch.setattr(paths, "MIX_DIR", mix)
    monkeypatch.setattr(paths, "MEDIA_MARKER", tmp_path / ".music-media")
    return tmp_path


def test_resolve_audio_relative_to_mix(media: Path) -> None:
    f = media / "Mix" / "audio" / "swing" / "a_-_b.flac"
    f.write_bytes(b"")
    assert paths.resolve_audio({"file": "[[audio/swing/a_-_b.flac]]"}) == f


def test_resolve_audio_missing_or_malformed(media: Path) -> None:
    assert paths.resolve_audio({"file": "[[audio/absent.flac]]"}) is None
    assert paths.resolve_audio({"file": ""}) is None


def test_mix_relative(media: Path) -> None:
    f = media / "Mix" / "audio" / "x.flac"
    assert paths.mix_relative(f) == "audio/x.flac"
    assert paths.mix_relative(Path("/ailleurs/x.flac")) == "/ailleurs/x.flac"


def test_require_media_needs_marker(media: Path) -> None:
    with pytest.raises(paths.MediaRootUnavailable):
        paths.require_media()
    assert paths.media_ok() is False
    (media / ".music-media").touch()
    assert paths.media_ok() is True


@pytest.mark.parametrize(("codec", "expected"), [
    ("opus", ".flac"), ("vorbis", ".flac"), ("flac", ".flac"),
    ("mp4a.40.2", ".m4a"), ("mp3", ".mp3"),
])
def test_download_targets_rekordbox_formats(
    codec: str, expected: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []

    def fake_call(cmd: list[str]) -> int:
        calls.append(cmd)
        (tmp_path / f"t{expected}").write_bytes(b"")
        return 0

    monkeypatch.setattr(grab.subprocess, "check_call", fake_call)
    cand = grab.Candidate(source="youtube", url="https://example.invalid/x",
                          title="t", info={}, fmt={"acodec": codec})
    out = grab.download_candidate(cand, tmp_path / "t")
    assert out.suffix == expected
    assert ("--audio-format" in calls[0]) is (expected == ".flac")

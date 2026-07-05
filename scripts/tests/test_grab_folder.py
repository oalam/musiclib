"""Tests unitaires du rangement par style de grab.py.

Aucun reseau requis : tout est pur (deduce_folder) ou sur tmp_path
(existing_audio avec AUDIO_DIR monkeypatche).

Lancer (depuis scripts/) :
    python -m pytest tests/test_grab_folder.py
"""
from __future__ import annotations

import grab


# ---------------------------------------------------------------------------
# deduce_folder
# ---------------------------------------------------------------------------

def test_folder_explicite_prime_sur_genre():
    assert grab.deduce_folder("swing", ["Tango"]) == "swing"


def test_folder_deduit_du_premier_genre_slugifie():
    assert grab.deduce_folder(None, ["Rock & Roll", "Oldies"]) == "rock_roll"


def test_folder_none_sans_genre():
    assert grab.deduce_folder(None, []) is None


# ---------------------------------------------------------------------------
# existing_audio (recherche recursive dans les sous-dossiers)
# ---------------------------------------------------------------------------

def _patch_audio_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(grab, "AUDIO_DIR", tmp_path)


def test_existing_audio_racine(monkeypatch, tmp_path):
    _patch_audio_dir(monkeypatch, tmp_path)
    f = tmp_path / "artist_-_title.opus"
    f.touch()
    assert grab.existing_audio("artist_-_title") == f


def test_existing_audio_sous_dossier(monkeypatch, tmp_path):
    _patch_audio_dir(monkeypatch, tmp_path)
    sub = tmp_path / "swing"
    sub.mkdir()
    f = sub / "artist_-_title.flac"
    f.touch()
    assert grab.existing_audio("artist_-_title") == f


def test_existing_audio_ignore_extensions_inconnues(monkeypatch, tmp_path):
    _patch_audio_dir(monkeypatch, tmp_path)
    sub = tmp_path / "swing"
    sub.mkdir()
    (sub / "artist_-_title.json").touch()
    assert grab.existing_audio("artist_-_title") is None


def test_existing_audio_absent(monkeypatch, tmp_path):
    _patch_audio_dir(monkeypatch, tmp_path)
    assert grab.existing_audio("artist_-_title") is None

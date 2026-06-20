"""Tests unitaires de l'extraction Spotify de grab.py.

Aucun reseau requis : urlopen est mocke par une page embed synthetique.

Lancer (depuis scripts/) :
    python -m pytest tests/test_grab_spotify.py
"""
from __future__ import annotations

import io
import json
from contextlib import contextmanager

import grab


def _embed_html(name: str, tracks: list[tuple[str, str]], kind: str = "playlist") -> str:
    """Construit une page embed Spotify minimale (subtitle=artistes, title=titre)."""
    entity: dict = {
        "type": kind,
        "name": name,
        "trackList": [{"subtitle": a, "title": t} for a, t in tracks],
    }
    data = {"props": {"pageProps": {"state": {"data": {"entity": entity}}}}}
    blob = json.dumps(data)
    return (
        f'<html><body><script id="__NEXT_DATA__" type="application/json">'
        f"{blob}</script></body></html>"
    )


@contextmanager
def _fake_urlopen(html: str):
    """Patch grab.urllib.request.urlopen pour renvoyer `html`."""
    orig = grab.urllib.request.urlopen

    def fake(_req, timeout=0):  # noqa: ANN001
        return io.BytesIO(html.encode())

    grab.urllib.request.urlopen = fake
    try:
        yield
    finally:
        grab.urllib.request.urlopen = orig


def test_is_spotify_detects_url_and_uri_forms():
    assert grab.is_spotify("https://open.spotify.com/playlist/69CWyZkHWDzKXc8u6f1POR")
    assert grab.is_spotify("https://open.spotify.com/track/abc123")
    assert grab.is_spotify("spotify:album:xyz789")
    assert not grab.is_spotify("https://youtube.com/watch?v=abc")
    assert not grab.is_spotify("RVDE 90s Hammer")


def test_spotify_queries_builds_artist_title():
    html = _embed_html(
        "ma playlist",
        [("Sevdaliza, Pabllo Vittar", "Alibi"), ("Fantomel, Kate Linn", "Dame Un Grrr")],
    )
    with _fake_urlopen(html):
        queries = grab.spotify_queries(
            "https://open.spotify.com/playlist/69CWyZkHWDzKXc8u6f1POR"
        )
    assert queries == [
        "Sevdaliza, Pabllo Vittar Alibi",
        "Fantomel, Kate Linn Dame Un Grrr",
    ]


def test_spotify_queries_skips_empty_title():
    html = _embed_html("p", [("Artiste", ""), ("Autre", "Titre")])
    with _fake_urlopen(html):
        queries = grab.spotify_queries("spotify:playlist:abc")
    assert queries == ["Autre Titre"]


def test_spotify_queries_title_without_artist():
    html = _embed_html("p", [("", "Solo Titre")])
    with _fake_urlopen(html):
        queries = grab.spotify_queries("https://open.spotify.com/playlist/abc")
    assert queries == ["Solo Titre"]


def test_spotify_queries_single_track_url():
    """Une URL de track isolee (entity.type == 'track', pas de trackList)."""
    entity = {"type": "track", "subtitle": "RVDE", "title": "90s Hammer", "trackList": []}
    data = {"props": {"pageProps": {"state": {"data": {"entity": entity}}}}}
    html = (
        '<script id="__NEXT_DATA__" type="application/json">'
        f"{json.dumps(data)}</script>"
    )
    with _fake_urlopen(html):
        queries = grab.spotify_queries("https://open.spotify.com/track/xyz")
    assert queries == ["RVDE 90s Hammer"]


def test_spotify_queries_non_spotify_url_returns_empty():
    assert grab.spotify_queries("https://youtube.com/watch?v=abc") == []

"""Description courte d'artiste via l'API publique MusicBrainz.

Lookup `Artist name` → infos structurees (pays, tags genres, type).
Cache local dans `library/artists/<slug>.json` pour eviter le rate-limit
(MusicBrainz autorise ~1 req/sec). User-Agent identifie comme requis
par leur politique.
"""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from library_md import slugify

_USER_AGENT = "oalam-music/1.0 (https://github.com/oalam ; bailet.thomas@gmail.com)"
_MB_ENDPOINT = "https://musicbrainz.org/ws/2/artist"
_RATE_LIMIT_S = 1.1  # MB demande max 1 req/sec, on prend marge

# Splitter pour extraire le premier artiste dans une chaine multi-artistes
_PRIMARY_SEPS = (
    " feat. ", " ft. ", " featuring ", " vs ", " vs. ",
    " x ", " & ", ", ",
)


def primary_artist(artist_str: str) -> str:
    """Extrait le 1er artiste d'une chaine 'A & B', 'A feat. B', etc."""
    s = artist_str.strip()
    for sep in _PRIMARY_SEPS:
        if sep in s:
            return s.split(sep, 1)[0].strip()
    return s


def _country_code_to_name(code: str | None) -> str | None:
    """Quelques pays courants. Pour le reste on retourne le code."""
    if not code:
        return None
    common = {
        "FR": "FR", "US": "US", "GB": "UK", "DE": "DE", "NL": "NL",
        "BE": "BE", "JP": "JP", "CO": "Colombia", "BR": "Brazil",
        "AR": "Argentina", "MX": "Mexico", "ES": "ES", "IT": "IT",
        "CA": "CA", "AU": "AU", "JM": "Jamaica", "ZA": "South Africa",
    }
    return common.get(code, code)


def fetch_mb_artist(
    name: str,
    cache_dir: Path,
    rate_limit: bool = True,
) -> dict[str, Any] | None:
    """Cherche un artiste sur MusicBrainz, cache le resultat. None si echec."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"{slugify(name)}.json"
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass

    params = {
        "fmt": "json",
        "limit": "5",
        "query": name,
    }
    url = f"{_MB_ENDPOINT}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as exc:
        cache_path.write_text(json.dumps({
            "_error": str(exc), "_queried": name,
        }), encoding="utf-8")
        if rate_limit:
            time.sleep(_RATE_LIMIT_S)
        return None

    artists = data.get("artists") or []
    if not artists:
        cache_path.write_text(json.dumps({
            "_no_match": True, "_queried": name,
        }), encoding="utf-8")
        if rate_limit:
            time.sleep(_RATE_LIMIT_S)
        return None

    # Prend le 1er resultat (MB ordonne par pertinence/score)
    a = artists[0]
    result = {
        "id": a.get("id"),
        "name": a.get("name"),
        "sort_name": a.get("sort-name"),
        "country": a.get("country"),
        "type": a.get("type"),
        "score": a.get("score"),
        "tags": [
            t.get("name") for t in (a.get("tags") or [])
            if t.get("name") and (t.get("count") or 0) > 0
        ][:10],
        "_queried": name,
    }
    cache_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    if rate_limit:
        time.sleep(_RATE_LIMIT_S)
    return result


def compose_about(info: dict[str, Any]) -> str:
    """Format compact : '<pays>, <tag1>, <tag2>, <tag3>'.

    Vide si pas assez d'infos."""
    if "_error" in info or "_no_match" in info:
        return ""
    parts: list[str] = []
    country = _country_code_to_name(info.get("country"))
    if country:
        parts.append(country)
    tags = info.get("tags") or []
    # Garde uniquement les tags utiles (drop tags pourris type "seen live")
    blacklist = {"seen live", "favourite", "favorites", "german", "french",
                 "british", "american", "english"}
    clean_tags = [t for t in tags if t.lower() not in blacklist][:3]
    if clean_tags:
        parts.append(", ".join(clean_tags))
    return " | ".join(parts)


def describe_artist(name: str, cache_dir: Path, rate_limit: bool = True) -> str:
    """Lookup + compose. Retourne la chaine `about` ou vide."""
    info = fetch_mb_artist(primary_artist(name), cache_dir, rate_limit=rate_limit)
    if not info:
        return ""
    return compose_about(info)

#!/usr/bin/env python3
"""Telecharge un morceau en meilleure qualite disponible.

Source par URL ou par requete texte libre. Le moteur cherche les
candidats sur YouTube + SoundCloud, compare leurs codecs et debit, et
telecharge sans perte supplementaire, dans un format lu par Rekordbox :
FLAC pour le lossless et l'opus/vorbis, m4a/mp3 natifs.

Usage:
    grab.py URL [URL ...]
    grab.py "RVDE 90s Hammer Original Mix"
    grab.py https://open.spotify.com/playlist/...  # playlist Spotify -> N tracks
    grab.py --dry-run "query"        # voir le candidat retenu sans dl
    grab.py --replace URL            # ecraser un fichier deja present
    grab.py --folder swing "query"   # ranger dans <MEDIA>/Mix/audio/swing/

Rangement : chaque fichier va dans un sous-dossier de <MEDIA>/Mix/audio/ par
style. Le style vient de --folder si fourni, sinon il est deduit du genre
(--genre ou metadata de la source). Sans genre connu, le fichier reste a
la racine de <MEDIA>/Mix/audio/.

Une URL Spotify (playlist / album / track) est developpee en autant de requetes
'artiste titre' qu'elle contient de morceaux : Spotify n'autorise pas le DL audio,
on recupere seulement la tracklist puis on cherche chaque titre sur YT/SoundCloud.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel

from library_md import (
    PRESERVED_FIELDS,
    parse_library,
    slugify,
    update_field,
    write_library,
)

from paths import (
    ARTISTS_DIR,
    AUDIO_DIR,
    LIBRARY_FILE,
    MIX_DIR,
    QUALITY_DIR,
    REKORDBOX_EXTS,
    VISUALS_DIR,
    mix_relative,
    media_ok,
)

KNOWN_EXTS = (".flac", ".opus", ".m4a", ".mp3", ".ogg", ".webm")

# Options passees a chaque appel yt-dlp (ex: cookies), remplies par --cookies-from-browser.
# Debloque les videos en 403 et, avec un compte Premium, le format AAC 256k.
YTDLP_EXTRA_ARGS: list[str] = []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return bool(parsed.scheme in ("http", "https") and parsed.netloc)
    except Exception:
        return False


def detect_source(url: str) -> str:
    if "bandcamp.com" in url:
        return "bandcamp"
    if "soundcloud.com" in url:
        return "soundcloud"
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    return "unknown"


# ---------------------------------------------------------------------------
# Spotify (extraction de tracklist -> requetes texte)
# ---------------------------------------------------------------------------

# Spotify n'autorise aucun telechargement audio direct. On lit la tracklist
# (artiste + titre) d'une URL Spotify via l'endpoint `embed` public (sans auth),
# puis chaque morceau est cherche/telecharge sur YouTube/SoundCloud comme une
# requete texte ordinaire.

_SPOTIFY_URL_RE = re.compile(
    r"(?:open\.spotify\.com/(?:embed/)?|spotify:)(playlist|album|track)[/:]([A-Za-z0-9]+)"
)


def is_spotify(value: str) -> bool:
    return bool(_SPOTIFY_URL_RE.search(value))


def spotify_queries(url: str) -> list[str]:
    """Extrait les morceaux d'une URL Spotify (playlist/album/track) et retourne
    des requetes 'artiste titre' a chercher sur YouTube/SoundCloud.

    Limitation : l'endpoint embed plafonne les grosses playlists (~100 pistes) ;
    le compte affiche reflete ce qui a reellement ete extrait."""
    m = _SPOTIFY_URL_RE.search(url)
    if not m:
        return []
    kind, sid = m.group(1), m.group(2)
    embed = f"https://open.spotify.com/embed/{kind}/{sid}"
    req = urllib.request.Request(embed, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode()
    except Exception as exc:  # noqa: BLE001
        print(f"    spotify: echec recuperation ({exc})", file=sys.stderr)
        return []

    blob = re.search(
        r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S
    )
    if not blob:
        print("    spotify: tracklist introuvable (page modifiee ?)", file=sys.stderr)
        return []
    try:
        data = json.loads(blob.group(1))
        entity = data["props"]["pageProps"]["state"]["data"]["entity"]
    except (KeyError, TypeError, ValueError) as exc:
        print(f"    spotify: structure inattendue ({exc})", file=sys.stderr)
        return []

    track_list = entity.get("trackList") or []
    if not track_list and entity.get("type") == "track":
        track_list = [entity]

    queries: list[str] = []
    for t in track_list:
        title = (t.get("title") or "").strip()
        artists = (t.get("subtitle") or "").strip()
        if not title:
            continue
        queries.append(f"{artists} {title}".strip() if artists else title)
    return queries


# ---------------------------------------------------------------------------
# Query cleaning
# ---------------------------------------------------------------------------

_ALBUM_RE = re.compile(
    r"\s*(?:de\s+l[’‘']\s*(?:album|ep|single)|from\s+(?:the\s+)?album)\s+"
    r".+?(?=\s+(?:par|by)\b|$)",
    re.IGNORECASE,
)
_BY_RE = re.compile(r"\s*\b(?:par|by)\s+(.+?)\s*$", re.IGNORECASE)
# Label ou annee en queue : "[VISION]", "[2020]", "(NOMARK)"
_TRAILING_TAG_RE = re.compile(r"\s*[\[\(][^\]\)]{1,30}[\]\)]\s*$")


def clean_query(raw: str) -> str:
    """Rends une chaine libre plus search-friendly :
    - drop 'de l'album X' / 'from the album X'
    - drop label/annee final entre [...] ou (...)
    - deplace 'par X' / 'by X' en tete (artiste devant)"""
    q = _ALBUM_RE.sub("", raw)
    q = _TRAILING_TAG_RE.sub("", q)
    m = _BY_RE.search(q)
    if m:
        artist = m.group(1).strip().rstrip(",;.")
        rest = q[:m.start()].strip().rstrip(",;.")
        q = f"{artist} {rest}"
    q = re.sub(r"\s+", " ", q).strip()
    return q or raw


def expand_inputs(raw_inputs: list[str]) -> list[str]:
    """Si un argument contient des newlines, l'eclate en une entree par ligne."""
    out: list[str] = []
    for item in raw_inputs:
        if "\n" in item:
            out.extend(line.strip() for line in item.splitlines() if line.strip())
        else:
            out.append(item)
    return out


_QUOTED_TITLE_RE = re.compile(
    r"^(.+?)\s+[‘'\"“](.+?)['’\"”]\s*(?:\(.*\))?\s*$"
)


def parse_artist_title(raw_title: str) -> tuple[str | None, str | None]:
    """Heuristique fallback quand le metadata `artist` est manquant :
    - 'Artist Quotedtitle (suffix)' (YouTube label-style)
    - 'Artist - Title (suffix)'
    Retourne (None, None) si rien ne matche."""
    cleaned = re.sub(r"\s*\([^)]+\)\s*$", "", raw_title).strip()
    m = _QUOTED_TITLE_RE.match(cleaned)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    if " - " in cleaned:
        a, t = cleaned.split(" - ", 1)
        return a.strip(), t.strip()
    return None, None


# ---------------------------------------------------------------------------
# Quality model
# ---------------------------------------------------------------------------

# codec -> (storage_extension, is_lossless, perceptual_multiplier)
_CODEC_INFO: dict[str, tuple[str, bool, float]] = {
    "flac":   ("flac", True,  0.0),
    "alac":   ("flac", True,  0.0),
    "wav":    ("flac", True,  0.0),
    "pcm":    ("flac", True,  0.0),
    "opus":   ("opus", False, 1.6),
    "vorbis": ("ogg",  False, 1.3),
    "aac":    ("m4a",  False, 1.2),
    "mp4a":   ("m4a",  False, 1.2),
    "mp3":    ("mp3",  False, 1.0),
}


def codec_info(codec: str) -> tuple[str, bool, float]:
    c = (codec or "").lower()
    for key, info in _CODEC_INFO.items():
        if key in c:
            return info
    return ("opus", False, 1.0)


def quality_score(fmt: dict[str, Any]) -> float:
    codec = (fmt.get("acodec") or "").lower()
    abr = float(fmt.get("abr") or 0)
    _, lossless, mult = codec_info(codec)
    if lossless:
        return 1_000_000.0
    return abr * mult


def score_str(score: float) -> str:
    return "LOSSLESS" if score >= 1_000_000 else f"{score:.0f}"


def _tokenize(s: str) -> set[str]:
    return {t for t in re.findall(r"\w+", s.lower()) if len(t) >= 2 or t.isdigit()}


def title_match(query: str, candidate_title: str) -> float:
    """Fraction des tokens significatifs de la query presents dans le titre."""
    q = _tokenize(query)
    t = _tokenize(candidate_title)
    if not q:
        return 1.0
    return len(q & t) / len(q)


def best_audio_format(info: dict[str, Any]) -> dict[str, Any] | None:
    fmts = info.get("formats") or []
    audio_only = [
        f for f in fmts
        if f.get("vcodec") in ("none", None)
        and f.get("acodec") not in ("none", None)
    ]
    if not audio_only:
        audio_only = [f for f in fmts if f.get("acodec") not in ("none", None)]
    if not audio_only:
        return None
    return max(audio_only, key=quality_score)


# ---------------------------------------------------------------------------
# yt-dlp wrappers
# ---------------------------------------------------------------------------

def fetch_metadata(url: str) -> dict[str, Any]:
    raw = subprocess.check_output(
        ["yt-dlp", "-J", "--no-warnings", *YTDLP_EXTRA_ARGS, url],
        text=True, stderr=subprocess.PIPE,
    )
    return json.loads(raw)


def flat_search(prefix: str, query: str, n: int) -> list[dict[str, Any]]:
    search_url = f"{prefix}{n}:{query}"
    try:
        raw = subprocess.check_output(
            ["yt-dlp", "-J", "--flat-playlist", "--no-warnings",
             *YTDLP_EXTRA_ARGS, search_url],
            text=True, stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as exc:
        err = exc.stderr.strip() if exc.stderr else str(exc)
        print(f"    search {prefix} failed: {err}", file=sys.stderr)
        return []
    data = json.loads(raw)
    return [e for e in (data.get("entries") or []) if e]


def entry_url(entry: dict[str, Any], src: str) -> str | None:
    url = entry.get("webpage_url") or entry.get("url")
    if not url:
        eid = entry.get("id")
        if eid and src == "youtube":
            return f"https://www.youtube.com/watch?v={eid}"
        return None
    if url.startswith("http"):
        return url
    if src == "youtube":
        return f"https://www.youtube.com/watch?v={url}"
    return url


# ---------------------------------------------------------------------------
# Candidate model
# ---------------------------------------------------------------------------

@dataclass
class Candidate:
    source: str
    url: str
    title: str
    info: dict[str, Any]
    fmt: dict[str, Any]
    match: float = 1.0  # 0..1, pertinence textuelle vs query

    @property
    def codec(self) -> str:
        return (self.fmt.get("acodec") or "").lower()

    @property
    def abr(self) -> float:
        return float(self.fmt.get("abr") or 0)

    @property
    def quality(self) -> float:
        return quality_score(self.fmt)

    @property
    def score(self) -> float:
        """Score combine : qualite penalisee si le titre ne matche pas."""
        q = self.quality
        if self.match < 0.5:
            return q * 0.1
        return q * self.match


def resolve_candidates(query_or_url: str, search_n: int) -> list[Candidate]:
    if is_url(query_or_url):
        info = fetch_metadata(query_or_url)
        fmt = best_audio_format(info)
        if not fmt:
            return []
        return [Candidate(
            source=detect_source(query_or_url),
            url=query_or_url,
            title=info.get("title") or info.get("track") or query_or_url,
            info=info, fmt=fmt,
        )]

    clean = clean_query(query_or_url)
    print(f"    query nettoyee : {clean!r}")
    seen: set[str] = set()
    candidates: list[Candidate] = []
    for prefix, src in [("ytsearch", "youtube"), ("scsearch", "soundcloud")]:
        print(f"    recherche {src}...", end=" ", flush=True)
        entries = flat_search(prefix, clean, search_n)
        print(f"{len(entries)} resultat(s)")
        for e in entries:
            url = entry_url(e, src)
            if not url or url in seen:
                continue
            seen.add(url)
            try:
                info = fetch_metadata(url)
            except subprocess.CalledProcessError:
                continue
            fmt = best_audio_format(info)
            if not fmt:
                continue
            cand_title = info.get("title") or e.get("title") or url
            # Match : on inclut artiste/uploader pour aider les morceaux ou le
            # nom de l'artiste apparait dans le metadata mais pas le titre
            haystack = " ".join([
                cand_title,
                info.get("artist") or "",
                info.get("uploader") or "",
                info.get("creator") or "",
            ])
            candidates.append(Candidate(
                source=src, url=url, title=cand_title,
                info=info, fmt=fmt,
                match=title_match(clean, haystack),
            ))
    return candidates


def print_candidate_table(cands: list[Candidate], picked: Candidate) -> None:
    if not cands:
        return
    print()
    header = (
        f"    {'':2}{'source':<11}{'codec':<8}{'abr':>5}  {'qual':>5}  "
        f"{'match':>5}  {'score':>7}  title"
    )
    print(header)
    print("    " + "-" * (len(header) - 4))
    for c in sorted(cands, key=lambda x: -x.score):
        mark = ">" if c.url == picked.url else " "
        title = c.title[:50]
        print(
            f"    {mark} {c.source:<10}{c.codec:<8}{int(c.abr):>5}  "
            f"{score_str(c.quality):>5}  {c.match * 100:>4.0f}%  "
            f"{score_str(c.score):>7}  {title}"
        )
    print()


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------

def download_candidate(cand: Candidate, out_stem: Path) -> Path:
    """Telecharge le candidat. FLAC pour lossless et codecs hors Rekordbox, natif sinon."""
    out_stem.parent.mkdir(parents=True, exist_ok=True)
    template = str(out_stem) + ".%(ext)s"
    ext, lossless, _ = codec_info(cand.codec)

    cmd = [
        "yt-dlp", "--no-progress", "--no-warnings", *YTDLP_EXTRA_ARGS,
        "-f", "bestaudio", "-x", "-o", template,
    ]
    # FLAC pour le lossless, et pour les codecs que Rekordbox ne lit pas
    # (opus, vorbis) : le decodage est sans nouvelle perte.
    if lossless or f".{ext}" not in REKORDBOX_EXTS:
        cmd += ["--audio-format", "flac"]
        final_ext = ".flac"
    else:
        final_ext = "." + ext
    cmd.append(cand.url)

    proc = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        errors = [ln for ln in proc.stderr.splitlines() if ln.startswith("ERROR")]
        msg = errors[-1] if errors else proc.stderr.strip()[-300:]
        if "403" in msg:
            msg += " -- yt-dlp sans doute perime : brew upgrade yt-dlp"
        raise GrabError(f"yt-dlp : {msg}")

    expected = out_stem.with_suffix(final_ext)
    if expected.exists():
        return expected
    for e in KNOWN_EXTS:
        p = out_stem.with_suffix(e)
        if p.exists():
            return p
    raise FileNotFoundError(f"download: aucun fichier produit pour {out_stem}")


# ---------------------------------------------------------------------------
# Audio analysis (BPM + key)
# ---------------------------------------------------------------------------

_MAJOR = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
_MINOR = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
_KEYS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def analyze_audio(path: Path, start_bpm: float = 140.0) -> tuple[float, str]:
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import librosa
        import numpy as np

        y, sr = librosa.load(str(path), sr=22050, mono=True)
        tempo_value, _ = librosa.beat.beat_track(y=y, sr=sr, start_bpm=start_bpm)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

    tempo = float(np.atleast_1d(tempo_value)[0])
    if tempo < 90:
        tempo *= 2

    chroma_mean = chroma.mean(axis=1)
    major = np.array(_MAJOR)
    minor = np.array(_MINOR)
    best = (-2.0, "C", "major")
    for shift in range(12):
        rolled = np.roll(chroma_mean, -shift)
        sm = float(np.corrcoef(rolled, major)[0, 1])
        sn = float(np.corrcoef(rolled, minor)[0, 1])
        if sm > best[0]:
            best = (sm, _KEYS[shift], "major")
        if sn > best[0]:
            best = (sn, _KEYS[shift], "minor")
    return round(tempo, 1), f"{best[1]} {best[2]}"


# ---------------------------------------------------------------------------
# Tag writing (multi-conteneur)
# ---------------------------------------------------------------------------

def write_tags(path: Path, meta: TrackMeta, bpm: float, key: str) -> None:
    ext = path.suffix.lower()
    if ext == ".flac":
        from mutagen.flac import FLAC
        _write_vorbis(FLAC(str(path)), meta, bpm, key)
    elif ext == ".opus":
        from mutagen.oggopus import OggOpus
        _write_vorbis(OggOpus(str(path)), meta, bpm, key)
    elif ext == ".ogg":
        from mutagen.oggvorbis import OggVorbis
        _write_vorbis(OggVorbis(str(path)), meta, bpm, key)
    elif ext in (".m4a", ".mp4"):
        _write_mp4(path, meta, bpm, key)
    elif ext == ".mp3":
        _write_mp3(path, meta, bpm, key)
    else:
        print(f"    warning: pas de tag writer pour {ext}", file=sys.stderr)


def _write_vorbis(audio: Any, meta: TrackMeta, bpm: float, key: str) -> None:
    audio["TITLE"] = meta.title
    audio["ARTIST"] = meta.artist
    if meta.album:
        audio["ALBUM"] = meta.album
    if meta.year:
        audio["DATE"] = str(meta.year)
    if meta.genre:
        audio["GENRE"] = meta.genre
    if bpm > 0:
        audio["BPM"] = str(bpm)
    if key and key != "?":
        audio["KEY"] = key
        audio["INITIALKEY"] = key
    audio["COMMENT"] = f"Source: {meta.url}"
    audio.save()


def _write_mp4(path: Path, meta: TrackMeta, bpm: float, key: str) -> None:
    from mutagen.mp4 import MP4
    audio = MP4(str(path))
    audio["\xa9nam"] = meta.title
    audio["\xa9ART"] = meta.artist
    if meta.album:
        audio["\xa9alb"] = meta.album
    if meta.year:
        audio["\xa9day"] = str(meta.year)
    if meta.genre:
        audio["\xa9gen"] = ", ".join(meta.genre)
    if bpm > 0:
        audio["tmpo"] = [int(round(bpm))]
    if key and key != "?":
        audio["----:com.apple.iTunes:initialkey"] = [key.encode("utf-8")]
    audio["\xa9cmt"] = f"Source: {meta.url}"
    audio.save()


def _write_mp3(path: Path, meta: TrackMeta, bpm: float, key: str) -> None:
    from mutagen.easyid3 import EasyID3
    from mutagen.id3 import ID3NoHeaderError
    try:
        audio = EasyID3(str(path))
    except ID3NoHeaderError:
        from mutagen.mp3 import MP3
        m = MP3(str(path))
        m.add_tags()
        m.save()
        audio = EasyID3(str(path))
    EasyID3.RegisterTextKey("initialkey", "TKEY")
    audio["title"] = meta.title
    audio["artist"] = meta.artist
    if meta.album:
        audio["album"] = meta.album
    if meta.year:
        audio["date"] = str(meta.year)
    if meta.genre:
        audio["genre"] = meta.genre
    if bpm > 0:
        audio["bpm"] = str(bpm)
    if key and key != "?":
        audio["initialkey"] = key
    audio.save()


# ---------------------------------------------------------------------------
# Metadata model
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Buy URL detection (description + fallback recherche Bandcamp)
# ---------------------------------------------------------------------------

# Sites marchands directs (le clic mene a la fiche du track)
DIRECT_BUY_DOMAINS: tuple[str, ...] = (
    "bandcamp.com",
    "beatport.com",
    "junodownload.com",
    "hardwax.com",
    "bleep.com",
    "traxsource.com",
    "whatpeopleplay.com",
    "music.apple.com",
    "itunes.apple.com",
    "deejay.de",
    "boomkat.com",
)

# Smart links / landing pages (le clic mene a une page avec plusieurs stores)
SMART_LINK_DOMAINS: tuple[str, ...] = (
    "fanlink.to",
    "linktr.ee",
    "ffm.to",
    "ditto.fm",
    "songwhip.com",
    "album.link",
    "linkfire.com",
    "found.ee",
    "li.sten.to",
    "backl.ink",
    "show.co",
)

_URL_RE = re.compile(r"https?://[^\s<>\"\)\]]+")


def _is_direct_buy(url: str) -> bool:
    return any(d in url for d in DIRECT_BUY_DOMAINS)


def _is_smart_link(url: str) -> bool:
    return any(d in url for d in SMART_LINK_DOMAINS)


def _scan_description(info: dict[str, Any]) -> tuple[str | None, str | None]:
    """Retourne (direct_url, smart_link) depuis la description yt-dlp."""
    direct: str | None = None
    smart: str | None = None
    description = info.get("description") or ""
    for raw in _URL_RE.findall(description):
        cleaned = raw.rstrip(".,;:!?\"')")
        if not direct and _is_direct_buy(cleaned):
            direct = cleaned
        elif not smart and _is_smart_link(cleaned):
            smart = cleaned
        if direct and smart:
            break
    return direct, smart


def _search_bandcamp(artist: str, title: str) -> str | None:
    """Cherche un track sur Bandcamp via l'API publique d'autocomplete.

    Retourne le candidat qui matche le mieux artist+title (titre + nom
    d'artiste agreges), >= 50% de tokens en commun. None si pas assez
    de match ou si la requete echoue."""
    import json as _json
    import urllib.request

    query = " ".join(p for p in (artist, title) if p and p != "unknown").strip()
    if not query:
        return None
    endpoint = "https://bandcamp.com/api/bcsearch_public_api/1/autocomplete_elastic"
    body = _json.dumps({
        "search_text": query,
        "search_filter": "t",  # tracks uniquement
        "full_page": False,
        "fan_id": None,
    }).encode()
    req = urllib.request.Request(endpoint, data=body, headers={
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = _json.loads(resp.read())
    except Exception:
        return None

    results = (data.get("auto") or {}).get("results") or []
    tracks = [r for r in results if r.get("type") == "t" and r.get("item_url_path")]
    if not tracks:
        return None

    expected_tokens = _tokenize(query)

    def score(track: dict[str, Any]) -> float:
        cand = f"{track.get('band_name', '')} {track.get('name', '')}"
        cand_tokens = _tokenize(cand)
        if not expected_tokens:
            return 0.0
        return len(expected_tokens & cand_tokens) / len(expected_tokens)

    best = max(tracks, key=score)
    if score(best) < 0.5:
        return None
    return str(best["item_url_path"])


def find_buy_url(info: dict[str, Any], artist: str, title: str) -> str | None:
    """Trouve un lien d'achat pour le morceau.

    Ordre de preference :
    1. URL source sur un site marchand direct
    2. Lien marchand direct dans la description
    3. Recherche Bandcamp via API (uniquement si la source n'est pas Bandcamp)
    4. Smart link (fanlink.to / linktr.ee / etc.) dans la description
    """
    source_url = info.get("webpage_url") or info.get("original_url") or ""
    if _is_direct_buy(source_url):
        return source_url

    direct, smart = _scan_description(info)
    if direct:
        return direct

    if "bandcamp.com" not in source_url:
        bc = _search_bandcamp(artist, title)
        if bc:
            return bc

    return smart


@dataclass
class TrackMeta:
    title: str
    artist: str
    url: str
    source: str
    duration_s: int
    album: str | None = None
    year: int | None = None
    genre: list[str] = field(default_factory=list)
    buy_url: str | None = None


# ---------------------------------------------------------------------------
# Library (upsert d'une entree)
# ---------------------------------------------------------------------------

def upsert_track(
    library_path: Path,
    meta: TrackMeta,
    audio_rel: Path,
    bpm: float,
    key: str,
    quality: str,
) -> tuple[bool, str]:
    """Insere ou met a jour un morceau dans library.md.

    Retourne (created, slug). Preserve les champs `energy`, `mood`, `tags`,
    `notes` d'une eventuelle entree existante."""
    entries = parse_library(library_path)
    slug = f"{slugify(meta.artist)}_-_{slugify(meta.title)}"
    is_new = slug not in entries
    existing = entries.get(slug, {})

    minutes, seconds = divmod(meta.duration_s or 0, 60)
    new_fields: dict[str, str] = {
        "artist": meta.artist,
        "title": meta.title,
        "bpm": f"{bpm}" if bpm > 0 else "",
        "key": key if key and key != "?" else "",
        "duration": f"{minutes}:{seconds:02d}",
        "year": str(meta.year) if meta.year else "",
        "genre": ", ".join(meta.genre) or existing.get("genre", ""),
        "quality": quality,
        "source": meta.source,
        "url": meta.url,
        "buy_url": meta.buy_url or existing.get("buy_url", ""),
        "file": f"[[{audio_rel.as_posix()}]]",
        "added": existing.get("added") or date.today().isoformat(),
    }
    # quality_score est preserve (vient d'analyze.py, pas de grab.py)
    if "quality_score" in existing:
        new_fields["quality_score"] = existing["quality_score"]
    for k in PRESERVED_FIELDS:
        new_fields[k] = existing.get(k, "")

    entries[slug] = new_fields
    write_library(library_path, entries)
    return is_new, slug


# ---------------------------------------------------------------------------
# Existing file detection + rangement par style
# ---------------------------------------------------------------------------

def existing_audio(slug: str) -> Path | None:
    """Cherche slug.<ext> a la racine de <MEDIA>/Mix/audio/ puis recursivement
    dans ses sous-dossiers de style."""
    for ext in KNOWN_EXTS:
        p = AUDIO_DIR / f"{slug}{ext}"
        if p.exists():
            return p
    for p in AUDIO_DIR.rglob(f"{slug}.*"):
        if p.is_file() and p.suffix.lower() in KNOWN_EXTS:
            return p
    return None


def deduce_folder(folder_arg: str | None, genres: list[str]) -> str | None:
    """Sous-dossier de rangement dans <MEDIA>/Mix/audio/.

    --folder prime ; sinon le premier genre connu (slugifie) ; sinon None
    (racine de <MEDIA>/Mix/audio/, comportement historique)."""
    if folder_arg:
        return folder_arg
    if genres:
        return slugify(genres[0])
    return None


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class GrabError(Exception):
    """Acquisition impossible (aucun candidat, source illisible)."""


class CandidateInfo(BaseModel):
    """Candidat serialisable (CLI et API 7.I), sans le JSON yt-dlp brut."""

    source: str
    url: str
    title: str
    uploader: str = ""
    duration_s: int = 0
    codec: str
    abr: int
    quality: str  # score_str : debit pondere ou LOSSLESS
    match: float  # 0..1
    score: float


def candidate_info(cand: Candidate) -> CandidateInfo:
    return CandidateInfo(
        source=cand.source, url=cand.url, title=cand.title,
        uploader=cand.info.get("uploader") or cand.info.get("channel") or "",
        duration_s=int(cand.info.get("duration") or 0),
        codec=cand.codec, abr=int(cand.abr), quality=score_str(cand.quality),
        match=round(cand.match, 2), score=round(cand.score, 1),
    )


def search(query_or_url: str, search_n: int = 3) -> list[Candidate]:
    """Candidats YT/SC tries par score decroissant (le premier est le choix par defaut)."""
    return sorted(resolve_candidates(query_or_url, search_n=search_n),
                  key=lambda c: -c.score)


@dataclass
class IngestOptions:
    analyze: bool = True
    bpm_override: float | None = None
    key_override: str | None = None
    genre_override: list[str] | None = None
    replace: bool = False
    start_bpm: float = 140.0
    folder: str | None = None


@dataclass
class IngestResult:
    slug: str
    created: bool
    audio_path: Path
    # BPM confirme par la fenetre du style (a imposer a l'analyse complete),
    # None sans style reconnu ou si le BPM est force
    style_bpm: float | None = None


def style_hints(cand: Candidate, opts: IngestOptions) -> list[str]:
    """Textes qui designent le style, par priorite : dossier, genre force,
    genre de la source, titre + tags. Jamais le genre de library.md (souvent
    deduit du BPM lui-meme)."""
    info = cand.info
    return [
        opts.folder or "",
        ", ".join(opts.genre_override or []),
        info.get("genre") or "",
        " ".join([cand.title, *(info.get("tags") or []), *(info.get("categories") or [])]),
    ]


def correct_bpm(bpm: float, hints: list[str]) -> tuple[float, str | None]:
    """Ramene le BPM dans la fenetre du style (erreurs d'octave). Retourne
    (bpm, style) ; style None si aucun style reconnu ou aucune octave plausible."""
    from analyzer.infer import fold_bpm, style_window

    style = style_window(hints)
    if style is None:
        return bpm, None
    name, lo, hi = style
    folded = fold_bpm(bpm, lo, hi)
    if folded is None:
        return bpm, None
    if folded != bpm:
        print(f"    bpm {bpm} -> {folded} (style {name} : {lo:.0f}-{hi:.0f})")
    return folded, name


_ARTIST_LINKS = {"x", "feat", "ft", "featuring", "and", "et", "vs", "with"}


def track_meta(cand: Candidate, genre_override: list[str] | None) -> TrackMeta:
    """Artiste / titre / genre / lien d'achat deduits du metadata du candidat."""
    info = cand.info
    title = info.get("track") or info.get("title") or "untitled"
    artist_meta = info.get("artist") or info.get("creator")
    if artist_meta:
        artist = artist_meta
    else:
        # Pas de champ artist : essayer de parser depuis le titre.
        parsed_a, parsed_t = parse_artist_title(title)
        if parsed_a and parsed_t:
            artist = parsed_a
            title = parsed_t
        else:
            artist = info.get("uploader") or "unknown"
    # SoundCloud (et parfois YT) renvoient `title = "Artist - Track - Label"`.
    # Nettoyer : retire le prefixe "<artist> - " et un eventuel suffixe " - <X>"
    # quand <X> matche (en substring) l'uploader/channel/album.
    artist = re.sub(r"\s+,", ",", artist).strip()  # "LIMITLEZZ , Maureen"
    if " - " in title:
        lead, rest = title.split(" - ", 1)
        # "Limitlezz x Maureen - ..." avec artist "Limitlezz, Maureen" : memes
        # tokens une fois les liaisons (x, feat, &...) retirees
        lead_tokens = _tokenize(lead) - _ARTIST_LINKS
        if lead_tokens and lead_tokens <= _tokenize(artist):
            title = rest.strip()
        suffix_candidates = [
            (info.get("uploader") or "").lower().strip(),
            (info.get("channel") or "").lower().strip(),
            (info.get("album") or "").lower().strip(),
        ]
        suffix_candidates = [s for s in suffix_candidates if s]
        if " - " in title and suffix_candidates:
            base, tail = title.rsplit(" - ", 1)
            tail_low = tail.strip().lower()
            if tail_low and any(
                tail_low in c or c in tail_low for c in suffix_candidates
            ):
                title = base.strip()
    # Retire un suffixe entre parentheses "(Official Audio)", "(Original Mix)"
    # quand il ressemble a un descripteur de version sans info utile
    title = re.sub(
        r"\s*[\(\[](?:official\s+(?:audio|video|music\s+video|lyric\s+video|visualizer)"
        r"|clip\s+officiel|audio\s+officiel|vid[eé]o\s+officielle|lyrics?|hd|hq)[\)\]]\s*$",
        "",
        title,
        flags=re.IGNORECASE,
    ).strip()
    year: int | None = None
    if info.get("release_year"):
        year = int(info["release_year"])
    elif info.get("upload_date"):
        year = int(str(info["upload_date"])[:4])
    raw_genre = info.get("genre") or ""
    genre = [g.strip() for g in re.split(r"[,/;]", raw_genre) if g.strip()]
    if genre_override:
        genre = genre_override

    print("    recherche lien d'achat...", end=" ", flush=True)
    buy_url = find_buy_url(info, artist, title)
    print(buy_url if buy_url else "(aucun)")

    return TrackMeta(
        title=title, artist=artist, album=info.get("album"), url=cand.url,
        source=cand.source, duration_s=int(info.get("duration") or 0),
        year=year, genre=genre, buy_url=buy_url,
    )


def _dest_dir(folder: str | None, genre: list[str]) -> Path:
    dest_folder = deduce_folder(folder, genre)
    dest_dir = AUDIO_DIR / dest_folder if dest_folder else AUDIO_DIR
    print(f"    dossier   : {dest_dir.relative_to(MIX_DIR).as_posix()}/"
          + ("" if folder else " (deduit)" if dest_folder else " (racine, genre inconnu)"))
    return dest_dir


def ingest(
    target: str | Candidate,
    opts: IngestOptions,
    on_step: Callable[[str], None] | None = None,
) -> IngestResult:
    """Telecharge un candidat (ou une URL), detecte BPM/key, tague et upsert library.md.

    `on_step` recoit le nom de chaque etape au moment ou elle demarre (jobs 7.I)."""
    step = on_step or (lambda _name: None)
    style_bpm: float | None = None
    if isinstance(target, str):
        step("metadata")
        found = resolve_candidates(target, search_n=1)
        if not found:
            raise GrabError(f"aucun format audio pour {target}")
        cand = found[0]
    else:
        cand = target

    meta = track_meta(cand, opts.genre_override)
    quality = f"{cand.codec} {int(cand.abr)}kbps"
    print(f"    selection : {cand.source} | {quality}")
    dest_dir = _dest_dir(opts.folder, meta.genre)

    slug = f"{slugify(meta.artist)}_-_{slugify(meta.title)}"
    existing = existing_audio(slug)
    if existing and not opts.replace:
        rel = existing.relative_to(AUDIO_DIR).as_posix()
        print(f"    deja present : {rel} (--replace pour ecraser)")
        audio_path = existing
    else:
        step("download")
        if existing:
            print(f"    --replace : suppression de {existing.name}")
            existing.unlink()
        audio_path = download_candidate(cand, dest_dir / slug)
        print(f"    telecharge : {audio_path.relative_to(AUDIO_DIR).as_posix()}")

    if opts.bpm_override is not None:
        bpm = float(opts.bpm_override)
        key = opts.key_override or "?"
        print(f"    overrides bpm={bpm} key={key}")
    elif opts.analyze:
        step("bpm_key")
        print("    analyse bpm/key...")
        bpm, key = analyze_audio(audio_path, start_bpm=opts.start_bpm)
        if opts.key_override:
            key = opts.key_override
        print(f"    bpm={bpm} key={key}")
        bpm, style = correct_bpm(bpm, style_hints(cand, opts))
        if style:
            style_bpm = bpm
            if not meta.genre:
                meta.genre = [style]
    else:
        bpm, key = 0.0, opts.key_override or "?"

    step("library")
    write_tags(audio_path, meta, bpm, key)
    audio_rel = audio_path.relative_to(MIX_DIR)
    created, slug = upsert_track(LIBRARY_FILE, meta, audio_rel, bpm, key, quality)
    print(f"    library.md : {'ajoute' if created else 'mis a jour'}")
    return IngestResult(slug=slug, created=created, audio_path=audio_path,
                        style_bpm=style_bpm)


def grab_one(
    query_or_url: str,
    analyze: bool,
    bpm_override: float | None,
    key_override: str | None,
    genre_override: list[str] | None,
    dry_run: bool,
    replace: bool,
    search_n: int,
    start_bpm: float,
    analyze_quality_flag: bool = False,
    folder: str | None = None,
) -> None:
    """Parcours CLI : search -> meilleur candidat -> ingest (+ analyse qualite)."""
    label = "url" if is_url(query_or_url) else "query"
    print(f"[+] {label}: {query_or_url}")

    candidates = search(query_or_url, search_n=search_n)
    if not candidates:
        print("    aucun candidat trouve", file=sys.stderr)
        return
    picked = candidates[0]
    print_candidate_table(candidates, picked)

    if dry_run:
        meta = track_meta(picked, genre_override)
        print(f"    selection : {picked.source} | {picked.codec} {int(picked.abr)}kbps")
        _dest_dir(folder, meta.genre)
        print("    dry-run : pas de telechargement")
        return

    result = ingest(picked, IngestOptions(
        analyze=analyze, bpm_override=bpm_override, key_override=key_override,
        genre_override=genre_override, replace=replace, start_bpm=start_bpm,
        folder=folder,
    ))

    if analyze_quality_flag:
        try:
            run_quality_analysis(result.audio_path, result.slug, result.style_bpm)
        except Exception as exc:  # noqa: BLE001
            print(f"    [warn] analyse qualite ignoree : {exc}", file=sys.stderr)


def run_quality_analysis(audio_path: Path, slug: str,
                         override_bpm: float | None = None) -> None:
    """Lance le pipeline analyzer (Phase 1 + 2) sur un fichier juste telecharge,
    puis populate les champs derives (energy / mood / genre / tags via infer,
    about via MusicBrainz). Skip les champs deja non-vides (preserve les edits)."""
    # Imports lazy : librosa/scipy sont lourds, inutile sans le flag
    from analyzer.describe import describe_artist
    from analyzer.infer import infer_energy, infer_genre, infer_mood, infer_tags
    from analyzer.pipeline import analyze_file as _analyze
    from analyzer.report import save_sidecar

    print("    analyse qualite (Phase 1+2)...")
    file_path_str = mix_relative(audio_path)
    report = _analyze(
        path=audio_path,
        slug=slug,
        with_structure=True,
        file_path_str=file_path_str,
        override_bpm=override_bpm,  # BPM confirme par le style (cf. correct_bpm)
    )
    save_sidecar(report, QUALITY_DIR)
    update_field(LIBRARY_FILE, slug, "quality_score", f"{report.quality.score:.1f}")
    if report.frequency_bands:
        from analyzer.frequency_bands import to_compact_string
        update_field(
            LIBRARY_FILE, slug, "band_profile",
            to_compact_string(report.frequency_bands),
        )
    flags_str = f", flags={','.join(report.quality.flags)}" if report.quality.flags else ""
    print(f"    quality_score : {report.quality.score:.1f}/100 ({report.quality.rating}){flags_str}")
    if report.structure:
        print(f"    structure     : {report.structure.n_segments} segments")
    if report.cues and report.cues.cues:
        print(f"    cues          : {len(report.cues.cues)} points")
    if report.rhythm_signature and report.rhythm_signature.bars_used:
        rs = report.rhythm_signature
        print(
            f"    groove        : syncope {rs.syncopation:.2f} / "
            f"pulse {rs.pulse_clarity:.2f} / swing {rs.swing:.2f}"
        )

    # --- Phase 4 : inferences semantiques (skip si champ deja non-vide) ---
    entry = parse_library(LIBRARY_FILE).get(slug, {})
    sidecar = report.model_dump()
    filled: list[str] = []
    inferences = [
        ("genre",  lambda: infer_genre(sidecar, entry)),
        ("energy", lambda: infer_energy(sidecar, entry)),
        ("mood",   lambda: infer_mood(sidecar, entry)),
        ("tags",   lambda: infer_tags(sidecar)),
    ]
    for field, fn in inferences:
        if entry.get(field, "").strip():
            continue
        value = fn()
        if value:
            update_field(LIBRARY_FILE, slug, field, value)
            filled.append(f"{field}={value}")
    if filled:
        print(f"    infer         : {', '.join(filled)}")

    # MusicBrainz pour `about` (1.1s de rate-limit si pas en cache)
    if not entry.get("about", "").strip():
        artist = entry.get("artist") or ""
        if artist:
            about = describe_artist(artist, ARTISTS_DIR, rate_limit=True)
            if about:
                update_field(LIBRARY_FILE, slug, "about", about)
                print(f"    about         : {about}")

    # Phase 5 : PNG signature + maj index
    try:
        from analyzer.visualize import render_track, write_index_md
        visuals_dir = VISUALS_DIR
        png_path = visuals_dir / f"{slug}.png"
        sidecar_data = report.model_dump()
        # Re-read l'entry pour avoir les champs juste mis a jour
        fresh_entry = parse_library(LIBRARY_FILE).get(slug, {})
        render_track(audio_path, fresh_entry, sidecar_data, png_path)
        write_index_md(parse_library(LIBRARY_FILE), visuals_dir)
        print(f"    visual        : {png_path}")
    except Exception as exc:  # noqa: BLE001
        print(f"    [warn] rendu PNG ignore : {exc}", file=sys.stderr)


def refresh_buy_urls() -> int:
    """Parcourt library.md, et pour chaque entree dont `buy_url` est vide,
    refait un yt-dlp -J sur `url` pour extraire un eventuel lien d'achat."""
    entries = parse_library(LIBRARY_FILE)
    if not entries:
        print("library.md vide.")
        return 0

    to_process = [
        (slug, fields) for slug, fields in entries.items()
        if not fields.get("buy_url") and fields.get("url")
    ]
    print(f"[refresh] {len(to_process)} entrees a traiter sur {len(entries)} total")

    found = 0
    for slug, fields in to_process:
        url = fields["url"]
        artist = fields.get("artist", "")
        title = fields.get("title", "")
        print(f"[+] {artist} — {title}")
        try:
            info = fetch_metadata(url)
        except subprocess.CalledProcessError as exc:
            err = exc.stderr if isinstance(exc.stderr, str) else ""
            print(f"    yt-dlp echoue ({err.strip() or exc})", file=sys.stderr)
            continue
        print("    recherche lien d'achat...", end=" ", flush=True)
        buy_url = find_buy_url(info, artist, title)
        print(buy_url if buy_url else "(aucun)")
        if buy_url:
            update_field(LIBRARY_FILE, slug, "buy_url", buy_url)
            found += 1

    print(f"\n[refresh] termine : {found}/{len(to_process)} liens trouves")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Grab des morceaux dans la library en choisissant la meilleure source.",
    )
    parser.add_argument(
        "inputs", nargs="*",
        help="URLs ou requetes texte libre.",
    )
    parser.add_argument("--refresh-buy-urls", action="store_true",
                        help="Backfill : remplit buy_url pour les entrees "
                             "existantes de library.md qui n'en ont pas.")
    parser.add_argument("--no-analyze", action="store_true",
                        help="Skip BPM/key (librosa).")
    parser.add_argument("--bpm", type=float, help="Force BPM, skip detection.")
    parser.add_argument("--key", type=str, help="Force key (ex: 'A minor').")
    parser.add_argument("--genre", type=str, help="Genres separes par virgule.")
    parser.add_argument("--folder", type=str,
                        help="Sous-dossier de <MEDIA>/Mix/audio/ ou ranger le fichier "
                             "(ex: swing). Si absent, deduit du genre ; sans genre "
                             "connu, racine de <MEDIA>/Mix/audio/.")
    parser.add_argument("--cookies-from-browser", type=str, metavar="BROWSER",
                        help="Authentifie yt-dlp avec les cookies du navigateur "
                             "(chrome, firefox, safari...). Debloque playlists "
                             "privees, videos en 403 et formats Premium.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Cherche et selectionne sans telecharger.")
    parser.add_argument("--replace", action="store_true",
                        help="Re-telecharger meme si fichier deja present.")
    parser.add_argument("--search-n", type=int, default=3,
                        help="Candidats par plateforme (defaut 3).")
    parser.add_argument("--start-bpm", type=float, default=140.0,
                        help="Hint BPM pour librosa (defaut 140, mets 180 pour tribe).")
    parser.add_argument("--analyze-quality", action="store_true",
                        help="Lance l'analyse audiophile apres download "
                             "(quality_score + sidecar JSON).")
    args = parser.parse_args()
    if not media_ok():
        return 2

    if args.cookies_from_browser:
        YTDLP_EXTRA_ARGS[:] = ["--cookies-from-browser", args.cookies_from_browser]

    if args.refresh_buy_urls:
        return refresh_buy_urls()

    if args.folder:
        sub = Path(args.folder)
        if sub.is_absolute() or ".." in sub.parts:
            parser.error(f"--folder doit etre un sous-chemin relatif simple "
                         f"(recu : {args.folder})")

    if not args.inputs:
        parser.print_help()
        return 1

    genre_override = (
        [g.strip() for g in args.genre.split(",") if g.strip()]
        if args.genre else None
    )

    inputs = expand_inputs(args.inputs)
    if len(inputs) != len(args.inputs):
        print(f"[i] {len(inputs)} entrees apres expansion multi-lignes")

    # Developpe les URLs Spotify en requetes texte 'artiste titre'.
    expanded: list[str] = []
    for item in inputs:
        if is_spotify(item):
            queries = spotify_queries(item)
            if not queries:
                print(f"[!] Spotify: aucune piste extraite de {item}", file=sys.stderr)
                continue
            print(f"[i] Spotify: {len(queries)} piste(s) extraite(s) de {item}")
            expanded.extend(queries)
        else:
            expanded.append(item)
    inputs = expanded

    code = 0
    for q in inputs:
        try:
            grab_one(
                query_or_url=q,
                analyze=not args.no_analyze,
                bpm_override=args.bpm,
                key_override=args.key,
                genre_override=genre_override,
                dry_run=args.dry_run,
                replace=args.replace,
                search_n=args.search_n,
                start_bpm=args.start_bpm,
                analyze_quality_flag=args.analyze_quality,
                folder=args.folder,
            )
        except subprocess.CalledProcessError as exc:
            err = exc.stderr if isinstance(exc.stderr, str) else ""
            print(f"[ERROR] {q}: yt-dlp a echoue ({err.strip() or exc})",
                  file=sys.stderr)
            code = 1
        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] {q}: {exc}", file=sys.stderr)
            code = 1
    return code


if __name__ == "__main__":
    sys.exit(main())

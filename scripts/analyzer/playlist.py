"""Generation greedy d'une playlist a partir d'un track de depart.

A chaque etape : prend le track non-joue avec le meilleur score de
transition vers le precedent, jusqu'a atteindre la duree cible.

Pas d'optimisation globale (ce serait un TSP-like) : greedy local
est suffisant pour des sets < 2h.

Export Mixxx via la fonction `to_m3u8` (format universel)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .compatibility import TransitionScore, parse_energy, score_transition


@dataclass
class PlaylistStep:
    slug: str
    fields: dict[str, str]
    transition_from_prev: TransitionScore | None = None


@dataclass
class Playlist:
    target_duration_min: float
    direction: str
    steps: list[PlaylistStep] = field(default_factory=list)

    @property
    def total_duration_s(self) -> float:
        return sum(_duration_s(s.fields) for s in self.steps)

    @property
    def slugs(self) -> set[str]:
        return {s.slug for s in self.steps}


def _duration_s(fields: dict[str, str]) -> float:
    raw = fields.get("duration", "")
    if not raw or ":" not in raw:
        return 0.0
    try:
        parts = raw.split(":")
        if len(parts) == 2:
            m, s = parts
            return float(m) * 60.0 + float(s)
        if len(parts) == 3:
            h, m, s = parts
            return float(h) * 3600.0 + float(m) * 60.0 + float(s)
    except ValueError:
        pass
    return 0.0


def build_playlist_to_peak(
    entries: dict[str, dict[str, str]],
    peak_slug: str,
    target_duration_min: float = 60.0,
    min_transition_score: float = 0.4,
    max_track_duration_min: float = 15.0,
) -> Playlist:
    """Construit une playlist qui se termine sur `peak_slug` avec
    progression d'energie montante.

    Algorithme : greedy backward. A chaque etape on cherche un predecesseur
    P tel que score_transition(P, current_first, 'rising') est maximise.
    Inverse semantiquement build_playlist (forward), avec la transition
    stockee sur le step destination (transition_from_prev)."""
    if peak_slug not in entries:
        raise ValueError(f"slug inconnu : {peak_slug}")

    playlist = Playlist(
        target_duration_min=target_duration_min,
        direction="rising",
    )
    playlist.steps.append(PlaylistStep(
        slug=peak_slug,
        fields=entries[peak_slug],
    ))

    target_s = target_duration_min * 60.0
    max_dur_s = max_track_duration_min * 60.0
    # Plancher d'energie : eviter que le greedy degringole jusqu'a very_low
    # alors qu'on construit vers un peak. Empiriquement : peak - 2 crans.
    peak_energy = parse_energy(entries[peak_slug].get("energy"))
    energy_floor: float | None = (peak_energy - 2.0) if peak_energy else None

    while playlist.total_duration_s < target_s:
        current_first = playlist.steps[0]
        candidates = []
        for slug, fields in entries.items():
            if slug in playlist.slugs:
                continue
            if _duration_s(fields) > max_dur_s:
                continue
            if energy_floor is not None:
                en = parse_energy(fields.get("energy"))
                if en is not None and en < energy_floor:
                    continue
            candidates.append((slug, fields))

        if not candidates:
            break

        scored = []
        for slug, fields in candidates:
            t = score_transition(fields, current_first.fields, direction="rising")
            if t.total >= min_transition_score:
                scored.append((t.total, slug, fields, t))

        if not scored:
            break

        scored.sort(key=lambda x: -x[0])
        _, slug, fields, transition = scored[0]
        # La transition est P -> current_first, donc on l'attache au step
        # qui devient le successeur de P (= current_first).
        current_first.transition_from_prev = transition
        new_step = PlaylistStep(slug=slug, fields=fields)
        playlist.steps.insert(0, new_step)

    return playlist


_FILE_REF_RE = re.compile(r"\[\[(.+?)\]\]")


def to_m3u8(playlist: Playlist, library_root: Path) -> str:
    """Serialise une playlist au format M3U8 (UTF-8 + extensions EXTINF).

    Mixxx, VLC, foobar2000 etc. lisent ce format. `library_root` est le
    repertoire qui contient `audio/` (ex: `music/library/`)."""
    lines = ["#EXTM3U"]
    for step in playlist.steps:
        artist = step.fields.get("artist", "?")
        title = step.fields.get("title", "?")
        dur_s = _duration_s(step.fields)
        file_ref = step.fields.get("file", "")
        match = _FILE_REF_RE.search(file_ref)
        if not match:
            continue
        rel_path = match.group(1)
        abs_path = (library_root / rel_path).resolve()
        lines.append(f"#EXTINF:{int(dur_s)},{artist} - {title}")
        lines.append(str(abs_path))
    return "\n".join(lines) + "\n"


def build_playlist(
    entries: dict[str, dict[str, str]],
    start_slug: str,
    target_duration_min: float = 60.0,
    direction: str = "rising",
    min_transition_score: float = 0.4,
    max_track_duration_min: float = 15.0,
) -> Playlist:
    """Construit une playlist greedy a partir de start_slug.

    direction : "rising" / "maintain" / "falling" pour la progression d'energie.
    min_transition_score : seuil sous lequel on ne mixe pas.
    max_track_duration_min : exclut les fichiers plus longs (mix radio, set
        captation) du pool. start_slug est toujours inclus meme s'il depasse.
    """
    if start_slug not in entries:
        raise ValueError(f"slug inconnu : {start_slug}")

    playlist = Playlist(
        target_duration_min=target_duration_min,
        direction=direction,
    )
    playlist.steps.append(PlaylistStep(
        slug=start_slug,
        fields=entries[start_slug],
    ))

    max_dur_s = max_track_duration_min * 60.0
    target_s = target_duration_min * 60.0
    while playlist.total_duration_s < target_s:
        current = playlist.steps[-1]
        candidates = [
            (slug, fields) for slug, fields in entries.items()
            if slug not in playlist.slugs
            and _duration_s(fields) <= max_dur_s
        ]
        if not candidates:
            break

        scored = []
        for slug, fields in candidates:
            t = score_transition(current.fields, fields, direction=direction)
            if t.total >= min_transition_score:
                scored.append((t.total, slug, fields, t))

        if not scored:
            break

        scored.sort(key=lambda x: -x[0])
        _, slug, fields, transition = scored[0]
        playlist.steps.append(PlaylistStep(
            slug=slug,
            fields=fields,
            transition_from_prev=transition,
        ))

    return playlist

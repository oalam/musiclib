#!/usr/bin/env python3
"""Set builder : preparer un set free party a partir de library.md.

Phase 4 du projet quality-analyzer : doublons, compatibilite harmonique
(Camelot), recommandation d'enchainement, generation de playlist.

Commandes:
    setbuilder.py duplicates                # liste les doublons
    setbuilder.py compatible <slug> [-n 10] # tracks compatibles avec <slug>
    setbuilder.py playlist --start <slug> \
        --duration 60 --energy rising      # genere un set
    setbuilder.py keys                      # liste les keys + Camelot
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from analyzer.compatibility import score_transition
from analyzer.describe import describe_artist
from analyzer.duplicates import find_duplicates
from analyzer.infer import (
    infer_energy,
    infer_genre,
    infer_mood,
    infer_tags,
    load_sidecar,
)
from analyzer.keys import to_camelot
from analyzer.playlist import build_playlist, build_playlist_to_peak, to_m3u8
from analyzer.rhythm_signature import cluster, rhythm_distance, to_sparkline
from analyzer.types import RhythmSignatureReport
from library_md import parse_library, update_field

from paths import ARTISTS_DIR, LIBRARY_FILE, MIX_DIR, QUALITY_DIR


def _format_duration(seconds: float) -> str:
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"


def _track_label(slug: str, fields: dict[str, str], width: int = 50) -> str:
    artist = fields.get("artist", "?")
    title = fields.get("title", "?")
    full = f"{artist} — {title}"
    if len(full) > width:
        full = full[:width - 1] + "…"
    return full


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_duplicates(entries: dict[str, dict[str, str]]) -> int:
    groups = find_duplicates(entries)
    if not groups:
        print("Aucun doublon detecte.")
        return 0
    print(f"{len(groups)} groupe(s) de doublons :\n")
    for grp in groups:
        print(f"== {grp.signature}")
        for slug, fields in grp.entries:
            q = fields.get("quality_score", "?")
            quality_label = fields.get("quality", "?")
            print(f"  [{q:>5}] {_track_label(slug, fields, 55)}  ({quality_label})")
            print(f"          file: {fields.get('file', '')}")
        print()
    return 0


def cmd_compatible(
    entries: dict[str, dict[str, str]],
    target_slug: str,
    n: int,
    direction: str,
    min_score: float,
) -> int:
    if target_slug not in entries:
        print(f"[ERROR] slug introuvable : {target_slug}", file=sys.stderr)
        print("Slugs disponibles :", file=sys.stderr)
        for s in sorted(entries):
            print(f"  {s}", file=sys.stderr)
        return 1

    target = entries[target_slug]
    print(f"Compatibilite avec : {_track_label(target_slug, target, 60)}")
    bpm = target.get("bpm") or "?"
    key = target.get("key") or "?"
    ck = to_camelot(target.get("key"))
    energy = target.get("energy") or "?"
    print(f"  bpm={bpm}  key={key} ({ck or '?'})  energy={energy}  direction={direction}\n")

    scored = []
    for slug, fields in entries.items():
        if slug == target_slug:
            continue
        ts = score_transition(target, fields, direction=direction)
        if ts.total >= min_score:
            scored.append((ts.total, slug, fields, ts))
    scored.sort(key=lambda x: -x[0])

    if not scored:
        print(f"Aucun candidat avec score >= {min_score}.")
        return 0

    print(f"{'score':>6}  {'bpm':>5}  {'key':>3}  {'en':>3}  track")
    print("-" * 78)
    for score, slug, fields, ts in scored[:n]:
        bpm_v = fields.get("bpm", "?")[:5]
        ck_v = to_camelot(fields.get("key")) or "?"
        en_v = fields.get("energy", "?")[:3] or "?"
        print(
            f"{score:>6.2f}  {bpm_v:>5}  {ck_v:>3}  {en_v:>3}  "
            f"{_track_label(slug, fields, 50)}"
        )
    print()
    return 0


def cmd_playlist(
    entries: dict[str, dict[str, str]],
    start_slug: str | None,
    peak_slug: str | None,
    duration_min: float,
    direction: str,
    min_score: float,
    max_track_min: float,
    export_m3u8: str | None,
) -> int:
    try:
        if peak_slug:
            playlist = build_playlist_to_peak(
                entries,
                peak_slug=peak_slug,
                target_duration_min=duration_min,
                min_transition_score=min_score,
                max_track_duration_min=max_track_min,
            )
            mode_label = f"backward (peak={peak_slug})"
        else:
            assert start_slug is not None  # garanti par argparse
            playlist = build_playlist(
                entries,
                start_slug=start_slug,
                target_duration_min=duration_min,
                direction=direction,
                min_transition_score=min_score,
                max_track_duration_min=max_track_min,
            )
            mode_label = f"forward (start={start_slug}, {direction})"
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    total = playlist.total_duration_s
    print(f"Playlist {duration_min:.0f} min — {mode_label}, min score {min_score}")
    print(f"  {len(playlist.steps)} tracks, total {_format_duration(total)}\n")

    cumul = 0.0
    for i, step in enumerate(playlist.steps):
        bpm = step.fields.get("bpm", "?")[:5]
        ck = to_camelot(step.fields.get("key")) or "?"
        en = step.fields.get("energy", "?")[:6] or "?"
        dur_s = 0.0
        raw_dur = step.fields.get("duration", "")
        if ":" in raw_dur:
            try:
                m, s = raw_dur.split(":")
                dur_s = float(m) * 60 + float(s)
            except ValueError:
                pass
        cumul += dur_s
        marker = "T+" + _format_duration(cumul - dur_s)
        print(
            f"  {i + 1:>2}. {marker:>7}  {bpm:>5}  {ck:>3}  {en:>6}  "
            f"{_track_label(step.slug, step.fields, 45)}"
        )
        if step.transition_from_prev:
            ts = step.transition_from_prev
            print(f"        transition: {ts.total:.2f}  ({' '.join(ts.notes)})")

    if export_m3u8:
        out_path = Path(export_m3u8)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(to_m3u8(playlist, MIX_DIR), encoding="utf-8")
        print(f"\n[export] M3U8 ecrit : {out_path}")
    return 0


_INFER_FIELDS = ("genre", "energy", "mood", "tags")


def cmd_infer(
    entries: dict[str, dict[str, str]],
    fields: tuple[str, ...],
    force: bool,
) -> int:
    """Remplit genre / energy / mood / tags depuis les sidecars Phase 1+2."""
    no_sidecar: list[str] = []
    counts: dict[str, int] = {f: 0 for f in fields}

    for slug, entry in entries.items():
        sidecar = load_sidecar(QUALITY_DIR, slug)
        if not sidecar:
            no_sidecar.append(slug)
            continue
        for field in fields:
            current = entry.get(field, "").strip()
            if current and not force:
                continue
            if field == "energy":
                value = infer_energy(sidecar, entry)
            elif field == "mood":
                value = infer_mood(sidecar, entry)
            elif field == "genre":
                value = infer_genre(sidecar, entry)
            elif field == "tags":
                value = infer_tags(sidecar)
            else:
                continue
            # On n'ecrit jamais vide : protege les editions manuelles meme
            # sous --force. Pour clearer un champ, edite library.md a la main.
            if not value:
                continue
            update_field(LIBRARY_FILE, slug, field, value)
            counts[field] += 1

    print("Infer termine :")
    for field, n in counts.items():
        print(f"  {field:<6} : {n} entree(s) mises a jour")
    if no_sidecar:
        print(f"\n{len(no_sidecar)} entree(s) sans sidecar (lance analyze.py --all) :")
        for slug in no_sidecar:
            print(f"  - {slug}")
    return 0


def cmd_describe(entries: dict[str, dict[str, str]], force: bool) -> int:
    """Remplit `about` via MusicBrainz pour chaque artist unique."""
    # Regroupe par artiste unique pour limiter les requetes
    artists_to_lookup: dict[str, list[str]] = {}  # primary_artist -> [slugs]
    for slug, fields in entries.items():
        if fields.get("about") and not force:
            continue
        artist = fields.get("artist", "").strip()
        if not artist:
            continue
        from analyzer.describe import primary_artist
        key = primary_artist(artist)
        artists_to_lookup.setdefault(key, []).append(slug)

    if not artists_to_lookup:
        print("Toutes les entrees ont deja un `about` (utilise --force pour ecraser).")
        return 0

    print(f"[describe] {len(artists_to_lookup)} artiste(s) a interroger sur MusicBrainz")
    print(f"           (rate-limit 1 req/sec, ~{len(artists_to_lookup)}s d'attente)\n")

    found = 0
    for artist_name, slugs in artists_to_lookup.items():
        about = describe_artist(artist_name, ARTISTS_DIR, rate_limit=True)
        marker = about if about else "(aucun)"
        print(f"  {artist_name:<35} -> {marker}")
        if about:
            for slug in slugs:
                update_field(LIBRARY_FILE, slug, "about", about)
            found += 1

    print(f"\n[describe] {found}/{len(artists_to_lookup)} artistes resolus")
    return 0


def cmd_keys(entries: dict[str, dict[str, str]]) -> int:
    """Inventaire des keys de la library + Camelot."""
    counts: dict[str, list[str]] = {}
    no_key: list[str] = []
    for slug, fields in entries.items():
        key = fields.get("key", "").strip()
        if not key:
            no_key.append(slug)
            continue
        ck = to_camelot(key)
        bucket = f"{key} ({ck or '?'})"
        counts.setdefault(bucket, []).append(slug)
    print(f"Keys ({len(entries) - len(no_key)} renseignees) :\n")
    for bucket in sorted(counts):
        slugs = counts[bucket]
        print(f"  {bucket:<20}  {len(slugs):>2}x")
        for s in slugs:
            print(f"      - {_track_label(s, entries[s], 55)}")
    if no_key:
        print(f"\nSans key renseignee : {len(no_key)}")
        for s in no_key:
            print(f"  - {_track_label(s, entries[s], 55)}")
    return 0


def _load_signatures(
    entries: dict[str, dict[str, str]],
) -> tuple[list[tuple[str, RhythmSignatureReport]], list[str]]:
    """Charge les signatures rythmiques depuis les sidecars.

    Retourne (signatures valides, slugs sans signature exploitable)."""
    sigs: list[tuple[str, RhythmSignatureReport]] = []
    missing: list[str] = []
    for slug in entries:
        sidecar = load_sidecar(QUALITY_DIR, slug)
        raw = (sidecar or {}).get("rhythm_signature")
        if not raw or not raw.get("bars_used"):
            missing.append(slug)
            continue
        try:
            sigs.append((slug, RhythmSignatureReport(**raw)))
        except (TypeError, ValueError):
            missing.append(slug)
    return sigs, missing


def cmd_similar(
    entries: dict[str, dict[str, str]],
    target_slug: str,
    n: int,
) -> int:
    """Voisins par groove (signature rythmique), independamment du BPM/key."""
    if target_slug not in entries:
        print(f"[ERROR] slug introuvable : {target_slug}", file=sys.stderr)
        return 1

    sigs, missing = _load_signatures(entries)
    sig_map = dict(sigs)
    if target_slug not in sig_map:
        print(
            f"[ERROR] pas de signature rythmique pour {target_slug} "
            f"(lance analyze.py {target_slug}).",
            file=sys.stderr,
        )
        return 1

    target = sig_map[target_slug]
    print(f"Voisins de groove : {_track_label(target_slug, entries[target_slug], 55)}")
    print(f"  sub : {to_sparkline(target.sub_pattern)}")
    print(
        f"  syncope={target.syncopation:.2f}  pulse={target.pulse_clarity:.2f}"
        f"  swing={target.swing:.2f}\n"
    )

    scored = [
        (rhythm_distance(target, sig), slug)
        for slug, sig in sigs
        if slug != target_slug
    ]
    scored.sort(key=lambda x: x[0])

    print(f"{'dist':>5}  {'bpm':>5}  {'key':>3}  groove (sub)        track")
    print("-" * 78)
    for dist, slug in scored[:n]:
        fields = entries[slug]
        bpm_v = fields.get("bpm", "?")[:5]
        ck_v = to_camelot(fields.get("key")) or "?"
        spark = to_sparkline(sig_map[slug].sub_pattern)
        print(
            f"{dist:>5.3f}  {bpm_v:>5}  {ck_v:>3}  {spark}  "
            f"{_track_label(slug, fields, 32)}"
        )
    if missing:
        print(f"\n{len(missing)} track(s) sans signature (lance analyze.py --all).")
    return 0


def cmd_groove_clusters(
    entries: dict[str, dict[str, str]],
    k: int,
    write: bool,
) -> int:
    """Regroupe la library en familles de groove (clustering agglomeratif).

    Indicatif : sur une petite library, ~5-8 familles restent lisibles."""
    sigs, missing = _load_signatures(entries)
    if len(sigs) < 2:
        print("[ERROR] pas assez de signatures (lance analyze.py --all).",
              file=sys.stderr)
        return 1

    labels = cluster(sigs, k)
    families: dict[int, list[str]] = {}
    for slug, label in labels.items():
        families.setdefault(label, []).append(slug)

    print(f"{len(families)} famille(s) de groove sur {len(sigs)} tracks "
          f"(indicatif) :\n")
    sig_map = dict(sigs)
    for label in sorted(families):
        members = families[label]
        print(f"== groove #{label}  ({len(members)} tracks)")
        for slug in sorted(members):
            spark = to_sparkline(sig_map[slug].sub_pattern)
            bpm_v = entries[slug].get("bpm", "?")[:5]
            print(f"   {spark}  {bpm_v:>5}  {_track_label(slug, entries[slug], 40)}")
            if write:
                update_field(LIBRARY_FILE, slug, "groove_cluster", str(label))
        print()

    if write:
        print(f"[library] champ groove_cluster ecrit pour {len(labels)} tracks.")
    else:
        print("(--write pour ecrire groove_cluster dans library.md)")
    if missing:
        print(f"{len(missing)} track(s) sans signature (ignorees).")
    return 0


# ---------------------------------------------------------------------------
# Argparse
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Set builder : doublons, compatibilite, playlist depuis library.md.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("duplicates", help="Liste les doublons detectes")

    sp_c = sub.add_parser("compatible", help="Tracks compatibles avec un slug")
    sp_c.add_argument("slug", help="Slug du track de reference (artist_-_title)")
    sp_c.add_argument("-n", type=int, default=10, help="Nombre de candidats (defaut 10)")
    sp_c.add_argument("--energy", choices=["rising", "maintain", "falling"],
                      default="maintain")
    sp_c.add_argument("--min-score", type=float, default=0.4,
                      help="Score minimum pour afficher (defaut 0.4)")

    sp_p = sub.add_parser("playlist", help="Genere une playlist depuis un slug")
    sp_p_target = sp_p.add_mutually_exclusive_group(required=True)
    sp_p_target.add_argument("--start", help="Slug de depart (build forward)")
    sp_p_target.add_argument("--peak",
                             help="Slug 'point d'orgues' a la fin du set "
                                  "(build backward avec energie montante)")
    sp_p.add_argument("--duration", type=float, default=60.0,
                      help="Duree cible en minutes (defaut 60)")
    sp_p.add_argument("--energy", choices=["rising", "maintain", "falling"],
                      default="rising",
                      help="Direction d'energie (ignore si --peak).")
    sp_p.add_argument("--min-score", type=float, default=0.4)
    sp_p.add_argument("--max-track", type=float, default=15.0,
                      help="Duree max d'un track candidat en minutes (defaut 15).")
    sp_p.add_argument("--export-m3u8",
                      help="Chemin de sortie pour un fichier .m3u8 importable "
                           "dans Mixxx (File -> Import Playlist).")

    sub.add_parser("keys", help="Inventaire des keys de la library")

    sp_s = sub.add_parser("similar",
                          help="Voisins par groove (signature rythmique)")
    sp_s.add_argument("slug", help="Slug du track de reference")
    sp_s.add_argument("-n", type=int, default=8,
                      help="Nombre de voisins (defaut 8)")

    sp_gc = sub.add_parser("groove-clusters",
                           help="Regroupe la library en familles de groove")
    sp_gc.add_argument("--k", type=int, default=6,
                       help="Nombre de familles (defaut 6)")
    sp_gc.add_argument("--write", action="store_true",
                       help="Ecrit groove_cluster dans library.md.")

    sp_i = sub.add_parser("infer", help="Auto-remplit energy / mood / tags")
    sp_i.add_argument(
        "--field",
        choices=("genre", "energy", "mood", "tags", "all"),
        default="all",
        help="Quel champ inferer (defaut: tous).",
    )
    sp_i.add_argument("--force", action="store_true",
                      help="Ecrase meme si la valeur existante est non vide.")

    sp_d = sub.add_parser("describe",
                          help="Remplit `about` via MusicBrainz pour chaque artiste")
    sp_d.add_argument("--force", action="store_true",
                      help="Ecrase meme si la valeur existante est non vide.")

    args = parser.parse_args()
    entries = parse_library(LIBRARY_FILE)
    if not entries:
        print("[ERROR] library.md vide ou introuvable", file=sys.stderr)
        return 1

    if args.cmd == "duplicates":
        return cmd_duplicates(entries)
    if args.cmd == "compatible":
        return cmd_compatible(
            entries, args.slug, args.n, args.energy, args.min_score,
        )
    if args.cmd == "playlist":
        return cmd_playlist(
            entries, args.start, args.peak, args.duration, args.energy,
            args.min_score, args.max_track, args.export_m3u8,
        )
    if args.cmd == "keys":
        return cmd_keys(entries)
    if args.cmd == "similar":
        return cmd_similar(entries, args.slug, args.n)
    if args.cmd == "groove-clusters":
        return cmd_groove_clusters(entries, args.k, args.write)
    if args.cmd == "infer":
        fields = _INFER_FIELDS if args.field == "all" else (args.field,)
        return cmd_infer(entries, fields, args.force)
    if args.cmd == "describe":
        return cmd_describe(entries, args.force)
    return 1


if __name__ == "__main__":
    sys.exit(main())

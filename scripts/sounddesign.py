#!/usr/bin/env python3
"""Sound design : nouveaux samples par chaines de plugins (Phase 8).

Un traitement (ex. `rumble`) part d'un sample de la library, le passe dans
les chaines d'un preset (pedalboard + devices maison) et ecrit une boucle
48 kHz / 24 bits avec son sidecar. Moteur : `analyzer/sounddesign.py`.

Usage:
    sounddesign.py list                          # traitements et presets
    sounddesign.py devices                       # catalogue des devices et parametres
    sounddesign.py render rumble deep --source "Drumbrute kick/KIK DB 160 (1).wav"
    sounddesign.py render rumble deep --source <wav> --set bpm=185 --set bars=2
    sounddesign.py render rumble kick_rumble --source <wav> --mute Kick --bypass Rumble:2
    sounddesign.py render rumble deep --source <wav> --dry-run   # rendu sans ecriture
    sounddesign.py render rumble deep --source <wav> --verse     # + copie dans le pack
    sounddesign.py render rumble deep --source <wav> --name "RM 150 Fat dbr"
    sounddesign.py render riser white_sweep --set bars=8      # bruit genere, sans --source
    sounddesign.py render riser pad_lift --source <wav>       # nappe qui monte (FX/RISE)
                                                  # Samples/SoundDesign (relancer samples.py)

`--source` : chemin absolu, ou relatif a `<MEDIA>/Samples`.
`--bypass CHAINE:INDEX` : index du device dans la chaine (0 = premier),
`master:INDEX` pour la chaine de sortie.

Fichiers :
    library/sounddesign/presets/<traitement>/<id>.json      # presets (vault)
    <MEDIA>/SoundDesign/<traitement>/<nom DT2> <hash>.wav (+ .json)
    <MEDIA>/Samples/SoundDesign/<traitement>/<nom DT2> <hash>.wav    # --verse

Nom DT2 propose (8.E) : celui de la source avec le code du traitement et le
tempo (`BD C Punch 01 dbr` -> `RM 150 C Punch dbr`), `--name` pour le forcer ;
`--verse` le range par override dans DRUMS/RM/<sous-dossier de la source>
(riser : FX/RISE, `FX 150 Rise Noise` sans source).

Automation (8.G) : un device pedalboard d'un preset peut porter
`params_end` (valeurs atteintes en fin de rendu, interpolees selon la
courbe du traitement ; geometriquement pour les frequences).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from analyzer.sounddesign import (
    NO_SOURCE,
    SR,
    TREATMENTS,
    PresetError,
    SourceError,
    device_specs,
    load_presets,
    load_source,
    needs_source,
    render,
    target,
    verse,
    with_overrides,
    write_render,
)
from analyzer.samples import Manifest
from samples import MANIFEST_FILE, OVERRIDES_FILE, load_manifest, load_overrides, save_overrides
from paths import SAMPLES_SRC_DIR, SOUNDDESIGN_OUT_DIR, SOUNDDESIGN_PRESETS_DIR, media_ok, media_relative


def _cmd_list() -> int:
    for treatment in TREATMENTS.values():
        spec = treatment.spec
        print(f"{spec.id} — {spec.label} : {spec.summary}")
        print(f"  source : {spec.source_hint} ; notebook : {spec.notebook}")
        print("  reglages : " + ", ".join(f"{s.name}={s.default:g}" for s in spec.settings))
        for preset in load_presets(spec.id, SOUNDDESIGN_PRESETS_DIR):
            chains = ", ".join(f"{c.name}{' (mute)' if c.mute else ''}" for c in preset.chains)
            print(f"  - {preset.id} : {preset.label} [{chains}]")
    return 0


def _cmd_devices() -> int:
    for spec in device_specs():
        print(f"{spec.type} — {spec.label} : {spec.help}")
        for p in spec.params:
            if p.choices:
                print(f"    {p.name} = {p.default:g} : " + ", ".join(f"{i}={c}" for i, c in enumerate(p.choices)))
            else:
                print(f"    {p.name} = {p.default:g} {p.unit} [{p.min:g} .. {p.max:g}]".rstrip())
    return 0


def _parse_set(items: list[str]) -> dict[str, float]:
    out: dict[str, float] = {}
    for item in items:
        name, sep, value = item.partition("=")
        if not sep:
            raise PresetError(f"--set attend NOM=VALEUR, recu {item!r}")
        out[name] = float(value)
    return out


def _parse_bypass(items: list[str]) -> list[tuple[str, int]]:
    out = []
    for item in items:
        name, sep, index = item.rpartition(":")
        if not sep or not index.isdigit():
            raise PresetError(f"--bypass attend CHAINE:INDEX, recu {item!r}")
        out.append((name, int(index)))
    return out


def _cmd_render(args: argparse.Namespace) -> int:
    if not media_ok():
        return 1
    presets = {p.id: p for p in load_presets(args.treatment, SOUNDDESIGN_PRESETS_DIR)}
    if args.preset not in presets:
        print(f"preset inconnu {args.preset!r} (connus : {sorted(presets)})", file=sys.stderr)
        return 1
    preset = with_overrides(presets[args.preset], _parse_set(args.set), args.mute,
                            _parse_bypass(args.bypass))
    source: Path | None = None
    if needs_source(preset):
        if not args.source:
            raise SourceError(f"{preset.treatment}/{preset.id} demande un sample : --source")
        source = Path(args.source)
        if not source.is_absolute():
            source = SAMPLES_SRC_DIR / source
    audio = render(preset, load_source(source) if source else NO_SOURCE)
    rel = (source.relative_to(SAMPLES_SRC_DIR).as_posix()
           if source and source.is_relative_to(SAMPLES_SRC_DIR) else "")
    manifest = load_manifest(MANIFEST_FILE) or Manifest(source_root=str(SAMPLES_SRC_DIR), total=0)
    name, sub_dir = target(rel, manifest, preset.treatment, preset.settings.get("bpm"))
    name = args.name or name
    print(f"{preset.treatment}/{preset.id} : {audio.shape[1] / SR:.3f} s, "
          f"{len(preset.chains) - sum(c.mute for c in preset.chains)} chaine(s) active(s), "
          f"nom {name!r}, sous-dossier {sub_dir or '(racine)'}")
    if args.dry_run:
        return 0
    record = write_render(audio, media_relative(source) if source else "", preset, SOUNDDESIGN_OUT_DIR, name, sub_dir)
    print(f"-> {SOUNDDESIGN_OUT_DIR / record.file}")
    if args.verse:
        overrides = load_overrides(OVERRIDES_FILE)
        key = verse(record, SOUNDDESIGN_OUT_DIR, SAMPLES_SRC_DIR, overrides)
        save_overrides(overrides, OVERRIDES_FILE)
        print(f"-> verse : Samples/{key} (relancer samples.py pour le classer)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Sound design par chaines de plugins.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="traitements et presets")
    sub.add_parser("devices", help="catalogue des devices")
    r = sub.add_parser("render", help="rend une boucle a partir d'un sample")
    r.add_argument("treatment", choices=sorted(TREATMENTS))
    r.add_argument("preset")
    r.add_argument("--source", help="wav source (absolu ou relatif a <MEDIA>/Samples) ; "
                                    "facultatif si le preset n'en demande pas (riser sur bruit)")
    r.add_argument("--set", action="append", default=[], metavar="NOM=VALEUR",
                   help="reglage du traitement (bpm, bars...)")
    r.add_argument("--mute", action="append", default=[], metavar="CHAINE")
    r.add_argument("--bypass", action="append", default=[], metavar="CHAINE:INDEX")
    r.add_argument("--dry-run", action="store_true", help="rend sans ecrire")
    r.add_argument("--verse", action="store_true",
                   help="copie aussi le rendu dans le pack Samples/SoundDesign")
    r.add_argument("--name", help="nom DT2 (defaut : propose a partir de la source)")
    args = parser.parse_args()
    try:
        if args.cmd == "list":
            return _cmd_list()
        if args.cmd == "devices":
            return _cmd_devices()
        return _cmd_render(args)
    except (PresetError, SourceError) as exc:
        print(f"[sounddesign] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

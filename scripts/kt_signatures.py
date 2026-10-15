"""Passe rhythm_signature pour les KT théorie (SPEC 7.M, décision 4).

Lit les sidecars `library/quality/<slug>.json` des morceaux de référence de
chaque style et imprime, en markdown, leurs patterns 16 pas par bande
(`X` ≥ 0,6, `x` ≥ 0,3, `.` sinon), la syncope, le swing (0,5 = droit,
> 0,5 = énergie sur le « a » qui précède le temps) et la clarté de pulsation,
puis la moyenne du style. Sortie à coller dans `digitakt/kb/theorie/_index.md`.

    python kt_signatures.py            # tous les styles
    python kt_signatures.py tribe dnb  # certains styles
    python kt_signatures.py --harmony  # passe harmonique (gamme, accords)

Passe harmonique (lot 2, KT5-KT9) : gamme detectee (`harmony.scale` du
sidecar, score et incertitude) et accords distincts de la section principale
(`harmony.progression`), pour comparer la theorie des modes aux morceaux.
"""

from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Préfixes de slugs (globs) des morceaux de référence, par style.
STYLES: dict[str, list[str]] = {
    "tribe": [
        "floxytek_-_micro_tribe",
        "floxytek_-_roots",
        "kodaman_-_beton",
        "area_23_-_indian_tribe",
        "apre_-_contrast",
        "liberte_naturel_-_tracknard",
        "tekotak_-_lokapi",
    ],
    "acidcore_mental": [
        "six_ou_sept_-_acid_pirate",
        "nailik_hypnotik_-_nailik_le_renard",
        "*diuko303_-_diuko_mirages",
        "captain_303_-_acidcore",
        "luche_-_whispers_farfa",
        "spice_up_teksa_vorteks_-_soldiers",
        "ktc_smk_-_ktc_cykada",
        "berio_-_path",
    ],
    "tekno_rapide": [
        "unkomun_-_akira",
        "ciklo_-_vrech",
        "moldetek_-_cybertekno",
        "neurotribe_kokko_-_neurotribe_vs_kokko",
        "a_laan_-_live_extract",
        "axolotl_-_remix_psylotribe",
    ],
    "hard_techno": ["beauz_-_bel_mercy"],
    "hardcore": ["maureen_-_kompet_x_jiggle", "mad_dog_-_wild_for_the_night"],
    "dnb": [
        "dimension_-_uk",
        "document_one_-_1964",
        "tim_reaper_-_scorched_earth_a2",
        "noisia_-_the_hole_pt_1",
        "dizrupt_mkjay_-_room_service",
    ],
    "dubstep": [
        "2hot2play_-_keep_the_balance",
        "densha_crisis_-_monster",
        "excision_downlink_-_resistance",
        "utk_-_kaiono",
    ],
    "techno_lente_dub": ["*polar_inertia_-_hell*", "*kangding_ray*"],
}


def glyph(value: float) -> str:
    """Un pas en glyphe : `X` fort, `x` présent, `.` vide."""
    return "X" if value >= 0.6 else ("x" if value >= 0.3 else ".")


def row(pattern: list[float]) -> str:
    return "".join(glyph(v) for v in pattern)


def report(style: str, patterns: list[str]) -> list[str]:
    """Lignes markdown d'un style : une ligne par morceau, puis la moyenne."""
    lines = [
        f"### {style}",
        "",
        "| morceau | BPM | sub | mid | high | sync | swing | pulse |",
        "|---|---|---|---|---|---|---|---|",
    ]
    acc = {k: [0.0] * 16 for k in ("sub", "mid", "high")}
    n = 0
    for pat in patterns:
        files = sorted(glob.glob(str(ROOT / "library" / "quality" / f"{pat}*.json")))
        if not files:
            lines.append(f"| `{pat}` | | absent de la library | | | | | |")
            continue
        data = json.loads(Path(files[0]).read_text())
        sig = data.get("rhythm_signature")
        if not sig:
            lines.append(f"| `{pat}` | | sans signature | | | | | |")
            continue
        bpm = (data.get("beats") or {}).get("tempo_bpm", "")
        slug = Path(files[0]).stem
        lines.append(
            f"| {slug[:40]} | {bpm} | `{row(sig['sub_pattern'])}` | `{row(sig['mid_pattern'])}` | "
            f"`{row(sig['high_pattern'])}` | {sig['syncopation']:.2f} | {sig['swing']:.2f} | "
            f"{sig['pulse_clarity']:.2f} |"
        )
        for k in acc:
            acc[k] = [a + b for a, b in zip(acc[k], sig[f"{k}_pattern"])]
        n += 1
    if n:
        mean = {k: [v / n for v in acc[k]] for k in acc}
        lines.append(
            f"| **moyenne ({n})** | | `{row(mean['sub'])}` | `{row(mean['mid'])}` | "
            f"`{row(mean['high'])}` | | | |"
        )
    lines.append("")
    return lines


def harmony_report(style: str, patterns: list[str]) -> list[str]:
    """Lignes markdown : gamme detectee et accords de la section principale."""
    lines = [
        f"### {style}",
        "",
        "| morceau | gamme détectée | score | accords (section principale) |",
        "|---|---|---|---|",
    ]
    for pat in patterns:
        files = sorted(glob.glob(str(ROOT / "library" / "quality" / f"{pat}*.json")))
        if not files:
            lines.append(f"| `{pat}` | absent de la library | | |")
            continue
        data = json.loads(Path(files[0]).read_text())
        harm = data.get("harmony") or {}
        scale = harm.get("scale") or {}
        prog = harm.get("progression") or []
        main_sec = next((p for p in prog if p.get("label") == "main"), prog[0] if prog else None)
        chords = (main_sec or {}).get("chords") or []
        distinct = [c for i, c in enumerate(chords) if i == 0 or c != chords[i - 1]]
        score = f"{scale['score']:.2f}" if "score" in scale else ""
        if scale.get("uncertain"):
            score += " (incertain)"
        lines.append(
            f"| {Path(files[0]).stem[:40]} | {scale.get('label', 'sans analyse')} | {score} | "
            f"{' '.join(distinct[:8]) or '—'} |"
        )
    lines.append("")
    return lines


def main(argv: list[str]) -> int:
    harmony = "--harmony" in argv
    argv = [a for a in argv if a != "--harmony"]
    wanted = argv or list(STYLES)
    unknown = [s for s in wanted if s not in STYLES]
    if unknown:
        print(f"styles inconnus : {', '.join(unknown)} (connus : {', '.join(STYLES)})")
        return 2
    for style in wanted:
        fn = harmony_report if harmony else report
        print("\n".join(fn(style, STYLES[style])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

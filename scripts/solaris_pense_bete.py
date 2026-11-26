"""Génère le pense-bête du live solaris : une page A4 paysage en couleur (SVG imprimable).

Quatre blocs : déroulé des banques, chrono, notes par banque, grille des 16 tracks.
Les tableaux sont recopiés de digitakt/doctrine-dt2-solaris.md, qui fait foi
(grille : digitakt/doctrine.md §1).
"""

from __future__ import annotations

import pathlib
import re
from xml.sax.saxutils import escape

W, H, M = 1123, 794, 32  # A4 paysage à 96 dpi, marge
FONT = "Helvetica, Arial, sans-serif"
INK, GREY, RULE = "#1a1a1a", "#5a5a5a", "#b5b5b5"
OUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "digitakt"

# Couleur par tonalité : (accent, teinte claire)
TON = {"fa": ("#1f5fa8", "#e1ecf9"), "la#": ("#1e7a4a", "#ddf1e5")}
# Couleur de chaque banque (nuances de la tonalité)
SEC = {"B": "#4a86c8", "C": "#3fa36f", "D": "#12523a", "E": "#1f5fa8", "F": "#163a6b"}
SEC_TON = {"B": "fa", "C": "la#", "D": "la#", "E": "fa", "F": "fa"}
PHRYG = "#d97706"  # seconde phrygienne
SENS = "#7a3fb0"  # sensible du mineur harmonique


def markup(s: str, bold_prefix: str = "") -> str:
    """Échappe le texte, resserre le ♭ (glyphe de repli trop large) et met un préfixe en gras."""
    rest = s
    head = ""
    if bold_prefix and s.startswith(bold_prefix):
        head = f'<tspan font-weight="bold">{escape(bold_prefix)}</tspan>'
        rest = s[len(bold_prefix):]
    body = escape(rest)
    body = re.sub(r"♭(.?)", lambda m: '<tspan dx="-0.12em">♭</tspan>'
                  + (f'<tspan dx="-0.12em">{m.group(1)}</tspan>' if m.group(1) else ""), body)
    return head + body


class Page:
    def __init__(self) -> None:
        self.out: list[str] = []

    def raw(self, s: str) -> None:
        self.out.append(s)

    def text(self, x: float, y: float, s: str, size: float = 10, weight: str = "normal",
             fill: str = INK, anchor: str = "start", bold_prefix: str = "") -> None:
        self.raw(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" '
                 f'fill="{fill}" text-anchor="{anchor}">{markup(s, bold_prefix)}</text>')

    def rect(self, x: float, y: float, w: float, h: float, fill: str, stroke: str = "none",
             sw: float = 0, rx: float = 0) -> None:
        self.raw(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def svg(self) -> str:
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="297mm" height="210mm" '
                f'viewBox="0 0 {W} {H}" font-family="{FONT}">\n'
                f'<rect width="{W}" height="{H}" fill="white"/>\n' + "\n".join(self.out) + "\n</svg>\n")


def wrap(s: str, width_px: float, size: float) -> list[str]:
    """Découpe en lignes selon une largeur moyenne de caractère (0,52 em)."""
    maxc = max(6, int(width_px / (size * 0.52)))
    lines: list[str] = []
    cur = ""
    for w in s.split():
        if cur and len(cur) + 1 + len(w) > maxc:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    if cur:
        lines.append(cur)
    return lines


def header(p: Page, subtitle: str) -> float:
    for i, k in enumerate("BCDEF"):  # bandeau aux couleurs des banques
        p.rect(i * W / 5, 0, W / 5 + 1, 8, SEC[k])
    p.text(M, M + 16, "SOLARIS — live Digitakt II", 20, "bold")
    p.text(M + 290, M + 16, subtitle, 11.5, "bold", fill=GREY)
    p.text(W - M, M + 16, "pense-bête · plan du 2026-11-26 · 1h05-1h30 · fa → la# → fa", 10, fill=GREY, anchor="end")
    p.raw(f'<line x1="{M}" y1="{M+26}" x2="{W-M}" y2="{M+26}" stroke="{INK}" stroke-width="1.2"/>')
    return M + 44


def footer(p: Page, y_used: float) -> None:
    assert y_used <= H - M - 22, f"déborde : {y_used:.0f}"
    p.raw(f'<line x1="{M}" y1="{H-M-14}" x2="{W-M}" y2="{H-M-14}" stroke="{RULE}" stroke-width="0.5"/>')
    p.text(M, H - M - 2, "Source : digitakt/doctrine-dt2-solaris.md (fait foi) · doctrine générale §1, §10, §11 · "
           "KT5 · kb/tutos/maison-groove-tribe-battement", 7.5, fill=GREY)
    p.text(W - M, H - M - 2, "A4 paysage · imprimer à 100 % · couleur", 7.5, fill=GREY, anchor="end")


def title(p: Page, x: float, y: float, s: str, width: float | None = None, color: str = INK) -> float:
    x2 = x + width if width else W - M
    p.rect(x, y - 12, 5, 16, color)
    p.text(x + 11, y, s.upper(), 12, "bold", fill=color)
    p.raw(f'<line x1="{x}" y1="{y+7}" x2="{x2}" y2="{y+7}" stroke="{color}" stroke-width="0.9"/>')
    return y + 22


def bullets(p: Page, x: float, y: float, items: list[str], width: float, size: float = 10,
            lh: float = 12.6, gap: float = 4, mark: str = INK) -> float:
    for it in items:
        lines = wrap(it, width - 12, size)
        p.raw(f'<circle cx="{x+3}" cy="{y+size-3.5}" r="2.4" fill="{mark}"/>')
        for line in lines:
            p.text(x + 12, y + size, line, size)
            y += lh
        y += gap
    return y


def chip(p: Page, x: float, y: float, w: float, h: float, label: str, color: str, size: float = 13) -> None:
    p.rect(x, y, w, h, color, rx=3)
    p.text(x + w / 2, y + h / 2 + size * 0.36, label, size, "bold", fill="white", anchor="middle")


# ======================================================================== la page
AEOL = ["1", "2", "♭3", "4", "5", "♭6", "♭7"]
PHRY = ["1", "♭2", "♭3", "4", "5", "♭6", "♭7"]
HARM = ["1", "2", "♭3", "4", "5", "♭6", "7"]


def page() -> str:
    p = Page()
    y = header(p, "déroulé, chrono, notes, tracks")

    # ------------------------------------------------------------ 1. déroulé
    y = title(p, M, y, "1. Déroulé, banques B → F (A vide)")
    cols = ["", "Banque · section", "BPM", "Durée", "Tonalité · KB SCALE", "Kick / sub", "Temps · croche · mes.", "Contenu clé"]
    widths = [30, 112, 62, 58, 158, 122, 132]
    widths.append(W - 2 * M - sum(widths))
    rows = [
        ["B", "Flatiron · half-time", "160 (ressenti 80)", "10-15 min", "fa min. harmonique · HARMONIC MINOR, F", "F1 43,7 Hz, rumbles en fa", "375 · 187,5 · 1 500 ms", "Intro drone seul, kick lourde jusqu'à un temps, snare sur le 3, montée ; dernier pattern hybride : stab do# puis kick la# entrent"],
        ["C", "Davyl · techno", "142", "10-15 min", "la# éolien · AEOLIAN, A#", "B♭1 58,3 Hz, kick glissant", "422,5 · 211,3 · 1 690 ms", "Kick-sub + stab do#2 (~150 ms) sur 3, 7, 11, 15 + charley : trois tracks, sans rumble"],
        ["D", "A Virus · acid", "154", "20-25 min", "la# phrygien · PHRYGIAN, A#", "B♭1 58,3 Hz ; rien en fin", "389,6 · 194,8 · 1 558 ms", "Cœur du set : l'acid entre en B♭, do♭ frotté ; fin en respiration : kick allégée, drone la#, triton mi (NOTE chromatique), montée sur fa + silence"],
        ["E", "Neptune · tribe", "160", "10-15 min", "fa min. harmonique · HARMONIC MINOR, F", "F1 43,7 Hz, kickbass ≤ 360 ms", "375 · 187,5 · 1 500 ms", "Tribe percussive et bruitée, kickbass à longue queue, percs tribales, rolls, triolets ; dernier pattern où les breaks s'annoncent"],
        ["F", "Ominous · DnB", "170", "15-20 min", "fa phrygien · PHRYGIAN, F", "F1 43,7 Hz", "352,9 · 176,5 · 1 412 ms", "Gros kick régulier, breaks découpés, reese fa / sol♭, de plus en plus sale ; pattern de fin"],
    ]
    size, lh, pad = 9.4, 11.2, 3.5
    xs = [M]
    for w in widths[:-1]:
        xs.append(xs[-1] + w)
    for cx, c in zip(xs, cols):
        p.text(cx + pad, y + size, c, size, "bold", fill=GREY)
    y += size + 5
    for row in rows:
        bq = row[0]
        tint = TON[SEC_TON[bq]][1]
        cells = [wrap(c, w - 2 * pad, size) for c, w in zip(row[1:], widths[1:])]
        rh = max(len(c) for c in cells) * lh + 2 * pad + 1
        p.rect(M, y, W - 2 * M, rh, tint)
        p.raw(f'<line x1="{M}" y1="{y+rh}" x2="{W-M}" y2="{y+rh}" stroke="white" stroke-width="2"/>')
        chip(p, M + 2, y + 3, 26, rh - 6, bq, SEC[bq], 15)
        for k, (cx, lines) in enumerate(zip(xs[1:], cells), start=1):
            bold = k in (1, 4)
            color = TON[SEC_TON[bq]][0] if k == 4 else INK
            for j, line in enumerate(lines):
                p.text(cx + pad, y + pad + size + j * lh, line, size, "bold" if bold else "normal", fill=color)
        y += rh
    y += 18

    # ------------------------------------------------------------ 2. chrono
    segs = [("B", "Flatiron", 15, 160), ("C", "Davyl", 15, 142), ("D", "A Virus", 25, 154),
            ("E", "Neptune", 15, 160), ("F", "Ominous", 20, 170)]
    total = sum(s[2] for s in segs)
    y = title(p, M, y, f"2. Chrono indicatif (durées hautes, {total} min) et sauts de tempo")
    bw, x, bh, start = W - 2 * M, float(M), 34, 0
    prev = None
    for bq, name, dur, bpm in segs:
        w = bw * dur / total
        p.rect(x, y, w - 2, bh, SEC[bq])
        p.text(x + 6, y + 14, f"{bq} {name}", 10.5, "bold", fill="white")
        jump = "" if prev is None else f" ({bpm - prev:+d})".replace("-", "− ").replace("+", "+ ")
        p.text(x + 6, y + 27, f"{dur} min · {bpm} BPM{jump}", 9, fill="white")
        ton = SEC_TON[bq]
        mode = {"B": "harm.", "C": "éolien", "D": "phr.", "E": "harm.", "F": "phr."}[bq]
        p.rect(x, y + bh + 2, w - 2, 15, TON[ton][1])
        p.text(x + w / 2, y + bh + 13, f"{ton} {mode}", 9.5, "bold", fill=TON[ton][0], anchor="middle")
        p.text(x, y + bh + 29, f"{start}'", 9, fill=GREY)
        x += w
        start += dur
        prev = bpm
    p.text(W - M, y + bh + 29, f"{total}'", 9, fill=GREY, anchor="end")
    y += bh + 38
    y = bullets(p, M, y, [
        "À ne pas rater : la note tenue (pas le mi) sur la chute à 142 (B → C), le saut à 154 sur une coupure et le do♭ (C → D), "
        "la respiration puis fa tenue et retombée en fa à 160 (D → E), kick et sub en fa tenus pendant le saut à 170 (E → F). "
        "Tempo fixe dans une banque.",
    ], W - 2 * M, size=9.6, lh=12, mark="#c0392b")
    y += 20

    # ------------------------------------------------------------ 3. notes (gauche) / 4. grille (droite)
    gw = 286  # largeur de la colonne grille
    gap = 24
    nw = W - 2 * M - gw - gap
    xg = M + nw + gap
    y_cols = y
    y = title(p, M, y, "3. Notes par banque (sous 120 Hz : tonique seule)", nw)
    scales = [
        ("B", "fa min. harm.", "HARMONIC MINOR, F", "F G A♭ B♭ C D♭ E", HARM, "F2, C, F3 ; E passage vers F · A♭, D♭ lentes"),
        ("C", "la# éolien", "AEOLIAN, A#", "B♭ C D♭ E♭ F G♭ A♭", AEOL, "stab D♭2 dans le sub (écart voulu : c'est le battement)"),
        ("D", "la# phrygien", "PHRYGIAN, A#", "B♭ C♭ D♭ E♭ F G♭ A♭", PHRY, "B♭2, F, B♭3 · acid en B♭, C♭ (= B) frottée ; fin : drone B♭, triton E hors gamme"),
        ("E", "fa min. harm.", "HARMONIC MINOR, F", "F G A♭ B♭ C D♭ E", HARM, "F2, C ; kickbass longue queue en F · D♭ et E"),
        ("F", "fa phrygien", "PHRYGIAN, F", "F G♭ A♭ B♭ C D♭ E♭", PHRY, "F2, C ; reese F / G♭ > 80 Hz · G♭ frottée"),
    ]
    cw, ch, cg = 44, 33, 4  # case note
    nx = M + 128
    tx = nx + 7 * (cw + cg) + 8
    for bq, name, scale_kb, notes, degs, use in scales:
        acc, tint = TON[SEC_TON[bq]]
        chip(p, M, y, 28, ch, bq, SEC[bq], 16)
        p.text(M + 35, y + 15, name, 10.5, "bold", fill=acc)
        p.text(M + 35, y + 27, scale_kb, 7.5, fill=GREY)
        for i, (n, d) in enumerate(zip(notes.split(), degs)):
            cx = nx + i * (cw + cg)
            if i == 0:
                p.rect(cx, y, cw, ch, acc, rx=4)
                fill, dfill = "white", "white"
            elif d in ("♭2", "7"):
                mark = PHRYG if d == "♭2" else SENS
                p.rect(cx + 1, y + 1, cw - 2, ch - 2, "#fdf0dc" if d == "♭2" else "#eee4f8", mark, 2.2, rx=4)
                fill, dfill = INK, mark
            else:
                p.rect(cx, y, cw, ch, tint, acc, 0.8, rx=4)
                fill, dfill = INK, acc
            p.text(cx + cw / 2, y + 20, n, 16, "bold", fill=fill, anchor="middle")
            p.text(cx + cw / 2, y + 30, d, 7.5, "bold", fill=dfill, anchor="middle")
        lines = wrap(use, M + nw - tx, 9)
        y0 = y + ch / 2 - (len(lines) - 1) * 5.5 + 3.5
        for j, line in enumerate(lines):
            p.text(tx, y0 + j * 11, line, 9)
        y += ch + 4
    y += 4
    p.rect(M, y, 14, 11, TON["fa"][0], rx=2)
    p.text(M + 19, y + 9, "tonique", 8.5)
    p.rect(M + 66, y, 14, 11, "#fdf0dc", PHRYG, 2, rx=2)
    p.text(M + 85, y + 9, "seconde phrygienne", 8.5)
    p.rect(M + 180, y, 14, 11, "#eee4f8", SENS, 2, rx=2)
    p.text(M + 199, y + 9, "sensible", 8.5)
    p.text(M + 250, y + 9, "Pivots : B♭ et D♭ (fa → la#), F (la# → fa). Tierce et ♭2 jamais dans le sub. KB FOLD ON, gamme par track (9, 10, 12, 13).", 8.5, fill=GREY)
    y += 14

    fam = {"grave": "#b45309", "drums": "#475569", "mélo": "#be185d", "fx": "#8a8a8a"}
    y4 = title(p, xg, y_cols, "4. Grille des 16 tracks", gw)
    grid = [("1", "Kick", "grave"), ("2", "Rumble / sub", "grave"), ("3", "Clap / snare", "drums"),
            ("4", "Perc", "drums"), ("5", "Hats", "drums"), ("6", "Cymbales", "drums"),
            ("7", "Id1 appel", "drums"), ("8", "Id1 réponse", "drums"), ("9", "Basse (stab)", "grave"),
            ("10", "Séquence / acid", "mélo"), ("11", "Atmo / drone", "mélo"), ("12", "Vocal", "mélo"),
            ("13", "Id2 bas-médium", "mélo"), ("14", "Id3 médium-aigu", "mélo"), ("15", "FX transition", "fx"),
            ("16", "Kick fantôme", "grave")]
    half = gw / 2
    for i, (n, lab, f) in enumerate(grid):
        cx = xg + (half if i >= 8 else 0)
        cy = y4 + (i % 8) * 16
        p.rect(cx, cy, 22, 13, fam[f], rx=2)
        p.text(cx + 11, cy + 10, n, 9.5, "bold", fill="white", anchor="middle")
        p.text(cx + 28, cy + 10, lab, 9.5)
    y4 += 8 * 16 + 6
    y4 = bullets(p, xg, y4, [
        "16 : copie du kick hors main, source du sidechain ; le pompage tient quand le 1 est muté.",
        "0-KIT en fa (slots A01-A16) ; une autre tonalité corrige par TUNE ou sample lock.",
    ], gw, size=9, lh=11, gap=3)
    footer(p, max(y, y4))
    return p.svg()


def main() -> None:
    path = OUT_DIR / "solaris-pense-bete.svg"
    path.write_text(page())
    print(f"ok {path.name}")


if __name__ == "__main__":
    main()

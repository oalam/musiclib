"""Arpégiateur (slices 11 à 21) : ordre des notes tenues, octaves, motifs, accords."""

from __future__ import annotations

from collections.abc import Mapping, Sequence, Set
from typing import Literal

ArpOrder = Literal["up", "down", "updown", "played", "random"]
ORDERS: tuple[ArpOrder, ...] = ("up", "down", "updown", "played", "random")
ORDER_LABELS: dict[ArpOrder, str] = {  # écran : 4 lettres
    "up": "UP",
    "down": "DOWN",
    "updown": "UPDN",
    "played": "PLAY",
    "random": "RAND",
}
MAX_OCTAVES = 3
GATE_MIN, GATE_MAX, GATE_STEP = 10, 100, 5  # durée d'une note, en % de la division

# Accords (slice 15) : un pad = un accord pris dans la gamme. Pour chaque note de l'accord,
# les candidates en demi-tons au-dessus de la fondamentale, la première dans la gamme gagne.
ArpChord = Literal["off", "tri", "7th", "sus2", "sus4", "pwr"]
CHORDS: tuple[ArpChord, ...] = ("off", "tri", "7th", "sus2", "sus4", "pwr")
CHORD_LABELS: dict[ArpChord, str] = {
    "off": "OFF",
    "tri": "TRI",
    "7th": "7TH",
    "sus2": "SUS2",
    "sus4": "SUS4",
    "pwr": "PWR",
}
_SECOND, _THIRD, _FOURTH = (2, 1, 3), (3, 4), (5, 6, 4)
_FIFTH, _SEVENTH, _OCTAVE = (7, 6, 8), (10, 11, 9), (12,)
CHORD_TONES: dict[ArpChord, tuple[tuple[int, ...], ...]] = {
    "off": (),
    "tri": (_THIRD, _FIFTH),
    "7th": (_THIRD, _FIFTH, _SEVENTH),
    "sus2": (_SECOND, _FIFTH),
    "sus4": (_FOURTH, _FIFTH),
    "pwr": (_FIFTH, _OCTAVE),
}

# Renversements (slice 21) : 1 / 2 = les 1 ou 2 notes les plus basses de l'accord montent
# d'une octave ; fix = toutes les notes ramenées dans l'octave au-dessus du pad tenu.
ArpInversion = Literal["off", "1", "2", "fix"]
INVERSIONS: tuple[ArpInversion, ...] = ("off", "1", "2", "fix")
INVERSION_LABELS: dict[ArpInversion, str] = {"off": "OFF", "1": "1", "2": "2", "fix": "FIX"}

# Progressions (slice 16) : suites de degrés 1-7 comptés depuis le pad tenu, un accord par
# durée `BAR` ; degrés 2-4 vers le haut, 5-7 vers le bas (une quarte au plus du pad).
ArpBars = Literal["1/2", "1", "2", "4"]
BARS: tuple[ArpBars, ...] = ("1/2", "1", "2", "4")
BARS_TICKS: dict[ArpBars, int] = {"1/2": 48, "1": 96, "2": 192, "4": 384}  # 96 ticks par mesure
PROGRESSION_OFF = "OFF"
PROGRESSION_MAX = 16
DEGREES_UP = 4  # dernier degré compté vers le haut
AEOLIAN = (0, 2, 3, 5, 7, 8, 10)  # sans gamme connue

MOTIF_STEPS = 16  # longueur maximale d'un motif (slice 19 : 1 à 16 pas)
MOTIF_OFF = "OFF"  # pas de motif : une note par division, sans atténuation
MOTIF_NAME_MAX = 4  # largeur de la case de l'écran
NOTE, ACCENT, REST, TIE = "x", "X", ".", "-"  # un caractère par pas du motif
# Ratchets (slice 18) : la note du pas rejouée 2 ou 3 fois dans le pas ; majuscule = accent.
RATCHETS: dict[str, int] = {"r": 2, "R": 2, "t": 3, "T": 3}
CHANCE = "?"  # slice 20 : note ordinaire jouée une fois sur deux, silence sinon
CHANCE_ODDS = 0.5
PLAYED = frozenset({NOTE, ACCENT, CHANCE, *RATCHETS})  # pas qui prennent une note de l'arpège

Held = tuple[int, int]  # (pad, note)


class MotifError(ValueError):
    """Motif d'arpège mal écrit (longueur, caractère inconnu, aucune note)."""


def parse_motif(text: str) -> str:
    """Motif de la config → ses pas (1 à 16), sans les espaces qui séparent les temps."""
    steps = "".join(text.split())
    if not 1 <= len(steps) <= MOTIF_STEPS:
        raise MotifError(f"motif {text!r} : {len(steps)} pas, 1 à {MOTIF_STEPS} attendus")
    unknown = sorted(set(steps) - PLAYED - {REST, TIE})
    if unknown:
        raise MotifError(f"motif {text!r} : pas inconnus {''.join(unknown)!r}")
    if not PLAYED & set(steps):
        raise MotifError(f"motif {text!r} : aucune note")
    return steps


def hits(kind: str) -> int:
    """Nombre de coups d'un pas joué : 1, ou 2 / 3 pour un ratchet."""
    return RATCHETS.get(kind, 1)


def accented(kind: str) -> bool:
    """Pas à la pression du pad (`X`, `R`, `T`) ; les autres sont atténués."""
    return kind.isupper()


def ties_after(steps: str, index: int) -> int:
    """Nombre de pas liés qui prolongent la note du pas `index` (le motif boucle)."""
    n = 0
    while n < len(steps) - 1 and steps[(index + n + 1) % len(steps)] == TIE:
        n += 1
    return n


def sequence(held: Sequence[Held], order: ArpOrder, octaves: int) -> list[Held]:
    """Un tour d'arpège : les notes tenues (dans l'ordre d'appui) sur `octaves` octaves.

    `played` et `random` gardent l'ordre d'appui, octave après octave (le tirage se fait
    à l'appel) ; `updown` ne répète ni le sommet ni la base. Notes au-delà de 127 écartées."""
    wide = [
        (pad, note + 12 * o) for o in range(octaves) for pad, note in held if note + 12 * o < 128
    ]
    if order in ("played", "random"):
        return wide
    up = sorted(wide, key=lambda k: (k[1], k[0]))
    if order == "up":
        return up
    if order == "down":
        return up[::-1]
    return up + up[-2:0:-1]


def chord(note: int, kind: ArpChord, scale: Set[int]) -> list[int]:
    """Notes de l'accord `kind` sur la fondamentale `note`, prises dans `scale` (classes de
    hauteur 0-11) : la première candidate dans la gamme, sinon la première tout court."""
    tones = [note]
    for candidates in CHORD_TONES[kind]:
        tones.append(
            note + next((c for c in candidates if (note + c) % 12 in scale), candidates[0])
        )
    return tones


# Nom affiché de l'accord en cours : intervalles au-dessus de la fondamentale → suffixe.
_QUALITIES: dict[tuple[int, ...], str] = {
    (3, 7): "m",
    (4, 7): "",
    (3, 6): "dim",
    (4, 8): "aug",
    (3, 7, 10): "m7",
    (4, 7, 11): "maj7",
    (4, 7, 10): "7",
    (3, 6, 10): "m7b5",
    (3, 7, 11): "mM7",
    (3, 6, 9): "dim7",
    (2, 7): "sus2",
    (1, 7): "susb2",
    (5, 7): "sus4",
    (6, 7): "sus#4",
    (7, 12): "5",
}


def chord_name(tones: Sequence[int], names: Sequence[str]) -> str:
    """`Ab`, `Cm`, `Ebmaj7`… : la fondamentale (`names`, 12 classes de hauteur) et la qualité
    lue sur les intervalles ; un accord sans nom connu ne garde que sa fondamentale."""
    root = tones[0]
    return names[root % 12] + _QUALITIES.get(tuple(t - root for t in tones[1:]), "")


def invert(tones: Sequence[int], kind: ArpInversion, anchor: int) -> list[int]:
    """Accord renversé. `1` / `2` : ses 1 ou 2 notes les plus basses montent d'une octave
    (la plus haute ne bouge jamais). `fix` : chaque note ramenée dans l'octave qui part de
    `anchor` (la note du pad tenu), du grave à l'aigu : une progression reste en place."""
    if kind == "off":
        return list(tones)
    if kind == "fix":
        return sorted({anchor + (t - anchor) % 12 for t in tones})
    n = min(int(kind), len(tones) - 1)
    return list(dict.fromkeys([*tones[n:], *(t + 12 for t in tones[:n])]))


def spread(
    held: Sequence[Held],
    kind: ArpChord,
    scale: Set[int],
    inversion: ArpInversion = "off",
    anchors: Mapping[int, int] | None = None,
) -> list[Held]:
    """Pads tenus → notes de leurs accords, dans l'ordre d'appui ; une même note une seule
    fois (le premier pad qui l'apporte la garde), rien au-delà de 127. `anchors` : pad →
    note du pad avant progression, repère du renversement `fix`."""
    out: list[Held] = []
    seen: set[int] = set()
    for pad, note in held:
        anchor = note if anchors is None else anchors.get(pad, note)
        for tone in invert(chord(note, kind, scale), inversion, anchor):
            if tone < 128 and tone not in seen:
                seen.add(tone)
                out.append((pad, tone))
    return out


def degree_steps(degree: int) -> int:
    """Degré 1-7 d'une progression → pas de gamme depuis le pad (2-4 montent, 5-7 descendent)."""
    return degree - 1 if degree <= DEGREES_UP else degree - 8


def shift(note: int, steps: int, scale: Set[int]) -> int:
    """`note` déplacée de `steps` notes de la gamme `scale` (classes de hauteur 0-11).

    Hors gamme, la note garde son écart avec celle de la gamme juste en dessous ; sans
    gamme, éolien construit sur la note elle-même."""
    pcs = sorted(scale) or sorted((note + i) % 12 for i in AEOLIAN)
    pc = note % 12
    index = sum(1 for p in pcs if p <= pc) - 1  # -1 : sous la première, dernière d'en dessous
    below = pcs[index] if index >= 0 else pcs[-1] - 12
    octave, k = divmod(index + steps, len(pcs))
    return note - pc + pcs[k] + 12 * octave + (pc - below)

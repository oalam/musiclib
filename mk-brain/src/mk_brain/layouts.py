"""Dispositions de pads (groupes A-H du template DT2 Pads) : notes et couleurs.

Les pads sont numérotés comme sur la face avant : 1 en bas à gauche, 16 en
haut à droite.
"""

from __future__ import annotations

from mk_brain.config import RGB, Config, Layout, VelocityConfig

N_PADS = 16


class LayoutError(Exception):
    """Disposition ou pad invalide."""


def pad_note(layout: Layout, pad: int) -> int:
    """Note MIDI jouée par le pad `pad` (1-16)."""
    if not 1 <= pad <= N_PADS:
        raise LayoutError(f"pad {pad} hors 1-16")
    i = pad - 1
    if layout.kind == "rythmique":
        note = i  # note n - 1 = track n, quelle que soit la track active (manuel §8.4)
    elif layout.kind == "chromatique":
        note = layout.base + i
    else:
        n = len(layout.intervals)
        note = layout.base + 12 * (i // n) + layout.intervals[i % n]
    if note > 127:
        raise LayoutError(f"groupe {layout.group}, pad {pad} : note {note} > 127")
    return note


def for_bank(layout: Layout, scale: Layout, tonic: int) -> Layout:
    """Disposition calée sur une banque (mode design, slice 5.D).

    `scale` est la disposition du mode de la banque (ses intervalles),
    `tonic` sa tonique (0 = C) : départ sur la tonique dans l'octave de C5,
    la chromatique prend la gamme de la banque pour éteindre le hors gamme.
    """
    if layout.kind == "rythmique":
        return layout
    update: dict[str, object] = {"base": 60 + tonic}
    if layout.kind == "chromatique":
        update["intervals"] = scale.intervals
    return layout.model_copy(update=update)


def shift_octave(layout: Layout, octaves: int) -> Layout:
    """Disposition décalée de `octaves` octaves ; la rythmique ne bouge pas."""
    if octaves == 0 or layout.kind == "rythmique":
        return layout
    return layout.model_copy(update={"base": layout.base + 12 * octaves})


def fits(layout: Layout) -> bool:
    """Toutes les notes des pads dans 0-127."""
    if layout.base < 0:
        return False
    try:
        pad_note(layout, N_PADS)
    except LayoutError:
        return False
    return True


def in_scale(layout: Layout, pad: int) -> bool:
    """Note du pad dans la gamme : toujours vrai hors chromatique, et sans gamme connue."""
    if layout.kind != "chromatique" or not layout.intervals:
        return True
    return (pad_note(layout, pad) - layout.base) % 12 in layout.intervals


def pad_color(cfg: Config, layout: Layout, pad: int) -> RGB:
    """Couleur pleine du pad (à la frappe) : track en rythmique, rôle de la note sinon.

    Chromatique : seule la tonique est en couleur, le reste en blanc ; le
    hors gamme est éteint au repos (`in_scale`), pas ici (décidé le 2026-11-09).
    Gamme : tonique, tierce, quinte, puis la couleur de la famille.
    """
    if layout.kind == "rythmique":
        return cfg.track_colors[pad]
    degree = (pad_note(layout, pad) - layout.base) % 12
    if degree == 0:
        return cfg.roles.tonique
    if layout.kind == "gamme":
        if degree in (3, 4):
            return cfg.roles.tierce
        if degree == 7:
            return cfg.roles.quinte
    return cfg.families[layout.family]


def scale(rgb: RGB, factor: float) -> RGB:
    r, g, b = rgb
    return (round(r * factor), round(g * factor), round(b * factor))


def velocity(cfg: VelocityConfig, pressure: int) -> int:
    """Pression 12 bits → vélocité MIDI, courbe en puissance `gamma`."""
    span = cfg.full_scale - cfg.threshold
    x = min(1.0, max(0.0, (pressure - cfg.threshold) / span))
    return max(cfg.min, min(cfg.max, cfg.min + round((cfg.max - cfg.min) * float(x**cfg.gamma))))


DEGREES = ("T", "b2", "2", "b3", "3", "4", "b5", "5", "b6", "6", "b7", "7")
DEGREE_NAMES = (  # écran : anglais, la police n'a pas les accents
    "root",
    "minor 2nd",
    "2nd",
    "minor 3rd",
    "major 3rd",
    "4th",
    "tritone",
    "5th",
    "minor 6th",
    "6th",
    "minor 7th",
    "major 7th",
)
NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
FLAT_NAMES = ("C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B")  # écrans


def flat_note(note: int) -> str:
    """Nom à l'écran, en bémols comme la doctrine (B♭) : 70 → `Bb4` (60 = C5)."""
    return f"{FLAT_NAMES[note % 12]}{note // 12}"


def degree_name(layout: Layout, note: int) -> str:
    """Place de la note dans la gamme, depuis la tonique (`base`) ; hors gamme signalé."""
    degree = (note - layout.base) % 12
    name = DEGREE_NAMES[degree]
    if layout.kind == "chromatique" and layout.intervals and degree not in layout.intervals:
        name += ", out of scale"
    return name


def note_name(note: int) -> str:
    """Nom Elektron : 60 = C5 (manuel §8.4, fiche midi-config)."""
    return f"{NOTE_NAMES[note % 12]}{note // 12}"


def describe_note(layout: Layout, pad: int, note: int) -> str:
    """Texte d'écran : track en rythmique, degré + nom MIDI sinon.

    Le nom suppose la DT2 sans TUNE. Avec un projet, la disposition part de la
    tonique de la banque (`for_bank`) : le nom est la vraie note, et la CLI
    affiche banque, tonique et mode devant (slice 6.B).
    """
    if layout.kind == "rythmique":
        return f"pad {pad} -> track {note + 1}"
    degree = DEGREES[(note - layout.base) % 12]
    return f"pad {pad} -> {degree} ({note_name(note)}, {note})"

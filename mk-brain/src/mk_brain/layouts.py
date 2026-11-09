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


def pad_color(cfg: Config, layout: Layout, pad: int) -> RGB:
    """Couleur pleine du pad : track en rythmique, rôle de la note sinon."""
    if layout.kind == "rythmique":
        return cfg.track_colors[pad]
    degree = (pad_note(layout, pad) - layout.base) % 12
    if degree == 0:
        return cfg.roles.tonique
    if degree in (3, 4):
        return cfg.roles.tierce
    if degree == 7:
        return cfg.roles.quinte
    if layout.kind == "chromatique" and degree not in layout.intervals:
        return cfg.roles.hors_gamme
    return cfg.families[layout.family]


def scale(rgb: RGB, factor: float) -> RGB:
    r, g, b = rgb
    return (round(r * factor), round(g * factor), round(b * factor))


def velocity(cfg: VelocityConfig, pressure: int) -> int:
    """Pression 12 bits → vélocité MIDI, courbe en puissance `gamma`."""
    span = cfg.full_scale - cfg.threshold
    x = min(1.0, max(0.0, (pressure - cfg.threshold) / span))
    return max(cfg.min, min(cfg.max, cfg.min + round((cfg.max - cfg.min) * float(x**cfg.gamma))))

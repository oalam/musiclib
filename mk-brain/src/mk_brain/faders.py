"""Faders des tracks : valeurs connues de la DT2, état « hors prise », mutes.

Les encodeurs de la MK2 sont relatifs et la DT2 ne renvoie rien au
changement de pattern : le Pi part de la dernière valeur connue. Il apprend
celles jouées sur la DT2 (`ENCODER DEST` et `MUTE DEST` = `INT + EXT`,
décidé le 2026-11-09). Après un changement de pattern, toutes les valeurs
sont marquées « hors prise » (`~`) : la DT2 a rechargé son kit.
Plusieurs pages de 8 (flèches à côté des écrans, qui cyclent dans les deux
sens) ; un paramètre est un CC ou le pitch bend (`PITCH_BEND`), sa valeur est
gardée quelle que soit la page.

Course des encodeurs : `raw_per_step` unités brutes par cran de CC en geste
lent ; avec une accélération (`Accel`), le geste rapide en demande moins. La
vitesse d'un encodeur est la somme signée de ses rotations sur une courte
fenêtre glissante ; une rotation isolée compte toujours comme lente.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

DEFAULT_VALUE = 64  # valeur de départ d'un paramètre jamais vu
# CC de mute : 0 = ouvert, autre valeur = muté. La DT2 envoie 1 pour muté, le Pi
# envoie 127 (vérifié en 5.A) ; constaté le 2026-11-09 à l'essai.
MUTED, OPEN = 127, 0


@dataclass(frozen=True, slots=True)
class FaderView:
    name: str
    cc: int
    value: int
    stale: bool  # « ~ » : valeur supposée, la DT2 a pu changer
    known: bool


@dataclass(frozen=True, slots=True)
class Accel:
    """Accélération des encodeurs : pas rapide et seuils de vitesse (unités brutes / s)."""

    raw_per_step: int  # unités brutes par cran de CC à pleine vitesse
    slow: float  # en dessous : pas lent (`Faders.raw_per_step`)
    fast: float  # au-dessus : pas rapide ; entre les deux, interpolation
    window_ns: int  # fenêtre de mesure de la vitesse


class Faders:
    def __init__(
        self,
        pages: list[list[tuple[str, int]]],
        mute_cc: int,
        raw_per_step: int,
        accel: Accel | None = None,
    ) -> None:
        self.pages = pages  # pages de 8 × (abrégé, CC ou PITCH_BEND)
        self.page_index = 0
        self.mute_cc = mute_cc
        self.raw_per_step = raw_per_step
        self._values: dict[tuple[int, int], int] = {}  # (track, CC) → valeur connue
        self._stale: set[tuple[int, int]] = set()
        self.accel = accel
        self.speed = 0.0  # vitesse de la dernière rotation, unités brutes / s (réglage des seuils)
        self._residue: dict[int, float] = {}  # encodeur → reste de rotation brute (pondérée)
        self._recent: dict[int, deque[tuple[int, int]]] = {}  # encodeur → (instant, rotation)
        self.muted: dict[int, bool] = {}

    @property
    def n_pages(self) -> int:
        return len(self.pages)

    @property
    def page(self) -> list[tuple[str, int]]:
        return self.pages[self.page_index]

    def cycle(self, step: int) -> int:
        """Flèches : page suivante (+1) ou précédente (−1), en boucle. Rend la page."""
        self.page_index = (self.page_index + step) % self.n_pages
        return self.page_index

    # --- entrées ------------------------------------------------------------

    def _boost(self, encoder: int, raw_delta: int, now: int | None) -> float:
        """Facteur du geste : 1 en lent, `raw_per_step / accel.raw_per_step` à pleine vitesse."""
        accel = self.accel
        if accel is None or now is None:
            return 1.0
        recent = self._recent.setdefault(encoder, deque())
        while recent and now - recent[0][0] > accel.window_ns:
            recent.popleft()
        recent.append((now, raw_delta))
        if len(recent) < 2:  # rotation isolée : geste lent
            self.speed = 0.0
            return 1.0
        self.speed = abs(sum(d for _, d in recent)) * 1e9 / accel.window_ns
        ratio = (self.speed - accel.slow) / (accel.fast - accel.slow)
        return 1.0 + (self.raw_per_step / accel.raw_per_step - 1.0) * max(0.0, min(1.0, ratio))

    def steps(self, encoder: int, raw_delta: int, now: int | None = None) -> int:
        """Rotation brute de l'encodeur 1-8 → crans entiers (le reste est gardé).
        `now` (ns) : instant de la rotation, pour l'accélération ; sans lui, pas lent."""
        acc = self._residue.get(encoder, 0.0) + raw_delta * self._boost(encoder, raw_delta, now)
        steps = int(acc / self.raw_per_step)  # vers zéro, dans les deux sens
        self._residue[encoder] = acc - steps * self.raw_per_step
        return steps

    def value(self, track: int, cc: int) -> int:
        """Valeur tenue pour ce paramètre (celle d'où part le prochain cran)."""
        return self._values.get((track, cc), DEFAULT_VALUE)

    def nudge(self, track: int, cc: int, steps: int) -> int | None:
        """Paramètre d'une track décalé de `steps` crans → nouvelle valeur, ou None si
        rien ne change."""
        key = (track, cc)
        old = self._values.get(key, DEFAULT_VALUE)
        new = max(0, min(127, old + steps))
        self._stale.discard(key)
        if new == old and key in self._values:
            return None
        self._values[key] = new
        return new

    def turn(
        self, track: int, encoder: int, raw_delta: int, now: int | None = None
    ) -> tuple[int, int] | None:
        """Rotation de l'encodeur 1-8 → (CC ou PITCH_BEND, valeur 0-127), ou None."""
        steps = self.steps(encoder, raw_delta, now)
        if steps == 0:
            return None
        _, cc = self.page[encoder - 1]
        new = self.nudge(track, cc, steps)
        return None if new is None else (cc, new)

    def toggle_mute(self, track: int) -> tuple[int, int]:
        """MUTE + pad → (CC, valeur). Un mute jamais vu est supposé ouvert.

        127 = muter, 0 = ouvrir (vérifié sur la DT2).
        """
        muted = not self.muted.get(track, False)
        self.muted[track] = muted
        return self.mute_cc, MUTED if muted else OPEN

    def received(self, track: int, cc: int, value: int) -> None:
        """CC venu de la DT2 sur le canal d'une track : bouton ou mute joué sur la machine."""
        if cc == self.mute_cc:  # la DT2 envoie 1 = muté, 0 = ouvert (constaté le 2026-11-09)
            self.muted[track] = value != OPEN
            return
        if any(c == cc for page in self.pages for _, c in page):
            self._values[(track, cc)] = value
            self._stale.discard((track, cc))

    def pattern_changed(self) -> None:
        self._stale = set(self._values)

    # --- session (sauvée, reprise au démarrage) -----------------------------------

    def values(self) -> dict[tuple[int, int], int]:
        """Valeurs connues, (track, paramètre) → valeur."""
        return dict(self._values)

    def restore(self, values: dict[tuple[int, int], int], muted: set[int]) -> None:
        """Valeurs d'une session passée, toutes hors prise ; mutes pour l'affichage."""
        known = {c for page in self.pages for _, c in page}
        self._values = {k: v for k, v in values.items() if k[1] in known}
        self._stale = set(self._values)
        self.muted = {t: True for t in muted}

    # --- lecture --------------------------------------------------------------

    def view(self, track: int) -> list[FaderView]:
        out = []
        for name, cc in self.page:
            key = (track, cc)
            out.append(
                FaderView(
                    name,
                    cc,
                    self._values.get(key, DEFAULT_VALUE),
                    key in self._stale,
                    key in self._values,
                )
            )
        return out

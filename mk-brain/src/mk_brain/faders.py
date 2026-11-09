"""Faders des tracks : valeurs connues de la DT2, état « hors prise », mutes.

Les encodeurs de la MK2 sont relatifs et la DT2 ne renvoie rien au
changement de pattern : le Pi part de la dernière valeur connue. Il apprend
celles jouées sur la DT2 (`ENCODER DEST` et `MUTE DEST` = `INT + EXT`,
décidé le 2026-11-09). Après un changement de pattern, toutes les valeurs
sont marquées « hors prise » (`~`) : la DT2 a rechargé son kit.
"""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_VALUE = 64  # valeur de départ d'un paramètre jamais vu


@dataclass(frozen=True, slots=True)
class FaderView:
    name: str
    cc: int
    value: int
    stale: bool  # « ~ » : valeur supposée, la DT2 a pu changer
    known: bool


class Faders:
    def __init__(self, page: list[tuple[str, int]], mute_cc: int, raw_per_step: int) -> None:
        self.page = page  # 8 × (abrégé, CC)
        self.mute_cc = mute_cc
        self.raw_per_step = raw_per_step
        self._values: dict[tuple[int, int], int] = {}  # (track, CC) → valeur connue
        self._stale: set[tuple[int, int]] = set()
        self._residue: dict[int, int] = {}  # encodeur → reste de rotation brute
        self.muted: dict[int, bool] = {}

    # --- entrées ------------------------------------------------------------

    def turn(self, track: int, encoder: int, raw_delta: int) -> tuple[int, int] | None:
        """Rotation de l'encodeur 1-8 → (CC, valeur) à envoyer, ou None si rien ne change."""
        acc = self._residue.get(encoder, 0) + raw_delta
        steps = int(acc / self.raw_per_step)  # vers zéro, dans les deux sens
        self._residue[encoder] = acc - steps * self.raw_per_step
        if steps == 0:
            return None
        _, cc = self.page[encoder - 1]
        key = (track, cc)
        old = self._values.get(key, DEFAULT_VALUE)
        new = max(0, min(127, old + steps))
        self._stale.discard(key)
        if new == old and key in self._values:
            return None
        self._values[key] = new
        return cc, new

    def toggle_mute(self, track: int) -> tuple[int, int]:
        """MUTE + pad → (CC, valeur). Un mute jamais vu est supposé ouvert."""
        muted = not self.muted.get(track, False)
        self.muted[track] = muted
        return self.mute_cc, 127 if muted else 0

    def received(self, track: int, cc: int, value: int) -> None:
        """CC venu de la DT2 sur le canal d'une track : bouton ou mute joué sur la machine."""
        if cc == self.mute_cc:
            self.muted[track] = value >= 64
            return
        if any(c == cc for _, c in self.page):
            self._values[(track, cc)] = value
            self._stale.discard((track, cc))

    def pattern_changed(self) -> None:
        self._stale = set(self._values)

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

"""Modes live / design et leur bascule verrouillée (SPEC, Modes ; slice 5.B).

SHIFT + CONTROL tenus 1 s proposent l'autre mode ; un appui sur l'encodeur
maître confirme. En live, transport lancé, la bascule est refusée, à la
proposition comme à la confirmation. Une proposition s'annule seule après
5 s, ou dès qu'un autre bouton est pressé. Pur : temps en ns passé par l'appelant.
"""

from __future__ import annotations

from typing import Literal

Mode = Literal["live", "design"]
HOLD_NS = 1_000_000_000  # SHIFT + CONTROL tenus 1 s
CONFIRM_NS = 5_000_000_000  # délai pour confirmer à l'encodeur maître
LOCKED = "transport lancé : live verrouillé"


def other(mode: Mode) -> Mode:
    return "design" if mode == "live" else "live"


class ModeSwitch:
    def __init__(self, mode: Mode = "live") -> None:
        self.mode: Mode = mode
        self.pending: Mode | None = None  # mode proposé, en attente de confirmation
        self._held_since: int | None = None
        self._pending_since = 0

    def combo_pressed(self, now: int) -> None:
        """SHIFT et CONTROL viennent d'être tenus ensemble."""
        self._held_since = now

    def combo_released(self) -> None:
        self._held_since = None

    def cancel(self) -> str | None:
        if self.pending is None:
            return None
        self.pending = None
        return "bascule annulée"

    def update(self, now: int, running: bool) -> str | None:
        """Message à afficher quand l'état change, sinon None."""
        if self.pending is not None:
            if self.mode == "live" and running:
                self.pending = None
                return LOCKED
            if now - self._pending_since > CONFIRM_NS:
                return self.cancel()
        if self._held_since is not None and now - self._held_since >= HOLD_NS:
            self._held_since = None  # une proposition par maintien
            if self.mode == "live" and running:
                return LOCKED
            self.pending = other(self.mode)
            self._pending_since = now
            return f"-> {self.pending.upper()} ? encodeur maître"
        return None

    def confirm(self, running: bool) -> str | None:
        """Appui sur l'encodeur maître : bascule si une proposition attend."""
        if self.pending is None:
            return None
        if self.mode == "live" and running:
            self.pending = None
            return LOCKED
        self.mode, self.pending = self.pending, None
        return f"mode {self.mode.upper()}"

"""Compteur de phrases : mesure dans la phrase, numéro de phrase, caps, LED Group.

Pur : tout se calcule depuis les ticks reçus depuis le Start (96 par mesure).
Remises à zéro (SHIFT + PLAY, SHIFT + GROUP n, Program Change) toujours
appliquées à la barre suivante, jamais à la réception : la DT2 envoie le PC
10 clocks avant la mesure du nouveau pattern (SPEC, question 7).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from mk_brain.clock import TICKS_PER_BAR, TICKS_PER_BEAT

PhraseLength = Literal[32, 64]
BLOCK_BARS = 8  # un bouton GROUP par bloc de 8 mesures
CAP_BARS = 16  # caps : 16, 32, 64
TAIL_BARS = 4  # 4 dernières mesures d'une phrase en vidéo inverse
COUNTDOWN_BARS = 2  # -2, -1 en très gros avant un cap
BANKS = "ABCDEFGH"  # PC = banque × 16 + (pattern − 1), 128 patterns


def pattern_label(program: int) -> str:
    """Program Change → nom de pattern DT2 (`36` → `C05`)."""
    return f"{BANKS[program // 16 % len(BANKS)]}{program % 16 + 1:02d}"


@dataclass(frozen=True, slots=True)
class PhraseState:
    bar: int  # mesure dans la phrase, 1..length
    phrase: int  # numéro de phrase depuis le dernier recalage, base 1
    beat: int  # 1-4
    length: int
    pulse: bool  # première croche du 1 de la mesure
    half_beat_on: bool  # première moitié du temps (clignotement)

    @property
    def cap(self) -> int:
        """Prochain cap (16, 32, 64) atteint à la fin de sa mesure."""
        return min(self.length, -(-self.bar // CAP_BARS) * CAP_BARS)

    @property
    def to_cap(self) -> int:
        """Mesures restantes avant le cap, la mesure en cours comprise (1 = dernière)."""
        return self.cap - self.bar + 1

    @property
    def tail(self) -> bool:
        return self.bar > self.length - TAIL_BARS

    @property
    def countdown(self) -> int | None:
        return -self.to_cap if self.to_cap <= COUNTDOWN_BARS else None

    @property
    def blocks_lit(self) -> int:
        return (self.bar - 1) // BLOCK_BARS + 1

    @property
    def blinking(self) -> bool:
        """Dernière mesure avant un cap : le bloc en cours clignote au temps."""
        return self.to_cap == 1


@dataclass
class _Reset:
    at_bar: int  # mesure absolue (0 = première après le Start)
    first_bar: int  # numéro donné à cette mesure dans la phrase
    pattern: str | None


class PhraseCounter:
    def __init__(self, length: PhraseLength = 32) -> None:
        self.length: int = length
        self._origin = 0  # mesure absolue du recalage
        self._offset = 0  # mesures déjà écoulées dans la phrase à l'origine
        self._pending: _Reset | None = None
        self.pattern: str | None = None  # dernier pattern annoncé par PC, appliqué

    # --- entrées ------------------------------------------------------------

    def start(self) -> None:
        self._origin, self._offset, self._pending = 0, 0, None

    def stop(self) -> None:
        """Le PC qui accompagne un Stop ne change rien : on oublie la remise en attente."""
        self._pending = None

    def reset_next_bar(self, ticks: int, first_bar: int = 1, pattern: str | None = None) -> int:
        """Recale le compteur : la barre suivante devient `first_bar`. Rend sa mesure absolue."""
        at = ticks // TICKS_PER_BAR + 1
        self._pending = _Reset(at, first_bar, pattern)
        return at

    @property
    def pending(self) -> bool:
        return self._pending is not None

    # --- lecture --------------------------------------------------------------

    def update(self, ticks: int) -> PhraseState:
        """État à `ticks` depuis le Start ; applique la remise en attente si sa barre est passée."""
        abs_bar = ticks // TICKS_PER_BAR
        p = self._pending
        if p is not None and abs_bar >= p.at_bar:
            self._origin, self._offset = p.at_bar, p.first_bar - 1
            if p.pattern is not None:
                self.pattern = p.pattern
            self._pending = None
        elapsed = abs_bar - self._origin + self._offset
        in_bar = ticks % TICKS_PER_BAR
        return PhraseState(
            bar=elapsed % self.length + 1,
            phrase=elapsed // self.length + 1,
            beat=in_bar // TICKS_PER_BEAT + 1,
            length=self.length,
            pulse=in_bar < TICKS_PER_BEAT // 2,
            half_beat_on=in_bar % TICKS_PER_BEAT < TICKS_PER_BEAT // 2,
        )

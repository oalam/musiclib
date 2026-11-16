"""Boucle de gestes (slice 22) : ce que REC garde, sans moteur ni MIDI.

Une boucle de 1, 2, 4 ou 8 mesures garde des gestes, chacun fait d'actions placées
dans la boucle (position en ticks, 96 par mesure). Le moteur les rejoue comme s'ils
venaient de la MK2 ; ce module ne fait que les ranger, les rendre dans l'ordre et
annuler / rétablir geste par geste, dans l'ordre de l'enregistrement.

- Positions données en ticks depuis le début de la boucle, tours compris
  (`tour × longueur + position`) : le tour d'enregistrement d'une action est retenu,
  elle n'est pas rejouée pendant ce tour (la main vient de la jouer).
- Deux files : `ahead` (notes directes, planifiées en avance à leur instant exact) et
  le reste (appliqué à son passage).
- Un geste d'encodeur ou de réglage remplace, sur la portion de boucle qu'il couvre,
  ce que les gestes plus anciens y avaient écrit pour le même paramètre ; annulé, il
  le leur rend.
- Densité : au plus une valeur par tick et par paramètre (`dedupe`).
"""

from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass, field
from typing import Literal

from mk_brain.clock import TICKS_PER_BAR

LoopBars = Literal[1, 2, 4, 8]
LOOP_BARS: tuple[LoopBars, ...] = (1, 2, 4, 8)  # REC tenu + boutons d'écran 1-4
PadMode = Literal["note", "arp", "repeat"]
Value = str | int | bool | None
Key = tuple[str, int, int] | tuple[str, str]  # paramètre d'une track, réglage, pression
EDGE = 0.001  # relâché forcé juste avant le bouclage, en ticks


@dataclass(frozen=True, slots=True)
class PadOn:
    """Frappe : `hit` numérote la frappe, `shift` place la grille visée (arpège, repeat)
    par rapport à la position de l'action."""

    hit: int
    pad: int
    mode: PadMode
    channel: int
    note: int
    velocity: int
    pressure: int
    shift: float = 0.0


@dataclass(frozen=True, slots=True)
class Pressure:
    hit: int
    value: int


@dataclass(frozen=True, slots=True)
class PadOff:
    hit: int


@dataclass(frozen=True, slots=True)
class Param:
    """Valeur d'un encodeur : CC ou pitch bend d'une track (canal FX : sa track fixe)."""

    track: int
    param: int
    value: int


@dataclass(frozen=True, slots=True)
class Setting:
    """Réglage du moteur : arpège, division, maintien, preset rappelé."""

    name: str
    value: Value


Action = PadOn | Pressure | PadOff | Param | Setting


@dataclass(slots=True)
class _Event:
    pos: float  # dans la boucle, 0 ≤ pos < longueur
    born: int  # tour d'enregistrement
    seq: int
    action: Action
    key: Key | None
    ahead: bool


@dataclass(eq=False)
class Gesture:
    """Unité d'annulation : une frappe (ou un accord), un mouvement d'encodeur, un réglage."""

    label: str
    events: list[_Event] = field(default_factory=list)
    hits: list[int] = field(default_factory=list)
    masks: set[Key] = field(default_factory=set)  # paramètres que ce geste remplace
    start: float = 0.0  # première et dernière position, tours compris
    end: float = 0.0
    _last: dict[Key, tuple[int, _Event]] = field(default_factory=dict)


class Loop:
    def __init__(self, bars: LoopBars) -> None:
        self.bars: LoopBars = bars
        self.gestures: list[Gesture] = []  # dans l'ordre de l'enregistrement
        self.undone: list[Gesture] = []  # annulés, à rétablir (le dernier annulé au bout)
        self.base: dict[str, Value] = {}  # réglages d'avant leur premier geste enregistré
        self.dirty = False  # gestes ajoutés depuis le dernier `rebuild`
        self._seq = 0
        self._hits = 0
        self._queues: dict[bool, tuple[list[float], list[_Event]]] = {
            False: ([], []),
            True: ([], []),
        }

    @property
    def ticks(self) -> int:
        return self.bars * TICKS_PER_BAR

    @property
    def empty(self) -> bool:
        return not self.gestures and not self.undone

    def resize(self, bars: LoopBars) -> None:
        """Longueur : boucle vide seulement (au moteur de le vérifier)."""
        self.bars = bars

    # --- enregistrement -------------------------------------------------------

    def open(self, label: str) -> Gesture:
        """Nouveau geste, le dernier de la pile ; ce qui pouvait être rétabli est perdu."""
        g = Gesture(label)
        self.gestures.append(g)
        self.undone.clear()
        return g

    def new_hit(self, g: Gesture) -> int:
        self._hits += 1
        g.hits.append(self._hits)
        return self._hits

    def add(
        self,
        g: Gesture,
        pos: float,
        action: Action,
        *,
        key: Key | None = None,
        ahead: bool = False,
        dedupe: bool = False,
        mask: bool = False,
    ) -> None:
        """Ajoute une action au geste, à `pos` (ticks depuis le début de la boucle, tours
        compris). `dedupe` : une seule valeur par tick pour `key`, la dernière."""
        if not g.events:
            g.start = pos
        g.end = max(g.end, pos)
        if mask and key is not None:
            g.masks.add(key)
        born = int(pos // self.ticks)
        if dedupe and key is not None:
            last = g._last.get(key)
            if last is not None and last[0] == int(pos):
                last[1].action = action
                return
        self._seq += 1
        ev = _Event(pos - born * self.ticks, born, self._seq, action, key, ahead)
        g.events.append(ev)
        if key is not None:
            g._last[key] = (int(pos), ev)
        self.dirty = True

    def settle(self) -> None:
        """La boucle repart de zéro (Start) : tout ce qui est gardé se rejoue dès ce tour."""
        for g in self.gestures + self.undone:
            for ev in g.events:
                ev.born = -1

    # --- annuler, rétablir ------------------------------------------------------

    def undo(self) -> Gesture | None:
        if not self.gestures:
            return None
        g = self.gestures.pop()
        self.undone.append(g)
        self.rebuild()
        return g

    def redo(self) -> Gesture | None:
        if not self.undone:
            return None
        g = self.undone.pop()
        self.gestures.append(g)
        self.rebuild()
        return g

    # --- lecture ----------------------------------------------------------------

    def _covers(self, g: Gesture, pos: float) -> bool:
        """`pos` est dans la portion de boucle parcourue par le geste."""
        if g.end - g.start >= self.ticks:
            return True
        lo, hi = g.start % self.ticks, g.end % self.ticks
        return lo <= pos <= hi if lo <= hi else pos >= lo or pos <= hi

    def rebuild(self) -> None:
        """Files de lecture : les gestes actifs, le plus récent l'emportant sur sa portion."""
        events: list[_Event] = []
        for g in self.gestures:
            if g.masks:
                events = [e for e in events if not (e.key in g.masks and self._covers(g, e.pos))]
            events.extend(g.events)
        events.sort(key=lambda e: (e.pos, e.seq))
        for ahead in (False, True):
            chosen = [e for e in events if e.ahead == ahead]
            self._queues[ahead] = ([e.pos for e in chosen], chosen)
        self.dirty = False

    def due(self, lo: float, hi: float, ahead: bool) -> list[tuple[float, Action, Key | None]]:
        """Actions de `lo` (compris) à `hi` (exclu), positions tours compris, dans l'ordre.
        Une action n'est pas rendue pendant son tour d'enregistrement."""
        out: list[tuple[float, Action, Key | None]] = []
        positions, events = self._queues[ahead]
        if hi <= lo or not events:
            return out
        length = self.ticks
        lap = int(lo // length)
        while lap * length < hi:
            base = lap * length
            first = bisect_left(positions, lo - base)
            last = bisect_left(positions, hi - base)
            for ev in events[first:last]:
                if ev.born != lap:
                    out.append((base + ev.pos, ev.action, ev.key))
            lap += 1
        return out

    def touched(self) -> set[str]:
        """Réglages que les gestes actifs changent : remis à leur valeur d'avant à chaque tour."""
        return {
            e.action.name for g in self.gestures for e in g.events if isinstance(e.action, Setting)
        }

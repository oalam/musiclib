"""Moteur : seul propriétaire de l'état, sans HID ni MIDI (testable à l'horloge simulée).

Rend des messages datés `(instant_ns, message)` que l'ordonnanceur envoie.
- Slice 1 : pads → notes ; GROUP A-H choisit la disposition (provisoire,
  l'affectation définitive des GROUP se décide à la slice 5).
- Slice 3 : quantize « nearest » (GRID), swing (SWING + encodeur maître),
  note repeat (NOTE REPEAT tenu, SHIFT + NOTE REPEAT verrouille, boutons
  d'écran 1-8 = division). Sans transport lancé : envoi immédiat, sans repeat.
- Slice 4 : compteur de phrases (`phrase.py`) ; Start, Stop et Program Change
  reçus de la DT2 ; SHIFT + PLAY = mesure 1 à la barre suivante, SHIFT +
  GROUP n = début du bloc n ; transport lancé, les LED GROUP montrent le
  compteur et PLAY pulse sur le 1.
- Slice 5.A : SELECT + pad = track des encodeurs, MUTE + pad = mute (CC 94),
  PATTERN + GROUP A-H = banque (sans envoi), PATTERN + pad = Program
  Change dans la banque courante (refusé tant qu'elle est inconnue) ;
  8 encodeurs → CC sur le canal de la track, valeurs apprises de la DT2
  (`faders.py`). La track de l'AUTO CHANNEL n'est pas joignable par son
  canal : refusée.
- Slice 5.B : modes live / design (`modes.py`), bascule par SHIFT + CONTROL
  tenus 1 s puis appui sur l'encodeur maître, refusée en live transport
  lancé. Live : pads en rythmique, GROUP seul sans effet. Design :
  disposition au choix (GROUP ou PAD MODE, chromatique par défaut),
  encodeurs sur l'AUTO CHANNEL. Quantize propre à chaque mode (off en design).
"""

from __future__ import annotations

from dataclasses import dataclass

from mk_brain.clock import ClockTracker
from mk_brain.config import RGB, Config, Layout
from mk_brain.faders import Faders
from mk_brain.hid_mk2 import (
    GROUPS,
    LED_MAX,
    ButtonEvent,
    EncoderEvent,
    Event,
    LedState,
    PadEvent,
    pad_label,
)
from mk_brain.layouts import N_PADS, pad_color, pad_note, scale, velocity
from mk_brain.modes import ModeSwitch
from mk_brain.phrase import BLOCK_BARS, PhraseCounter, PhraseState, pattern_label
from mk_brain.quantize import (
    GRID_TICKS,
    QUANTIZE_CYCLE,
    QuantizeMode,
    clamp_swing,
    nearest,
    swing_offset,
)
from mk_brain.repeat import DIVISION_TICKS, DIVISIONS, GATE

NOTE_OFF_MIN_NS = 5_000_000  # note off au moins 5 ms après sa note on


@dataclass(frozen=True, slots=True)
class NoteOn:
    channel: int  # 0-15, comme mido
    note: int
    velocity: int


@dataclass(frozen=True, slots=True)
class NoteOff:
    channel: int
    note: int


@dataclass(frozen=True, slots=True)
class ControlChange:
    channel: int
    control: int
    value: int


@dataclass(frozen=True, slots=True)
class ProgramChange:
    channel: int
    program: int


MidiOut = NoteOn | NoteOff | ControlChange | ProgramChange
MODIFIERS = ("SELECT", "MUTE", "PATTERN")  # + pad : commande, pas de note
LIVE_GROUP = 0  # disposition rythmique, imposée en live
DESIGN_GROUP = 1  # chromatique, disposition de départ en design
MODE_KEYS = ("SHIFT", "CONTROL", "MASTER_PUSH")  # n'annulent pas une bascule proposée
Timed = tuple[int, MidiOut]


@dataclass
class _Attack:
    start: int
    peak: int


@dataclass
class _Repeat:
    note: int
    next_pos: float


class Engine:
    def __init__(self, cfg: Config, clock: ClockTracker | None = None) -> None:
        self.cfg = cfg
        self.clock = clock or ClockTracker()
        self.channel = cfg.midi.auto_channel - 1
        self.modes = ModeSwitch()
        self.group = DESIGN_GROUP  # disposition du mode design (en live : rythmique)
        self._quantize: dict[str, QuantizeMode] = {"live": cfg.play.quantize, "design": "off"}
        self._rec_hint = False  # rappel « DT2 en LIVE REC ? » déjà donné dans ce passage en design
        self.swing = cfg.play.swing
        self.division: str = cfg.play.repeat
        self.repeat_held = False
        self.repeat_locked = False
        self._held_buttons: set[str] = set()
        self._attacks: dict[int, _Attack] = {}  # pad 1-16 → attaque en cours de mesure
        self._sounding: dict[int, tuple[int, int]] = {}  # pad → (note, instant de la note on)
        self._repeats: dict[int, _Repeat] = {}
        self._pressure: dict[int, int] = {}
        self.leds_dirty = True
        self.last_played: tuple[int, int, int] | None = None  # (pad, note, vélocité)
        self.last_decision = ""  # diagnostic quantize : position de la frappe et décision
        self.phrase = PhraseCounter(cfg.play.phrase)
        self.phrase_state: PhraseState | None = None
        self._phrase_leds: tuple[object, ...] = ()
        self.log: list[str] = []  # évènements du compteur, lus et vidés par la CLI
        enc = cfg.encoders
        self.faders = Faders([(e.name, e.cc) for e in enc.page], enc.mute_cc, enc.raw_per_step)
        self.track = 1  # track des encodeurs (SELECT + pad)
        self.last_program: int | None = None  # dernier PC reçu
        self.bank: int | None = None  # banque de PATTERN + pad : PC reçu ou PATTERN + GROUP
        self.last_control = ""  # dernier geste de contrôle, pour l'écran
        self._consumed: set[int] = set()  # pads frappés avec un modificateur

    @property
    def design(self) -> bool:
        return self.modes.mode == "design"

    @property
    def layout(self) -> Layout:
        return self.cfg.layouts[self.group if self.design else LIVE_GROUP]

    @property
    def quantize(self) -> QuantizeMode:
        return self._quantize[self.modes.mode]

    @quantize.setter
    def quantize(self, value: QuantizeMode) -> None:
        self._quantize[self.modes.mode] = value

    @property
    def running(self) -> bool:
        return self.clock.ticks_since_start is not None

    @property
    def repeat_active(self) -> bool:
        return self.repeat_held or self.repeat_locked

    # --- entrées ------------------------------------------------------------

    def handle(self, ev: Event, now: int) -> list[Timed]:
        if isinstance(ev, ButtonEvent):
            self._button(ev, now)
            return []
        if isinstance(ev, EncoderEvent):
            if ev.index == 0:
                if "SWING" in self._held_buttons:
                    self.swing = clamp_swing(self.swing + ev.delta)
                return []
            return self._encoder(ev.index, ev.delta, now)
        return self._pad(pad_label(ev.index), ev, now)

    def _reachable(self, track: int) -> bool:
        if track == self.cfg.midi.auto_channel:
            self.last_control = f"T{track:02d} = AUTO CHANNEL : pas de canal propre"
            return False
        return True

    def _encoder(self, index: int, delta: int, now: int) -> list[Timed]:
        """Live : canal de la track sélectionnée. Design : AUTO CHANNEL, donc la track
        active de la DT2 (p-locks en LIVE REC) ; valeurs tenues sous la track sélectionnée."""
        if not self.design and not self._reachable(self.track):
            return []
        sent = self.faders.turn(self.track, index, delta)
        if sent is None:
            return []
        cc, value = sent
        name = self.faders.page[index - 1][0]
        self.last_control = f"T{self.track:02d} {name} {value}"
        if self.design and not self._rec_hint:
            self._rec_hint = True
            self.last_control += "  DT2 en LIVE REC ?"
        channel = self.channel if self.design else self.track - 1
        return [(now, ControlChange(channel, cc, value))]

    def _command(self, pad: int, now: int) -> list[Timed]:
        held = self._held_buttons
        if "SELECT" in held:
            if self.design or self._reachable(pad):
                self.track = pad
                self.last_control = f"T{pad:02d} sélectionnée"
            return []
        if "MUTE" in held:
            if not self._reachable(pad):
                return []
            cc, value = self.faders.toggle_mute(pad)
            self.last_control = f"T{pad:02d} {'mute' if value else 'démute'}"
            return [(now, ControlChange(pad - 1, cc, value))]
        if self.bank is None:
            self.last_control = "banque ? (PATTERN + GROUP)"
            return []
        program = self.bank * 16 + pad - 1
        self.last_control = f"-> {pattern_label(program)}"
        return [(now, ProgramChange(self.cfg.midi.program_channel - 1, program))]

    def on_control_change(self, channel: int, control: int, value: int) -> None:
        """CC reçu de la DT2 (canal 0-15) : bouton ou mute joué sur la machine.

        La DT2 envoie ses boutons sur l'AUTO CHANNEL, sans dire quelle track est
        active (constaté le 2026-11-09) : la valeur va à la track sélectionnée sur
        la MK2. Un mute sur ce canal n'a pas de track sûre : ignoré.
        """
        track = channel + 1
        if track == self.cfg.midi.auto_channel:
            if control == self.faders.mute_cc:
                return
            track = self.track
        self.faders.received(track, control, value)
        self.leds_dirty = True

    def on_start(self) -> None:
        self.phrase.start()

    def on_stop(self) -> None:
        self.phrase.stop()
        self.phrase_state = None
        self.leds_dirty = True

    def on_program_change(self, program: int) -> None:
        """PC reçu : banque courante, faders hors prise ; transport lancé, mesure 1 à la barre
        suivante (arrêté : compteur inchangé)."""
        if program != self.last_program:
            self.faders.pattern_changed()
        if program // 16 != self.bank:
            self.log.append(f"banque {pattern_label(program)[0]} (PC reçu)")
        self.last_program = program
        self.bank = program // 16
        ticks = self.clock.ticks_since_start
        if ticks is None:
            return
        label = pattern_label(program)
        at = self.phrase.reset_next_bar(ticks, pattern=label)
        self.log.append(f"PC {label} -> mesure 1 à la barre {at + 1}")

    def _recalibrate(self, first_bar: int) -> bool:
        ticks = self.clock.ticks_since_start
        if ticks is None or first_bar > self.phrase.length:
            return False
        at = self.phrase.reset_next_bar(ticks, first_bar=first_bar)
        self.log.append(f"recalage -> mesure {first_bar} à la barre {at + 1}")
        return True

    def _switch_mode(self, name: str, now: int) -> bool:
        """Bascule de mode : SHIFT + CONTROL tenus, appui maître = confirmer. True si consommé."""
        if name == "MASTER_PUSH" and self.modes.pending is not None:
            msg = self.modes.confirm(self.running)
            if self.design and msg and msg.startswith("mode"):
                self._rec_hint = False
            self._note(msg)
            self.leds_dirty = True
            return True
        if name not in MODE_KEYS:
            self._note(self.modes.cancel())
        if {"SHIFT", "CONTROL"} <= self._held_buttons and name in ("SHIFT", "CONTROL"):
            self.modes.combo_pressed(now)
            return True
        return False

    def _note(self, msg: str | None) -> None:
        if msg:
            self.last_control = msg
            self.log.append(msg)
            self.leds_dirty = True

    def _button(self, ev: ButtonEvent, now: int) -> None:
        name = ev.name
        if not ev.pressed:
            self._held_buttons.discard(name)
            if name in ("SHIFT", "CONTROL"):
                self.modes.combo_released()
            if name in MODIFIERS:
                self.leds_dirty = True
            if name == "NOTE_REPEAT":
                self.repeat_held = False
                if not self.repeat_locked:
                    self._repeats.clear()
                self.leds_dirty = True
            return
        self._held_buttons.add(name)
        if self._switch_mode(name, now):
            return
        shift = "SHIFT" in self._held_buttons
        if shift and name == "PLAY":
            self._recalibrate(1)
            return
        if shift and name.startswith("GROUP_"):
            self._recalibrate(GROUPS.index(name[-1]) * BLOCK_BARS + 1)
            return
        if "PATTERN" in self._held_buttons and name.startswith("GROUP_"):
            self.bank = GROUPS.index(name[-1])
            self.last_control = f"banque {name[-1]}"
            self.leds_dirty = True
            return
        if name.startswith("GROUP_"):
            if not self.design:  # live : pads toujours en rythmique
                return
            self.group = GROUPS.index(name[-1])
        elif name == "PAD_MODE" and self.design:
            self.group = (self.group + 1) % len(self.cfg.layouts)
        elif name == "GRID":
            i = QUANTIZE_CYCLE.index(self.quantize)
            self.quantize = QUANTIZE_CYCLE[(i + 1) % len(QUANTIZE_CYCLE)]
        elif name == "NOTE_REPEAT":
            if shift:
                self.repeat_locked = not self.repeat_locked
                if not self.repeat_locked:
                    self._repeats.clear()
            else:
                self.repeat_held = True
        elif name.startswith("DISPLAY_") and self.repeat_active:
            self.division = DIVISIONS[int(name[-1]) - 1][0]
        elif name in MODIFIERS:
            pass
        else:
            return
        self.leds_dirty = True

    def _pad(self, pad: int, ev: PadEvent, now: int) -> list[Timed]:
        if pad in self._consumed:  # frappé avec un modificateur : pas de note jusqu'au relâché
            if not ev.pressed:
                self._consumed.discard(pad)
            return []
        if ev.pressed and pad not in self._pressure and self._held_buttons & set(MODIFIERS):
            self._consumed.add(pad)
            self.leds_dirty = True
            return self._command(pad, now)
        if ev.pressed:
            was_held = pad in self._pressure
            self._pressure[pad] = ev.pressure
            if pad in self._attacks:
                att = self._attacks[pad]
                att.peak = max(att.peak, ev.pressure)
            elif not was_held:  # pad tenu à la fin d'un repeat : pas de nouvelle frappe
                self._attacks[pad] = _Attack(now, ev.pressure)
                self.leds_dirty = True
            return self.tick(now)
        # relâché
        self._pressure.pop(pad, None)
        out: list[Timed] = []
        if pad in self._attacks:
            out += self._fire(pad, now)
        if self._repeats.pop(pad, None) is not None:
            self.leds_dirty = True
        if pad in self._sounding:
            note, on_at = self._sounding.pop(pad)
            out.append((max(now, on_at + NOTE_OFF_MIN_NS), NoteOff(self.channel, note)))
            self.leds_dirty = True
        return out

    # --- temps ----------------------------------------------------------------

    def tick(self, now: int) -> list[Timed]:
        """Attaques dont la fenêtre de vélocité est écoulée, coups de repeat à venir."""
        self._note(self.modes.update(now, self.running))
        self._update_phrase()
        window = int(self.cfg.velocity.window_ms * 1e6)
        out: list[Timed] = []
        for pad in [p for p, a in self._attacks.items() if now - a.start >= window]:
            out += self._fire(pad, now)
        horizon = now + int(self.cfg.play.horizon_ms * 1e6)
        div = DIVISION_TICKS[self.division]
        for pad, rep in self._repeats.items():
            while (t := self._time_of(rep.next_pos)) is not None and t < horizon:
                vel = velocity(self.cfg.velocity, self._pressure.get(pad, 0))
                gate = self._time_of(rep.next_pos + div * GATE) or t + NOTE_OFF_MIN_NS
                out.append((max(t, now), NoteOn(self.channel, rep.note, vel)))
                out.append((max(gate, now + NOTE_OFF_MIN_NS), NoteOff(self.channel, rep.note)))
                self.last_played = (pad, rep.note, vel)
                rep.next_pos += div
        return out

    def _update_phrase(self) -> None:
        ticks = self.clock.ticks_since_start
        st = None if ticks is None else self.phrase.update(ticks)
        self.phrase_state = st
        sig: tuple[object, ...] = (
            () if st is None else (st.blocks_lit, st.blinking and st.half_beat_on, st.pulse)
        )
        if sig != self._phrase_leds:
            self._phrase_leds = sig
            self.leds_dirty = True

    def _time_of(self, position: float) -> int | None:
        t = self.clock.position_time(position + swing_offset(position, self.swing))
        return None if t is None else int(t)

    def _fire(self, pad: int, now: int) -> list[Timed]:
        att = self._attacks.pop(pad)
        note = pad_note(self.layout, pad)
        vel = velocity(self.cfg.velocity, att.peak)
        self.last_played = (pad, note, vel)
        ticks = self.clock.ticks_at(att.start)  # instant de la frappe, pas de la fin de fenêtre
        if ticks is None:  # transport arrêté : immédiat, pas de repeat
            self._sounding[pad] = (note, now)
            return [(now, NoteOn(self.channel, note, vel))]
        if self.repeat_active:
            pos, _ = nearest(ticks, DIVISION_TICKS[self.division])
            self._repeats[pad] = _Repeat(note, pos)
            return self.tick(now)
        target = now
        self.last_decision = f"frappe {ticks:.1f} ticks, Qoff"
        if self.quantize != "off":
            pos, immediate = nearest(ticks, GRID_TICKS[self.quantize])
            t = self._time_of(pos)
            if not immediate and t is not None:
                target = max(now, t)
            ms = (ticks - pos) * (self.clock.period_ns or 0) / 1e6
            verdict = "immédiat" if immediate else "retardé"
            self.last_decision = f"frappe {ticks:.1f} -> pas {pos:.0f} ({ms:+.0f} ms) {verdict}"
        self._sounding[pad] = (note, target)
        return [(target, NoteOn(self.channel, note, vel))]

    # --- sorties ----------------------------------------------------------------

    def status(self) -> str:
        q = "Qoff" if self.quantize == "off" else f"Q{self.quantize[2:]}"
        rep = f"  R{self.division}{'*' if self.repeat_locked else ''}" if self.repeat_active else ""
        return f"T{self.track:02d}  {q}  SW{self.swing}{rep}"

    def leds(self) -> LedState:
        layout = self.layout
        dim = self.cfg.leds.dim
        lit = set(self._attacks) | set(self._sounding) | set(self._repeats)
        held = self._held_buttons
        pads: list[RGB] = [(0, 0, 0)] * N_PADS
        for index in range(N_PADS):
            pad = pad_label(index)
            full = pad_color(self.cfg, layout, pad)
            auto = pad == self.cfg.midi.auto_channel
            if auto and ("MUTE" in held or ("SELECT" in held and not self.design)):
                pads[index] = (0, 0, 0)  # track de l'AUTO CHANNEL : pas joignable
            elif "MUTE" in held:  # tracks ouvertes pleines, mutées éteintes
                pads[index] = (0, 0, 0) if self.faders.muted.get(pad) else full
            elif "SELECT" in held:
                pads[index] = full if pad == self.track else scale(full, dim)
            else:
                pads[index] = full if pad in lit else scale(full, dim)
        st = self.phrase_state
        if "PATTERN" in held:  # PATTERN tenu : les GROUP montrent la banque
            white = self.cfg.families["chromatique"]
            groups = [scale(white, 1.0 if g == self.bank else dim) for g in range(len(GROUPS))]
        elif st is None and not self.design:  # live arrêté : GROUP sans rôle, éteints
            groups = [(0, 0, 0)] * len(GROUPS)
        elif st is None:  # design arrêté : les GROUP montrent la disposition
            groups = [
                scale(self.cfg.families[lay.family], 1.0 if g == self.group else dim)
                for g, lay in enumerate(self.cfg.layouts)
            ]
        else:  # un bouton de plus toutes les 8 mesures ; le bloc en cours clignote avant un cap
            color = self.cfg.leds.phrase
            groups = [color if g < st.blocks_lit else (0, 0, 0) for g in range(len(GROUPS))]
            if st.blinking and not st.half_beat_on:
                groups[st.blocks_lit - 1] = (0, 0, 0)
        low = round(LED_MAX * dim)
        buttons = {
            "GRID": LED_MAX if self.quantize != "off" else 0,
            "NOTE_REPEAT": LED_MAX if self.repeat_active else 0,
            "SWING": LED_MAX if self.swing > 50 else 0,
            "PLAY": LED_MAX if st is not None and st.pulse else 0,
            "CONTROL": LED_MAX if self.design or self.modes.pending else low,
            "PAD_MODE": low if self.design else 0,
        }
        for name in MODIFIERS:
            buttons[name] = LED_MAX if name in held else low
        if self.repeat_active:
            for i, (name, _) in enumerate(DIVISIONS):
                buttons[f"DISPLAY_{i + 1}"] = LED_MAX if name == self.division else low
        self.leds_dirty = False
        return LedState(pads=pads, groups=groups, buttons=buttons)

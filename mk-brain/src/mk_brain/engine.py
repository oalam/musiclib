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
- Slice 5.D : design avec un projet (`project.py`). GROUP A-H = banque du
  projet : sa tonique cale les dispositions, sa gamme marque le hors gamme
  de la chromatique, sa phrase règle le compteur ; PAD MODE fait défiler les
  dispositions. Menu : boutons d'écran 1-4 = GAMME, TRACK, QUANT, PHRASE ;
  l'encodeur maître règle l'entrée qui a le focus (GAMME au départ), appliquée
  à chaque cran ; son appui passe le focus à l'entrée suivante.
- Slice 6.B : en live, la banque du dernier PC reçu règle le contexte
  (`context`) : sa phrase s'applique avec la remise à 1 (tout de suite
  transport arrêté), sa tonique et son mode s'affichent, son titre et sa
  description s'annoncent 2 s au changement de banque (`announce`). En
  design, le PC reste sans effet sur la banque choisie.
- Slice 6.C : sélection de projet (`selection.py`) : SHIFT + BROWSE l'ouvre
  (refusée en live transport lancé) ou la ferme ; l'encodeur maître fait
  défiler, son appui charge le projet (`set_project`), `loaded` le nomme
  pour que la CLI le retienne.
- Session (`session.py`) : `snapshot` et `restore` des derniers réglages
  (banque, pattern, track, faders, mutes), sans rien envoyer à la DT2.
- Slice 8 : mode unique (live et design fusionnés, `modes.py` retiré). Pads
  en MPC (table `mpc` : tranche sur le canal de sa track) ou en clavier
  (disposition de la banque sur la track sélectionnée), PAD MODE bascule.
  Une banque courante (PC reçu ou GROUP seul), une quantize, menu et
  PATTERN + pad toujours disponibles. Les mentions live / design ci-dessus
  sont l'historique des slices 5-6.
- Slice 9 : PATTERN + pad retiré (la DT2 seule change de pattern) ; LED GROUP
  arrêté = la banque courante seule ; perform par SOLO (`perform_lock`) : les
  pads ne jouent plus, un tap sur le pad n ajoute ou retire la track n au groupe
  des encodeurs, PAD MODE en sort ; PB tenu par SHIFT ;
  écrans du clavier = ceux du MPC.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable
from dataclasses import dataclass

from mk_brain.arp import (
    BARS,
    BARS_TICKS,
    CHANCE,
    CHANCE_ODDS,
    CHORD_LABELS,
    CHORDS,
    GATE_MAX,
    GATE_MIN,
    GATE_STEP,
    INVERSION_LABELS,
    INVERSIONS,
    MAX_OCTAVES,
    ORDER_LABELS,
    ORDERS,
    REST,
    TIE,
    ArpBars,
    ArpChord,
    ArpInversion,
    ArpOrder,
    accented,
    degree_steps,
    hits,
    shift,
    spread,
    ties_after,
)
from mk_brain.arp import chord as arp_chord
from mk_brain.arp import sequence as arp_sequence
from mk_brain.clock import ClockTracker
from mk_brain.config import PITCH_BEND, PRESET_SLOTS, RGB, ArpPreset, Config, Layout
from mk_brain.faders import Accel, Faders
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
from mk_brain.layouts import (
    FLAT_NAMES,
    N_PADS,
    fits,
    for_bank,
    in_scale,
    pad_color,
    pad_note,
    scale,
    shift_octave,
    velocity,
)
from mk_brain.phrase import BLOCK_BARS, PhraseCounter, PhraseLength, PhraseState, pattern_label
from mk_brain.presets import user_name
from mk_brain.project import Bank, Project
from mk_brain.quantize import (
    GRID_TICKS,
    QUANTIZE_CYCLE,
    QuantizeMode,
    clamp_swing,
    nearest,
    swing_offset,
)
from mk_brain.repeat import DIVISION_TICKS, DIVISIONS, GATE
from mk_brain.selection import Selector
from mk_brain.session import FaderValue, Session

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


@dataclass(frozen=True, slots=True)
class PitchBend:
    channel: int
    pitch: int  # -8192..8191, 0 = centre (mido)


@dataclass(frozen=True, slots=True)
class Aftertouch:
    """Aftertouch de canal (channel pressure) : une valeur pour toute la track."""

    channel: int
    value: int  # 0-127


MidiOut = NoteOn | NoteOff | ControlChange | ProgramChange | PitchBend | Aftertouch
MODIFIERS = ("MUTE", "SELECT")  # + pad : commande, pas de note
KEYBOARD_GROUP = 0  # chromatique, disposition du clavier sans banque
ARP_TAP_NS = 300_000_000  # PATTERN relâché avant : appui bref (sortie d'ARPG), sinon config
POWEROFF_HOLD_NS = 2_000_000_000  # SHIFT + ERASE tenus : extinction du Pi
MAX_OCTAVE = 4  # clavier : décalage d'octave borné à ±4 (flèches de transport)
MENU = ("GAMME", "TRACK", "QUANT", "PHRASE")  # boutons d'écran 1-4 (banque : GROUP)
PHRASES: tuple[PhraseLength, ...] = (32, 64)
Timed = tuple[int, MidiOut]


@dataclass
class _Attack:
    start: int
    peak: int


@dataclass
class _Repeat:
    channel: int
    note: int
    next_pos: float


@dataclass
class _ArpNote:
    channel: int
    note: int
    velocity: int  # dernière vélocité jouée : celle des notes maintenues, pad relâché


class Engine:
    def __init__(
        self,
        cfg: Config,
        clock: ClockTracker | None = None,
        project: Project | None = None,
        catalog: Callable[[], Selector] | None = None,
    ) -> None:
        self.cfg = cfg
        self.project = project
        self.catalog = catalog  # liste des projets pour la sélection (lue à chaque ouverture)
        self.selector: Selector | None = None  # sélection de projet ouverte
        self.loaded: str | None = None  # nom du dernier projet chargé par la sélection
        self._phrase_override: PhraseLength | None = None  # menu PHRASE ; None = celle de la banque
        self.menu = 0  # entrée de menu qui a le focus (index dans MENU) ; GAMME au départ
        self.clock = clock or ClockTracker()
        self.mpc = True  # pads en MPC (table `mpc`) ; False : clavier (PAD MODE bascule)
        self.group = KEYBOARD_GROUP  # disposition du clavier (index dans `cfg.layouts`)
        self.quantize: QuantizeMode = cfg.play.quantize
        self.swing = cfg.play.swing
        self.division: str = cfg.play.repeat
        self.repeat_held = False
        self.repeat_locked = False
        self.arp = False  # mode ARPG (PATTERN) : les pads tenus du clavier sont arpégés
        # PATTERN tenu en ARPG : (instant de l'appui, appui qui a ouvert le mode ou servi
        # à un réglage) ; un appui bref qui n'a servi à rien sort du mode au relâché
        self._pattern_down: tuple[int, bool] | None = None
        self.arp_order: ArpOrder = cfg.arp.order
        self.arp_octaves = cfg.arp.octaves
        self.arp_gate = cfg.arp.gate
        self.arp_motif = cfg.arp.motif  # nom du motif (slice 12), ou OFF
        self.arp_chord: ArpChord = cfg.arp.chord  # un pad = un accord (slice 15), ou off
        self.arp_progression = cfg.arp.progression  # nom de la progression (slice 16), ou OFF
        self.arp_bars: ArpBars = cfg.arp.bars  # durée de chaque accord, en mesures
        self.arp_inversion: ArpInversion = cfg.arp.inversion  # renversement (slice 21)
        self._arp_degree: int | None = None  # rang de l'accord en cours dans la progression
        self._arp_tones: list[int] = []  # son accord, sur le premier pad tenu (écran)
        self.arp_preset: str | None = None  # dernier preset rappelé (slice 13)
        # slice 14 : emplacements 1-16 sauvés depuis la MK2 (`state/arp-presets.json`), qui
        # l'emportent sur ceux de la config ; `arp_bank_dirty` : fichier à réécrire
        self.arp_user: dict[int, ArpPreset] = {}
        self.arp_bank_dirty = False
        self.arp_hold = False  # maintien (NOTE REPEAT) : l'arpège continue pads relâchés
        self._arp_notes: dict[int, _ArpNote] = {}  # pad → note, dans l'ordre d'appui
        self._arp_pos: float | None = None  # position (ticks) de la prochaine note
        self._arp_step = 0
        self._arp_residue: dict[int, int] = {}  # encodeur de la page ARP → reste de rotation
        self._rng = random.Random()
        self._held_buttons: set[str] = set()
        self._attacks: dict[int, _Attack] = {}  # pad 1-16 → attaque en cours de mesure
        self._sounding: dict[int, tuple[int, int, int]] = {}  # pad → (canal, note, instant du on)
        self._repeats: dict[int, _Repeat] = {}
        self._pressure: dict[int, int] = {}
        # aftertouch : dernier envoi par canal (valeur, instant) ; absent = au repos
        self._aftertouch_sent: dict[int, tuple[int, int]] = {}
        self.leds_dirty = True
        self.last_played: tuple[int, int, int] | None = None  # (pad, note, vélocité)
        self.last_decision = ""  # diagnostic quantize : position de la frappe et décision
        self.phrase = PhraseCounter(cfg.play.phrase)
        self.phrase_state: PhraseState | None = None
        self._phrase_leds: tuple[object, ...] = ()
        self.log: list[str] = []  # évènements du compteur, lus et vidés par la CLI
        enc = cfg.encoders
        pages = [[(e.name, e.param) for e in page] for page in enc.pages]
        accel = (
            None
            if enc.accel is None
            else Accel(
                enc.accel.raw_per_step,
                enc.accel.slow,
                enc.accel.fast,
                int(enc.accel.window_ms * 1e6),
            )
        )
        self.faders = Faders(pages, enc.mute_cc, enc.raw_per_step, accel)
        self.track = 1  # track des encodeurs (SELECT + pad)
        self.last_program: int | None = None  # dernier PC reçu
        self.bank: int | None = None  # banque courante, 0 = A : PC reçu ou GROUP seul
        self.last_control = ""  # dernier geste de contrôle, pour l'écran
        self._consumed: set[int] = set()  # pads frappés avec un modificateur
        self.last_touch: tuple[int, int] | None = None  # (encodeur 1-8, instant) pour l'écran
        self.last_hit: tuple[int, int, int, int] | None = None  # (pad, note, vélocité, instant)
        self.last_hit_mpc = False  # dernière frappe jouée en MPC (écran : label et cible)
        self.perform_lock = False  # SOLO : perform verrouillé, les pads ne jouent plus
        self._latched: dict[int, int] = {}  # perform verrouillé : pads allumés → track visée
        self._released_at: dict[int, int] = {}  # SOLO : dernier relâché de chaque pad (rebonds)
        # SHIFT tenu : valeur d'avant de chaque (track, paramètre) tourné, rendue au relâché
        self._shift_saved: dict[tuple[int, int], int] = {}
        self._bent: set[int] = set()  # tracks dont le pitch bend est hors du centre (SHIFT tenu)
        self.poweroff_enabled = False  # vrai sous le service du Pi (posé par la CLI)
        self.poweroff = False  # extinction demandée : la CLI sort de la boucle et éteint
        self._poweroff_since: int | None = None  # début de l'appui SHIFT + ERASE
        self.octave = 0  # décalage d'octave du clavier (flèches de transport), remis à 0 par GROUP
        # annonce d'une nouvelle banque reçue par PC : (clé, fiche, instant) ; instant posé au tick
        self.announce: tuple[str, Bank, int | None] | None = None

    @property
    def mode_name(self) -> str:
        """Mode courant, toujours affiché : MUTE ou SELECT tenu, SOLO, ARPG, sinon KEYS
        ou MPC."""
        for name in MODIFIERS:  # tenu : le pad commande, comme les LED
            if name in self._held_buttons:
                return name
        if self.perform_lock:
            return "SOLO"
        return "ARPG" if self.arp else "KEYS" if self.keyboard else "MPC"

    @property
    def keyboard(self) -> bool:
        """Pads en clavier (vue détaillée à l'écran) ; False : MPC."""
        return not self.mpc

    @property
    def sheet(self) -> tuple[str, Bank] | None:
        """Fiche de la banque courante (clé, banque), None sans banque ou hors projet."""
        if self.project is None or self.bank is None:
            return None
        return self.project.bank(self.bank)

    @property
    def layout(self) -> Layout:
        """Disposition du clavier, calée sur la banque courante et décalée d'octave."""
        lay = self.cfg.layouts[self.group]
        sheet = self.sheet
        if sheet is not None:
            bank = sheet[1]
            lay = for_bank(lay, self.cfg.scale(bank.mode), bank.tonic)
        return shift_octave(lay, self.octave)

    @property
    def running(self) -> bool:
        return self.clock.ticks_since_start is not None

    @property
    def next_pattern(self) -> str | None:
        """Prochain pattern, annoncé par la DT2 (PC reçu)."""
        nxt = self.phrase.next_pattern
        return None if nxt == self.phrase.pattern else nxt

    @property
    def perform_tracks(self) -> list[int]:
        """Tracks des encodeurs en perform (SOLO) : pads allumés, dans l'ordre des taps."""
        return list(self._latched.values())

    @property
    def perform_track(self) -> int | None:
        """Première track du groupe SOLO, None sans groupe."""
        return next(iter(self.perform_tracks), None)

    @property
    def fader_track(self) -> int:
        """Track dont les faders s'affichent : celle du perform, sinon la sélectionnée."""
        perform = self.perform_track
        return self.track if perform is None else perform

    @property
    def repeating(self) -> bool:
        """Un pad au moins répète (note repeat en cours)."""
        return bool(self._repeats)

    @property
    def repeat_active(self) -> bool:
        """NOTE REPEAT tenu ou verrouillé ; jamais en ARPG, où l'arpège le remplace."""
        return not self.arp and (self.repeat_held or self.repeat_locked)

    @property
    def arp_menu(self) -> bool:
        """Config de l'arpège à l'écran et sous les encodeurs : ARPG, PATTERN tenu."""
        return self.arp and "PATTERN" in self._held_buttons

    def arp_view(self) -> list[tuple[str, str]]:
        """Config de l'arpège, encodeurs 1-8 : (abrégé, valeur affichée)."""
        return [
            ("ORD", ORDER_LABELS[self.arp_order]),
            ("OCT", str(self.arp_octaves)),
            ("GATE", f"{self.arp_gate}%"),
            ("MOT", self.arp_motif),
            ("INV", INVERSION_LABELS[self.arp_inversion]),
            ("CHD", CHORD_LABELS[self.arp_chord]),
            ("PRG", self.arp_progression),
            ("BAR", self.arp_bars),
        ]

    @property
    def arp_preset_shown(self) -> str | None:
        """Le dernier preset rappelé, si aucun réglage ne s'en est écarté."""
        preset = self.arp_bank.get(self.arp_preset or "")
        return self.arp_preset if preset == self._arp_current() else None

    def _arp_current(self) -> ArpPreset:
        """Les cinq réglages courants, tels qu'un preset les garde."""
        return ArpPreset(
            order=self.arp_order,
            octaves=self.arp_octaves,
            gate=self.arp_gate,
            division=self.division,
            motif=self.arp_motif,
            chord=self.arp_chord,
            progression=self.arp_progression,
            bars=self.arp_bars,
            inversion=self.arp_inversion,
        )

    def arp_slots(self) -> list[tuple[str, ArpPreset] | None]:
        """Les 16 emplacements de la banque, pad 1 à 16 : (nom, réglages), ou None si vide.
        Sauvé depuis la MK2 (`U03`) d'abord, sinon le preset de même rang de la config."""
        config = list(self.cfg.arp.presets.items())
        slots: list[tuple[str, ArpPreset] | None] = []
        for n in range(1, PRESET_SLOTS + 1):
            if n in self.arp_user:
                slots.append((user_name(n), self.arp_user[n]))
            else:
                slots.append(config[n - 1] if n <= len(config) else None)
        return slots

    @property
    def arp_bank(self) -> dict[str, ArpPreset]:
        """Emplacements occupés, dans l'ordre des pads : nom → réglages."""
        return dict(slot for slot in self.arp_slots() if slot is not None)

    def _arp_recall(self, name: str) -> None:
        p = self.arp_bank[name]
        self.arp_preset = name
        self.arp_order, self.arp_octaves, self.arp_gate = p.order, p.octaves, p.gate
        self.division, self.arp_motif, self.arp_chord = p.division, p.motif, p.chord
        self.arp_progression, self.arp_bars = p.progression, p.bars
        self.arp_inversion = p.inversion
        self.leds_dirty = True

    def _preset_pad(self, pad: int) -> None:
        """PATTERN tenu en ARPG : pad n = rappel de l'emplacement n ; SHIFT + pad n = les
        réglages courants y sont écrits (slice 14)."""
        self._pattern_used()
        if "SHIFT" in self._held_buttons:
            self.arp_user[pad] = self._arp_current()
            self.arp_preset = user_name(pad)
            self.arp_bank_dirty = True
            self.last_control = f"ARP PRE {self.arp_preset} saved"
            return
        slot = self.arp_slots()[pad - 1]
        if slot is None:
            self.last_control = f"ARP PRE {pad:02d} empty"
            return
        self._arp_recall(slot[0])
        self.last_control = f"ARP PRE {slot[0]}"

    @property
    def arp_now(self) -> tuple[list[int], int, list[int]] | None:
        """Progression qui joue : (ses degrés, rang de l'accord en cours, notes de cet
        accord sur le premier pad tenu). None sans progression ou sans arpège lancé."""
        degrees = self.cfg.arp.progressions.get(self.arp_progression)
        if degrees is None or self._arp_degree is None or not self._arp_tones:
            return None
        return degrees, self._arp_degree % len(degrees), self._arp_tones

    @property
    def arp_steps(self) -> str | None:
        """Les 16 pas du motif choisi ; None sans motif (OFF)."""
        return self.cfg.arp.motifs.get(self.arp_motif)

    # --- entrées ------------------------------------------------------------

    def handle(self, ev: Event, now: int) -> list[Timed]:
        if isinstance(ev, ButtonEvent):
            self._button(ev, now)
            if ev.name == "SHIFT" and not ev.pressed:
                return self._release_shift(now)
            return []
        if isinstance(ev, EncoderEvent):
            if ev.index == 0:
                if self.selector is not None:
                    self.selector.scroll(ev.delta)
                elif "SWING" in self._held_buttons:
                    self.swing = clamp_swing(self.swing + ev.delta)
                else:
                    self._turn_menu(ev.delta)
                return []
            return self._encoder(ev.index, ev.delta, now)
        return self._pad(pad_label(ev.index), ev, now)

    def _reachable(self, track: int) -> bool:
        if track == self.cfg.midi.auto_channel:
            self.last_control = f"T{track:02d} = AUTO CHANNEL: no own channel"
            return False
        return True

    @staticmethod
    def _param_out(channel: int, param: int, value: int) -> MidiOut:
        if param == PITCH_BEND:  # 0-127 → -8192..8191, 64 = centre
            return PitchBend(channel, max(-8192, min(8191, (value - 64) * 128)))
        return ControlChange(channel, param, value)

    def _encoder(self, index: int, delta: int, now: int) -> list[Timed]:
        """CC sur le canal de la track sélectionnée ; la 16 est l'AUTO CHANNEL, donc la
        track active de la DT2 (p-locks en LIVE REC). En perform : sur les tracks des pads
        du groupe SOLO. PB seulement SHIFT tenu, au centre au relâché de SHIFT.
        PATTERN tenu en ARPG : réglages de l'arpège, rien n'est envoyé."""
        if self.arp_menu:
            self._arp_turn(index, delta, now)
            return []
        if self.faders.page[index - 1][1] == PITCH_BEND and "SHIFT" not in self._held_buttons:
            self.last_control = "PB: hold SHIFT"
            return []
        if self._latched:
            return self._perform_turn(index, delta, now)
        self.last_touch = (index, now)
        before = self.faders.value(self.track, self.faders.page[index - 1][1])
        sent = self.faders.turn(self.track, index, delta, now)
        if sent is None:
            return []
        param, value = sent
        self._keep_for_shift(self.track, param, before)
        name = self.faders.page[index - 1][0]
        self.last_control = f"T{self.track:02d} {name} {value}"
        channel = self.track - 1
        if param == PITCH_BEND:
            self._bent.add(self.track)
        return [(now, self._param_out(channel, param, value))]

    # --- arpégiateur : mode ARPG (slice 11) -------------------------------------

    def _pattern_pressed(self, now: int) -> None:
        """PATTERN : entre en ARPG (clavier) ; déjà en ARPG, l'appui ouvre la config tant
        qu'il est tenu, et sort du mode au relâché s'il a été bref et n'a rien réglé."""
        self._pattern_down = (now, not self.arp)
        if self.arp:
            return
        self.arp = True
        self.mpc = False
        self.repeat_held = False
        self._repeats.clear()

    def _pattern_released(self, now: int) -> None:
        down, self._pattern_down = self._pattern_down, None
        if self.arp and down is not None and not down[1] and now - down[0] < ARP_TAP_NS:
            self._leave_arp()
        self.leds_dirty = True

    def _pattern_used(self) -> None:
        """Un réglage fait PATTERN tenu : le relâché ne sortira pas du mode."""
        if self._pattern_down is not None:
            self._pattern_down = (self._pattern_down[0], True)

    def _leave_arp(self) -> None:
        """Sortie : l'arpège et son maintien s'arrêtent (les note off sont déjà planifiés)."""
        self.arp = self.arp_hold = False
        self._arp_residue.clear()
        self._arp_clear()

    def _arp_clear(self) -> None:
        self._arp_notes.clear()
        self._arp_pos = None
        self._arp_step = 0
        self._arp_degree = None
        self._arp_tones = []
        self.leds_dirty = True

    def _toggle_hold(self) -> None:
        """NOTE REPEAT en ARPG : maintien. Coupé, seules les notes des pads tenus restent."""
        self.arp_hold = not self.arp_hold
        if not self.arp_hold:
            for pad in [p for p in self._arp_notes if p not in self._pressure]:
                del self._arp_notes[pad]
            if not self._arp_notes:
                self._arp_clear()

    def _arp_turn(self, index: int, delta: int, now: int) -> None:
        """Encodeurs 1-8, PATTERN tenu en ARPG : ordre, octaves, gate, motif, preset, accord,
        progression, durée d'un accord.
        Course propre à la page (`arp.raw_per_choice`, `arp.raw_per_gate_step`) : au pas
        d'un CC, le moindre mouvement sautait plusieurs valeurs (essai du 2026-11-11)."""
        self._pattern_used()
        per = self.cfg.arp.raw_per_gate_step if index == 3 else self.cfg.arp.raw_per_choice
        acc = self._arp_residue.get(index, 0) + delta
        steps = int(acc / per)  # vers zéro, dans les deux sens
        self._arp_residue[index] = acc - steps * per
        if steps == 0:
            return
        self.last_touch = (index, now)
        if index == 1:
            i = max(0, min(len(ORDERS) - 1, ORDERS.index(self.arp_order) + steps))
            self.arp_order = ORDERS[i]
        elif index == 2:
            self.arp_octaves = max(1, min(MAX_OCTAVES, self.arp_octaves + steps))
        elif index == 3:
            self.arp_gate = max(GATE_MIN, min(GATE_MAX, self.arp_gate + GATE_STEP * steps))
        elif index == 4:
            names = self.cfg.arp.motif_names
            self.arp_motif = names[max(0, min(len(names) - 1, names.index(self.arp_motif) + steps))]
        elif index == 6:
            i = max(0, min(len(CHORDS) - 1, CHORDS.index(self.arp_chord) + steps))
            self.arp_chord = CHORDS[i]
        elif index == 7:
            names = self.cfg.arp.progression_names
            i = max(0, min(len(names) - 1, names.index(self.arp_progression) + steps))
            self.arp_progression = names[i]
        elif index == 8:
            self.arp_bars = BARS[max(0, min(len(BARS) - 1, BARS.index(self.arp_bars) + steps))]
        else:  # renversement (les presets se rappellent aux pads)
            i = INVERSIONS.index(self.arp_inversion) + steps
            self.arp_inversion = INVERSIONS[max(0, min(len(INVERSIONS) - 1, i))]
        self.leds_dirty = True  # le pad du preset courant s'éteint dès qu'un réglage s'en écarte
        name, value = self.arp_view()[index - 1]
        self.last_control = f"ARP {name} {value}"

    def _arp_add(self, pad: int, channel: int, note: int, vel: int, ticks: float) -> None:
        """Frappe en ARPG : la note entre dans l'arpège. En maintien, une frappe alors
        qu'aucun pad de l'arpège n'est tenu remplace les notes ; sinon elle s'ajoute."""
        if self.arp_hold and not any(p in self._pressure for p in self._arp_notes if p != pad):
            self._arp_notes.clear()
            self._arp_step = 0
        self._arp_notes.pop(pad, None)
        self._arp_notes[pad] = _ArpNote(channel, note, vel)
        if self._arp_pos is None:
            self._arp_pos, _ = nearest(ticks, DIVISION_TICKS[self.division])
            self._arp_step = 0
        self.leds_dirty = True

    def _arp_tick(self, now: int, horizon: int, div: float) -> list[Timed]:
        """Notes de l'arpège à venir avant `horizon` : une par division, vélocité de la
        pression courante du pad (la dernière jouée s'il est relâché, en maintien).

        Motif (slice 12) : le pas est la position sur la grille de la division, modulo la
        longueur du motif (16 pas : calé sur la mesure en 1/16 ; moins : il tourne contre elle).
        Silence et liée ne consomment pas de note ; un pas
        `x` est atténué (`arp.unaccented`) ; les liées qui suivent allongent la note."""
        out: list[Timed] = []
        steps = self.arp_steps
        while self._arp_notes and self._arp_pos is not None:
            t = self._time_of(self._arp_pos)
            if t is None or t >= horizon:
                break
            kind, ties = None, 0
            if steps is not None:
                index = round(self._arp_pos / div) % len(steps)
                kind = steps[index]
                # silence, liée, ou pas `?` perdu au tirage : la note attend le prochain pas joué
                if kind in (REST, TIE) or (kind == CHANCE and self._rng.random() >= CHANCE_ODDS):
                    self._arp_pos += div
                    continue
                ties = ties_after(steps, index)
            held = [(p, n.note) for p, n in self._arp_notes.items()]
            anchors = dict(held)  # notes des pads avant progression : repère de `INV FIX`
            lay = self.layout
            scale = {(lay.base + i) % 12 for i in lay.intervals}
            degrees = self.cfg.arp.progressions.get(self.arp_progression)
            if degrees is not None:  # progression : les pads tenus suivent les degrés
                rank = int((self._arp_pos + 0.01) // BARS_TICKS[self.arp_bars]) % len(degrees)
                if rank != self._arp_degree:  # nouvel accord : l'arpège repart de sa 1re note
                    self._arp_degree = rank
                    self._arp_step = 0
                move = degree_steps(degrees[rank])
                held = [(p, m) for p, n in held if (m := shift(n, move, scale)) in range(128)]
                if not held:  # tout est sorti de 0-127 : rien à jouer sur ce pas
                    self._arp_pos += div
                    continue
                self._arp_tones = arp_chord(held[0][1], self.arp_chord, scale)
            if self.arp_chord != "off" or self.arp_inversion != "off":
                # un pad = un accord, pris dans la gamme du clavier, renversé ou non
                held = spread(held, self.arp_chord, scale, self.arp_inversion, anchors)
            seq = arp_sequence(held, self.arp_order, self.arp_octaves)
            if self.arp_order == "random":
                pad, note = seq[self._rng.randrange(len(seq))]
            else:
                pad, note = seq[self._arp_step % len(seq)]
            entry = self._arp_notes[pad]
            if pad in self._pressure and pad not in self._attacks:
                entry.velocity = velocity(self.cfg.velocity, self._pressure[pad])
            vel = entry.velocity
            if kind is not None and not accented(kind):  # pas ordinaire : atténué
                vel = max(1, round(vel * self.cfg.arp.unaccented / 100))
            count = hits(kind) if kind is not None else 1  # ratchet : la note rejouée dans le pas
            part = div / count
            for h in range(count):
                start = self._arp_pos + part * h
                tied = div * ties if h == count - 1 else 0  # les liées prolongent le dernier coup
                on = max(self._time_of(start) or t, now)
                off = self._time_of(start + tied + part * self.arp_gate / 100) or on
                nxt = self._time_of(start + tied + part)
                if nxt is not None:  # gate 100 % : coupée juste avant le coup suivant
                    off = min(off, nxt - NOTE_OFF_MIN_NS)
                out.append((on, NoteOn(entry.channel, note, vel)))
                out.append((max(off, on + NOTE_OFF_MIN_NS), NoteOff(entry.channel, note)))
            self.last_played = (pad, note, vel)
            self._arp_pos += div
            self._arp_step += 1
        return out

    # --- perform : SOLO -------------------------------------------------------

    def _latch(self, pad: int) -> None:
        """Perform verrouillé : un tap ajoute la track n du pad n au groupe, un second la
        retire (grille des tracks, jamais la table `mpc`)."""
        self._consumed.add(pad)  # pas de note jusqu'au relâché
        self.leds_dirty = True
        if self._latched.pop(pad, None) is not None:
            self.last_control = f"PERF -T{pad:02d}"
            return
        track = pad  # SOLO : pad n = track n, en MPC comme en clavier
        if self._reachable(track):
            self._latched[pad] = track
            self.last_control = f"PERF +T{track:02d}"

    def _toggle_lock(self) -> None:
        """SOLO : perform verrouillé ou pads rejoués ; la sortie vide le groupe."""
        self.perform_lock = not self.perform_lock
        if not self.perform_lock:
            self._latched.clear()

    def _perform_turn(self, index: int, delta: int, now: int) -> list[Timed]:
        """Encodeur en perform : même pas sur chaque track tenue."""
        self.last_touch = (index, now)
        steps = self.faders.steps(index, delta, now)
        if steps == 0:
            return []
        param = self.faders.page[index - 1][1]
        name = self.faders.page[index - 1][0]
        out: list[Timed] = []
        for track in self.perform_tracks:
            before = self.faders.value(track, param)
            value = self.faders.nudge(track, param, steps)
            if value is None:
                continue
            self._keep_for_shift(track, param, before)
            self.last_control = f"PERF T{track:02d} {name} {value}"
            if param == PITCH_BEND:
                self._bent.add(track)
            out.append((now, self._param_out(track - 1, param, value)))
        return out

    def _command(self, pad: int, now: int) -> list[Timed]:
        held = self._held_buttons
        if "SELECT" in held:  # la 16 = AUTO CHANNEL : la track active de la DT2
            self.track = pad
            auto = pad == self.cfg.midi.auto_channel
            self.last_control = f"T{pad:02d} selected" + (" (DT2 active)" if auto else "")
            return []
        if "MUTE" in held:
            if not self._reachable(pad):
                return []
            cc, value = self.faders.toggle_mute(pad)
            self.last_control = f"T{pad:02d} {'muted' if value else 'unmuted'}"
            return [(now, ControlChange(pad - 1, cc, value))]
        return []

    def on_control_change(self, channel: int, control: int, value: int) -> None:
        """CC reçu de la DT2 (canal 0-15) : bouton ou mute joué sur la machine.

        Mutes : sur le canal de la track ; sur l'AUTO CHANNEL, pas de track sûre,
        ignorés. Boutons, selon `OUTPUT CH` de la DT2 (`midi.knobs_on_track_channel`) :
        - TRACK CH (vérifié le 2026-11-09) : canal de la track active, la MK2 la
          sélectionne (sur l'AUTO CHANNEL, c'est la track 16) ;
        - AUTO CH : sans dire quelle track est active, la valeur va à la track
          sélectionnée sur la MK2.
        """
        track = channel + 1
        auto = track == self.cfg.midi.auto_channel
        if control == self.faders.mute_cc:
            if not auto:
                self.faders.received(track, control, value)
                self.leds_dirty = True
            return
        if auto and not self.cfg.midi.knobs_on_track_channel:
            track = self.track
        elif track != self.track:
            self.track = track  # suit la track active de la DT2
            self.last_control = f"T{track:02d} selected (DT2)"
        self.faders.received(track, control, value)
        self.leds_dirty = True

    def on_start(self) -> None:
        self.phrase.start()

    def on_stop(self) -> None:
        self._arp_clear()  # pas d'arpège à l'arrêt, même maintenu
        self.phrase.stop()
        self.phrase_state = None
        self.leds_dirty = True

    def on_program_change(self, program: int) -> None:
        """PC reçu : banque courante, faders hors prise ; transport lancé, mesure 1 à la barre
        suivante (arrêté : compteur inchangé).

        Une autre banque devient la banque courante, comme GROUP : disposition du clavier
        calée sur son mode, octave à 0, sa phrase avec la remise (arrêté : tout de suite),
        son titre annoncé 2 s. Un autre pattern de la même banque garde les surcharges.
        """
        if program != self.last_program:
            self.faders.pattern_changed()
        # la DT2 change de banque, et pas vers celle déjà choisie (GROUP) : surcharges gardées
        moved = self.last_program is None or program // 16 != self.last_program // 16
        new_bank = moved and program // 16 != self.bank
        self.last_program = program
        if new_bank:
            self.log.append(f"banque {pattern_label(program)[0]} (PC reçu)")
            self._set_bank(program // 16)
        length = self._phrase_length()
        sheet = self.sheet
        if new_bank and sheet is not None:
            self.announce = (*sheet, None)
            self.last_control = f"{sheet[0]} (DT2)"
            self.log.append(f"{sheet[0]} : {sheet[1].title}, phrase {length}")
        label = pattern_label(program)
        ticks = self.clock.ticks_since_start
        if ticks is None:  # arrêté : pattern et phrase changés tout de suite, compteur inchangé
            self.phrase.pattern = label
            if length is not None:
                self.phrase.length = length
            return
        at = self.phrase.reset_next_bar(ticks, pattern=label, length=length)
        self.log.append(f"PC {label} -> mesure 1 à la barre {at + 1}")

    def _recalibrate(self, first_bar: int) -> bool:
        ticks = self.clock.ticks_since_start
        if ticks is None or first_bar > self.phrase.length:
            return False
        at = self.phrase.reset_next_bar(ticks, first_bar=first_bar)
        self.log.append(f"recalage -> mesure {first_bar} à la barre {at + 1}")
        return True

    # --- projet : sélection et chargement ---------------------------------------

    def open_selection(self) -> None:
        """Ouvre la liste des projets ; refusée transport lancé."""
        if self.running:
            self._note("transport running: no project change")
            return
        if self.catalog is None:
            self._note("no project list")
            return
        self.selector = self.catalog()
        self.leds_dirty = True

    def _load_selected(self) -> None:
        assert self.selector is not None
        entry = self.selector.current
        if entry is None or entry.project is None:
            self._note("no project" if entry is None else f"{entry.name}: invalid")
            return
        self.selector = None
        self.set_project(entry.project)
        self.loaded = entry.name
        self._note(f"project {entry.name}")

    def set_project(self, project: Project | None) -> None:
        """Change de projet : la banque courante (dernier PC ou GROUP) prend ses réglages."""
        self.project = project
        self.announce = None
        if self.bank is not None:
            self._set_bank(self.bank)
        self._apply_phrase()
        self.leds_dirty = True

    # --- session : derniers réglages -------------------------------------------

    def snapshot(self) -> Session:
        values = self.faders.values()
        return Session(
            layout=self.cfg.layouts[self.group].name,
            octave=self.octave,
            bank=self.bank,
            program=self.last_program,
            track=self.track,
            page=self.faders.page_index,
            faders=[
                FaderValue(track=t, param=p, value=v)
                for (t, p), v in sorted(values.items())
                if p != PITCH_BEND  # ressort : toujours au centre au départ
            ],
            muted=sorted(t for t, m in self.faders.muted.items() if m),
            division=self.division,
            arp_order=self.arp_order,
            arp_octaves=self.arp_octaves,
            arp_gate=self.arp_gate,
            arp_motif=self.arp_motif,
            arp_chord=self.arp_chord,
            arp_progression=self.arp_progression,
            arp_bars=self.arp_bars,
            arp_inversion=self.arp_inversion,
            arp_preset=self.arp_preset,
        )

    def restore(self, session: Session) -> None:
        """Reprend une session sauvée ; ce que la DT2 a déjà dit (PC reçu) l'emporte.

        Sessions d'avant la slice 8 : `bank`, sinon `design_bank` (banque du design)."""
        if self.bank is None:
            saved = session.bank if session.bank is not None else session.design_bank
            if saved is not None:
                self._set_bank(saved)
        for i, lay in enumerate(self.cfg.layouts):  # par son nom, ou son groupe (avant)
            if session.layout is not None and session.layout in (lay.name, lay.group):
                self.group = i
                break
        if abs(session.octave) <= MAX_OCTAVE:
            self.octave = session.octave
            if not fits(self.layout):
                self.octave = 0
        if self.last_program is None and session.program is not None:
            self.last_program = session.program
            self.phrase.pattern = pattern_label(session.program)
        self.track = session.track
        if session.page < self.faders.n_pages:
            self.faders.page_index = session.page
        values = {(f.track, f.param): f.value for f in session.faders}
        self.faders.restore(values, set(session.muted))
        if session.division in DIVISION_TICKS:
            self.division = session.division
        for order in ORDERS:
            if order == session.arp_order:
                self.arp_order = order
        if session.arp_octaves is not None and 1 <= session.arp_octaves <= MAX_OCTAVES:
            self.arp_octaves = session.arp_octaves
        if session.arp_gate is not None and GATE_MIN <= session.arp_gate <= GATE_MAX:
            self.arp_gate = session.arp_gate
        if session.arp_motif in self.cfg.arp.motif_names:
            self.arp_motif = session.arp_motif
        for kind in CHORDS:
            if kind == session.arp_chord:
                self.arp_chord = kind
        if session.arp_progression in self.cfg.arp.progression_names:
            self.arp_progression = session.arp_progression
        for bars in BARS:
            if bars == session.arp_bars:
                self.arp_bars = bars
        for inversion in INVERSIONS:
            if inversion == session.arp_inversion:
                self.arp_inversion = inversion
        if session.arp_preset in self.arp_bank:
            self.arp_preset = session.arp_preset
        self._apply_phrase()
        self.leds_dirty = True

    # --- banque courante et menu ----------------------------------------------

    def _set_bank(self, index: int) -> None:
        """Banque courante (GROUP, PC d'une autre banque, session) : octave à 0, phrase de
        la banque, disposition du clavier calée sur son mode (GAMME la surcharge ensuite,
        jusqu'au prochain changement de banque)."""
        self.bank, self._phrase_override, self.octave = index, None, 0
        found = None if self.project is None else self.project.bank(index)
        if found is not None:
            self.group = self.cfg.layouts.index(self.cfg.scale(found[1].mode))
        self.leds_dirty = True

    def _phrase_length(self) -> PhraseLength:
        """Phrase : celle du menu, sinon celle de la banque courante, sinon la config."""
        if self._phrase_override is not None:
            return self._phrase_override
        sheet = self.sheet
        if sheet is None or self.project is None:
            return self.cfg.play.phrase
        return self.project.phrase(sheet[1])

    def _apply_phrase(self) -> None:
        self.phrase.length = self._phrase_length()

    def _choose_bank(self, index: int) -> None:
        """GROUP seul : banque courante, sans rien envoyer à la DT2."""
        self._set_bank(index)
        self._apply_phrase()
        found = None if self.project is None else self.project.bank(index)
        if found is None:
            absent = "" if self.project is None else " (not in project)"
            self.last_control = f"bank {GROUPS[index]}{absent}"
            return
        key, bank = found
        self.last_control = f"{key}  {FLAT_NAMES[bank.tonic]} {self.cfg.scale(bank.mode).name}"

    def _shift_octave(self, step: int) -> None:
        """Flèches de transport en clavier : ±1 octave, ±4 au plus, notes dans 0-127."""
        if self.mpc:
            self.last_control = "octave: keyboard only"
            return
        new = self.octave + step
        if abs(new) > MAX_OCTAVE or not fits(shift_octave(self.layout, step)):
            self.last_control = f"octave limit {self.octave:+d}"
            return
        self.octave = new
        self.last_control = f"octave {new:+d}"
        self.leds_dirty = True

    def _menu_items(self, entry: int) -> tuple[list[str], int, Callable[[int], None]]:
        """Valeurs d'une entrée du menu, index de la valeur en cours, application."""
        name = MENU[entry]
        if name == "GAMME":
            labels = [lay.name for lay in self.cfg.layouts]
            return labels, self.group, lambda i: setattr(self, "group", i)
        if name == "TRACK":
            names = self.cfg.track_names
            labels = [f"T{t:02d} {names.get(t, '')}".rstrip() for t in range(1, 17)]
            return labels, self.track - 1, lambda i: setattr(self, "track", i + 1)
        if name == "QUANT":
            labels = [f"Q {q}" for q in QUANTIZE_CYCLE]
            cur = QUANTIZE_CYCLE.index(self.quantize)
            return labels, cur, lambda i: setattr(self, "quantize", QUANTIZE_CYCLE[i])

        def phrase(i: int) -> None:
            self._phrase_override = PHRASES[i]
            self._apply_phrase()

        return [f"{n} bars" for n in PHRASES], PHRASES.index(self.phrase.length), phrase

    def menu_view(self) -> list[tuple[str, str, bool]]:
        """Pour l'écran : (entrée, valeur en cours, focus)."""
        view = []
        for entry, name in enumerate(MENU):
            labels, cur, _ = self._menu_items(entry)
            view.append((name, labels[cur] if labels else "-", entry == self.menu))
        return view

    def _focus_menu(self, entry: int) -> None:
        """Bouton d'écran 1-4 : focus sur son entrée ; 5-8 sans effet."""
        if entry < len(MENU):
            self.menu = entry
            self.last_control = MENU[entry]

    def _turn_menu(self, delta: int) -> None:
        """Encodeur maître : la valeur de l'entrée qui a le focus, appliquée à chaque
        cran, en boucle."""
        labels, cur, apply = self._menu_items(self.menu)
        new = (cur + delta) % len(labels)
        if new != cur:
            apply(new)
            self.leds_dirty = True
        self.last_control = labels[new]

    def _keep_for_shift(self, track: int, param: int, before: int) -> None:
        """SHIFT tenu : retient la valeur d'avant le premier cran (le PB a son centre)."""
        if "SHIFT" in self._held_buttons and param != PITCH_BEND:
            self._shift_saved.setdefault((track, param), before)

    def _release_shift(self, now: int) -> list[Timed]:
        """SHIFT relâché : chaque paramètre tourné sous SHIFT revient à sa valeur d'avant,
        le pitch bend au centre sur chaque track où il est parti."""
        out: list[Timed] = []
        for (track, param), value in sorted(self._shift_saved.items()):
            self.faders.received(track, param, value)
            out.append((now, self._param_out(track - 1, param, value)))
        self._shift_saved.clear()
        for track in sorted(self._bent):
            self.faders.received(track, PITCH_BEND, 64)
            out.append((now, PitchBend(track - 1, 0)))
        self._bent.clear()
        self.leds_dirty = bool(out) or self.leds_dirty
        return out

    def _note(self, msg: str | None) -> None:
        if msg:
            self.last_control = msg
            self.log.append(msg)
            self.leds_dirty = True

    def _button(self, ev: ButtonEvent, now: int) -> None:
        name = ev.name
        if not ev.pressed:
            self._held_buttons.discard(name)
            if name in ("SHIFT", "ERASE") and self._poweroff_since is not None:
                self._poweroff_since = None
                self.last_control = "power off cancelled"
            if name in MODIFIERS or name.startswith("BROWSE_"):
                self.leds_dirty = True
            if name == "PATTERN":
                self._pattern_released(now)
            if name == "NOTE_REPEAT":
                self.repeat_held = False
                if not self.repeat_locked:
                    self._repeats.clear()
                self.leds_dirty = True
            return
        self._held_buttons.add(name)
        held = self._held_buttons
        shift = "SHIFT" in held
        if self.poweroff_enabled and name in ("SHIFT", "ERASE") and {"SHIFT", "ERASE"} <= held:
            self._poweroff_since = now
            self.last_control = "POWER OFF: hold 2 s"
            return
        if shift and name == "PLAY":
            self._recalibrate(1)
            return
        if shift and name.startswith("GROUP_"):
            self._recalibrate(GROUPS.index(name[-1]) * BLOCK_BARS + 1)
            return
        if shift and name in ("BROWSE_LEFT", "BROWSE_RIGHT"):  # sélection de projet
            if self.selector is not None:
                self.selector = None
                self.leds_dirty = True
            else:
                self.open_selection()
            return
        if name == "MASTER_PUSH" and self.selector is not None:
            self._load_selected()
            return
        if name in ("BROWSE_LEFT", "BROWSE_RIGHT"):  # page d'encodeurs
            page = self.faders.cycle(-1 if name == "BROWSE_LEFT" else 1)  # en boucle
            self.last_control = f"page {page + 1}/{self.faders.n_pages}"
            self.leds_dirty = True
            return
        if name in ("TRANSPORT_LEFT", "TRANSPORT_RIGHT"):  # octave du clavier
            self._shift_octave(-1 if name == "TRANSPORT_LEFT" else 1)
            return
        if name.startswith("GROUP_"):
            self._choose_bank(GROUPS.index(name[-1]))
        elif name == "SOLO" or (name == "PAD_MODE" and self.perform_lock):
            self._toggle_lock()  # PAD MODE sous SOLO : sortie, disposition inchangée
        elif name == "PATTERN":
            self._pattern_pressed(now)
        elif name == "PAD_MODE":  # MPC <-> clavier ; les notes tenues gardent leur cible
            if self.arp:  # ARPG : sortie vers MPC
                self._leave_arp()
            self.mpc = not self.mpc
            if not self.mpc:  # le mode est déjà affiché en bas à gauche : seule la gamme
                self.last_control = self.layout.name
        elif name == "GRID":
            i = QUANTIZE_CYCLE.index(self.quantize)
            self.quantize = QUANTIZE_CYCLE[(i + 1) % len(QUANTIZE_CYCLE)]
        elif name == "NOTE_REPEAT" and self.arp:
            self._toggle_hold()
        elif name == "NOTE_REPEAT":
            if shift:
                self.repeat_locked = not self.repeat_locked
                if not self.repeat_locked:
                    self._repeats.clear()
            else:
                self.repeat_held = True
        elif name.startswith("DISPLAY_") and (self.repeat_active or self.arp):
            self.division = DIVISIONS[int(name[-1]) - 1][0]
            self._pattern_used()
            if self._arp_pos is not None:  # arpège en cours : recalé sur la nouvelle grille
                div = DIVISION_TICKS[self.division]
                self._arp_pos = math.ceil(self._arp_pos / div) * div
        elif name.startswith("DISPLAY_"):
            self._focus_menu(int(name[-1]) - 1)
        elif name == "MASTER_PUSH":  # focus à l'entrée suivante, en boucle
            self._focus_menu((self.menu + 1) % len(MENU))
        elif name in MODIFIERS:
            pass
        else:
            return
        self.leds_dirty = True

    def _bounce(self, pad: int, now: int) -> bool:
        """Appui moins de `play.tap_debounce_ms` après le relâché d'une commande (SOLO, SELECT,
        MUTE) sur ce pad : rebond du doigt qui se lève, ignoré."""
        released = self._released_at.get(pad)
        return released is not None and now - released < int(self.cfg.play.tap_debounce_ms * 1e6)

    def _pad(self, pad: int, ev: PadEvent, now: int) -> list[Timed]:
        if pad in self._consumed:  # frappé avec un modificateur : pas de note jusqu'au relâché
            if not ev.pressed:
                self._consumed.discard(pad)
                self._released_at[pad] = now
            return []
        if ev.pressed and pad not in self._pressure and self.arp_menu:  # banque de presets
            self._consumed.add(pad)
            self.leds_dirty = True
            if not self._bounce(pad, now):
                self._preset_pad(pad)
            return []
        if ev.pressed and pad not in self._pressure and self._held_buttons & set(MODIFIERS):
            self._consumed.add(pad)
            self.leds_dirty = True
            return self._command(pad, now) if not self._bounce(pad, now) else []
        if ev.pressed and pad not in self._pressure and self.perform_lock:
            self._consumed.add(pad)
            if not self._bounce(pad, now):
                self._latch(pad)
            return []
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
        if pad in self._arp_notes and not self.arp_hold:  # sans maintien : la note sort
            del self._arp_notes[pad]
            if not self._arp_notes:
                self._arp_clear()
            self.leds_dirty = True
        if pad in self._sounding:
            channel, note, on_at = self._sounding.pop(pad)
            out.append((max(now, on_at + NOTE_OFF_MIN_NS), NoteOff(channel, note)))
            self.leds_dirty = True
        return out + self._aftertouch(now)

    # --- temps ----------------------------------------------------------------

    def tick(self, now: int) -> list[Timed]:
        """Attaques dont la fenêtre de vélocité est écoulée, coups de repeat à venir."""
        if self.selector is not None and self.running:
            self.selector = None  # Start : la sélection se ferme sur le projet en cours
            self._note("transport running: selection closed")
        if self.announce is not None and self.announce[2] is None:
            self.announce = (self.announce[0], self.announce[1], now)
        self._update_phrase()
        if self._poweroff_since is not None and now - self._poweroff_since >= POWEROFF_HOLD_NS:
            self._poweroff_since = None
            self.poweroff = True
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
                out.append((max(t, now), NoteOn(rep.channel, rep.note, vel)))
                out.append((max(gate, now + NOTE_OFF_MIN_NS), NoteOff(rep.channel, rep.note)))
                self.last_played = (pad, rep.note, vel)
                rep.next_pos += div
        out += self._arp_tick(now, horizon, div)
        return out + self._aftertouch(now)

    def _aftertouch(self, now: int) -> list[Timed]:
        """Pression des pads tenus → aftertouch de canal de leur track (slice 10).

        Un pad compte `aftertouch.delay_ms` après sa note, au-dessus de `threshold` : une
        frappe n'en envoie pas. Plusieurs pads sur un canal (clavier) : la pression la plus
        forte. Un message par canal et par `interval_ms`, seulement si la valeur change ;
        le retour à 0 au relâché part tout de suite. Les coups du NOTE REPEAT n'en envoient
        pas (leur pression règle déjà la vélocité)."""
        cfg = self.cfg.aftertouch
        delay, interval = int(cfg.delay_ms * 1e6), int(cfg.interval_ms * 1e6)
        levels: dict[int, int] = {}
        for pad, (channel, _, on_at) in self._sounding.items():
            if now - on_at < delay:
                continue
            span = cfg.full_scale - cfg.threshold
            x = min(1.0, max(0.0, (self._pressure.get(pad, 0) - cfg.threshold) / span))
            levels[channel] = max(levels.get(channel, 0), round(127 * x))
        out: list[Timed] = []
        for channel in sorted(set(levels) | set(self._aftertouch_sent)):
            value = levels.get(channel, 0)
            sent = self._aftertouch_sent.get(channel)
            if sent is None and value == 0:
                continue
            if sent is not None and (value == sent[0] or (value and now - sent[1] < interval)):
                continue
            out.append((now, Aftertouch(channel, value)))
            if value:
                self._aftertouch_sent[channel] = (value, now)
            else:
                del self._aftertouch_sent[channel]
        return out

    def _update_phrase(self) -> None:
        ticks = self.clock.ticks_since_start
        st = None if ticks is None else self.phrase.update(ticks)
        self.phrase_state = st
        sig: tuple[object, ...] = (
            () if st is None else (st.blocks_lit, st.blinking, st.half_beat_on)
        )
        if sig != self._phrase_leds:
            self._phrase_leds = sig
            self.leds_dirty = True

    def _time_of(self, position: float) -> int | None:
        t = self.clock.position_time(position + swing_offset(position, self.swing))
        return None if t is None else int(t)

    def target(self, pad: int) -> tuple[int, int]:
        """(canal 0-15, note) du pad : tranche de la table `mpc` sur le canal de sa track,
        ou note du clavier sur la track sélectionnée (la 16 = AUTO CHANNEL)."""
        if self.mpc:
            entry = self.cfg.mpc_pad(pad)
            return entry.track - 1, entry.note
        return self.track - 1, pad_note(self.layout, pad)

    def _fire(self, pad: int, now: int) -> list[Timed]:
        att = self._attacks.pop(pad)
        channel, note = self.target(pad)
        vel = velocity(self.cfg.velocity, att.peak)
        self.last_played = (pad, note, vel)
        self.last_hit = (pad, note, vel, now)
        self.last_hit_mpc = self.mpc
        ticks = self.clock.ticks_at(att.start)  # instant de la frappe, pas de la fin de fenêtre
        if ticks is None:  # transport arrêté : immédiat, pas de repeat
            self._sounding[pad] = (channel, note, now)
            return [(now, NoteOn(channel, note, vel))]
        if self.arp:  # la note entre dans l'arpège au lieu de sonner
            self._arp_add(pad, channel, note, vel, ticks)
            return self.tick(now)
        if self.repeat_active:
            pos, _ = nearest(ticks, DIVISION_TICKS[self.division])
            self._repeats[pad] = _Repeat(channel, note, pos)
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
        self._sounding[pad] = (channel, note, target)
        return [(target, NoteOn(channel, note, vel))]

    # --- sorties ----------------------------------------------------------------

    def status(self) -> str:
        q = "Qoff" if self.quantize == "off" else f"Q{self.quantize[2:]}"
        rep = f"  R{self.division}{'*' if self.repeat_locked else ''}" if self.repeat_active else ""
        return f"T{self.track:02d}  {q}  SW{self.swing}{rep}"

    def _pad_full(self, pad: int) -> tuple[RGB, bool]:
        """Couleur pleine du pad et s'il est allumé au repos (hors gamme du clavier éteint)."""
        if self.mpc:
            return self.cfg.mpc_pad(pad).color, True
        layout = self.layout
        return pad_color(self.cfg, layout, pad), in_scale(layout, pad)

    def leds(self) -> LedState:
        dim = self.cfg.leds.dim
        lit = set(self._attacks) | set(self._sounding) | set(self._repeats) | set(self._arp_notes)
        lit |= set(self._latched)  # pads du groupe SOLO : pleins
        held = self._held_buttons
        pads: list[RGB] = [(0, 0, 0)] * N_PADS
        slots, shown = self.arp_slots(), self.arp_preset_shown
        for index in range(N_PADS):
            pad = pad_label(index)
            track = self.cfg.track_colors[pad]  # modificateur tenu : pad n = track n
            auto = pad == self.cfg.midi.auto_channel
            if "MUTE" in held:  # tracks ouvertes pleines, mutées éteintes ; la 16 sans mute
                pads[index] = (0, 0, 0) if auto or self.faders.muted.get(pad) else track
            elif "SELECT" in held:
                pads[index] = track if pad == self.track else (0, 0, 0)
            elif self.arp_menu:  # banque de presets : occupé faible, courant plein, vide éteint
                slot = slots[pad - 1]
                if slot is not None:
                    full = self.cfg.leds.preset
                    pads[index] = full if slot[0] == shown else scale(full, dim)
            elif self.perform_lock:  # SOLO : remplace les couleurs du MPC et du clavier
                on = pad in self._latched
                pads[index] = self.cfg.leds.perform_on if on else self.cfg.leds.perform_idle
            else:
                full, rest = self._pad_full(pad)
                pads[index] = full if pad in lit else scale(full, dim if rest else 0)
        st = self.phrase_state
        if st is not None:  # un bouton de plus toutes les 8 mesures, les passés fixes
            color = self.cfg.leds.phrase
            groups = [color if g < st.blocks_lit else (0, 0, 0) for g in range(len(GROUPS))]
            # bloc en cours : clignote au temps, orange la dernière mesure avant un cap
            now_color = self.cfg.leds.phrase_warn if st.blinking else color
            groups[st.blocks_lit - 1] = now_color if st.half_beat_on else (0, 0, 0)
        else:  # arrêté : la banque courante seule allumée (slice 9)
            groups = [(0, 0, 0)] * len(GROUPS)
            if self.bank is not None:
                groups[self.bank] = self.cfg.leds.bank
        low = round(LED_MAX * dim)
        buttons = {
            "GRID": LED_MAX if self.quantize != "off" else 0,
            "NOTE_REPEAT": LED_MAX if self.repeat_active or self.arp_hold else 0,
            "PATTERN": LED_MAX if self.arp else low,
            "SWING": LED_MAX if self.swing > 50 else 0,
            "PLAY": LED_MAX if st is not None and st.half_beat_on else 0,  # au tempo
            "PAD_MODE": low if self.mpc else LED_MAX,
            "SOLO": LED_MAX if self.perform_lock else low,
        }
        for name in MODIFIERS:
            buttons[name] = LED_MAX if name in held else low
        for name in ("BROWSE_LEFT", "BROWSE_RIGHT"):  # cyclent : toujours disponibles
            buttons[name] = LED_MAX if name in held else low
        if self.keyboard:  # pleine du côté où l'on est décalé
            buttons["TRANSPORT_LEFT"] = LED_MAX if self.octave < 0 else low
            buttons["TRANSPORT_RIGHT"] = LED_MAX if self.octave > 0 else low
        if self.repeat_active or self.arp:
            for i, (name, _) in enumerate(DIVISIONS):
                buttons[f"DISPLAY_{i + 1}"] = LED_MAX if name == self.division else low
        else:
            for i in range(len(MENU)):
                buttons[f"DISPLAY_{i + 1}"] = LED_MAX if i == self.menu else low
        self.leds_dirty = False
        return LedState(pads=pads, groups=groups, buttons=buttons)

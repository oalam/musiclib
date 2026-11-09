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
  l'encodeur maître choisit, son appui valide, le même bouton ferme.
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
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from mk_brain.clock import ClockTracker
from mk_brain.config import PITCH_BEND, RGB, Config, Layout
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
from mk_brain.modes import ModeSwitch
from mk_brain.phrase import BLOCK_BARS, PhraseCounter, PhraseLength, PhraseState, pattern_label
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


MidiOut = NoteOn | NoteOff | ControlChange | ProgramChange | PitchBend
MODIFIERS = ("SELECT", "MUTE", "PATTERN")  # + pad : commande, pas de note
LIVE_GROUP = 0  # disposition rythmique, imposée en live
DESIGN_GROUP = 1  # chromatique, disposition de départ en design
MODE_KEYS = ("SHIFT", "CONTROL", "MASTER_PUSH")  # n'annulent pas une bascule proposée
MAX_OCTAVE = 4  # design : décalage d'octave borné à ±4 (flèches de transport)
MENU = ("GAMME", "TRACK", "QUANT", "PHRASE")  # design : boutons d'écran 1-4 (banque : GROUP)
PHRASES: tuple[PhraseLength, ...] = (32, 64)
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
        self.design_bank: int | None = None  # banque du design (GROUP, menu BANK), 0 = A
        self._design_phrase: PhraseLength | None = None  # menu PHRASE ; None = celle de la banque
        self.menu: int | None = None  # entrée de menu ouverte (index dans MENU)
        self.menu_choice = 0  # valeur en cours de choix à l'encodeur maître
        self.clock = clock or ClockTracker()
        self.channel = cfg.midi.auto_channel - 1
        self.modes = ModeSwitch(cfg.play.mode)
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
        pages = [[(e.name, e.param) for e in page] for page in enc.pages]
        self.faders = Faders(pages, enc.mute_cc, enc.raw_per_step)
        self.track = 1  # track des encodeurs (SELECT + pad)
        self.last_program: int | None = None  # dernier PC reçu
        self.bank: int | None = None  # banque de PATTERN + pad : PC reçu ou PATTERN + GROUP
        self.last_control = ""  # dernier geste de contrôle, pour l'écran
        self._consumed: set[int] = set()  # pads frappés avec un modificateur
        self.last_touch: tuple[int, int] | None = None  # (encodeur 1-8, instant) pour l'écran
        self.last_hit: tuple[int, int, int, int] | None = None  # (pad, note, vélocité, instant)
        self._requested: str | None = None  # pattern demandé par PATTERN + pad, pas encore confirmé
        self._bent: tuple[int, int] | None = None  # (track, canal) du pitch bend en cours
        self.octave = 0  # décalage d'octave du design (flèches de transport), remis à 0 par GROUP
        # annonce d'une nouvelle banque en live : (clé, fiche, instant) ; instant posé au tick
        self.announce: tuple[str, Bank, int | None] | None = None
        if self.design:  # démarrage en design (`play.mode`)
            self._enter_design()

    @property
    def design(self) -> bool:
        return self.modes.mode == "design"

    @property
    def sheet(self) -> tuple[str, Bank] | None:
        """Fiche de la banque du design (clé, banque), None hors design ou sans projet."""
        if not self.design or self.project is None or self.design_bank is None:
            return None
        return self.project.bank(self.design_bank)

    @property
    def live_sheet(self) -> tuple[str, Bank] | None:
        """Fiche de la banque du dernier PC reçu (live), None sans PC ou hors projet."""
        if self.project is None or self.last_program is None:
            return None
        return self.project.bank(self.last_program // 16)

    @property
    def context(self) -> tuple[str, Bank] | None:
        """Banque qui règle le jeu : choisie en design, suivie par PC en live."""
        return self.sheet if self.design else self.live_sheet

    @property
    def layout(self) -> Layout:
        if not self.design:
            return self.cfg.layouts[LIVE_GROUP]
        lay = self.cfg.layouts[self.group]
        sheet = self.sheet
        if sheet is not None:
            bank = sheet[1]
            lay = for_bank(lay, self.cfg.scale(bank.mode), bank.tonic)
        return shift_octave(lay, self.octave)

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
    def next_pattern(self) -> str | None:
        """Prochain pattern : annoncé par la DT2 (PC reçu), sinon demandé par PATTERN + pad."""
        nxt = self.phrase.next_pattern or self._requested
        return None if nxt == self.phrase.pattern else nxt

    @property
    def _modifiers(self) -> set[str]:
        """SELECT, MUTE, PATTERN ; PATTERN sans effet en design (décidé le 2026-11-09)."""
        return set(MODIFIERS) - ({"PATTERN"} if self.design else set())

    @property
    def repeating(self) -> bool:
        """Un pad au moins répète (note repeat en cours)."""
        return bool(self._repeats)

    @property
    def repeat_active(self) -> bool:
        return self.repeat_held or self.repeat_locked

    # --- entrées ------------------------------------------------------------

    def handle(self, ev: Event, now: int) -> list[Timed]:
        if isinstance(ev, ButtonEvent):
            self._button(ev, now)
            if ev.name == "SHIFT" and not ev.pressed:
                return self._release_bend(now)
            return []
        if isinstance(ev, EncoderEvent):
            if ev.index == 0:
                if self.selector is not None:
                    self.selector.scroll(ev.delta)
                elif "SWING" in self._held_buttons:
                    self.swing = clamp_swing(self.swing + ev.delta)
                elif self.menu is not None:
                    n = len(self._menu_items(self.menu)[0])
                    self.menu_choice = max(0, min(n - 1, self.menu_choice + ev.delta))
                return []
            return self._encoder(ev.index, ev.delta, now)
        return self._pad(pad_label(ev.index), ev, now)

    def _reachable(self, track: int) -> bool:
        if track == self.cfg.midi.auto_channel:
            self.last_control = f"T{track:02d} = AUTO CHANNEL: no own channel"
            return False
        return True

    def _encoder(self, index: int, delta: int, now: int) -> list[Timed]:
        """Live : canal de la track sélectionnée. Design : AUTO CHANNEL, donc la track
        active de la DT2 (p-locks en LIVE REC) ; valeurs tenues sous la track sélectionnée."""
        if not self.design and not self._reachable(self.track):
            return []
        if self.faders.page[index - 1][1] == PITCH_BEND and "SHIFT" not in self._held_buttons:
            self.last_control = "PB: hold SHIFT"  # pitch bend tenu par SHIFT seulement
            return []
        self.last_touch = (index, now)
        sent = self.faders.turn(self.track, index, delta)
        if sent is None:
            return []
        param, value = sent
        name = self.faders.page[index - 1][0]
        self.last_control = f"T{self.track:02d} {name} {value}"
        if self.design and not self._rec_hint:
            self._rec_hint = True
            self.last_control += "  DT2 in LIVE REC?"
        channel = self.channel if self.design else self.track - 1
        if param == PITCH_BEND:  # 0-127 → -8192..8191, 64 = centre
            self._bent = (self.track, channel)
            return [(now, PitchBend(channel, max(-8192, min(8191, (value - 64) * 128))))]
        return [(now, ControlChange(channel, param, value))]

    def _command(self, pad: int, now: int) -> list[Timed]:
        held = self._held_buttons
        if "SELECT" in held:
            if self.design or self._reachable(pad):
                self.track = pad
                self.last_control = f"T{pad:02d} selected"
            return []
        if "MUTE" in held:
            if not self._reachable(pad):
                return []
            cc, value = self.faders.toggle_mute(pad)
            self.last_control = f"T{pad:02d} {'muted' if value else 'unmuted'}"
            return [(now, ControlChange(pad - 1, cc, value))]
        if self.bank is None:
            self.last_control = "bank? (PATTERN + GROUP)"
            return []
        program = self.bank * 16 + pad - 1
        self._requested = pattern_label(program)
        self.last_control = f"-> {self._requested}"
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
        suivante (arrêté : compteur inchangé).

        En live, la banque du projet suit le PC (slice 6.B) : sa phrase s'applique avec la
        remise (arrêté : tout de suite), son titre s'annonce si la banque change. En design,
        un PC d'une autre banque la choisit comme GROUP (demandé le 2026-11-09) ; un autre
        pattern de la même banque laisse le choix fait à la main.
        """
        if program != self.last_program:
            self.faders.pattern_changed()
        if program // 16 != self.bank:
            self.log.append(f"banque {pattern_label(program)[0]} (PC reçu)")
        new_bank = self.last_program is None or program // 16 != self.last_program // 16
        self.last_program = program
        self.bank = program // 16
        self._requested = None  # la DT2 a répondu
        length: int | None = None
        if self.design:
            found = None if self.project is None else self.project.bank(program // 16)
            fresh = (
                new_bank and program // 16 != self.design_bank
            )  # déjà choisie : surcharge gardée
            if fresh and found is not None and self.project is not None:
                self._set_design_bank(program // 16)
                length = self.project.phrase(found[1])
                self.last_control = f"{found[0]} (DT2)"
        else:
            sheet = self.live_sheet
            length = self._live_phrase()
            if new_bank and sheet is not None:
                self.announce = (*sheet, None)
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
        """Ouvre la liste des projets ; refusée en live transport lancé."""
        if not self.design and self.running:
            self._note("transport running: no project change")
            return
        if self.catalog is None:
            self._note("no project list")
            return
        self.selector = self.catalog()
        self.menu = None
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
        """Change de projet : banque du design à rechoisir, contexte live repris du dernier PC."""
        self.project = project
        self.design_bank, self._design_phrase, self.octave = None, None, 0
        self.announce = None
        if self.design:
            self._enter_design()
        else:
            self._apply_phrase()
        self.leds_dirty = True

    # --- session : derniers réglages -------------------------------------------

    def snapshot(self) -> Session:
        values = self.faders.values()
        return Session(
            design_bank=self.design_bank,
            group=self.group,
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
        )

    def restore(self, session: Session) -> None:
        """Reprend une session sauvée ; ce que la DT2 a déjà dit (PC reçu) l'emporte."""
        banks = [i for i, _, _ in self._banks()]
        if session.design_bank in banks:
            self.design_bank = session.design_bank
        if session.group < len(self.cfg.layouts):
            self.group = session.group
        if abs(session.octave) <= MAX_OCTAVE:
            self.octave = session.octave
            if not fits(self.layout):
                self.octave = 0
        if self.last_program is None and session.program is not None:
            self.last_program = session.program
            self.phrase.pattern = pattern_label(session.program)
        if self.bank is None:
            self.bank = session.bank
        self.track = session.track
        if session.page < self.faders.n_pages:
            self.faders.page_index = session.page
        values = {(f.track, f.param): f.value for f in session.faders}
        self.faders.restore(values, set(session.muted))
        self._apply_phrase()
        self.leds_dirty = True

    # --- design : banque et menu ----------------------------------------------

    def _banks(self) -> list[tuple[int, str, Bank]]:
        """Banques du projet : (lettre 0-7, clé, fiche)."""
        if self.project is None:
            return []
        found = ((i, self.project.bank(i)) for i in range(len(GROUPS)))
        return [(i, b[0], b[1]) for i, b in found if b is not None]

    def _enter_design(self) -> None:
        """Premier passage : la banque de la DT2 si le projet l'a, sinon la première."""
        self._rec_hint = False
        banks = [i for i, _, _ in self._banks()]
        if self.design_bank is None and banks:
            self._set_design_bank(self.bank if self.bank in banks else banks[0])
        self._apply_phrase()

    def _set_design_bank(self, index: int) -> None:
        """Banque du design (GROUP, PC d'une autre banque, premier passage) : octave à 0,
        phrase de la banque, disposition calée sur son mode (PAD MODE la surcharge ensuite,
        jusqu'au prochain changement de banque ; demandé le 2026-11-09)."""
        self.design_bank, self._design_phrase, self.octave = index, None, 0
        found = None if self.project is None else self.project.bank(index)
        if found is not None:
            self.group = self.cfg.layouts.index(self.cfg.scale(found[1].mode))
        self.leds_dirty = True

    def _live_phrase(self) -> PhraseLength:
        """Phrase du live : celle de la banque du dernier PC, sinon la config."""
        sheet = self.live_sheet
        if sheet is None or self.project is None:
            return self.cfg.play.phrase
        return self.project.phrase(sheet[1])

    def _apply_phrase(self) -> None:
        """Longueur de phrase : celle de la banque (ou du menu) en design, du dernier PC en live."""
        if not self.design:
            self.phrase.length = self._live_phrase()
            return
        length: PhraseLength = self.cfg.play.phrase
        sheet = self.sheet
        if self._design_phrase is not None:
            length = self._design_phrase
        elif sheet is not None and self.project is not None:
            length = self.project.phrase(sheet[1])
        self.phrase.length = length

    def _choose_bank(self, index: int) -> None:
        if self.project is None:
            self.last_control = "no project"
            return
        found = self.project.bank(index)
        if found is None:
            self.last_control = f"no bank {GROUPS[index]}"
            return
        self._set_design_bank(index)
        self._apply_phrase()
        key, bank = found
        self.last_control = f"{key}  {FLAT_NAMES[bank.tonic]} {self.cfg.scale(bank.mode).name}"

    def _shift_octave(self, step: int) -> None:
        """Flèches de transport en design : ±1 octave, ±3 au plus, notes dans 0-127."""
        if self.layout.kind == "rythmique":
            self.last_control = "octave: not in Drums"
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
            self._design_phrase = PHRASES[i]
            self._apply_phrase()

        return [f"{n} bars" for n in PHRASES], PHRASES.index(self.phrase.length), phrase

    def menu_view(self) -> list[tuple[str, str, bool]]:
        """Pour l'écran : (entrée, valeur affichée, ouverte) ; ouverte = choix en cours."""
        view = []
        for entry, name in enumerate(MENU):
            labels, cur, _ = self._menu_items(entry)
            opened = entry == self.menu
            i = self.menu_choice if opened else cur
            view.append((name, labels[i] if labels else "-", opened))
        return view

    def _open_menu(self, entry: int) -> None:
        if entry >= len(MENU) or entry == self.menu:
            self.menu = None  # même bouton (ou bouton sans entrée) : fermer sans appliquer
            return
        labels, cur, _ = self._menu_items(entry)
        if labels:
            self.menu, self.menu_choice = entry, cur

    def _validate_menu(self) -> None:
        assert self.menu is not None
        entry, self.menu = self.menu, None
        labels, _, apply = self._menu_items(entry)
        apply(self.menu_choice)
        self.last_control = labels[self.menu_choice]

    def _release_bend(self, now: int) -> list[Timed]:
        """SHIFT relâché : pitch bend remis au centre sur le canal où il est parti."""
        if self._bent is None:
            return []
        track, channel = self._bent
        self._bent = None
        self.faders.received(track, PITCH_BEND, 64)
        self.leds_dirty = True
        return [(now, PitchBend(channel, 0))]

    def _switch_mode(self, name: str, now: int) -> bool:
        """Bascule de mode : SHIFT + CONTROL tenus, appui maître = confirmer. True si consommé."""
        if name == "MASTER_PUSH" and self.modes.pending is not None:
            msg = self.modes.confirm(self.running)
            if msg and msg.startswith("mode"):
                self.menu = None
                if self.design:
                    self._enter_design()
                else:
                    self._apply_phrase()
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
            if name in MODIFIERS or name.startswith("BROWSE_"):
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
        if name in ("TRANSPORT_LEFT", "TRANSPORT_RIGHT"):  # octave du design
            if self.design:
                self._shift_octave(-1 if name == "TRANSPORT_LEFT" else 1)
            return
        if "PATTERN" in self._held_buttons and name.startswith("GROUP_") and not self.design:
            self.bank = GROUPS.index(name[-1])
            self.last_control = f"bank {name[-1]}"
            self.leds_dirty = True
            return
        if name.startswith("GROUP_"):
            if not self.design:  # live : pads toujours en rythmique
                return
            self._choose_bank(GROUPS.index(name[-1]))
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
        elif name.startswith("DISPLAY_") and self.design:
            self._open_menu(int(name[-1]) - 1)
        elif name == "MASTER_PUSH" and self.menu is not None:
            self._validate_menu()
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
        if ev.pressed and pad not in self._pressure and self._held_buttons & self._modifiers:
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
        if self.selector is not None and not self.design and self.running:
            self.selector = None  # Start en live : la sélection se ferme sur le projet en cours
            self._note("transport running: selection closed")
        if self.announce is not None and self.announce[2] is None:
            self.announce = (self.announce[0], self.announce[1], now)
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
        self.last_hit = (pad, note, vel, now)
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
            elif pad in lit:
                pads[index] = full
            elif pad == self.track and not self.design:  # live : track des encodeurs repérée
                pads[index] = scale(full, self.cfg.leds.selected)
            else:  # repos ; hors gamme de la chromatique éteint
                pads[index] = scale(full, dim if in_scale(layout, pad) else 0)
        st = self.phrase_state
        if "PATTERN" in held and not self.design:  # PATTERN tenu : les GROUP montrent la banque
            white = self.cfg.families["chromatique"]
            groups = [scale(white, 1.0 if g == self.bank else dim) for g in range(len(GROUPS))]
        elif self.design:  # banques du projet en couleur de leur mode, la choisie en blanc plein
            groups = [(0, 0, 0)] * len(GROUPS)
            for g, _, bank in self._banks():
                family = self.cfg.scale(bank.mode).family
                groups[g] = scale(self.cfg.families[family], dim)
            if self.design_bank is not None and self.project is not None:
                groups[self.design_bank] = self.cfg.leds.bank
        elif st is None:  # live arrêté : GROUP sans rôle, éteints
            groups = [(0, 0, 0)] * len(GROUPS)
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
            buttons[name] = (LED_MAX if name in held else low) if name in self._modifiers else 0
        for name in ("BROWSE_LEFT", "BROWSE_RIGHT"):  # cyclent : toujours disponibles
            buttons[name] = LED_MAX if name in held else low
        if self.design and layout.kind != "rythmique":  # pleine du côté où l'on est décalé
            buttons["TRANSPORT_LEFT"] = LED_MAX if self.octave < 0 else low
            buttons["TRANSPORT_RIGHT"] = LED_MAX if self.octave > 0 else low
        if self.repeat_active:
            for i, (name, _) in enumerate(DIVISIONS):
                buttons[f"DISPLAY_{i + 1}"] = LED_MAX if name == self.division else low
        elif self.design:
            for i in range(len(MENU)):
                buttons[f"DISPLAY_{i + 1}"] = LED_MAX if i == self.menu else low
        self.leds_dirty = False
        return LedState(pads=pads, groups=groups, buttons=buttons)

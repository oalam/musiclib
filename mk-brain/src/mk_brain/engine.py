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
  arrêté = la banque courante seule ; perform : SHIFT + pad tenu ne joue pas,
  les encodeurs règlent la track du pad (`perform_track`), la valeur reste au
  relâché ; SOLO verrouille le perform (`perform_lock`) : les pads ne jouent
  plus, un tap ajoute ou retire la track du pad au groupe des encodeurs ;
  écrans du clavier = ceux du MPC.
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
MODIFIERS = ("SELECT", "MUTE")  # + pad : commande, pas de note
KEYBOARD_GROUP = 0  # chromatique, disposition du clavier sans banque
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
        self._held_buttons: set[str] = set()
        self._attacks: dict[int, _Attack] = {}  # pad 1-16 → attaque en cours de mesure
        self._sounding: dict[int, tuple[int, int, int]] = {}  # pad → (canal, note, instant du on)
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
        self.bank: int | None = None  # banque courante, 0 = A : PC reçu ou GROUP seul
        self.last_control = ""  # dernier geste de contrôle, pour l'écran
        self._consumed: set[int] = set()  # pads frappés avec un modificateur
        self.last_touch: tuple[int, int] | None = None  # (encodeur 1-8, instant) pour l'écran
        self.last_hit: tuple[int, int, int, int] | None = None  # (pad, note, vélocité, instant)
        self.last_hit_mpc = False  # dernière frappe jouée en MPC (écran : label et cible)
        self._perform: dict[int, int] = {}  # perform (SHIFT + pad tenu) : pad → track visée
        self.perform_lock = False  # SOLO : perform verrouillé, les pads ne jouent plus
        self._latched: dict[int, int] = {}  # perform verrouillé : pads allumés → track visée
        self._released_at: dict[int, int] = {}  # SOLO : dernier relâché de chaque pad (rebonds)
        self._bent: tuple[int, int] | None = None  # (track, canal) du pitch bend en cours
        self.octave = 0  # décalage d'octave du clavier (flèches de transport), remis à 0 par GROUP
        # annonce d'une nouvelle banque reçue par PC : (clé, fiche, instant) ; instant posé au tick
        self.announce: tuple[str, Bank, int | None] | None = None

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
        """Tracks des encodeurs en perform, distinctes : pads tenus puis pads allumés (SOLO)."""
        return list(dict.fromkeys([*self._perform.values(), *self._latched.values()]))

    @property
    def perform_track(self) -> int | None:
        """Première track du perform (pad tenu, sinon pad allumé), None hors perform."""
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
        tenus, la valeur d'avant gardée pour le relâché."""
        if self._perform or self._latched:
            return self._perform_turn(index, delta, now)
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
        channel = self.track - 1
        if param == PITCH_BEND:
            self._bent = (self.track, channel)
        return [(now, self._param_out(channel, param, value))]

    # --- perform : SHIFT + pad tenu --------------------------------------------

    def _perform_target(self, pad: int) -> int:
        """Track visée par un pad en perform : celle de l'entrée `mpc`, ou pad n = track n
        en clavier."""
        return self.cfg.mpc_pad(pad).track if self.mpc else pad

    def _perform_press(self, pad: int) -> None:
        track = self._perform_target(pad)
        if not self._reachable(track):
            self._consumed.add(pad)  # pad 16 en clavier : ni note ni perform
            return
        self._perform[pad] = track
        self.last_control = f"PERF T{track:02d}"
        self.leds_dirty = True

    def _latch(self, pad: int) -> None:
        """Perform verrouillé : un tap ajoute la track du pad au groupe, un second la retire."""
        self._consumed.add(pad)  # pas de note jusqu'au relâché
        self.leds_dirty = True
        if self._latched.pop(pad, None) is not None:
            self.last_control = f"PERF -T{self._perform_target(pad):02d}"
            return
        track = self._perform_target(pad)
        if self._reachable(track):
            self._latched[pad] = track
            self.last_control = f"PERF +T{track:02d}"

    def _toggle_lock(self) -> None:
        """SOLO : perform verrouillé ou pads rejoués ; la sortie vide le groupe."""
        self.perform_lock = not self.perform_lock
        if not self.perform_lock:
            self._latched.clear()
        self.last_control = "PERF lock" if self.perform_lock else "PERF off"

    def _perform_turn(self, index: int, delta: int, now: int) -> list[Timed]:
        """Encodeur en perform : même pas sur chaque track tenue."""
        self.last_touch = (index, now)
        steps = self.faders.steps(index, delta)
        if steps == 0:
            return []
        param = self.faders.page[index - 1][1]
        name = self.faders.page[index - 1][0]
        out: list[Timed] = []
        for track in self.perform_tracks:
            value = self.faders.nudge(track, param, steps)
            if value is None:
                continue
            self.last_control = f"PERF T{track:02d} {name} {value}"
            out.append((now, self._param_out(track - 1, param, value)))
        return out

    def _perform_release(self, pad: int) -> list[Timed]:
        """Pad relâché : les valeurs réglées restent ; les encodeurs reviennent à la track
        sélectionnée (ou au pad encore tenu). Rien n'est envoyé."""
        self._perform.pop(pad, None)
        self.leds_dirty = True
        return []

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

    def _release_bend(self, now: int) -> list[Timed]:
        """SHIFT relâché : pitch bend remis au centre sur le canal où il est parti."""
        if self._bent is None:
            return []
        track, channel = self._bent
        self._bent = None
        self.faders.received(track, PITCH_BEND, 64)
        self.leds_dirty = True
        return [(now, PitchBend(channel, 0))]

    def _note(self, msg: str | None) -> None:
        if msg:
            self.last_control = msg
            self.log.append(msg)
            self.leds_dirty = True

    def _button(self, ev: ButtonEvent, now: int) -> None:
        name = ev.name
        if not ev.pressed:
            self._held_buttons.discard(name)
            if name in MODIFIERS or name.startswith("BROWSE_"):
                self.leds_dirty = True
            if name == "NOTE_REPEAT":
                self.repeat_held = False
                if not self.repeat_locked:
                    self._repeats.clear()
                self.leds_dirty = True
            return
        self._held_buttons.add(name)
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
        if name in ("TRANSPORT_LEFT", "TRANSPORT_RIGHT"):  # octave du clavier
            self._shift_octave(-1 if name == "TRANSPORT_LEFT" else 1)
            return
        if name.startswith("GROUP_"):
            self._choose_bank(GROUPS.index(name[-1]))
        elif name == "SOLO":
            self._toggle_lock()
        elif name == "PAD_MODE":  # MPC <-> clavier ; les notes tenues gardent leur cible
            self.mpc = not self.mpc
            self.last_control = "MPC" if self.mpc else f"keyboard {self.layout.name}"
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
        elif name.startswith("DISPLAY_"):
            self._focus_menu(int(name[-1]) - 1)
        elif name == "MASTER_PUSH":  # focus à l'entrée suivante, en boucle
            self._focus_menu((self.menu + 1) % len(MENU))
        elif name in MODIFIERS:
            pass
        else:
            return
        self.leds_dirty = True

    def _pad(self, pad: int, ev: PadEvent, now: int) -> list[Timed]:
        if pad in self._perform:  # perform : pas de note jusqu'au relâché
            return [] if ev.pressed else self._perform_release(pad)
        if pad in self._consumed:  # frappé avec un modificateur : pas de note jusqu'au relâché
            if not ev.pressed:
                self._consumed.discard(pad)
                self._released_at[pad] = now
            return []
        if ev.pressed and pad not in self._pressure and self._held_buttons & set(MODIFIERS):
            self._consumed.add(pad)
            self.leds_dirty = True
            return self._command(pad, now)
        if ev.pressed and pad not in self._pressure and self.perform_lock:
            self._consumed.add(pad)
            released = self._released_at.get(pad)
            debounce = int(self.cfg.play.tap_debounce_ms * 1e6)
            if released is None or now - released >= debounce:  # sinon : rebond du relâché
                self._latch(pad)
            return []
        if ev.pressed and pad not in self._pressure and "SHIFT" in self._held_buttons:
            self._perform_press(pad)
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
        if pad in self._sounding:
            channel, note, on_at = self._sounding.pop(pad)
            out.append((max(now, on_at + NOTE_OFF_MIN_NS), NoteOff(channel, note)))
            self.leds_dirty = True
        return out

    # --- temps ----------------------------------------------------------------

    def tick(self, now: int) -> list[Timed]:
        """Attaques dont la fenêtre de vélocité est écoulée, coups de repeat à venir."""
        if self.selector is not None and self.running:
            self.selector = None  # Start : la sélection se ferme sur le projet en cours
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
                out.append((max(t, now), NoteOn(rep.channel, rep.note, vel)))
                out.append((max(gate, now + NOTE_OFF_MIN_NS), NoteOff(rep.channel, rep.note)))
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
        lit = set(self._attacks) | set(self._sounding) | set(self._repeats)
        lit |= set(self._perform) | set(self._latched)  # pads du perform : pleins
        held = self._held_buttons
        pads: list[RGB] = [(0, 0, 0)] * N_PADS
        for index in range(N_PADS):
            pad = pad_label(index)
            track = self.cfg.track_colors[pad]  # modificateur tenu : pad n = track n
            auto = pad == self.cfg.midi.auto_channel
            if "MUTE" in held:  # tracks ouvertes pleines, mutées éteintes ; la 16 sans mute
                pads[index] = (0, 0, 0) if auto or self.faders.muted.get(pad) else track
            elif "SELECT" in held:
                pads[index] = track if pad == self.track else scale(track, dim)
            elif self.perform_lock:  # SOLO : remplace les couleurs du MPC et du clavier
                on = pad in self._latched or pad in self._perform
                pads[index] = self.cfg.leds.perform_on if on else self.cfg.leds.perform_idle
            else:
                full, rest = self._pad_full(pad)
                pads[index] = full if pad in lit else scale(full, dim if rest else 0)
        st = self.phrase_state
        if st is not None:  # un bouton de plus toutes les 8 mesures ; clignote avant un cap
            color = self.cfg.leds.phrase
            groups = [color if g < st.blocks_lit else (0, 0, 0) for g in range(len(GROUPS))]
            if st.blinking and not st.half_beat_on:
                groups[st.blocks_lit - 1] = (0, 0, 0)
        else:  # arrêté : la banque courante seule allumée (slice 9)
            groups = [(0, 0, 0)] * len(GROUPS)
            if self.bank is not None:
                groups[self.bank] = self.cfg.leds.bank
        low = round(LED_MAX * dim)
        buttons = {
            "GRID": LED_MAX if self.quantize != "off" else 0,
            "NOTE_REPEAT": LED_MAX if self.repeat_active else 0,
            "SWING": LED_MAX if self.swing > 50 else 0,
            "PLAY": LED_MAX if st is not None and st.pulse else 0,
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
        if self.repeat_active:
            for i, (name, _) in enumerate(DIVISIONS):
                buttons[f"DISPLAY_{i + 1}"] = LED_MAX if name == self.division else low
        else:
            for i in range(len(MENU)):
                buttons[f"DISPLAY_{i + 1}"] = LED_MAX if i == self.menu else low
        self.leds_dirty = False
        return LedState(pads=pads, groups=groups, buttons=buttons)

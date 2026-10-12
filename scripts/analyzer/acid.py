"""Generateur de lignes acid (Phase 9.A), inspire de Sting (if-tah).

Une sequence = 16 pas en quatre couches tirees ensemble par `generate` :
- **notes** : degre de la gamme (marche aleatoire, `type` 1 = pas conjoints
  et tonique frequente, 16 = grands sauts) ;
- **velocity** : accent a 3 niveaux (0 aucun, 1 moyen, 2 fort), contraste
  regle par `accent` (0-100) ;
- **gate** : pas joue ou silence (`density` pas joues sur 16, le pas 0
  toujours joue) et longueur a 3 niveaux (court, normal, long), echelle `gate`
  (1-200 %) ; en `tie_mode` un pas long suivi d'un pas joue est lie (slide) ;
- **octave** : decalage de `octave_low` a `octave_high` (0 favori).

Chaque couche a son propre tirage (graine + nom de couche) : verrouiller une
couche et relancer les autres ne change que celles-ci. Lecture : `steps` pas
a partir de `offset`, sens `direction` ; `swing` decale les pas impairs.

Exemple :
    python -m analyzer.acid --root F# --scale PHRYGIAN --type 11 --density 14 --seed 3 -o /tmp/acid.mid
"""
from __future__ import annotations

import argparse
import random
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from analyzer.harmony import NOTE_NAMES, SCALES

Layer = Literal["notes", "velocity", "gate", "octave"]
Direction = Literal["forward", "backward", "pendulum"]
Mode = Literal["algo", "arp"]
ArpPattern = Literal["up", "down", "updown", "random"]

LAYERS: tuple[Layer, ...] = ("notes", "velocity", "gate", "octave")
SEQ_LEN = 32
BLOCK = 16  # une mesure de doubles-croches : Density se compte par bloc

# progressions d'accords en degres de la gamme (0 = tonique), mode arp (9.C2)
PROGRESSIONS: dict[str, tuple[int, ...]] = {
    "I-VI-VII-I": (0, 5, 6, 0),
    "I-IV-V-I": (0, 3, 4, 0),
    "I-VII-VI-VII": (0, 6, 5, 6),
    "I-III-VII-IV": (0, 2, 6, 3),
    "I-V": (0, 4),
    "I-IV": (0, 3),
    "I (pédale)": (0,),
}
_ARP_UPDOWN = (0, 1, 2, 1)
PPQ = 480
TICKS_PER_STEP = PPQ // 4  # double-croche

_ACCENT_WEIGHTS = (0.6, 0.25, 0.15)   # aucun / moyen / fort
_GATE_WEIGHTS = (0.25, 0.5, 0.25)     # court / normal / long
_GATE_STEPS = (0.25, 0.5, 1.0)        # longueur en pas a gate = 100 %
_BASE_VELOCITY = 80
_MAX_ACCENT_GAIN = 47                 # 80 + 47 = 127 : accent fort a 100
_OCTAVE_HOME = 0.6                    # probabilite de l'octave 0 si permise


class AcidError(Exception):
    """Parametres ou etat incoherents pour le generateur acid."""


class AcidParams(BaseModel):
    type: int = Field(8, ge=1, le=16)
    density: int = Field(12, ge=1, le=16)
    accent: int = Field(50, ge=0, le=100)
    gate: int = Field(100, ge=1, le=200)         # % des longueurs
    root: int = Field(0, ge=0, le=11)            # 0 = C
    scale: str = "AEOLIAN (MINOR)"
    transpose: int = Field(0, ge=-24, le=24)
    octave_low: int = Field(-1, ge=-1, le=2)
    octave_high: int = Field(1, ge=-1, le=2)
    base_note: int = Field(36, ge=0, le=96)      # note MIDI de la tonique a l'octave 0
    steps: int = Field(16, ge=1, le=SEQ_LEN)
    offset: int = Field(0, ge=0, le=SEQ_LEN - 1)
    direction: Direction = "forward"
    swing: int = Field(50, ge=50, le=75)         # % ; 50 = droit, 66 = ternaire
    tie_mode: bool = True
    mode: Mode = "algo"                          # arp : notes = accords de `progression`
    progression: list[int] = Field(default_factory=lambda: [0, 5, 6, 0], min_length=1, max_length=8)
    chord_steps: Literal[8, 16] = 16             # pas par accord (demi-mesure / mesure)
    arp: ArpPattern = "up"

    @field_validator("scale")
    @classmethod
    def _known_scale(cls, v: str) -> str:
        if v not in SCALES:
            raise ValueError(f"gamme inconnue : {v}")
        return v

    @model_validator(mode="after")
    def _octave_range(self) -> AcidParams:
        if self.octave_low > self.octave_high:
            raise ValueError("octave_low > octave_high")
        return self


class AcidStep(BaseModel):
    on: bool = True
    degree: int = 0                      # degre de la gamme (0 = tonique, peut sortir de l'octave)
    accent: int = Field(0, ge=0, le=2)
    gate: int = Field(1, ge=0, le=2)     # 0 court, 1 normal, 2 long
    octave: int = Field(0, ge=-1, le=2)


class AcidSequence(BaseModel):
    seed: int
    params: AcidParams
    steps: list[AcidStep] = Field(min_length=SEQ_LEN, max_length=SEQ_LEN)

    @field_validator("steps", mode="before")
    @classmethod
    def _pad_16(cls, v: Any) -> Any:
        """Sequence de 16 pas (avant le passage a 32) : la 2e moitie repete la 1re."""
        if isinstance(v, list) and len(v) == BLOCK:
            return v + v
        return v


class GenerateRequest(BaseModel):
    """Corps de `POST /api/acid/generate` ; sans graine, une graine est tiree."""
    params: AcidParams = AcidParams()
    seed: int | None = Field(None, ge=0)
    previous: AcidSequence | None = None
    locks: list[Layer] = []

    def resolved_seed(self) -> int:
        return self.seed if self.seed is not None else random.randrange(2**31)


class AcidNote(BaseModel):
    """Note jouee, en ticks (PPQ) depuis le debut du cycle."""
    start: int
    end: int
    note: int
    velocity: int
    slide: bool = False  # liee a la suivante (chevauchement)


class ScaleInfo(BaseModel):
    name: str          # nom KB SCALE de la DT2 (cle de `harmony.SCALES`)
    label: str
    intervals: list[int]


def scales() -> list[ScaleInfo]:
    """Gammes proposees au front (memes noms que la DT2)."""
    return [ScaleInfo(name=k, label=lab, intervals=list(iv)) for k, (lab, iv) in SCALES.items()]


class ProgressionInfo(BaseModel):
    name: str
    degrees: list[int]


def progressions() -> list[ProgressionInfo]:
    return [ProgressionInfo(name=k, degrees=list(v)) for k, v in PROGRESSIONS.items()]


def _rng(seed: int, layer: Layer) -> random.Random:
    return random.Random(f"{seed}:{layer}")


def _draw_notes(p: AcidParams, rng: random.Random) -> list[int]:
    n_degrees = len(SCALES[p.scale][1])
    max_leap = 1 + (p.type - 1) * 13 // 15            # 1 a 14 degres
    p_root = 0.35 * (16 - p.type) / 15                 # retour a la tonique
    lo, hi = -n_degrees, 2 * n_degrees - 1
    degrees = [0]
    for _ in range(SEQ_LEN - 1):
        if rng.random() < p_root:
            degrees.append(0)
            continue
        d = degrees[-1] + rng.randint(-max_leap, max_leap)
        degrees.append(max(lo, min(hi, d)))
    return degrees


def _draw_velocity(rng: random.Random) -> list[int]:
    return rng.choices((0, 1, 2), weights=_ACCENT_WEIGHTS, k=SEQ_LEN)


def _arp_notes(p: AcidParams, rng: random.Random) -> list[int]:
    """Degres d'un arpege sur la progression : triade de la gamme (degres d, d+2,
    d+4), un accord tous les `chord_steps` pas ; motif compte sur la position
    dans l'accord. Fondamentale de V, VI, VII prise sous la tonique (basse)."""
    n = len(SCALES[p.scale][1])
    out = []
    for i in range(SEQ_LEN):
        root = p.progression[(i // p.chord_steps) % len(p.progression)] % n
        if root >= 4:
            root -= n
        tones = (root, root + 2, root + 4)
        k = i % p.chord_steps
        if p.arp == "up":
            out.append(tones[k % 3])
        elif p.arp == "down":
            out.append(tones[2 - k % 3])
        elif p.arp == "updown":
            out.append(tones[_ARP_UPDOWN[k % 4]])
        else:
            out.append(rng.choice(tones))
    return out


def _draw_gate(p: AcidParams, rng: random.Random) -> list[tuple[bool, int]]:
    played: set[int] = set()
    for b in range(0, SEQ_LEN, BLOCK):  # `density` pas joues sur 16, premier pas de chaque mesure joue
        played |= {b} | {b + i for i in rng.sample(range(1, BLOCK), p.density - 1)}
    lengths = rng.choices((0, 1, 2), weights=_GATE_WEIGHTS, k=SEQ_LEN)
    return [(i in played, lengths[i]) for i in range(SEQ_LEN)]


def _draw_octave(p: AcidParams, rng: random.Random) -> list[int]:
    allowed = list(range(p.octave_low, p.octave_high + 1))
    others = [o for o in allowed if o != 0]
    out = []
    for _ in range(SEQ_LEN):
        if 0 in allowed and (not others or rng.random() < _OCTAVE_HOME):
            out.append(0)
        else:
            out.append(rng.choice(others or allowed))
    return out


def generate(params: AcidParams, seed: int, previous: AcidSequence | None = None,
             locks: frozenset[Layer] = frozenset()) -> AcidSequence:
    """Tire les couches non verrouillees ; les couches de `locks` viennent de `previous`.

    Les octaves verrouillees sont ramenees dans [octave_low, octave_high]."""
    if locks and previous is None:
        raise AcidError("verrou demande sans sequence precedente")
    prev = previous.steps if previous is not None else None

    def keep(layer: Layer) -> bool:
        return prev is not None and layer in locks

    degrees = ([s.degree for s in prev] if keep("notes") and prev
               else (_arp_notes if params.mode == "arp" else _draw_notes)(params, _rng(seed, "notes")))
    accents = ([s.accent for s in prev] if keep("velocity") and prev
               else _draw_velocity(_rng(seed, "velocity")))
    gates = ([(s.on, s.gate) for s in prev] if keep("gate") and prev
             else _draw_gate(params, _rng(seed, "gate")))
    octaves = ([max(params.octave_low, min(params.octave_high, s.octave)) for s in prev]
               if keep("octave") and prev else _draw_octave(params, _rng(seed, "octave")))
    steps = [AcidStep(on=gates[i][0], degree=degrees[i], accent=accents[i],
                      gate=gates[i][1], octave=octaves[i]) for i in range(SEQ_LEN)]
    return AcidSequence(seed=seed, params=params, steps=steps)


def play_order(params: AcidParams) -> list[int]:
    """Indices des pas joues sur un cycle (`steps` pas depuis `offset`, selon `direction`)."""
    window = [(params.offset + i) % SEQ_LEN for i in range(params.steps)]
    if params.direction == "backward":
        return window[::-1]
    if params.direction == "pendulum" and len(window) > 2:
        return window + window[-2:0:-1]
    return window


def step_note(params: AcidParams, step: AcidStep) -> int:
    """Note MIDI d'un pas : tonique + transposition + degre (gamme) + octave, bornee 0-127."""
    intervals = SCALES[params.scale][1]
    octs, idx = divmod(step.degree, len(intervals))
    note = (params.base_note + params.root + params.transpose
            + 12 * (octs + step.octave) + intervals[idx])
    return max(0, min(127, note))


def step_velocity(params: AcidParams, step: AcidStep) -> int:
    return min(127, _BASE_VELOCITY + round(step.accent * params.accent * _MAX_ACCENT_GAIN / 200))


def _swung(pos: int, swing: int) -> int:
    """Tick de debut de la position `pos` : les positions impaires sont retardees."""
    tick = pos * TICKS_PER_STEP
    if pos % 2:
        tick += round((2 * swing / 100 - 1) * TICKS_PER_STEP)
    return tick


def render_notes(seq: AcidSequence) -> list[AcidNote]:
    """Notes d'un cycle de lecture. En `tie_mode`, un pas long suivi d'un pas joue
    est lie : meme note = prolongee, note differente = coupee au debut de la
    suivante (le note_on passe avant le note_off, slide sur un synthe mono)."""
    p = seq.params
    order = play_order(p)
    cycle_end = len(order) * TICKS_PER_STEP
    notes: list[AcidNote] = []
    tied = False  # la note precedente est liee a celle-ci
    for pos, idx in enumerate(order):
        step = seq.steps[idx]
        if not step.on:
            tied = False
            continue
        start = _swung(pos, p.swing)
        end = start + max(1, round(_GATE_STEPS[step.gate] * p.gate / 100 * TICKS_PER_STEP))
        nxt = seq.steps[order[pos + 1]] if pos + 1 < len(order) else None
        tie_next = p.tie_mode and step.gate == 2 and nxt is not None and nxt.on
        if tie_next:
            end = _swung(pos + 1, p.swing)
        note = step_note(p, step)
        if tied and notes and notes[-1].note == note:
            notes[-1].end = end
            notes[-1].slide = tie_next
        else:
            notes.append(AcidNote(start=start, end=min(end, cycle_end), note=note,
                                  velocity=step_velocity(p, step), slide=tie_next))
        tied = tie_next
    for n, nxt_note in zip(notes, notes[1:] + [None]):
        n.end = min(n.end, cycle_end)
        if nxt_note is not None and nxt_note.note == n.note:  # gate > 100 % : pas de chevauchement sur soi
            n.end = min(n.end, nxt_note.start)
    return notes


def note_events(seq: AcidSequence, channel: int) -> list[tuple[int, int, Any]]:
    """(tick, priorite, message) d'un cycle, comme `digitakt.track_note_events` :
    note_off normal (0) avant note_on (1) ; note_off d'une note liee (2) apres."""
    import mido

    events: list[tuple[int, int, Any]] = []
    for n in render_notes(seq):
        events.append((n.start, 1, mido.Message("note_on", channel=channel,
                                                note=n.note, velocity=n.velocity)))
        events.append((n.end, 2 if n.slide else 0,
                       mido.Message("note_off", channel=channel, note=n.note, velocity=0)))
    return events


def write_midi(seq: AcidSequence, out_path: Path, bpm: float = 140, channel: int = 0) -> None:
    """Un cycle de lecture en .mid (une mesure a 16 pas)."""
    import mido

    mid = mido.MidiFile(ticks_per_beat=PPQ)
    trk = mido.MidiTrack()
    mid.tracks.append(trk)
    trk.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0))
    trk.append(mido.MetaMessage("track_name", name=f"acid {seq.seed}", time=0))
    events = note_events(seq, channel)
    events.append((len(play_order(seq.params)) * TICKS_PER_STEP, 3,
                   mido.MetaMessage("end_of_track")))
    events.sort(key=lambda e: (e[0], e[1]))
    prev = 0
    for tick, _prio, msg in events:
        msg.time = tick - prev
        prev = tick
        trk.append(msg)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    mid.save(str(out_path))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Tire une ligne acid et l'exporte en .mid")
    ap.add_argument("--root", default="C", choices=NOTE_NAMES)
    ap.add_argument("--scale", default="AEOLIAN (MINOR)", choices=sorted(SCALES))
    ap.add_argument("--type", type=int, default=8)
    ap.add_argument("--density", type=int, default=12)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--bpm", type=float, default=140)
    ap.add_argument("-o", "--out", type=Path, required=True)
    args = ap.parse_args(argv)
    params = AcidParams(root=NOTE_NAMES.index(args.root), scale=args.scale,
                        type=args.type, density=args.density)
    seq = generate(params, args.seed)
    write_midi(seq, args.out, bpm=args.bpm)
    print(f"{args.out} : {len(render_notes(seq))} notes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

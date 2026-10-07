"""Classement des samples DT2 en famille / code / fichier (Phase 7.J1).

Source : la copie des packs faite depuis Transfer (`<MEDIA>/Samples`, lecture
seule). Chaque wav recoit une famille (style, UNIVERSEL ou SAMPLE) et un code
de categorie a 2 lettres facon Elektron (`BD`, `SD`, `BR`...), puis un nom
court `<CODE> [BPM|note] <desc> <pack>` de 18 caracteres au plus : l'ecran de
choix du sample d'une track n'en montre qu'environ 14.

Selection : quota par case famille x code, candidats = 3 x quota repartis
entre sous-packs. Pre-filtre qualite (7.J2) : chaque candidat est mesure
(niveau, saturation, blanc en tete, longueur) ; les defauts sont signales par
des drapeaux et repoussent le candidat en fin de case, sans l'ecarter : la
decision reste a l'ecoute. Le manifeste garde les decisions d'ecoute (`keep` / `drop`)
d'un passage a l'autre ; les overrides (famille, code, nom) sont edites a la
main dans un fichier a part.
"""
from __future__ import annotations

import re
import struct
from collections import defaultdict
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Literal

import numpy as np
import soundfile as sf
from pydantic import BaseModel, Field

NAME_MAX = 18
FOLD_MIN = 4          # en dessous, la case rejoint le meme code dans UNIVERSEL
CANDIDATE_FACTOR = 3  # candidats par case = 3 x quota (pre-selection d'ecoute)
LONG_ONESHOT_S = 4.0  # un "kick" de plus de 4 s est une boucle
TEMPO_LOOP_S = 2.0    # tempo dans le nom + au moins 2 s : boucle (piano, synth...)

# Pre-filtre qualite (7.J2) : seuils des drapeaux, poids pour le reclassement.
MUTE_PEAK_DB = -40.0     # crete sous ce niveau : fichier quasi muet
LOW_PEAK_DB = -18.0      # crete sous ce niveau : sample faible (gain a remonter)
CLIP_LEVEL = 0.999       # echantillon pleine echelle
CLIP_RUN = 3             # au moins 3 echantillons consecutifs a pleine echelle...
CLIP_SHARE = 0.001       # ... sur plus de 0,1 % du fichier
LEAD_DB = -40.0          # relatif a la crete : en dessous, c'est du blanc
LEAD_MAX_S = 0.03        # blanc en tete d'un one-shot au-dela duquel le trig traine
LONG_HIT_S = 2.0         # frappe de drums plus longue (queue, reverb, boucle mal rangee)
FLAG_WEIGHT = {"illisible": 3, "muet": 3, "sature": 1, "blanc": 1, "faible": 1, "long": 1}

FAMILIES = ("AUTRES", "DUBSTEP", "HARDCORE", "JUNGLE", "SAMPLE", "TECHNO", "TRIBE", "UNIVERSEL")
CODES = ("BD", "SD", "CP", "HH", "OH", "CY", "TM", "PC",
         "BR", "DL", "PL", "ML", "BL", "BS", "ST", "PD", "FX", "VX", "RS")
DRUMS = frozenset({"BD", "SD", "CP", "HH", "OH", "CY", "TM", "PC"})
TONAL = frozenset({"BD", "BS", "ST", "PD", "ML", "BL"})   # note gardee dans le nom
# Boucles : BR break, DL drums, PL percussions / hats, ML melodie, BL basse
TEMPO = frozenset({"BR", "DL", "PL", "ML", "BL"})         # BPM garde dans le nom
NO_FOLD = frozenset({"UNIVERSEL", "SAMPLE"})

# Prefixe de chemin (minuscules, relatif a Samples/) -> famille. Le plus long
# gagne ; tout ce qui n'est pas liste va dans UNIVERSEL.
FAMILY_RULES: dict[str, str] = {
    "tribalism": "TRIBE",
    "hardcore free samples": "HARDCORE",
    "low entropy": "HARDCORE",
    "rthm/loops/hardcore": "HARDCORE",
    "rthm/loops/blutotnium": "HARDCORE",
    "vi ta lee /millennium": "HARDCORE",
    "vi ta lee /overdrive": "HARDCORE",
    "vi ta lee /darktechno": "TECHNO",
    "jungle 89": "JUNGLE",
    "jungle dnb rthm": "JUNGLE",
    "rthm/loops/jungle": "JUNGLE",
    "rthm/loops/breakbeat": "JUNGLE",
    "rthm/packs/nightmares": "JUNGLE",
    "rthm/packs/neurotek": "TRIBE",     # kit one-shots, choisi pour la tribe
    "rthm/loops/dubstep": "DUBSTEP",
    "rthm/packs/tortured": "DUBSTEP",
    "bass graves": "DUBSTEP",
    "samples megabit/95 bpm": "TECHNO",
    "samples megabit/deep tech": "TECHNO",
    "samples megabit/minimal": "TECHNO",
    "samples megabit/drumtronic": "TECHNO",
    "samples megabit/balkan": "AUTRES",
    "samples megabit/dirty dutch": "AUTRES",
    "samples megabit/dope house": "AUTRES",
    "samples megabit/edm": "AUTRES",
    "rthm/loops/histibe": "AUTRES",
    "native instrument/caribean": "AUTRES",
    "vocal/african": "AUTRES",
    "elektron pack/aotearoa": "AUTRES",
    "music radar/percussion": "AUTRES",
    "recorded": "SAMPLE",
    "minibrute resample": "SAMPLE",
    "transfers": "SAMPLE",
}

# Prefixe de chemin -> suffixe de pack (3 caracteres). Le plus long gagne ;
# a defaut, les 3 premieres lettres du dossier de premier niveau.
PACK_CODES: dict[str, str] = {
    "909": "909",
    "bass graves": "bgr",
    "bass": "bas",
    "cinematic noiiz": "noi",
    "drum wizadry": "dwz",
    "drumbrute kick": "dbr",
    "elektron pack": "elk",
    "glitch": "gli",
    "hardcore free samples": "hcf",
    "instru": "ins",
    "jungle 89": "j89",
    "jungle dnb rthm": "jdr",
    "korger1samples": "er1",
    "loops pack": "lpk",
    "low entropy": "lwe",
    "minibrute resample": "mbr",
    "minimoog synth": "mmg",
    "mpc_kit": "mpc",
    "music radar": "mrd",
    "native instrument": "ni",
    "recorded": "rec",
    "rise": "ris",
    "rthm": "rth",
    "rthm/packs/linndrum": "lin",
    "samples megabit": "meg",
    "sfx": "sfx",
    "taktile": "tak",
    "transfers": "trf",
    "tribalism": "trb",
    "vi ta lee ": "vtl",
    "vocal": "voc",
}

# Ordre = priorite : le premier code dont le motif matche le chemin gagne.
_B, _E = r"(?<![a-z])", r"(?![a-z])"   # bornes : _ et chiffres separent les mots
CODE_RULES: tuple[tuple[str, str], ...] = (
    ("BR", r"break|amen"),
    ("BD", rf"kick|{_B}bd|bassdrum|basedrum|bass ?drum|{_B}kik"),
    ("SD", rf"snare|{_B}sd{_E}|{_B}sd\d|{_B}snr|{_B}rim|{_B}rs\d"),
    ("CP", rf"clap|{_B}cp{_E}|{_B}cp\d|snap"),
    ("OH", rf"open ?h|{_B}oh{_E}|{_B}oh\d|ohh"),
    ("HH", rf"hi ?-?hat|hihat|hit hat|{_B}hh|{_B}ch\d|{_B}chh|closed|hat"),
    ("CY", rf"cymbal|crash|{_B}ride|{_B}cy{_E}|{_B}cy\d|splash"),
    ("TM", rf"{_B}tom|{_B}[lmh]t\d"),
    ("PC", rf"perc|conga|bongo|shaker|tamb|cowbell|clave|block|cabasa|{_B}pc{_E}|gourd|stick|tick"),
    ("BS", rf"bass|{_B}sub{_E}|reese|808"),
    ("VX", r"vox|vocal|voice|shout|chant|speech|acapella|adlib"),
    ("FX", rf"{_B}fx|sfx|rise|riser|downlift|uplift|impact|sweep|noise|glitch|cartoon|whoosh|reverse|drop"),
    ("PD", r"pad|drone|texture|ambien|atmos|cinematic"),
    ("ST", r"stab|chord|hit|riff|arp|lead|synth|key|piano|organ|instru|minimoog|brass|string|guitar|shot"),
    ("RS", r"recorded|resample|transfers"),
)
_CODE_RX = tuple((c, re.compile(p)) for c, p in CODE_RULES)

# Une boucle se reconnait au chemin ; son code depend ensuite de son contenu.
_LOOP_RX = re.compile(rf"loop|{_B}grooves?{_E}|sequence|{_B}tops?{_E}|{_B}fill|{_B}builds?{_E}")
LOOP_RULES: tuple[tuple[str, str], ...] = (
    ("VX", r"vox|vocal|voice|chant|adlib|acapella"),
    ("PD", r"pad|drone|atmos|ambien|texture"),            # une nappe n'est pas une boucle
    ("FX", rf"{_B}fx|sfx|rise|sweep|noise|glitch|{_B}builds?{_E}"),
    ("BL", rf"bass|{_B}sub{_E}|reese|808"),
    ("ML", rf"synth|lead|{_B}arp|chord|piano|{_B}keys?{_E}|guitar|riff|melod|stab|organ"
           rf"|string|brass|minimoog|sequence"),
    ("PL", rf"perc|conga|bongo|shaker|tamb|{_B}hats?{_E}|hihat|{_B}hh|{_B}tops?{_E}"
           rf"|cyclick|gourd|{_B}ride"),
)
_LOOP_CODE_RX = tuple((c, re.compile(p)) for c, p in LOOP_RULES)

# Mots retires de la description : categories (deja dans le code) et bruit
# recurrent des packs.
_NOISE = frozenset("""
kick kicks bd bassdrum basedrum basedrums drum drums snare snares sd clap claps cp hat hats
hihat hihats hh closed open oh cymbal cymbals crash ride tom toms perc percs percussion
break breaks loop loops bass sub fx sfx vox vocal vocals pad pads stab stabs one shot
shots oneshot sample samples wav bpm free or tip sp dt vtl ls the of and a vol pack
beat beats openhh closedhh hihat ohh chh xtrmraw
""".split())
_NOTE_RX = re.compile(r"^([A-G][#b]?)(m|min|maj)?$")
_BPM_RX = re.compile(r"(\d{2,3}) ?bpm")
# tempo dans le nom sans "bpm" : 170_HeavyBoiBeat, CPCT_120_C_Gamelan, vb6_drm120
_TEMPO_NAME_RX = re.compile(r"(?:^|_|drm)(\d{2,3})_")
_ONESHOT_DIR_RX = re.compile(r"one ?-?shots?")
_SPLIT_RX = re.compile(r"[\s_\-.()\[\],+&']+")
_CAMEL_RX = re.compile(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])")

Status = Literal["pending", "keep", "drop"]
LOOPS = frozenset({"BR", "DL", "PL", "ML", "BL"})


class SampleError(Exception):
    """Source de samples ou manifeste inexploitable."""


class SampleEntry(BaseModel):
    """Un candidat : fichier source, case, nom DT2 et decision d'ecoute."""
    source: str                     # relatif a Samples/
    family: str
    code: str
    pack: str
    name: str                       # sans extension, <= NAME_MAX
    duration: float | None
    rank: int                       # ordre dans la case (1 = premier propose)
    status: Status = "pending"
    selected: bool = False          # retenu pour l'export (7.J3)
    flags: list[str] | None = None  # defauts du pre-filtre (None = pas mesure)

    @property
    def dest(self) -> str:
        return f"{self.family}/{self.code}/{self.name}.wav"


class Override(BaseModel):
    """Correction manuelle d'un fichier (overrides.json, cle = source)."""
    family: str | None = None
    code: str | None = None
    name: str | None = None
    exclude: bool = False


class Manifest(BaseModel):
    source_root: str
    total: int
    entries: list[SampleEntry] = Field(default_factory=list)
    unclassified: list[str] = Field(default_factory=list)
    folded: list[str] = Field(default_factory=list)   # cases "FAM/CODE" repliees


class _Raw(BaseModel):
    source: str
    family: str
    code: str | None
    pack: str
    duration: float | None


# --- Lecture --------------------------------------------------------------

def wav_duration(path: Path) -> float | None:
    """Duree via l'en-tete RIFF (chunks fmt + data), sans decoder l'audio."""
    try:
        with path.open("rb") as f:
            if f.read(4) != b"RIFF":
                return None
            f.read(4)
            if f.read(4) != b"WAVE":
                return None
            byte_rate = 0
            while True:
                hdr = f.read(8)
                if len(hdr) < 8:
                    return None
                cid, size = hdr[:4], struct.unpack("<I", hdr[4:])[0]
                if cid == b"fmt ":
                    fmt = f.read(size + size % 2)
                    byte_rate = struct.unpack("<I", fmt[8:12])[0]
                elif cid == b"data":
                    return round(size / byte_rate, 3) if byte_rate else None
                else:
                    f.seek(size + size % 2, 1)
    except (OSError, struct.error):
        return None


def measure(path: Path, code: str) -> list[str]:
    """Drapeaux qualite d'un fichier : illisible, muet, faible, sature, blanc
    (en tete d'un one-shot), long (frappe de drums de plus de LONG_HIT_S)."""
    try:
        y, sr = sf.read(str(path), dtype="float32", always_2d=True)
    except (sf.LibsndfileError, RuntimeError, ValueError):
        return ["illisible"]
    a = np.abs(y).max(axis=1) if y.size else np.zeros(0, dtype=np.float32)
    peak = float(a.max()) if a.size else 0.0
    if peak <= 10 ** (MUTE_PEAK_DB / 20):
        return ["muet"]
    flags: list[str] = []
    if peak < 10 ** (LOW_PEAK_DB / 20):
        flags.append("faible")
    if clipped_share(a) > CLIP_SHARE:
        flags.append("sature")
    if code not in LOOPS:
        first = int(np.argmax(a >= peak * 10 ** (LEAD_DB / 20)))
        if first / sr > LEAD_MAX_S:
            flags.append("blanc")
    if code in DRUMS and a.size / sr > LONG_HIT_S:
        flags.append("long")
    return flags


def clipped_share(a: np.ndarray) -> float:
    """Part des echantillons pris dans une suite d'au moins CLIP_RUN valeurs
    a pleine echelle (un pic isole a 0 dBFS n'est pas une saturation)."""
    hot = np.concatenate(([0], (a >= CLIP_LEVEL).astype(np.int8), [0]))
    edges = np.flatnonzero(np.diff(hot))
    runs = edges[1::2] - edges[::2]
    return float(runs[runs >= CLIP_RUN].sum()) / max(a.size, 1)


def penalty(flags: list[str] | None) -> int:
    return sum(FLAG_WEIGHT.get(f, 1) for f in flags or [])


def iter_wavs(root: Path) -> Iterable[Path]:
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() == ".wav" and not p.name.startswith("._"):
            yield p


# --- Classement -------------------------------------------------------------

def _longest_prefix(rel_low: str, table: dict[str, str]) -> str | None:
    best = max((k for k in table if rel_low.startswith(k)), key=len, default=None)
    return table[best] if best is not None else None


def family_of(rel: str) -> str:
    return _longest_prefix(rel.lower(), FAMILY_RULES) or "UNIVERSEL"


def pack_of(rel: str) -> str:
    code = _longest_prefix(rel.lower(), PACK_CODES)
    if code:
        return code
    top = re.sub(r"[^a-z0-9]", "", rel.split("/")[0].lower())
    return top[:3] or "pk"


def loop_code(low: str) -> str:
    """Code d'une boucle selon son contenu ; drums par defaut."""
    return next((c for c, rx in _LOOP_CODE_RX if rx.search(low)), "DL")


def code_of(rel: str, duration: float | None) -> str | None:
    low = rel.lower()
    code = next((c for c, rx in _CODE_RX if rx.search(low)), None)
    if code == "BR":
        return code
    # boucle : mot-cle du chemin ou BPM dans le nom du fichier (pas du dossier)
    loop = bool(_LOOP_RX.search(low) or _BPM_RX.search(low.rsplit("/", 1)[-1]))
    # replis : BPM dans le dossier (Cyclick/110bpm/), one-shot drum trop long
    loop = loop or (code is None and bool(_BPM_RX.search(low)))
    loop = loop or (code in DRUMS and (duration or 0) > LONG_ONESHOT_S)
    # tempo en tete ou au milieu du nom (sans "bpm"), assez long, hors dossier one-shot
    loop = loop or ((duration or 0) >= TEMPO_LOOP_S and tempo_in_name(low)
                    and not _ONESHOT_DIR_RX.search(low))
    return loop_code(low) if loop else code


def tempo_in_name(low: str) -> bool:
    m = _TEMPO_NAME_RX.search(low.rsplit("/", 1)[-1])
    return m is not None and 60 <= int(m.group(1)) <= 229


def _is_mono_twin(rel: str, all_low: set[str]) -> bool:
    """Version mono d'un fichier qui existe aussi en stereo (on garde la stereo)."""
    low = rel.lower()
    return "mono" in low and low.replace("mono", "stereo") in all_low


def quota(family: str, code: str) -> int | None:
    """Nombre de samples retenus par case ; None = tout (SAMPLE)."""
    if family == "SAMPLE":
        return None
    if code in {"BD", "BR", "DL"} and family in {"HARDCORE", "JUNGLE", "TRIBE"}:
        return 32
    if family == "UNIVERSEL" and code == "BD":
        return 32
    if code == "PL" and family in {"JUNGLE", "TRIBE"}:
        return 32
    return 16 if code in DRUMS | LOOPS else 8


# --- Nommage ----------------------------------------------------------------

def _tokens(text: str) -> list[str]:
    """Mots du nom : separateurs, CamelCase et frontieres lettres/chiffres."""
    return [t for chunk in _SPLIT_RX.split(text) for t in _CAMEL_RX.split(chunk) if t]


def short_name(rel: str, code: str, pack: str) -> str:
    """`<CODE> [BPM|note] <desc> <num> <pack>`, NAME_MAX caracteres au plus."""
    parts = rel.split("/")
    stem = Path(parts[-1]).stem
    folder_words = {t.lower() for d in parts[:-1] for t in _tokens(d)}
    toks = _tokens(stem)

    head: list[str] = []
    if code in TEMPO:
        m = _BPM_RX.search(rel.lower())
        lead = _TEMPO_NAME_RX.search(stem.lower())
        bpm = m.group(1) if m else (lead.group(1) if lead else None)
        if bpm and 60 <= int(bpm) <= 220:
            head.append(bpm)
    note = None
    if code in TONAL:
        note = next((t for t in toks if _NOTE_RX.match(t)), None)
        if note:
            head.append(_NOTE_RX.match(note).group(1))  # type: ignore[union-attr]

    # numero de variante : 1-2 chiffres ; 406, 516... sont des references de label
    nums = [t for t in toks if t.isdigit() and (len(t) <= 2 or t.startswith("0"))
            and t not in head]
    num = f"{int(nums[-1]):02d}" if nums else ""
    # abreviations de pack en capitales (LS-CVP, PXXL) ignorees si le nom a
    # aussi des minuscules ; les lettres isolees ne disent rien
    has_lower = any(c.islower() for c in stem)
    words = [
        t.capitalize() for t in toks
        if t.isalpha() and t != note and len(t) > 1
        and not (has_lower and t.isupper() and len(t) <= 5)
        and t.lower() not in _NOISE and t.lower() not in folder_words
    ]
    if not words:   # rien de distinctif dans le nom : le dossier le plus proche
        fallback = [t for t in _tokens(parts[-2]) if t.isalpha()] if len(parts) > 1 else []
        words = [fallback[0].capitalize()[:6]] if fallback else ["Smp"]

    fixed = " ".join([code, *head])
    budget = NAME_MAX - len(fixed) - len(pack) - 2           # deux espaces
    desc_budget = budget - (len(num) + 1 if num else 0)
    if num and desc_budget < 2:       # BPM + note + numero : plus de place
        body = num[-budget:]
    else:
        desc = " ".join(words)[:max(desc_budget, 1)].rstrip()
        body = f"{desc} {num}" if num else desc
    return f"{fixed} {body} {pack}"


def _unique(name: str, taken: set[str]) -> str:
    """Suffixe de desambiguisation en tronquant la description si besoin."""
    if name not in taken:
        return name
    code_part, _, pack = name.rpartition(" ")
    for k in range(2, 1000):
        tag = f"{k}"
        base = code_part[: NAME_MAX - len(pack) - len(tag) - 2].rstrip()
        cand = f"{base} {tag} {pack}"
        if cand not in taken:
            return cand
    raise SampleError(f"impossible de rendre unique : {name}")


# --- Pipeline ---------------------------------------------------------------

def classify(root: Path, overrides: dict[str, Override]) -> tuple[list[_Raw], list[str]]:
    """Famille, code, pack et duree de chaque wav ; retourne aussi les non classes."""
    paths = list(iter_wavs(root))
    rels = [p.relative_to(root).as_posix() for p in paths]
    all_low = {r.lower() for r in rels}
    found: list[tuple[str, float | None, str | None, Override, tuple[str, int]]] = []
    for p, rel in zip(paths, rels):
        ov = overrides.get(rel, Override())
        if ov.exclude or _is_mono_twin(rel, all_low):
            continue
        dur = wav_duration(p)
        found.append((rel, dur, ov.code or code_of(rel, dur), ov,
                      (p.name.lower(), p.stat().st_size)))
    # doublon exact entre packs (meme nom, meme taille) : une seule copie, la
    # classee de preference, puis la plus profonde (plus de contexte de dossier :
    # jungle dnb rthm/ est une copie de rthm/loops/jungle dnb/)
    keeper: dict[tuple[str, int], str] = {}
    for rel, _, code, _, key in sorted(found, key=lambda f: (f[2] is None, -f[0].count("/"), f[0])):
        keeper.setdefault(key, rel)
    raws: list[_Raw] = []
    unclassified: list[str] = []
    for rel, dur, code, ov, key in found:
        if keeper[key] != rel:
            continue
        if code is None:
            unclassified.append(rel)
            continue
        raws.append(_Raw(source=rel, family=ov.family or family_of(rel),
                         code=code, pack=pack_of(rel), duration=dur))
    return raws, unclassified


def fold_small_cells(raws: list[_Raw], overrides: dict[str, Override]) -> list[str]:
    """Replie dans UNIVERSEL les cases de moins de FOLD_MIN fichiers."""
    counts: dict[tuple[str, str | None], int] = defaultdict(int)
    for r in raws:
        counts[r.family, r.code] += 1
    folded = sorted(f"{f}/{c}" for (f, c), n in counts.items()
                    if n < FOLD_MIN and f not in NO_FOLD)
    for r in raws:
        forced = overrides.get(r.source, Override()).family is not None
        if f"{r.family}/{r.code}" in folded and not forced:
            r.family = "UNIVERSEL"
    return folded


def _round_robin(raws: list[_Raw]) -> list[_Raw]:
    """Alterne les sous-dossiers pour que la pre-selection couvre tous les packs."""
    groups: dict[str, list[_Raw]] = defaultdict(list)
    for r in sorted(raws, key=lambda r: r.source.lower()):
        groups[r.source.rsplit("/", 1)[0]].append(r)
    queues = [groups[k] for k in sorted(groups)]
    out: list[_Raw] = []
    while any(queues):
        for q in queues:
            if q:
                out.append(q.pop(0))
    return out


Measure = Callable[[Path, str], list[str]]


def _pinned(source: str, prev_status: dict[str, Status], overrides: dict[str, Override]) -> bool:
    ov = overrides.get(source)
    moved = ov is not None and (ov.family is not None or ov.code is not None)
    return moved or prev_status.get(source, "pending") != "pending"



def build_manifest(root: Path, overrides: dict[str, Override],
                   previous: Manifest | None = None,
                   measure_fn: Measure | None = measure) -> Manifest:
    """Manifeste rejouable. Les drapeaux deja mesures sont repris du manifeste
    precedent ; `measure_fn=None` saute la mesure (rang = tour de role)."""
    raws, unclassified = classify(root, overrides)
    folded = fold_small_cells(raws, overrides)
    prev = {e.source: e for e in previous.entries} if previous else {}
    prev_status = {k: e.status for k, e in prev.items()}

    cells: dict[tuple[str, str], list[_Raw]] = defaultdict(list)
    for r in raws:
        assert r.code is not None
        cells[r.family, r.code].append(r)

    entries: list[SampleEntry] = []
    for (fam, code), items in sorted(cells.items()):
        q = quota(fam, code)
        ordered = _round_robin(items)
        # les decisions d'ecoute restent candidates meme hors du plafond
        cap = len(ordered) if q is None else q * CANDIDATE_FACTOR
        # les decisions d'ecoute et les deplacements manuels (override de case)
        # restent candidats meme hors du plafond
        kept = ordered[:cap] + [r for r in ordered[cap:] if _pinned(r.source, prev_status, overrides)]
        flags: dict[str, list[str] | None] = {}
        for r in kept:
            old = prev.get(r.source)
            if old is not None and old.flags is not None and old.code == code:
                flags[r.source] = old.flags
            elif measure_fn is not None:
                flags[r.source] = measure_fn(root / r.source, code)
            else:
                flags[r.source] = None
        # tri stable : les defauts passent en fin de case, le tour de role reste
        kept.sort(key=lambda r: penalty(flags[r.source]))
        taken: set[str] = set()
        cell_entries: list[SampleEntry] = []
        for rank, r in enumerate(kept, 1):
            ov = overrides.get(r.source, Override())
            name = _unique(ov.name or short_name(r.source, code, r.pack), taken)
            taken.add(name)
            cell_entries.append(SampleEntry(
                source=r.source, family=fam, code=code, pack=r.pack, name=name,
                duration=r.duration, rank=rank,
                status=prev_status.get(r.source, "pending"), flags=flags[r.source]))
        select(cell_entries, q)
        entries.extend(cell_entries)

    return Manifest(source_root=str(root), total=len(raws) + len(unclassified),
                    entries=entries, unclassified=unclassified, folded=folded)


def select(cell: list[SampleEntry], q: int | None) -> None:
    """keep d'abord, puis pending par rang, jamais drop ; les keep depassent le quota."""
    keeps = [e for e in cell if e.status == "keep"]
    pend = sorted((e for e in cell if e.status == "pending"), key=lambda e: e.rank)
    room = len(pend) if q is None else max(q - len(keeps), 0)
    chosen = {id(e) for e in keeps + pend[:room]}
    for e in cell:
        e.selected = id(e) in chosen


def cell_of(manifest: Manifest, family: str, code: str) -> list[SampleEntry]:
    return sorted((e for e in manifest.entries if e.family == family and e.code == code),
                  key=lambda e: e.rank)


def set_status(manifest: Manifest, source: str, status: Status) -> list[SampleEntry]:
    """Decision d'ecoute d'un candidat, puis nouvelle selection de sa case
    (un drop fait monter le pending suivant). Renvoie la case."""
    entry = next((e for e in manifest.entries if e.source == source), None)
    if entry is None:
        raise SampleError(f"candidat inconnu : {source}")
    entry.status = status
    cell = cell_of(manifest, entry.family, entry.code)
    select(cell, quota(entry.family, entry.code))
    return cell


def move(manifest: Manifest, source: str, family: str, code: str, root: Path,
         measure_fn: Measure | None = measure) -> tuple[list[SampleEntry], Override]:
    """Deplace un candidat vers une autre case (correction a l'ecoute).

    Statut garde ; le candidat se range en fin de la nouvelle case, renomme
    avec le nouveau code et remesure (blanc / long dependent du code). Les deux
    cases sont reselectionnees. Renvoie l'ancienne case et l'override a
    enregistrer pour que le deplacement survive a une reconstruction."""
    if family not in FAMILIES:
        raise SampleError(f"famille inconnue : {family}")
    if code not in CODES:
        raise SampleError(f"code inconnu : {code}")
    entry = next((e for e in manifest.entries if e.source == source), None)
    if entry is None:
        raise SampleError(f"candidat inconnu : {source}")
    old = (entry.family, entry.code)
    if old == (family, code):
        return cell_of(manifest, family, code), Override(family=family, code=code)
    target = cell_of(manifest, family, code)
    entry.family, entry.code = family, code
    entry.rank = max((e.rank for e in target), default=0) + 1
    entry.name = _unique(short_name(source, code, entry.pack), {e.name for e in target})
    path = root / source
    if measure_fn is not None and path.is_file():
        entry.flags = measure_fn(path, code)
    select(cell_of(manifest, family, code), quota(family, code))
    old_cell = cell_of(manifest, *old)
    select(old_cell, quota(*old))
    return old_cell, Override(family=family, code=code)


def grid(manifest: Manifest) -> dict[str, dict[str, tuple[int, int]]]:
    """famille -> code -> (candidats, retenus)."""
    out: dict[str, dict[str, tuple[int, int]]] = defaultdict(dict)
    for e in manifest.entries:
        n, s = out[e.family].get(e.code, (0, 0))
        out[e.family][e.code] = (n + 1, s + int(e.selected))
    return out

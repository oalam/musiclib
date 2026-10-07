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

Bibliotheque (7.J4) : les overrides portent aussi les tags libres, les etoiles
(1 a 5 : un sample note passe devant les non-notes de sa case) et la corbeille
(son rejete partout, distinct de `drop` qui ne vaut que pour la case). Les
operations du front (`move`, `set_stars`, `set_tags`, `trash`, `restore`)
modifient le manifeste et les overrides en memoire ; l'appelant les ecrit.

Kits (7.J5) : un kit est un prefixe de chemin, le dossier de premier niveau
(pack) puis son sous-dossier (`Native instrument/caribean`, `rthm/packs/neurotek` :
un dossier `packs` regroupe des kits, on descend d'un cran). Le manifeste liste
aussi la reserve (`reserve` : fichiers classes au-dela du plafond de 3 x quota,
non mesures) pour voir tout un kit ; garder, ecarter, noter ou ranger un
fichier de la reserve le fait entrer comme candidat (`promote`). Un kit (ou un
pack) mis a la corbeille est une regle : override `"<prefixe>/": {"trash": true}`,
tous ses fichiers sont exclus, et il se restaure d'un bloc. Les tags d'un kit
(`"<prefixe>/": {"tags": [...]}`) sont herites par tous ses fichiers, reserve
et fichiers a venir compris.

Export (7.J3) : les retenus (`selected`) sont copies tels quels sous
`<dest>/<FAMILLE>/<CODE>/<nom>.wav`, arborescence que Transfer envoie sur le
+Drive de la DT2. Rejouable : un index (`export.json`) liste les fichiers
ecrits par l'export ; un relancement ne recopie que ce qui a change et ne
retire que des fichiers de l'index, jamais un fichier pose a la main.
"""
from __future__ import annotations

import json
import os
import re
import shutil
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
TEMPO_RANGE = (60, 229)
MIN_LOOP_S = 1.0      # plus court : one-shot, si le chemin donne un code
BAR_COUNTS = (1, 2, 4, 8, 16)   # longueurs de boucle plausibles, en mesures 4/4
BAR_TOL = 0.04                  # ecart toléré entre tempo librosa et tempo des mesures

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
_TEMPO_NAME_RX = re.compile(r"(?:^|[_ ]|drm)(\d{2,3})(?=[_ ])")
_ONESHOT_DIR_RX = re.compile(r"one ?-?shots?")
# pack de frappes (MILLENNIUM KICKS 3) : une frappe longue y reste une frappe
_KICKS_DIR_RX = re.compile(r"kicks\b")
_SPLIT_RX = re.compile(r"[\s_\-.()\[\],+&']+")
_CAMEL_RX = re.compile(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])")

TAG_MAX = 24
STARS_MAX = 5

KIT_CONTAINERS = frozenset({"packs"})   # dossier qui regroupe des kits (rthm/packs)

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
    bpm: int | None = None          # boucle sans tempo dans le nom : tempo de l'audio
    bpm_est: bool = False           # bpm librosa seul (pas confirme par la duree)
    tags: list[str] = Field(default_factory=list)   # copie des overrides (7.J4)
    stars: int | None = None
    overflow: bool = False          # reserve hors plafond, vue par kit (7.J5), jamais stocke

    @property
    def dest(self) -> str:
        return f"{self.family}/{self.code}/{self.name}.wav"


class Override(BaseModel):
    """Correction manuelle d'un fichier (overrides.json, cle = source)."""
    family: str | None = None
    code: str | None = None
    name: str | None = None
    exclude: bool = False
    tags: list[str] = Field(default_factory=list)
    stars: int | None = Field(default=None, ge=1, le=STARS_MAX)
    trash: bool = False     # corbeille : hors de toutes les cases, restaurable


class LooseSample(BaseModel):
    """Fichier hors des cases : non classe ou en corbeille."""
    source: str
    pack: str
    tags: list[str] = Field(default_factory=list)
    stars: int | None = None


class ReserveSample(BaseModel):
    """Fichier classe au-dela du plafond de candidats (7.J5) : visible par kit,
    pas mesure ; il devient candidat des qu'on le garde, l'ecarte, le note ou
    le range."""
    source: str
    family: str
    code: str
    pack: str
    duration: float | None
    tags: list[str] = Field(default_factory=list)


class KitInfo(BaseModel):
    """Bilan d'un kit (prefixe de chemin) pour les pads du front (7.J5)."""
    kit: str
    pack: str                       # dossier de premier niveau
    label: str                      # dernier element du prefixe
    candidates: int = 0
    selected: int = 0
    keep: int = 0
    reserve: int = 0
    unclassified: int = 0
    trashed: int = 0                # fichiers du kit a la corbeille (un par un)
    trashed_kit: bool = False       # kit entier a la corbeille (regle)

    @property
    def files(self) -> int:
        return self.candidates + self.reserve + self.unclassified + self.trashed


class Manifest(BaseModel):
    source_root: str
    total: int
    entries: list[SampleEntry] = Field(default_factory=list)
    reserve: list[ReserveSample] = Field(default_factory=list)   # hors plafond (7.J5)
    unclassified: list[str] = Field(default_factory=list)
    folded: list[str] = Field(default_factory=list)   # cases "FAM/CODE" repliees
    trashed: list[str] = Field(default_factory=list)  # corbeille (overrides trash)
    trashed_kits: dict[str, int] = Field(default_factory=dict)  # prefixe -> fichiers


class ExportItem(BaseModel):
    """Fichier ecrit par l'export (index, cle = chemin relatif a dest)."""
    source: str
    size: int
    mtime_ns: int


class ExportReport(BaseModel):
    dest: str
    dry_run: bool
    files: int = 0                  # retenus exportes (plan)
    bytes: int = 0
    copied: list[str] = Field(default_factory=list)
    unchanged: int = 0
    removed: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)    # source absente du disque
    conflicts: list[str] = Field(default_factory=list)  # fichier pose a la main a cet endroit


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


def kit_of(rel: str) -> str:
    """Prefixe du kit d'un fichier : pack, puis son sous-dossier (on traverse
    un dossier `packs`). Un fichier pose a la racine du pack : le pack."""
    parts = rel.split("/")[:-1]
    if not parts:
        return ""
    out = [parts[0]]
    for p in parts[1:]:
        out.append(p)
        if p.lower() not in KIT_CONTAINERS:
            break
    return "/".join(out)


def in_kit(source: str, kit: str) -> bool:
    """`kit` : prefixe de kit ou de pack."""
    return source.startswith(kit + "/")


def tags_of(overrides: dict[str, Override], source: str) -> list[str]:
    """Tags effectifs : ceux du fichier et ceux des kits (prefixes) qui le
    contiennent."""
    tags = set(overrides.get(source, Override()).tags)
    for k, ov in overrides.items():
        if k.endswith("/") and ov.tags and source.startswith(k):
            tags.update(ov.tags)
    return sorted(tags)


def kit_rules(overrides: dict[str, Override]) -> list[str]:
    """Kits (ou packs) a la corbeille : overrides de cle `<prefixe>/`."""
    return sorted(k[:-1] for k, ov in overrides.items() if k.endswith("/") and ov.trash)


def code_of(rel: str, duration: float | None) -> str | None:
    low = rel.lower()
    code = next((c for c, rx in _CODE_RX if rx.search(low)), None)
    if code == "BR":
        # BreakApartKick de 0,4 s : une frappe, on prend le code suivant du nom
        other = next((c for c, rx in _CODE_RX if c != "BR" and rx.search(low)), None)
        short = duration is not None and duration < MIN_LOOP_S
        return other if short and other is not None else code
    # boucle : mot-cle du chemin ou BPM dans le nom du fichier (pas du dossier)
    loop = bool(_LOOP_RX.search(low) or _BPM_RX.search(low.rsplit("/", 1)[-1]))
    # replis : BPM dans le dossier (Cyclick/110bpm/), one-shot drum trop long
    loop = loop or (code is None and bool(_BPM_RX.search(low)))
    # replis hors dossier one-shot ou de kicks (un crash de 4 s y reste un
    # crash) : drum trop long, tempo en tete ou au milieu du nom (sans "bpm")
    # et assez long
    folder = low.rsplit("/", 1)[0] if "/" in low else ""
    if not (_ONESHOT_DIR_RX.search(low) or _KICKS_DIR_RX.search(folder)):
        loop = loop or (code in DRUMS and (duration or 0) > LONG_ONESHOT_S)
        loop = loop or ((duration or 0) >= TEMPO_LOOP_S
                        and tempo_from_name(low.rsplit("/", 1)[-1]) is not None)
    # moins d'une seconde : un one-shot, meme dans un dossier de boucles ou de fills
    if loop and code is not None and duration is not None and duration < MIN_LOOP_S:
        return code
    return loop_code(low) if loop else code


def _in_range(n: int) -> bool:
    return TEMPO_RANGE[0] <= n <= TEMPO_RANGE[1]


def tempo_from_name(stem_low: str) -> int | None:
    """Premier nombre plausible du nom isole par `_` ou espace (02_..._175_ -> 175)."""
    return next((int(m.group(1)) for m in _TEMPO_NAME_RX.finditer(stem_low)
                 if _in_range(int(m.group(1)))), None)


def tempo_of(rel: str) -> int | None:
    """Tempo ecrit dans le chemin : `NNN bpm` n'importe ou, sinon dans le nom."""
    m = _BPM_RX.search(rel.lower())
    if m and _in_range(int(m.group(1))):
        return int(m.group(1))
    return tempo_from_name(Path(rel).stem.lower())


def snap_to_bars(tempo: float, duration: float) -> int | None:
    """Tempo d'une boucle de 1 a 16 mesures 4/4 coherent avec l'estimation
    (a x2 ou /2 pres, BAR_TOL) : 240 x mesures / duree."""
    if duration <= 0 or tempo <= 0:
        return None
    hits: list[tuple[bool, bool, int]] = []   # (hors 80-200, pas x1, tempo)
    for n in BAR_COUNTS:
        cand = 240 * n / duration
        if not _in_range(round(cand)):
            continue
        for k, t in enumerate((tempo, tempo * 2, tempo / 2)):
            if abs(cand - t) / t <= BAR_TOL:
                hits.append((not 80 <= cand <= 200, k > 0, round(cand)))
    # 70 ou 140 pour la meme boucle : la zone 80-200 d'abord, puis l'estimation telle quelle
    return min(hits)[2] if hits else None


def estimate_bpm(path: Path, duration: float | None) -> tuple[int | None, bool]:
    """Tempo d'une boucle sans tempo ecrit : librosa, cale sur un nombre entier
    de mesures si la duree le confirme (exact), sinon librosa seul (estime)."""
    import librosa   # lourd : seulement quand une boucle doit etre mesuree

    try:
        y, sr = librosa.load(str(path), sr=22050, mono=True, duration=30.0)
    except Exception:  # noqa: BLE001 - fichier illisible : pas de tempo
        return None, False
    if y.size < sr // 2:
        return None, False
    tempo = float(np.atleast_1d(librosa.feature.tempo(y=y, sr=sr))[0])
    snapped = snap_to_bars(tempo, duration or y.size / sr)
    if snapped is not None:
        return snapped, False
    while tempo and tempo < 80:
        tempo *= 2
    return (round(tempo), True) if tempo and _in_range(round(tempo)) else (None, False)


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


def short_name(rel: str, code: str, pack: str, bpm: int | None = None) -> str:
    """`<CODE> [BPM|note] <desc> <num> <pack>`, NAME_MAX caracteres au plus.
    `bpm` : tempo mesure, utilise si le chemin n'en donne pas."""
    parts = rel.split("/")
    stem = Path(parts[-1]).stem
    folder_words = {t.lower() for d in parts[:-1] for t in _tokens(d)}
    toks = _tokens(stem)

    head: list[str] = []
    if code in TEMPO:
        tempo = tempo_of(rel) or bpm
        if tempo:
            head.append(str(tempo))
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

def classify(root: Path, overrides: dict[str, Override]
             ) -> tuple[list[_Raw], list[str], list[str], dict[str, int]]:
    """Famille, code, pack et duree de chaque wav ; retourne aussi les non
    classes, la corbeille et les kits a la corbeille (fichiers par prefixe)."""
    rules = kit_rules(overrides)
    trashed_kits: dict[str, int] = {k: 0 for k in rules}
    paths = list(iter_wavs(root))
    rels = [p.relative_to(root).as_posix() for p in paths]
    all_low = {r.lower() for r in rels}
    found: list[tuple[str, float | None, str | None, Override, tuple[str, int]]] = []
    trashed: list[str] = []
    for p, rel in zip(paths, rels):
        ov = overrides.get(rel, Override())
        if ov.exclude or _is_mono_twin(rel, all_low):
            continue
        rule = next((k for k in rules if in_kit(rel, k)), None)
        if rule is not None:
            trashed_kits[rule] += 1
            continue
        if ov.trash:
            trashed.append(rel)
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
    return raws, unclassified, sorted(trashed), trashed_kits


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
BpmFn = Callable[[Path, float | None], tuple[int | None, bool]]


def _pinned(source: str, prev_status: dict[str, Status], overrides: dict[str, Override]) -> bool:
    ov = overrides.get(source)
    touched = ov is not None and (ov.family is not None or ov.code is not None
                                  or ov.stars is not None)
    return touched or prev_status.get(source, "pending") != "pending"


def star_key(stars: int | None) -> int:
    """Cle de tri : les notes passent devant les non-notes, 5 etoiles d'abord."""
    return -(stars or 0)



def build_manifest(root: Path, overrides: dict[str, Override],
                   previous: Manifest | None = None,
                   measure_fn: Measure | None = measure,
                   bpm_fn: BpmFn | None = estimate_bpm) -> Manifest:
    """Manifeste rejouable. Les drapeaux deja mesures sont repris du manifeste
    precedent ; `measure_fn=None` saute la mesure (rang = tour de role)."""
    raws, unclassified, trashed, trashed_kits = classify(root, overrides)
    folded = fold_small_cells(raws, overrides)
    prev = {e.source: e for e in previous.entries} if previous else {}
    prev_status = {k: e.status for k, e in prev.items()}

    cells: dict[tuple[str, str], list[_Raw]] = defaultdict(list)
    for r in raws:
        assert r.code is not None
        cells[r.family, r.code].append(r)

    entries: list[SampleEntry] = []
    reserve: list[ReserveSample] = []
    for (fam, code), items in sorted(cells.items()):
        q = quota(fam, code)
        ordered = _round_robin(items)
        # les decisions d'ecoute restent candidates meme hors du plafond
        cap = len(ordered) if q is None else q * CANDIDATE_FACTOR
        # les decisions d'ecoute et les deplacements manuels (override de case)
        # restent candidats meme hors du plafond
        kept = ordered[:cap] + [r for r in ordered[cap:] if _pinned(r.source, prev_status, overrides)]
        held = {r.source for r in kept}
        reserve.extend(ReserveSample(source=r.source, family=fam, code=code, pack=r.pack,
                                     duration=r.duration,
                                     tags=tags_of(overrides, r.source))
                       for r in ordered[cap:] if r.source not in held)
        flags: dict[str, list[str] | None] = {}
        for r in kept:
            old = prev.get(r.source)
            if old is not None and old.flags is not None and old.code == code:
                flags[r.source] = old.flags
            elif measure_fn is not None:
                flags[r.source] = measure_fn(root / r.source, code)
            else:
                flags[r.source] = None
        # tempo des boucles qui ne l'ecrivent pas (repris du manifeste precedent)
        tempos: dict[str, tuple[int | None, bool]] = {}
        if code in TEMPO:
            for r in kept:
                old = prev.get(r.source)
                if tempo_of(r.source) is not None:
                    continue
                if old is not None and old.bpm is not None:
                    tempos[r.source] = (old.bpm, old.bpm_est)
                elif bpm_fn is not None:
                    tempos[r.source] = bpm_fn(root / r.source, r.duration)
        # tri stable : les notes en tete, les defauts en fin de case, le tour
        # de role reste
        stars = {r.source: overrides.get(r.source, Override()).stars for r in kept}
        kept.sort(key=lambda r: (star_key(stars[r.source]), penalty(flags[r.source])))
        taken: set[str] = set()
        cell_entries: list[SampleEntry] = []
        for rank, r in enumerate(kept, 1):
            ov = overrides.get(r.source, Override())
            bpm, est = tempos.get(r.source, (None, False))
            name = _unique(ov.name or short_name(r.source, code, r.pack, bpm), taken)
            taken.add(name)
            cell_entries.append(SampleEntry(
                source=r.source, family=fam, code=code, pack=r.pack, name=name,
                duration=r.duration, rank=rank,
                status=prev_status.get(r.source, "pending"), flags=flags[r.source],
                bpm=bpm, bpm_est=est, tags=tags_of(overrides, r.source), stars=ov.stars))
        select(cell_entries, q)
        entries.extend(cell_entries)

    return Manifest(source_root=str(root), total=len(raws) + len(unclassified) + len(trashed),
                    entries=entries, reserve=reserve, unclassified=unclassified,
                    folded=folded, trashed=trashed, trashed_kits=trashed_kits)


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


def _entry(manifest: Manifest, source: str) -> SampleEntry | None:
    return next((e for e in manifest.entries if e.source == source), None)


def _reselect(manifest: Manifest, family: str, code: str) -> list[SampleEntry]:
    """Rang (notes en tete, ordre stable sinon) puis selection d'une case."""
    cell = cell_of(manifest, family, code)
    cell.sort(key=lambda e: star_key(e.stars))
    for rank, e in enumerate(cell, 1):
        e.rank = rank
    select(cell, quota(family, code))
    return cell


def _set_override(overrides: dict[str, Override], source: str, **update: object) -> Override:
    """Met a jour l'override d'un fichier ; un override revenu aux valeurs par
    defaut est retire (overrides.json reste lisible a la main)."""
    ov = overrides.get(source, Override()).model_copy(update=update)
    if ov == Override():
        overrides.pop(source, None)
    else:
        overrides[source] = ov
    return ov


def _reserved(manifest: Manifest, source: str) -> ReserveSample | None:
    return next((r for r in manifest.reserve if r.source == source), None)


def known(manifest: Manifest, source: str) -> bool:
    """Fichier du manifeste : candidat, reserve, non classe ou en corbeille."""
    return (_entry(manifest, source) is not None or source in manifest.unclassified
            or source in manifest.trashed or _reserved(manifest, source) is not None)


def norm_tag(tag: str) -> str:
    return " ".join(tag.lower().split())[:TAG_MAX].strip()


def set_status(manifest: Manifest, source: str, status: Status) -> list[SampleEntry]:
    """Decision d'ecoute d'un candidat, puis nouvelle selection de sa case
    (un drop fait monter le pending suivant). Renvoie la case."""
    entry = _entry(manifest, source)
    if entry is None:
        raise SampleError(f"candidat inconnu : {source}")
    entry.status = status
    cell = cell_of(manifest, entry.family, entry.code)
    select(cell, quota(entry.family, entry.code))
    return cell


def _adopt(manifest: Manifest, source: str, family: str, code: str,
           overrides: dict[str, Override], root: Path, measure_fn: Measure | None,
           bpm_fn: BpmFn | None) -> SampleEntry:
    """Fait entrer un fichier hors case (non classe, restaure) en fin de case."""
    ov = overrides.get(source, Override())
    path = root / source
    present = path.is_file()
    dur = wav_duration(path) if present else None
    bpm, est = None, False
    if code in TEMPO and tempo_of(source) is None and bpm_fn is not None and present:
        bpm, est = bpm_fn(path, dur)
    target = cell_of(manifest, family, code)
    pack = pack_of(source)
    entry = SampleEntry(
        source=source, family=family, code=code, pack=pack,
        name=_unique(ov.name or short_name(source, code, pack, bpm), {e.name for e in target}),
        duration=dur, rank=max((e.rank for e in target), default=0) + 1,
        flags=measure_fn(path, code) if measure_fn is not None and present else None,
        bpm=bpm, bpm_est=est, tags=tags_of(overrides, source), stars=ov.stars)
    manifest.entries.append(entry)
    _reselect(manifest, family, code)
    return entry


def move(manifest: Manifest, overrides: dict[str, Override], source: str,
         family: str, code: str, root: Path, measure_fn: Measure | None = measure,
         bpm_fn: BpmFn | None = estimate_bpm) -> None:
    """Range un fichier dans une case (correction a l'ecoute, ou case donnee a
    un non classe, qui devient candidat).

    Statut garde ; le candidat se range en fin de la nouvelle case (apres les
    notes), renomme avec le nouveau code et remesure (blanc / long dependent du
    code). Les deux cases sont reselectionnees. L'override (famille, code) fait
    survivre le deplacement a une reconstruction ; un nom force ne suit pas."""
    if family not in FAMILIES:
        raise SampleError(f"famille inconnue : {family}")
    if code not in CODES:
        raise SampleError(f"code inconnu : {code}")
    promote(manifest, overrides, source, root, measure_fn, bpm_fn)
    entry = _entry(manifest, source)
    if entry is None and source not in manifest.unclassified:
        raise SampleError(f"ni candidat ni non classe : {source}")
    _set_override(overrides, source, family=family, code=code, name=None)
    if entry is None:
        manifest.unclassified.remove(source)
        _adopt(manifest, source, family, code, overrides, root, measure_fn, bpm_fn)
        return
    old = (entry.family, entry.code)
    if old == (family, code):
        return
    target = cell_of(manifest, family, code)
    entry.family, entry.code = family, code
    entry.rank = max((e.rank for e in target), default=0) + 1
    entry.name = _unique(short_name(source, code, entry.pack, entry.bpm),
                         {e.name for e in target})
    path = root / source
    if measure_fn is not None and path.is_file():
        entry.flags = measure_fn(path, code)
    _reselect(manifest, family, code)
    _reselect(manifest, *old)


def set_stars(manifest: Manifest, overrides: dict[str, Override], source: str,
              stars: int | None) -> None:
    """Note (None = retiree) ; un candidat note remonte dans sa case. Noter ne
    vaut pas garder : le statut ne change pas."""
    if stars is not None and not 1 <= stars <= STARS_MAX:
        raise SampleError(f"etoiles hors 1..{STARS_MAX} : {stars}")
    if not known(manifest, source):
        raise SampleError(f"sample inconnu : {source}")
    _set_override(overrides, source, stars=stars)
    entry = _entry(manifest, source)
    if entry is not None:
        entry.stars = stars
        _reselect(manifest, entry.family, entry.code)


def set_tags(manifest: Manifest, overrides: dict[str, Override], source: str,
             add: Iterable[str] = (), remove: Iterable[str] = ()) -> list[str]:
    """Ajoute / retire des tags libres (normalises) du fichier ; renvoie ses
    tags effectifs (ceux de son kit compris, qu'on retire sur le kit)."""
    if not known(manifest, source):
        raise SampleError(f"sample inconnu : {source}")
    _set_override(overrides, source, tags=_edit_tags(
        overrides.get(source, Override()).tags, add, remove))
    tags = tags_of(overrides, source)
    entry = _entry(manifest, source) or _reserved(manifest, source)
    if entry is not None:
        entry.tags = tags
    return tags


def _edit_tags(tags: Iterable[str], add: Iterable[str], remove: Iterable[str]) -> list[str]:
    gone = {norm_tag(t) for t in remove}
    return sorted((set(tags) - gone) | {t for t in map(norm_tag, add) if t})


def set_kit_tags(manifest: Manifest, overrides: dict[str, Override], kit: str,
                 add: Iterable[str] = (), remove: Iterable[str] = ()) -> list[str]:
    """Tags d'un kit (ou d'un pack), herites par tous ses fichiers ; les
    candidats et la reserve du manifeste sont mis a jour. Renvoie les tags du kit."""
    kit = kit.strip("/")
    if not kit or not _kit_exists(manifest, kit):
        raise SampleError(f"kit inconnu : {kit}")
    key = f"{kit}/"
    tags = _edit_tags(overrides.get(key, Override()).tags, add, remove)
    _set_override(overrides, key, tags=tags)
    for row in (*manifest.entries, *manifest.reserve):
        if in_kit(row.source, kit):
            row.tags = tags_of(overrides, row.source)
    return tags


def trash(manifest: Manifest, overrides: dict[str, Override], source: str) -> None:
    """Corbeille : sort le fichier de sa case (ou des non classes) ; jamais
    supprime du disque."""
    entry = _entry(manifest, source)
    spare = _reserved(manifest, source)
    if entry is not None:
        manifest.entries.remove(entry)
        _reselect(manifest, entry.family, entry.code)
    elif spare is not None:
        manifest.reserve.remove(spare)
    elif source in manifest.unclassified:
        manifest.unclassified.remove(source)
    elif source not in manifest.trashed:
        raise SampleError(f"sample inconnu : {source}")
    _set_override(overrides, source, trash=True)
    manifest.trashed = sorted({*manifest.trashed, source})


def restore(manifest: Manifest, overrides: dict[str, Override], source: str, root: Path,
            measure_fn: Measure | None = measure, bpm_fn: BpmFn | None = estimate_bpm) -> None:
    """Sort de la corbeille : retour dans sa case (override ou regles) en fin
    de case, ou parmi les non classes."""
    if source not in manifest.trashed:
        raise SampleError(f"pas dans la corbeille : {source}")
    manifest.trashed.remove(source)
    ov = _set_override(overrides, source, trash=False)
    path = root / source
    code = ov.code or code_of(source, wav_duration(path) if path.is_file() else None)
    if code is None:
        manifest.unclassified = sorted({*manifest.unclassified, source})
        return
    _adopt(manifest, source, ov.family or family_of(source), code, overrides, root,
           measure_fn, bpm_fn)


def promote(manifest: Manifest, overrides: dict[str, Override], source: str, root: Path,
            measure_fn: Measure | None = measure, bpm_fn: BpmFn | None = estimate_bpm) -> bool:
    """Fait entrer un fichier de la reserve dans sa case, comme candidat en fin
    de case (mesure, tempo). Sans effet hors reserve ; renvoie True s'il y etait.
    Une decision ou une note l'y epingle ensuite d'une reconstruction a l'autre."""
    spare = _reserved(manifest, source)
    if spare is None:
        return False
    manifest.reserve.remove(spare)
    _adopt(manifest, source, spare.family, spare.code, overrides, root, measure_fn, bpm_fn)
    return True


def overflow_of(manifest: Manifest, family: str, code: str, kit: str) -> list[SampleEntry]:
    """Reserve d'une case pour un kit, en lignes de liste (`overflow`), apres
    les candidats ; noms calcules a l'affichage."""
    start = max((e.rank for e in manifest.entries
                 if e.family == family and e.code == code), default=0)
    rows = [r for r in manifest.reserve
            if r.family == family and r.code == code and in_kit(r.source, kit)]
    return [SampleEntry(source=r.source, family=family, code=code, pack=r.pack,
                        name=short_name(r.source, code, r.pack, tempo_of(r.source)),
                        duration=r.duration, rank=start + i, tags=r.tags, overflow=True)
            for i, r in enumerate(rows, 1)]


def kits(manifest: Manifest) -> list[KitInfo]:
    """Bilan par kit (prefixe), kits a la corbeille compris, tries par chemin."""
    out: dict[str, KitInfo] = {}

    def info(kit: str) -> KitInfo:
        if kit not in out:
            out[kit] = KitInfo(kit=kit, pack=kit.split("/")[0], label=kit.rsplit("/", 1)[-1])
        return out[kit]

    for e in manifest.entries:
        k = info(kit_of(e.source))
        k.candidates += 1
        k.selected += int(e.selected)
        k.keep += int(e.status == "keep")
    for r in manifest.reserve:
        info(kit_of(r.source)).reserve += 1
    for src in manifest.unclassified:
        info(kit_of(src)).unclassified += 1
    for src in manifest.trashed:
        info(kit_of(src)).trashed += 1
    for kit, n in manifest.trashed_kits.items():
        k = info(kit)
        k.trashed_kit, k.trashed = True, k.trashed + n
    return sorted(out.values(), key=lambda k: k.kit.lower())


def kit_tags(overrides: dict[str, Override]) -> dict[str, list[str]]:
    """Tags poses sur un kit ou un pack (prefixe -> tags)."""
    return {k[:-1]: ov.tags for k, ov in sorted(overrides.items())
            if k.endswith("/") and ov.tags}


def _kit_exists(manifest: Manifest, kit: str) -> bool:
    return kit in manifest.trashed_kits or any(
        in_kit(s, kit) for s in (*(e.source for e in manifest.entries),
                                 *(r.source for r in manifest.reserve),
                                 *manifest.unclassified, *manifest.trashed))


def trash_kit(manifest: Manifest, overrides: dict[str, Override], kit: str, root: Path,
              measure_fn: Measure | None = measure,
              bpm_fn: BpmFn | None = estimate_bpm) -> Manifest:
    """Kit (ou pack) entier a la corbeille : regle dans les overrides, puis
    reconstruction (les cases se remplissent depuis la reserve). Les decisions
    d'ecoute de ses fichiers sont perdues ; tags et etoiles restent."""
    kit = kit.strip("/")
    if not kit or not _kit_exists(manifest, kit):
        raise SampleError(f"kit inconnu : {kit}")
    if kit in manifest.trashed_kits:
        raise SampleError(f"kit deja a la corbeille : {kit}")
    _set_override(overrides, f"{kit}/", trash=True)
    return build_manifest(root, overrides, manifest, measure_fn, bpm_fn)


def restore_kit(manifest: Manifest, overrides: dict[str, Override], kit: str, root: Path,
                measure_fn: Measure | None = measure,
                bpm_fn: BpmFn | None = estimate_bpm) -> Manifest:
    """Sort un kit de la corbeille : ses fichiers reviennent comme a un premier
    classement (candidats en attente, reserve, non classes)."""
    kit = kit.strip("/")
    if kit not in manifest.trashed_kits:
        raise SampleError(f"kit pas dans la corbeille : {kit}")
    _set_override(overrides, f"{kit}/", trash=False)
    return build_manifest(root, overrides, manifest, measure_fn, bpm_fn)


def loose(manifest: Manifest, overrides: dict[str, Override], which: str,
          kit: str | None = None) -> list[LooseSample]:
    """Non classes (`unclassified`) ou corbeille (`trash`), avec tags et etoiles ;
    `kit` restreint a un kit (ou un pack)."""
    sources = manifest.trashed if which == "trash" else manifest.unclassified
    out = []
    for src in sources:
        if kit and not in_kit(src, kit):
            continue
        ov = overrides.get(src, Override())
        out.append(LooseSample(source=src, pack=pack_of(src), tags=tags_of(overrides, src),
                               stars=ov.stars))
    return out


def all_tags(overrides: dict[str, Override]) -> list[str]:
    """Tags deja utilises (autocompletion)."""
    return sorted({t for ov in overrides.values() for t in ov.tags})


def grid(manifest: Manifest) -> dict[str, dict[str, tuple[int, int]]]:
    """famille -> code -> (candidats, retenus)."""
    out: dict[str, dict[str, tuple[int, int]]] = defaultdict(dict)
    for e in manifest.entries:
        n, s = out[e.family].get(e.code, (0, 0))
        out[e.family][e.code] = (n + 1, s + int(e.selected))
    return out


# --- Export (7.J3) ----------------------------------------------------------

def load_export_index(path: Path) -> dict[str, ExportItem]:
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SampleError(f"{path} : JSON invalide ({exc})") from exc
    return {k: ExportItem.model_validate(v) for k, v in raw.items()}


def save_export_index(index: dict[str, ExportItem], path: Path) -> None:
    data = {k: v.model_dump() for k, v in sorted(index.items())}
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    tmp.replace(path)


def export_plan(manifest: Manifest) -> dict[str, str]:
    """Chemin d'arrivee (relatif a dest) -> source, pour les retenus. Les noms
    sont uniques par case ; la casse est ignoree (disque macOS)."""
    plan: dict[str, str] = {}
    seen: set[str] = set()
    for e in sorted(manifest.entries, key=lambda e: (e.family, e.code, e.rank)):
        if e.selected and e.dest.lower() not in seen:
            seen.add(e.dest.lower())
            plan[e.dest] = e.source
    return plan


def export(manifest: Manifest, root: Path, dest: Path, index_path: Path,
           dry_run: bool = False) -> ExportReport:
    """Synchronise `dest` avec les retenus du manifeste (voir l'en-tete)."""
    index = load_export_index(index_path)
    plan = export_plan(manifest)
    report = ExportReport(dest=str(dest), dry_run=dry_run)
    new_index: dict[str, ExportItem] = {}
    for rel, source in plan.items():
        src, out = root / source, dest / rel
        try:
            st = src.stat()
        except FileNotFoundError:
            report.missing.append(source)
            continue
        item = ExportItem(source=source, size=st.st_size, mtime_ns=st.st_mtime_ns)
        report.files += 1
        report.bytes += st.st_size
        old = index.get(rel)
        same_size = out.is_file() and out.stat().st_size == st.st_size
        if out.exists() and old is None and not same_size:
            report.conflicts.append(rel)
            continue
        # meme taille sans entree d'index : copie d'un export interrompu, reprise
        if same_size and old in (None, item):
            report.unchanged += 1
            new_index[rel] = item
            continue
        report.copied.append(rel)
        new_index[rel] = item
        if not dry_run:
            out.parent.mkdir(parents=True, exist_ok=True)
            tmp = out.with_name(f".{out.name}.tmp")
            shutil.copy2(src, tmp)
            tmp.replace(out)
    for rel in sorted(index.keys() - plan.keys()):
        report.removed.append(rel)
        if not dry_run:
            (dest / rel).unlink(missing_ok=True)
    if not dry_run:
        _prune_empty_dirs(dest)
        save_export_index(new_index, index_path)
    return report


def _prune_empty_dirs(dest: Path) -> None:
    """Retire les dossiers de case vides (une case videe par l'ecoute)."""
    if not dest.is_dir():
        return
    for dirpath, _dirs, _files in sorted(os.walk(dest), key=lambda w: -len(w[0])):
        d = Path(dirpath)
        if d != dest and not any(d.iterdir()):
            d.rmdir()


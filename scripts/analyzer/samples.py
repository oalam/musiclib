"""Classement des samples DT2 en famille / code / fichier (Phase 7.J1).

Source : la copie des packs faite depuis Transfer (`<MEDIA>/Samples`, lecture
seule). Chaque wav recoit une famille (style, UNIVERSEL ou SAMPLE) et un code
de categorie a 2 lettres facon Elektron (`BD`, `SD`, `BR`...), puis un nom
court `<CODE> [BPM|note] <desc> <pack>` de 18 caracteres au plus : l'ecran de
choix du sample d'une track n'en montre qu'environ 14.

Selection : quota par case (dossier final), candidats = 3 x quota repartis
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

Tags inferes (7.J6) : les mots des dossiers d'un fichier donnent des tags
automatiques (`auto_tags`) via un dictionnaire cure (`TAG_WORDS`, groupes
genre / instrument / mot-cle) ; recalcules a chaque reconstruction, jamais
ecrits dans les overrides ; `no_auto` (sur un fichier ou un `<prefixe>/`) en
masque. `tag_report` liste les mots frequents non couverts.

Tonalite (7.J7) : la note d'un one-shot tonal vient du nom de fichier
(prioritaire, `note_src="nom"`) ou, pour BD / BS / PD, de l'audio
(`measure_note` : fondamentale pyin du corps du son apres l'attaque, retenue
retenue telle quelle pour BD, seulement si le pic spectral donne la meme
note pour BS / PD ; sinon `incertaine`). La
note mesuree entre dans le nom DT2 comme une note lue. Mesuree comme les
drapeaux (candidats seulement, reprise du manifeste precedent) ; la reserve
n'a que la note du nom. `SampleFilter.notes` filtre par note.

Arbre par type (7.J8) : une case est un dossier final du +Drive,
`<BRANCHE>/<CODE>/[<SOUS>]` (`DRUMS/BD/HARD`, `LOOPS/BR`, `FX/RISE`, `VX`,
`SAMPLE/<CODE>`), avec un plafond par dossier (`quota`). La famille ne range
plus : elle repere SAMPLE et donne un tag de genre (`GENRE_TAGS`). La
sous-categorie est inferee des mots du chemin (`SUB_RULES`), corrigee a
l'ecoute (override `sub`) ; une sous-categorie de moins de FOLD_MIN fichiers
remonte a la racine de son code.

Export (7.J3) : les retenus (`selected`) sont copies tels quels sous
`<dest>/<dossier final>/<nom>.wav`, arborescence que Transfer envoie sur le
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
from pydantic import BaseModel, Field, computed_field

NAME_MAX = 18
FOLD_MIN = 4          # en dessous, la sous-categorie remonte a la racine de son code
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
# Tonalite (7.J7) : plage de la fondamentale par code, attaque sautee.
NOTE_RANGE_HZ = {"BD": (30.0, 250.0), "BS": (27.0, 500.0), "PD": (40.0, 1500.0)}
NOTE_ATTACK_S = {"BD": 0.05}    # glissando du kick ; autres codes : NOTE_ATTACK_DEFAULT_S
NOTE_ATTACK_DEFAULT_S = 0.03
NOTE_PEAK_CHECK = frozenset({"BS", "PD"})   # note retenue si le pic spectral s'accorde (BD : pyin seul)
NOTE_BODY_S = 2.0               # duree lue
NOTE_MIN_FRAMES = 3             # trames voisees minimum
PITCH_CLASSES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
_FLAT_TO_SHARP = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#", "Cb": "B", "Fb": "E",
                  "E#": "F", "B#": "C"}
FLAG_WEIGHT = {"illisible": 3, "muet": 3, "sature": 1, "blanc": 1, "faible": 1, "long": 1}

FAMILIES = ("AUTRES", "DUBSTEP", "HARDCORE", "JUNGLE", "SAMPLE", "TECHNO", "TRIBE", "UNIVERSEL")
CODES = ("BD", "RM", "SD", "CP", "HH", "OH", "CY", "TM", "PC",
         "BR", "DL", "PL", "ML", "BL", "BS", "ST", "PD", "FX", "VX", "RS")
# RM : rumble (track 2 de la doctrine), rendu par le sound design (8.E) et
# range par override au versement, jamais infere d'un nom de fichier
DRUMS = frozenset({"BD", "RM", "SD", "CP", "HH", "OH", "CY", "TM", "PC"})
TONAL = frozenset({"BD", "RM", "BS", "ST", "PD", "ML", "BL"})   # note gardee dans le nom
PITCHED = frozenset({"BD", "BS", "PD"})   # note mesuree dans l'audio (7.J7 ; ST : accords)
# Boucles : BR break, DL drums, PL percussions / hats, ML melodie, BL basse
TEMPO = frozenset({"BR", "DL", "PL", "ML", "BL", "RM"})   # BPM garde dans le nom
RHYTHM = DRUMS | {"BR", "DL", "PL"}   # tracks 1 a 8 de la doctrine ; le reste : melodique
BIG_CAP = frozenset({"BR", "DL", "PL"})   # boucles rythmiques : 32 par dossier, le reste 16
# plafonds propres a un dossier final (prioritaires) : breaks lents nombreux
FOLDER_CAPS = {"LOOPS/BR/060": 64}

# Arbre du +Drive (7.J8) : BRANCHE / CODE / [SOUS] ; FX et VX sans niveau code.
BRANCHES = ("DRUMS", "TONAL", "LOOPS", "FX", "VX", "SAMPLE")
# Sous-categories par code : debuts de mots du chemin (minuscules), dans
# l'ordre de priorite ; sans mot reconnu, le fichier reste a la racine du code.
SUB_RULES: dict[str, tuple[tuple[str, tuple[str, ...]], ...]] = {
    "BD": (("HARD", ("hard", "distort", "gabber", "overdrive", "xtrmraw", "rough", "crunch")),
           ("SUB", ("sub", "boom", "808", "long")),
           ("ACOU", ("acou", "live", "real", "jazz", "vintage")),
           ("CLEAN", ("909", "clean", "tight", "punch", "short"))),
    # RM : memes sous-dossiers que le kick, herites de la source au versement
    "RM": (("HARD", ()), ("SUB", ()), ("ACOU", ()), ("CLEAN", ())),
    "ML": (("KEYS", ("piano", "key", "organ", "rhodes", "epiano")),
           ("PADS", ("pad", "drone", "nappe", "string")),
           ("ATMOS", ("atmo", "ambien", "texture", "spher", "cinematic")),
           ("GUITAR", ("guitar",))),
    "FX": (("RISE", ("rise", "riser", "uplift", "downlift", "sweep", "swell", "build", "fall",
                     "transition")),
           ("REV", ("revers",)),
           ("HIT", ("impact", "hit", "thump", "boom", "drop", "crash")),
           ("NOISE", ("noise", "glitch", "static", "white"))),
    "PC": (("SHAKER", ("shaker", "tamb", "cabasa", "maraca")),
           ("SKIN", ("conga", "bongo", "djembe", "cajon", "tabla", "udu", "bodhran", "hand", "darbuk")),
           ("METAL", ("cowbell", "bell", "metal", "agogo", "triang", "chime")),
           ("WOOD", ("block", "clave", "stick", "rim", "wood", "click", "tick")),
           ("FOLEY", ("foley", "cartoon", "orch", "sting"))),
    "PL": (("SKIN", ("conga", "bongo", "djembe", "cajon", "tabla", "udu", "bodhran", "hand")),
           ("TOPS", ("top", "hat", "ride", "cym")),
           ("SHAKER", ("shaker", "tamb"))),
    "ST": (("CHORD", ("chord",)), ("STAB", ("stab", "hit")), ("METAL", ("metal",)),
           ("ANALOG", ("minimoog", "moog", "modular", "analog", "minibrute")),
           ("BELL", ("bell", "blip", "blop", "pluck", "zap")),
           ("ORCH", ("string", "brass", "sax", "horn", "orch", "acoustic", "piano", "organ"))),
    "PD": (("AMBIENT", ("ambien", "atmo", "texture", "shimmer")),
           ("CHORD", ("chord",)),
           ("DRONE", ("drone", "rumble"))),
    "VX": (("SPEECH", ("documentary", "speech", "talk", "spoken", "news")),
           ("CHANT", ("chant", "choir", "african", "sing")),
           ("MC", ("mc", "shout", "hype", "party", "adlib", "control")),
           ("CUT", ("cut", "mouth", "chop"))),
    "BS": (("SUB", ("sub", "808")),
           ("WOB", ("wob", "dubstep", "growl")),
           ("DIST", ("dist", "filth", "buzz", "dirt", "grit", "crunch", "acid", "303")),
           ("ANALOG", ("minimoog", "moog", "analog", "minibrute", "buchla"))),
    "SD": (("RIM", ("rim",)),),
}
# Boucles BR / DL : sous-categorie = tranche de tempo, nommee par sa borne
# basse pour le tri alphabetique de la DT2 (tempo du nom, sinon mesure).
TEMPO_SUBS = frozenset({"BR", "DL"})
TEMPO_BANDS = (("060", 0), ("120", 120), ("150", 150), ("180", 180))
# Sans mot reconnu, sous-categorie par duree (lue dans l'en-tete, gratuite) :
# nom, duree minimale en secondes.
DURATION_SUBS: dict[str, tuple[tuple[str, float], ...]] = {
    "BS": (("SHORT", 0.0), ("MID", 0.6), ("LONG", 2.0)),
    "ST": (("SHORT", 0.0), ("MID", 0.6), ("LONG", 2.0)),
    "PD": (("SHORT", 0.0), ("LONG", 4.0)),      # nappes : mediane 5,4 s
}
SUBS: dict[str, tuple[str, ...]] = {
    **{c: tuple(s for s, _ in rules) for c, rules in SUB_RULES.items()},
    **{c: tuple(name for name, _ in TEMPO_BANDS) for c in TEMPO_SUBS},
}
for _c, _bands in DURATION_SUBS.items():
    SUBS[_c] = (*SUBS.get(_c, ()), *(name for name, _ in _bands))
# Famille -> tag de genre : la famille sort de l'arbre, elle reste filtrable.
GENRE_TAGS = {"HARDCORE": "hardcore", "JUNGLE": "jungle", "DUBSTEP": "dubstep",
              "TECHNO": "techno", "TRIBE": "tribe"}

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
    ("FX", rf"{_B}fx|sfx|rise|riser|downlift|uplift|impact|sweep|noise|glitch|cartoon|whoosh|reverse|drop"
           r"|thump|transition"),   # cinematic Noiiz : Low End Thumps, Transitions
    ("PD", r"pad|drone|texture|ambien|atmos|cinematic"),
    ("ST", r"stab|chord|hit|riff|arp|lead|synth|key|piano|organ|instru|minimoog|brass|string|guitar|shot"),
    ("RS", r"recorded|resample|transfers"),
)
_CODE_RX = tuple((c, re.compile(p)) for c, p in CODE_RULES)

# Une boucle se reconnait au chemin ; son code depend ensuite de son contenu.
_LOOP_RX = re.compile(rf"loop|{_B}grooves?{_E}|sequence|{_B}tops?{_E}|{_B}fill|{_B}builds?{_E}")
LOOP_RULES: tuple[tuple[str, str], ...] = (
    ("VX", r"vox|vocal|voice|chant|adlib|acapella"),
    ("ML", r"pad|drone|atmos|ambien|texture"),            # boucle de nappe : LOOPS/ML/PADS (7.J8)
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

# Tags inferes des noms de dossiers (7.J6) : groupe -> tag -> mots (minuscules).
TAG_GROUPS: dict[str, dict[str, tuple[str, ...]]] = {
    "genre": {
        "jungle": ("jungle",), "dnb": ("dnb", "drumnbass"), "breakbeat": ("breakbeat", "breaks", "break"),
        "hardcore": ("hardcore", "gabber", "xtrmraw"), "hardstyle": ("hardstyle",),
        "dubstep": ("dubstep",), "techno": ("techno", "darktechno", "tech"), "house": ("house",),
        "tribe": ("tribe", "tribal", "tribalism", "tekno", "neurotek"), "oldskool": ("oldskool", "oldschool"),
        "industrial": ("industrial",), "minimal": ("minimal",), "acid": ("acid",), "trance": ("trance",),
        "hiphop": ("hiphop",), "world": ("world", "african", "caribean", "caribbean"),
        "cinematic": ("cinematic", "trailer"),
    },
    "instrument": {
        "kick": ("kick", "kicks", "basedrums", "bassdrum", "bassdrums"), "snare": ("snare", "snares", "snaredrums"),
        "hat": ("hat", "hats", "hihat", "hihats"), "clap": ("clap", "claps"),
        "cymbal": ("cymbal", "cymbals", "ride", "crash"), "tom": ("tom", "toms"),
        "percussion": ("perc", "percu", "percussion", "percussive", "percs"), "shaker": ("shaker", "shakers"),
        "conga": ("conga", "congas"), "bongo": ("bongo", "bongos"), "cajon": ("cajon",), "djembe": ("djembe",),
        "udu": ("udu",), "bodhran": ("bodhran",), "tabla": ("tabla",), "cowbell": ("cowbell",),
        "bass": ("bass", "bassline", "basses", "sub"), "synth": ("synth", "synths"), "piano": ("piano",),
        "keys": ("key", "keys", "organ"), "guitar": ("guitar", "guitars"), "strings": ("string", "strings"),
        "orchestral": ("orch", "orchestral"), "pad": ("pad", "pads", "nappe"), "vocal": ("vocal", "vocals", "vox", "voice"),
        "arp": ("arp", "arps"), "chord": ("chord", "chords"), "riff": ("riff", "riffs"), "stab": ("stab", "stabs"),
        "lead": ("lead", "leads"), "minimoog": ("minimoog",), "909": ("909",), "808": ("808",),
        "linndrum": ("linndrum",), "mpc": ("mpc",),
    },
    "mot": {
        "cassette": ("cassette",), "foley": ("foley",), "glitch": ("glitch",), "noise": ("noise",),
        "ambient": ("ambience", "ambient", "atmos", "atmo", "atmosphere"), "riser": ("riser", "risers", "rise", "sweep", "swell"),
        "impact": ("impact", "impacts", "thumps"), "transition": ("transition", "transitions", "whoosh", "whooshes", "downlifter", "downlifters"),
        "cartoon": ("cartoon",), "vinyl": ("vinyl",), "lofi": ("lofi",), "analog": ("analog", "analogue"),
        "dark": ("dark",), "clean": ("clean",), "classic": ("classic",), "fx": ("fx", "sfx"),
        "hit": ("hit", "hits"), "sting": ("sting", "stings"), "top": ("top", "tops"), "cut": ("cut", "cuts"),
        "documentary": ("documentary",), "resample": ("resample", "resamples", "recorded"),
    },
}
TAG_WORDS: dict[str, str] = {w: tag for tags in TAG_GROUPS.values() for tag, words in tags.items() for w in words}
TAG_GROUP: dict[str, str] = {tag: g for g, tags in TAG_GROUPS.items() for tag in tags}

Status = Literal["pending", "keep", "drop"]
# nom : lue dans le nom ; mesure : mesuree ; incertaine : mesuree sans note sure
NoteSrc = Literal["nom", "mesure", "incertaine"]
LOOPS = frozenset({"BR", "DL", "PL", "ML", "BL"})
SLICES_TAG = "slices"     # tag d'un fichier de tranches GRID (sound design 8.I) : pas de controle long
LOOPED = LOOPS | {"RM"}   # boucles (pas de controle blanc / long), RM compris


class SampleError(Exception):
    """Source de samples ou manifeste inexploitable."""


class SampleEntry(BaseModel):
    """Un candidat : fichier source, case, nom DT2 et decision d'ecoute."""
    source: str                     # relatif a Samples/
    family: str                     # genre (tag) ou SAMPLE
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
    auto_tags: list[str] = Field(default_factory=list)  # inferes des dossiers (7.J6)
    note: str | None = None         # classe de hauteur en dieses (7.J7)
    note_hz: float | None = None    # fondamentale mesuree (pyin)
    note_src: NoteSrc | None = None  # None : pas mesuree (ou code non tonal)
    overflow: bool = False          # reserve hors plafond, vue par kit (7.J5), jamais stocke
    sub: str = ""                   # sous-categorie (7.J8), "" = racine du code

    @computed_field  # type: ignore[prop-decorator]
    @property
    def folder(self) -> str:
        """Dossier final (case), serialise pour le front."""
        return folder_of(self.family, self.code, self.sub)

    @property
    def dest(self) -> str:
        return f"{self.folder}/{self.name}.wav"


class Override(BaseModel):
    """Correction manuelle d'un fichier (overrides.json, cle = source)."""
    family: str | None = None
    code: str | None = None
    name: str | None = None
    exclude: bool = False
    tags: list[str] = Field(default_factory=list)
    stars: int | None = Field(default=None, ge=1, le=STARS_MAX)
    trash: bool = False     # corbeille : hors de toutes les cases, restaurable
    no_auto: list[str] = Field(default_factory=list)   # tags inferes masques (7.J6)
    sub: str | None = None  # sous-categorie forcee, "" = racine du code (7.J8)


class LooseSample(BaseModel):
    """Fichier hors des cases : non classe ou en corbeille."""
    source: str
    pack: str
    tags: list[str] = Field(default_factory=list)
    stars: int | None = None
    auto_tags: list[str] = Field(default_factory=list)


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
    auto_tags: list[str] = Field(default_factory=list)
    sub: str = ""
    # tempo deja mesure quand le fichier etait candidat : sans lui, une boucle
    # rangee dans sa tranche de tempo repartirait a la racine au passage suivant
    bpm: int | None = None
    bpm_est: bool = False

    @property
    def folder(self) -> str:
        return folder_of(self.family, self.code, self.sub)


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
    folded: list[str] = Field(default_factory=list)   # sous-categories remontees a la racine
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
    sub: str = ""


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
    if code not in LOOPED:
        first = int(np.argmax(a >= peak * 10 ** (LEAD_DB / 20)))
        if first / sr > LEAD_MAX_S:
            flags.append("blanc")
    if code in DRUMS and code not in LOOPED and a.size / sr > LONG_HIT_S:
        flags.append("long")
    return flags


def pitch_class(hz: float) -> str:
    """Classe de hauteur (dieses) d'une frequence, au demi-ton le plus proche."""
    return PITCH_CLASSES[round(12 * np.log2(hz / 440.0) + 69) % 12]


def spectral_peak(y: np.ndarray, sr: int, lo: float, hi: float) -> float | None:
    """Frequence du plus fort pic du spectre (1 s au plus, fenetre de Hann)
    entre `lo` et `hi`."""
    w = y[:sr] * np.hanning(min(y.size, sr))
    spec = np.abs(np.fft.rfft(w, 1 << 16))
    freqs = np.fft.rfftfreq(1 << 16, 1 / sr)
    band = (freqs >= lo) & (freqs <= hi)
    return float(freqs[band][np.argmax(spec[band])]) if band.any() else None


def measure_note(path: Path, code: str) -> tuple[str | None, float | None]:
    """(note, fondamentale en Hz) d'un one-shot BD / BS / PD : mediane pyin
    sur le corps du son, apres l'attaque. BD : pyin seul (le pic spectral des
    kicks distordus tombe sur un harmonique) ; BS / PD : la note n'est donnee
    que si le pic spectral tombe sur la meme, sinon (None, Hz) : incertaine."""
    import librosa   # lourd : seulement quand un one-shot doit etre mesure

    lo, hi = NOTE_RANGE_HZ[code]
    try:
        y, sr = librosa.load(str(path), sr=22050, mono=True, duration=NOTE_BODY_S)
    except Exception:  # noqa: BLE001 - fichier illisible : pas de note
        return None, None
    if not y.size:
        return None, None
    frame = 4096 if code in {"BD", "BS"} else 2048
    start = int(np.argmax(np.abs(y)))
    body = y[start + int(NOTE_ATTACK_S.get(code, NOTE_ATTACK_DEFAULT_S) * sr):]
    if body.size < frame:       # son tres court : tout depuis la crete
        body = y[start:]
    if body.size < frame:
        return None, None
    f0, voiced, _ = librosa.pyin(body, fmin=lo, fmax=hi, sr=sr, frame_length=frame)
    ok = voiced & np.isfinite(f0)
    if ok.sum() < NOTE_MIN_FRAMES:
        return None, None
    hz = float(np.median(f0[ok]))
    note = pitch_class(hz)
    if code in NOTE_PEAK_CHECK:
        peak = spectral_peak(body, sr, lo, hi)
        if not peak or pitch_class(peak) != note:
            return None, round(hz, 1)
    return note, round(hz, 1)


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


def _dir_words(rel: str) -> set[str]:
    return {t.lower() for d in rel.split("/")[:-1] for t in _tokens(d)}


def auto_tags_of(overrides: dict[str, Override], source: str) -> list[str]:
    """Tags inferes des dossiers (dictionnaire `TAG_WORDS`) et le genre de la
    famille (`GENRE_TAGS`), moins ceux que
    masque `no_auto` sur le fichier ou sur un prefixe qui le contient."""
    own = overrides.get(source, Override())
    hidden = set(own.no_auto)
    for k, ov in overrides.items():
        if k.endswith("/") and ov.no_auto and source.startswith(k):
            hidden.update(ov.no_auto)
    tags = {TAG_WORDS[w] for w in _dir_words(source) if w in TAG_WORDS}
    genre = GENRE_TAGS.get(own.family or family_of(source))   # la famille en tag (7.J8)
    if genre:
        tags.add(genre)
    return sorted(tags - hidden)


def tag_report(sources: Iterable[str], min_files: int = 20) -> list[tuple[str, int]]:
    """Mots de dossiers frequents (au moins `min_files` fichiers) absents du
    dictionnaire : candidats pour enrichir `TAG_WORDS`."""
    counts: dict[str, int] = defaultdict(int)
    for src in sources:
        for w in _dir_words(src):
            if len(w) > 2 and not w.isdigit() and w not in TAG_WORDS:
                counts[w] += 1
    return sorted(((w, n) for w, n in counts.items() if n >= min_files), key=lambda x: (-x[1], x[0]))


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


def branch_of(family: str, code: str) -> str:
    """Branche du +Drive (7.J8) : SAMPLE pour la famille SAMPLE et les resamples."""
    if family == "SAMPLE" or code == "RS":
        return "SAMPLE"
    if code in DRUMS:
        return "DRUMS"
    if code in LOOPS:
        return "LOOPS"
    if code in ("FX", "VX"):
        return code
    return "TONAL"


def folder_of(family: str, code: str, sub: str = "") -> str:
    """Dossier final : `DRUMS/BD/HARD`, `LOOPS/BR`, `FX/RISE`, `VX`, `SAMPLE/BD`
    (SAMPLE et VX sans sous-categorie)."""
    branch = branch_of(family, code)
    if branch == "SAMPLE":
        return f"SAMPLE/{code}"
    parts = [branch] if branch == code else [branch, code]
    return "/".join(parts + [sub] if sub and code in SUBS else parts)


def folder_parts(folder: str) -> tuple[str, str, str]:
    """(branche, code, sous-categorie) d'un dossier final."""
    parts = folder.split("/")
    if parts[0] in ("FX", "VX"):
        return parts[0], parts[0], parts[1] if len(parts) > 1 else ""
    return parts[0], parts[1], parts[2] if len(parts) > 2 else ""


def folder_code(folder: str) -> str:
    return folder_parts(folder)[1]


def folder_key(folder: str) -> tuple[int, int, str]:
    """Tri des dossiers : branche, code dans l'ordre des tracks, sous-categorie."""
    branch, code, sub = folder_parts(folder)
    return BRANCHES.index(branch), CODES.index(code), sub


def target_folders() -> list[str]:
    """Dossiers ou ranger un fichier (hors SAMPLE, qui suit la famille), dans
    l'ordre des branches puis des codes : racine du code, puis ses sous-categories."""
    return sorted((folder_of("", code, sub) for code in CODES if branch_of("", code) != "SAMPLE"
                   for sub in ("", *SUBS.get(code, ()))), key=folder_key)


# Sous-dossiers ajoutes a la main (7.K) : fusionnes dans SUBS au chargement
# (`samples.load_manual_subs`) ; sans mot-cle, seuls les rangements manuels
# (override `sub`) les remplissent.
SUB_NAME = re.compile(r"[A-Z0-9]{2,10}")


def register_subs(manual: dict[str, list[str]]) -> None:
    """Ajoute des sous-categories manuelles aux connues (rejouable)."""
    for code, subs in manual.items():
        known = SUBS.get(code, ())
        if code in CODES:
            SUBS[code] = (*known, *(s for s in dict.fromkeys(subs) if s not in known))


def has_sub(code: str, sub: str) -> bool:
    """`sub` est une sous-categorie connue de `code` (regles ou manuelle)."""
    return sub in SUBS.get(code, ())


def check_sub(code: str, sub: str) -> str:
    """Nom normalise d'un nouveau sous-dossier de `code`, ou SampleError."""
    name = sub.strip().upper()
    if code not in CODES or branch_of("", code) == "SAMPLE":
        raise SampleError(f"code sans sous-dossier possible : {code}")
    if not SUB_NAME.fullmatch(name):
        raise SampleError("nom de sous-dossier : 2 a 10 lettres ou chiffres")
    return name


def quota(folder: str) -> int | None:
    """Plafond de retenus d'un dossier final ; None = tout (SAMPLE)."""
    if folder.startswith("SAMPLE/"):
        return None
    if folder in FOLDER_CAPS:
        return FOLDER_CAPS[folder]
    return 32 if folder_code(folder) in BIG_CAP else 16


def tempo_band(bpm: int | None) -> str:
    """Tranche de tempo d'une boucle BR / DL, "" sans tempo."""
    if not bpm:
        return ""
    return [name for name, lo in TEMPO_BANDS if bpm >= lo][-1]


def sub_of(rel: str, code: str, duration: float | None = None) -> str:
    """Sous-categorie inferee des mots du chemin (`SUB_RULES`), sinon de la
    duree (`DURATION_SUBS`) ; pour BR / DL, du tempo ecrit dans le nom ; ""
    sinon."""
    if code in TEMPO_SUBS:
        return tempo_band(tempo_of(rel))
    words = [t.lower() for t in _tokens(rel.rsplit(".", 1)[0].replace("/", " "))]
    by_word = next((sub for sub, starts in SUB_RULES.get(code, ())
                    if any(w.startswith(starts) for w in words)), "")
    if by_word or duration is None or code not in DURATION_SUBS:
        return by_word
    return [name for name, lo in DURATION_SUBS[code] if duration >= lo][-1]


def _sub_for(rel: str, family: str, code: str, ov: Override, duration: float | None) -> str:
    """Sous-categorie forcee par l'override, sinon inferee ; aucune en SAMPLE."""
    if branch_of(family, code) == "SAMPLE":
        return ""
    return ov.sub if ov.sub is not None else sub_of(rel, code, duration)


# --- Nommage ----------------------------------------------------------------

def _tokens(text: str) -> list[str]:
    """Mots du nom : separateurs, CamelCase et frontieres lettres/chiffres."""
    return [t for chunk in _SPLIT_RX.split(text) for t in _CAMEL_RX.split(chunk) if t]


def name_note(rel: str, code: str) -> str | None:
    """Note ecrite dans le nom d'un fichier tonal, telle quelle (`Bb`, `C#`)."""
    if code not in TONAL:
        return None
    tok = next((t for t in _tokens(Path(rel).stem) if _NOTE_RX.match(t)), None)
    return _NOTE_RX.match(tok).group(1) if tok else None  # type: ignore[union-attr]


def sharp(note: str) -> str:
    """`Bb` -> `A#` : les notes du filtre et de la roue sont en dieses."""
    return _FLAT_TO_SHARP.get(note, note)


def short_name(rel: str, code: str, pack: str, bpm: int | None = None,
               note: str | None = None) -> str:
    """`<CODE> [BPM|note] <desc> <num> <pack>`, NAME_MAX caracteres au plus.
    `bpm` : tempo mesure, utilise si le chemin n'en donne pas ; `note` : note
    mesuree, utilisee si le nom n'en donne pas (7.J7)."""
    parts = rel.split("/")
    stem = Path(parts[-1]).stem
    folder_words = {t.lower() for d in parts[:-1] for t in _tokens(d)}
    toks = _tokens(stem)

    head: list[str] = []
    if code in TEMPO:
        tempo = tempo_of(rel) or bpm
        if tempo:
            head.append(str(tempo))
    note_tok = None
    if code in TONAL:
        note_tok = next((t for t in toks if _NOTE_RX.match(t)), None)
        if note_tok:
            head.append(_NOTE_RX.match(note_tok).group(1))  # type: ignore[union-attr]
        elif note:
            head.append(note)

    # numero de variante : 1-2 chiffres ; 406, 516... sont des references de label
    nums = [t for t in toks if t.isdigit() and (len(t) <= 2 or t.startswith("0"))
            and t not in head]
    num = f"{int(nums[-1]):02d}" if nums else ""
    # abreviations de pack en capitales (LS-CVP, PXXL) ignorees si le nom a
    # aussi des minuscules ; les lettres isolees ne disent rien
    has_lower = any(c.islower() for c in stem)
    words = [
        t.capitalize() for t in toks
        if t.isalpha() and t != note_tok and len(t) > 1
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


def unique_name(name: str, taken: set[str]) -> str:
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
        fam = ov.family or family_of(rel)
        raws.append(_Raw(source=rel, family=fam, code=code, pack=pack_of(rel), duration=dur,
                         sub=_sub_for(rel, fam, code, ov, dur)))
    return raws, unclassified, sorted(trashed), trashed_kits


def _raw_folder(r: _Raw) -> str:
    assert r.code is not None
    return folder_of(r.family, r.code, r.sub)


def fold_small_subs(raws: list[_Raw], overrides: dict[str, Override]) -> list[str]:
    """Remonte a la racine de leur code les sous-categories de moins de
    FOLD_MIN fichiers (sauf sous-categorie forcee)."""
    counts: dict[str, int] = defaultdict(int)
    for r in raws:
        if r.sub:
            counts[_raw_folder(r)] += 1
    folded = sorted(f for f, n in counts.items() if n < FOLD_MIN)
    for r in raws:
        forced = overrides.get(r.source, Override()).sub is not None
        if r.sub and not forced and _raw_folder(r) in folded:
            r.sub = ""
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
NoteFn = Callable[[Path, str], tuple[str | None, float | None]]
NoteFields = tuple[str | None, float | None, NoteSrc | None]


def note_fields(source: str, code: str, path: Path, old: SampleEntry | None,
                note_fn: NoteFn | None) -> NoteFields:
    """(note, Hz, origine) d'un candidat : la note du nom d'abord, sinon la
    mesure du manifeste precedent (meme code), sinon `note_fn` (BD / BS / PD)."""
    written = name_note(source, code)
    if written:
        return sharp(written), None, "nom"
    if code not in PITCHED:
        return None, None, None
    if old is not None and old.code == code and old.note_src in ("mesure", "incertaine"):
        return old.note, old.note_hz, old.note_src
    if note_fn is None or not path.is_file():
        return None, None, None
    note, hz = note_fn(path, code)
    return note, hz, "mesure" if note else "incertaine"


def measured_note(fields: NoteFields) -> str | None:
    """Note a ecrire dans le nom : la mesuree ; celle du nom y est deja."""
    return fields[0] if fields[2] == "mesure" else None


def _pinned(source: str, prev_status: dict[str, Status], overrides: dict[str, Override]) -> bool:
    ov = overrides.get(source)
    touched = ov is not None and (ov.family is not None or ov.code is not None
                                  or ov.sub is not None or ov.stars is not None)
    return touched or prev_status.get(source, "pending") != "pending"


def star_key(stars: int | None) -> int:
    """Cle de tri : les notes passent devant les non-notes, 5 etoiles d'abord."""
    return -(stars or 0)



def build_manifest(root: Path, overrides: dict[str, Override],
                   previous: Manifest | None = None,
                   measure_fn: Measure | None = measure,
                   bpm_fn: BpmFn | None = estimate_bpm,
                   note_fn: NoteFn | None = measure_note) -> Manifest:
    """Manifeste rejouable. Les drapeaux et notes deja mesures sont repris du
    manifeste precedent ; `measure_fn=None` saute la mesure (rang = tour de role)."""
    raws, unclassified, trashed, trashed_kits = classify(root, overrides)
    prev = {e.source: e for e in previous.entries} if previous else {}
    # tempos deja mesures, candidats et reserve : un tempo n'est jamais perdu
    # (sinon les boucles oscillent entre racine et tranche d'un passage a l'autre)
    prev_bpm: dict[str, tuple[int, bool]] = {}
    if previous:
        prev_bpm = {r.source: (r.bpm, r.bpm_est) for r in previous.reserve if r.bpm}
        prev_bpm |= {e.source: (e.bpm, e.bpm_est) for e in previous.entries if e.bpm}
    # boucle BR / DL sans tempo dans le nom : tranche du tempo deja mesure (un
    # tempo mesure a ce passage la range au suivant)
    for r in raws:
        old_bpm = prev_bpm.get(r.source)
        if (r.code in TEMPO_SUBS and not r.sub and old_bpm is not None
                and branch_of(r.family, r.code) != "SAMPLE"
                and overrides.get(r.source, Override()).sub is None):
            r.sub = tempo_band(old_bpm[0])
    folded = fold_small_subs(raws, overrides)
    prev_status = {k: e.status for k, e in prev.items()}

    cells: dict[str, list[_Raw]] = defaultdict(list)
    for r in raws:
        cells[_raw_folder(r)].append(r)

    entries: list[SampleEntry] = []
    reserve: list[ReserveSample] = []
    for folder, items in sorted(cells.items()):
        code = folder_code(folder)
        q = quota(folder)
        ordered = _round_robin(items)
        # les decisions d'ecoute restent candidates meme hors du plafond
        cap = len(ordered) if q is None else q * CANDIDATE_FACTOR
        # les decisions d'ecoute et les deplacements manuels (override de case)
        # restent candidats meme hors du plafond
        kept = ordered[:cap] + [r for r in ordered[cap:] if _pinned(r.source, prev_status, overrides)]
        held = {r.source for r in kept}
        reserve.extend(ReserveSample(source=r.source, family=r.family, code=code, sub=r.sub,
                                     pack=r.pack, duration=r.duration,
                                     tags=tags_of(overrides, r.source),
                                     auto_tags=auto_tags_of(overrides, r.source),
                                     bpm=prev_bpm.get(r.source, (None, False))[0],
                                     bpm_est=prev_bpm.get(r.source, (None, False))[1])
                       for r in ordered[cap:] if r.source not in held)
        flags: dict[str, list[str] | None] = {}
        for r in kept:
            old = prev.get(r.source)
            if old is not None and old.flags is not None and old.code == code:
                flags[r.source] = old.flags
            elif measure_fn is not None:
                measured = measure_fn(root / r.source, code)
                # fichier de tranches (variations, 8.I) : plusieurs frappes a la
                # suite, la duree ne dit rien de la qualite
                if SLICES_TAG in tags_of(overrides, r.source):
                    measured = [f for f in measured if f != "long"]
                flags[r.source] = measured
            else:
                flags[r.source] = None
        # tempo des boucles qui ne l'ecrivent pas (repris du manifeste precedent)
        tempos: dict[str, tuple[int | None, bool]] = {}
        if code in TEMPO:
            for r in kept:
                if tempo_of(r.source) is not None:
                    continue
                if r.source in prev_bpm:
                    tempos[r.source] = prev_bpm[r.source]
                elif bpm_fn is not None:
                    tempos[r.source] = bpm_fn(root / r.source, r.duration)
        notes = {r.source: note_fields(r.source, code, root / r.source, prev.get(r.source), note_fn)
                 for r in kept}
        # tri stable : les notes en tete, les defauts en fin de case, le tour
        # de role reste
        stars = {r.source: overrides.get(r.source, Override()).stars for r in kept}
        kept.sort(key=lambda r: (star_key(stars[r.source]), penalty(flags[r.source])))
        taken: set[str] = set()
        cell_entries: list[SampleEntry] = []
        for rank, r in enumerate(kept, 1):
            ov = overrides.get(r.source, Override())
            bpm, est = tempos.get(r.source, (None, False))
            note, note_hz, note_src = notes[r.source]
            name = unique_name(ov.name or short_name(r.source, code, r.pack, bpm,
                                                 measured_note(notes[r.source])), taken)
            taken.add(name)
            cell_entries.append(SampleEntry(
                source=r.source, family=r.family, code=code, sub=r.sub, pack=r.pack, name=name,
                duration=r.duration, rank=rank,
                status=prev_status.get(r.source, "pending"), flags=flags[r.source],
                bpm=bpm, bpm_est=est, tags=tags_of(overrides, r.source), stars=ov.stars,
                auto_tags=auto_tags_of(overrides, r.source),
                note=note, note_hz=note_hz, note_src=note_src))
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


def cell_of(manifest: Manifest, folder: str) -> list[SampleEntry]:
    """Candidats d'une case (dossier final), par rang."""
    return sorted((e for e in manifest.entries if e.folder == folder), key=lambda e: e.rank)


def _entry(manifest: Manifest, source: str) -> SampleEntry | None:
    return next((e for e in manifest.entries if e.source == source), None)


def _reselect(manifest: Manifest, folder: str) -> list[SampleEntry]:
    """Rang (notes en tete, ordre stable sinon) puis selection d'une case."""
    cell = cell_of(manifest, folder)
    cell.sort(key=lambda e: star_key(e.stars))
    for rank, e in enumerate(cell, 1):
        e.rank = rank
    select(cell, quota(folder))
    return cell


def set_override(overrides: dict[str, Override], source: str, **update: object) -> Override:
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
    cell = cell_of(manifest, entry.folder)
    select(cell, quota(entry.folder))
    return cell


def _adopt(manifest: Manifest, source: str, family: str, code: str, sub: str,
           overrides: dict[str, Override], root: Path, measure_fn: Measure | None,
           bpm_fn: BpmFn | None, note_fn: NoteFn | None) -> SampleEntry:
    """Fait entrer un fichier hors case (non classe, restaure) en fin de case."""
    ov = overrides.get(source, Override())
    path = root / source
    present = path.is_file()
    dur = wav_duration(path) if present else None
    bpm, est = None, False
    if code in TEMPO and tempo_of(source) is None and bpm_fn is not None and present:
        bpm, est = bpm_fn(path, dur)
    notes = note_fields(source, code, path, None, note_fn)
    if (not sub and code in TEMPO_SUBS and ov.sub is None
            and branch_of(family, code) != "SAMPLE"):
        sub = tempo_band(bpm)
    folder = folder_of(family, code, sub)
    target = cell_of(manifest, folder)
    pack = pack_of(source)
    entry = SampleEntry(
        source=source, family=family, code=code, sub=sub, pack=pack,
        name=unique_name(ov.name or short_name(source, code, pack, bpm, measured_note(notes)),
                     {e.name for e in target}),
        duration=dur, rank=max((e.rank for e in target), default=0) + 1,
        flags=measure_fn(path, code) if measure_fn is not None and present else None,
        bpm=bpm, bpm_est=est, tags=tags_of(overrides, source), stars=ov.stars,
        auto_tags=auto_tags_of(overrides, source),
        note=notes[0], note_hz=notes[1], note_src=notes[2])
    manifest.entries.append(entry)
    _reselect(manifest, folder)
    return entry


def move(manifest: Manifest, overrides: dict[str, Override], source: str,
         code: str, sub: str, root: Path, measure_fn: Measure | None = measure,
         bpm_fn: BpmFn | None = estimate_bpm, note_fn: NoteFn | None = measure_note) -> None:
    """Range un fichier dans une case : code et sous-categorie ("" = racine du
    code), correction a l'ecoute ou case donnee a un non classe, qui devient
    candidat. La famille (genre, SAMPLE) ne change pas.

    Statut garde ; le candidat se range en fin de la nouvelle case (apres les
    notes), renomme avec le nouveau code et remesure (blanc / long dependent du
    code), note comprise. Les deux cases sont reselectionnees. L'override
    (code, sous-categorie) fait survivre le deplacement a une reconstruction ;
    un nom force ne suit pas."""
    if code not in CODES:
        raise SampleError(f"code inconnu : {code}")
    if sub and sub not in SUBS.get(code, ()):
        raise SampleError(f"sous-categorie inconnue pour {code} : {sub}")
    promote(manifest, overrides, source, root, measure_fn, bpm_fn, note_fn)
    entry = _entry(manifest, source)
    if entry is None and source not in manifest.unclassified:
        raise SampleError(f"ni candidat ni non classe : {source}")
    set_override(overrides, source, code=code, sub=sub, name=None)
    if entry is None:
        manifest.unclassified.remove(source)
        family = overrides.get(source, Override()).family or family_of(source)
        _adopt(manifest, source, family, code, sub, overrides, root, measure_fn, bpm_fn,
               note_fn)
        return
    old = entry.folder
    folder = folder_of(entry.family, code, sub)
    if old == folder and entry.code == code:
        return
    target = cell_of(manifest, folder)
    old_entry = entry.model_copy()
    entry.code, entry.sub = code, sub
    entry.rank = max((e.rank for e in target), default=0) + 1
    path = root / source
    notes = note_fields(source, code, path, old_entry, note_fn)
    entry.note, entry.note_hz, entry.note_src = notes
    entry.name = unique_name(short_name(source, code, entry.pack, entry.bpm, measured_note(notes)),
                         {e.name for e in target})
    if measure_fn is not None and path.is_file():
        entry.flags = measure_fn(path, code)
    _reselect(manifest, folder)
    _reselect(manifest, old)


def set_stars(manifest: Manifest, overrides: dict[str, Override], source: str,
              stars: int | None) -> None:
    """Note (None = retiree) ; un candidat note remonte dans sa case. Noter ne
    vaut pas garder : le statut ne change pas."""
    if stars is not None and not 1 <= stars <= STARS_MAX:
        raise SampleError(f"etoiles hors 1..{STARS_MAX} : {stars}")
    if not known(manifest, source):
        raise SampleError(f"sample inconnu : {source}")
    set_override(overrides, source, stars=stars)
    entry = _entry(manifest, source)
    if entry is not None:
        entry.stars = stars
        _reselect(manifest, entry.folder)


def set_tags(manifest: Manifest, overrides: dict[str, Override], source: str,
             add: Iterable[str] = (), remove: Iterable[str] = ()) -> list[str]:
    """Ajoute / retire des tags libres (normalises) du fichier ; renvoie ses
    tags effectifs (ceux de son kit compris, qu'on retire sur le kit)."""
    if not known(manifest, source):
        raise SampleError(f"sample inconnu : {source}")
    set_override(overrides, source, tags=_edit_tags(
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
    set_override(overrides, key, tags=tags)
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
        _reselect(manifest, entry.folder)
    elif spare is not None:
        manifest.reserve.remove(spare)
    elif source in manifest.unclassified:
        manifest.unclassified.remove(source)
    elif source not in manifest.trashed:
        raise SampleError(f"sample inconnu : {source}")
    set_override(overrides, source, trash=True)
    manifest.trashed = sorted({*manifest.trashed, source})


def restore(manifest: Manifest, overrides: dict[str, Override], source: str, root: Path,
            measure_fn: Measure | None = measure, bpm_fn: BpmFn | None = estimate_bpm,
            note_fn: NoteFn | None = measure_note) -> None:
    """Sort de la corbeille : retour dans sa case (override ou regles) en fin
    de case, ou parmi les non classes."""
    if source not in manifest.trashed:
        raise SampleError(f"pas dans la corbeille : {source}")
    manifest.trashed.remove(source)
    ov = set_override(overrides, source, trash=False)
    path = root / source
    dur = wav_duration(path) if path.is_file() else None
    code = ov.code or code_of(source, dur)
    if code is None:
        manifest.unclassified = sorted({*manifest.unclassified, source})
        return
    family = ov.family or family_of(source)
    _adopt(manifest, source, family, code, _sub_for(source, family, code, ov, dur), overrides, root,
           measure_fn, bpm_fn, note_fn)


def promote(manifest: Manifest, overrides: dict[str, Override], source: str, root: Path,
            measure_fn: Measure | None = measure, bpm_fn: BpmFn | None = estimate_bpm,
            note_fn: NoteFn | None = measure_note) -> bool:
    """Fait entrer un fichier de la reserve dans sa case, comme candidat en fin
    de case (mesure, tempo). Sans effet hors reserve ; renvoie True s'il y etait.
    Une decision ou une note l'y epingle ensuite d'une reconstruction a l'autre."""
    spare = _reserved(manifest, source)
    if spare is None:
        return False
    manifest.reserve.remove(spare)
    _adopt(manifest, source, spare.family, spare.code, spare.sub, overrides, root, measure_fn,
           bpm_fn, note_fn)
    return True


def overflow_of(manifest: Manifest, folder: str,
                kit: str | None = None) -> list[SampleEntry]:
    """Reserve d'une case (d'un kit, ou toute avec `kit=None`), en lignes de
    liste (`overflow`), apres les candidats ; noms calcules a l'affichage."""
    start = max((e.rank for e in manifest.entries if e.folder == folder), default=0)
    rows = [r for r in manifest.reserve
            if r.folder == folder and (kit is None or in_kit(r.source, kit))]
    notes = [_reserve_note(r) for r in rows]
    return [SampleEntry(source=r.source, family=r.family, code=r.code, sub=r.sub, pack=r.pack,
                        name=short_name(r.source, r.code, r.pack, tempo_of(r.source)),
                        duration=r.duration, rank=start + i, tags=r.tags,
                        auto_tags=r.auto_tags, overflow=True,
                        note=note, note_src="nom" if note else None)
            for i, (r, note) in enumerate(zip(rows, notes), 1)]


# Tranches de tempo du filtre de la vue de droite (7.K) : nom, borne basse.
BPM_BANDS = (("<90", 0), ("90", 90), ("110", 110), ("130", 130), ("145", 145),
             ("160", 160), ("175", 175), ("190", 190))


def bpm_band(bpm: int | None) -> str | None:
    """Tranche de BPM_BANDS d'un tempo ; None sans tempo."""
    if not bpm:
        return None
    return [name for name, lo in BPM_BANDS if bpm >= lo][-1]


def tempo_of_entry(source: str, measured: int | None = None) -> int | None:
    """Tempo d'un fichier : ecrit dans le chemin, sinon mesure (boucles)."""
    return tempo_of(source) or measured


class SampleFilter(BaseModel):
    """Barre de recherche (7.J6) : ET entre facettes, OU dans une facette."""
    q: str | None = None                    # mots du nom DT2 ou du chemin (tous)
    tags: list[str] = Field(default_factory=list)   # manuels, de kit ou inferes
    kits: list[str] = Field(default_factory=list)   # prefixes de kit ou de pack
    section: Literal["rhythm", "melodic"] | None = None
    codes: list[str] = Field(default_factory=list)
    kind: Literal["oneshot", "loop"] | None = None
    min_stars: int | None = None
    notes: list[str] = Field(default_factory=list)  # classes de hauteur, en dieses (7.J7)
    bpms: list[str] = Field(default_factory=list)   # tranches de BPM_BANDS (7.K)

    def active(self) -> bool:
        return self != SampleFilter()

    def keep(self, source: str, code: str | None, tags: Iterable[str], auto: Iterable[str],
             stars: int | None = None, name: str = "", note: str | None = None,
             bpm: int | None = None) -> bool:
        if self.notes and note not in self.notes:
            return False
        if self.bpms and bpm_band(bpm) not in self.bpms:
            return False
        if self.q and not all(w in f"{name} {source}".lower() for w in self.q.lower().split()):
            return False
        if self.tags and not set(self.tags) & {*tags, *auto}:
            return False
        if self.kits and not any(in_kit(source, k) for k in self.kits):
            return False
        if code is None:        # non classe : aucune case, exclu des facettes de case
            return not (self.section or self.codes or self.kind)
        if self.section and (code in RHYTHM) != (self.section == "rhythm"):
            return False
        if self.codes and code not in self.codes:
            return False
        if self.kind and (code in LOOPS) != (self.kind == "loop"):
            return False
        return not self.min_stars or (stars or 0) >= self.min_stars


def filter_manifest(manifest: Manifest, f: SampleFilter,
                    overrides: dict[str, Override]) -> Manifest:
    """Copie du manifeste reduite aux fichiers qui passent le filtre ; grille,
    kits, cases et listes se calculent dessus (rangs et selection d'origine)."""
    if not f.active():
        return manifest
    loose_ok = [src for src in manifest.unclassified
                if f.keep(src, None, tags_of(overrides, src), auto_tags_of(overrides, src),
                          overrides.get(src, Override()).stars, bpm=tempo_of(src))]
    trash_ok = [src for src in manifest.trashed
                if f.keep(src, None, tags_of(overrides, src), auto_tags_of(overrides, src),
                          overrides.get(src, Override()).stars, bpm=tempo_of(src))]
    return manifest.model_copy(update={
        "entries": [e for e in manifest.entries
                    if f.keep(e.source, e.code, e.tags, e.auto_tags, e.stars, e.name, e.note,
                              tempo_of_entry(e.source, e.bpm))],
        "reserve": [r for r in manifest.reserve
                    if f.keep(r.source, r.code, r.tags, r.auto_tags, note=_reserve_note(r),
                              bpm=tempo_of_entry(r.source, r.bpm))],
        "unclassified": loose_ok, "trashed": trash_ok,
    })


def facet_tags(manifest: Manifest, overrides: dict[str, Override]) -> list[tuple[str, str, int]]:
    """(tag, groupe, fichiers) pour la barre de recherche : groupes du
    dictionnaire (genre, instrument, mot), sinon `manuel`."""
    counts: dict[str, int] = defaultdict(int)
    rows = [(e.tags, e.auto_tags) for e in manifest.entries] + \
           [(r.tags, r.auto_tags) for r in manifest.reserve] + \
           [(tags_of(overrides, s), auto_tags_of(overrides, s)) for s in manifest.unclassified]
    for tags, auto in rows:
        for t in {*tags, *auto}:
            counts[t] += 1
    return sorted(((t, TAG_GROUP.get(t, "manuel"), n) for t, n in counts.items()),
                  key=lambda x: (-x[2], x[0]))


def _reserve_note(r: ReserveSample) -> str | None:
    """Reserve non mesuree : seule la note du nom compte."""
    written = name_note(r.source, r.code)
    return sharp(written) if written else None


def facet_notes(manifest: Manifest, kit: str | None = None) -> list[tuple[str, int]]:
    """(note, fichiers) des 12 classes de hauteur, candidats et reserve, pour
    la roue chromatique (7.J7) ; reduit a un kit si donne (7.K)."""
    counts = dict.fromkeys(PITCH_CLASSES, 0)
    entries = [e.note for e in manifest.entries if kit is None or in_kit(e.source, kit)]
    reserve = [_reserve_note(r) for r in manifest.reserve if kit is None or in_kit(r.source, kit)]
    for note in entries + reserve:
        if note in counts:
            counts[note] += 1
    return list(counts.items())


def facet_bpms(manifest: Manifest, kit: str | None = None) -> list[tuple[str, int]]:
    """(tranche, fichiers) de BPM_BANDS, candidats et reserve, reduit a un kit
    si donne : filtre de tempo de la vue de droite (7.K)."""
    tally = {name: 0 for name, _ in BPM_BANDS}
    tempos = [tempo_of_entry(e.source, e.bpm) for e in manifest.entries if kit is None or in_kit(e.source, kit)]
    tempos += [tempo_of_entry(r.source, r.bpm) for r in manifest.reserve if kit is None or in_kit(r.source, kit)]
    for t in tempos:
        band = bpm_band(t)
        if band is not None:
            tally[band] += 1
    return list(tally.items())


def kit_rows(manifest: Manifest, kit: str | None) -> list[SampleEntry]:
    """Fichiers classes d'un kit (tous avec `kit=None`), case par case :
    candidats par rang, puis la reserve hors plafond (`overflow`).
    Arborescence du front (7.J5, vue par type 7.K)."""
    def keep(source: str) -> bool:
        return kit is None or in_kit(source, kit)

    out: list[SampleEntry] = []
    cells = sorted({e.folder for e in manifest.entries if keep(e.source)}
                   | {r.folder for r in manifest.reserve if keep(r.source)}, key=folder_key)
    for folder in cells:
        out += [e for e in cell_of(manifest, folder) if keep(e.source)]
        out += overflow_of(manifest, folder, kit)
    return out


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
              bpm_fn: BpmFn | None = estimate_bpm,
              note_fn: NoteFn | None = measure_note) -> Manifest:
    """Kit (ou pack) entier a la corbeille : regle dans les overrides, puis
    reconstruction (les cases se remplissent depuis la reserve). Les decisions
    d'ecoute de ses fichiers sont perdues ; tags et etoiles restent."""
    kit = kit.strip("/")
    if not kit or not _kit_exists(manifest, kit):
        raise SampleError(f"kit inconnu : {kit}")
    if kit in manifest.trashed_kits:
        raise SampleError(f"kit deja a la corbeille : {kit}")
    set_override(overrides, f"{kit}/", trash=True)
    return build_manifest(root, overrides, manifest, measure_fn, bpm_fn, note_fn)


def restore_kit(manifest: Manifest, overrides: dict[str, Override], kit: str, root: Path,
                measure_fn: Measure | None = measure,
                bpm_fn: BpmFn | None = estimate_bpm,
                note_fn: NoteFn | None = measure_note) -> Manifest:
    """Sort un kit de la corbeille : ses fichiers reviennent comme a un premier
    classement (candidats en attente, reserve, non classes)."""
    kit = kit.strip("/")
    if kit not in manifest.trashed_kits:
        raise SampleError(f"kit pas dans la corbeille : {kit}")
    set_override(overrides, f"{kit}/", trash=False)
    return build_manifest(root, overrides, manifest, measure_fn, bpm_fn, note_fn)


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
                               stars=ov.stars, auto_tags=auto_tags_of(overrides, src)))
    return out


def all_tags(overrides: dict[str, Override]) -> list[str]:
    """Tags deja utilises (autocompletion)."""
    return sorted({t for ov in overrides.values() for t in ov.tags})


def grid(manifest: Manifest) -> dict[str, tuple[int, int]]:
    """dossier final -> (candidats, retenus), dans l'ordre des chemins."""
    out: dict[str, tuple[int, int]] = {}
    for e in manifest.entries:
        n, s = out.get(e.folder, (0, 0))
        out[e.folder] = (n + 1, s + int(e.selected))
    return dict(sorted(out.items(), key=lambda kv: folder_key(kv[0])))


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
    for e in sorted(manifest.entries, key=lambda e: (e.folder, e.rank)):
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


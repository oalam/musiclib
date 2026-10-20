"""Lives DT2 (Phase 7.L) : selection de samples de la lib rangee par banque.

La lib (7.J) range par type pour chercher ; un live range par banque pour
jouer. Un live est un fichier `<LIVES_META_DIR>/<live>.json` : ses banques
(une par section, ex. `A-HALF`), et pour chaque sample retenu sa source, sa
branche (DRUMS, TONAL, LOOPS, FX, VX), son nom DT2 et les banques qui
l'utilisent. Il est independant des decisions keep / drop de la lib : la
source est tout le catalogue classe (candidats et reserve).

Arbre de l'export, que Transfer envoie sur le +Drive (7.L5) :
`<DT2_LIVES_DIR>/<live>/<BANQUE>/<nom>.wav`, a plat : une banque de patterns
= une banque RAM de la DT2 (127 slots) = un dossier, charge d'un coup. Un
sample appartient a une seule banque (l'ajouter ailleurs le deplace). Pas de
dossier par branche ni par code : le prefixe du nom regroupe au tri
alphabetique. Plafond de LIVE_CAP fichiers par banque, en simple avertissement.

Kit par defaut `0-KIT` : banque implicite de KIT_TRACKS samples au plus, un
par track de la grille de la doctrine (`track`), exporte en
`0-KIT/<NN> <nom>.wav` ; charge en premier dans la banque RAM A, il occupe les
slots A01-A16 sur lesquels pointe tout pattern vide.

RAM : la DT2 charge les samples en 48 kHz / 16 bits, 400 Mo par projet
(manuel §9.1). La place d'un sample est estimee a ce format (Transfer
convertit a l'envoi), pas d'apres la taille du fichier source ; elle est
mesuree a l'ajout (en-tete seul) et gardee dans le live.

Export rejouable : meme copie que l'export de la lib (`samples.sync`), avec
un index propre au live (`<live>.export.json`).

Accordage par banque : les kicks, rumbles, basses, pads et stabs (TUNABLE) d'une banque
dont la note est connue sont ramenes sur la tonique de sa tonalite, par le
plus court chemin (-6 a +5 demi-tons). Le decalage est garde dans le live et
applique a l'export en varispeed (comme le pitch de la DT2 : la duree suit) ;
la lib n'est pas touchee. L'accordage s'applique au live entier
(`tune_live`) ; 0-KIT a sa propre tonalite, comme une banque.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

import soundfile as sf
from pydantic import BaseModel, Field, model_validator

from .samples import (
    NAME_MAX,
    ExportReport,
    Manifest,
    PITCHED,
    SampleError,
    _entry,
    _reserved,
    branch_of,
    measure_note,
    name_note,
    sharp,
    short_name,
    sync,
    unique_name,
)

KIT = "0-KIT"                    # kit par defaut : slots A01-A16 du projet
KIT_TRACKS = 16
LEGACY_COMMON = "0-COMMON"       # banque implicite d'avant 7.L5, fusionnee a la migration
LIVE_CAP = 127                   # fichiers par banque : une banque RAM de la DT2 (1016 / 8)
LIVE_BRANCHES = ("DRUMS", "TONAL", "LOOPS", "FX", "VX")
# tracks du kit proposees par code (grille de digitakt/doctrine §1, analyzer.digitakt.TRACKS)
KIT_TRACK_FOR: dict[str, tuple[int, ...]] = {
    "BD": (1,), "RM": (2,), "SD": (3,), "CP": (3,), "TM": (4, 5), "PC": (4, 5),
    "BR": (5,), "DL": (5,), "PL": (5,), "HH": (6,), "OH": (7,), "CY": (8,),
    "BS": (9,), "BL": (9, 13), "ST": (10,), "PD": (11,), "VX": (12,),
    "ML": (14, 13), "FX": (15,),
}
DT2_RATE = 48_000
DT2_SAMPLE_BYTES = 2             # 16 bits
RAM_LIMIT = 400_000_000          # 400 Mo par projet (manuel §9.1)
LIVE_NAME = re.compile(r"[a-z0-9][a-z0-9_-]{0,31}")
BANK_NAME = re.compile(r"[A-Z1-9][A-Z0-9-]{0,15}")   # 0-... reserve a 0-KIT
PACK_NAME = re.compile(r"[a-z0-9]{2,4}")
KEY_MAX = 12                     # tonalite d'une banque, texte libre (Fa m, sol mineur)
TEMPO_RANGE = (30.0, 300.0)      # BPM de la DT2
EXPORT_SUFFIX = ".export.json"
TUNABLE = frozenset({"BD", "RM", "BS", "PD", "ST"})   # one-shots accordes sur la tonique de la banque
RUMBLE_PRESETS_MAX = 5           # presets de rumble associes a une banque (8.L2)
PRESET_ID = re.compile(r"[a-z0-9_]{1,32}")   # id de preset du sound design (nom de fichier)
PITCH_CLASSES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
_SOLFEGE = {"do": "C", "re": "D", "mi": "E", "fa": "F", "sol": "G", "la": "A", "si": "B"}
_KEY_RX = re.compile(
    r"^(?:(?P<fr>do|r[eé]|mi|fa|sol|la|si)|(?P<en>[a-g]))"
    r"\s*(?P<acc>#|♯|b(?![a-z])|♭|di[eè]se|b[eé]mol)?",
    re.IGNORECASE,
)


class LiveError(Exception):
    """Live introuvable, nom invalide ou sample inutilisable."""


class LiveItem(BaseModel):
    """Un sample du live."""
    source: str                      # relatif a Samples/
    code: str
    branch: str                      # LIVE_BRANCHES
    name: str                        # nom DT2 voulu, sans extension (<= NAME_MAX)
    bank: str = ""                   # banque du live (ou KIT) ; vide : pas encore place (render_item).
                                     # Un sample peut figurer dans plusieurs banques (7.L6) : un item
                                     # par banque, identite (source, bank), nom / accordage / track propres
    track: int | None = None         # track 1-16 dans le kit (KIT seulement), unique
    ram: int | None = None           # octets en RAM DT2, None : en-tete illisible
    note: str | None = None          # note de la source (dieses), relevee a l'accordage
    shift: int = 0                   # demi-tons de varispeed appliques a l'export
    parent: str | None = None        # sample d'origine d'un rendu du sound design (8.L1)
    rumble: str | None = None        # preset du rumble genere pour la banque (8.L2)


class Live(BaseModel):
    name: str
    pack: str = ""                   # pack des samples maison du live (famille SAMPLE), ex. slr
    banks: list[str] = Field(default_factory=list)   # sans 0-KIT, toujours present
    keys: dict[str, str] = Field(default_factory=dict)  # tonalite saisie par banque (ex. A-HALF : Fa m)
    tempos: dict[str, float] = Field(default_factory=dict)  # BPM par banque (ecoute au clavier du front)
    # presets de rumble par banque (8.L2) : un rumble par kick de la banque et par
    # preset, au tempo de la banque ; banque absente = aucun rumble genere
    rumbles: dict[str, list[str]] = Field(default_factory=dict)
    items: list[LiveItem] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _migrate(cls, data: object) -> object:
        """Live d'avant 7.L5 (`banks` par item, 0-COMMON) : un sample de plusieurs
        banques donne un item par banque (7.L6), un sample de 0-COMMON rejoint la
        derniere banque du live ; tonalite, tempo et presets de 0-COMMON sont oublies."""
        if not isinstance(data, dict) or not isinstance(data.get("items"), list):
            return data
        banks = data.get("banks") or []
        last = banks[-1] if banks else None
        items = []
        for it in data["items"]:
            if isinstance(it, dict) and "banks" in it and "bank" not in it:
                old = [b for b in it["banks"] if b != LEGACY_COMMON] or ([last] if last else [])
                base = {k: v for k, v in it.items() if k not in ("banks", "folder")}
                items += [base | {"bank": b} for b in old]
                continue
            items.append(it)
        data = {**data, "items": items}
        for key in ("keys", "tempos", "rumbles"):
            if isinstance(data.get(key), dict):
                data[key] = {b: v for b, v in data[key].items() if b != LEGACY_COMMON}
        return data


class LiveFolder(BaseModel):
    path: str                        # <BANQUE> (ou KIT)
    files: int
    ram: int
    over_cap: bool
    branches: dict[str, int] = Field(default_factory=dict)   # fichiers par branche (filtre du panneau)


class LiveSummary(BaseModel):
    live: Live
    folders: list[LiveFolder]
    ram: int                         # somme des ram connues
    ram_limit: int = RAM_LIMIT
    unknown_ram: int = 0             # samples dont l'en-tete n'a pas ete lu


# --- Noms et fichiers ---------------------------------------------------------

def check_live_name(name: str) -> str:
    if not LIVE_NAME.fullmatch(name):
        raise LiveError(f"nom de live invalide : {name!r} (minuscules, chiffres, - et _)")
    return name


def check_bank(bank: str) -> str:
    if bank != KIT and not BANK_NAME.fullmatch(bank):
        raise LiveError(f"banque invalide : {bank!r} (ex. A-HALF)")
    return bank


def live_file(meta_dir: Path, name: str) -> Path:
    return meta_dir / f"{check_live_name(name)}.json"


def index_file(meta_dir: Path, name: str) -> Path:
    return meta_dir / f"{check_live_name(name)}{EXPORT_SUFFIX}"


def list_lives(meta_dir: Path) -> list[str]:
    if not meta_dir.is_dir():
        return []
    return sorted(p.stem for p in meta_dir.glob("*.json") if not p.name.endswith(EXPORT_SUFFIX))


def load_live(meta_dir: Path, name: str) -> Live:
    path = live_file(meta_dir, name)
    if not path.exists():
        raise LiveError(f"live inconnu : {name}")
    try:
        return Live.model_validate_json(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise LiveError(f"{path} : illisible ({exc})") from exc


def save_live(live: Live, meta_dir: Path) -> None:
    path = live_file(meta_dir, live.name)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = live.model_dump()
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    tmp.replace(path)


def ram_bytes(path: Path, shift: int = 0) -> int | None:
    """Place en RAM DT2 (48 kHz / 16 bits, canaux gardes), d'apres l'en-tete ;
    `shift` : demi-tons de varispeed (la duree est divisee par 2^(shift/12))."""
    try:
        info = sf.info(str(path))
    except (RuntimeError, OSError):
        return None
    if info.samplerate <= 0:
        return None
    frames = math.ceil(info.frames * DT2_RATE / info.samplerate / 2.0 ** (shift / 12.0))
    return frames * info.channels * DT2_SAMPLE_BYTES


# --- Operations ---------------------------------------------------------------

def create_live(meta_dir: Path, name: str, banks: list[str], pack: str = "") -> Live:
    if live_file(meta_dir, name).exists():
        raise LiveError(f"live deja existant : {name}")
    if pack and not PACK_NAME.fullmatch(pack):
        raise LiveError(f"pack invalide : {pack!r} (2 a 4 minuscules ou chiffres)")
    live = Live(name=name, pack=pack)
    set_banks(live, banks)
    return live


def set_banks(live: Live, banks: list[str]) -> None:
    """Fixe la liste ordonnee des banques. Un sample perd les banques retirees ;
    sans banque, il sort du live."""
    for b in banks:
        if b == KIT:
            raise LiveError(f"{KIT} est implicite, ne pas le lister")
        check_bank(b)
    if len(set(banks)) != len(banks):
        raise LiveError("banque en double")
    live.banks = list(banks)
    kept = set(banks) | {KIT}
    live.items = [it for it in live.items if it.bank in kept]
    live.keys = {b: k for b, k in live.keys.items() if b in kept}
    live.tempos = {b: t for b, t in live.tempos.items() if b in kept}
    live.rumbles = {b: p for b, p in live.rumbles.items() if b in kept}


def set_tempo(live: Live, bank: str, bpm: float | None) -> None:
    """Tempo d'une banque (ou du kit), arrondi au dixieme ; None : retire."""
    if bank != KIT and bank not in live.banks:
        raise LiveError(f"banque absente du live : {bank}")
    if bpm is None:
        live.tempos.pop(bank, None)
        return
    lo, hi = TEMPO_RANGE
    if not lo <= bpm <= hi:
        raise LiveError(f"tempo hors plage : {bpm} ({lo:g} a {hi:g} BPM)")
    live.tempos[bank] = round(bpm, 1)


def set_key(live: Live, bank: str, key: str) -> None:
    """Tonalite d'une banque du live (ou du kit) ; vide : retiree."""
    if bank != KIT and bank not in live.banks:
        raise LiveError(f"banque absente du live : {bank}")
    key = " ".join(key.split())
    if len(key) > KEY_MAX:
        raise LiveError(f"tonalite trop longue : {key!r} ({KEY_MAX} caracteres au plus)")
    if key:
        live.keys[bank] = key
    else:
        live.keys.pop(bank, None)


def set_rumbles(live: Live, bank: str, presets: list[str]) -> None:
    """Presets de rumble d'une banque (8.L2), dedoublonnes dans l'ordre donne,
    RUMBLE_PRESETS_MAX au plus ; vide : plus de rumble pour cette banque.
    Pas pour le kit : son rumble (track 2) se choisit a la main."""
    if bank not in live.banks:
        raise LiveError(f"banque absente du live : {bank}")
    ids = list(dict.fromkeys(p.strip() for p in presets if p.strip()))
    bad = [p for p in ids if not PRESET_ID.fullmatch(p)]
    if bad:
        raise LiveError(f"id de preset invalide : {', '.join(bad)}")
    if len(ids) > RUMBLE_PRESETS_MAX:
        raise LiveError(f"{len(ids)} presets pour {bank} ({RUMBLE_PRESETS_MAX} au plus)")
    if ids:
        live.rumbles[bank] = ids
    else:
        live.rumbles.pop(bank, None)


def key_root(key: str) -> str | None:
    """Tonique d'une tonalite saisie (`Fa m`, `sol mineur`, `Si bemol`, `F#m`,
    `Bb`), en dieses ; None si illisible."""
    m = _KEY_RX.match(key.strip())
    if m is None:
        return None
    fr = m["fr"]
    root = _SOLFEGE[fr.lower().replace("é", "e")] if fr else m["en"].upper()
    acc = (m["acc"] or "").lower()
    step = 1 if acc in ("#", "♯") or acc.startswith("di") else -1 if acc else 0
    return PITCH_CLASSES[(PITCH_CLASSES.index(root) + step) % 12]


def semitones(note: str, target: str) -> int:
    """Plus court decalage de `note` vers `target` (dieses), de -6 a +5 :
    a egalite on descend (un kick monte de 6 demi-tons perd sa queue)."""
    d = (PITCH_CLASSES.index(target) - PITCH_CLASSES.index(note)) % 12
    return d - 12 if d >= 6 else d


def transpose(note: str, shift: int) -> str:
    return PITCH_CLASSES[(PITCH_CLASSES.index(note) + shift) % 12]


def entry_note(manifest: Manifest, item: LiveItem) -> str | None:
    """Note connue sans mesure : manifeste, sinon nom du fichier (dieses)."""
    entry = _entry(manifest, item.source)
    if entry is not None and entry.note:
        return sharp(entry.note)
    written = name_note(item.source, item.code)
    return sharp(written) if written else None


def source_note(manifest: Manifest, item: LiveItem, root: Path) -> str | None:
    """Note de la source : celle du manifeste (lue ou mesuree), sinon lue dans
    le nom du fichier, sinon mesuree dans l'audio (BD / BS de la reserve, jamais
    mesures, mesure gardee dans `item.note`) ; None si la mesure est incertaine
    (RM : pas de mesure)."""
    known = entry_note(manifest, item)
    if known:
        return known
    if item.note:
        return item.note
    if item.code in PITCHED and (root / item.source).is_file():
        return measure_note(root / item.source, item.code)[0]
    return None


def _renote(name: str, old: str, new: str | None) -> str:
    """Remplace la note `old` d'un nom DT2 (`BD F Hard 01 k`) par `new`, apres
    le code et l'eventuel BPM ; `new` None : la retire. Sans note dans le nom,
    `new` est inseree apres le code (et le BPM), la description tronquee pour
    tenir dans NAME_MAX."""
    toks = name.split(" ")
    for i, t in enumerate(toks[1:3], 1):
        if t and t[0].isupper() and len(t) <= 2 and sharp(t) == old:
            if new is None:
                del toks[i]
            else:
                toks[i] = new
            return " ".join(toks)
    if new is None or len(toks) < 3:
        return name
    at = 2 if toks[1].isdigit() else 1
    toks.insert(at, new)
    over = len(" ".join(toks)) - NAME_MAX
    if over > 0:      # tronque la description (avant le numero de variante et le pack)
        words, num = toks[at + 1:-1], []
        if words and words[-1].isdigit():
            words, num = words[:-1], words[-1:]
        desc = " ".join(words)[:-over].rstrip()
        toks = [*toks[:at + 1], *([desc] if desc else []), *num, toks[-1]]
    return " ".join(toks)


def tune_bank(live: Live, manifest: Manifest, bank: str, root: Path,
              reset: bool = False) -> list[LiveItem]:
    """Accorde les TUNABLE d'une banque (ou du kit) sur la tonique de sa
    tonalite ; `reset` : les remet a leur hauteur d'origine. Renvoie les
    samples TUNABLE de la banque (accordes ou sans note connue)."""
    if bank != KIT and bank not in live.banks:
        raise LiveError(f"banque absente du live : {bank}")
    target = None
    if not reset:
        key = live.keys.get(bank, "")
        if not key:
            raise LiveError(f"{bank} n'a pas de tonalite : la saisir d'abord")
        target = key_root(key)
        if target is None:
            raise LiveError(f"tonalite illisible pour {bank} : {key!r} (ex. Fa m, F#m, sol)")
    touched = [it for it in live.items if it.bank == bank and it.code in TUNABLE]
    _tune_items(touched, manifest, target, root)
    return touched


def _tune_items(items: list[LiveItem], manifest: Manifest, target: str | None, root: Path) -> None:
    """Ramene `items` (TUNABLE) sur la tonique `target` ; None : hauteur d'origine."""
    for it in items:
        it.note = source_note(manifest, it, root)
        shift = semitones(it.note, target) if it.note and target else 0
        if shift == it.shift:
            continue
        if it.note:
            # note absente du nom d'origine (mesuree ici) : inseree, retiree au reset
            named = bool(entry_note(manifest, it))
            new = transpose(it.note, shift) if shift or named else None
            it.name = _renote(it.name, transpose(it.note, it.shift), new)
        it.shift = shift
        it.ram = ram_bytes(root / it.source, shift)


def bank_target(live: Live, bank: str) -> str | None:
    """Tonique de la banque si sa tonalite est saisie et lisible, sinon None
    (l'accordage explicite, lui, signale une tonalite illisible)."""
    key = live.keys.get(bank, "")
    return key_root(key) if key else None


def tune_live(live: Live, manifest: Manifest, root: Path, reset: bool = False) -> list[LiveItem]:
    """Accorde tout le live : chaque banque (kit compris) qui a une
    tonalite ; les samples d'une banque sans tonalite reprennent leur hauteur
    d'origine. `reset` : tout le live a sa hauteur d'origine. Tout ou rien :
    une tonalite illisible arrete avant toute modification."""
    rows = rows_of(live)
    if not reset:
        bad = [f"{b} ({live.keys[b]!r})" for b in rows if live.keys.get(b) and key_root(live.keys[b]) is None]
        if bad:
            raise LiveError(f"tonalite illisible : {', '.join(bad)} (ex. Fa m, F#m, sol)")
    touched: list[LiveItem] = []
    for b in rows:
        touched += tune_bank(live, manifest, b, root, reset=reset or not live.keys.get(b))
    return touched


def rows_of(live: Live) -> list[str]:
    """Dossiers du live dans l'ordre d'export : le kit, puis les banques."""
    return [KIT, *live.banks]


def _free_track(live: Live, code: str) -> int:
    """Track proposee pour un nouveau sample du kit : la premiere libre parmi
    celles de son code (KIT_TRACK_FOR), sinon la premiere libre du kit."""
    taken = {it.track for it in live.items if it.bank == KIT}
    for t in [*KIT_TRACK_FOR.get(code, ()), *range(1, KIT_TRACKS + 1)]:
        if t not in taken:
            return t
    raise LiveError(f"kit plein : {KIT_TRACKS} samples, retirer d'abord")


def _find(live: Live, source: str, bank: str) -> LiveItem | None:
    """Item d'un sample dans une banque : l'identite d'un item est (source, bank)."""
    return next((i for i in live.items if i.source == source and i.bank == bank), None)


def _only(live: Live, source: str, bank: str | None) -> LiveItem:
    """Item vise par (source, bank) ; sans `bank`, le seul item du sample dans
    le live (erreur s'il est dans plusieurs banques : preciser)."""
    if bank is not None:
        it = _find(live, source, bank)
        if it is None:
            raise LiveError(f"sample absent de {bank} : {source}")
        return it
    hits = [i for i in live.items if i.source == source]
    if not hits:
        raise LiveError(f"sample absent du live : {source}")
    if len(hits) > 1:
        raise LiveError(f"{source} est dans {len(hits)} banques ({', '.join(i.bank for i in hits)}) : preciser la banque")
    return hits[0]


def _place(live: Live, it: LiveItem, bank: str) -> None:
    """Met l'item neuf `it` dans `bank` ; dans le kit, la track est attribuee."""
    it.bank = bank
    it.track = _free_track(live, it.code) if bank == KIT else None
    live.items.append(it)


def set_track(live: Live, source: str, track: int) -> LiveItem:
    """Track d'un sample du kit (1 a KIT_TRACKS) ; une track deja prise est
    echangee avec l'occupant."""
    if not 1 <= track <= KIT_TRACKS:
        raise LiveError(f"track hors grille : {track} (1 a {KIT_TRACKS})")
    it = _find(live, source, KIT)
    if it is None:
        raise LiveError(f"sample absent du kit : {source}")
    other = next((i for i in live.items if i.bank == KIT and i.track == track), None)
    if other is not None and other is not it:
        other.track = it.track
    it.track = track
    return it


def _with_pack(name: str, pack: str) -> str:
    """Remplace le pack (dernier mot) d'un nom DT2, en tronquant la description."""
    head, _, _old = name.rpartition(" ")
    head = head[: NAME_MAX - len(pack) - 1].rstrip()
    return f"{head} {pack}"


def _new_item(live: Live, manifest: Manifest, source: str, root: Path) -> LiveItem:
    """Item d'un sample du catalogue, pas encore place (`_place`)."""
    entry = _entry(manifest, source)
    reserve = None if entry else _reserved(manifest, source)
    if entry is not None:
        family, code, name = entry.family, entry.code, entry.name
    elif reserve is not None:
        family, code = reserve.family, reserve.code
        name = short_name(reserve.source, reserve.code, reserve.pack, reserve.bpm)
    else:
        raise LiveError(f"sample hors catalogue classe (non classe, corbeille ou inconnu) : {source}")
    branch = branch_of("", code)
    if branch not in LIVE_BRANCHES:
        raise LiveError(f"code {code} sans branche de live : ranger d'abord {source} sous un code d'instrument")
    if family == "SAMPLE" and live.pack:
        name = _with_pack(name, live.pack)
    return LiveItem(source=source, code=code, branch=branch, name=name,
                    ram=ram_bytes(root / source), parent=entry.parent if entry else None)


def _copy_item(it: LiveItem) -> LiveItem:
    """Copie d'un item du live pour une autre banque : meme nom DT2, parent et
    preset, sans banque ni track ; l'accordage est refait pour la banque
    d'arrivee par `_tune_items` (hauteur d'origine si elle n'a pas de tonalite)."""
    return it.model_copy(update={"bank": "", "track": None})


def add(live: Live, manifest: Manifest, sources: list[str], bank: str, root: Path) -> None:
    """Ajoute des samples a une banque (ou au kit) ; un sample deja dans cette
    banque y reste, un sample d'une autre banque y est copie (7.L6 : un item
    par banque, accorde et nomme pour elle). Tout ou rien (catalogue, place
    dans le kit). Si la banque a une tonalite lisible, les TUNABLE ajoutes y
    sont accordes aussitot (comme `tune_bank`, sans attendre un reaccordage
    de la banque)."""
    if bank != KIT and bank not in live.banks:
        raise LiveError(f"banque absente du live : {bank}")
    wanted = [s for s in dict.fromkeys(sources) if _find(live, s, bank) is None]
    new: list[LiveItem] = []
    for s in wanted:
        elsewhere = next((i for i in live.items if i.source == s), None)
        # copie de l'item d'une autre banque (nom du live, rendu pas encore au
        # manifeste), sinon item neuf du catalogue
        new.append(_copy_item(elsewhere) if elsewhere is not None else _new_item(live, manifest, s, root))
    if bank == KIT:
        room = KIT_TRACKS - sum(1 for it in live.items if it.bank == KIT)
        if len(new) > room:
            raise LiveError(f"kit plein : {len(new)} a placer pour {room} track(s) libre(s) sur {KIT_TRACKS}")
    for it in new:
        _place(live, it, bank)
    # accordes sur la banque ; une copie accordee ailleurs reprend sa hauteur
    # d'origine si la banque n'a pas de tonalite ; un item neuf n'est pas mesure
    target = bank_target(live, bank)
    _tune_items([it for it in new if it.code in TUNABLE and (target or it.shift)], manifest, target, root)


def render_item(source: str, code: str, name: str, root: Path, parent: str | None,
                rumble: str | None = None) -> LiveItem:
    """Item d'un rendu du sound design verse (8.L2), construit depuis son
    sidecar sans attendre la reanalyse du manifeste (le nom DT2 est celui du
    rendu, la note s'y lit a l'accordage)."""
    branch = branch_of("", code)
    if branch not in LIVE_BRANCHES:
        raise LiveError(f"code {code} sans branche de live : {source}")
    return LiveItem(source=source, code=code, branch=branch, name=name,
                    ram=ram_bytes(root / source), parent=parent, rumble=rumble)


def add_item(live: Live, item: LiveItem, bank: str) -> tuple[LiveItem, bool]:
    """Ajoute `item` a `bank` (un item par banque : le meme rendu peut etre
    dans d'autres banques). Renvoie l'item du live et False s'il y etait deja."""
    if bank != KIT and bank not in live.banks:
        raise LiveError(f"banque absente du live : {bank}")
    it = _find(live, item.source, bank)
    if it is not None:
        return it, False
    _place(live, item, bank)
    return item, True


def untuned_name(item: LiveItem) -> str:
    """Nom DT2 de l'item avec sa note d'origine (avant accordage)."""
    if item.shift and item.note:
        return _renote(item.name, transpose(item.note, item.shift), item.note)
    return item.name


def inherit_tuning(item: LiveItem, parent: LiveItem, root: Path) -> None:
    """Un rendu issu de `parent` (rumble d'un kick accorde) prend sa note, son
    decalage et sa note affichee : il sort accorde comme lui a l'export."""
    if not parent.shift or not parent.note:
        return
    item.note = parent.note
    item.shift = parent.shift
    item.name = _renote(item.name, parent.note, transpose(parent.note, parent.shift))
    item.ram = ram_bytes(root / item.source, item.shift)


def remove(live: Live, sources: list[str], bank: str | None = None) -> None:
    """Retire des samples d'une banque, ou du live entier (`bank` None)."""
    wanted = set(sources)
    live.items = [it for it in live.items
                  if it.source not in wanted or (bank is not None and it.bank != bank)]


def rename(live: Live, source: str, name: str, bank: str | None = None) -> LiveItem:
    """Nom DT2 d'un item ; `bank` obligatoire si le sample est dans plusieurs banques."""
    name = " ".join(name.split())
    if not name or len(name) > NAME_MAX or "/" in name:
        raise LiveError(f"nom DT2 invalide : {name!r} ({NAME_MAX} caracteres au plus, sans /)")
    it = _only(live, source, bank)
    it.name = name
    return it


# --- Lecture et export ----------------------------------------------------------

class _NoCase(set[str]):
    """Noms deja pris, casse ignoree (disque macOS) : pour `unique_name`."""
    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and super().__contains__(name.lower())


def plan(live: Live) -> dict[str, str]:
    """Chemin d'arrivee (relatif au dossier du live) -> source, noms rendus
    uniques par banque."""
    return {rel: it.source for rel, it in _placed(live).items()}


def export_name(it: LiveItem) -> str:
    """Nom de fichier exporte, sans extension : dans le kit, le numero de track
    en tete (`01 BD F Kick 03 rth`), la description tronquee pour tenir dans
    NAME_MAX ; ailleurs le nom DT2."""
    if it.bank == KIT and it.track:
        return f"{it.track:02d} {it.name[:NAME_MAX - 3].rstrip()}"
    return it.name


def _placed(live: Live) -> dict[str, LiveItem]:
    out: dict[str, LiveItem] = {}
    taken: dict[str, _NoCase] = {}
    order = {b: i for i, b in enumerate(rows_of(live))}
    for it in sorted(live.items, key=lambda i: (order.get(i.bank, len(order)), i.track or 0,
                                                LIVE_BRANCHES.index(i.branch), i.name, i.source)):
        seen = taken.setdefault(it.bank, _NoCase())
        name = unique_name(export_name(it), seen)
        seen.add(name.lower())
        out[f"{it.bank}/{name}.wav"] = it
    return out


def summary(live: Live) -> LiveSummary:
    folders: dict[str, LiveFolder] = {}
    unknown = 0
    for it in live.items:
        f = folders.setdefault(it.bank, LiveFolder(path=it.bank, files=0, ram=0, over_cap=False))
        f.files += 1
        f.ram += it.ram or 0
        f.branches[it.branch] = f.branches.get(it.branch, 0) + 1
        unknown += it.ram is None
    order = {b: i for i, b in enumerate(rows_of(live))}
    rows = sorted(folders.values(), key=lambda f: order.get(f.path, len(order)))
    for f in rows:
        f.over_cap = f.files > (KIT_TRACKS if f.path == KIT else LIVE_CAP)
    return LiveSummary(live=live, folders=rows, ram=sum(f.ram for f in rows), unknown_ram=unknown)


def export_live(live: Live, root: Path, dest_root: Path, meta_dir: Path,
                dry_run: bool = False) -> ExportReport:
    """Synchronise `<dest_root>/<live>/` avec le live (voir l'en-tete)."""
    try:
        placed = _placed(live)
        shifts = {rel: it.shift for rel, it in placed.items() if it.shift}
        return sync({rel: it.source for rel, it in placed.items()}, root, dest_root / live.name,
                    index_file(meta_dir, live.name), dry_run, shifts)
    except SampleError as exc:
        raise LiveError(str(exc)) from exc

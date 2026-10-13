"""Lives DT2 (Phase 7.L) : selection de samples de la lib rangee par banque.

La lib (7.J) range par type pour chercher ; un live range par banque pour
jouer. Un live est un fichier `<LIVES_META_DIR>/<live>.json` : ses banques
(une par section, ex. `A-HALF`), et pour chaque sample retenu sa source, sa
branche (DRUMS, TONAL, LOOPS, FX, VX), son nom DT2 et les banques qui
l'utilisent. Il est independant des decisions keep / drop de la lib : la
source est tout le catalogue classe (candidats et reserve).

Arbre de l'export, que Transfer envoie sur le +Drive :
`<DT2_LIVES_DIR>/<live>/<BANQUE>/<BRANCHE>/<nom>.wav`. Un sample utilise par
deux banques ou plus va dans `0-COMMON` (jamais duplique). Pas de dossier
par code : le prefixe du nom regroupe au tri alphabetique. Plafond de
LIVE_CAP fichiers par dossier, en simple avertissement.

RAM : la DT2 charge les samples en 48 kHz / 16 bits, 400 Mo par projet
(manuel §9.1). La place d'un sample est estimee a ce format (Transfer
convertit a l'envoi), pas d'apres la taille du fichier source ; elle est
mesuree a l'ajout (en-tete seul) et gardee dans le live.

Export rejouable : meme copie que l'export de la lib (`samples.sync`), avec
un index propre au live (`<live>.export.json`).

Accordage par banque : les kicks, rumbles et basses (TUNABLE) d'une banque
dont la note est connue sont ramenes sur la tonique de sa tonalite, par le
plus court chemin (-6 a +5 demi-tons). Le decalage est garde dans le live et
applique a l'export en varispeed (comme le pitch de la DT2 : la duree suit) ;
la lib n'est pas touchee. 0-COMMON n'est accorde que sur sa propre tonalite.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

import soundfile as sf
from pydantic import BaseModel, Field, computed_field

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

COMMON = "0-COMMON"
LIVE_CAP = 64                    # fichiers par dossier <BANQUE>/<BRANCHE>
LIVE_BRANCHES = ("DRUMS", "TONAL", "LOOPS", "FX", "VX")
DT2_RATE = 48_000
DT2_SAMPLE_BYTES = 2             # 16 bits
RAM_LIMIT = 400_000_000          # 400 Mo par projet (manuel §9.1)
LIVE_NAME = re.compile(r"[a-z0-9][a-z0-9_-]{0,31}")
BANK_NAME = re.compile(r"[A-Z1-9][A-Z0-9-]{0,15}")   # 0-... reserve a 0-COMMON
PACK_NAME = re.compile(r"[a-z0-9]{2,4}")
KEY_MAX = 12                     # tonalite d'une banque, texte libre (Fa m, sol mineur)
TEMPO_RANGE = (30.0, 300.0)      # BPM de la DT2
EXPORT_SUFFIX = ".export.json"
TUNABLE = frozenset({"BD", "RM", "BS"})   # one-shots accordes sur la tonique de la banque
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
    banks: list[str]                 # banques qui l'utilisent, dans l'ordre du live
    ram: int | None = None           # octets en RAM DT2, None : en-tete illisible
    note: str | None = None          # note de la source (dieses), relevee a l'accordage
    shift: int = 0                   # demi-tons de varispeed appliques a l'export

    @computed_field  # type: ignore[prop-decorator]
    @property
    def folder(self) -> str:
        """Banque d'arrivee : 0-COMMON des que le sample sert a plusieurs banques."""
        return COMMON if COMMON in self.banks or len(self.banks) > 1 else self.banks[0]


class Live(BaseModel):
    name: str
    pack: str = ""                   # pack des samples maison du live (famille SAMPLE), ex. slr
    banks: list[str] = Field(default_factory=list)   # sans 0-COMMON, toujours present
    keys: dict[str, str] = Field(default_factory=dict)  # tonalite saisie par banque (ex. A-HALF : Fa m)
    tempos: dict[str, float] = Field(default_factory=dict)  # BPM par banque (ecoute au clavier du front)
    items: list[LiveItem] = Field(default_factory=list)


class LiveFolder(BaseModel):
    path: str                        # <BANQUE>/<BRANCHE>
    files: int
    ram: int
    over_cap: bool


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
    if bank != COMMON and not BANK_NAME.fullmatch(bank):
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
    data = live.model_dump(exclude={"items": {"__all__": {"folder"}}})
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
        if b == COMMON:
            raise LiveError(f"{COMMON} est implicite, ne pas le lister")
        check_bank(b)
    if len(set(banks)) != len(banks):
        raise LiveError("banque en double")
    live.banks = list(banks)
    kept = set(banks) | {COMMON}
    for it in live.items:
        it.banks = _ordered(live, [b for b in it.banks if b in kept])
    live.items = [it for it in live.items if it.banks]
    live.keys = {b: k for b, k in live.keys.items() if b in kept}
    live.tempos = {b: t for b, t in live.tempos.items() if b in kept}


def set_tempo(live: Live, bank: str, bpm: float | None) -> None:
    """Tempo d'une banque (ou de 0-COMMON), arrondi au dixieme ; None : retire."""
    if bank != COMMON and bank not in live.banks:
        raise LiveError(f"banque absente du live : {bank}")
    if bpm is None:
        live.tempos.pop(bank, None)
        return
    lo, hi = TEMPO_RANGE
    if not lo <= bpm <= hi:
        raise LiveError(f"tempo hors plage : {bpm} ({lo:g} a {hi:g} BPM)")
    live.tempos[bank] = round(bpm, 1)


def set_key(live: Live, bank: str, key: str) -> None:
    """Tonalite d'une banque du live (ou de 0-COMMON) ; vide : retiree."""
    if bank != COMMON and bank not in live.banks:
        raise LiveError(f"banque absente du live : {bank}")
    key = " ".join(key.split())
    if len(key) > KEY_MAX:
        raise LiveError(f"tonalite trop longue : {key!r} ({KEY_MAX} caracteres au plus)")
    if key:
        live.keys[bank] = key
    else:
        live.keys.pop(bank, None)


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
    """Accorde les TUNABLE d'une banque (ou de 0-COMMON) sur la tonique de sa
    tonalite ; `reset` : les remet a leur hauteur d'origine. Renvoie les
    samples TUNABLE de la banque (accordes ou sans note connue)."""
    if bank != COMMON and bank not in live.banks:
        raise LiveError(f"banque absente du live : {bank}")
    target = None
    if not reset:
        key = live.keys.get(bank, "")
        if not key:
            raise LiveError(f"{bank} n'a pas de tonalite : la saisir d'abord")
        target = key_root(key)
        if target is None:
            raise LiveError(f"tonalite illisible pour {bank} : {key!r} (ex. Fa m, F#m, sol)")
    touched = [it for it in live.items if it.folder == bank and it.code in TUNABLE]
    for it in touched:
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
    return touched


def _ordered(live: Live, banks: list[str]) -> list[str]:
    order = {b: i for i, b in enumerate([COMMON, *live.banks])}
    return sorted(set(banks), key=lambda b: order[b])


def _with_pack(name: str, pack: str) -> str:
    """Remplace le pack (dernier mot) d'un nom DT2, en tronquant la description."""
    head, _, _old = name.rpartition(" ")
    head = head[: NAME_MAX - len(pack) - 1].rstrip()
    return f"{head} {pack}"


def _new_item(live: Live, manifest: Manifest, source: str, root: Path) -> LiveItem:
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
    return LiveItem(source=source, code=code, branch=branch, name=name, banks=[],
                    ram=ram_bytes(root / source))


def add(live: Live, manifest: Manifest, sources: list[str], bank: str, root: Path) -> None:
    """Ajoute des samples a une banque (ou a 0-COMMON) ; tout ou rien."""
    if bank != COMMON and bank not in live.banks:
        raise LiveError(f"banque absente du live : {bank}")
    by_source = {it.source: it for it in live.items}
    new = [_new_item(live, manifest, s, root) for s in dict.fromkeys(sources) if s not in by_source]
    for it in new:
        live.items.append(it)
        by_source[it.source] = it
    for s in sources:
        it = by_source[s]
        it.banks = _ordered(live, [*it.banks, bank])


def remove(live: Live, sources: list[str], bank: str | None = None) -> None:
    """Retire des samples d'une banque, ou du live entier (`bank` None)."""
    wanted = set(sources)
    for it in live.items:
        if it.source in wanted:
            it.banks = [] if bank is None else [b for b in it.banks if b != bank]
    live.items = [it for it in live.items if it.banks]


def rename(live: Live, source: str, name: str) -> LiveItem:
    name = " ".join(name.split())
    if not name or len(name) > NAME_MAX or "/" in name:
        raise LiveError(f"nom DT2 invalide : {name!r} ({NAME_MAX} caracteres au plus, sans /)")
    it = next((i for i in live.items if i.source == source), None)
    if it is None:
        raise LiveError(f"sample absent du live : {source}")
    it.name = name
    return it


# --- Lecture et export ----------------------------------------------------------

class _NoCase(set[str]):
    """Noms deja pris, casse ignoree (disque macOS) : pour `unique_name`."""
    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and super().__contains__(name.lower())


def plan(live: Live) -> dict[str, str]:
    """Chemin d'arrivee (relatif au dossier du live) -> source, noms rendus
    uniques par dossier."""
    return {rel: it.source for rel, it in _placed(live).items()}


def _placed(live: Live) -> dict[str, LiveItem]:
    out: dict[str, LiveItem] = {}
    taken: dict[str, _NoCase] = {}
    for it in sorted(live.items, key=lambda i: (i.folder, i.branch, i.name, i.source)):
        folder = f"{it.folder}/{it.branch}"
        seen = taken.setdefault(folder, _NoCase())
        name = unique_name(it.name, seen)
        seen.add(name.lower())
        out[f"{folder}/{name}.wav"] = it
    return out


def summary(live: Live) -> LiveSummary:
    folders: dict[str, LiveFolder] = {}
    unknown = 0
    for it in live.items:
        path = f"{it.folder}/{it.branch}"
        f = folders.setdefault(path, LiveFolder(path=path, files=0, ram=0, over_cap=False))
        f.files += 1
        f.ram += it.ram or 0
        unknown += it.ram is None
    order = {b: i for i, b in enumerate([COMMON, *live.banks])}
    rows = sorted(folders.values(), key=lambda f: (order.get(f.path.split("/")[0], len(order)),
                                                  LIVE_BRANCHES.index(f.path.split("/")[1])))
    for f in rows:
        f.over_cap = f.files > LIVE_CAP
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

"""Detection de doublons dans la library.

Strategie :
- Normalise artist + title (retire "(Original Mix)", "(Remix)", "feat. X" etc.)
- Regroupe par signature normalisee
- Au sein d'un groupe : tri par quality_score decroissant -> meilleure version en tete
"""
from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass

_VERSION_SUFFIX_RE = re.compile(
    r"\s*[\(\[](?:original\s+mix|extended\s+mix|club\s+mix|"
    r"radio\s+(?:edit|mix)|edit|mix|version|vip|hd|hq|"
    r"official\s+(?:audio|video|music\s+video)|"
    r"\d{4})\s*[\)\]]\s*$",
    re.IGNORECASE,
)
_FEAT_RE = re.compile(r"\s+(?:feat|ft|featuring)\.?\s+.+$", re.IGNORECASE)
_TRAILING_TAG_RE = re.compile(r"\s*[\[\(][^\]\)]{1,30}[\]\)]\s*$")


def _normalize(value: str) -> str:
    s = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    s = _VERSION_SUFFIX_RE.sub("", s)
    s = _TRAILING_TAG_RE.sub("", s)
    s = _FEAT_RE.sub("", s)
    s = re.sub(r"[^\w\s]", "", s).strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def signature(artist: str, title: str) -> str:
    """Signature normalisee artist + title pour regroupement."""
    return f"{_normalize(artist)}|{_normalize(title)}"


@dataclass
class DuplicateGroup:
    signature: str
    entries: list[tuple[str, dict[str, str]]]  # (slug, fields)


def _quality(fields: dict[str, str]) -> float:
    try:
        return float(fields.get("quality_score", "0") or 0)
    except ValueError:
        return 0.0


def find_duplicates(
    entries: dict[str, dict[str, str]],
) -> list[DuplicateGroup]:
    """Regroupe les entrees library.md par signature normalisee.

    Retourne uniquement les groupes contenant >= 2 entrees. Au sein
    de chaque groupe, tri par quality_score decroissant."""
    by_sig: dict[str, list[tuple[str, dict[str, str]]]] = defaultdict(list)
    for slug, fields in entries.items():
        sig = signature(fields.get("artist", ""), fields.get("title", ""))
        by_sig[sig].append((slug, fields))

    groups: list[DuplicateGroup] = []
    for sig, members in by_sig.items():
        if len(members) < 2:
            continue
        members.sort(key=lambda kv: -_quality(kv[1]))
        groups.append(DuplicateGroup(signature=sig, entries=members))
    return groups

"""Rapports HID de la Maschine MK2 : décodage des entrées, LED, accès au périphérique.

Format repris de cabl (shaduzlabs, MIT), `src/devices/ni/MaschineMK2.cpp`,
à confirmer sur la machine au spike de la slice 0 :

- entrée 0x01 (25 octets) : 7 octets de boutons (bit n = bouton n), encodeur
  maître sur 4 bits à l'octet 8, puis 8 encodeurs sur 10 bits (LE) aux octets 9-24 ;
- entrée 0x20 (65 octets) : 16 couples (bas, haut), pad = haut >> 4,
  pression = ((haut & 0x0F) << 8) | bas, sur 12 bits ;
- sortie 0x80 : LED des pads, RGB, dans l'ordre des index de pad ;
- sortie 0x81 : LED des groupes A-H (2 LED RGB chacun, 6 octets) puis
  RESTART… SHIFT (index 48-55) ;
- sortie 0x82 : LED des boutons, une valeur par bouton.
"""

from __future__ import annotations

import sys
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Any, Protocol

VENDOR_ID = 0x17CC
PRODUCT_ID = 0x1140

REPORT_BUTTONS = 0x01
REPORT_PADS = 0x20
REPORT_LED_PADS = 0x80
REPORT_LED_GROUPS = 0x81
REPORT_LED_BUTTONS = 0x82

BUTTONS_REPORT_LEN = 25
PADS_REPORT_LEN = 65
LED_PADS_LEN = 49
LED_GROUPS_LEN = 57
LED_BUTTONS_LEN = 32

N_PADS = 16
N_ENCODERS = 8
ENCODER_RANGE = 1024  # 10 bits
MASTER_RANGE = 16  # 4 bits
PAD_THRESHOLD = 200  # sur 4095, valeur de cabl

LED_MAX = 0xFF

# Index de bit dans le rapport 0x01 (ordre de l'enum Button de cabl).
BUTTONS: tuple[str, ...] = (
    "DISPLAY_1", "DISPLAY_2", "DISPLAY_3", "DISPLAY_4",
    "DISPLAY_5", "DISPLAY_6", "DISPLAY_7", "DISPLAY_8",
    "CONTROL", "STEP", "BROWSE", "SAMPLING",
    "BROWSE_LEFT", "BROWSE_RIGHT", "ALL", "AUTO_WRITE",
    "VOLUME", "SWING", "TEMPO", "MASTER_LEFT",
    "MASTER_RIGHT", "ENTER", "NOTE_REPEAT", "MASTER_PUSH",  # « Main » chez cabl = appui maître
    "GROUP_A", "GROUP_B", "GROUP_C", "GROUP_D",
    "GROUP_E", "GROUP_F", "GROUP_G", "GROUP_H",
    "RESTART", "TRANSPORT_LEFT", "TRANSPORT_RIGHT", "GRID",
    "PLAY", "REC", "ERASE", "SHIFT",
    "SCENE", "PATTERN", "PAD_MODE", "NAVIGATE",
    "DUPLICATE", "SELECT", "SOLO", "MUTE",
)  # fmt: skip

# Index dans le rapport 0x82 (LED de boutons, enum Led de cabl 0-30).
_BUTTON_LED_ORDER: tuple[str, ...] = (
    "CONTROL", "STEP", "BROWSE", "SAMPLING",
    "BROWSE_LEFT", "BROWSE_RIGHT", "ALL", "AUTO_WRITE",
    "DISPLAY_1", "DISPLAY_2", "DISPLAY_3", "DISPLAY_4",
    "DISPLAY_5", "DISPLAY_6", "DISPLAY_7", "DISPLAY_8",
    "SCENE", "PATTERN", "PAD_MODE", "NAVIGATE",
    "DUPLICATE", "SELECT", "SOLO", "MUTE",
    "VOLUME", "SWING", "TEMPO", "MASTER_LEFT",
    "MASTER_RIGHT", "ENTER", "NOTE_REPEAT",
)  # fmt: skip
BUTTON_LEDS: dict[str, int] = {name: i for i, name in enumerate(_BUTTON_LED_ORDER)}

# Index dans le rapport 0x81 pour les boutons monochromes du transport.
TRANSPORT_LEDS: dict[str, int] = {
    name: 48 + i
    for i, name in enumerate(
        ("RESTART", "TRANSPORT_LEFT", "TRANSPORT_RIGHT", "GRID", "PLAY", "REC", "ERASE", "SHIFT")
    )
}

GROUPS = "ABCDEFGH"

RGB = tuple[int, int, int]


class Mk2Error(Exception):
    """Erreur liée à la Maschine MK2."""


class Mk2NotFoundError(Mk2Error):
    """Aucune MK2 n'est visible en HID."""


class Mk2OpenError(Mk2Error):
    """La MK2 est visible mais ne s'ouvre pas (pilote NI qui la tient ?)."""


class Mk2ReportError(Mk2Error):
    """Rapport HID inattendu (longueur, identifiant)."""


def pad_label(index: int) -> int:
    """Numéro imprimé du pad (1 en bas à gauche) depuis l'index du rapport.

    L index 0 est le pad 13 (en haut à gauche), vérifié le 2026-11-09.
    """
    if not 0 <= index < N_PADS:
        raise Mk2ReportError(f"index de pad hors bornes : {index}")
    return (3 - index // 4) * 4 + index % 4 + 1


# --- Évènements ----------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ButtonEvent:
    name: str
    pressed: bool


@dataclass(frozen=True, slots=True)
class EncoderEvent:
    """`index` 0 = encodeur maître, 1-8 = encodeurs sous les écrans."""

    index: int
    delta: int
    raw: int


@dataclass(frozen=True, slots=True)
class PadEvent:
    index: int
    pressed: bool
    pressure: int


Event = ButtonEvent | EncoderEvent | PadEvent


def _wrap_delta(old: int, new: int, span: int) -> int:
    """Écart signé le plus court entre deux lectures d'un compteur qui boucle."""
    return (new - old + span // 2) % span - span // 2


class InputDecoder:
    """Transforme les rapports bruts en évènements, en gardant l'état précédent.

    Première lecture des encodeurs : sert de référence, aucun évènement.
    """

    def __init__(self, pad_threshold: int = PAD_THRESHOLD) -> None:
        self.pad_threshold = pad_threshold
        self._buttons = 0
        self._encoders: list[int] | None = None
        self._pads = [False] * N_PADS

    def feed(self, report: bytes | Sequence[int]) -> list[Event]:
        data = bytes(report)
        if not data:
            return []
        if data[0] == REPORT_BUTTONS:
            return list(self._buttons_report(data))
        if data[0] == REPORT_PADS:
            return list(self._pads_report(data))
        return []

    def _buttons_report(self, data: bytes) -> Iterator[Event]:
        if len(data) < BUTTONS_REPORT_LEN:
            raise Mk2ReportError(f"rapport boutons trop court : {len(data)} octets")
        bits = int.from_bytes(data[1:7], "little")
        changed = bits ^ self._buttons
        for i, name in enumerate(BUTTONS):
            if changed >> i & 1:
                yield ButtonEvent(name, bool(bits >> i & 1))
        self._buttons = bits

        values = [data[8] & 0x0F] + [
            data[9 + 2 * k] | (data[10 + 2 * k] & 0x03) << 8 for k in range(N_ENCODERS)
        ]
        if self._encoders is not None:
            for i, (old, new) in enumerate(zip(self._encoders, values, strict=True)):
                if old != new:
                    span = MASTER_RANGE if i == 0 else ENCODER_RANGE
                    yield EncoderEvent(i, _wrap_delta(old, new, span), new)
        self._encoders = values

    def _pads_report(self, data: bytes) -> Iterator[Event]:
        if len(data) < 1 + 2 * N_PADS:
            raise Mk2ReportError(f"rapport pads trop court : {len(data)} octets")
        for k in range(N_PADS):
            low, high = data[1 + 2 * k], data[2 + 2 * k]
            pad = high >> 4
            pressure = (high & 0x0F) << 8 | low
            pressed = pressure > self.pad_threshold
            if pressed:
                yield PadEvent(pad, True, pressure)
            elif self._pads[pad]:
                yield PadEvent(pad, False, 0)
            self._pads[pad] = pressed


# --- LED -------------------------------------------------------------------------


@dataclass
class LedState:
    """Image complète des LED ; `reports()` rend les trois rapports de sortie."""

    pads: list[RGB]
    groups: list[RGB]
    buttons: dict[str, int]

    @classmethod
    def off(cls) -> LedState:
        return cls(pads=[(0, 0, 0)] * N_PADS, groups=[(0, 0, 0)] * len(GROUPS), buttons={})

    def reports(self) -> list[bytes]:
        pads = bytearray(LED_PADS_LEN)
        for i, rgb in enumerate(self.pads):
            pads[3 * i : 3 * i + 3] = bytes(rgb)

        groups = bytearray(LED_GROUPS_LEN)
        for i, rgb in enumerate(self.groups):
            groups[6 * i : 6 * i + 6] = bytes(rgb) * 2

        buttons = bytearray(LED_BUTTONS_LEN)
        for name, value in self.buttons.items():
            if name in BUTTON_LEDS:
                buttons[BUTTON_LEDS[name]] = value
            elif name in TRANSPORT_LEDS:
                groups[TRANSPORT_LEDS[name]] = value
            # sinon : bouton sans LED (MASTER_PUSH, GROUP_x géré à part)

        return [
            bytes([REPORT_LED_PADS]) + pads,
            bytes([REPORT_LED_GROUPS]) + groups,
            bytes([REPORT_LED_BUTTONS]) + buttons,
        ]


# --- Périphérique ------------------------------------------------------------------


class HidHandle(Protocol):
    def write(self, data: list[int]) -> int: ...
    def read(self, max_length: int, timeout_ms: int = 0) -> list[int]: ...
    def get_input_report(self, report_num: int, max_length: int) -> list[int]: ...
    def close(self) -> None: ...


def _hid_module() -> Any:
    """Module hidapi : backend hidraw sur Linux (requis par GET_REPORT), natif ailleurs."""
    if sys.platform.startswith("linux"):
        import hidraw

        return hidraw
    import hid

    return hid


def enumerate_mk2() -> list[dict[str, Any]]:
    return list(_hid_module().enumerate(VENDOR_ID, PRODUCT_ID))


class Mk2Device:
    """Accès HID à la MK2 (hidapi), mêmes appels sur Mac et sur Linux.

    `poll_buttons` : sur le Pi, la MK2 n'émet jamais le rapport 0x01 par
    interruption (constat du 2026-11-11, SPEC § Constats HID) ; l'état des
    boutons et des encodeurs est alors demandé par GET_REPORT après chaque
    lecture, et rendu comme un rapport 0x01 quand il a changé.
    """

    def __init__(self, handle: HidHandle, *, poll_buttons: bool = False) -> None:
        self._h = handle
        self._poll_buttons = poll_buttons
        self._last_buttons: bytes | None = None
        self._pending: bytes | None = None

    @classmethod
    def open(cls) -> Mk2Device:
        infos = enumerate_mk2()
        if not infos:
            raise Mk2NotFoundError(
                f"aucune MK2 en HID ({VENDOR_ID:04x}:{PRODUCT_ID:04x}) : câble, alimentation ?"
            )
        dev = _hid_module().device()
        try:
            dev.open_path(infos[0]["path"])
        except OSError as exc:
            raise Mk2OpenError(
                "MK2 visible mais impossible à ouvrir : NIHardwareAgent la tient "
                "peut-être, ou macOS refuse l'accès (Surveillance de l'entrée)"
            ) from exc
        return cls(dev, poll_buttons=sys.platform.startswith("linux"))

    def write(self, report: bytes) -> None:
        n = self._h.write(list(report))
        if n < 0:
            raise Mk2Error(f"écriture HID refusée (rapport 0x{report[0]:02x}, {len(report)} o)")

    def read(self, timeout_ms: int = 5) -> bytes:
        if self._pending is not None:
            report, self._pending = self._pending, None
            return report
        report = bytes(self._h.read(128, timeout_ms))
        if not self._poll_buttons:
            return report
        buttons = self._poll()
        if buttons is None:
            return report
        if not report:
            return buttons
        self._pending = buttons
        return report

    def _poll(self) -> bytes | None:
        """État 0x01 demandé à la MK2, rendu seulement s'il a changé."""
        try:
            state = bytes(self._h.get_input_report(REPORT_BUTTONS, BUTTONS_REPORT_LEN))
        except OSError as exc:
            raise Mk2Error("lecture de l'état des boutons refusée (GET_REPORT 0x01)") from exc
        if len(state) < BUTTONS_REPORT_LEN or state == self._last_buttons:
            return None
        self._last_buttons = state
        return state

    def send_leds(self, leds: LedState) -> None:
        for report in leds.reports():
            self.write(report)

    def close(self) -> None:
        self._h.close()

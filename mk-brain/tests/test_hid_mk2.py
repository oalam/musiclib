from __future__ import annotations

import pytest

from mk_brain.hid_mk2 import (
    BUTTONS,
    BUTTONS_REPORT_LEN,
    LED_BUTTONS_LEN,
    LED_GROUPS_LEN,
    LED_PADS_LEN,
    REPORT_BUTTONS,
    REPORT_PADS,
    ButtonEvent,
    EncoderEvent,
    InputDecoder,
    LedState,
    Mk2Device,
    Mk2ReportError,
    PadEvent,
    pad_label,
)


def buttons_report(bits: int = 0, master: int = 0, encoders: list[int] | None = None) -> bytes:
    enc = encoders or [0] * 8
    data = bytearray(BUTTONS_REPORT_LEN)
    data[0] = 0x01
    data[1:7] = bits.to_bytes(6, "little")
    data[8] = master
    for k, v in enumerate(enc):
        data[9 + 2 * k] = v & 0xFF
        data[10 + 2 * k] = v >> 8
    return bytes(data)


def pads_report(pressures: dict[int, int]) -> bytes:
    data = bytearray(65)
    data[0] = 0x20
    for k in range(16):
        v = pressures.get(k, 0)
        data[1 + 2 * k] = v & 0xFF
        data[2 + 2 * k] = (k << 4) | (v >> 8)
    return bytes(data)


def test_button_press_and_release() -> None:
    dec = InputDecoder()
    shift = BUTTONS.index("SHIFT")
    assert dec.feed(buttons_report(1 << shift)) == [ButtonEvent("SHIFT", True)]
    assert dec.feed(buttons_report(1 << shift)) == []
    assert dec.feed(buttons_report(0)) == [ButtonEvent("SHIFT", False)]


def test_first_encoder_read_is_reference_only() -> None:
    dec = InputDecoder()
    assert dec.feed(buttons_report(encoders=[500] * 8)) == []


def test_encoder_wraps_both_ways() -> None:
    dec = InputDecoder()
    dec.feed(buttons_report(master=15, encoders=[1023] + [0] * 7))
    events = dec.feed(buttons_report(master=0, encoders=[1] + [1022] + [0] * 6))
    assert events == [
        EncoderEvent(0, 1, 0),  # 15 -> 0 : +1
        EncoderEvent(1, 2, 1),  # 1023 -> 1 : +2
        EncoderEvent(2, -2, 1022),  # 0 -> 1022 : -2
    ]


def test_pad_threshold_and_release() -> None:
    dec = InputDecoder(pad_threshold=200)
    assert dec.feed(pads_report({3: 150})) == []
    assert dec.feed(pads_report({3: 2000})) == [PadEvent(3, True, 2000)]
    assert dec.feed(pads_report({})) == [PadEvent(3, False, 0)]
    assert dec.feed(pads_report({})) == []


def test_short_report_raises() -> None:
    with pytest.raises(Mk2ReportError):
        InputDecoder().feed(b"\x01\x00")


def test_unknown_report_ignored() -> None:
    assert InputDecoder().feed(b"\x99\x00\x00") == []


def test_pad_label_follows_cabl_layout() -> None:
    assert [pad_label(i) for i in (0, 3, 4, 12, 15)] == [13, 16, 9, 1, 4]
    with pytest.raises(Mk2ReportError):
        pad_label(16)


def test_led_reports_layout() -> None:
    leds = LedState.off()
    leds.pads[1] = (1, 2, 3)
    leds.groups[2] = (9, 8, 7)
    leds.buttons.update({"CONTROL": 255, "NOTE_REPEAT": 10, "SHIFT": 5, "MASTER_PUSH": 99})
    pads, groups, buttons = leds.reports()
    assert (pads[0], len(pads)) == (0x80, 1 + LED_PADS_LEN)
    assert pads[1 + 3 : 1 + 6] == bytes([1, 2, 3])
    assert (groups[0], len(groups)) == (0x81, 1 + LED_GROUPS_LEN)
    assert groups[1 + 12 : 1 + 18] == bytes([9, 8, 7, 9, 8, 7])
    assert groups[1 + 55] == 5  # SHIFT
    assert (buttons[0], len(buttons)) == (0x82, 1 + LED_BUTTONS_LEN)
    assert buttons[1 + 0] == 255 and buttons[1 + 30] == 10


class _FakeHandle:
    """Poignée hidapi factice : file de rapports d'interruption + état 0x01 interrogeable."""

    def __init__(self, reads: list[bytes], state: bytes) -> None:
        self.reads = list(reads)
        self.state = state
        self.polls = 0

    def write(self, data: list[int]) -> int:
        return len(data)

    def read(self, max_length: int, timeout_ms: int = 0) -> list[int]:
        return list(self.reads.pop(0)) if self.reads else []

    def get_input_report(self, report_num: int, max_length: int) -> list[int]:
        self.polls += 1
        return list(self.state)

    def close(self) -> None:
        pass


def _state(first_button_byte: int = 0) -> bytes:
    return bytes([REPORT_BUTTONS, first_button_byte]) + bytes(BUTTONS_REPORT_LEN - 2)


def test_device_without_poll_never_asks_state() -> None:
    handle = _FakeHandle([b"\x20" + bytes(64)], _state())
    dev = Mk2Device(handle)
    assert dev.read()[0] == REPORT_PADS
    assert dev.read() == b""
    assert handle.polls == 0


def test_device_poll_returns_state_only_on_change() -> None:
    handle = _FakeHandle([], _state())
    dev = Mk2Device(handle, poll_buttons=True)
    assert dev.read() == _state()  # premier état : référence du décodeur
    assert dev.read() == b""
    handle.state = _state(0x01)
    assert dev.read() == _state(0x01)
    assert dev.read() == b""


def test_device_poll_keeps_pad_report_and_queues_state() -> None:
    pads = b"\x20" + bytes(64)
    handle = _FakeHandle([pads], _state(0x02))
    dev = Mk2Device(handle, poll_buttons=True)
    assert dev.read() == pads
    assert dev.read() == _state(0x02)
    assert handle.polls == 1  # le rapport en attente sort sans nouvelle interrogation


def test_device_poll_ignores_short_state() -> None:
    handle = _FakeHandle([], b"\x01\x00")
    dev = Mk2Device(handle, poll_buttons=True)
    assert dev.read() == b""

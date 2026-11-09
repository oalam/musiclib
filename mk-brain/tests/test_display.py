from __future__ import annotations

import pytest

from mk_brain.display import (
    FRAME_BYTES,
    DisplayError,
    frame_reports,
    image_to_frame,
    mire,
    new_image,
)


def test_pixel_packing_msb_left() -> None:
    img = new_image()
    img.putpixel((0, 0), 1)
    img.putpixel((9, 1), 1)
    frame = image_to_frame(img)
    assert len(frame) == FRAME_BYTES
    assert frame[0] == 0x80
    assert frame[32 + 1] == 0x40


def test_frame_reports_headers_and_chunks() -> None:
    frame = bytes(range(256)) * 8
    reports = frame_reports(1, frame)
    assert len(reports) == 8
    for i, r in enumerate(reports):
        assert r[:9] == bytes([0xE1, 0, 0, 8 * i, 0, 0x20, 0, 0x08, 0])
        assert r[9:] == frame[256 * i : 256 * (i + 1)]


def test_invalid_inputs() -> None:
    with pytest.raises(DisplayError):
        frame_reports(2, bytes(FRAME_BYTES))
    with pytest.raises(DisplayError):
        frame_reports(0, b"\x00")


def test_pattern_has_border() -> None:
    frame = image_to_frame(mire(0))
    assert frame[0] == 0xFF and frame[-1] == 0xFF

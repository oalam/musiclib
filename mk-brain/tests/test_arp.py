from __future__ import annotations

import pytest

from mk_brain.arp import (
    MotifError,
    accented,
    chord,
    chord_name,
    degree_steps,
    hits,
    parse_motif,
    sequence,
    shift,
    spread,
    ties_after,
)

HELD = [(5, 65), (1, 58), (3, 61)]  # (pad, note), dans l'ordre d'appui


def test_orders_over_one_octave() -> None:
    assert [n for _, n in sequence(HELD, "up", 1)] == [58, 61, 65]
    assert [n for _, n in sequence(HELD, "down", 1)] == [65, 61, 58]
    assert [n for _, n in sequence(HELD, "updown", 1)] == [58, 61, 65, 61]
    assert sequence(HELD, "played", 1) == HELD
    assert sequence(HELD, "random", 1) == HELD  # le tirage se fait à l'appel


def test_octaves_stack_and_keep_the_pad() -> None:
    assert sequence(HELD, "up", 2) == [(1, 58), (3, 61), (5, 65), (1, 70), (3, 73), (5, 77)]
    assert [n for _, n in sequence(HELD, "played", 2)] == [65, 58, 61, 77, 70, 73]
    assert [n for _, n in sequence([(1, 60)], "updown", 1)] == [60]
    assert [n for _, n in sequence([(1, 60), (2, 64)], "updown", 1)] == [60, 64]


def test_notes_above_127_are_dropped() -> None:
    assert [n for _, n in sequence([(1, 120)], "up", 3)] == [120]


def test_motif_parsed_without_spaces() -> None:
    assert parse_motif("X.xx -x.X x-x. Xx.x") == "X.xx-x.Xx-x.Xx.x"


@pytest.mark.parametrize(
    ("text", "match"),
    [("X.xx", "4 pas"), ("X.xo X.xx X.xx X.xx", "inconnus"), ("-... .... .... ....", "aucune")],
)
def test_bad_motif_rejected(text: str, match: str) -> None:
    with pytest.raises(MotifError, match=match):
        parse_motif(text)


def test_ratchets_are_played_steps() -> None:
    assert parse_motif("r... .... .... ....") == "r" + "." * 15  # un ratchet suffit comme note
    assert [hits(k) for k in "xXrRtT"] == [1, 1, 2, 2, 3, 3]
    assert [accented(k) for k in "xXrRtT"] == [False, True] * 3


def test_ties_after_a_step_wrap_around() -> None:
    steps = parse_motif("X--- x-x. .... ..x-")
    assert [ties_after(steps, i) for i in (0, 4, 6, 14)] == [3, 1, 0, 1]
    assert ties_after(parse_motif("x--- ---- ---- ----"), 0) == 15


AEOLIAN = {0, 2, 3, 5, 7, 8, 10}  # do éolien, classes de hauteur


def test_chords_follow_the_scale() -> None:
    assert chord(60, "off", AEOLIAN) == [60]
    assert chord(60, "tri", AEOLIAN) == [60, 63, 67]  # i mineur
    assert chord(63, "tri", AEOLIAN) == [63, 67, 70]  # III majeur
    assert chord(62, "tri", AEOLIAN) == [62, 65, 68]  # ii diminué
    assert chord(60, "7th", AEOLIAN) == [60, 63, 67, 70]
    assert chord(68, "7th", AEOLIAN) == [68, 72, 75, 79]  # VI majeur 7
    assert chord(60, "sus2", AEOLIAN) == [60, 62, 67]
    assert chord(60, "sus4", AEOLIAN) == [60, 65, 67]
    assert chord(60, "pwr", AEOLIAN) == [60, 67, 72]
    assert chord(60, "7th", set()) == [60, 63, 67, 70]  # sans gamme : mineur par défaut


def test_spread_merges_the_chords_of_held_pads() -> None:
    held = [(1, 60), (3, 63)]
    assert spread(held, "tri", AEOLIAN) == [(1, 60), (1, 63), (1, 67), (3, 70)]
    assert spread([(1, 122)], "tri", AEOLIAN) == [(1, 122), (1, 125)]  # rien au-delà de 127


def test_degrees_stay_within_a_fourth_of_the_pad() -> None:
    assert [degree_steps(d) for d in range(1, 8)] == [0, 1, 2, 3, -3, -2, -1]


def test_shift_walks_the_scale() -> None:
    assert [shift(60, s, AEOLIAN) for s in (0, 1, 2, 3, -1, -2, -3, 7)] == [
        60,
        62,
        63,
        65,
        58,
        56,
        55,
        72,
    ]
    assert shift(61, 2, AEOLIAN) == 64  # hors gamme : garde son demi-ton au-dessus de do
    assert shift(59, 1, AEOLIAN) == 61  # sous la première note de la gamme (si bémol + 1)
    assert shift(64, -2, set()) == 60  # sans gamme : éolien sur la note
    assert shift(60, 2, {0, 3, 5, 7, 10}) == 65  # pentatonique : les degrés comptent ses notes


def test_chord_name_reads_the_quality_from_the_intervals() -> None:
    names = ("C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B")
    assert chord_name([60], names) == "C"  # CHD OFF : la note seule
    assert chord_name([60, 63, 67], names) == "Cm"
    assert chord_name([56, 60, 63], names) == "Ab"
    assert chord_name([62, 65, 68, 72], names) == "Dm7b5"
    assert chord_name([58, 65, 70], names) == "Bb5"
    assert chord_name([60, 62, 66], names) == "C"  # sans nom connu : la fondamentale

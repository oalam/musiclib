from __future__ import annotations

from mk_brain.modes import CONFIRM_NS, HOLD_NS, LOCKED, ModeSwitch


def test_hold_one_second_then_confirm() -> None:
    m = ModeSwitch()
    m.combo_pressed(0)
    assert m.update(HOLD_NS - 1, running=False) is None
    assert m.update(HOLD_NS, running=False) == "-> DESIGN? push master"
    assert m.update(HOLD_NS + 1, running=False) is None  # une seule proposition
    assert m.confirm(running=False) == "mode DESIGN" and m.mode == "design"
    assert m.confirm(running=False) is None  # rien en attente


def test_released_before_one_second_proposes_nothing() -> None:
    m = ModeSwitch()
    m.combo_pressed(0)
    m.combo_released()
    assert m.update(2 * HOLD_NS, running=False) is None and m.pending is None


def test_live_locked_while_running() -> None:
    m = ModeSwitch()
    m.combo_pressed(0)
    assert m.update(HOLD_NS, running=True) == LOCKED and m.pending is None


def test_start_during_proposal_cancels_it() -> None:
    m = ModeSwitch()
    m.combo_pressed(0)
    m.update(HOLD_NS, running=False)
    assert m.update(HOLD_NS + 1, running=True) == LOCKED
    assert m.confirm(running=True) is None and m.mode == "live"


def test_design_leaves_even_when_running() -> None:
    m = ModeSwitch("design")
    m.combo_pressed(0)
    assert m.update(HOLD_NS, running=True) == "-> LIVE? push master"
    assert m.confirm(running=True) == "mode LIVE" and m.mode == "live"


def test_proposal_expires() -> None:
    m = ModeSwitch()
    m.combo_pressed(0)
    m.update(HOLD_NS, running=False)
    assert m.update(HOLD_NS + CONFIRM_NS + 1, running=False) == "switch cancelled"
    assert m.pending is None

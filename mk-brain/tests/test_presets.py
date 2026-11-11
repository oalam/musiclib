from __future__ import annotations

from pathlib import Path

from mk_brain.config import ArpPreset, Config
from mk_brain.presets import load_bank, save_bank, user_name

MINE = ArpPreset(order="updown", octaves=2, gate=35, division="1/16", motif="SYNC")


def test_bank_round_trip(tmp_path: Path, cfg: Config) -> None:
    path = tmp_path / "state" / "arp-presets.json"
    assert load_bank(cfg.arp, path) == {}  # absent : la config seule
    save_bank({3: MINE, 16: MINE.model_copy(update={"motif": "OFF"})}, path)
    assert load_bank(cfg.arp, path) == {3: MINE, 16: MINE.model_copy(update={"motif": "OFF"})}
    assert user_name(3) == "U03"


def test_unusable_slots_are_dropped(tmp_path: Path, cfg: Config) -> None:
    """Hors des 16 pads, ou motif disparu de la config : ignoré ; fichier illisible : rien."""
    path = tmp_path / "arp-presets.json"
    gone = MINE.model_copy(update={"progression": "2514"})
    save_bank(
        {0: MINE, 17: MINE, 5: MINE.model_copy(update={"motif": "RIEN"}), 6: gone, 9: MINE}, path
    )
    assert load_bank(cfg.arp, path) == {9: MINE}
    path.write_text("{", encoding="utf-8")
    assert load_bank(cfg.arp, path) == {}
    path.write_text('{"slots": {"2": {"order": "zigzag"}}}', encoding="utf-8")
    assert load_bank(cfg.arp, path) == {}

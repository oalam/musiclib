from __future__ import annotations

from pathlib import Path

import pytest

from mk_brain.config import Config, ConfigError, load_config


def test_default_config_loads(cfg: Config) -> None:
    assert [lay.group for lay in cfg.layouts[:7]] == list("BCDEFGH")
    assert all(lay.group is None and lay.mode is None for lay in cfg.layouts[7:])
    assert cfg.midi.auto_channel == 16
    assert (cfg.mpc_pad(1).label, cfg.mpc_pad(1).track, cfg.mpc_pad(1).note) == ("BD", 1, 60)


def test_mpc_table_validated(tmp_path: Path, cfg: Config) -> None:
    import yaml

    for change, match in (({"pad": 2}, "16 pads"), ({"track": 16}, "AUTO CHANNEL")):
        raw = cfg.model_dump()
        raw["mpc"][0].update(change)
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.safe_dump(raw))
        with pytest.raises(ConfigError, match=match):
            load_config(bad)


def test_invalid_scale_rejected(tmp_path: Path, cfg: Config) -> None:
    raw = cfg.model_dump()
    raw["layouts"][1]["intervals"] = [2, 0]
    bad = tmp_path / "bad.yaml"
    import yaml

    bad.write_text(yaml.safe_dump(raw))
    with pytest.raises(ConfigError, match="intervalles"):
        load_config(bad)


def test_missing_file() -> None:
    with pytest.raises(ConfigError):
        load_config(Path("/nonexistent.yaml"))


def test_arp_motifs_validated(tmp_path: Path, cfg: Config) -> None:
    import yaml

    assert cfg.arp.motif_names[0] == "OFF" and cfg.arp.motifs["GALO"] == "X.xx" * 4
    good = {"order": "up", "octaves": 1, "gate": 50, "division": "1/16", "motif": "GALO"}
    assert cfg.arp.presets["RUSH"].division == "1/32"
    for change, match in (
        ({"motifs": {"GALO": "X.xx" * 5}}, "16 attendus"),
        ({"motifs": {"GALOP": "X.xx" * 4}}, "4 caractères"),
        ({"motifs": {"OFF": "X.xx" * 4}}, "réservé"),
        ({"motif": "RIEN"}, "absent"),
        ({"progression": "2514"}, "absente"),
        ({"progressions": {"1800": [1, 8]}}, "de 1 à 7"),
        ({"progressions": {"LONGUE": [1, 4]}}, "4 caractères"),
        ({"presets": {"P": {**good, "progression": "2514"}}}, "absents"),
        ({"presets": {"TROPLONG": dict(good)}}, "4 caractères"),
        ({"presets": {"P": {**good, "motif": "RIEN"}}}, "absents"),
        ({"presets": {"P": {**good, "division": "1/5"}}}, "inconnue"),
        ({"presets": {"U03": dict(good)}}, "réservés"),
        ({"presets": {f"P{n}": dict(good) for n in range(17)}}, "16 au plus"),
    ):
        raw = cfg.model_dump()
        raw["arp"].update(change)
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.safe_dump(raw))
        with pytest.raises(ConfigError, match=match):
            load_config(bad)

from __future__ import annotations

from pathlib import Path

import pytest

from mk_brain.config import Config, ConfigError, load_config


def test_default_config_loads(cfg: Config) -> None:
    assert [lay.group for lay in cfg.layouts] == list("ABCDEFGH")
    assert cfg.midi.auto_channel == 16


def test_invalid_scale_rejected(tmp_path: Path, cfg: Config) -> None:
    raw = cfg.model_dump()
    raw["layouts"][2]["intervals"] = [2, 0]
    bad = tmp_path / "bad.yaml"
    import yaml

    bad.write_text(yaml.safe_dump(raw))
    with pytest.raises(ConfigError, match="intervalles"):
        load_config(bad)


def test_missing_file() -> None:
    with pytest.raises(ConfigError):
        load_config(Path("/nonexistent.yaml"))

"""Configuration pytest partagee."""
from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers", "integration: lit de l'audio reel (SSD media), saute sinon")


@pytest.fixture(autouse=True)
def _isolated_manual_subs(tmp_path_factory: pytest.TempPathFactory,
                          monkeypatch: pytest.MonkeyPatch) -> None:
    """Sous-dossiers manuels (7.K) : jamais le folders.json du vault, et SUBS
    restaure apres chaque test (le registre est un etat de module)."""
    import samples
    from analyzer import samples as analyzer_samples

    monkeypatch.setattr(samples, "FOLDERS_FILE", tmp_path_factory.mktemp("folders") / "folders.json")
    monkeypatch.setattr(analyzer_samples, "SUBS", dict(analyzer_samples.SUBS))

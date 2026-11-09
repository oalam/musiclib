from __future__ import annotations

import pytest

from mk_brain.config import Config, load_config
from mk_brain.project import Project, load_project


@pytest.fixture(scope="session")
def cfg() -> Config:
    """Config du dépôt, démarrage forcé en live : les tests partent du mode de scène."""
    base = load_config()
    return base.model_copy(update={"play": base.play.model_copy(update={"mode": "live"})})


@pytest.fixture(scope="session")
def project() -> Project:
    return load_project()

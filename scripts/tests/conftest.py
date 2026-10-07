"""Configuration pytest partagee."""
from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers", "integration: lit de l'audio reel (SSD media), saute sinon")

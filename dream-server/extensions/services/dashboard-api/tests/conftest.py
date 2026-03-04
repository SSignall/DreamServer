"""Shared fixtures for dashboard-api unit tests."""

import sys
from pathlib import Path

import pytest

# Add dashboard-api source to path so we can import modules directly.
DASHBOARD_API_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DASHBOARD_API_DIR))


@pytest.fixture()
def install_dir(tmp_path, monkeypatch):
    """Provide an isolated install directory with a .env file."""
    d = tmp_path / "dream-server"
    d.mkdir()
    monkeypatch.setattr("helpers.INSTALL_DIR", str(d))
    return d


@pytest.fixture()
def data_dir(tmp_path, monkeypatch):
    """Provide an isolated data directory for bootstrap/token files."""
    d = tmp_path / "data"
    d.mkdir()
    monkeypatch.setattr("helpers.DATA_DIR", str(d))
    monkeypatch.setattr("helpers._TOKEN_FILE", d / "token_counter.json")
    return d

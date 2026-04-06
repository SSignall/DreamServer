"""Tests for dream-host-agent.py — _parse_mem_value and _iso_now."""

import importlib.util
import sys
from pathlib import Path

# Import the host agent module from bin/ using importlib.
# The module has an ``if __name__ == "__main__":`` guard so no server starts.
_agent_path = Path(__file__).resolve().parents[4] / "bin" / "dream-host-agent.py"
_spec = importlib.util.spec_from_file_location("dream_host_agent", _agent_path)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["dream_host_agent"] = _mod
_spec.loader.exec_module(_mod)

_parse_mem_value = _mod._parse_mem_value
_iso_now = _mod._iso_now


# --- _parse_mem_value ---


class TestParseMemValue:

    def test_mib(self):
        assert _parse_mem_value("256MiB") == 256.0

    def test_gib(self):
        assert _parse_mem_value("4GiB") == 4096.0

    def test_tib(self):
        assert _parse_mem_value("1TiB") == 1024 * 1024

    def test_kib(self):
        assert _parse_mem_value("512KiB") == 0.5

    def test_bytes(self):
        result = _parse_mem_value("1024B")
        assert abs(result - 1024 / (1024 * 1024)) < 1e-9

    def test_fractional_gib(self):
        assert _parse_mem_value("1.5GiB") == 1536.0

    def test_zero_bytes(self):
        assert _parse_mem_value("0B") == 0.0

    def test_dash_dash(self):
        assert _parse_mem_value("--") == 0.0

    def test_empty_string(self):
        assert _parse_mem_value("") == 0.0

    def test_invalid_number(self):
        assert _parse_mem_value("xyzMiB") == 0.0

    def test_whitespace_padding(self):
        assert _parse_mem_value("  256MiB  ") == 256.0


# --- _iso_now ---


class TestIsoNow:

    def test_returns_utc_iso_string(self):
        result = _iso_now()
        assert isinstance(result, str)
        # UTC ISO strings end with +00:00
        assert "+00:00" in result

    def test_contains_t_separator(self):
        result = _iso_now()
        assert "T" in result

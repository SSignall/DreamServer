"""
=== GENERATED TEST FILE — NEEDS REVIEW ===
Generated: 2026-03-08T01:57:37.584388+00:00
Source: extensions/services/dashboard-api/routers/privacy.py
Generator: Qwen3-Coder (local GPU)

This file was auto-generated and has NOT been reviewed or run.
Review before using. May need fixture adjustments or mock updates.
================================================================
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException

# Mock dependencies before importing the router module
with patch('config.SERVICES', {'privacy-shield': {'host': 'privacy-shield', 'port': 8080}, 'llama-server': {'host': 'llama-server', 'port': 8000}}):
    with patch('config.INSTALL_DIR', '/app'):
        with patch('security.verify_api_key', return_value=True):
            from routers.privacy import router, get_privacy_shield_status, toggle_privacy_shield, get_privacy_shield_stats
            from models import PrivacyShieldStatus, PrivacyShieldToggle

# Create a test client
from fastapi import FastAPI
app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestGetPrivacyShieldStatus:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Reset environment variables
        with patch.dict('os.environ', {
            'SHIELD_PORT': '9000',
            'TARGET_API_URL': 'http://target-api:8000/v1',
            'PII_CACHE_ENABLED': 'true'
        }, clear=True):
            yield

    @patch('asyncio.create_subprocess_exec')
    @patch('aiohttp.ClientSession')
    def test_status_success(self, mock_session, mock_subprocess):
        # Mock docker ps output
        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(return_value=(b"dream-privacy-shield", b""))
        mock_proc.returncode = 0
        mock_subprocess.return_value = mock_proc

        # Mock health check response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)

        response = client.get("/api/privacy-shield/status", headers={"X-API-Key": "test-key"})

        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is True
        assert data["container_running"] is True
        assert data["port"] == 9000
        assert data["pii_cache_enabled"] is True
        assert "active" in data["message"]

    @patch('asyncio.create_subprocess_exec')
    def test_status_container_not_running(self, mock_subprocess):
        # Mock docker ps output with no container
        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(return_value=(b"", b""))
        mock_subprocess.return_value = mock_proc

        response = client.get("/api/privacy-shield/status", headers={"X-API-Key": "test-key"})

        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is False
        assert data["container_running"] is False
        assert "not running" in data["message"].lower()

    @patch('asyncio.create_subprocess_exec')
    @patch('aiohttp.ClientSession')
    def test_status_container_running_but_unhealthy(self, mock_session, mock_subprocess):
        # Mock docker ps output
        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(return_value=(b"dream-privacy-shield", b""))
        mock_subprocess.return_value = mock_proc

        # Mock health check failure
        mock_response = MagicMock()
        mock_response.status = 503
        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)

        response = client.get("/api/privacy-shield/status", headers={"X-API-Key": "test-key"})

        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is False
        assert data["container_running"] is True
        assert "not running" in data["message"].lower()

    @patch('asyncio.create_subprocess_exec')
    def test_status_docker_command_error(self, mock_subprocess):
        # Mock docker command exception
        mock_subprocess.side_effect = Exception("Docker command failed")

        response = client.get("/api/privacy-shield/status", headers={"X-API-Key": "test-key"})

        assert response.status_code == 200
        data = response.json()
        assert data["container_running"] is False
        assert data["enabled"] is False

    def test_status_missing_api_key(self):
        response = client.get("/api/privacy-shield/status")
        assert response.status_code == 403


class TestTogglePrivacyShield:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Reset environment variables
        with patch.dict('os.environ', {}, clear=True):
            yield

    @patch('asyncio.create_subprocess_exec')
    def test_toggle_enable_success(self, mock_subprocess):
        # Mock successful docker compose up
        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(return_value=(b"", b""))
        mock_proc.returncode = 0
        mock_subprocess.return_value = mock_proc

        request = PrivacyShieldToggle(enable=True)
        response = client.post(
            "/api/privacy-shield/toggle",
            json=request.dict(),
            headers={"X-API-Key": "test-key"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "started" in data["message"].lower()

    @patch('asyncio.create_subprocess_exec')
    def test_toggle_enable_failure(self, mock_subprocess):
        # Mock failed docker compose up
        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(return_value=(b"", b"Error starting service"))
        mock_proc.returncode = 1
        mock_subprocess.return_value = mock_proc

        request = PrivacyShieldToggle(enable=True)
        response = client.post(
            "/api/privacy-shield/toggle",
            json=request.dict(),
            headers={"X-API-Key": "test-key"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "failed" in data["message"].lower()

    @patch('asyncio.create_subprocess_exec')
    def test_toggle_disable_success(self, mock_subprocess):
        # Mock successful docker compose stop
        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(return_value=(b"", b""))
        mock_proc.returncode = 0
        mock_subprocess.return_value = mock_proc

        request = PrivacyShieldToggle(enable=False)
        response = client.post(
            "/api/privacy-shield/toggle",
            json=request.dict(),
            headers={"X-API-Key": "test-key"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "stopped" in data["message"].lower()

    @patch('asyncio.create_subprocess_exec')
    def test_toggle_disable_failure(self, mock_subprocess):
        # Mock failed docker compose stop
        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(return_value=(b"", b"Error stopping service"))
        mock_proc.returncode = 1
        mock_subprocess.return_value = mock_proc

        request = PrivacyShieldToggle(enable=False)
        response = client.post(
            "/api/privacy-shield/toggle",
            json=request.dict(),
            headers={"X-API-Key": "test-key"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False

    @patch('asyncio.create_subprocess_exec')
    def test_toggle_docker_not_found(self, mock_subprocess):
        # Mock FileNotFoundError
        mock_subprocess.side_effect = FileNotFoundError("Docker not found")

        request = PrivacyShieldToggle(enable=True)
        response = client.post(
            "/api/privacy-shield/toggle",
            json=request.dict(),
            headers={"X-API-Key": "test-key"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "docker not available" in data["message"].lower()

    @patch('asyncio.create_subprocess_exec')
    def test_toggle_timeout(self, mock_subprocess):
        # Mock timeout
        mock_subprocess.side_effect = asyncio.TimeoutError()

        request = PrivacyShieldToggle(enable=True)
        response = client.post(
            "/api/privacy-shield/toggle",
            json=request.dict(),
            headers={"X-API-Key": "test-key"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "timed out" in data["message"].lower()

    @patch('asyncio.create_subprocess_exec')
    def test_toggle_generic_exception(self, mock_subprocess):
        # Mock generic exception
        mock_subprocess.side_effect = Exception("Unexpected error")

        request = PrivacyShieldToggle(enable=True)
        response = client.post(
            "/api/privacy-shield/toggle",
            json=request.dict(),
            headers={"X-API-Key": "test-key"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False

    def test_toggle_missing_api

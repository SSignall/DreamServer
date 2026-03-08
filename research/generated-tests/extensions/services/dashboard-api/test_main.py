"""
=== GENERATED TEST FILE — NEEDS REVIEW ===
Generated: 2026-03-08T01:52:00.421645+00:00
Source: extensions/services/dashboard-api/main.py
Generator: Qwen3-Coder (local GPU)

This file was auto-generated and has NOT been reviewed or run.
Review before using. May need fixture adjustments or mock updates.
================================================================
"""

import pytest
import asyncio
import os
import socket
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from datetime import datetime, timezone

# Mock the local modules before importing main
import sys
from types import ModuleType

# Create mock modules
mock_config = ModuleType('config')
mock_config.SERVICES = {
    "service1": {"name": "Service 1", "port": 8001, "external_port": 8001},
    "service2": {"name": "Service 2", "port": 8002, "external_port": 8002},
}
mock_config.INSTALL_DIR = "/install"
mock_config.DATA_DIR = "/data"
mock_config.SIDEBAR_ICONS = {}

mock_models = ModuleType('models')
mock_models.GPUInfo = MagicMock
mock_models.ServiceStatus = MagicMock
mock_models.DiskUsage = MagicMock
mock_models.ModelInfo = MagicMock
mock_models.BootstrapStatus = MagicMock
mock_models.FullStatus = MagicMock
mock_models.PortCheckRequest = MagicMock

mock_security = ModuleType('security')
mock_security.verify_api_key = MagicMock()

mock_gpu = ModuleType('gpu')
mock_gpu.get_gpu_info = MagicMock()

mock_helpers = ModuleType('helpers')
mock_helpers.check_service_health = MagicMock()
mock_helpers.get_all_services = MagicMock()
mock_helpers.get_disk_usage = MagicMock()
mock_helpers.get_model_info = MagicMock()
mock_helpers.get_bootstrap_status = MagicMock()
mock_helpers.get_uptime = MagicMock()
mock_helpers.get_cpu_metrics = MagicMock()
mock_helpers.get_ram_metrics = MagicMock()
mock_helpers.get_llama_metrics = MagicMock()
mock_helpers.get_loaded_model = MagicMock()
mock_helpers.get_llama_context_size = MagicMock()

mock_agent_monitor = ModuleType('agent_monitor')
mock_agent_monitor.collect_metrics = MagicMock()

mock_routers = ModuleType('routers')
mock_routers.workflows = ModuleType('routers.workflows')
mock_routers.workflows.router = MagicMock()
mock_routers.features = ModuleType('routers.features')
mock_routers.features.router = MagicMock()
mock_routers.setup = ModuleType('routers.setup')
mock_routers.setup.router = MagicMock()
mock_routers.updates = ModuleType('routers.updates')
mock_routers.updates.router = MagicMock()
mock_routers.agents = ModuleType('routers.agents')
mock_routers.agents.router = MagicMock()
mock_routers.privacy = ModuleType('routers.privacy')
mock_routers.privacy.router = MagicMock()

# Add mocks to sys.modules
sys.modules['config'] = mock_config
sys.modules['models'] = mock_models
sys.modules['security'] = mock_security
sys.modules['gpu'] = mock_gpu
sys.modules['helpers'] = mock_helpers
sys.modules['agent_monitor'] = mock_agent_monitor
sys.modules['routers'] = mock_routers
sys.modules['routers.workflows'] = mock_routers.workflows
sys.modules['routers.features'] = mock_routers.features
sys.modules['routers.setup'] = mock_routers.setup
sys.modules['routers.updates'] = mock_routers.updates
sys.modules['routers.agents'] = mock_routers.agents
sys.modules['routers.privacy'] = mock_routers.privacy

# Now import main
import main


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(main.app)


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_returns_ok_status(self, client):
        """Test health endpoint returns correct status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
        # Verify timestamp is ISO format with timezone
        try:
            datetime.fromisoformat(data["timestamp"])
        except ValueError:
            pytest.fail("Timestamp is not in ISO format")


class TestPreflightDockerEndpoint:
    """Tests for /api/preflight/docker endpoint."""

    def test_preflight_docker_host_env(self, client):
        """Test Docker detection when /.dockerenv exists."""
        with patch('os.path.exists', return_value=True):
            response = client.get("/api/preflight/docker", headers={"Authorization": "Bearer valid-key"})
            assert response.status_code == 200
            data = response.json()
            assert data["available"] is True
            assert data["version"] == "available (host)"

    def test_preflight_docker_command_success(self, client):
        """Test Docker detection when docker command succeeds."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Docker version 24.0.5, build abc123"
        
        with patch('subprocess.run', return_value=mock_result), \
             patch('os.path.exists', return_value=False):
            response = client.get("/api/preflight/docker", headers={"Authorization": "Bearer valid-key"})
            assert response.status_code == 200
            data = response.json()
            assert data["available"] is True
            assert data["version"] == "24.0.5"

    def test_preflight_docker_command_failure(self, client):
        """Test Docker detection when docker command fails."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "Docker command failed"
        
        with patch('subprocess.run', return_value=mock_result), \
             patch('os.path.exists', return_value=False):
            response = client.get("/api/preflight/docker", headers={"Authorization": "Bearer valid-key"})
            assert response.status_code == 200
            data = response.json()
            assert data["available"] is False
            assert "error" in data

    def test_preflight_docker_not_installed(self, client):
        """Test Docker detection when docker command not found."""
        with patch('subprocess.run', side_effect=FileNotFoundError), \
             patch('os.path.exists', return_value=False):
            response = client.get("/api/preflight/docker", headers={"Authorization": "Bearer valid-key"})
            assert response.status_code == 200
            data = response.json()
            assert data["available"] is False
            assert data["error"] == "Docker not installed"

    def test_preflight_docker_timeout(self, client):
        """Test Docker detection when command times out."""
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired), \
             patch('os.path.exists', return_value=False):
            response = client.get("/api/preflight/docker", headers={"Authorization": "Bearer valid-key"})
            assert response.status_code == 200
            data = response.json()
            assert data["available"] is False
            assert data["error"] == "Docker check timed out"

    def test_preflight_docker_unauthorized(self, client):
        """Test Docker endpoint requires authentication."""
        response = client.get("/api/preflight/docker")
        assert response.status_code == 401


class TestPreflightGPUEndpoint:
    """Tests for /api/preflight/gpu endpoint."""

    def test_preflight_gpu_nvidia_success(self, client):
        """Test GPU detection for NVIDIA GPU."""
        mock_gpu_info = MagicMock()
        mock_gpu_info.name = "NVIDIA GeForce RTX 4090"
        mock_gpu_info.memory_total_mb = 24576
        mock_gpu_info.gpu_backend = "nvidia"
        mock_gpu_info.memory_type = "dedicated"
        
        with patch('main.get_gpu_info', return_value=mock_gpu_info):
            response = client.get("/api/preflight/gpu", headers={"Authorization": "Bearer valid-key"})
            assert response.status_code == 200
            data = response.json()
            assert data["available"] is True
            assert data["name"] == "NVIDIA GeForce RTX 4090"
            assert data["vram"] == 24.0
            assert data["backend"] == "nvidia"
            assert data["memory_type"] == "dedicated"

    def test_preflight_gpu_unified_memory(self, client):
        """Test GPU detection with unified memory."""
        mock_gpu_info = MagicMock()
        mock_gpu_info.name = "AMD Radeon Pro W6800"
        mock_gpu_info.memory_total_mb = 32768
        mock_gpu_info.gpu_backend = "amd"
        mock_gpu_info.memory_type = "unified"
        
        with patch('main.get_gpu_info', return_value=mock_gpu_info):
            response = client.get("/api/preflight/gpu", headers={"Authorization": "Bearer valid-key"})
            assert response.status_code == 200
            data = response.json()
            assert data["available"] is True
            assert data["memory_label"] == "32.0 GB Unified"

    def test_preflight_gpu_no_gpu_detected(self, client):
        """Test GPU detection when no GPU is found."""
        with patch('main.get_gpu_info', return_value=None):
            response = client.get("/api/preflight/gpu", headers={"Authorization": "Bearer valid-key"})
            assert response.status_code == 200
            data = response.json()
            assert data["available"] is False
            assert "error" in data

    def test_preflight_gpu_amd_error(self, client):
        """Test GPU detection for AMD GPU with error."""
        with patch('main.get_gpu_info', return_value=None), \
             patch.dict(os.environ, {"GPU_BACKEND": "amd"}):
            response = client.get("/api/preflight/gpu", headers={"Authorization": "Bearer valid-key"})
            assert response.status_code

"""
=== GENERATED TEST FILE — NEEDS REVIEW ===
Generated: 2026-03-08T01:56:27.249304+00:00
Source: extensions/services/dashboard-api/routers/agents.py
Generator: Qwen3-Coder (local GPU)

This file was auto-generated and has NOT been reviewed or run.
Review before using. May need fixture adjustments or mock updates.
================================================================
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.responses import HTMLResponse
from fastapi.exceptions import HTTPException

# Mock the imports before importing the router module
mock_get_full_agent_metrics = MagicMock()
mock_cluster_status = MagicMock()
mock_throughput = MagicMock()
mock_verify_api_key = MagicMock()

# Mock cluster_status.refresh() and to_dict()
mock_cluster_status.refresh = AsyncMock()
mock_cluster_status.to_dict.return_value = {"nodes": []}

# Mock throughput.get_stats()
mock_throughput.get_stats.return_value = {"tokens_per_sec": 100.0}

# Patch the imports in the agents module
with patch('extensions.services.dashboard-api.routers.agents.get_full_agent_metrics', mock_get_full_agent_metrics), \
     patch('extensions.services.dashboard-api.routers.agents.cluster_status', mock_cluster_status), \
     patch('extensions.services.dashboard-api.routers.agents.throughput', mock_throughput), \
     patch('extensions.services.dashboard-api.routers.agents.verify_api_key', mock_verify_api_key):
    from extensions.services.dashboard-api.routers import agents


@pytest.fixture
def api_key_header():
    """Fixture to provide a valid API key."""
    return "valid-api-key"


@pytest.fixture
def mock_metrics_data():
    """Fixture providing sample metrics data."""
    return {
        "cluster": {
            "active_gpus": 4,
            "total_gpus": 4,
            "failover_ready": True
        },
        "agent": {
            "session_count": 10,
            "last_update": "2024-01-01T12:34:56Z"
        },
        "tokens": {
            "total_tokens_24h": 1234567,
            "total_cost_24h": 12.3456,
            "requests_24h": 1000,
            "top_models": [
                {"model": "gpt-4", "tokens": 500000, "requests": 500},
                {"model": "claude-3", "tokens": 300000, "requests": 300}
            ]
        },
        "throughput": {
            "current": 150.5,
            "average": 120.3
        }
    }


class TestAgentMetrics:
    """Tests for /api/agents/metrics endpoint."""

    @pytest.mark.asyncio
    async def test_get_agent_metrics_success(self, api_key_header):
        """Test successful retrieval of agent metrics."""
        expected_metrics = {"cluster": {}, "agent": {}, "tokens": {}, "throughput": {}}
        mock_get_full_agent_metrics.return_value = expected_metrics
        
        result = await agents.get_agent_metrics(api_key=api_key_header)
        
        assert result == expected_metrics
        mock_get_full_agent_metrics.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_agent_metrics_with_invalid_api_key(self):
        """Test that invalid API key raises HTTPException."""
        mock_verify_api_key.side_effect = HTTPException(status_code=401, detail="Invalid API key")
        
        with pytest.raises(HTTPException) as exc_info:
            await agents.get_agent_metrics(api_key="invalid-key")
        
        assert exc_info.value.status_code == 401


class TestAgentMetricsHTML:
    """Tests for /api/agents/metrics.html endpoint."""

    @pytest.mark.asyncio
    async def test_get_agent_metrics_html_success(self, api_key_header, mock_metrics_data):
        """Test successful HTML generation with valid metrics."""
        mock_get_full_agent_metrics.return_value = mock_metrics_data
        
        result = await agents.get_agent_metrics_html(api_key=api_key_header)
        
        assert isinstance(result, HTMLResponse)
        html_content = result.body.decode()
        
        # Check key elements are present
        assert "4/4 GPUs" in html_content
        assert "Ready ✅" in html_content
        assert "10" in html_content  # session count
        assert "1234K" in html_content  # tokens_k
        assert "12.3456" in html_content  # cost
        assert "1000" in html_content  # requests
        assert "150.5" in html_content  # current throughput
        assert "120.3" in html_content  # average throughput
        assert "gpt-4" in html_content  # top model
        assert "500K" in html_content  # top model tokens
        assert "500" in html_content  # top model requests

    @pytest.mark.asyncio
    async def test_get_agent_metrics_html_no_top_models(self, api_key_header):
        """Test HTML generation when no top models are available."""
        mock_metrics = {
            "cluster": {"active_gpus": 2, "total_gpus": 4, "failover_ready": False},
            "agent": {"session_count": 5, "last_update": "2024-01-01T10:20:30Z"},
            "tokens": {
                "total_tokens_24h": 100000,
                "total_cost_24h": 1.23,
                "requests_24h": 100,
                "top_models": []
            },
            "throughput": {"current": 50.0, "average": 45.5}
        }
        mock_get_full_agent_metrics.return_value = mock_metrics
        
        result = await agents.get_agent_metrics_html(api_key=api_key_header)
        html_content = result.body.decode()
        
        # Check failover status is warning
        assert "Single GPU ⚠️" in html_content
        assert "status-warn" in html_content
        # Check no top models table is present
        assert "<article class='metric-card'><h4>Top Models" not in html_content

    @pytest.mark.asyncio
    async def test_get_agent_metrics_html_html_escaping(self, api_key_header):
        """Test that HTML special characters are properly escaped."""
        mock_metrics = {
            "cluster": {"active_gpus": 1, "total_gpus": 1, "failover_ready": False},
            "agent": {"session_count": 1, "last_update": "2024-01-01T12:00:00Z"},
            "tokens": {
                "total_tokens_24h": 1000,
                "total_cost_24h": 0.1,
                "requests_24h": 10,
                "top_models": [
                    {"model": "<script>alert('xss')</script>", "tokens": 500, "requests": 5}
                ]
            },
            "throughput": {"current": 10.0, "average": 10.0}
        }
        mock_get_full_agent_metrics.return_value = mock_metrics
        
        result = await agents.get_agent_metrics_html(api_key=api_key_header)
        html_content = result.body.decode()
        
        # Check that HTML special characters are escaped
        assert "&lt;script&gt;alert('xss')&lt;/script&gt;" in html_content
        assert "<script>" not in html_content

    @pytest.mark.asyncio
    async def test_get_agent_metrics_html_with_invalid_api_key(self):
        """Test that invalid API key raises HTTPException for HTML endpoint."""
        mock_verify_api_key.side_effect = HTTPException(status_code=401, detail="Invalid API key")
        
        with pytest.raises(HTTPException) as exc_info:
            await agents.get_agent_metrics_html(api_key="invalid-key")
        
        assert exc_info.value.status_code == 401


class TestClusterStatus:
    """Tests for /api/agents/cluster endpoint."""

    @pytest.mark.asyncio
    async def test_get_cluster_status_success(self, api_key_header):
        """Test successful cluster status retrieval."""
        expected_status = {"nodes": [{"id": "node1", "status": "healthy"}]}
        mock_cluster_status.to_dict.return_value = expected_status
        
        result = await agents.get_cluster_status(api_key=api_key_header)
        
        assert result == expected_status
        mock_cluster_status.refresh.assert_awaited_once()
        mock_cluster_status.to_dict.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_cluster_status_with_invalid_api_key(self):
        """Test that invalid API key raises HTTPException for cluster endpoint."""
        mock_verify_api_key.side_effect = HTTPException(status_code=401, detail="Invalid API key")
        
        with pytest.raises(HTTPException) as exc_info:
            await agents.get_cluster_status(api_key="invalid-key")
        
        assert exc_info.value.status_code == 401


class TestThroughput:
    """Tests for /api/agents/throughput endpoint."""

    @pytest.mark.asyncio
    async def test_get_throughput_success(self, api_key_header):
        """Test successful throughput metrics retrieval."""
        expected_stats = {"tokens_per_sec": 100.0, "window": "5m"}
        mock_throughput.get_stats.return_value = expected_stats
        
        result = await agents.get_throughput(api_key=api_key_header)
        
        assert result == expected_stats
        mock_throughput.get_stats.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_throughput_with_invalid_api_key(self):
        """Test that invalid API key raises HTTPException for throughput endpoint."""
        mock_verify_api_key.side_effect = HTTPException(status_code=

"""
=== GENERATED TEST FILE — NEEDS REVIEW ===
Generated: 2026-03-08T02:01:06.777357+00:00
Source: extensions/services/privacy-shield/proxy.py
Generator: Qwen3-Coder (local GPU)

This file was auto-generated and has NOT been reviewed or run.
Review before using. May need fixture adjustments or mock updates.
================================================================
"""

import pytest
import os
import asyncio
import hashlib
from unittest.mock import AsyncMock, MagicMock, patch, call
from fastapi.testclient import TestClient
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
import httpx

# Mock the pii_scrubber module before importing proxy
pii_scrubber_mock = MagicMock()
PrivacyShield_mock = MagicMock()
pii_scrubber_mock.PrivacyShield = PrivacyShield_mock
with patch.dict('sys.modules', {'pii_scrubber': pii_scrubber_mock}):
    from extensions.services.privacy_shield import proxy


@pytest.fixture(autouse=True)
def reset_globals():
    """Reset global state before each test."""
    # Reset environment variables
    original_env = os.environ.copy()
    os.environ.clear()
    os.environ.update({
        "SHIELD_API_KEY": "test-api-key-123",
        "TARGET_API_URL": "http://test-server:8000/v1",
        "SHIELD_PORT": "8085",
        "PII_CACHE_ENABLED": "true",
        "PII_CACHE_SIZE": "1000",
        "PII_CACHE_TTL": "300",
        "SHIELD_SESSION_MAXSIZE": "10000",
        "SHIELD_SESSION_TTL": "3600"
    })
    
    # Reset global objects
    proxy.sessions.clear()
    proxy.http_client = httpx.AsyncClient(
        limits=httpx.Limits(max_keepalive_connections=100, max_connections=200),
        timeout=httpx.Timeout(60.0, connect=5.0)
    )
    
    yield
    
    # Restore environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def client():
    """Create test client with mocked dependencies."""
    with patch('extensions.services.privacy_shield.proxy.app'):
        with patch('extensions.services.privacy_shield.proxy.uvicorn.run'):
            # Reinitialize the app
            proxy.app = proxy.FastAPI(title="API Privacy Shield", version="0.2.0")
            # Re-register routes
            proxy.app.add_api_route("/health", proxy.health, methods=["GET"])
            proxy.app.add_api_route("/stats", proxy.stats, methods=["GET"])
            proxy.app.add_api_route("/{path:path}", proxy.proxy, methods=["GET", "POST"])
            
            return TestClient(proxy.app)


class TestHealthEndpoint:
    def test_health_endpoint_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "api-privacy-shield"
        assert data["version"] == "0.2.0"
        assert data["target_api"] == "http://test-server:8000/v1"
        assert data["cache_enabled"] is True
        assert data["active_sessions"] == 0


class TestStatsEndpoint:
    def test_stats_endpoint_returns_zero_when_no_sessions(self, client):
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["active_sessions"] == 0
        assert data["total_pii_scrubbed"] == 0
        assert data["cache_enabled"] is True
        assert data["cache_size"] == 1000


class TestAPIKeyAuthentication:
    def test_valid_api_key_succeeds(self, client):
        response = client.get("/health", headers={"Authorization": "Bearer test-api-key-123"})
        assert response.status_code == 200
    
    def test_invalid_api_key_fails(self, client):
        response = client.get("/health", headers={"Authorization": "Bearer invalid-key"})
        assert response.status_code == 403
    
    def test_missing_authorization_header_fails(self, client):
        response = client.get("/health")
        assert response.status_code == 403
    
    def test_missing_api_key_generates_temporary_key(self, client, monkeypatch):
        # Remove API key from environment
        monkeypatch.delenv("SHIELD_API_KEY", raising=False)
        
        # Reinitialize the module
        import importlib
        importlib.reload(proxy)
        
        # Create new test client with reloaded module
        test_client = TestClient(proxy.app)
        
        # Should still work because temporary key is generated
        response = test_client.get("/health")
        assert response.status_code == 200


class TestProxyEndpoint:
    def test_proxy_forwards_post_request(self, client):
        # Mock the httpx client
        mock_response = MagicMock()
        mock_response.content = b'{"text": "Hello world"}'
        mock_response.status_code = 200
        
        with patch.object(proxy.http_client, 'post', new=AsyncMock(return_value=mock_response)):
            with patch.object(proxy.CachedPrivacyShield, 'process_request', return_value=("", {})):
                with patch.object(proxy.CachedPrivacyShield, 'process_response', return_value='{"text": "Hello world"}'):
                    response = client.post(
                        "/chat/completions",
                        json={"message": "Hello"},
                        headers={"Authorization": "Bearer test-api-key-123"}
                    )
                    assert response.status_code == 200
    
    def test_proxy_forwards_get_request(self, client):
        # Mock the httpx client
        mock_response = MagicMock()
        mock_response.content = b'{"status": "ok"}'
        mock_response.status_code = 200
        
        with patch.object(proxy.http_client, 'get', new=AsyncMock(return_value=mock_response)):
            with patch.object(proxy.CachedPrivacyShield, 'process_request', return_value=("", {})):
                with patch.object(proxy.CachedPrivacyShield, 'process_response', return_value='{"status": "ok"}'):
                    response = client.get(
                        "/models",
                        headers={"Authorization": "Bearer test-api-key-123"}
                    )
                    assert response.status_code == 200
    
    def test_proxy_preserves_headers(self, client):
        # Mock the httpx client
        mock_response = MagicMock()
        mock_response.content = b'{"text": "Hello world"}'
        mock_response.status_code = 200
        
        with patch.object(proxy.http_client, 'post', new=AsyncMock(return_value=mock_response)) as mock_post:
            with patch.object(proxy.CachedPrivacyShield, 'process_request', return_value=("", {})):
                with patch.object(proxy.CachedPrivacyShield, 'process_response', return_value='{"text": "Hello world"}'):
                    client.post(
                        "/chat/completions",
                        json={"message": "Hello"},
                        headers={
                            "Authorization": "Bearer test-api-key-123",
                            "Content-Type": "application/json",
                            "X-Custom-Header": "value"
                        }
                    )
                    
                    # Check that headers were forwarded (except host and content-length)
                    call_kwargs = mock_post.call_args.kwargs
                    headers = call_kwargs.get('headers', {})
                    assert "Content-Type" in headers
                    assert "X-Custom-Header" in headers
                    assert "host" in headers
    
    def test_proxy_handles_target_api_key(self, client, monkeypatch):
        # Set target API key
        monkeypatch.setenv("TARGET_API_KEY", "target-key-456")
        
        # Reinitialize the module
        import importlib
        importlib.reload(proxy)
        
        # Create new test client with reloaded module
        test_client = TestClient(proxy.app)
        
        # Mock the httpx client
        mock_response = MagicMock()
        mock_response.content = b'{"text": "Hello world"}'
        mock_response.status_code = 200
        
        with patch.object(proxy.http_client, 'post', new=AsyncMock(return_value=mock_response)) as mock_post:
            with patch.object(proxy.CachedPrivacyShield, 'process_request', return_value=("", {})):
                with patch.object(proxy.CachedPrivacyShield, 'process_response', return_value='{"text": "Hello world"}'):
                    test_client.post(
                        "/chat/completions",
                        json={"message": "Hello"},
                        headers={"Authorization": "Bearer test-api-key-123"}
                    )
                    
                    # Check that Authorization header was set for target
                    call_kwargs = mock_post.call_args.kwargs
                    headers = call_kwargs.get('headers', {})
                    assert headers.get("Authorization") == "Bearer target-key-456"


class TestSessionManagement:
    def test_session_created_for_authorization_header(self, client):
        auth_header = "Bearer test-token"
        expected_hash = hashlib.sha256(auth_header.encode()).hexdigest()
        
        # Mock the httpx client
        mock_response = MagicMock()
        mock_response.content = b'{"text": "Hello world"}'
        mock_response.status_code = 200
        
        with patch.object(proxy.http_client, 'post', new=AsyncMock(return_value=mock_response)):
            with patch.object(proxy.CachedPrivacyShield, 'process_request', return_value=("", {})):
                with patch.object(proxy.CachedPrivacyShield, 'process_response', return_value='{"text": "Hello world"}'):
                    client.post(
                        "/chat/completions",
                        json={"message": "Hello"},
                        headers={"Authorization": auth_header}
                    )
                    
                    # Check that session was created
                    assert expected_hash in proxy.sessions
    
    def test_session_created_for_client_ip_when_no_auth(self, client):
        # Mock client info
        with patch('fastapi.Request.client', new=MagicMock(host="192.168.1.1")):

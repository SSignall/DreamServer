"""
=== GENERATED TEST FILE — NEEDS REVIEW ===
Generated: 2026-03-08T02:34:20.074474+00:00
Source: extensions/services/privacy_shield/proxy.py
Generator: Qwen3-Coder (local GPU)

This file was auto-generated and has NOT been reviewed or run.
Review before using. May need fixture adjustments or mock updates.
================================================================
"""

import pytest
import os
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from fastapi.testclient import TestClient
from fastapi import HTTPException
from httpx import Response as HttpxResponse
import hashlib
import secrets

# Mock dependencies before importing the module
with patch('pii_scrubber.PrivacyShield'):
    with patch('cachetools.TTLCache'):
        from extensions.services.privacy_shield.proxy import (
            app,
            SHIELD_API_KEY,
            verify_api_key,
            get_session,
            CachedPrivacyShield,
            sessions,
            CACHE_ENABLED,
            CACHE_SIZE,
            TARGET_API_BASE,
            TARGET_API_KEY,
            PORT,
            http_client
        )

# Create test client
client = TestClient(app)


class MockPrivacyShield:
    def __init__(self, *args, **kwargs):
        self.detector = MagicMock()
        self.detector.scrub = MagicMock(return_value="scrubbed_text")
        self.detector.get_stats = MagicMock(return_value={'unique_pii_count': 5})
    
    def process_request(self, text):
        return "scrubbed_text", {"pii_found": True}
    
    def process_response(self, text):
        return "restored_text"


class MockCachedPrivacyShield:
    def __init__(self, *args, **kwargs):
        self.detector = MagicMock()
        self.detector.scrub = MagicMock(return_value="cached_scrubbed_text")
        self.detector.get_stats = MagicMock(return_value={'unique_pii_count': 3})
    
    def process_request(self, text):
        return "cached_scrubbed_text", {"pii_found": False}
    
    def process_response(self, text):
        return "cached_restored_text"


@pytest.fixture(autouse=True)
def reset_globals():
    """Reset global state before each test."""
    # Clear sessions cache
    sessions.clear()
    
    # Reset environment variables
    os.environ['SHIELD_API_KEY'] = 'test-api-key-123'
    os.environ['TARGET_API_URL'] = 'http://test-api:8000/v1'
    os.environ['TARGET_API_KEY'] = 'target-key-456'
    os.environ['SHIELD_PORT'] = '8085'
    os.environ['PII_CACHE_ENABLED'] = 'true'
    os.environ['PII_CACHE_SIZE'] = '100'
    os.environ['PII_CACHE_TTL'] = '300'
    os.environ['SHIELD_SESSION_MAXSIZE'] = '10000'
    os.environ['SHIELD_SESSION_TTL'] = '3600'


@pytest.fixture
def mock_http_client():
    """Mock httpx.AsyncClient."""
    with patch('extensions.services.privacy_shield.proxy.http_client') as mock_client:
        yield mock_client


@pytest.fixture
def mock_privacy_shield():
    """Mock CachedPrivacyShield."""
    with patch('extensions.services.privacy_shield.proxy.CachedPrivacyShield', MockCachedPrivacyShield):
        yield MockCachedPrivacyShield


def test_health_endpoint():
    """Test health check endpoint returns expected structure."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "api-privacy-shield"
    assert data["version"] == "0.2.0"
    assert data["target_api"] == "http://test-api:8000/v1"
    assert data["cache_enabled"] is True
    assert "active_sessions" in data


def test_stats_endpoint():
    """Test stats endpoint returns expected structure."""
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "active_sessions" in data
    assert "total_pii_scrubbed" in data
    assert data["cache_enabled"] is True
    assert data["cache_size"] == 100


def test_verify_api_key_valid():
    """Test API key verification with valid credentials."""
    from extensions.services.privacy_shield.proxy import security_scheme
    
    # Create a request with valid credentials
    request = MagicMock()
    request.headers = {"authorization": "Bearer test-api-key-123"}
    
    async def run():
        credentials = await security_scheme(request)
        return await verify_api_key(credentials)
    
    result = asyncio.run(run())
    assert result == "test-api-key-123"


def test_verify_api_key_invalid():
    """Test API key verification with invalid credentials."""
    from extensions.services.privacy_shield.proxy import security_scheme
    
    # Create a request with invalid credentials
    request = MagicMock()
    request.headers = {"authorization": "Bearer invalid-key"}
    
    async def run():
        credentials = await security_scheme(request)
        await verify_api_key(credentials)
    
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(run())
    
    assert exc_info.value.status_code == 403
    assert "Invalid API key" in exc_info.value.detail


def test_verify_api_key_missing_credentials():
    """Test API key verification with missing credentials."""
    from extensions.services.privacy_shield.proxy import security_scheme
    
    # Create a request with no authorization header
    request = MagicMock()
    request.headers = {}
    
    async def run():
        credentials = await security_scheme(request)
        await verify_api_key(credentials)
    
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(run())
    
    assert exc_info.value.status_code == 403


def test_proxy_post_request_success(mock_http_client, mock_privacy_shield):
    """Test successful POST request through proxy."""
    # Setup mock response
    mock_response = MagicMock(spec=HttpxResponse)
    mock_response.status_code = 200
    mock_response.content = b'{"text": "Hello, world!"}'
    mock_response.headers = {"content-type": "application/json"}
    mock_http_client.post.return_value = mock_response
    
    # Make request with auth header
    response = client.post(
        "/chat/completions",
        json={"message": "Hello"},
        headers={"Authorization": "Bearer test-api-key-123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "restored_text" in str(data) or "cached_restored_text" in str(data)
    assert "X-Privacy" in response.headers


def test_proxy_get_request_success(mock_http_client, mock_privacy_shield):
    """Test successful GET request through proxy."""
    # Setup mock response
    mock_response = MagicMock(spec=HttpxResponse)
    mock_response.status_code = 200
    mock_response.content = b'{"data": "test"}'
    mock_response.headers = {"content-type": "application/json"}
    mock_http_client.get.return_value = mock_response
    
    # Make request with auth header
    response = client.get(
        "/models",
        headers={"Authorization": "Bearer test-api-key-123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_proxy_missing_auth_header():
    """Test proxy endpoint without authentication."""
    response = client.post("/chat/completions", json={"message": "test"})
    assert response.status_code == 403


def test_proxy_invalid_auth_header():
    """Test proxy endpoint with invalid authentication."""
    response = client.post(
        "/chat/completions",
        json={"message": "test"},
        headers={"Authorization": "Bearer invalid-key"}
    )
    assert response.status_code == 403


def test_proxy_target_api_url():
    """Test that target API URL is correctly constructed."""
    os.environ['TARGET_API_URL'] = 'http://custom-api:9000/api'
    
    # Need to reinitialize app to pick up new env vars
    with patch('extensions.services.privacy_shield.proxy.http_client') as mock_client:
        mock_response = MagicMock(spec=HttpxResponse)
        mock_response.status_code = 200
        mock_response.content = b'{"result": "ok"}'
        mock_client.post.return_value = mock_response
        
        response = client.post(
            "/chat/completions",
            json={"message": "test"},
            headers={"Authorization": "Bearer test-api-key-123"}
        )
        
        # Verify the target URL used in the request
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "http://custom-api:9000/api/chat/completions"


def test_proxy_target_api_key_header(mock_http_client):
    """Test that target API key is correctly set in headers."""
    os.environ['TARGET_API_KEY'] = 'custom-target-key'
    
    mock_response = MagicMock(spec=HttpxResponse)
    mock_response.status_code = 200
    mock_response.content = b'{"result": "ok"}'
    mock_http_client.post.return_value = mock_response
    
    response = client.post(
        "/chat/completions",
        json={"message": "test"},
        headers={"Authorization": "Bearer test-api-key-123"}
    )
    
    # Verify the Authorization header was set for target API
    call_args = mock_client.post.call_args
    headers = call_args[1]['headers']
    assert headers.get("Authorization") == "Bearer custom-target-key"


def test_proxy_no_target_api_key(mock_http_client):
    """Test that no target API key is set when not configured."""
    os.environ['TARGET_API_KEY'] = 'not-needed'
    
    mock_response = MagicMock(spec=HttpxResponse)
    mock_response.status_code =

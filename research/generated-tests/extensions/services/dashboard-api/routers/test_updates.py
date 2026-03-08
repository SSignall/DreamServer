"""
=== GENERATED TEST FILE — NEEDS REVIEW ===
Generated: 2026-03-08T01:58:21.770728+00:00
Source: extensions/services/dashboard-api/routers/updates.py
Generator: Qwen3-Coder (local GPU)

This file was auto-generated and has NOT been reviewed or run.
Review before using. May need fixture adjustments or mock updates.
================================================================
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from datetime import datetime, timezone
from pathlib import Path
import json

# Mock dependencies before importing the router
pytestmark = pytest.mark.asyncio

# Fixtures
@pytest.fixture
def mock_install_dir(tmp_path):
    """Create a temporary install directory with .version file."""
    version_file = tmp_path / ".version"
    version_file.write_text("1.2.3")
    
    with patch("extensions.services.dashboard-api.routers.updates.INSTALL_DIR", str(tmp_path)):
        yield tmp_path

@pytest.fixture
def mock_version_file(mock_install_dir):
    """Create .version file in mock install dir."""
    version_file = mock_install_dir / ".version"
    version_file.write_text("1.2.3")
    return version_file

@pytest.fixture
def mock_script_path(tmp_path):
    """Create a mock update script."""
    script_dir = tmp_path / "scripts"
    script_dir.mkdir(parents=True, exist_ok=True)
    script_path = script_dir / "dream-update.sh"
    script_path.write_text("#!/bin/bash\necho 'Update script'")
    script_path.chmod(0o755)
    
    with patch("extensions.services.dashboard-api.routers.updates.Path") as mock_path:
        # Make Path(INSTALL_DIR).parent / "scripts" / "dream-update.sh" resolve to our script
        mock_path.return_value = MagicMock()
        mock_path.return_value.__truediv__.side_effect = lambda x: MagicMock(__str__=lambda: str(tmp_path / x))
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.__str__.return_value = str(script_path)
        
        # Patch the specific paths used in the function
        with patch("extensions.services.dashboard-api.routers.updates.Path") as mock_path_class:
            mock_instance = MagicMock()
            mock_instance.__truediv__.side_effect = lambda x: MagicMock(
                __str__=lambda: str(tmp_path / x),
                exists=lambda: x == "dream-update.sh" or x == "install.sh"
            )
            mock_instance.exists.return_value = True
            mock_instance.__str__.return_value = str(script_path)
            
            # Handle the specific path construction in trigger_update
            def path_side_effect(*args):
                if "scripts" in args:
                    return MagicMock(
                        __truediv__=lambda self, x: MagicMock(
                            __str__=lambda: str(tmp_path / "scripts" / x),
                            exists=lambda: x == "dream-update.sh"
                        ),
                        exists=lambda: True
                    )
                return mock_instance
            
            mock_path_class.side_effect = path_side_effect
            yield script_path

@pytest.fixture
def mock_verify_api_key():
    """Mock the verify_api_key dependency."""
    with patch("extensions.services.dashboard-api.routers.updates.verify_api_key") as mock:
        mock.return_value = "valid_api_key"
        yield mock

@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run for update tests."""
    with patch("extensions.services.dashboard-api.routers.updates.subprocess.run") as mock_run:
        yield mock_run

# Tests for /api/version
class TestGetVersion:
    @pytest.mark.asyncio
    async def test_get_version_success(self, mock_version_file, mock_verify_api_key):
        """Test successful version retrieval with no update available."""
        with patch("urllib.request.urlopen") as mock_urlopen:
            # Mock GitHub API response
            mock_response = Mock()
            mock_response.read.return_value = json.dumps({
                "tag_name": "v1.2.3",
                "html_url": "https://github.com/Light-Heart-Labs/DreamServer/releases/tag/v1.2.3"
            }).encode()
            mock_urlopen.return_value.__enter__.return_value = mock_response
            
            from extensions.services.dashboard_api.routers.updates import get_version
            result = await get_version()
            
            assert result["current"] == "1.2.3"
            assert result["latest"] == "1.2.3"
            assert result["update_available"] is False
            assert result["changelog_url"] is not None
            assert "checked_at" in result

    @pytest.mark.asyncio
    async def test_get_version_update_available(self, mock_version_file, mock_verify_api_key):
        """Test version check when update is available."""
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_response = Mock()
            mock_response.read.return_value = json.dumps({
                "tag_name": "v1.2.4",
                "html_url": "https://github.com/Light-Heart-Labs/DreamServer/releases/tag/v1.2.4"
            }).encode()
            mock_urlopen.return_value.__enter__.return_value = mock_response
            
            from extensions.services.dashboard_api.routers.updates import get_version
            result = await get_version()
            
            assert result["update_available"] is True
            assert result["latest"] == "1.2.4"

    @pytest.mark.asyncio
    async def test_get_version_network_error(self, mock_version_file, mock_verify_api_key):
        """Test version check when network fails."""
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = Exception("Network error")
            
            from extensions.services.dashboard_api.routers.updates import get_version
            result = await get_version()
            
            assert result["current"] == "1.2.3"
            assert result["latest"] is None
            assert result["update_available"] is False

    @pytest.mark.asyncio
    async def test_get_version_no_version_file(self, mock_verify_api_key, tmp_path):
        """Test version check when .version file doesn't exist."""
        with patch("extensions.services.dashboard_api.routers.updates.INSTALL_DIR", str(tmp_path)):
            with patch("urllib.request.urlopen") as mock_urlopen:
                mock_response = Mock()
                mock_response.read.return_value = json.dumps({
                    "tag_name": "v1.0.0",
                    "html_url": "https://github.com/Light-Heart-Labs/DreamServer/releases/tag/v1.0.0"
                }).encode()
                mock_urlopen.return_value.__enter__.return_value = mock_response
                
                from extensions.services.dashboard_api.routers.updates import get_version
                result = await get_version()
                
                assert result["current"] == "0.0.0"
                assert result["latest"] == "1.0.0"
                assert result["update_available"] is True

# Tests for /api/releases/manifest
class TestGetReleaseManifest:
    @pytest.mark.asyncio
    async def test_get_release_manifest_success(self, mock_verify_api_key):
        """Test successful release manifest retrieval."""
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_response = Mock()
            mock_response.read.return_value = json.dumps([
                {
                    "tag_name": "v1.2.3",
                    "published_at": "2023-01-01T00:00:00Z",
                    "name": "Release 1.2.3",
                    "body": "Release notes",
                    "html_url": "https://github.com/Light-Heart-Labs/DreamServer/releases/tag/v1.2.3",
                    "prerelease": False
                }
            ]).encode()
            mock_urlopen.return_value.__enter__.return_value = mock_response
            
            from extensions.services.dashboard_api.routers.updates import get_release_manifest
            result = await get_release_manifest()
            
            assert len(result["releases"]) == 1
            assert result["releases"][0]["version"] == "1.2.3"
            assert "checked_at" in result

    @pytest.mark.asyncio
    async def test_get_release_manifest_network_error(self, mock_verify_api_key, mock_install_dir):
        """Test release manifest when network fails."""
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = Exception("Network error")
            
            from extensions.services.dashboard_api.routers.updates import get_release_manifest
            result = await get_release_manifest()
            
            assert len(result["releases"]) == 1
            assert result["releases"][0]["version"] == "1.2.3"
            assert "error" in result

# Tests for /api/update
class TestTriggerUpdate:
    @pytest.mark.asyncio
    async def test_trigger_update_check_success(self, mock_script_path, mock_verify_api_key):
        """Test successful update check."""
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 2  # Update available
            mock_result.stdout = "Update available"
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            
            from models import UpdateAction
            from extensions.services.dashboard_api.routers.updates import trigger_update
            
            action = UpdateAction(action="check")
            result = await trigger_update(action, Mock())
            
            assert result["success"] is True
            assert result["update_available"] is True
            assert "output" in result

    @pytest.mark.asyncio
    async def test_trigger_update_check_timeout(self, mock_script_path, mock_verify_api_key):
        """Test update check timeout."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("script.sh", 30)
            
            from models import UpdateAction
            from extensions.services.dashboard_api.routers.updates import trigger_update
            
            action = UpdateAction(action="check")
            
            with pytest.raises(HTTPException

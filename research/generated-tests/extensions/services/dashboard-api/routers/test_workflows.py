"""
=== GENERATED TEST FILE — NEEDS REVIEW ===
Generated: 2026-03-08T01:58:58.115399+00:00
Source: extensions/services/dashboard-api/routers/workflows.py
Generator: Qwen3-Coder (local GPU)

This file was auto-generated and has NOT been reviewed or run.
Review before using. May need fixture adjustments or mock updates.
================================================================
"""

import pytest
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient

# Assuming the router is imported from the module under test
# from extensions.services.dashboard_api.routers.workflows import router, load_workflow_catalog, get_n8n_workflows, check_workflow_dependencies, check_n8n_available
from extensions.services.dashboard_api.routers import workflows


@pytest.fixture
def client():
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(workflows.router)
    return TestClient(app)


@pytest.fixture
def mock_api_key():
    with patch("extensions.services.dashboard_api.routers.workflows.verify_api_key") as mock:
        mock.return_value = "valid-key"
        yield mock


@pytest.fixture
def mock_load_workflow_catalog():
    with patch("extensions.services.dashboard_api.routers.workflows.load_workflow_catalog") as mock:
        mock.return_value = {
            "workflows": [
                {
                    "id": "test-wf-1",
                    "name": "Test Workflow",
                    "description": "A test workflow",
                    "icon": "test-icon",
                    "category": "general",
                    "dependencies": ["ollama"],
                    "file": "test-wf-1.json",
                    "setupTime": "2 min",
                    "diagram": {},
                    "featured": True
                }
            ],
            "categories": {"general": "General"}
        }
        yield mock


@pytest.fixture
def mock_get_n8n_workflows():
    with patch("extensions.services.dashboard_api.routers.workflows.get_n8n_workflows") as mock:
        mock.return_value = [
            {
                "id": "n8n-wf-1",
                "name": "Test Workflow",
                "active": True,
                "statistics": {"executions": {"total": 42}}
            }
        ]
        yield mock


@pytest.fixture
def mock_check_workflow_dependencies():
    with patch("extensions.services.dashboard_api.routers.workflows.check_workflow_dependencies") as mock:
        mock.return_value = {"ollama": True}
        yield mock


@pytest.fixture
def mock_check_n8n_available():
    with patch("extensions.services.dashboard_api.routers.workflows.check_n8n_available") as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def mock_services():
    with patch("extensions.services.dashboard_api.routers.workflows.SERVICES") as mock:
        mock.__contains__.side_effect = lambda x: x in ["llama-server"]
        yield mock


@pytest.fixture
def mock_check_service_health():
    with patch("extensions.services.dashboard_api.routers.workflows.check_service_health") as mock:
        mock.return_value = AsyncMock(status="healthy")
        yield mock


# --- Tests for /api/workflows ---

def test_api_workflows_success(
    client, mock_api_key, mock_load_workflow_catalog, mock_get_n8n_workflows,
    mock_check_workflow_dependencies, mock_check_n8n_available
):
    response = client.get("/api/workflows")
    assert response.status_code == 200
    data = response.json()
    assert "workflows" in data
    assert len(data["workflows"]) == 1
    wf = data["workflows"][0]
    assert wf["id"] == "test-wf-1"
    assert wf["name"] == "Test Workflow"
    assert wf["status"] == "active"
    assert wf["installed"] is True
    assert wf["active"] is True
    assert wf["n8nId"] == "n8n-wf-1"
    assert wf["executions"] == 42
    assert wf["allDependenciesMet"] is True


def test_api_workflows_catalog_file_not_found(
    client, mock_api_key,
    mock_get_n8n_workflows,
    mock_check_workflow_dependencies,
    mock_check_n8n_available
):
    with patch("extensions.services.dashboard_api.routers.workflows.load_workflow_catalog") as mock:
        mock.return_value = workflows.DEFAULT_WORKFLOW_CATALOG
        response = client.get("/api/workflows")
        assert response.status_code == 200
        data = response.json()
        assert data["catalogSource"] == str(workflows.WORKFLOW_CATALOG_FILE)


def test_api_workflows_n8n_not_responding(
    client, mock_api_key, mock_load_workflow_catalog,
    mock_get_n8n_workflows, mock_check_workflow_dependencies
):
    with patch("extensions.services.dashboard_api.routers.workflows.check_n8n_available") as mock:
        mock.return_value = False
        mock_get_n8n_workflows.return_value = []
        response = client.get("/api/workflows")
        assert response.status_code == 200
        data = response.json()
        assert data["n8nAvailable"] is False


def test_api_workflows_dependency_failure(
    client, mock_api_key, mock_load_workflow_catalog,
    mock_get_n8n_workflows, mock_check_workflow_dependencies
):
    mock_check_workflow_dependencies.return_value = {"ollama": False}
    response = client.get("/api/workflows")
    assert response.status_code == 200
    data = response.json()
    wf = data["workflows"][0]
    assert wf["dependencyStatus"]["ollama"] is False
    assert wf["allDependenciesMet"] is False


def test_api_workflows_dependency_alias_resolution(
    client, mock_api_key, mock_load_workflow_catalog,
    mock_get_n8n_workflows, mock_check_service_health
):
    # Override catalog to use 'ollama' dependency
    with patch("extensions.services.dashboard_api.routers.workflows.load_workflow_catalog") as mock:
        mock.return_value = {
            "workflows": [
                {
                    "id": "test-wf-1",
                    "name": "Test Workflow",
                    "description": "A test workflow",
                    "icon": "test-icon",
                    "category": "general",
                    "dependencies": ["ollama"],
                    "file": "test-wf-1.json",
                    "setupTime": "2 min",
                    "diagram": {},
                    "featured": True
                }
            ],
            "categories": {}
        }
        with patch("extensions.services.dashboard_api.routers.workflows.check_workflow_dependencies") as mock_deps:
            mock_deps.return_value = {"ollama": True}
            response = client.get("/api/workflows")
            assert response.status_code == 200
            # Verify alias resolution happened (mock_deps should have been called with ['ollama'])
            mock_deps.assert_called_once()


# --- Tests for /api/workflows/{workflow_id}/enable ---

def test_enable_workflow_success(
    client, mock_api_key,
    mock_load_workflow_catalog,
    mock_check_workflow_dependencies
):
    with patch("extensions.services.dashboard_api.routers.workflows.WORKFLOW_DIR") as mock_dir:
        mock_file = MagicMock()
        mock_file.resolve.return_value = mock_file
        mock_file.__str__.return_value = str(mock_dir.resolve.return_value / "test-wf-1.json")
        mock_dir.__truediv__.return_value = mock_file
        mock_dir.resolve.return_value = mock_dir

        with patch("extensions.services.dashboard_api.routers.workflows.open", create=True) as mock_open:
            mock_open.return_value.__enter__.return_value = MagicMock()
            response = client.post("/api/workflows/test-wf-1/enable")
            assert response.status_code == 200


def test_enable_workflow_invalid_id_format(client, mock_api_key):
    response = client.post("/api/workflows/invalid id!/enable")
    assert response.status_code == 400
    assert "Invalid workflow ID format" in response.json()["detail"]


def test_enable_workflow_not_found(client, mock_api_key):
    with patch("extensions.services.dashboard_api.routers.workflows.load_workflow_catalog") as mock:
        mock.return_value = {"workflows": []}
        response = client.post("/api/workflows/nonexistent/enable")
        assert response.status_code == 404
        assert "Workflow not found" in response.json()["detail"]


def test_enable_workflow_missing_dependencies(client, mock_api_key, mock_load_workflow_catalog):
    with patch("extensions.services.dashboard_api.routers.workflows.check_workflow_dependencies") as mock:
        mock.return_value = {"ollama": False}
        response = client.post("/api/workflows/test-wf-1/enable")
        assert response.status_code == 400
        assert "Missing dependencies" in response.json()["detail"]


def test_enable_workflow_security_path_traversal(client, mock_api_key, mock_load_workflow_catalog):
    with patch("extensions.services.dashboard_api.routers.workflows.WORKFLOW_DIR") as mock_dir:
        mock_file = MagicMock()
        resolved_path = MagicMock()
        resolved_path.__str__.return_value = "/etc/passwd"
        mock_file.resolve.return_value = resolved_path
        mock_dir.__truediv__.return_value = mock_file
        mock_dir.resolve.return_value = MagicMock()
        mock_dir.resolve.return_value.__str__.return_value = "/safe/path"

        response = client.post("/api/workflows/test-wf-1/enable")
        assert response.status_code == 400
        assert "Invalid workflow file path" in response.json()["detail"] or response.status_code == 500


def test_enable_workflow_file_not_found(client, mock_api_key, mock_load_workflow_catalog):
    with patch("extensions.services.dashboard_api.routers.workflows.WORKFLOW_DIR") as mock_dir:
        mock_file = MagicMock()
        mock_file.resolve.return_value = mock_file
        mock_file.__str__.return_value = str(mock_dir.resolve.return_value / "test-wf-1.json")

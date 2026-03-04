"""Tests for config.py — manifest loading and service discovery."""

import pytest

from config import load_extension_manifests, _read_manifest_file


VALID_MANIFEST = """\
schema_version: dream.services.v1
service:
  id: test-service
  name: Test Service
  port: 8080
  health: /health
  gpu_backends: [amd, nvidia]
  external_port_default: 8080
features:
  - id: test-feature
    name: Test Feature
    icon: Zap
    category: inference
    gpu_backends: [amd, nvidia]
"""


class TestReadManifestFile:

    def test_reads_yaml(self, tmp_path):
        f = tmp_path / "manifest.yaml"
        f.write_text(VALID_MANIFEST)
        data = _read_manifest_file(f)
        assert data["schema_version"] == "dream.services.v1"
        assert data["service"]["id"] == "test-service"

    def test_reads_json(self, tmp_path):
        import json
        f = tmp_path / "manifest.json"
        f.write_text(json.dumps({
            "schema_version": "dream.services.v1",
            "service": {"id": "json-svc", "name": "JSON", "port": 9090},
        }))
        data = _read_manifest_file(f)
        assert data["service"]["id"] == "json-svc"

    def test_rejects_non_dict_root(self, tmp_path):
        f = tmp_path / "manifest.yaml"
        f.write_text("- just\n- a\n- list\n")
        with pytest.raises(ValueError, match="object"):
            _read_manifest_file(f)


class TestLoadExtensionManifests:

    def test_loads_valid_manifest(self, tmp_path):
        svc_dir = tmp_path / "test-service"
        svc_dir.mkdir()
        (svc_dir / "manifest.yaml").write_text(VALID_MANIFEST)

        services, features = load_extension_manifests(tmp_path, "nvidia")
        assert "test-service" in services
        assert services["test-service"]["port"] == 8080
        assert services["test-service"]["name"] == "Test Service"
        assert services["test-service"]["health"] == "/health"
        assert len(features) == 1
        assert features[0]["id"] == "test-feature"

    def test_skips_wrong_schema_version(self, tmp_path):
        svc_dir = tmp_path / "old-service"
        svc_dir.mkdir()
        (svc_dir / "manifest.yaml").write_text(
            "schema_version: dream.services.v0\nservice:\n  id: old\n  port: 80\n"
        )

        services, features = load_extension_manifests(tmp_path, "nvidia")
        assert len(services) == 0

    def test_filters_by_gpu_backend(self, tmp_path):
        svc_dir = tmp_path / "nvidia-only"
        svc_dir.mkdir()
        (svc_dir / "manifest.yaml").write_text(
            "schema_version: dream.services.v1\n"
            "service:\n  id: nvidia-only\n  name: NVIDIA Only\n  port: 80\n"
            "  gpu_backends: [nvidia]\n"
        )

        services, _ = load_extension_manifests(tmp_path, "amd")
        assert len(services) == 0

        services, _ = load_extension_manifests(tmp_path, "nvidia")
        assert "nvidia-only" in services

    def test_empty_directory(self, tmp_path):
        services, features = load_extension_manifests(tmp_path, "nvidia")
        assert services == {}
        assert features == []

    def test_nonexistent_directory(self, tmp_path):
        missing = tmp_path / "does-not-exist"
        services, features = load_extension_manifests(missing, "nvidia")
        assert services == {}
        assert features == []

    def test_features_filtered_by_gpu(self, tmp_path):
        svc_dir = tmp_path / "mixed"
        svc_dir.mkdir()
        (svc_dir / "manifest.yaml").write_text(
            "schema_version: dream.services.v1\n"
            "service:\n  id: mixed\n  name: Mixed\n  port: 80\n"
            "  gpu_backends: [amd, nvidia]\n"
            "features:\n"
            "  - id: amd-feat\n    name: AMD Feature\n    gpu_backends: [amd]\n"
            "  - id: both-feat\n    name: Both Feature\n    gpu_backends: [amd, nvidia]\n"
        )

        _, features = load_extension_manifests(tmp_path, "nvidia")
        feature_ids = [f["id"] for f in features]
        assert "both-feat" in feature_ids
        assert "amd-feat" not in feature_ids

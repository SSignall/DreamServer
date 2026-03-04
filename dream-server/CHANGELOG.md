# Changelog

All notable changes to Dream Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [2.0.0] - 2026-03-03

### Added
- Documentation index (`docs/README.md`) for navigating 30+ doc files
- `.env.example` with all required and optional variables documented
- `docker-compose.override.yml` auto-include for custom service extensions
- Real shell function tests for `resolve_tier_config()` (replaces tautological Python tests)
- Dry-run reporting for phases 06, 07, 09, 10, 12
- `Makefile` with `lint`, `test`, `smoke`, `gate` targets
- ShellCheck integration in CI
- `CHANGELOG.md`, `CODE_OF_CONDUCT.md`, issue/PR templates

### Changed
- Modular installer: 2591-line monolith split into 6 libraries + 13 phases
- All services now core in `docker-compose.base.yml` (profiles removed)
- Models switched from AWQ to GGUF Q4_K_M quantization

### Fixed
- Tier error message now auto-updates when new tiers are added
- Phase 12 (health) no longer crashes in dry-run mode
- n8n timezone default changed from `America/New_York` to `UTC`
- Stale variable names in INTEGRATION-GUIDE.md
- Embeddings port in INTEGRATION-GUIDE.md (9103 → 8090)
- Purged all stale `--profile` references across codebase (12+ files)
- Purged all stale `docker-compose.yml` references in docs
- AWQ references in QUICKSTART.md updated to GGUF Q4_K_M
- `make lint` no longer silently swallows errors
- Makefile now uses `find` to discover all .sh files instead of hardcoded globs

### Removed
- Token Spy (service, docs, installer refs, systemd units, dashboard-api integration)
- `docker-compose.strix-halo.yml` (deprecated, merged into base + amd overlay)
- Tautological Python test suite (`test_installer.py`)
- `asyncpg` dependency from dashboard-api (was only used by Token Spy)

## [0.3.0-dev] - 2025-05-01

Initial development release with modular installer architecture.

# Dream Server Support Matrix

Last updated: 2026-03-02

## Support Tiers

- `Tier A` fully supported and actively tested in this repo
- `Tier B` partially supported (works in some paths, gaps remain)
- `Tier C` experimental or planned

## Platform Matrix

| Platform | GPU Path | Tier | Status |
|---|---|---|---|
| Linux (Ubuntu/Debian family) | NVIDIA (llama-server/CUDA) | Tier B | Installer path exists in `install-core.sh`; broader distro test matrix still pending |
| Linux (Strix Halo / AMD unified memory) | AMD (llama-server/ROCm) | Tier A | Primary path via `docker-compose.base.yml` + `docker-compose.amd.yml` |
| WSL2 (Windows) | NVIDIA via Docker Desktop + WSL2 | Tier B | Documented path; first-class Windows installer flow still maturing |
| Windows native installer UX | WSL2 delegated flow | Tier B | `installers/windows.ps1` now performs prerequisite checks, emits JSON preflight report, and delegates to WSL `install-core.sh` |
| macOS (Apple Silicon) | Metal/MLX-style local backend | Tier C | `installers/macos.sh` now runs preflight + doctor with actionable reports; runtime path still experimental |

## Current Truth

- If you need the most reliable experience today, use Linux with the Strix-Halo path in this repo.
- Linux + NVIDIA is supported but needs broader validation and CI matrix coverage.
- Windows delegated installer flow is available via WSL2 and Docker Desktop.
- macOS now has an actionable preflight path, but full local runtime remains experimental.
- Version baselines for triage are in `docs/KNOWN-GOOD-VERSIONS.md`.

## Next Milestones

1. Complete installer dispatch and platform modules.
2. Add CI smoke matrix for Linux NVIDIA/AMD and WSL logic checks.
3. Promote Windows/macOS paths from stubs to tested workflows.

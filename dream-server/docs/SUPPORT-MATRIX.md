# Dream Server Support Matrix

Last updated: 2026-03-04

## What Works Today

**Linux is the only platform where Dream Server fully installs and runs today.** macOS and Windows support is coming soon — the installers for those platforms currently provide system diagnostics and preflight checks only.

| Platform | Status | What you get today |
|----------|--------|-------------------|
| **Linux + AMD Strix Halo (ROCm)** | **Fully supported** | Complete install and runtime. Primary development platform. |
| **Linux + NVIDIA (CUDA)** | **Supported** | Complete install and runtime. Broader distro test matrix still expanding. |
| **macOS (Apple Silicon)** | **Coming soon** (target: mid-March 2026) | Preflight diagnostics and system readiness checks only. No runtime. |
| **Windows** | **Coming soon** (target: end of March 2026) | WSL2/Docker/GPU preflight checks only. No runtime. |

## Support Tiers

- `Tier A` — fully supported and actively tested in this repo
- `Tier B` — partially supported (works in some paths, gaps remain)
- `Tier C` — experimental or planned (installer diagnostics only, no runtime)

## Platform Matrix (detailed)

| Platform | GPU Path | Tier | Status |
|---|---|---|---|
| Linux (Ubuntu/Debian family) | NVIDIA (llama-server/CUDA) | Tier B | Installer path exists in `install-core.sh`; broader distro test matrix still pending |
| Linux (Strix Halo / AMD unified memory) | AMD (llama-server/ROCm) | Tier A | Primary path via `docker-compose.base.yml` + `docker-compose.amd.yml` |
| WSL2 (Windows) | NVIDIA via Docker Desktop + WSL2 | Tier C | `installers/windows.ps1` runs prerequisite checks and emits JSON preflight report; full runtime not yet available |
| Windows native installer UX | WSL2 delegated flow | Tier C | Preflight and delegation plumbing in place; full install-to-running-stack flow under development |
| macOS (Apple Silicon) | Metal/MLX-style local backend | Tier C | `installers/macos.sh` runs preflight + doctor with actionable reports; full runtime under development |

## Current Truth

- **For a working setup today, use Linux** (AMD Strix Halo or NVIDIA).
- Linux + NVIDIA is supported but needs broader validation and CI matrix coverage.
- macOS and Windows installers run preflight diagnostics only — they **will not produce a running AI stack**.
- macOS full runtime support is targeted for mid-March 2026.
- Windows full runtime support is targeted for end of March 2026.
- Version baselines for triage are in `docs/KNOWN-GOOD-VERSIONS.md`.

## Roadmap

| Target | Milestone |
|--------|-----------|
| **Now** | Linux AMD + NVIDIA fully supported |
| **Mid-March 2026** | macOS Apple Silicon full runtime support |
| **End of March 2026** | Windows full runtime support |
| **Ongoing** | CI smoke matrix expansion for all platforms |

## Next Milestones

1. Ship macOS Apple Silicon full runtime (installer + compose + runtime parity).
2. Ship Windows full runtime (WSL2-delegated install through to running stack).
3. Add CI smoke matrix for Linux NVIDIA/AMD and WSL logic checks.
4. Promote macOS/Windows from Tier C to Tier B after validated real-hardware runs.

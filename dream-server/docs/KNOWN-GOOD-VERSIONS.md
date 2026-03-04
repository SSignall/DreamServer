# Known-Good Version Baselines

Use these as minimum practical baselines for support triage.

Last updated: 2026-03-02

## Windows (WSL2 delegated path)

- Windows 11 23H2+ (or Windows 10 with current WSL2 support)
- WSL default version: `2`
- Docker Desktop: 4.30+ (WSL2 backend enabled)
- NVIDIA driver (if using NVIDIA): current Studio/Game Ready with WSL support

Quick checks:

```powershell
wsl --status
docker version
docker info | findstr WSL
nvidia-smi
```

WSL checks:

```bash
docker info
nvidia-smi
```

## macOS (installer MVP / experimental runtime)

- macOS 14+ recommended
- Apple Silicon (arm64) strongly recommended
- Docker Desktop: 4.30+

Quick checks:

```bash
uname -m
docker version
df -g "$HOME"
```

## Linux (native)

- Ubuntu 22.04+ / Debian 12+ recommended
- Docker Engine + Compose v2
- NVIDIA: modern driver + toolkit
- AMD unified memory path: current amdgpu/ROCm-compatible kernel stack

Quick checks:

```bash
docker version
docker compose version
nvidia-smi || true
```

## Standard remediation snippets

- Start Docker daemon/Desktop.
- Ensure required compose overlays exist.
- Re-run preflight and doctor:

```bash
scripts/preflight-engine.sh --help
scripts/dream-doctor.sh
```

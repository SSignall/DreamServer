# Contributing to Dream Server

Thanks for building with us.

## Fast Path

If you want to add or extend services, start here:
- [docs/EXTENSIONS.md](docs/EXTENSIONS.md) — extending services (Docker containers, dashboards)
- [docs/INSTALLER-ARCHITECTURE.md](docs/INSTALLER-ARCHITECTURE.md) — modding the installer itself

That guide includes a practical "add a service in 30 minutes" path with templates and checks.

## Reporting Issues

Open an issue with:
- hardware details (GPU, RAM, OS)
- expected behavior
- actual behavior
- relevant logs (`docker compose logs`)

## Pull Requests

1. Fork and create a branch (`git checkout -b feature/my-change`)
2. Keep PR scope focused (one milestone-sized change)
3. Run validation locally
4. Submit PR with clear description, impact, and test evidence

## Contributor Validation Checklist

The fastest way to validate everything:
```bash
make gate    # lint + test + smoke + simulate
```

Or run individual steps:
```bash
make lint    # Shell syntax + Python compile checks
make test    # Tier map unit tests + installer contracts
make smoke   # Platform smoke tests
```

Full manual checklist:
```bash
# Shell/API checks
bash -n install.sh install-core.sh installers/lib/*.sh installers/phases/*.sh scripts/*.sh tests/*.sh 2>/dev/null || true
python3 -m py_compile dashboard-api/main.py dashboard-api/agent_monitor.py

# Unit tests
bash tests/test-tier-map.sh

# Integration/smoke checks
bash tests/integration-test.sh
bash tests/smoke/linux-amd.sh
bash tests/smoke/linux-nvidia.sh
bash tests/smoke/wsl-logic.sh
bash tests/smoke/macos-dispatch.sh
```

If your change touches dashboard frontend and Node is available:
```bash
cd dashboard
npm install
npm run lint
npm run build
```

## High-Value Contributions

- extension manifests and service integrations
- dashboard plugin/registry improvements
- installer mods: new tiers, themes, phases (see [docs/INSTALLER-ARCHITECTURE.md](docs/INSTALLER-ARCHITECTURE.md))
- installer portability and platform support
- workflow catalog quality and docs
- CI coverage and deterministic tests

## Style

- Bash: predictable, defensive, and syntax-clean
- YAML/JSON: stable keys, minimal noise, no tabs
- Docs: concrete commands and compatibility notes

## Questions

Open an issue and include enough context to reproduce the problem quickly.

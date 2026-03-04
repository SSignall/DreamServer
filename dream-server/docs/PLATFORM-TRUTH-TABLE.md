# Platform Truth Table

Use this file as the canonical source for launch claims.

Last updated: 2026-03-04

| Platform path | Claim | Current level | Target | Evidence required before promoting |
|---|---|---|---|---|
| Linux (native) | First-class installer/runtime path | Tier A/B (by GPU path) | — | `install-core.sh` real run on target hardware + smoke/integration + doctor report |
| Linux AMD unified (Strix) | Preferred AMD path | Tier A | — | Real install + runtime benchmarks + doctor/preflight clean |
| Linux NVIDIA | CUDA/llama-server path | Tier B | — | Real install + model load + runtime/throughput checks |
| macOS Apple Silicon | Preflight diagnostics only (no runtime) | Tier C | Mid-March 2026 | `installers/macos.sh` run + preflight/doctor pass + full runtime parity |
| Windows via WSL2 | Preflight checks only (no runtime) | Tier C | End of March 2026 | `installers/windows.ps1` run + WSL docker/GPU checks + delegated install producing running stack |
| Windows native runtime (no WSL) | Not supported | — | No target | Full backend/runtime architecture and packaging changes |

## Release language guardrails

- Safe to claim now:
  - Linux support (AMD Strix Halo + NVIDIA).
  - macOS and Windows **coming soon** with preflight diagnostics available now.
- Not safe to claim now:
  - macOS or Windows **support** (implies a working runtime, which does not exist yet).
  - Full native Windows runtime parity.
  - Full macOS runtime parity with Linux.

# Platform Truth Table

Use this file as the canonical source for launch claims.

Last updated: 2026-03-02

| Platform path | Claim | Current level | Evidence required before promoting |
|---|---|---|---|
| Linux (native) | First-class installer/runtime path | Tier A/B (by GPU path) | `install-core.sh` real run on target hardware + smoke/integration + doctor report |
| Linux AMD unified (Strix) | Preferred AMD path | Tier A | Real install + runtime benchmarks + doctor/preflight clean |
| Linux NVIDIA | CUDA/llama-server path | Tier B | Real install + model load + runtime/throughput checks |
| Windows via WSL2 | Supported delegated path | Tier B | `installers/windows.ps1` run on Windows host + WSL docker/GPU checks + delegated install success |
| macOS Apple Silicon | Experimental installer + diagnostics path | Tier C | `installers/macos.sh` run + preflight/doctor pass; runtime parity work still required |
| Windows native runtime (no WSL) | Not supported | Tier C | Full backend/runtime architecture and packaging changes |

## Release language guardrails

- Safe to claim now:
  - Linux support.
  - Windows support via WSL2.
  - macOS experimental/preview installer diagnostics.
- Not safe to claim now:
  - Full native Windows runtime parity.
  - Full macOS runtime parity with Linux.

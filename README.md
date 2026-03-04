<div align="center">

# Dream Server

**Your turnkey local AI stack. Buy hardware. Run installer. AI running.**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/Light-Heart-Labs/DreamServer)](https://github.com/Light-Heart-Labs/DreamServer/stargazers)
[![Release](https://img.shields.io/github/v/release/Light-Heart-Labs/DreamServer)](https://github.com/Light-Heart-Labs/DreamServer/releases)
[![Docker](https://img.shields.io/badge/Docker-Required-2496ED?logo=docker)](https://docs.docker.com/get-docker/)

</div>

---

## 5-Minute Quickstart

```bash
# One-line install (Linux/WSL)
curl -fsSL https://raw.githubusercontent.com/Light-Heart-Labs/DreamServer/main/dream-server/get-dream-server.sh | bash
```

Or manually:

```bash
git clone https://github.com/Light-Heart-Labs/DreamServer.git
cd DreamServer/dream-server
./install.sh
```

The installer auto-detects your GPU, picks the right model, generates secure passwords, and starts everything. Open **http://localhost:3000** and start chatting.

### 🚀 Instant Start (Bootstrap Mode)

By default, Dream Server uses **bootstrap mode** for instant gratification:

1. Starts immediately with a tiny 1.5B model (downloads in <1 minute)
2. You can start chatting within **2 minutes** of running the installer
3. The full model downloads in the background
4. When ready, hot-swap to the full model with zero downtime

No more staring at download bars. Start playing immediately.

### Windows

```powershell
# Download and run
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Light-Heart-Labs/DreamServer/main/install.ps1" -OutFile install.ps1
.\install.ps1
```

Windows installer checks prerequisites (WSL2, Docker, NVIDIA), then delegates to the Linux install path.

---

## What You Get

One installer. Full AI stack. Zero config.

| Component | Purpose | Port |
|-----------|---------|------|
| **llama-server** | LLM inference engine with continuous batching | 8080 |
| **Open WebUI** | Beautiful chat interface with history & web search | 3000 |
| **Dashboard** | Real-time GPU metrics, service health, model management | 3001 |
| **LiteLLM** | Multi-model API gateway | 4000 |
| **OpenClaw** | Autonomous AI agent framework | 7860 |
| **SearXNG** | Self-hosted web search | 8888 |
| **Perplexica** | Deep research engine | 3004 |
| **n8n** | Workflow automation (400+ integrations) | 5678 |
| **Qdrant** | Vector database for RAG | 6333 |
| **Whisper** | Speech-to-text | 9000 |
| **Kokoro** | Text-to-speech | 8880 |
| **ComfyUI** | Image generation | 8188 |
| **Privacy Shield** | PII scrubbing proxy | 8085 |

---

## Hardware Support

The installer **automatically detects your GPU** and selects the optimal configuration:

### NVIDIA GPUs

| Tier | VRAM | Model | Example GPUs |
|------|------|-------|--------------|
| Tier 1 | 8-11GB | qwen2.5-7b-instruct (Q4_K_M) | RTX 4060 Ti, RTX 3060 12GB |
| Tier 2 | 12-15GB | qwen2.5-14b-instruct (Q4_K_M) | RTX 3080 12GB, RTX 4070 Ti |
| Tier 3 | 16-23GB | qwen2.5-32b-instruct (Q4_K_M) | RTX 4090, RTX 3090, A5000 |
| Tier 4 | 24GB+ | qwen2.5-72b-instruct (Q4_K_M) | 2x RTX 4090, A100 |

### AMD APUs (Strix Halo)

| Tier | Unified Memory | Model | Hardware |
|------|---------------|-------|----------|
| SH_LARGE | 90GB+ | qwen3-coder-next (80B MoE) | Ryzen AI MAX+ 395 (96GB) |
| SH_COMPACT | 64-89GB | qwen3-30b-a3b (30B MoE) | Ryzen AI MAX+ 395 (64GB) |

All models auto-selected based on available VRAM. No manual configuration.

---

## Documentation

| | |
|---|---|
| [**Quickstart**](dream-server/QUICKSTART.md) | Step-by-step install guide with troubleshooting |
| [**FAQ**](dream-server/FAQ.md) | Common questions, hardware advice, configuration |
| [**Changelog**](dream-server/CHANGELOG.md) | Version history and release notes |
| [**Contributing**](dream-server/CONTRIBUTING.md) | How to contribute to Dream Server |
| [**Architecture**](dream-server/docs/INSTALLER-ARCHITECTURE.md) | Modular installer design deep dive |
| [**Extensions**](dream-server/docs/EXTENSIONS.md) | How to add custom services |

---

## Repository Structure

```
DreamServer/
├── dream-server/          # v2.0.0 - Production-ready local AI stack
│   ├── install.sh         # Linux/WSL installer
│   ├── docker-compose.*.yml
│   ├── installers/        # Modular installer (13 phases)
│   ├── extensions/        # Drop-in service integrations
│   └── docs/              # 30+ documentation files
│
├── install.sh             # Root installer (delegates to dream-server/)
├── install.ps1            # Windows installer
│
└── archive/               # Legacy projects (reference only)
    ├── guardian/          # Process watchdog
    ├── memory-shepherd/   # Agent memory lifecycle
    ├── token-spy/         # API cost monitoring
    └── docs/              # Historical documentation
```

**Shipping:** `dream-server/` is the v2.0.0 release.
**Archive:** Legacy tools from the [OpenClaw Collective](archive/COLLECTIVE.md) development period.

---

## What's New in v2.0.0

- **Modular installer**: 2591-line monolith → 6 libraries + 13 phases
- **Zero-config service discovery**: Extensions auto-register via manifests
- **AMD Strix Halo support**: ROCm 6.3 with unified memory models
- **Bootstrap mode**: Chat in 2 minutes, upgrade later
- **Comprehensive testing**: `make gate` runs lint + test + smoke + simulate
- **30+ docs**: Installation, troubleshooting, Windows guides, extensions

See [`dream-server/CHANGELOG.md`](dream-server/CHANGELOG.md) for full release notes.

---

## License

Apache 2.0 — Use it, modify it, ship it. See [LICENSE](LICENSE).

---

*Built by [The Collective](https://github.com/Light-Heart-Labs/DreamServer) — Android-17, Todd, and friends*

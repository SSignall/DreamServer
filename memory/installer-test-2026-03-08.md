# Dream Server Test Report — Installer (.143)

**Date:** 2026-03-08 01:50 EST  
**Tester:** Android-17  
**Target:** Tower 2 (192.168.0.143) — Ubuntu 24.04.3 LTS  
**Install Source:** dev/main (git@github-ssignall:SSignall/Lighthouse-AI-Dev.git)

---

## Bug Found: Installer Hangs on Existing Installation

**Severity:** MEDIUM  
**Component:** `dream-server/install-core.sh`

### Reproduction
1. Have existing installation at `/home/michael/dream-server`
2. Run `bash install.sh` from fresh clone
3. Installer detects existing install, logs `[WARN] Existing installation found`
4. **Process hangs indefinitely** — no visible prompt, no timeout, no progress

### Expected Behavior
- Prompt user: "Existing installation found. Overwrite? [y/N]"
- OR: Support `--force` / `--non-interactive` flags for automated testing
- OR: Timeout after reasonable period with error exit

### Actual Behavior
- Process stuck at Phase 1/6 for 5+ minutes
- No user input requested
- Had to `kill` process manually

### Log Snippet
```
[INFO] Detected OS: Ubuntu 24.04.3 LTS
[INFO] curl: curl 8.5.0 (x86_64-pc-linux-gnu) ...
[WARN] Existing installation found at /home/michael/dream-server
[HANG — no further output]
```

---

## Suggested Fix

Add to install-core.sh:
```bash
# Near existing install check
if [ -d "$INSTALL_DIR" ]; then
    if [ "${FORCE:-0}" = "1" ]; then
        rm -rf "$INSTALL_DIR"
    elif [ "${NONINTERACTIVE:-0}" = "1" ]; then
        echo "[ERROR] Existing installation found. Use FORCE=1 to overwrite."
        exit 1
    else
        read -p "Existing installation found. Overwrite? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        rm -rf "$INSTALL_DIR"
    fi
fi
```

---

## Clean Install Test (Fresh Directory)

**Test path:** `/tmp/dream-server-test/fresh-test/dream-server`

### Results by Phase

| Phase | Status | Notes |
|-------|--------|-------|
| 1/6 — Pre-flight | ✅ PASS | OS detection, curl check, dependency validation |
| Hardware Scan | ✅ PASS | Correctly detected RTX PRO 6000 Blackwell (95GB VRAM), 124GB RAM |
| Tier Classification | ✅ PASS | Auto-classified as NV_ULTRA, selected qwen3-coder-next |
| 2/6 — Feature Selection | ⚠️ BLOCKS | Waits indefinitely for user input (Full/Core/Custom) |

### Hardware Detection Output
```
[INFO] RAM: 124GB
[INFO] Available disk: 1143GB
[INFO] GPU: NVIDIA RTX PRO 6000 Blackwell Workstation Edition (97887MB VRAM) x1
[INFO] NVIDIA driver: 590
[INFO] Auto-detected tier: NV_ULTRA
[INFO] Compose selection: -f docker-compose.base.yml -f docker-compose.nvidia.yml
```

### Tier Assignment
```
CLASSIFICATION: TIER NV_ULTRA
  Model:   qwen3-coder-next
  Speed:   ~50 tokens/second
  Users:   10-20 concurrent comfortably
```

---

## Bug #2: No Non-Interactive Mode

**Severity:** MEDIUM  
**Component:** Phase 2 feature selection

### Issue
Installer cannot run unattended. No environment variable or flag to pre-select Full/Core/Custom mode.

### Expected
```bash
INSTALL_MODE=full bash install.sh   # Auto-select full stack
INSTALL_MODE=core bash install.sh   # Auto-select core only
```

### Actual
Process blocks at:
```
[1] Full Stack (recommended — just press Enter)
[2] Core Only
[3] Custom
```

---

## Environment Details

- **OS:** Ubuntu 24.04.3 LTS (Noble Numbat)
- **Shell:** bash 5.2.21
- **GPU:** NVIDIA RTX PRO 6000 Blackwell (95GB VRAM)
- **CPU:** AMD Ryzen 9 7950X3D 16-Core
- **RAM:** 124GB
- **Test directories:** 
  - `/tmp/dream-server-test` (clone)
  - `/tmp/dream-server-test/fresh-test` (clean install test)

---

## Recommendations

1. **Add `INSTALL_MODE` env var support** for non-interactive installs
2. **Add `FORCE=1` env var** to overwrite existing installations
3. **Add timeout to prompts** (e.g., 30s default to recommended option)
4. **Document non-interactive mode** for CI/CD use cases

---

## Files

- Test log: `/tmp/dream-server-test/fresh-test/dream-server/install-fresh.log` (87 lines, Phase 2 interrupted)

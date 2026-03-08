# 2026-03-08 — Dual GPU Detection Fix

## GitHub Issue #55 — Fixed

**Problem:** Hardware scan only displayed one GPU when system had multiple GPUs (e.g., RTX 3090 + RTX 4090).

User report showed:
```
| GPU: NVIDIA GeForce RTX 3090 |
| VRAM: 24GB |
```

But nvidia-smi showed two GPUs (3090 + 4090, 24GB + 24GB).

**Root Cause:** `detect-hardware.sh` line 296 used `head -1` to extract GPU name:
```bash
# Get first GPU name for display (all GPUs in a system are usually the same model)
gpu_name=$(echo "$nvidia_out" | awk -F',' '{gsub(/^ +| +$/,"",$1); print $1}' | head -1)
```

The incorrect assumption was that all GPUs in a system are the same model.

**Fix Applied:** Modified GPU name building logic in `detect-hardware.sh`:
- Single GPU: unchanged (existing behavior)
- Multiple GPUs: extract unique models, count occurrences
- Format: "NVIDIA GeForce RTX 3090 x2" for identical cards
- Format: "NVIDIA GeForce RTX 4090 + NVIDIA GeForce RTX 3090" for mixed cards

**Files Modified:**
- `dream-server/scripts/detect-hardware.sh` — multi-GPU name building

**Testing:**
- Mixed GPUs (3090 + 4090): ✓ Shows both models
- Identical GPUs (3090 x2): ✓ Shows "NVIDIA GeForce RTX 3090 x2"
- Single GPU: ✓ Unchanged behavior

**Commit:** `fix(detect-hardware): properly display multi-GPU setups`

## Current Status

- #55: Fixed, committed, ready for user verification
- Next: Monitor for user confirmation that fix works on their dual GPU system

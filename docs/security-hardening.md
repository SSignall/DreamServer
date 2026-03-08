# Security Hardening Checklist

**Purpose:** Track security fixes across Dream Server extensions and infrastructure.

## Current Status

- **Wave 4:** ✅ Complete
- **Wave 5:** ⏳ Pending (RVC, Bark, Ollama, LocalAI)

---

## Wave 4: Complete ✅

| Item | Status | Details |
|------|--------|---------|
| SearXNG secret key | ✅ Fixed | Auto-generated at install time via `openssl rand -hex 32` |
| OpenClaw gateway binding | ✅ Fixed | Localhost-only (`127.0.0.1`) via `gateway.bind: "loopback"` |
| Token-spy HTML embedding | ✅ Acceptable risk | Localhost-only dev tool; API key in page source acceptable |
| Container image pinning | ✅ Fixed | All pinned (searxng:2026.3.6, etc.) |
| ComfyUI AMD security opts | ✅ Fixed | Removed `seccomp:unconfined` and `SYS_PTRACE` |

---

## Wave 5: Pending ⏳

| Item | Priority | Files |
|------|----------|-------|
| RVC path traversal | MEDIUM | `extensions/services/rvc/` workflows |
| Bark voice preset validation | MEDIUM | `extensions/services/bark/` workflows |
| Ollama auth pattern | LOW | `extensions/services/ollama/` workflows |
| LocalAI JSON escaping | LOW | `extensions/services/localai/` workflows |

---

## Security Patterns to Apply

### 1. timingSafeEqual (Constant-Time Comparison)

**Vulnerable pattern (DO NOT use):**
```javascript
const len = Math.max(a.length, b.length);
for (let i = 0; i < len; i++) { ... }
```

**Secure pattern:**
```javascript
if (a.length !== b.length) return false;
// Then constant-time comparison
```

### 2. Path Traversal Protection

**Required validation:**
- Reject `..`, `/`, `\`, `%2e`, `%2f`, `%5c`
- Allowlist: `^[a-zA-Z0-9._-]+$`
- Max length: 100 chars

### 3. Input Validation

- Whitelist allowed values (e.g., Bark voice presets)
- Reject empty/null inputs where not allowed
- Enforce type constraints (string, number, array)

### 4. Error Handling

- Generic error messages (no internal details)
- Never expose stack traces
- Log internally, return user-friendly messages

---

## Review Process

1. **Flag issue** — Android-18 or QA team identifies vulnerability
2. **Assign wave** — Add to current pending wave
3. **Fix and commit** — Apply security pattern consistently
4. **Validate** — Run `make validate-ext`
5. **Push** — Merge to dev/main
6. **Verify CI** — Confirm automated tests pass

---

## Related Documentation

- [MISSIONS.md - Workstream 4: Hardening & Quality](../MISSIONS.md#workstream-4-hardening--quality)
- [MEMORY.md - Security Hardening Section](../MEMORY.md) (search "Security Hardening")

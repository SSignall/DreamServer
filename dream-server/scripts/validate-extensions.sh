#!/bin/bash
# ============================================================================
# Dream Server — Extension Validation Pipeline
# ============================================================================
# Validates all extensions in extensions/services/ for quality standards:
#   - Manifest presence and schema compliance
#   - Compose file syntax, healthchecks, security, pinned images
#   - Port conflict detection across all extensions
#   - Duplicate environment variable detection
#   - Docker network connectivity (dream-network)
#   - Health endpoint consistency (manifest vs compose)
#   - Dangerous volume mounts and hardcoded passwords
#
# Usage: bash scripts/validate-extensions.sh [--strict]
#   --strict: Treat warnings as failures (for CI gating)
#
# Exit 0 if all pass, 1 if any failures found
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
# Extensions live at repo root, not inside dream-server/
EXT_DIR="$(dirname "$PROJECT_DIR")/extensions/services"
STRICT=false

[[ "${1:-}" == "--strict" ]] && STRICT=true

# Colors (match test-service-registry.sh style)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0
SKIP=0

pass() {
    echo -e "  ${GREEN}PASS${NC}  $1"
    PASS=$((PASS + 1))
}

fail() {
    echo -e "  ${RED}FAIL${NC}  $1"
    [[ -n "${2:-}" ]] && echo -e "        ${RED}→ $2${NC}"
    FAIL=$((FAIL + 1))
}

warn() {
    echo -e "  ${YELLOW}WARN${NC}  $1"
    [[ -n "${2:-}" ]] && echo -e "        ${YELLOW}→ $2${NC}"
    WARN=$((WARN + 1))
    if $STRICT; then FAIL=$((FAIL + 1)); fi
}

skip() {
    echo -e "  ${YELLOW}SKIP${NC}  $1"
    SKIP=$((SKIP + 1))
}

header() {
    echo ""
    echo -e "${BOLD}${CYAN}[$1]${NC} ${BOLD}$2${NC}"
    echo -e "${CYAN}$(printf '%.0s─' {1..60})${NC}"
}

# ============================================================================
# Pre-flight: check dependencies
# ============================================================================
if ! python3 -c "import yaml" 2>/dev/null; then
    echo -e "${RED}ERROR: PyYAML not installed. Run: pip3 install pyyaml${NC}"
    exit 1
fi

# Collect all extension directories
extensions=()
for d in "$EXT_DIR"/*/; do
    [[ -d "$d" ]] && extensions+=("$(basename "$d")")
done

if [[ ${#extensions[@]} -eq 0 ]]; then
    echo -e "${RED}ERROR: No extensions found in $EXT_DIR${NC}"
    exit 1
fi

echo -e "${BOLD}Dream Server — Extension Validation${NC}"
echo -e "Found ${#extensions[@]} extensions to validate"

# ============================================================================
# CHECK 1: Manifest Presence
# ============================================================================
header "1/13" "Manifest Presence"

for ext in "${extensions[@]}"; do
    if [[ -f "$EXT_DIR/$ext/manifest.yaml" ]]; then
        pass "$ext/manifest.yaml exists"
    else
        fail "$ext/manifest.yaml missing" "Every extension must have a manifest.yaml"
    fi
done

# ============================================================================
# CHECK 2: Manifest Schema Validation
# ============================================================================
header "2/13" "Manifest Schema & ID Match"

for ext in "${extensions[@]}"; do
    manifest="$EXT_DIR/$ext/manifest.yaml"
    [[ ! -f "$manifest" ]] && continue

    result=$(python3 -c "
import yaml, sys, json

with open(sys.argv[1]) as f:
    m = yaml.safe_load(f)

errors = []
info = {}

# schema_version
if m.get('schema_version') != 'dream.services.v1':
    errors.append('missing/wrong schema_version (expected dream.services.v1)')

s = m.get('service', {})
if not isinstance(s, dict):
    errors.append('service must be a mapping')
else:
    for field in ('id', 'name', 'port', 'health'):
        val = s.get(field)
        if field == 'health':
            # health can be empty string "" for CLI tools (no HTTP endpoint)
            if val is None:
                errors.append(f'missing required field: service.{field}')
        else:
            if not val and val != 0:
                errors.append(f'missing required field: service.{field}')
    info['id'] = s.get('id', '')
    info['category'] = s.get('category', '')
    info['type'] = s.get('type', 'docker')

if errors:
    print('FAIL:' + '; '.join(errors))
else:
    print('OK:' + json.dumps(info))
" "$manifest" 2>&1)

    if [[ "$result" == OK:* ]]; then
        pass "Schema valid: $ext"

        # Extract service ID and check it matches directory name
        svc_id=$(echo "${result#OK:}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))")
        if [[ "$svc_id" == "$ext" ]]; then
            pass "ID matches directory: $ext"
        else
            fail "ID mismatch: dir=$ext, service.id=$svc_id"
        fi
    else
        fail "Schema invalid: $ext" "${result#FAIL:}"
    fi
done

# ============================================================================
# CHECK 3: Compose File Presence & Syntax
# ============================================================================
header "3/13" "Compose Files"

for ext in "${extensions[@]}"; do
    manifest="$EXT_DIR/$ext/manifest.yaml"
    compose="$EXT_DIR/$ext/compose.yaml"

    # Determine if this is a core service or host-systemd (no compose needed)
    needs_compose=true
    if [[ -f "$manifest" ]]; then
        svc_type=$(python3 -c "
import yaml, sys
with open(sys.argv[1]) as f:
    m = yaml.safe_load(f)
s = m.get('service', {})
cat = s.get('category', 'optional')
stype = s.get('type', 'docker')
print(f'{cat}:{stype}')
" "$manifest" 2>/dev/null || echo "optional:docker")

        category="${svc_type%%:*}"
        service_type="${svc_type##*:}"

        if [[ "$service_type" == "host-systemd" ]]; then
            needs_compose=false
            skip "$ext: host-systemd service (no compose needed)"
        elif [[ "$category" == "core" && ! -f "$compose" ]]; then
            needs_compose=false
            skip "$ext: core service (compose in base.yml)"
        fi
    fi

    if $needs_compose; then
        if [[ -f "$compose" ]]; then
            pass "$ext/compose.yaml exists"

            # Validate YAML syntax
            if python3 -c "import yaml; yaml.safe_load(open('$compose'))" 2>/dev/null; then
                pass "$ext/compose.yaml valid YAML"
            else
                fail "$ext/compose.yaml invalid YAML"
            fi
        elif [[ -f "$EXT_DIR/$ext/compose.yaml.disabled" ]]; then
            skip "$ext: compose.yaml.disabled (service disabled)"
        else
            fail "$ext/compose.yaml missing" "Non-core docker services need a compose.yaml"
        fi
    fi
done

# ============================================================================
# CHECK 4: No Floating Docker Tags (:latest)
# ============================================================================
header "4/13" "Pinned Docker Images (no :latest)"

for ext in "${extensions[@]}"; do
    compose="$EXT_DIR/$ext/compose.yaml"
    [[ ! -f "$compose" ]] && continue

    # Extract image lines from compose, check for :latest
    floating=$(python3 -c "
import yaml, sys
with open(sys.argv[1]) as f:
    doc = yaml.safe_load(f)
if not doc:
    print('OK')
    sys.exit(0)
services = doc.get('services', {})
floating = []
for svc_name, svc in services.items():
    img = svc.get('image', '')
    if not img:
        continue
    # Check for :latest or no tag at all (implicitly latest)
    if ':latest' in img:
        floating.append(f'{svc_name}: {img}')
    elif ':' not in img and '@' not in img:
        floating.append(f'{svc_name}: {img} (no tag = implicit latest)')
if floating:
    print('FLOATING:' + ', '.join(floating))
else:
    print('OK')
" "$compose" 2>&1)

    if [[ "$floating" == "OK" ]]; then
        pass "Pinned images: $ext"
    elif [[ "$floating" == FLOATING:* ]]; then
        fail "Floating tags: $ext" "${floating#FLOATING:}"
    else
        skip "$ext: could not parse compose for image tags"
    fi
done

# ============================================================================
# CHECK 5: Healthchecks Present
# ============================================================================
header "5/13" "Healthchecks"

for ext in "${extensions[@]}"; do
    compose="$EXT_DIR/$ext/compose.yaml"
    manifest="$EXT_DIR/$ext/manifest.yaml"
    [[ ! -f "$compose" ]] && continue

    # Check if this is a CLI tool (health: "" means no HTTP endpoint)
    is_cli_tool=false
    if [[ -f "$manifest" ]]; then
        health_val=$(python3 -c "
import yaml, sys
with open(sys.argv[1]) as f:
    m = yaml.safe_load(f)
s = m.get('service', {})
print(s.get('health', 'MISSING'))
" "$manifest" 2>/dev/null || echo "MISSING")
        if [[ "$health_val" == "" ]]; then
            is_cli_tool=true
        fi
    fi

    result=$(python3 -c "
import yaml, sys
with open(sys.argv[1]) as f:
    doc = yaml.safe_load(f)
if not doc:
    print('OK')
    sys.exit(0)
services = doc.get('services', {})
missing = []
for svc_name, svc in services.items():
    if 'healthcheck' not in svc:
        missing.append(svc_name)
if missing:
    print('MISSING:' + ', '.join(missing))
else:
    print('OK')
" "$compose" 2>&1)

    if [[ "$result" == "OK" ]]; then
        pass "Healthchecks present: $ext"
    elif [[ "$result" == MISSING:* ]]; then
        if $is_cli_tool; then
            # CLI tools don't need healthchecks (no HTTP endpoint)
            pass "Healthcheck skipped (CLI tool): $ext"
        else
            fail "Missing healthcheck: $ext" "${result#MISSING:}"
        fi
    fi
done

# ============================================================================
# CHECK 6: Security Options (no-new-privileges)
# ============================================================================
header "6/13" "Security Options"

for ext in "${extensions[@]}"; do
    compose="$EXT_DIR/$ext/compose.yaml"
    [[ ! -f "$compose" ]] && continue

    result=$(python3 -c "
import yaml, sys
with open(sys.argv[1]) as f:
    doc = yaml.safe_load(f)
if not doc:
    print('OK')
    sys.exit(0)
services = doc.get('services', {})
missing = []
for svc_name, svc in services.items():
    sec_opt = svc.get('security_opt', [])
    has_nnp = any('no-new-privileges' in str(s) for s in sec_opt)
    if not has_nnp:
        missing.append(svc_name)
if missing:
    print('MISSING:' + ', '.join(missing))
else:
    print('OK')
" "$compose" 2>&1)

    if [[ "$result" == "OK" ]]; then
        pass "security_opt present: $ext"
    elif [[ "$result" == MISSING:* ]]; then
        fail "Missing security_opt (no-new-privileges): $ext" "${result#MISSING:}"
    fi
done

# ============================================================================
# CHECK 7: Resource Limits (warning only)
# ============================================================================
header "7/13" "Resource Limits"

for ext in "${extensions[@]}"; do
    compose="$EXT_DIR/$ext/compose.yaml"
    [[ ! -f "$compose" ]] && continue

    result=$(python3 -c "
import yaml, sys
with open(sys.argv[1]) as f:
    doc = yaml.safe_load(f)
if not doc:
    print('OK')
    sys.exit(0)
services = doc.get('services', {})
missing = []
for svc_name, svc in services.items():
    deploy = svc.get('deploy', {})
    resources = deploy.get('resources', {})
    limits = resources.get('limits', {})
    if not limits:
        missing.append(svc_name)
if missing:
    print('MISSING:' + ', '.join(missing))
else:
    print('OK')
" "$compose" 2>&1)

    if [[ "$result" == "OK" ]]; then
        pass "Resource limits set: $ext"
    elif [[ "$result" == MISSING:* ]]; then
        warn "No resource limits: $ext" "${result#MISSING:}"
    fi
done

# ============================================================================
# CHECK 8: Port Conflicts & Duplicate Env Vars
# ============================================================================
header "8/13" "Port Conflicts & Duplicate Env Vars"

# Port conflict detection across all manifests (external ports only)
# Internal container ports can overlap — only host-facing ports matter
port_map=$(python3 -c "
import yaml, os, sys, json

ext_dir = sys.argv[1]
ports = {}  # external_port -> [service_ids]

for name in sorted(os.listdir(ext_dir)):
    manifest = os.path.join(ext_dir, name, 'manifest.yaml')
    if not os.path.isfile(manifest):
        continue
    with open(manifest) as f:
        m = yaml.safe_load(f)
    svc = m.get('service', {})
    port = svc.get('port')
    ext_port = svc.get('external_port_default')
    # Use external_port_default if set, otherwise fall back to port
    effective_port = ext_port if ext_port else port
    if effective_port:
        ports.setdefault(effective_port, []).append(name)

conflicts = {str(p): svcs for p, svcs in ports.items() if len(svcs) > 1}
if conflicts:
    print('CONFLICTS:' + json.dumps(conflicts))
else:
    print('OK')
" "$EXT_DIR" 2>&1)

if [[ "$port_map" == "OK" ]]; then
    pass "No port conflicts across extensions"
elif [[ "$port_map" == CONFLICTS:* ]]; then
    conflict_json="${port_map#CONFLICTS:}"
    # Parse and display each conflict
    python3 -c "
import json, sys
conflicts = json.loads(sys.argv[1])
for port, svcs in conflicts.items():
    print(f'  Port {port}: {\" vs \".join(svcs)}')
" "$conflict_json"
    warn "Port conflicts detected (see above)" "Services share the same port"
fi

# Duplicate env var detection
echo ""
for ext in "${extensions[@]}"; do
    compose="$EXT_DIR/$ext/compose.yaml"
    [[ ! -f "$compose" ]] && continue

    result=$(python3 -c "
import yaml, sys
with open(sys.argv[1]) as f:
    doc = yaml.safe_load(f)
if not doc:
    print('OK')
    sys.exit(0)
services = doc.get('services', {})
dupes_found = []
for svc_name, svc in services.items():
    env = svc.get('environment', [])
    if isinstance(env, list):
        keys = [e.split('=')[0] for e in env if isinstance(e, str) and '=' in e]
    elif isinstance(env, dict):
        keys = list(env.keys())
    else:
        continue
    seen = set()
    dupes = []
    for k in keys:
        if k in seen:
            dupes.append(k)
        seen.add(k)
    if dupes:
        d = ', '.join(dupes)
        dupes_found.append(f'{svc_name}: {d}')
if dupes_found:
    print('DUPES:' + '; '.join(dupes_found))
else:
    print('OK')
" "$compose" 2>&1)

    if [[ "$result" == "OK" ]]; then
        pass "No duplicate env vars: $ext"
    elif [[ "$result" == DUPES:* ]]; then
        fail "Duplicate env vars: $ext" "${result#DUPES:}"
    fi
done

# ============================================================================
# CHECK 9: Docker Network (dream-network)
# ============================================================================
header "9/13" "Docker Network (dream-network)"

for ext in "${extensions[@]}"; do
    compose="$EXT_DIR/$ext/compose.yaml"
    [[ ! -f "$compose" ]] && continue

    result=$(python3 -c "
import yaml, sys
with open(sys.argv[1]) as f:
    doc = yaml.safe_load(f)
if not doc:
    print('OK')
    sys.exit(0)

services = doc.get('services', {})
networks = doc.get('networks', {})
missing = []

# Check if dream-network is defined at top level
has_top_level = 'dream-network' in networks

for svc_name, svc in services.items():
    svc_networks = svc.get('networks', [])
    if isinstance(svc_networks, dict):
        svc_nets = list(svc_networks.keys())
    elif isinstance(svc_networks, list):
        svc_nets = svc_networks
    else:
        svc_nets = []
    if 'dream-network' not in svc_nets:
        missing.append(svc_name)

if missing:
    print('MISSING:' + ', '.join(missing))
elif not has_top_level:
    print('NO_TOP_LEVEL')
else:
    print('OK')
" "$compose" 2>&1)

    if [[ "$result" == "OK" ]]; then
        pass "dream-network connected: $ext"
    elif [[ "$result" == "NO_TOP_LEVEL" ]]; then
        fail "dream-network not defined in networks: $ext" "Add networks: { dream-network: { external: true } }"
    elif [[ "$result" == MISSING:* ]]; then
        fail "Services not on dream-network: $ext" "${result#MISSING:}"
    fi
done

# ============================================================================
# CHECK 10: Health Endpoint Consistency
# ============================================================================
header "10/13" "Health Endpoint Consistency (manifest vs compose)"

for ext in "${extensions[@]}"; do
    manifest="$EXT_DIR/$ext/manifest.yaml"
    compose="$EXT_DIR/$ext/compose.yaml"
    [[ ! -f "$manifest" || ! -f "$compose" ]] && continue

    result=$(python3 -c "
import yaml, sys, re

with open(sys.argv[1]) as f:
    m = yaml.safe_load(f)
with open(sys.argv[2]) as f:
    c = yaml.safe_load(f)

svc = m.get('service', {})
health_path = svc.get('health', '')
port = svc.get('port')

# Skip CLI tools (health: '')
if health_path == '' or health_path is None:
    print('SKIP')
    sys.exit(0)

if not c:
    print('SKIP')
    sys.exit(0)

services = c.get('services', {})
mismatches = []
for svc_name, svc_def in services.items():
    hc = svc_def.get('healthcheck', {})
    test = hc.get('test', [])
    if isinstance(test, list):
        test_str = ' '.join(str(t) for t in test)
    else:
        test_str = str(test)

    # Extract URL from healthcheck (curl/wget commands)
    url_match = re.search(r'https?://[^\s\"]+', test_str)
    if not url_match:
        continue

    hc_url = url_match.group(0)

    # Check if manifest health path appears in healthcheck URL
    if health_path and health_path not in hc_url:
        mismatches.append(f'{svc_name}: manifest says {health_path}, compose checks {hc_url}')

if mismatches:
    print('MISMATCH:' + '; '.join(mismatches))
else:
    print('OK')
" "$manifest" "$compose" 2>&1)

    if [[ "$result" == "OK" ]]; then
        pass "Health endpoints consistent: $ext"
    elif [[ "$result" == "SKIP" ]]; then
        continue
    elif [[ "$result" == MISMATCH:* ]]; then
        warn "Health endpoint mismatch: $ext" "${result#MISMATCH:}"
    fi
done

# ============================================================================
# CHECK 11: Compose Port Conflicts
# ============================================================================
header "11/13" "Compose Port Mapping Conflicts"

# Scan all compose files for host port bindings and detect collisions
compose_ports=$(python3 -c "
import yaml, os, sys, json, re

ext_dir = sys.argv[1]
ports = {}  # host_port -> [service_ids]

for name in sorted(os.listdir(ext_dir)):
    compose = os.path.join(ext_dir, name, 'compose.yaml')
    if not os.path.isfile(compose):
        continue
    with open(compose) as f:
        doc = yaml.safe_load(f)
    if not doc:
        continue
    services = doc.get('services', {})
    for svc_name, svc in services.items():
        for p in svc.get('ports', []):
            p_str = str(p)
            # Extract host port from mappings like '8080:80', '0.0.0.0:8080:80'
            parts = p_str.split(':')
            if len(parts) >= 2:
                host_port = parts[-2].strip()
                # Remove IP binding if present
                if '.' in host_port:
                    continue  # skip, the port is the last numeric part
                try:
                    hp = int(host_port)
                    ports.setdefault(hp, []).append(f'{name}/{svc_name}')
                except ValueError:
                    pass

conflicts = {str(p): svcs for p, svcs in ports.items() if len(svcs) > 1}
if conflicts:
    print('CONFLICTS:' + json.dumps(conflicts))
else:
    print('OK')
" "$EXT_DIR" 2>&1)

if [[ "$compose_ports" == "OK" ]]; then
    pass "No compose port mapping conflicts"
elif [[ "$compose_ports" == CONFLICTS:* ]]; then
    conflict_json="${compose_ports#CONFLICTS:}"
    python3 -c "
import json, sys
conflicts = json.loads(sys.argv[1])
for port, svcs in conflicts.items():
    print(f'  Host port {port}: {\" vs \".join(svcs)}')
" "$conflict_json"
    fail "Compose port mapping conflicts detected" "Multiple services bind the same host port"
fi

# ============================================================================
# CHECK 12: Dangerous Volume Mounts
# ============================================================================
header "12/13" "Dangerous Volume Mounts"

for ext in "${extensions[@]}"; do
    compose="$EXT_DIR/$ext/compose.yaml"
    [[ ! -f "$compose" ]] && continue

    result=$(python3 -c "
import yaml, sys, re

with open(sys.argv[1]) as f:
    doc = yaml.safe_load(f)
if not doc:
    print('OK')
    sys.exit(0)

services = doc.get('services', {})
dangerous = []
patterns = [
    (r'~/', 'mounts home directory'),
    (r'\\\$HOME', 'mounts home directory'),
    (r'\\\${HOME}', 'mounts home directory'),
    (r'\.ssh', 'mounts SSH keys'),
    (r'\.gnupg', 'mounts GPG keys'),
    (r'\.aws', 'mounts AWS credentials'),
    (r'/etc/shadow', 'mounts shadow file'),
    (r'/etc/passwd', 'mounts passwd file'),
    (r'\\\${PWD}:/[^:]*$', 'mounts entire project directory'),
    (r'\.:/[^:]*$', 'mounts entire current directory'),
]

for svc_name, svc in services.items():
    volumes = svc.get('volumes', [])
    for v in volumes:
        v_str = str(v)
        # Handle dict-style volumes
        if isinstance(v, dict):
            v_str = v.get('source', '') + ':' + v.get('target', '')
        for pattern, reason in patterns:
            if re.search(pattern, v_str):
                dangerous.append(f'{svc_name}: {v_str} ({reason})')
                break

if dangerous:
    print('DANGEROUS:' + '; '.join(dangerous))
else:
    print('OK')
" "$compose" 2>&1)

    if [[ "$result" == "OK" ]]; then
        pass "No dangerous mounts: $ext"
    elif [[ "$result" == DANGEROUS:* ]]; then
        fail "Dangerous volume mount: $ext" "${result#DANGEROUS:}"
    fi
done

# ============================================================================
# CHECK 13: Hardcoded Passwords
# ============================================================================
header "13/13" "Hardcoded Passwords"

for ext in "${extensions[@]}"; do
    compose="$EXT_DIR/$ext/compose.yaml"
    [[ ! -f "$compose" ]] && continue

    result=$(python3 -c "
import yaml, sys, re

with open(sys.argv[1]) as f:
    doc = yaml.safe_load(f)
if not doc:
    print('OK')
    sys.exit(0)

services = doc.get('services', {})
hardcoded = []
password_keys = re.compile(r'(PASSWORD|SECRET|TOKEN|API_KEY)', re.IGNORECASE)

for svc_name, svc in services.items():
    env = svc.get('environment', {})
    if isinstance(env, list):
        pairs = {}
        for e in env:
            if isinstance(e, str) and '=' in e:
                k, v = e.split('=', 1)
                pairs[k] = v
        env = pairs
    elif not isinstance(env, dict):
        continue

    for key, val in env.items():
        if not password_keys.search(key):
            continue
        val_str = str(val).strip()
        # Skip if it's an env var reference like \${FOO} or empty
        if not val_str or val_str.startswith('\${') or val_str == 'None':
            continue
        # Skip common placeholder patterns
        if val_str in ('changeme', 'CHANGEME', 'change_me'):
            # These are still bad but at least obviously placeholders
            hardcoded.append(f'{svc_name}: {key}={val_str} (placeholder — use env var)')
            continue
        # Flag actual hardcoded values
        hardcoded.append(f'{svc_name}: {key} is hardcoded')

if hardcoded:
    print('HARDCODED:' + '; '.join(hardcoded))
else:
    print('OK')
" "$compose" 2>&1)

    if [[ "$result" == "OK" ]]; then
        pass "No hardcoded passwords: $ext"
    elif [[ "$result" == HARDCODED:* ]]; then
        warn "Hardcoded credentials: $ext" "${result#HARDCODED:}"
    fi
done

# ============================================================================
# Summary
# ============================================================================
echo ""
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
TOTAL=$((PASS + FAIL + WARN + SKIP))
echo -e "${BOLD}  Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC}, ${YELLOW}$WARN warnings${NC}, ${YELLOW}$SKIP skipped${NC} ${BOLD}($TOTAL total)${NC}"
echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [[ $FAIL -gt 0 ]]; then
    echo -e "${RED}Extension validation failed ($FAIL issues).${NC}"
    exit 1
else
    if [[ $WARN -gt 0 ]]; then
        echo -e "${YELLOW}Extension validation passed with $WARN warnings.${NC}"
    else
        echo -e "${GREEN}All extension checks passed!${NC}"
    fi
    exit 0
fi

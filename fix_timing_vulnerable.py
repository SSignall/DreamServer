#!/usr/bin/env python3
"""
Fix timingSafeEqual vulnerability: replace early-return pattern with constant-time pattern.
"""

import sys
from pathlib import Path

WORKFLOWS = [
    "extensions/services/localai/workflow-text-generation.json",
    "extensions/services/n8n/workflow-n8n-bark-tts.json",
    "extensions/services/n8n/workflow-n8n-dify.json",
    "extensions/services/n8n/workflow-n8n-flowise.json",
    "extensions/services/n8n/workflow-n8n-langflow.json",
    "extensions/services/n8n/workflow-n8n-localai.json",
    "extensions/services/whisper/workflow-stt.json",
]

# Pattern 1: Has early return before result initialization
VULNERABLE_PATTERN_1 = 'if (a.length > MAX_LEN || b.length > MAX_LEN) return false;\\n  let result = 0;'
SECURE_REPLACEMENT_1 = 'let result = (a.length > MAX_LEN || b.length > MAX_LEN) ? 1 : 0;'

# Pattern 2: Has comment about removed early check but no bounds check in result
VULNERABLE_PATTERN_2A = 'const MAX_LEN = 256;\\n    // Removed early length check: constant-time comparison must not leak timing via early exit\\n\\n  let result = 0;'
SECURE_REPLACEMENT_2A = 'const MAX_LEN = 256;\\n\\n  // Include bounds check in result (constant-time, no branch)\\n  let result = (a.length > MAX_LEN || b.length > MAX_LEN) ? 1 : 0;'

# Pattern 2B: With "MAX_LEN to prevent truncation attacks" before comment
VULNERABLE_PATTERN_2B = 'MAX_LEN to prevent truncation attacks\\n    // Removed early length check: constant-time comparison must not leak timing via early exit\\n  let result = 0;'
SECURE_REPLACEMENT_2B = 'MAX_LEN to prevent truncation attacks\\n\\n  // Include bounds check in result (constant-time, no branch)\\n  let result = (a.length > MAX_LEN || b.length > MAX_LEN) ? 1 : 0;'

# Pattern 2C: With extra spaces in blank line
VULNERABLE_PATTERN_2C = 'const MAX_LEN = 256;\\n    // Removed early length check: constant-time comparison must not leak timing via early exit\\n  \\n  let result = 0;'
SECURE_REPLACEMENT_2C = 'const MAX_LEN = 256;\\n\\n  // Include bounds check in result (constant-time, no branch)\\n  let result = (a.length > MAX_LEN || b.length > MAX_LEN) ? 1 : 0;'

def fix_workflow(filepath):
    """Fix timingSafeEqual in a single workflow file."""
    path = Path(filepath)
    if not path.exists():
        print(f"SKIP: {filepath} not found")
        return False

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Check if already has the secure pattern
    if 'let result = (a.length > MAX_LEN || b.length > MAX_LEN) ? 1 : 0' in content:
        print(f"OK: {filepath} already has constant-time pattern")
        return False

    fixed = False
    # Try pattern 1: early return
    if VULNERABLE_PATTERN_1 in content:
        content = content.replace(VULNERABLE_PATTERN_1, SECURE_REPLACEMENT_1)
        print(f"FIXED (pattern 1): {filepath}")
        fixed = True
    # Try pattern 2A: comment but no bounds check (standard)
    elif VULNERABLE_PATTERN_2A in content:
        content = content.replace(VULNERABLE_PATTERN_2A, SECURE_REPLACEMENT_2A)
        print(f"FIXED (pattern 2A): {filepath}")
        fixed = True
    # Try pattern 2B: with truncation attacks comment
    elif VULNERABLE_PATTERN_2B in content:
        content = content.replace(VULNERABLE_PATTERN_2B, SECURE_REPLACEMENT_2B)
        print(f"FIXED (pattern 2B): {filepath}")
        fixed = True
    # Try pattern 2C: with extra spaces
    elif VULNERABLE_PATTERN_2C in content:
        content = content.replace(VULNERABLE_PATTERN_2C, SECURE_REPLACEMENT_2C)
        print(f"FIXED (pattern 2C): {filepath}")
        fixed = True
    else:
        print(f"WARN: {filepath} - pattern not found")
        return False

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

    return True

def main():
    fixed_count = 0
    for workflow in WORKFLOWS:
        if fix_workflow(workflow):
            fixed_count += 1

    print(f"\n{fixed_count}/{len(WORKFLOWS)} files fixed")
    return 0 if fixed_count > 0 else 1

if __name__ == "__main__":
    sys.exit(main())

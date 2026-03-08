#!/usr/bin/env python3
"""
Validate timingSafeEqual implementation across all n8n workflow files.
Ensures all files use the gold standard pattern (no length oracle vulnerabilities).
"""

import json
import os
import sys

def validate_timingsafeequal(code, filepath):
    """Check if timingSafeEqual follows the gold standard pattern."""
    issues = []
    
    # Must have MAX_LEN = 256
    if 'const MAX_LEN = 256;' not in code:
        issues.append("MAX_LEN should be 256")
    
    # Must NOT have early return on length mismatch (length oracle vulnerability)
    if 'if (a.length !== b.length) return false;' in code:
        issues.append("Has length oracle vulnerability (early return on length mismatch)")
    
    # Must have folded length check (prevents length oracle)
    if 'result |= (a.length === b.length) ? 0 : 1;' not in code:
        issues.append("Missing folded length check")
    
    # Should use conditional access (more efficient than padEnd)
    if 'i < a.length ? a.charCodeAt(i) : 0' not in code:
        issues.append("Should use conditional char access instead of padEnd")
    
    return issues

def main():
    workflows = [
        'extensions/services/bark/workflow-tts.json',
        'extensions/services/n8n/workflow-n8n-rvc.json',
        'extensions/services/n8n/workflow-n8n-localai.json',
        'extensions/services/n8n/workflow-n8n-ollama.json',
    ]
    
    all_pass = True
    
    for path in workflows:
        if not os.path.exists(path):
            print(f"MISSING: {path}")
            all_pass = False
            continue
            
        with open(path) as f:
            data = json.load(f)
        
        for node in data.get('nodes', []):
            if 'Validate' in node.get('name', ''):
                code = node['parameters'].get('jsCode', '')
                issues = validate_timingsafeequal(code, path)
                
                if issues:
                    print(f"FAIL: {path}")
                    for issue in issues:
                        print(f"  - {issue}")
                    all_pass = False
                else:
                    print(f"PASS: {path}")
                break
        else:
            print(f"SKIP: {path} (no validation node)")
    
    return 0 if all_pass else 1

if __name__ == '__main__':
    sys.exit(main())

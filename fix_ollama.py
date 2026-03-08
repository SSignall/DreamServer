#!/usr/bin/env python3
"""Fix Ollama workflow timingSafeEqual to gold standard pattern."""

import json
import re

WORKFLOW_PATH = "extensions/services/n8n/workflow-n8n-ollama.json"

GOLD_TIMING_SAFE_EQUAL = '''// Timing-safe comparison - constant time regardless of input length
// Prevents timing oracle attacks by ensuring comparison takes same time for all inputs
function timingSafeEqual(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string') return false;
  const MAX_LEN = 256;
  if (a.length > MAX_LEN || b.length > MAX_LEN) return false;

  let result = 0;
  // Constant-time comparison: always iterate MAX_LEN, use 0 for out-of-bounds
  for (let i = 0; i < MAX_LEN; i++) {
    const charA = i < a.length ? a.charCodeAt(i) : 0;
    const charB = i < b.length ? b.charCodeAt(i) : 0;
    result |= charA ^ charB;
  }
  // Include length check in constant-time result (CRITICAL: prevents length oracle attacks)
  result |= (a.length === b.length) ? 0 : 1;
  return result === 0;
}'''

# Read the workflow
with open(WORKFLOW_PATH, 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# Find the Validate Input node and update timingSafeEqual
for node in workflow['nodes']:
    if node['name'] == 'Validate Input' and 'jsCode' in node['parameters']:
        js_code = node['parameters']['jsCode']
        
        # Pattern to match the timingSafeEqual function (start to return result === 0;)
        pattern = r'// Timing-safe comparison[^\n]*\n// Prevents[^\n]*\nfunction timingSafeEqual\(a, b\) \{[^}]*\{[^}]*\}[^}]*\}'
        
        # Check if this workflow uses the vulnerable pattern
        if 'padEnd(MAX_LEN' in js_code:
            # Replace with gold standard
            new_js_code = re.sub(pattern, GOLD_TIMING_SAFE_EQUAL, js_code, count=1)
            node['parameters']['jsCode'] = new_js_code
            
            # Write back
            with open(WORKFLOW_PATH, 'w', encoding='utf-8') as f:
                json.dump(workflow, f, indent=2, ensure_ascii=False)
            print("✅ Fixed Ollama workflow to gold standard timingSafeEqual")
        else:
            print("✅ Ollama already uses gold standard pattern")
        break
else:
    print("❌ Could not find Validate Input node")

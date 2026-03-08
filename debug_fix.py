#!/usr/bin/env python3
import json
import re

filepath = 'extensions/services/bark/workflow-tts.json'

with open(filepath) as f:
    data = json.load(f)

code = data['nodes'][1]['parameters']['jsCode']

print("=== SEARCHING FOR FUNCTION ===")
start = code.find('function timingSafeEqual(a, b)')
print(f"Start position: {start}")

if start != -1:
    search_from = start + 30
    end_marker = 'return result === 0;'
    end_pos = code.find(end_marker, search_from)
    print(f"End marker position: {end_pos}")
    
    brace_pos = code.find('}', end_pos)
    func_end = brace_pos + 1
    print(f"Function end: {func_end}")
    
    func = code[start:func_end]
    print("=== FOUND FUNCTION ===")
    print(repr(func[:500]))
    
    # Check what we need to replace
    old_pattern = '''function timingSafeEqual(a, b) {
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
    
    print("\n=== OLD PATTERN MATCH:", old_pattern in code)
    
    # Check the actual content
    print("\n=== ACTUAL CONTENT ===")
    print(repr(code[start:start+500]))

import json
import sys
import re

# The correct timingSafeEqual implementation (as a JavaScript string)
NEW_TIMING_SAFE_EQUAL = '''function timingSafeEqual(a, b) {
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
  // Include length check in constant-time result
  result |= (a.length === b.length) ? 0 : 1;
  return result === 0;
}'''

files = [
    "extensions/services/n8n/workflow-n8n-rvc.json",
    "extensions/services/n8n/workflow-n8n-localai.json", 
    "extensions/services/n8n/workflow-n8n-bark-tts.json",
    "extensions/services/whisper/workflow-stt.json",
    "extensions/services/bark/workflow-tts.json",
    "extensions/services/rvc/workflow-voice-convert.json"
]

for filepath in files:
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        modified = False
        for node in data.get('nodes', []):
            js_code = node.get('parameters', {}).get('jsCode', '')
            if 'timingSafeEqual' in js_code and 'padEnd' in js_code:
                # Replace using regex for flexibility
                # Match the entire timingSafeEqual function with any variation of padEnd
                old_func_pattern = r'(function timingSafeEqual\(a, b\) \{)([^}]*)(const aPadded = a\.padEnd\(MAX_LEN,[^)]+\);)([^}]*)(const bPadded = b\.padEnd\(MAX_LEN,[^)]+\);)([^}]*)(let result = 0;)([^}]*)(for \(let i = 0; i < MAX_LEN; i\+\+\) \{)([^}]*)(\})([^}]*)(return result === 0;)'
                
                # Simple string replacement approach
                # Find and replace the whole function
                start_idx = js_code.find('function timingSafeEqual(a, b) {')
                if start_idx == -1:
                    continue
                
                # Find the closing brace of the function
                brace_count = 0
                end_idx = start_idx
                for i in range(start_idx, len(js_code)):
                    if js_code[i] == '{':
                        brace_count += 1
                    elif js_code[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i + 1
                            break
                
                old_func = js_code[start_idx:end_idx]
                new_js_code = js_code[:start_idx] + NEW_TIMING_SAFE_EQUAL + js_code[end_idx:]
                node['parameters']['jsCode'] = new_js_code
                modified = True
                print(f"FIXED: {filepath}")
                break
        
        if modified:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            print(f"SKIP: {filepath}")
            
    except Exception as e:
        print(f"ERROR: {filepath} - {e}")

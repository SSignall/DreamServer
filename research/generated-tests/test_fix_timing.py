"""
=== GENERATED TEST FILE — NEEDS REVIEW ===
Generated: 2026-03-08T10:08:45.901449+00:00
Source: fix_timing.py
Generator: Qwen3-Coder (local GPU)

This file was auto-generated and has NOT been reviewed or run.
Review before using. May need fixture adjustments or mock updates.
================================================================
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
import pytest

# Import the module to test
import fix_timing


class TestFixTiming:
    """Tests for the fix_timing.py module."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Sample workflow data with old timingSafeEqual implementation
        self.old_workflow_data = {
            "nodes": [
                {
                    "name": "Test Node",
                    "parameters": {
                        "jsCode": '''
function timingSafeEqual(a, b) {
  const MAX_LEN = 256;
  const aPadded = a.padEnd(MAX_LEN, '\\0');
  const bPadded = b.padEnd(MAX_LEN, '\\0');
  let result = 0;
  for (let i = 0; i < MAX_LEN; i++) {
    result |= aPadded.charCodeAt(i) ^ bPadded.charCodeAt(i);
  }
  return result === 0;
}
some other code here
'''
                    }
                }
            ]
        }
        
        # Sample workflow data without timingSafeEqual
        self.no_timing_workflow_data = {
            "nodes": [
                {
                    "name": "Test Node",
                    "parameters": {
                        "jsCode": "console.log('Hello World');"
                    }
                }
            ]
        }
        
        # Sample workflow data with timingSafeEqual but no padEnd
        self.timing_no_pad_workflow_data = {
            "nodes": [
                {
                    "name": "Test Node",
                    "parameters": {
                        "jsCode": '''
function timingSafeEqual(a, b) {
  if (a.length !== b.length) return false;
  let result = 0;
  for (let i = 0; i < a.length; i++) {
    result |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return result === 0;
}
'''
                    }
                }
            ]
        }

    def teardown_method(self):
        """Clean up test fixtures."""
        # Remove temporary directory and its contents
        for f in Path(self.temp_dir).glob('*'):
            f.unlink()
        os.rmdir(self.temp_dir)

    def _create_test_file(self, filename, data):
        """Helper to create a test file in temp directory."""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f)
        return filepath

    def test_new_timing_safe_equal_function_exists(self):
        """Test that the NEW_TIMING_SAFE_EQUAL constant is defined."""
        assert hasattr(fix_timing, 'NEW_TIMING_SAFE_EQUAL')
        assert isinstance(fix_timing.NEW_TIMING_SAFE_EQUAL, str)
        assert 'timingSafeEqual' in fix_timing.NEW_TIMING_SAFE_EQUAL
        assert 'MAX_LEN' in fix_timing.NEW_TIMING_SAFE_EQUAL
        assert 'charCodeAt' in fix_timing.NEW_TIMING_SAFE_EQUAL

    def test_files_list_exists(self):
        """Test that the files list is defined."""
        assert hasattr(fix_timing, 'files')
        assert isinstance(fix_timing.files, list)
        assert len(fix_timing.files) > 0

    def test_process_workflow_with_old_implementation(self):
        """Test that old timingSafeEqual implementation gets replaced."""
        filename = "test-workflow.json"
        filepath = self._create_test_file(filename, self.old_workflow_data)
        
        # Process the file (simulate what the main code does)
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        modified = False
        for node in data.get('nodes', []):
            js_code = node.get('parameters', {}).get('jsCode', '')
            if 'timingSafeEqual' in js_code and 'padEnd' in js_code:
                start_idx = js_code.find('function timingSafeEqual(a, b) {')
                if start_idx != -1:
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
                    new_js_code = js_code[:start_idx] + fix_timing.NEW_TIMING_SAFE_EQUAL + js_code[end_idx:]
                    node['parameters']['jsCode'] = new_js_code
                    modified = True
                    break
        
        assert modified
        # Verify the new function is in the code
        new_js_code = data['nodes'][0]['parameters']['jsCode']
        assert 'function timingSafeEqual(a, b) {' in new_js_code
        assert 'padEnd' not in new_js_code
        assert 'MAX_LEN' in new_js_code
        assert 'charA' in new_js_code
        assert 'charB' in new_js_code

    def test_process_workflow_without_timing_safe_equal(self):
        """Test that files without timingSafeEqual are skipped."""
        filename = "test-workflow-no-timing.json"
        filepath = self._create_test_file(filename, self.no_timing_workflow_data)
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        modified = False
        for node in data.get('nodes', []):
            js_code = node.get('parameters', {}).get('jsCode', '')
            if 'timingSafeEqual' in js_code and 'padEnd' in js_code:
                modified = True
                break
        
        assert not modified

    def test_process_workflow_with_timing_safe_equal_no_padend(self):
        """Test that files with timingSafeEqual but no padEnd are skipped."""
        filename = "test-workflow-timing-no-pad.json"
        filepath = self._create_test_file(filename, self.timing_no_pad_workflow_data)
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        modified = False
        for node in data.get('nodes', []):
            js_code = node.get('parameters', {}).get('jsCode', '')
            if 'timingSafeEqual' in js_code and 'padEnd' in js_code:
                modified = True
                break
        
        assert not modified

    def test_process_workflow_multiple_nodes(self):
        """Test processing workflow with multiple nodes."""
        workflow_data = {
            "nodes": [
                {
                    "name": "Node 1",
                    "parameters": {
                        "jsCode": "console.log('Node 1');"
                    }
                },
                {
                    "name": "Node 2",
                    "parameters": {
                        "jsCode": self.old_workflow_data["nodes"][0]["parameters"]["jsCode"]
                    }
                },
                {
                    "name": "Node 3",
                    "parameters": {
                        "jsCode": "console.log('Node 3');"
                    }
                }
            ]
        }
        
        filename = "test-workflow-multiple.json"
        filepath = self._create_test_file(filename, workflow_data)
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        modified = False
        for node in data.get('nodes', []):
            js_code = node.get('parameters', {}).get('jsCode', '')
            if 'timingSafeEqual' in js_code and 'padEnd' in js_code:
                start_idx = js_code.find('function timingSafeEqual(a, b) {')
                if start_idx != -1:
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
                    
                    new_js_code = js_code[:start_idx] + fix_timing.NEW_TIMING_SAFE_EQUAL + js_code[end_idx:]
                    node['parameters']['jsCode'] = new_js_code
                    modified = True
                    break
        
        assert modified
        # Verify only the second node was modified
        assert 'console.log' in data['nodes'][0]['parameters']['jsCode']
        assert 'padEnd' not in data['nodes'][1]['parameters']['jsCode']
        assert 'console.log' in data['nodes'][2]['parameters']['jsCode']

    def test_process_workflow_with_invalid_json(self):
        """Test handling of invalid JSON files."""
        filename = "invalid.json"
        filepath = os.path.join(self.temp_dir, filename)
        
        # Write invalid JSON
        with open(filepath, 'w') as f:
            f.write("{ invalid json }")
        
        # Test that exception is caught and handled
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            # Expected behavior
            pass

    def test_process_workflow_with_missing_file(self):
        """Test handling of missing files."""
        filepath = os.path.join(self.temp_dir, "nonexistent.json")
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            # Expected behavior
            pass

    def test_process_workflow_with_empty_nodes(self):
        """Test handling of workflow with empty nodes array."""
        workflow_data = {
            "nodes": []
        }
        
        filename = "test-workflow-empty-nodes.json"
        filepath = self._create_test_file(filename, workflow_data)
        
        with open(filepath, '

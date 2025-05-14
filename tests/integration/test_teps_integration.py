#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration tests for the Tool Execution & Permission Service (TEPS) module.

These tests verify the interaction of TEPS with file system operations
in a controlled environment.

AI-GENERATED: [Forge] - Task:[RFI-TEPS-002]
"""

import unittest
import os
import tempfile
import shutil
from unittest.mock import patch

# Import the module to test
from framework_core.teps import TEPSEngine

class TestTEPSIntegration(unittest.TestCase):
    """Integration tests for the TEPSEngine class."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary directory for file operations
        self.test_dir = tempfile.mkdtemp()
        
        # Create a TEPS instance
        self.teps = TEPSEngine()
    
    def tearDown(self):
        """Clean up after each test."""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)
    
    @patch('builtins.input', return_value='y')
    @patch('builtins.print')
    def test_file_write_and_read_integration(self, mock_print, mock_input):
        """Test writing to a file and then reading it back."""
        # Define test file path in the temporary directory
        test_file_path = os.path.join(self.test_dir, "test_file.txt")
        test_content = "This is a test file content.\nWith multiple lines.\n"
        
        # Create a write file request
        write_request = {
            "request_id": "integration-write-1",
            "tool_name": "writeFile",
            "parameters": {
                "path": test_file_path,
                "content": test_content,
            },
            "icerc_full_text": f"Intent: Write test file, Command: Write to {test_file_path}, Expected: File created, Risk: Low"
        }
        
        # Execute the write request
        write_result = self.teps.execute_tool(write_request)
        
        # Verify the write was successful
        self.assertEqual(write_result["status"], "success")
        self.assertEqual(write_result["data"]["file_path"], test_file_path)
        
        # Verify the file exists
        self.assertTrue(os.path.exists(test_file_path))
        
        # Create a read file request
        read_request = {
            "request_id": "integration-read-1",
            "tool_name": "readFile",
            "parameters": {
                "path": test_file_path,
            },
            "icerc_full_text": f"Intent: Read test file, Command: Read {test_file_path}, Expected: File content, Risk: Low"
        }
        
        # Execute the read request
        read_result = self.teps.execute_tool(read_request)
        
        # Verify the read was successful
        self.assertEqual(read_result["status"], "success")
        self.assertEqual(read_result["data"]["file_path"], test_file_path)
        self.assertEqual(read_result["data"]["content"], test_content)
    
    @patch('builtins.input', return_value='y')
    @patch('builtins.print')
    def test_bash_command_integration(self, mock_print, mock_input):
        """Test executing a real bash command in the test directory."""
        # Create a test file
        test_file_path = os.path.join(self.test_dir, "bash_test.txt")
        with open(test_file_path, 'w') as f:
            f.write("Test content")
        
        # Create a bash command request to list files
        bash_request = {
            "request_id": "integration-bash-1",
            "tool_name": "executeBashCommand",
            "parameters": {
                "command": f"ls -l {self.test_dir}",
            },
            "icerc_full_text": f"Intent: List files in test dir, Command: ls -l {self.test_dir}, Expected: File listing, Risk: Low"
        }
        
        # Execute the bash command
        bash_result = self.teps.execute_tool(bash_request)
        
        # Verify the command was successful
        self.assertEqual(bash_result["status"], "success")
        self.assertEqual(bash_result["data"]["exit_code"], 0)
        
        # Verify the output contains our test file name
        self.assertIn("bash_test.txt", bash_result["data"]["stdout"])
    
    @patch('builtins.input', return_value='y')
    @patch('builtins.print')
    def test_create_nested_directory_structure(self, mock_print, mock_input):
        """Test creating a file in a nested directory structure."""
        # Define a path with nested directories
        nested_path = os.path.join(self.test_dir, "level1", "level2", "level3", "test.txt")
        test_content = "Content in nested file"
        
        # Create a write request
        write_request = {
            "request_id": "integration-write-2",
            "tool_name": "writeFile",
            "parameters": {
                "path": nested_path,
                "content": test_content,
            },
            "icerc_full_text": f"Intent: Write nested file, Command: Write to {nested_path}, Expected: File and dirs created, Risk: Low"
        }
        
        # Execute the write
        write_result = self.teps.execute_tool(write_request)
        
        # Verify success
        self.assertEqual(write_result["status"], "success")
        
        # Verify directories and file were created
        self.assertTrue(os.path.exists(nested_path))
        
        # Read the file to verify content
        with open(nested_path, 'r') as f:
            content = f.read()
            self.assertEqual(content, test_content)

if __name__ == '__main__':
    unittest.main()
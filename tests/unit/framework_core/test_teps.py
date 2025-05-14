#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the Tool Execution & Permission Service (TEPS) module.

AI-GENERATED: [Forge] - Task:[RFI-TEPS-002]
"""

import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import io
import sys
import tempfile

# Import the module to test
from framework_core.teps import TEPSEngine

class TestTEPSEngine(unittest.TestCase):
    """Test cases for the TEPSEngine class."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create a TEPS instance with no config
        self.teps = TEPSEngine()
        
        # Create a TEPS instance with allowlist config (for testing allowlist functionality)
        self.teps_with_allowlist = TEPSEngine({
            "allowlist_file": "dummy_allowlist.txt",
            "dry_run_enabled": True
        })
        # Mock the allowlist loading
        self.teps_with_allowlist.allowlist = ["ls", "pwd", "echo"]
    
    @patch('builtins.input', return_value='y')
    @patch('builtins.print')
    def test_execute_tool_bash_success(self, mock_print, mock_input):
        """Test executing a bash command with user confirmation."""
        # Mock subprocess.run to avoid actually running commands
        with patch('subprocess.run') as mock_run:
            # Configure the mock to return a successful result
            mock_process = MagicMock()
            mock_process.stdout = "command output"
            mock_process.stderr = ""
            mock_process.returncode = 0
            mock_run.return_value = mock_process
            
            # Create a tool request for a bash command
            tool_request = {
                "request_id": "test-123",
                "tool_name": "executeBashCommand",
                "parameters": {
                    "command": "ls -la",
                    "working_directory": "/tmp"
                },
                "icerc_full_text": "Intent: List files, Command: ls -la, Expected: File listing, Risk: Low"
            }
            
            # Execute the tool
            result = self.teps.execute_tool(tool_request)
            
            # Verify the result
            self.assertEqual(result["request_id"], "test-123")
            self.assertEqual(result["tool_name"], "executeBashCommand")
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["data"]["stdout"], "command output")
            self.assertEqual(result["data"]["exit_code"], 0)
            
            # Verify subprocess.run was called correctly
            mock_run.assert_called_once_with(
                "ls -la", 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd="/tmp"
            )
    
    @patch('builtins.input', return_value='n')
    @patch('builtins.print')
    def test_execute_tool_user_declined(self, mock_print, mock_input):
        """Test user declining a tool execution."""
        # Create a tool request
        tool_request = {
            "request_id": "test-456",
            "tool_name": "executeBashCommand",
            "parameters": {
                "command": "rm -rf /",
            },
            "icerc_full_text": "Intent: Remove files, Command: rm -rf /, Expected: Deletion, Risk: HIGH"
        }
        
        # Execute the tool (should be declined)
        result = self.teps.execute_tool(tool_request)
        
        # Verify the result
        self.assertEqual(result["request_id"], "test-456")
        self.assertEqual(result["tool_name"], "executeBashCommand")
        self.assertEqual(result["status"], "declined_by_user")
        self.assertIn("declined", result["data"]["message"].lower())
    
    @patch('builtins.input', return_value='y')
    @patch('builtins.print')
    def test_execute_tool_bash_error(self, mock_print, mock_input):
        """Test executing a bash command that fails."""
        # Mock subprocess.run to simulate a command that fails
        with patch('subprocess.run') as mock_run:
            # Configure the mock to raise an exception
            mock_run.side_effect = Exception("Command failed")
            
            # Create a tool request
            tool_request = {
                "request_id": "test-789",
                "tool_name": "executeBashCommand",
                "parameters": {
                    "command": "invalid_command",
                },
                "icerc_full_text": "Intent: Run invalid command, Command: invalid_command, Expected: Error, Risk: Low"
            }
            
            # Execute the tool (should catch the exception)
            result = self.teps.execute_tool(tool_request)
            
            # Verify the result
            self.assertEqual(result["request_id"], "test-789")
            self.assertEqual(result["tool_name"], "executeBashCommand")
            self.assertEqual(result["status"], "error")
            self.assertIn("Command failed", result["data"]["error_message"])
    
    @patch('builtins.input', return_value='y')
    @patch('builtins.print')
    def test_read_file_success(self, mock_print, mock_input):
        """Test reading a file successfully."""
        # Mock open to avoid actually reading files
        with patch('builtins.open', mock_open(read_data="file content")) as mock_file:
            # Create a tool request for reading a file
            tool_request = {
                "request_id": "test-read-1",
                "tool_name": "readFile",
                "parameters": {
                    "path": "/path/to/file.txt",
                },
                "icerc_full_text": "Intent: Read file, Command: Read /path/to/file.txt, Expected: File content, Risk: Low"
            }
            
            # Execute the tool
            result = self.teps.execute_tool(tool_request)
            
            # Verify the result
            self.assertEqual(result["request_id"], "test-read-1")
            self.assertEqual(result["tool_name"], "readFile")
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["data"]["file_path"], "/path/to/file.txt")
            self.assertEqual(result["data"]["content"], "file content")
            
            # Verify open was called correctly
            mock_file.assert_called_once_with("/path/to/file.txt", 'r', encoding='utf-8')
    
    @patch('builtins.input', return_value='y')
    @patch('builtins.print')
    def test_write_file_success(self, mock_print, mock_input):
        """Test writing a file successfully."""
        # Mock open to avoid actually writing files
        # Also mock os.path.dirname and os.makedirs to handle directory creation
        with patch('builtins.open', mock_open()) as mock_file, \
             patch('os.path.dirname', return_value="/path/to") as mock_dirname, \
             patch('os.path.exists', return_value=True) as mock_exists, \
             patch('os.makedirs') as mock_makedirs:
            
            # Create a tool request for writing a file
            tool_request = {
                "request_id": "test-write-1",
                "tool_name": "writeFile",
                "parameters": {
                    "path": "/path/to/file.txt",
                    "content": "new content",
                },
                "icerc_full_text": "Intent: Write file, Command: Write to /path/to/file.txt, Expected: File updated, Risk: Low"
            }
            
            # Execute the tool
            result = self.teps.execute_tool(tool_request)
            
            # Verify the result
            self.assertEqual(result["request_id"], "test-write-1")
            self.assertEqual(result["tool_name"], "writeFile")
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["data"]["file_path"], "/path/to/file.txt")
            self.assertIn("success", result["data"]["status"])
            
            # Verify open was called correctly
            mock_file.assert_called_once_with("/path/to/file.txt", 'w', encoding='utf-8')
            mock_file().write.assert_called_once_with("new content")
    
    @patch('builtins.input', return_value='y')
    @patch('builtins.print')
    def test_unknown_tool(self, mock_print, mock_input):
        """Test handling an unknown tool."""
        # Create a tool request with an unknown tool
        tool_request = {
            "request_id": "test-unknown-1",
            "tool_name": "unknownTool",
            "parameters": {},
            "icerc_full_text": "Intent: Test unknown tool, Command: unknownTool, Expected: Error, Risk: Low"
        }
        
        # Execute the tool (should return an error)
        result = self.teps.execute_tool(tool_request)
        
        # Verify the result
        self.assertEqual(result["request_id"], "test-unknown-1")
        self.assertEqual(result["tool_name"], "unknownTool")
        self.assertEqual(result["status"], "error")
        self.assertIn("Unknown tool", result["data"]["error_message"])
    
    @patch('builtins.input', return_value='y')
    @patch('builtins.print')
    def test_missing_parameters(self, mock_print, mock_input):
        """Test handling missing parameters."""
        # Create a tool request with missing parameters
        tool_request = {
            "request_id": "test-missing-1",
            "tool_name": "readFile",
            "parameters": {},  # Missing path
            "icerc_full_text": "Intent: Read file with missing path, Command: Read file, Expected: Error, Risk: Low"
        }
        
        # Execute the tool (should return an error)
        result = self.teps.execute_tool(tool_request)
        
        # Verify the result
        self.assertEqual(result["status"], "error")
        self.assertIn("not specified", result["data"]["error_message"].lower())
    
    def test_action_description(self):
        """Test generating action descriptions for different tools."""
        # Test bash command description
        bash_desc = self.teps._get_action_description("executeBashCommand", {"command": "ls -la"})
        self.assertEqual(bash_desc, "BASH: ls -la")
        
        # Test read file description
        read_desc = self.teps._get_action_description("readFile", {"path": "/etc/passwd"})
        self.assertEqual(read_desc, "READ FILE: /etc/passwd")
        
        # Test write file description
        write_desc = self.teps._get_action_description("writeFile", {
            "path": "/tmp/test.txt", 
            "content": "A" * 100
        })
        self.assertIn("WRITE FILE: /tmp/test.txt", write_desc)
        self.assertIn("100", write_desc)  # Should mention content length
        
        # Test unknown tool description
        unknown_desc = self.teps._get_action_description("unknownTool", {"param": "value"})
        self.assertIn("TOOL: unknownTool", unknown_desc)
        self.assertIn("param", unknown_desc)
    
    @patch('os.path.exists', return_value=True)
    def test_load_allowlist(self, mock_exists):
        """Test loading the command allowlist."""
        # Mock open to provide a dummy allowlist file
        with patch('builtins.open', mock_open(read_data="ls\npwd\n# Comment\necho")) as mock_file:
            # Load the allowlist
            allowlist = self.teps._load_allowlist("dummy_allowlist.txt")
            
            # Verify the allowlist was loaded correctly
            self.assertEqual(len(allowlist), 3)
            self.assertIn("ls", allowlist)
            self.assertIn("pwd", allowlist)
            self.assertIn("echo", allowlist)
            self.assertNotIn("# Comment", allowlist)
    
    @patch('os.path.exists', return_value=False)
    @patch('builtins.print')
    def test_load_allowlist_missing_file(self, mock_print, mock_exists):
        """Test loading a missing allowlist file."""
        # Try to load a non-existent allowlist file
        allowlist = self.teps._load_allowlist("nonexistent_file.txt")
        
        # Verify an empty allowlist was returned
        self.assertEqual(allowlist, [])

if __name__ == '__main__':
    unittest.main()
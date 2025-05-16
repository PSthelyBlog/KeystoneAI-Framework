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
        
        # Create a TEPS instance with bash command security configuration
        self.teps_with_bash_security = TEPSEngine({
            "bash": {
                "allowed_commands": ["ls", "cat", "echo", "grep", "find"],
                "blocked_commands": ["rm", "sudo", "su", "chmod", "chown"]
            }
        })
        
        # Create a temporary directory structure for path testing
        self.test_root_dir = tempfile.mkdtemp()
        self.test_subdir = os.path.join(self.test_root_dir, "subdir")
        os.makedirs(self.test_subdir, exist_ok=True)
        
        # Create a TEPS instance with project root path
        self.teps_with_project_root = TEPSEngine(project_root_path=self.test_root_dir)
    
    def tearDown(self):
        """Clean up after each test."""
        # Remove temporary directory structure
        try:
            os.rmdir(self.test_subdir)
            os.rmdir(self.test_root_dir)
        except:
            pass
    
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
                    "file_path": "/path/to/file.txt",
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
                    "file_path": "/path/to/file.txt",
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
        read_desc = self.teps._get_action_description("readFile", {"file_path": "/etc/passwd"})
        self.assertEqual(read_desc, "READ FILE: /etc/passwd")
        
        # Test write file description
        write_desc = self.teps._get_action_description("writeFile", {
            "file_path": "/tmp/test.txt", 
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

    def test_bash_command_blocked(self):
        """Test that blocked bash commands are rejected."""
        # Create a tool request for a blocked bash command
        tool_request = {
            "request_id": "test-blocked-1",
            "tool_name": "executeBashCommand",
            "parameters": {
                "command": "sudo apt update",
            },
            "icerc_full_text": "Intent: System update, Command: sudo apt update, Expected: Update package list, Risk: High"
        }
        
        # Execute the tool (should be blocked before user prompt)
        result = self.teps_with_bash_security.execute_tool(tool_request)
        
        # Verify the result
        self.assertEqual(result["request_id"], "test-blocked-1")
        self.assertEqual(result["tool_name"], "executeBashCommand")
        self.assertEqual(result["status"], "error")
        self.assertIn("blocked by security policy", result["data"]["error_message"])
        self.assertIn("sudo", result["data"]["error_message"])
    
    def test_bash_command_not_allowed(self):
        """Test that commands not in the allowed list are rejected."""
        # Create a tool request for a command not in the allowed list
        tool_request = {
            "request_id": "test-not-allowed-1",
            "tool_name": "executeBashCommand",
            "parameters": {
                "command": "wget https://example.com/file.txt",
            },
            "icerc_full_text": "Intent: Download file, Command: wget, Expected: File download, Risk: Medium"
        }
        
        # Execute the tool (should be rejected before user prompt)
        result = self.teps_with_bash_security.execute_tool(tool_request)
        
        # Verify the result
        self.assertEqual(result["request_id"], "test-not-allowed-1")
        self.assertEqual(result["tool_name"], "executeBashCommand")
        self.assertEqual(result["status"], "error")
        self.assertIn("not in the allowed commands list", result["data"]["error_message"])
        self.assertIn("wget", result["data"]["error_message"])
    
    def test_bash_command_allowed(self):
        """Test that allowed bash commands are properly validated."""
        # Mock user input to confirm the command
        with patch('builtins.input', return_value='y'), \
             patch('builtins.print'), \
             patch('subprocess.run') as mock_run:
            
            # Configure the mock to return a successful result
            mock_process = MagicMock()
            mock_process.stdout = "command output"
            mock_process.stderr = ""
            mock_process.returncode = 0
            mock_run.return_value = mock_process
            
            # Create a tool request for an allowed bash command
            tool_request = {
                "request_id": "test-allowed-1",
                "tool_name": "executeBashCommand",
                "parameters": {
                    "command": "ls -la /tmp",
                },
                "icerc_full_text": "Intent: List files, Command: ls -la /tmp, Expected: File listing, Risk: Low"
            }
            
            # Execute the tool (should proceed to user confirmation)
            result = self.teps_with_bash_security.execute_tool(tool_request)
            
            # Verify the result
            self.assertEqual(result["request_id"], "test-allowed-1")
            self.assertEqual(result["tool_name"], "executeBashCommand")
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["data"]["stdout"], "command output")
    
    def test_parse_command_with_arguments(self):
        """Test parsing commands with arguments to correctly identify the main command."""
        # Create a tool request with a command that has arguments
        tool_request = {
            "request_id": "test-parse-1",
            "tool_name": "executeBashCommand",
            "parameters": {
                "command": "grep -r 'pattern' /path/to/dir",
            },
            "icerc_full_text": "Intent: Search for pattern, Command: grep, Expected: Search results, Risk: Low"
        }
        
        # Mock user input to confirm the command
        with patch('builtins.input', return_value='y'), \
             patch('builtins.print'), \
             patch('subprocess.run') as mock_run:
            
            # Configure the mock to return a successful result
            mock_process = MagicMock()
            mock_process.stdout = "pattern found"
            mock_process.stderr = ""
            mock_process.returncode = 0
            mock_run.return_value = mock_process
            
            # Execute the tool
            result = self.teps_with_bash_security.execute_tool(tool_request)
            
            # Verify the result
            self.assertEqual(result["status"], "success")
            # grep is in the allowed list, so it should be allowed
    
    def test_empty_command_lists(self):
        """Test behavior when both allowed and blocked command lists are empty."""
        # Create a TEPS instance with empty command lists
        teps_with_empty_lists = TEPSEngine({
            "bash": {
                "allowed_commands": [],
                "blocked_commands": []
            }
        })
        
        # Mock user input to confirm the command
        with patch('builtins.input', return_value='y'), \
             patch('builtins.print'), \
             patch('subprocess.run') as mock_run:
            
            # Configure the mock to return a successful result
            mock_process = MagicMock()
            mock_process.stdout = "command output"
            mock_process.stderr = ""
            mock_process.returncode = 0
            mock_run.return_value = mock_process
            
            # Create a tool request for any command
            tool_request = {
                "request_id": "test-empty-lists-1",
                "tool_name": "executeBashCommand",
                "parameters": {
                    "command": "any-command -with args",
                },
                "icerc_full_text": "Intent: Test command, Command: any-command, Expected: Output, Risk: Low"
            }
            
            # Execute the tool (should proceed to user confirmation since lists are empty)
            result = teps_with_empty_lists.execute_tool(tool_request)
            
            # Verify the result
            self.assertEqual(result["status"], "success")
    
    def test_invalid_command_format(self):
        """Test handling invalid command format."""
        # Create a tool request with an invalid command format
        tool_request = {
            "request_id": "test-invalid-format-1",
            "tool_name": "executeBashCommand",
            "parameters": {
                "command": "echo 'unclosed quote",  # Missing closing quote
            },
            "icerc_full_text": "Intent: Echo text, Command: echo, Expected: Text output, Risk: Low"
        }
        
        # Execute the tool (should return error about invalid format)
        result = self.teps_with_bash_security.execute_tool(tool_request)
        
        # Verify the result
        self.assertEqual(result["request_id"], "test-invalid-format-1")
        self.assertEqual(result["tool_name"], "executeBashCommand")
        self.assertEqual(result["status"], "error")
        self.assertIn("Invalid command format", result["data"]["error_message"])
    
    def test_is_path_within_project_root(self):
        """Test the path validation helper method directly."""
        # Test with path inside project root
        inside_path = os.path.join(self.test_root_dir, "file.txt")
        self.assertTrue(self.teps_with_project_root._is_path_within_project_root(inside_path))
        
        # Test with subdirectory path
        subdir_path = os.path.join(self.test_subdir, "file.txt")
        self.assertTrue(self.teps_with_project_root._is_path_within_project_root(subdir_path))
        
        # Test with project root itself
        self.assertTrue(self.teps_with_project_root._is_path_within_project_root(self.test_root_dir))
        
        # Test with path outside project root
        parent_dir = os.path.dirname(self.test_root_dir)
        self.assertFalse(self.teps_with_project_root._is_path_within_project_root(parent_dir))
        
        # Test with sibling directory
        sibling_dir = os.path.join(parent_dir, "sibling")
        self.assertFalse(self.teps_with_project_root._is_path_within_project_root(sibling_dir))
        
        # Test with path containing parent traversal that resolves inside
        path_with_parent_inside = os.path.join(self.test_subdir, "..", "file.txt")
        self.assertTrue(self.teps_with_project_root._is_path_within_project_root(path_with_parent_inside))
        
        # Test with path containing parent traversal that resolves outside
        path_with_parent_outside = os.path.join(self.test_root_dir, "..", "file.txt")
        self.assertFalse(self.teps_with_project_root._is_path_within_project_root(path_with_parent_outside))
        
        # Test with relative path (should be resolved to absolute)
        relative_path = "./file.txt"
        # This should be treated as relative to current working directory, not project_root_path
        absolute_of_relative = os.path.abspath(relative_path)
        # The result depends on whether current working directory is within project_root_path
        expected_result = os.path.commonpath([self.test_root_dir, absolute_of_relative]) == self.test_root_dir
        self.assertEqual(self.teps_with_project_root._is_path_within_project_root(relative_path), expected_result)
    
    def test_path_validation_disabled(self):
        """Test behavior when no project root is configured."""
        # The regular TEPS instance has no project root configured
        # All paths should be allowed
        arbitrary_path = "/etc/passwd"
        self.assertTrue(self.teps._is_path_within_project_root(arbitrary_path))
    
    @patch('builtins.input', return_value='y')
    @patch('builtins.print')
    def test_readfile_path_denied(self, mock_print, mock_input):
        """Test that file read operations outside project root are denied."""
        # Create a tool request for reading a file outside project root
        tool_request = {
            "request_id": "test-read-denied-1",
            "tool_name": "readFile",
            "parameters": {
                "file_path": "/etc/passwd",  # Typically outside project root
            },
            "icerc_full_text": "Intent: Read system file, Command: Read /etc/passwd, Expected: File content, Risk: High"
        }
        
        # Execute the tool (should be denied before user prompt)
        result = self.teps_with_project_root.execute_tool(tool_request)
        
        # Verify the result
        self.assertEqual(result["status"], "error")
        self.assertIn("Access to path '/etc/passwd' is denied", result["data"]["error_message"])
    
    @patch('builtins.input', return_value='y')
    @patch('builtins.print')
    def test_writefile_path_denied(self, mock_print, mock_input):
        """Test that file write operations outside project root are denied."""
        # Create a tool request for writing a file outside project root
        tool_request = {
            "request_id": "test-write-denied-1",
            "tool_name": "writeFile",
            "parameters": {
                "file_path": "/tmp/unsafe.txt",  # Typically outside project root
                "content": "unsafe content"
            },
            "icerc_full_text": "Intent: Write system file, Command: Write to /tmp/unsafe.txt, Expected: File written, Risk: High"
        }
        
        # Execute the tool (should be denied before user prompt)
        result = self.teps_with_project_root.execute_tool(tool_request)
        
        # Verify the result
        self.assertEqual(result["status"], "error")
        self.assertIn("Access to path '/tmp/unsafe.txt' is denied", result["data"]["error_message"])
    
    @patch('builtins.input', return_value='y')
    @patch('builtins.print')
    def test_readfile_path_allowed(self, mock_print, mock_input):
        """Test that file read operations inside project root are allowed."""
        # Create a safe path inside project root
        safe_file_path = os.path.join(self.test_root_dir, "safe_file.txt")
        
        # Mock open to avoid actually reading files
        with patch('builtins.open', mock_open(read_data="safe content")) as mock_file:
            # Create a tool request for reading a file inside project root
            tool_request = {
                "request_id": "test-read-allowed-1",
                "tool_name": "readFile",
                "parameters": {
                    "file_path": safe_file_path,
                },
                "icerc_full_text": f"Intent: Read file, Command: Read {safe_file_path}, Expected: File content, Risk: Low"
            }
            
            # Execute the tool (should proceed to user confirmation)
            result = self.teps_with_project_root.execute_tool(tool_request)
            
            # Verify the result
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["data"]["content"], "safe content")
    
    @patch('builtins.input', return_value='y')
    @patch('builtins.print')
    def test_writefile_path_allowed(self, mock_print, mock_input):
        """Test that file write operations inside project root are allowed."""
        # Create a safe path inside project root
        safe_file_path = os.path.join(self.test_root_dir, "safe_file.txt")
        
        # Mock open to avoid actually writing files
        with patch('builtins.open', mock_open()) as mock_file, \
             patch('os.path.dirname', return_value=self.test_root_dir) as mock_dirname, \
             patch('os.path.exists', return_value=True) as mock_exists, \
             patch('os.makedirs') as mock_makedirs:
            
            # Create a tool request for writing a file inside project root
            tool_request = {
                "request_id": "test-write-allowed-1",
                "tool_name": "writeFile",
                "parameters": {
                    "file_path": safe_file_path,
                    "content": "safe content",
                },
                "icerc_full_text": f"Intent: Write file, Command: Write to {safe_file_path}, Expected: File written, Risk: Low"
            }
            
            # Execute the tool (should proceed to user confirmation)
            result = self.teps_with_project_root.execute_tool(tool_request)
            
            # Verify the result
            self.assertEqual(result["status"], "success")
            self.assertIn("written successfully", result["data"]["status"])
            
            # Verify open was called with the correct path
            mock_file.assert_called_once()

if __name__ == '__main__':
    unittest.main()
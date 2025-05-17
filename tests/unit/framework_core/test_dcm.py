"""
Unit tests for the DynamicContextManager class.

This module tests the functionality of the DynamicContextManager class
located in framework_core/dcm.py.
"""

import os
import re
import pytest
import logging
import tempfile
from unittest.mock import patch, mock_open, MagicMock, ANY, call

from framework_core.dcm import DynamicContextManager


class TestDynamicContextManager:
    """Test suite for the DynamicContextManager class."""
    
    def test_init_with_valid_context_file(self):
        """Test initialization with a valid context file."""
        # Setup
        valid_context_content = """
        # This is a comment
        ## Section One
        doc1: @path/to/doc1.md
        
        ## Personas
        persona1: @persona1.md
        
        # initial_prompt_template: "Test prompt template"
        """
        
        doc1_content = "Document 1 content"
        persona1_content = "Persona 1 content"
        
        # Define the behavior of os.path.exists to return True for the context file and referenced docs
        def mock_exists(path):
            return True
        
        # Define the behavior of open to return different content based on the file being opened
        def mock_open_func(file, mode, encoding=None):
            mock = MagicMock()
            if "context" in str(file):
                mock.read.return_value = valid_context_content
            elif "doc1.md" in str(file):
                mock.read.return_value = doc1_content
            elif "persona1.md" in str(file):
                mock.read.return_value = persona1_content
            
            # Create a mock file object that can be read line by line
            mock.__enter__.return_value.read.return_value = mock.read.return_value
            mock.__enter__.return_value.__iter__.return_value = mock.read.return_value.splitlines(True)
            
            return mock
        
        # Mock os.path.isabs to handle path resolution
        def mock_isabs(path):
            return path.startswith('/') or path.startswith('C:')
        
        # Mock os.path.abspath to handle path resolution
        def mock_abspath(path):
            if path.startswith('/') or path.startswith('C:'):
                return path
            return f"/base_dir/{path}"
        
        # Mock os.path.dirname to return the directory part of a path
        def mock_dirname(path):
            return "/base_dir"
        
        # Mock os.path.join to join path components
        def mock_join(dir, file):
            return f"{dir}/{file}"
        
        # Create the mocks
        with patch('os.path.exists', side_effect=mock_exists), \
            patch('builtins.open', side_effect=mock_open_func), \
            patch('os.path.isabs', side_effect=mock_isabs), \
            patch('os.path.abspath', side_effect=mock_abspath), \
            patch('os.path.dirname', side_effect=mock_dirname), \
            patch('os.path.join', side_effect=mock_join):
            
            # Act
            dcm = DynamicContextManager("context_file.md")
            
            # Assert
            assert dcm._loaded_docs.get("doc1") == doc1_content
            assert dcm._loaded_docs.get("persona1") == persona1_content
            assert dcm._persona_definitions.get("persona1") == persona1_content
            assert dcm._initial_prompt_template == "Test prompt template"
    
    def test_init_with_file_not_found(self):
        """Test initialization with a context file that doesn't exist."""
        # Mock builtins.open to raise FileNotFoundError
        mock_open_func = mock_open()
        mock_open_func.side_effect = FileNotFoundError("No such file")
        
        with patch('builtins.open', mock_open_func):
            # Act
            # The FileNotFoundError is caught inside __init__, so we need to check if 
            # the error was logged and no documents were loaded
            dcm = DynamicContextManager("nonexistent_file.md")
            
            # Assert
            assert len(dcm._loaded_docs) == 0
            assert len(dcm._persona_definitions) == 0
    
    def test_init_with_custom_encoding(self):
        """Test initialization with custom encoding."""
        # Setup - create a mock for open that tracks calls with encoding parameter
        mock_open_func = MagicMock()
        context_content = "## Section\ndoc1: @path/to/doc1.md"
        
        # Create a mock file object for the context file
        context_mock = MagicMock()
        context_mock.read.return_value = context_content
        context_mock.__enter__.return_value.read.return_value = context_content
        context_mock.__enter__.return_value.__iter__.return_value = context_content.splitlines(True)
        
        # Create a mock file object for the document file
        doc_mock = MagicMock()
        doc_mock.read.return_value = "Document content"
        doc_mock.__enter__.return_value.read.return_value = "Document content"
        
        # Configure the mock_open_func to return different mocks based on the file path
        def side_effect(file_path, mode, encoding=None):
            if "context_file.md" in str(file_path):
                return context_mock
            else:
                return doc_mock
        
        mock_open_func.side_effect = side_effect
        
        # Create the mocks
        with patch('os.path.exists', return_value=True), \
            patch('builtins.open', mock_open_func), \
            patch('os.path.isabs', return_value=False), \
            patch('os.path.abspath', return_value="/base_dir/path/to/doc1.md"), \
            patch('os.path.dirname', return_value="/base_dir"), \
            patch('os.path.join', return_value="/base_dir/path/to/doc1.md"):
            
            # Act
            dcm = DynamicContextManager("context_file.md", encoding="utf-16")
            
            # Assert
            # Check that the custom encoding was used in the call to open
            calls = [call for call in mock_open_func.mock_calls if isinstance(call, call.__class__)]
            
            # Verify at least one call was made with the utf-16 encoding
            encoding_used = False
            for call_obj in calls:
                args, kwargs = call_obj.args, call_obj.kwargs
                if len(args) >= 1 and "context_file.md" in str(args[0]) and kwargs.get('encoding') == 'utf-16':
                    encoding_used = True
                    break
            
            assert encoding_used, "Custom encoding (utf-16) was not used when opening the file"
    
    def test_init_with_custom_logger(self):
        """Test initialization with a custom logger."""
        # Setup
        custom_logger = logging.getLogger("custom_logger")
        
        with patch('os.path.exists', return_value=True), \
            patch('builtins.open', mock_open(read_data="# Empty context")), \
            patch('os.path.isabs', return_value=False), \
            patch('os.path.abspath', return_value="/base_dir"), \
            patch('os.path.dirname', return_value="/base_dir"), \
            patch('os.path.join', return_value="/base_dir"):
            
            # Act
            dcm = DynamicContextManager("context_file.md", logger=custom_logger)
            
            # Assert
            assert dcm.logger == custom_logger
    
    def test_init_with_missing_referenced_document(self):
        """Test initialization with a missing referenced document."""
        # Setup
        context_content = "## Section\ndoc1: @missing_doc.md"
        
        def mock_exists(path):
            # Return True for context file, False for the referenced document
            return "context" in str(path)
        
        # Define the behavior for open to raise FileNotFoundError for the missing document
        def mock_open_func(file, mode, encoding=None):
            mock = MagicMock()
            if "context" in str(file):
                mock.read.return_value = context_content
                mock.__enter__.return_value.read.return_value = context_content
                mock.__enter__.return_value.__iter__.return_value = context_content.splitlines(True)
                return mock
            else:
                raise FileNotFoundError(f"No such file: {file}")
        
        # Create the mocks
        with patch('os.path.exists', side_effect=mock_exists), \
            patch('builtins.open', side_effect=mock_open_func), \
            patch('os.path.isabs', return_value=False), \
            patch('os.path.abspath', return_value="/base_dir/missing_doc.md"), \
            patch('os.path.dirname', return_value="/base_dir"), \
            patch('os.path.join', return_value="/base_dir/missing_doc.md"), \
            patch('logging.Logger.warning') as mock_warning:
            
            # Act - DCM should still initialize but log a warning
            dcm = DynamicContextManager("context_file.md")
            
            # Assert
            # Should log a warning but not raise exception
            mock_warning.assert_called()
            assert "doc1" not in dcm._loaded_docs
    
    def test_init_with_malformed_line(self):
        """Test initialization with malformed lines in the context file."""
        # Setup
        context_content = """
        ## Section
        malformed_line
        doc1: @valid_doc.md
        """
        
        with patch('os.path.exists', return_value=True), \
            patch('builtins.open', mock_open(read_data=context_content)), \
            patch('os.path.isabs', return_value=False), \
            patch('os.path.abspath', return_value="/base_dir/valid_doc.md"), \
            patch('os.path.dirname', return_value="/base_dir"), \
            patch('os.path.join', return_value="/base_dir/valid_doc.md"), \
            patch('logging.Logger.debug') as mock_debug:
            
            # Act - DCM should still initialize and skip the malformed line
            dcm = DynamicContextManager("context_file.md")
            
            # Assert - should continue parsing and not raise an exception
            assert dcm is not None
    
    def test_resolve_path_with_absolute_path(self):
        """Test _resolve_path with an absolute path."""
        # Setup
        absolute_path = "/absolute/path/to/file.md"
        
        with patch('os.path.isabs', return_value=True), \
            patch('os.path.abspath', return_value=absolute_path):
            
            # Act
            dcm = DynamicContextManager("context_file.md")
            path = dcm._resolve_path(absolute_path)
            
            # Assert
            assert path == absolute_path
    
    def test_resolve_path_with_relative_path(self):
        """Test _resolve_path with a relative path."""
        # Setup
        relative_path = "relative/path/to/file.md"
        resolved_path = "/base_dir/relative/path/to/file.md"
        
        with patch('os.path.exists', return_value=True), \
            patch('builtins.open', mock_open(read_data="")), \
            patch('os.path.isabs', return_value=False), \
            patch('os.path.abspath') as mock_abspath, \
            patch('os.path.dirname', return_value="/base_dir"), \
            patch('os.path.join', return_value="/base_dir/relative/path/to/file.md"):
            
            mock_abspath.side_effect = lambda p: p if p.startswith('/') else resolved_path
            
            # Act
            dcm = DynamicContextManager("context_file.md")
            path = dcm._resolve_path(relative_path)
            
            # Assert
            assert path == resolved_path
    
    def test_resolve_path_with_dot_prefix(self):
        """Test _resolve_path with a path starting with ./"""
        # Setup
        dot_path = "./path/to/file.md"
        expected_path = "/base_dir/path/to/file.md"
        
        with patch('os.path.exists', return_value=True), \
            patch('builtins.open', mock_open(read_data="")), \
            patch('os.path.isabs', return_value=False), \
            patch('os.path.abspath', return_value="/base_dir/path/to/file.md"), \
            patch('os.path.dirname', return_value="/base_dir"), \
            patch('os.path.join', return_value="/base_dir/path/to/file.md"):
            
            # Act
            dcm = DynamicContextManager("context_file.md")
            path = dcm._resolve_path(dot_path)
            
            # Assert
            assert path == expected_path
    
    def test_resolve_path_security_check(self):
        """Test _resolve_path security check against path traversal."""
        # Setup
        traversal_path = "../../etc/passwd"
        
        # The security check in _resolve_path is based on the resolved path starting with os.path.abspath(os.sep)
        # So we need to mock os.path.abspath(os.sep) to return something specific like "/", 
        # and then make our path NOT start with that
        
        # Helper function to mock abspath behavior
        def mock_abspath(path):
            if path == os.sep:
                return "/root"  # Make the security check expect paths to start with "/root"
            if "context_file.md" in path:
                return "/base_dir/context_file.md"
            if "../../" in path or path == os.path.join("/base_dir", traversal_path):
                # This simulates a path traversal - returning a path that doesn't start with "/root"
                return "/etc/passwd"
            return path
        
        with patch('os.path.exists', return_value=True), \
            patch('builtins.open', mock_open(read_data="")), \
            patch('os.path.isabs', return_value=False), \
            patch('os.path.abspath', side_effect=mock_abspath), \
            patch('os.path.dirname', return_value="/base_dir"), \
            patch('os.path.join', side_effect=lambda a, b: f"{a}/{b}"):
            
            # Act & Assert
            dcm = DynamicContextManager("context_file.md")
            
            # Mock the warning first to ensure it's called
            with patch.object(dcm.logger, 'warning') as mock_warning:
                # Perform both assertions within the same try-catch
                try:
                    # This should raise ValueError
                    dcm._resolve_path(traversal_path)
                    pytest.fail("Should have raised ValueError")
                except ValueError as e:
                    # Verify the exception message
                    assert f"Invalid path: {traversal_path}" in str(e)
                    # Verify that a warning was logged for the suspicious path
                    mock_warning.assert_called_once()
                    assert "Suspicious path" in mock_warning.call_args[0][0]
    
    def test_get_full_initial_context(self):
        """Test get_full_initial_context returns all loaded documents."""
        # Setup
        with patch('os.path.exists', return_value=True), \
            patch('builtins.open', mock_open(read_data="")), \
            patch('os.path.isabs', return_value=False), \
            patch('os.path.abspath', return_value="/base_dir"), \
            patch('os.path.dirname', return_value="/base_dir"), \
            patch('os.path.join', return_value="/base_dir"):
            
            # Act
            dcm = DynamicContextManager("context_file.md")
            dcm._loaded_docs = {"doc1": "content1", "doc2": "content2"}
            context = dcm.get_full_initial_context()
            
            # Assert
            assert context == {"doc1": "content1", "doc2": "content2"}
            # Ensure it returns a copy, not the original
            assert context is not dcm._loaded_docs
    
    def test_get_document_content_existing(self):
        """Test get_document_content returns content for an existing doc_id."""
        # Setup
        with patch('os.path.exists', return_value=True), \
            patch('builtins.open', mock_open(read_data="")), \
            patch('os.path.isabs', return_value=False), \
            patch('os.path.abspath', return_value="/base_dir"), \
            patch('os.path.dirname', return_value="/base_dir"), \
            patch('os.path.join', return_value="/base_dir"):
            
            # Act
            dcm = DynamicContextManager("context_file.md")
            dcm._loaded_docs = {"existing_doc": "Document content"}
            content = dcm.get_document_content("existing_doc")
            
            # Assert
            assert content == "Document content"
    
    def test_get_document_content_nonexistent(self):
        """Test get_document_content returns None for a non-existent doc_id."""
        # Setup
        with patch('os.path.exists', return_value=True), \
            patch('builtins.open', mock_open(read_data="")), \
            patch('os.path.isabs', return_value=False), \
            patch('os.path.abspath', return_value="/base_dir"), \
            patch('os.path.dirname', return_value="/base_dir"), \
            patch('os.path.join', return_value="/base_dir"):
            
            # Act
            dcm = DynamicContextManager("context_file.md")
            dcm._loaded_docs = {"existing_doc": "Document content"}
            content = dcm.get_document_content("nonexistent_doc")
            
            # Assert
            assert content is None
    
    def test_get_persona_definitions(self):
        """Test get_persona_definitions returns all persona definitions."""
        # Setup
        with patch('os.path.exists', return_value=True), \
            patch('builtins.open', mock_open(read_data="")), \
            patch('os.path.isabs', return_value=False), \
            patch('os.path.abspath', return_value="/base_dir"), \
            patch('os.path.dirname', return_value="/base_dir"), \
            patch('os.path.join', return_value="/base_dir"):
            
            # Act
            dcm = DynamicContextManager("context_file.md")
            dcm._persona_definitions = {"persona1": "Definition 1", "persona2": "Definition 2"}
            personas = dcm.get_persona_definitions()
            
            # Assert
            assert personas == {"persona1": "Definition 1", "persona2": "Definition 2"}
            # Ensure it returns a copy, not the original
            assert personas is not dcm._persona_definitions
    
    def test_get_initial_prompt_template_exists(self):
        """Test get_initial_prompt_template when template exists."""
        # Setup
        with patch('os.path.exists', return_value=True), \
            patch('builtins.open', mock_open(read_data="")), \
            patch('os.path.isabs', return_value=False), \
            patch('os.path.abspath', return_value="/base_dir"), \
            patch('os.path.dirname', return_value="/base_dir"), \
            patch('os.path.join', return_value="/base_dir"):
            
            # Act
            dcm = DynamicContextManager("context_file.md")
            dcm._initial_prompt_template = "Template content"
            template = dcm.get_initial_prompt_template()
            
            # Assert
            assert template == "Template content"
    
    def test_get_initial_prompt_template_not_exists(self):
        """Test get_initial_prompt_template when template doesn't exist."""
        # Setup
        with patch('os.path.exists', return_value=True), \
            patch('builtins.open', mock_open(read_data="")), \
            patch('os.path.isabs', return_value=False), \
            patch('os.path.abspath', return_value="/base_dir"), \
            patch('os.path.dirname', return_value="/base_dir"), \
            patch('os.path.join', return_value="/base_dir"):
            
            # Act
            dcm = DynamicContextManager("context_file.md")
            dcm._initial_prompt_template = None
            template = dcm.get_initial_prompt_template()
            
            # Assert
            assert template is None
"""
Unit tests for the DCMManager class.

This module tests the functionality of the DCMManager class
located in framework_core/component_managers/dcm_manager.py.
"""

import os
import pytest
from unittest.mock import patch, MagicMock, ANY

from framework_core.component_managers.dcm_manager import DCMManager
from framework_core.exceptions import DCMInitError, ConfigError


class TestDCMManager:
    """Test suite for the DCMManager class."""
    
    def test_init_with_context_path(self):
        """Test initialization with a context definition path."""
        # Setup
        context_path = "/path/to/context.md"
        
        # Act
        dcm_manager = DCMManager(context_path)
        
        # Assert
        assert dcm_manager.context_definition_path == context_path
        assert dcm_manager.dcm_instance is None
    
    def test_init_without_context_path(self):
        """Test initialization without a context definition path."""
        # Act
        dcm_manager = DCMManager()
        
        # Assert
        assert dcm_manager.context_definition_path is None
        assert dcm_manager.dcm_instance is None
    
    def test_initialize_success(self):
        """Test successful initialization of the DCM component."""
        # Setup
        context_path = "/path/to/context.md"
        mock_dcm_instance = MagicMock()
        
        # Create the DCMManager instance
        dcm_manager = DCMManager(context_path)
        
        # The import is done inside the initialize method, so we need to patch the module directly
        real_import = __import__
        
        def mock_import(name, *args, **kwargs):
            if name == 'framework_core.dcm':
                module = MagicMock()
                module.DynamicContextManager = MagicMock(return_value=mock_dcm_instance)
                return module
            return real_import(name, *args, **kwargs)
        
        # Mock the import function
        with patch('builtins.__import__', side_effect=mock_import):
            # Act
            dcm_manager.initialize()
            
            # Assert
            assert dcm_manager.dcm_instance is mock_dcm_instance
    
    def test_initialize_missing_context_path(self):
        """Test initialization fails when context_definition_path is None."""
        # Setup
        dcm_manager = DCMManager()
        
        # Act & Assert
        with pytest.raises(ConfigError) as excinfo:
            dcm_manager.initialize()
        
        assert "Context definition path is required" in str(excinfo.value)
    
    def test_initialize_dcm_error(self):
        """Test initialization fails when DynamicContextManager raises an exception."""
        # Setup
        context_path = "/path/to/context.md"
        dcm_manager = DCMManager(context_path)
        
        # The import is done inside the initialize method, so we need to patch the module directly
        real_import = __import__
        
        def mock_import(name, *args, **kwargs):
            if name == 'framework_core.dcm':
                module = MagicMock()
                # Configure the mock to raise an exception when instantiated
                module.DynamicContextManager = MagicMock(side_effect=Exception("DCM initialization failed"))
                return module
            return real_import(name, *args, **kwargs)
        
        # Mock the import function
        with patch('builtins.__import__', side_effect=mock_import):
            # Act & Assert
            with pytest.raises(DCMInitError) as excinfo:
                dcm_manager.initialize()
            
            assert "Failed to initialize DCM" in str(excinfo.value)
    
    def test_get_initial_prompt_exists(self):
        """Test get_initial_prompt when a template exists."""
        # Setup
        dcm_manager = DCMManager("/path/to/context.md")
        mock_dcm_instance = MagicMock()
        mock_dcm_instance.get_initial_prompt_template.return_value = "Template content"
        dcm_manager.dcm_instance = mock_dcm_instance
        
        # Act
        result = dcm_manager.get_initial_prompt()
        
        # Assert
        assert result == "Template content"
        mock_dcm_instance.get_initial_prompt_template.assert_called_once()
    
    def test_get_initial_prompt_not_exists(self):
        """Test get_initial_prompt when no template exists."""
        # Setup
        dcm_manager = DCMManager("/path/to/context.md")
        mock_dcm_instance = MagicMock()
        mock_dcm_instance.get_initial_prompt_template.return_value = None
        dcm_manager.dcm_instance = mock_dcm_instance
        
        # Act
        result = dcm_manager.get_initial_prompt()
        
        # Assert
        assert result is None
        mock_dcm_instance.get_initial_prompt_template.assert_called_once()
    
    def test_get_initial_prompt_not_initialized(self):
        """Test get_initial_prompt when DCM is not initialized."""
        # Setup
        dcm_manager = DCMManager("/path/to/context.md")
        dcm_manager.dcm_instance = None
        
        # Act & Assert
        with pytest.raises(DCMInitError) as excinfo:
            dcm_manager.get_initial_prompt()
        
        assert "DCM is not initialized" in str(excinfo.value)
    
    def test_get_full_context(self):
        """Test get_full_context delegates to DCM instance."""
        # Setup
        dcm_manager = DCMManager("/path/to/context.md")
        mock_dcm_instance = MagicMock()
        mock_dcm_instance.get_full_initial_context.return_value = {"doc1": "content1", "doc2": "content2"}
        dcm_manager.dcm_instance = mock_dcm_instance
        
        # Act
        result = dcm_manager.get_full_context()
        
        # Assert
        assert result == {"doc1": "content1", "doc2": "content2"}
        mock_dcm_instance.get_full_initial_context.assert_called_once()
    
    def test_get_full_context_not_initialized(self):
        """Test get_full_context when DCM is not initialized."""
        # Setup
        dcm_manager = DCMManager("/path/to/context.md")
        dcm_manager.dcm_instance = None
        
        # Act & Assert
        with pytest.raises(DCMInitError) as excinfo:
            dcm_manager.get_full_context()
        
        assert "DCM is not initialized" in str(excinfo.value)
    
    def test_get_document_content_exists(self):
        """Test get_document_content for an existing document."""
        # Setup
        doc_id = "test_doc"
        dcm_manager = DCMManager("/path/to/context.md")
        mock_dcm_instance = MagicMock()
        mock_dcm_instance.get_document_content.return_value = "Document content"
        dcm_manager.dcm_instance = mock_dcm_instance
        
        # Act
        result = dcm_manager.get_document_content(doc_id)
        
        # Assert
        assert result == "Document content"
        mock_dcm_instance.get_document_content.assert_called_once_with(doc_id)
    
    def test_get_document_content_not_exists(self):
        """Test get_document_content for a non-existent document."""
        # Setup
        doc_id = "nonexistent_doc"
        dcm_manager = DCMManager("/path/to/context.md")
        mock_dcm_instance = MagicMock()
        mock_dcm_instance.get_document_content.return_value = None
        dcm_manager.dcm_instance = mock_dcm_instance
        
        # Act
        result = dcm_manager.get_document_content(doc_id)
        
        # Assert
        assert result is None
        mock_dcm_instance.get_document_content.assert_called_once_with(doc_id)
    
    def test_get_document_content_not_initialized(self):
        """Test get_document_content when DCM is not initialized."""
        # Setup
        dcm_manager = DCMManager("/path/to/context.md")
        dcm_manager.dcm_instance = None
        
        # Act & Assert
        with pytest.raises(DCMInitError) as excinfo:
            dcm_manager.get_document_content("doc_id")
        
        assert "DCM is not initialized" in str(excinfo.value)
    
    def test_get_persona_definitions(self):
        """Test get_persona_definitions delegates to DCM instance."""
        # Setup
        dcm_manager = DCMManager("/path/to/context.md")
        mock_dcm_instance = MagicMock()
        mock_dcm_instance.get_persona_definitions.return_value = {"persona1": "def1", "persona2": "def2"}
        dcm_manager.dcm_instance = mock_dcm_instance
        
        # Act
        result = dcm_manager.get_persona_definitions()
        
        # Assert
        assert result == {"persona1": "def1", "persona2": "def2"}
        mock_dcm_instance.get_persona_definitions.assert_called_once()
    
    def test_get_persona_definitions_not_initialized(self):
        """Test get_persona_definitions when DCM is not initialized."""
        # Setup
        dcm_manager = DCMManager("/path/to/context.md")
        dcm_manager.dcm_instance = None
        
        # Act & Assert
        with pytest.raises(DCMInitError) as excinfo:
            dcm_manager.get_persona_definitions()
        
        assert "DCM is not initialized" in str(excinfo.value)
    
    def test_get_document_ids_with_loaded_docs(self):
        """Test get_document_ids when _loaded_docs is available."""
        # Setup
        dcm_manager = DCMManager("/path/to/context.md")
        mock_dcm_instance = MagicMock()
        mock_dcm_instance._loaded_docs = {"doc1": "content1", "doc2": "content2"}
        dcm_manager.dcm_instance = mock_dcm_instance
        
        # Act
        result = dcm_manager.get_document_ids()
        
        # Assert - order may vary, so convert to set for comparison
        assert set(result) == {"doc1", "doc2"}
    
    def test_get_document_ids_without_loaded_docs_attribute(self):
        """Test get_document_ids when _loaded_docs attribute doesn't exist."""
        # Setup
        dcm_manager = DCMManager("/path/to/context.md")
        mock_dcm_instance = MagicMock(spec=[])  # Empty spec means no attributes
        dcm_manager.dcm_instance = mock_dcm_instance
        
        # Act
        result = dcm_manager.get_document_ids()
        
        # Assert
        assert result == []
    
    def test_get_document_ids_not_initialized(self):
        """Test get_document_ids when DCM is not initialized."""
        # Setup
        dcm_manager = DCMManager("/path/to/context.md")
        dcm_manager.dcm_instance = None
        
        # Act & Assert
        with pytest.raises(DCMInitError) as excinfo:
            dcm_manager.get_document_ids()
        
        assert "DCM is not initialized" in str(excinfo.value)
    
    def test_ensure_initialized_success(self):
        """Test _ensure_initialized when DCM is initialized."""
        # Setup
        dcm_manager = DCMManager("/path/to/context.md")
        dcm_manager.dcm_instance = MagicMock()
        
        # Act & Assert - should not raise an exception
        dcm_manager._ensure_initialized()
    
    def test_ensure_initialized_failure(self):
        """Test _ensure_initialized when DCM is not initialized."""
        # Setup
        dcm_manager = DCMManager("/path/to/context.md")
        dcm_manager.dcm_instance = None
        
        # Act & Assert
        with pytest.raises(DCMInitError) as excinfo:
            dcm_manager._ensure_initialized()
        
        assert "DCM is not initialized" in str(excinfo.value)
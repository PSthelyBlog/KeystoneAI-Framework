#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dynamic Context Manager (DCM)

This module implements the DCM component of the AI-Assisted Framework V2,
responsible for parsing the FRAMEWORK_CONTEXT.md file, loading referenced documents,
and providing access to the loaded content.

AI-GENERATED: [Forge] - Task:[RFI-DCM-Core-001]
"""

import os
import re
import logging
import traceback
from typing import Dict, Optional, Union, Any


class DynamicContextManager:
    """
    Dynamic Context Manager for handling framework context definition and document loading.
    
    This class parses a context definition file (FRAMEWORK_CONTEXT.md), loads all
    referenced documents, and provides methods to access the loaded content. It supports
    sectioned document organization, special directives like initial_prompt_template,
    and robust error handling.
    """
    
    def __init__(self, context_definition_file_path: str, encoding: str = "utf-8", logger: Optional[logging.Logger] = None):
        """
        Initialize the Dynamic Context Manager with a path to the context definition file.
        
        Args:
            context_definition_file_path: Path to the FRAMEWORK_CONTEXT.md file
            encoding: Character encoding for file operations (default: utf-8)
            logger: Optional logger instance for recording parsing progress and errors
        """
        self.base_path = os.path.dirname(os.path.abspath(context_definition_file_path))
        self.encoding = encoding
        self.logger = logger or self._get_default_logger()
        
        # Internal state
        self._loaded_docs = {}  # All loaded documents: doc_id -> content
        self._persona_definitions = {}  # Subset for personas: persona_id -> content
        self._initial_prompt_template = None  # Optional initial prompt template
        
        # Parse the context file
        try:
            self._parse_context_file(context_definition_file_path)
        except Exception as e:
            self.logger.error(f"Failed to parse context file: {e}")
            self.logger.debug(traceback.format_exc())
    
    def _get_default_logger(self) -> logging.Logger:
        """
        Create and return a default logger if none is provided.
        
        Returns:
            A configured logger instance
        """
        logger = logging.getLogger("dcm")
        
        # Configure logger if it doesn't have handlers already
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        
        return logger
    
    def _parse_context_file(self, file_path: str) -> None:
        """
        Parse the context definition file, extracting section markers, doc_ids, 
        and loading referenced documents.
        
        Args:
            file_path: Path to the context definition file
        """
        self.logger.info(f"Parsing context file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding=self.encoding) as f:
                current_section = None
                line_number = 0
                
                for line in f:
                    line_number += 1
                    line = line.strip()
                    
                    # Skip empty lines
                    if not line:
                        continue
                    
                    # Check for initial prompt template directive
                    if line.startswith('# initial_prompt_template:'):
                        try:
                            # Extract the template text which may be in quotes
                            template_text = line.split(':', 1)[1].strip()
                            
                            # Remove surrounding quotes if present
                            if (template_text.startswith('"') and template_text.endswith('"')) or \
                               (template_text.startswith("'") and template_text.endswith("'")):
                                template_text = template_text[1:-1]
                                
                            self._initial_prompt_template = template_text
                            self.logger.info("Found initial prompt template")
                        except Exception as e:
                            self.logger.warning(f"Error parsing initial prompt template on line {line_number}: {e}")
                        continue
                    
                    # Skip other comment lines
                    if line.startswith('#') and not line.startswith('##'):
                        continue
                    
                    # Check for section headers
                    section_match = re.match(r"^##\s*(.+)", line)
                    if section_match:
                        current_section = section_match.group(1).lower().replace(" ", "_")
                        self.logger.debug(f"Found section: {current_section}")
                        continue
                    
                    # Process document references if we're in a section
                    if current_section:
                        doc_ref_match = re.match(r"([\w_]+):\s*@(.+)", line)
                        if doc_ref_match:
                            doc_id, rel_path = doc_ref_match.groups()
                            self.logger.debug(f"Found document reference: {doc_id} -> {rel_path}")
                            
                            try:
                                self._load_document(doc_id, rel_path, current_section)
                            except Exception as e:
                                self.logger.warning(f"Error loading document '{doc_id}' on line {line_number}: {e}")
        
        except FileNotFoundError:
            self.logger.error(f"Context file not found: {file_path}")
            raise
        except Exception as e:
            self.logger.error(f"Error parsing context file: {e}")
            self.logger.debug(traceback.format_exc())
            raise
    
    def _load_document(self, doc_id: str, file_path: str, section: str) -> None:
        """
        Load a single document from the given file path and store it in the internal state.
        
        Args:
            doc_id: The identifier for this document
            file_path: Path to the document file (relative or absolute)
            section: The section this document belongs to (e.g., "personas")
        """
        # Resolve the file path
        resolved_path = self._resolve_path(file_path)
        
        self.logger.debug(f"Loading document: {doc_id} from {resolved_path}")
        
        try:
            with open(resolved_path, 'r', encoding=self.encoding) as doc_file:
                content = doc_file.read()
                self._loaded_docs[doc_id] = content
                
                # Store persona definitions separately
                if section.lower() == "personas":
                    self._persona_definitions[doc_id] = content
                    self.logger.debug(f"Stored persona definition: {doc_id}")
                
                self.logger.info(f"Successfully loaded document: {doc_id}")
        
        except FileNotFoundError:
            self.logger.warning(f"Document file not found: {resolved_path}")
            raise
        except Exception as e:
            self.logger.warning(f"Error reading document file: {e}")
            self.logger.debug(traceback.format_exc())
            raise
    
    def _resolve_path(self, file_path: str) -> str:
        """
        Resolve a file path that could be relative to the base path or absolute.
        
        Args:
            file_path: The file path to resolve (relative or absolute)
            
        Returns:
            The resolved absolute path
        """
        # If it's an absolute path, use it directly
        if os.path.isabs(file_path):
            return file_path
        
        # Handle ./ prefix if present
        if file_path.startswith('./') or file_path.startswith('.\\'):
            file_path = file_path[2:]
        
        # Resolve relative to the base path
        resolved_path = os.path.abspath(os.path.join(self.base_path, file_path))
        
        # Security check to prevent directory traversal attacks
        if not resolved_path.startswith(os.path.abspath(os.sep)):
            self.logger.warning(f"Suspicious path detected, may be a directory traversal attempt: {file_path}")
            raise ValueError(f"Invalid path: {file_path}")
        
        return resolved_path
    
    def get_full_initial_context(self) -> Dict[str, str]:
        """
        Return all loaded documents as a dictionary mapping doc_id to content.
        
        Returns:
            Dictionary mapping doc_id to document content
        """
        return self._loaded_docs.copy()
    
    def get_document_content(self, doc_id: str) -> Optional[str]:
        """
        Get the content of a specific document by its ID.
        
        Args:
            doc_id: The identifier of the document
            
        Returns:
            Document content as string, or None if not found
        """
        return self._loaded_docs.get(doc_id)
    
    def get_persona_definitions(self) -> Dict[str, str]:
        """
        Get all persona definitions as a dictionary mapping persona_id to content.
        
        Returns:
            Dictionary mapping persona_id to persona definition content
        """
        return self._persona_definitions.copy()
    
    def get_initial_prompt_template(self) -> Optional[str]:
        """
        Get the initial prompt template if specified in the context file.
        
        Returns:
            Initial prompt template as string, or None if not specified
        """
        return self._initial_prompt_template
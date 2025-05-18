#!/usr/bin/env python3
"""
Debug script to check if persona definitions are loaded correctly.
"""

import os
import sys
from framework_core.dcm import DynamicContextManager

def main():
    """Check if persona definitions are loaded correctly."""
    print("Debugging persona definitions...")
    
    # Initialize DCM with the context definition file
    context_path = os.path.join(os.getcwd(), "config", "FRAMEWORK_CONTEXT.md")
    print(f"Loading context from: {context_path}")
    
    # Create DCM instance
    dcm = DynamicContextManager(context_path)
    
    # Get all loaded documents
    print("\nLoaded documents:")
    for doc_id in dcm._loaded_docs:
        print(f"  - {doc_id}")
    
    # Get persona definitions
    print("\nPersona definitions:")
    personas = dcm.get_persona_definitions()
    if not personas:
        print("  No personas found!")
    else:
        for persona_id in personas:
            print(f"  - {persona_id}")
    
    # Print section map for debugging
    print("\nSection detection:")
    print(f"  Core_persona_definitions correctly mapped: {'core_persona_definitions' in ['core_persona_definitions', 'personas']}")
    
    # Get file content and check section parsing
    if os.path.exists(context_path):
        with open(context_path, 'r') as f:
            content = f.read()
            print("\nSection headers in context file:")
            import re
            for line in content.split('\n'):
                if line.startswith('##'):
                    section = re.match(r"^##\s*(.+)", line)
                    if section:
                        section_name = section.group(1).lower().replace(" ", "_")
                        print(f"  - '{line}' -> '{section_name}'")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
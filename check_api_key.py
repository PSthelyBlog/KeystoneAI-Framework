#!/usr/bin/env python3
"""
Utility script to check if the required API keys are set.
"""

import os
import sys

def check_api_keys():
    """Check if the required API keys are set in the environment."""
    print("Checking API keys...")
    
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        print("\nERROR: GEMINI_API_KEY environment variable is not set.")
        print("\nPlease set the GEMINI_API_KEY environment variable with your Gemini API key:")
        print("  export GEMINI_API_KEY=your_api_key_here")
        print("\nYou can get a Gemini API key from: https://ai.google.dev/")
        return False
    else:
        masked_key = gemini_key[:4] + "..." + gemini_key[-4:] if len(gemini_key) > 8 else "****"
        print(f"✓ GEMINI_API_KEY is set: {masked_key}")
    
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if not anthropic_key:
        print("! ANTHROPIC_API_KEY is not set (optional)")
    else:
        masked_key = anthropic_key[:4] + "..." + anthropic_key[-4:] if len(anthropic_key) > 8 else "****"
        print(f"✓ ANTHROPIC_API_KEY is set: {masked_key}")
    
    print("\nAPI key check complete.")
    return True

if __name__ == "__main__":
    if not check_api_keys():
        sys.exit(1)
    sys.exit(0)
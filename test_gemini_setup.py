#!/usr/bin/env python3
"""
Test script to verify Gemini API setup and connectivity.
Run this script to ensure your API key is configured correctly.
"""

import os
import sys
from dotenv import load_dotenv

def test_gemini_setup():
    """Test Gemini API setup and basic functionality."""
    print("=" * 60)
    print("Gemini API Setup Test")
    print("=" * 60)

    # Load environment variables
    load_dotenv()

    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\nERROR: GOOGLE_API_KEY not found in environment variables")
        print("Please create a .env file with your API key:")
        print("  GOOGLE_API_KEY=your_api_key_here")
        return False

    print(f"\nAPI Key found: {api_key[:10]}...{api_key[-4:]}")

    # Test basic import
    try:
        import google.generativeai as genai
        print("google-generativeai package: INSTALLED")
    except ImportError:
        print("ERROR: google-generativeai package not installed")
        print("Run: pip install google-generativeai")
        return False

    # Configure API
    try:
        genai.configure(api_key=api_key)
        print("API configuration: SUCCESS")
    except Exception as e:
        print(f"ERROR configuring API: {e}")
        return False

    # Test basic generation
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say hello in one word.")
        print(f"\nTest generation: SUCCESS")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"ERROR during generation: {e}")
        return False

    # List available models
    try:
        print("\nAvailable Gemini models:")
        for model in genai.list_models():
            if 'gemini' in model.name.lower():
                print(f"  - {model.name}")
                print(f"    Supported: {model.supported_generation_methods}")
    except Exception as e:
        print(f"WARNING: Could not list models: {e}")

    print("\n" + "=" * 60)
    print("All tests passed! Gemini API is ready to use.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_gemini_setup()
    sys.exit(0 if success else 1)

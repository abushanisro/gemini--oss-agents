#!/usr/bin/env python3
"""
LangChain with Safety Settings Example

This example demonstrates how to configure safety settings when using
Gemini models with LangChain. Safety settings help control the model's
responses to potentially harmful or sensitive content.

Prerequisites:
- pip install langchain-google-genai python-dotenv
- Set GOOGLE_API_KEY in .env file
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.safety_config import SafetyPreset, SafetyThreshold
from src.error_handling import GeminiErrorHandler

# Load environment variables
load_dotenv()


def example_with_moderate_safety():
    """Example using moderate safety preset (recommended for most use cases)."""
    print("\n" + "="*60)
    print("Example 1: Moderate Safety Settings")
    print("="*60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        # Create LLM with moderate safety settings
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            safety_settings=SafetyPreset.moderate(),
            temperature=0.7
        )

        # Test with safe prompt
        prompt = "Write a short poem about programming."
        print(f"\nPrompt: {prompt}")

        response = llm.invoke(prompt)
        print(f"\nResponse:\n{response.content}")

        print("\n Success with moderate safety settings")

    except Exception as e:
        print(f"\n Error: {e}")


def example_with_strict_safety():
    """Example using strict safety preset (maximum filtering)."""
    print("\n" + "="*60)
    print("Example 2: Strict Safety Settings")
    print("="*60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        # Create LLM with strict safety settings
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            safety_settings=SafetyPreset.strict(),
            temperature=0.7
        )

        prompt = "Explain what makes a good children's educational app."
        print(f"\nPrompt: {prompt}")

        response = llm.invoke(prompt)
        print(f"\nResponse:\n{response.content}")

        print("\n Success with strict safety settings (ideal for children's content)")

    except Exception as e:
        print(f"\n Error: {e}")


def example_with_custom_safety():
    """Example using custom safety configuration."""
    print("\n" + "="*60)
    print("Example 3: Custom Safety Configuration")
    print("="*60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        # Create custom safety settings
        custom_settings = SafetyPreset.custom(
            harassment=SafetyThreshold.BLOCK_LOW_AND_ABOVE,
            hate_speech=SafetyThreshold.BLOCK_LOW_AND_ABOVE,
            sexually_explicit=SafetyThreshold.BLOCK_MEDIUM_AND_ABOVE,
            dangerous_content=SafetyThreshold.BLOCK_ONLY_HIGH
        )

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            safety_settings=custom_settings,
            temperature=0.7
        )

        prompt = "What are best practices for online community moderation?"
        print(f"\nPrompt: {prompt}")

        response = llm.invoke(prompt)
        print(f"\nResponse:\n{response.content}")

        print("\n Success with custom safety configuration")

    except Exception as e:
        print(f"\n Error: {e}")


def example_with_error_handling():
    """Example combining safety settings with error handling."""
    print("\n" + "="*60)
    print("Example 4: Safety Settings + Error Handling")
    print("="*60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            safety_settings=SafetyPreset.moderate(),
            temperature=0.7
        )

        # Use safe generation with error handling
        def generate():
            return llm.invoke("Explain the importance of cybersecurity.")

        response, error = GeminiErrorHandler.safe_generate(
            generate,
            fallback_response="I apologize, but I couldn't generate a response. Please try again."
        )

        if error:
            print(f"\n Error occurred: {error}")
            print(f"Fallback response: {response}")
        else:
            print(f"\nResponse:\n{response.content}")
            print("\n Success with error handling")

    except Exception as e:
        print(f"\n Unexpected error: {e}")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("LangChain Safety Settings Examples")
    print("="*60)
    print("\nThese examples demonstrate different safety configurations")
    print("for production use with Gemini models in LangChain.")

    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n Error: GOOGLE_API_KEY not found in environment variables")
        print("Please create a .env file with your API key:")
        print("  GOOGLE_API_KEY=your_api_key_here")
        return

    # Run examples
    example_with_moderate_safety()
    example_with_strict_safety()
    example_with_custom_safety()
    example_with_error_handling()

    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)
    print("\nKey Takeaways:")
    print("1. Moderate safety (default) works well for most applications")
    print("2. Strict safety is ideal for children's content and regulated industries")
    print("3. Custom safety allows fine-grained control per category")
    print("4. Combine safety settings with error handling for robustness")
    print("\nFor production use, always test safety settings with your specific use case.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

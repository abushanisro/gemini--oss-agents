#!/usr/bin/env python3
"""
LangChain Error Handling Example

This example demonstrates robust error handling patterns for production-grade
Gemini API usage with LangChain, including retry logic, circuit breakers,
and graceful fallbacks.

Prerequisites:
- pip install langchain-google-genai python-dotenv
- Set GOOGLE_API_KEY in .env file
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.error_handling import (
    GeminiErrorHandler,
    retry_on_rate_limit,
    retry_on_server_error
)

# Load environment variables
load_dotenv()


def example_basic_retry():
    """Example with basic retry logic."""
    print("\n" + "="*60)
    print("Example 1: Basic Retry with Exponential Backoff")
    print("="*60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.7
        )

        # Wrap generation with retry logic
        @GeminiErrorHandler.retry_with_exponential_backoff(
            max_retries=3,
            base_delay=1.0
        )
        def generate_with_retry(prompt: str):
            return llm.invoke(prompt)

        prompt = "Explain cloud computing in simple terms."
        print(f"\nPrompt: {prompt}")

        response = generate_with_retry(prompt)
        print(f"\nResponse:\n{response.content}")

        print("\n Success with retry logic")
        print("Note: If the API fails, it will automatically retry up to 3 times")

    except Exception as e:
        print(f"\n Error after all retries: {e}")


def example_safe_generation():
    """Example using safe generation with fallback."""
    print("\n" + "="*60)
    print("Example 2: Safe Generation with Fallback")
    print("="*60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.7
        )

        prompt = "What are the benefits of renewable energy?"
        print(f"\nPrompt: {prompt}")

        # Use safe_generate for graceful error handling
        response, error = GeminiErrorHandler.safe_generate(
            lambda: llm.invoke(prompt),
            fallback_response="I apologize, but I'm temporarily unable to respond. Please try again shortly."
        )

        if error:
            print(f"\n An error occurred: {error}")
            print(f"Using fallback response: {response}")
        else:
            print(f"\nResponse:\n{response.content}")
            print("\n Success")

    except Exception as e:
        print(f"\n Unexpected error: {e}")


def example_circuit_breaker():
    """Example using circuit breaker pattern."""
    print("\n" + "="*60)
    print("Example 3: Circuit Breaker Pattern")
    print("="*60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.7
        )

        # Create circuit breaker
        circuit_breaker = GeminiErrorHandler.create_circuit_breaker(
            failure_threshold=3,
            timeout=30.0
        )

        @circuit_breaker
        def generate_with_breaker(prompt: str):
            return llm.invoke(prompt)

        prompts = [
            "What is machine learning?",
            "Explain neural networks.",
            "What is deep learning?"
        ]

        print("\nGenerating multiple responses with circuit breaker protection...")

        for i, prompt in enumerate(prompts, 1):
            try:
                print(f"\n{i}. Prompt: {prompt}")
                response = generate_with_breaker(prompt)
                print(f"   Response: {response.content[:100]}...")
                print("    Success")
            except Exception as e:
                print(f"    Failed: {e}")

        print("\n Circuit breaker prevents cascading failures")
        print("Note: After 3 failures, circuit opens for 30 seconds")

    except Exception as e:
        print(f"\n Error: {e}")


def example_comprehensive_error_handling():
    """Example combining multiple error handling strategies."""
    print("\n" + "="*60)
    print("Example 4: Comprehensive Error Handling")
    print("="*60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.7,
            timeout=30,
            max_retries=2
        )

        # Combine retry + circuit breaker + safe generation
        circuit_breaker = GeminiErrorHandler.create_circuit_breaker(
            failure_threshold=5,
            timeout=60.0
        )

        @circuit_breaker
        @retry_on_server_error(max_retries=3)
        def robust_generate(prompt: str):
            return llm.invoke(prompt)

        prompt = "Describe the future of artificial intelligence."
        print(f"\nPrompt: {prompt}")

        response, error = GeminiErrorHandler.safe_generate(
            lambda: robust_generate(prompt),
            fallback_response="Unable to generate response at this time."
        )

        if error:
            print(f"\n Error: {error}")
            print(f"Fallback: {response}")
        else:
            print(f"\nResponse:\n{response.content}")
            print("\n Success with comprehensive error handling")

        print("\nError handling layers:")
        print("1. Built-in timeout (30s) and retries (2)")
        print("2. Custom retry with exponential backoff (3 attempts)")
        print("3. Circuit breaker (opens after 5 failures)")
        print("4. Safe generation with fallback")

    except Exception as e:
        print(f"\n Error: {e}")


def example_handling_safety_blocks():
    """Example handling content blocked by safety filters."""
    print("\n" + "="*60)
    print("Example 5: Handling Safety Blocks")
    print("="*60)

    try:
        import google.generativeai as genai

        # Configure API
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Test with potentially sensitive prompt (educational example)
        prompt = "Explain the historical significance of protest movements."
        print(f"\nPrompt: {prompt}")

        response = model.generate_content(prompt)

        # Check if blocked
        is_blocked, reason = GeminiErrorHandler.handle_safety_block(response)

        if is_blocked:
            print(f"\n Content was blocked: {reason}")
            print("Consider adjusting safety settings or rephrasing prompt.")
        else:
            print(f"\nResponse: {response.text[:200]}...")
            print("\n Content passed safety filters")

    except Exception as e:
        print(f"\n Error: {e}")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("LangChain Error Handling Examples")
    print("="*60)
    print("\nThese examples demonstrate production-grade error handling")
    print("for robust Gemini API usage.")

    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n Error: GOOGLE_API_KEY not found in environment variables")
        print("Please create a .env file with your API key:")
        print("  GOOGLE_API_KEY=your_api_key_here")
        return

    # Run examples
    example_basic_retry()
    example_safe_generation()
    example_circuit_breaker()
    example_comprehensive_error_handling()
    example_handling_safety_blocks()

    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)
    print("\nKey Takeaways:")
    print("1. Always implement retry logic for transient failures")
    print("2. Use circuit breakers to prevent cascading failures")
    print("3. Provide fallback responses for better user experience")
    print("4. Combine multiple error handling strategies for robustness")
    print("5. Handle safety blocks gracefully with helpful messages")
    print("\nFor production, combine these patterns based on your needs.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

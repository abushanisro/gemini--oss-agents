#!/usr/bin/env python3
"""
LangChain Cost Tracking Example

This example demonstrates how to track token usage and estimate costs
when using Gemini models with LangChain. Essential for production deployments
where cost management is critical.

Prerequisites:
- pip install langchain-google-genai python-dotenv
- Set GOOGLE_API_KEY in .env file
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.cost_tracker import CostTracker, estimate_tokens, recommend_model

# Load environment variables
load_dotenv()


def example_basic_cost_tracking():
    """Example of basic cost tracking."""
    print("\n" + "="*60)
    print("Example 1: Basic Cost Tracking")
    print("="*60)

    try:
        import google.generativeai as genai

        # Configure API
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)

        # Create cost tracker
        tracker = CostTracker()

        # Create model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Make multiple API calls
        prompts = [
            "Explain quantum computing.",
            "What is blockchain technology?",
            "Describe machine learning algorithms."
        ]

        print("\nGenerating responses and tracking costs...\n")

        for i, prompt in enumerate(prompts, 1):
            print(f"{i}. Prompt: {prompt}")

            response = model.generate_content(prompt)

            # Track usage
            usage = tracker.add_from_response(response, model="gemini-2.0-flash-exp")

            if usage:
                print(f"   Tokens: {usage.total_tokens} "
                      f"(Input: {usage.prompt_tokens}, Output: {usage.completion_tokens})")
                print(f"   Est. Cost: ${usage.cost_estimate:.6f}")
            else:
                print("   (Could not extract usage data)")

            print(f"   Response: {response.text[:80]}...")
            print()

        # Print summary
        tracker.print_summary()

    except Exception as e:
        print(f"\n✗ Error: {e}")


def example_cost_comparison():
    """Compare costs across different models."""
    print("\n" + "="*60)
    print("Example 2: Cost Comparison Across Models")
    print("="*60)

    try:
        import google.generativeai as genai

        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)

        # Test prompt
        prompt = "Write a comprehensive article about renewable energy (500 words)."

        models = [
            "gemini-2.0-flash-exp",
            "gemini-1.5-flash",
            "gemini-1.5-pro"
        ]

        print(f"\nPrompt: {prompt}\n")
        print("Comparing costs across models...\n")

        for model_name in models:
            try:
                tracker = CostTracker()
                model = genai.GenerativeModel(model_name)

                response = model.generate_content(prompt)
                usage = tracker.add_from_response(response, model=model_name)

                if usage:
                    print(f"{model_name}:")
                    print(f"  Tokens: {usage.total_tokens}")
                    print(f"  Cost: ${usage.cost_estimate:.6f}")
                    print()
                else:
                    print(f"{model_name}: Could not extract usage\n")

            except Exception as e:
                print(f"{model_name}: Error - {e}\n")

        print("💡 Tip: Use Flash models for cost-effective general tasks")
        print("         Use Pro models for complex reasoning tasks")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def example_cost_estimation():
    """Estimate costs before making API calls."""
    print("\n" + "="*60)
    print("Example 3: Pre-Call Cost Estimation")
    print("="*60)

    try:
        # Long prompt example
        prompt = """
        Analyze the following business scenario and provide recommendations:

        A mid-sized company is considering digital transformation. They currently
        use legacy systems for inventory management, customer relations, and
        accounting. Their IT budget is limited, and they need to prioritize
        investments. What steps should they take?

        Consider:
        1. Cost-benefit analysis
        2. Risk assessment
        3. Implementation timeline
        4. Training requirements
        5. Expected ROI

        Provide a detailed strategic plan.
        """

        # Estimate tokens
        estimated_input_tokens = estimate_tokens(prompt)
        estimated_output_tokens = 1000  # Assuming comprehensive response

        print(f"\nPrompt length: {len(prompt)} characters")
        print(f"Estimated input tokens: ~{estimated_input_tokens}")
        print(f"Estimated output tokens: ~{estimated_output_tokens}")

        # Recommend model
        recommended = recommend_model(
            prompt_length=estimated_input_tokens,
            quality_priority=False,
            cost_priority=True
        )

        print(f"\nRecommended model: {recommended}")

        # Estimate cost for different models
        from src.cost_tracker import TokenUsage

        print("\nEstimated costs:")

        models_to_test = [
            ("gemini-2.0-flash-exp", "Flash (fastest, cheapest)"),
            ("gemini-1.5-pro", "Pro (best quality)")
        ]

        for model_name, description in models_to_test:
            usage = TokenUsage(
                prompt_tokens=estimated_input_tokens,
                completion_tokens=estimated_output_tokens,
                total_tokens=estimated_input_tokens + estimated_output_tokens,
                model=model_name
            )
            print(f"  {description}: ${usage.cost_estimate:.6f}")

        print("\n💡 Use this technique to estimate costs before expensive operations")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def example_batch_processing_with_tracking():
    """Example of batch processing with comprehensive cost tracking."""
    print("\n" + "="*60)
    print("Example 4: Batch Processing with Cost Tracking")
    print("="*60)

    try:
        import google.generativeai as genai

        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)

        # Create tracker
        tracker = CostTracker()

        # Batch of prompts to process
        prompts = [
            "Summarize: Cloud computing enables on-demand access to computing resources.",
            "Summarize: AI is transforming industries through automation and insights.",
            "Summarize: Cybersecurity is critical for protecting digital assets.",
            "Summarize: DevOps combines development and operations for faster delivery.",
            "Summarize: Data science extracts insights from large datasets."
        ]

        print(f"\nProcessing batch of {len(prompts)} prompts...\n")

        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        for i, prompt in enumerate(prompts, 1):
            response = model.generate_content(prompt)
            tracker.add_from_response(response, model="gemini-2.0-flash-exp")
            print(f"{i}. ✓ Processed: {prompt[:50]}...")

        print("\n" + "-"*60)
        tracker.print_summary()

        # Export to JSON
        output_file = "/tmp/gemini_usage_report.json"
        tracker.export_to_json(output_file)
        print(f"📊 Detailed report exported to: {output_file}")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def example_cost_optimization():
    """Example demonstrating cost optimization strategies."""
    print("\n" + "="*60)
    print("Example 5: Cost Optimization Strategies")
    print("="*60)

    print("\n💡 Cost Optimization Tips:\n")

    print("1. Choose the Right Model:")
    print("   - Use Flash models for simple tasks (5x cheaper)")
    print("   - Use Pro models only for complex reasoning")
    print("   - Test both to find the quality/cost balance")

    print("\n2. Optimize Prompts:")
    print("   - Be concise and specific")
    print("   - Avoid unnecessary context")
    print("   - Use examples sparingly")

    print("\n3. Control Output Length:")
    print("   - Set max_output_tokens to limit response length")
    print("   - Request summaries instead of full explanations when possible")

    print("\n4. Batch Processing:")
    print("   - Process multiple items in one request when possible")
    print("   - Use structured outputs to pack more info per token")

    print("\n5. Caching Strategies:")
    print("   - Cache frequent responses at application level")
    print("   - Implement context caching when available")
    print("   - Avoid regenerating identical content")

    print("\n6. Monitor and Analyze:")
    print("   - Track costs per feature/user")
    print("   - Set up alerts for unusual spending")
    print("   - Regular review of usage patterns")

    # Practical example
    try:
        import google.generativeai as genai

        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)

        tracker_verbose = CostTracker()
        tracker_concise = CostTracker()

        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Verbose prompt
        verbose_prompt = """
        I would like you to please explain to me, in great detail, with lots of
        examples and context, what machine learning is, including its history,
        various types, applications, and future prospects. Please be very thorough.
        """

        # Concise prompt (same intent)
        concise_prompt = "Explain machine learning: definition, types, and applications."

        print("\n\nComparing verbose vs. concise prompts:\n")

        # Verbose
        response1 = model.generate_content(verbose_prompt)
        tracker_verbose.add_from_response(response1, "gemini-2.0-flash-exp")
        print(f"Verbose prompt:")
        print(f"  Input length: {len(verbose_prompt)} chars")
        print(f"  Cost: ${tracker_verbose.total_cost:.6f}")

        # Concise
        response2 = model.generate_content(concise_prompt)
        tracker_concise.add_from_response(response2, "gemini-2.0-flash-exp")
        print(f"\nConcise prompt:")
        print(f"  Input length: {len(concise_prompt)} chars")
        print(f"  Cost: ${tracker_concise.total_cost:.6f}")

        savings = tracker_verbose.total_cost - tracker_concise.total_cost
        if savings > 0:
            savings_percent = (savings / tracker_verbose.total_cost) * 100
            print(f"\n💰 Savings: ${savings:.6f} ({savings_percent:.1f}%)")

    except Exception as e:
        print(f"\n⚠ Could not run practical example: {e}")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("LangChain Cost Tracking Examples")
    print("="*60)
    print("\nThese examples demonstrate cost tracking and optimization")
    print("for production Gemini API usage.")

    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n✗ Error: GOOGLE_API_KEY not found in environment variables")
        print("Please create a .env file with your API key:")
        print("  GOOGLE_API_KEY=your_api_key_here")
        return

    # Run examples
    example_basic_cost_tracking()
    example_cost_comparison()
    example_cost_estimation()
    example_batch_processing_with_tracking()
    example_cost_optimization()

    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)
    print("\nKey Takeaways:")
    print("1. Always track token usage and costs in production")
    print("2. Choose models based on task complexity and budget")
    print("3. Optimize prompts to reduce unnecessary tokens")
    print("4. Estimate costs before expensive operations")
    print("5. Monitor and analyze usage patterns regularly")
    print("\nCost management is essential for sustainable AI applications!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

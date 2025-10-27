"""
Cost Tracking and Estimation for Gemini API Usage

This module provides utilities for tracking token usage, estimating costs,
and optimizing API usage across different Gemini models.

Pricing (as of 2025 - verify current pricing at ai.google.dev):
- Gemini 2.5 Flash: Lower cost, faster
- Gemini 2.5 Pro: Higher cost, better quality
- Free tier available with quota limits
"""

import logging
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    """Tracks token usage for a single request."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def cost_estimate(self) -> float:
        """
        Estimate cost based on token usage and model.
        NOTE: Update these rates based on current Gemini pricing.
        """
        # Example pricing (verify current rates)
        pricing = {
            "gemini-2.5-flash": {
                "input": 0.00001875,  # per 1K tokens
                "output": 0.000075    # per 1K tokens
            },
            "gemini-2.5-pro": {
                "input": 0.000125,    # per 1K tokens
                "output": 0.000625    # per 1K tokens
            },
            "gemini-2.0-flash": {
                "input": 0.00001875,
                "output": 0.000075
            },
            "gemini-pro": {
                "input": 0.0005,      # per 1K tokens
                "output": 0.0015      # per 1K tokens
            }
        }

        # Find matching model (handle version variations)
        model_key = None
        for key in pricing.keys():
            if key in self.model.lower():
                model_key = key
                break

        if not model_key:
            logger.warning(f"Unknown model {self.model}, using Gemini Pro pricing")
            model_key = "gemini-pro"

        rates = pricing[model_key]
        input_cost = (self.prompt_tokens / 1000) * rates["input"]
        output_cost = (self.completion_tokens / 1000) * rates["output"]

        return input_cost + output_cost


class CostTracker:
    """Tracks cumulative API costs across multiple requests."""

    def __init__(self):
        self.usage_history: List[TokenUsage] = []
        self._total_prompt_tokens = 0
        self._total_completion_tokens = 0
        self._total_cost = 0.0

    def add_usage(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str
    ) -> TokenUsage:
        """
        Add a usage record and return the usage object.

        Args:
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            model: Model name used

        Returns:
            TokenUsage object
        """
        usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            model=model
        )

        self.usage_history.append(usage)
        self._total_prompt_tokens += prompt_tokens
        self._total_completion_tokens += completion_tokens
        self._total_cost += usage.cost_estimate

        return usage

    def add_from_response(self, response: any, model: str) -> Optional[TokenUsage]:
        """
        Extract token usage from API response and add to tracker.

        Args:
            response: Response object from Gemini API
            model: Model name used

        Returns:
            TokenUsage object if successful, None otherwise
        """
        try:
            # Try to extract usage metadata
            if hasattr(response, 'usage_metadata'):
                metadata = response.usage_metadata
                return self.add_usage(
                    prompt_tokens=metadata.prompt_token_count,
                    completion_tokens=metadata.candidates_token_count,
                    model=model
                )
            else:
                logger.warning("Response does not contain usage_metadata")
                return None

        except Exception as e:
            logger.error(f"Could not extract token usage: {e}")
            return None

    @property
    def total_tokens(self) -> int:
        """Total tokens used across all requests."""
        return self._total_prompt_tokens + self._total_completion_tokens

    @property
    def total_cost(self) -> float:
        """Total estimated cost across all requests."""
        return self._total_cost

    @property
    def request_count(self) -> int:
        """Total number of requests tracked."""
        return len(self.usage_history)

    def get_summary(self) -> Dict:
        """
        Get a summary of usage and costs.

        Returns:
            Dictionary with usage statistics
        """
        return {
            "total_requests": self.request_count,
            "total_tokens": self.total_tokens,
            "prompt_tokens": self._total_prompt_tokens,
            "completion_tokens": self._total_completion_tokens,
            "estimated_cost_usd": round(self._total_cost, 4),
            "average_tokens_per_request": (
                round(self.total_tokens / self.request_count, 2)
                if self.request_count > 0 else 0
            ),
            "average_cost_per_request": (
                round(self._total_cost / self.request_count, 4)
                if self.request_count > 0 else 0
            )
        }

    def get_cost_by_model(self) -> Dict[str, float]:
        """
        Get cost breakdown by model.

        Returns:
            Dictionary mapping model names to costs
        """
        model_costs = {}
        for usage in self.usage_history:
            model = usage.model
            cost = usage.cost_estimate
            model_costs[model] = model_costs.get(model, 0.0) + cost

        return {k: round(v, 4) for k, v in model_costs.items()}

    def print_summary(self):
        """Print a formatted summary of usage and costs."""
        summary = self.get_summary()
        model_costs = self.get_cost_by_model()

        print("\n" + "="*60)
        print("GEMINI API USAGE SUMMARY")
        print("="*60)
        print(f"Total Requests:              {summary['total_requests']}")
        print(f"Total Tokens:                {summary['total_tokens']:,}")
        print(f"  - Prompt Tokens:           {summary['prompt_tokens']:,}")
        print(f"  - Completion Tokens:       {summary['completion_tokens']:,}")
        print(f"Estimated Cost:              ${summary['estimated_cost_usd']:.4f}")
        print(f"Avg Tokens/Request:          {summary['average_tokens_per_request']:.2f}")
        print(f"Avg Cost/Request:            ${summary['average_cost_per_request']:.4f}")

        if model_costs:
            print("\nCost by Model:")
            for model, cost in model_costs.items():
                print(f"  - {model}: ${cost:.4f}")

        print("="*60 + "\n")

    def export_to_json(self, filepath: str):
        """
        Export usage history to JSON file.

        Args:
            filepath: Path to output JSON file
        """
        data = {
            "summary": self.get_summary(),
            "model_costs": self.get_cost_by_model(),
            "usage_history": [
                {
                    "timestamp": usage.timestamp.isoformat(),
                    "model": usage.model,
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens,
                    "cost_estimate": usage.cost_estimate
                }
                for usage in self.usage_history
            ]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Usage history exported to {filepath}")

    def reset(self):
        """Reset all tracking data."""
        self.usage_history.clear()
        self._total_prompt_tokens = 0
        self._total_completion_tokens = 0
        self._total_cost = 0.0


def estimate_tokens(text: str) -> int:
    """
    Rough estimation of token count for text.
    Note: This is approximate. For accurate counts, use the API's token counting.

    Rule of thumb: ~4 characters = 1 token for English text.

    Args:
        text: Input text

    Returns:
        Estimated token count
    """
    return len(text) // 4


def recommend_model(
    prompt_length: int,
    quality_priority: bool = False,
    cost_priority: bool = False
) -> str:
    """
    Recommend appropriate model based on requirements.

    Args:
        prompt_length: Estimated prompt length in tokens
        quality_priority: Prioritize quality over cost
        cost_priority: Prioritize cost over quality

    Returns:
        Recommended model name
    """
    if cost_priority:
        return "gemini-2.5-flash"

    if quality_priority:
        return "gemini-2.5-pro"

    # Default: balance based on prompt length
    if prompt_length < 1000:
        return "gemini-2.5-flash"  # Fast and cheap for short prompts
    else:
        return "gemini-2.5-pro"    # Better quality for complex prompts


# Global tracker instance (optional)
global_tracker = CostTracker()


# Example usage documentation
__doc_examples__ = """
Example Usage:

1. Basic cost tracking:
    ```python
    from src.cost_tracker import CostTracker

    tracker = CostTracker()

    # After each API call
    response = model.generate_content("Hello")
    tracker.add_from_response(response, model="gemini-2.5-pro")

    # View summary
    tracker.print_summary()
    ```

2. Manual token tracking:
    ```python
    tracker.add_usage(
        prompt_tokens=100,
        completion_tokens=50,
        model="gemini-2.5-flash"
    )
    ```

3. Cost estimation before API call:
    ```python
    from src.cost_tracker import estimate_tokens, recommend_model

    prompt = "Write a long essay about AI..."
    estimated_tokens = estimate_tokens(prompt)

    model = recommend_model(
        prompt_length=estimated_tokens,
        cost_priority=True
    )
    print(f"Recommended model: {model}")
    ```

4. Export tracking data:
    ```python
    tracker.export_to_json("usage_report.json")
    ```

5. Using global tracker:
    ```python
    from src.cost_tracker import global_tracker

    # Track throughout your application
    global_tracker.add_usage(100, 50, "gemini-pro")

    # Print summary at the end
    global_tracker.print_summary()
    ```
"""

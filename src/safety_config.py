"""
Safety Settings Configuration for Gemini Models

This module provides utilities for configuring safety settings across different
agent frameworks using Gemini models. Safety settings help control the model's
responses to potentially harmful or sensitive content.

Safety Categories:
- HARM_CATEGORY_HARASSMENT
- HARM_CATEGORY_HATE_SPEECH
- HARM_CATEGORY_SEXUALLY_EXPLICIT
- HARM_CATEGORY_DANGEROUS_CONTENT

Thresholds:
- BLOCK_NONE: No blocking
- BLOCK_ONLY_HIGH: Block only high probability violations
- BLOCK_MEDIUM_AND_ABOVE: Block medium and high probability violations
- BLOCK_LOW_AND_ABOVE: Block low, medium, and high probability violations
"""

from typing import Dict, List, Optional
from enum import Enum


class SafetyThreshold(Enum):
    """Safety threshold levels for content blocking."""
    BLOCK_NONE = "BLOCK_NONE"
    BLOCK_ONLY_HIGH = "BLOCK_ONLY_HIGH"
    BLOCK_MEDIUM_AND_ABOVE = "BLOCK_MEDIUM_AND_ABOVE"
    BLOCK_LOW_AND_ABOVE = "BLOCK_LOW_AND_ABOVE"


class SafetyCategory(Enum):
    """Safety categories for content filtering."""
    HARASSMENT = "HARM_CATEGORY_HARASSMENT"
    HATE_SPEECH = "HARM_CATEGORY_HATE_SPEECH"
    SEXUALLY_EXPLICIT = "HARM_CATEGORY_SEXUALLY_EXPLICIT"
    DANGEROUS_CONTENT = "HARM_CATEGORY_DANGEROUS_CONTENT"


class SafetyPreset:
    """Pre-configured safety setting presets for common use cases."""

    @staticmethod
    def permissive() -> List[Dict[str, str]]:
        """
        Permissive preset - minimal content filtering.
        Use for: Creative writing, general content generation.
        Warning: May generate content that requires human review.
        """
        return [
            {
                "category": category.value,
                "threshold": SafetyThreshold.BLOCK_ONLY_HIGH.value
            }
            for category in SafetyCategory
        ]

    @staticmethod
    def moderate() -> List[Dict[str, str]]:
        """
        Moderate preset - balanced content filtering.
        Use for: General applications, chatbots, customer service.
        Recommended for most production use cases.
        """
        return [
            {
                "category": category.value,
                "threshold": SafetyThreshold.BLOCK_MEDIUM_AND_ABOVE.value
            }
            for category in SafetyCategory
        ]

    @staticmethod
    def strict() -> List[Dict[str, str]]:
        """
        Strict preset - maximum content filtering.
        Use for: Children's apps, educational content, regulated industries.
        Minimizes risk but may over-block legitimate content.
        """
        return [
            {
                "category": category.value,
                "threshold": SafetyThreshold.BLOCK_LOW_AND_ABOVE.value
            }
            for category in SafetyCategory
        ]

    @staticmethod
    def custom(
        harassment: SafetyThreshold = SafetyThreshold.BLOCK_MEDIUM_AND_ABOVE,
        hate_speech: SafetyThreshold = SafetyThreshold.BLOCK_MEDIUM_AND_ABOVE,
        sexually_explicit: SafetyThreshold = SafetyThreshold.BLOCK_MEDIUM_AND_ABOVE,
        dangerous_content: SafetyThreshold = SafetyThreshold.BLOCK_MEDIUM_AND_ABOVE
    ) -> List[Dict[str, str]]:
        """
        Custom preset - specify threshold for each category.

        Args:
            harassment: Threshold for harassment content
            hate_speech: Threshold for hate speech
            sexually_explicit: Threshold for sexually explicit content
            dangerous_content: Threshold for dangerous content

        Returns:
            List of safety settings configurations
        """
        return [
            {
                "category": SafetyCategory.HARASSMENT.value,
                "threshold": harassment.value
            },
            {
                "category": SafetyCategory.HATE_SPEECH.value,
                "threshold": hate_speech.value
            },
            {
                "category": SafetyCategory.SEXUALLY_EXPLICIT.value,
                "threshold": sexually_explicit.value
            },
            {
                "category": SafetyCategory.DANGEROUS_CONTENT.value,
                "threshold": dangerous_content.value
            }
        ]


def get_safety_settings_for_langchain() -> Dict:
    """
    Get safety settings formatted for LangChain's ChatGoogleGenerativeAI.

    Returns:
        Dictionary with safety_settings key for LangChain
    """
    return {
        "safety_settings": SafetyPreset.moderate()
    }


def get_safety_settings_for_genai() -> List[Dict[str, str]]:
    """
    Get safety settings formatted for google.generativeai library.

    Returns:
        List of safety setting dictionaries
    """
    return SafetyPreset.moderate()


def explain_safety_rating(safety_ratings: List[Dict]) -> str:
    """
    Generate human-readable explanation of safety ratings from response.

    Args:
        safety_ratings: List of safety rating dictionaries from response

    Returns:
        Human-readable explanation string
    """
    if not safety_ratings:
        return "No safety ratings available."

    explanations = []
    for rating in safety_ratings:
        category = rating.get("category", "UNKNOWN")
        probability = rating.get("probability", "UNKNOWN")
        explanations.append(f"  - {category}: {probability}")

    return "Safety Ratings:\n" + "\n".join(explanations)


# Example usage documentation
__doc_examples__ = """
Example Usage:

1. Using presets with LangChain:
    ```python
    from langchain_google_genai import ChatGoogleGenerativeAI
    from src.safety_config import SafetyPreset

    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        safety_settings=SafetyPreset.moderate()
    )
    ```

2. Using presets with google.generativeai:
    ```python
    import google.generativeai as genai
    from src.safety_config import SafetyPreset

    model = genai.GenerativeModel(
        'gemini-pro',
        safety_settings=SafetyPreset.strict()
    )
    ```

3. Custom safety configuration:
    ```python
    from src.safety_config import SafetyPreset, SafetyThreshold

    custom_settings = SafetyPreset.custom(
        harassment=SafetyThreshold.BLOCK_LOW_AND_ABOVE,
        hate_speech=SafetyThreshold.BLOCK_LOW_AND_ABOVE,
        sexually_explicit=SafetyThreshold.BLOCK_MEDIUM_AND_ABOVE,
        dangerous_content=SafetyThreshold.BLOCK_ONLY_HIGH
    )
    ```
"""

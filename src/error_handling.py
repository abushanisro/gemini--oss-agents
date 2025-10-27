"""
Error Handling Utilities for Gemini API Integration

This module provides robust error handling patterns, retry logic, and fallback
mechanisms for production-grade Gemini API usage across different frameworks.

Common Errors:
- Rate limit exceeded (429)
- API quota exceeded (429)
- Invalid API key (401)
- Model not found (404)
- Server errors (500, 503)
- Network timeouts
- Safety filter blocks
"""

import time
import logging
from typing import Callable, Any, Optional, Type, Tuple
from functools import wraps
import random

logger = logging.getLogger(__name__)


class GeminiErrorHandler:
    """Handles common Gemini API errors with retry logic and fallbacks."""

    # Common error messages and their meanings
    ERROR_MESSAGES = {
        "429": "Rate limit exceeded. Try reducing request frequency or upgrading quota.",
        "401": "Invalid API key. Check GOOGLE_API_KEY environment variable.",
        "403": "Permission denied. Verify API key has correct permissions.",
        "404": "Model not found. Check model name spelling.",
        "500": "Internal server error. Retry after short delay.",
        "503": "Service unavailable. Gemini API may be experiencing issues.",
        "timeout": "Request timed out. Check network connection or increase timeout.",
        "blocked": "Content blocked by safety filters. Review safety settings."
    }

    @staticmethod
    def retry_with_exponential_backoff(
        func: Callable,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ) -> Callable:
        """
        Decorator for retrying function calls with exponential backoff.

        Args:
            func: Function to wrap
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential calculation
            jitter: Add random jitter to prevent thundering herd

        Returns:
            Wrapped function with retry logic
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    last_exception = e
                    error_msg = str(e).lower()

                    # Don't retry on certain errors
                    if any(x in error_msg for x in ['invalid api key', '401', '403', '404']):
                        logger.error(f"Non-retryable error: {e}")
                        raise

                    if attempt < max_retries:
                        # Calculate delay with exponential backoff
                        delay = min(base_delay * (exponential_base ** attempt), max_delay)

                        # Add jitter to prevent thundering herd
                        if jitter:
                            delay = delay * (0.5 + random.random())

                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                            f"Retrying in {delay:.2f} seconds..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed. Last error: {e}")

            raise last_exception

        return wrapper

    @staticmethod
    def safe_generate(
        generate_func: Callable,
        fallback_response: Optional[str] = None,
        log_errors: bool = True
    ) -> Tuple[Optional[str], Optional[Exception]]:
        """
        Safely execute generation function with error capture.

        Args:
            generate_func: Function that generates content
            fallback_response: Response to return if generation fails
            log_errors: Whether to log errors

        Returns:
            Tuple of (response, error). One will always be None.
        """
        try:
            response = generate_func()
            return response, None

        except Exception as e:
            if log_errors:
                logger.error(f"Generation failed: {e}")

            if fallback_response:
                return fallback_response, e

            return None, e

    @staticmethod
    def handle_safety_block(response: Any) -> Tuple[bool, Optional[str]]:
        """
        Check if response was blocked by safety filters.

        Args:
            response: Response object from Gemini API

        Returns:
            Tuple of (is_blocked, reason)
        """
        try:
            # Check for prompt_feedback (request blocked)
            if hasattr(response, 'prompt_feedback'):
                feedback = response.prompt_feedback
                if hasattr(feedback, 'block_reason'):
                    return True, f"Blocked: {feedback.block_reason}"

            # Check for finish_reason (response blocked)
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason'):
                    if candidate.finish_reason in ['SAFETY', 'BLOCKED']:
                        safety_ratings = getattr(candidate, 'safety_ratings', [])
                        return True, f"Content blocked. Safety ratings: {safety_ratings}"

            return False, None

        except Exception as e:
            logger.warning(f"Could not check safety block status: {e}")
            return False, None

    @staticmethod
    def create_circuit_breaker(
        failure_threshold: int = 5,
        timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        """
        Create a circuit breaker to prevent cascading failures.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before attempting to close circuit
            expected_exception: Exception type to catch

        Returns:
            Circuit breaker decorator
        """
        class CircuitBreaker:
            def __init__(self):
                self.failure_count = 0
                self.last_failure_time = None
                self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

            def call(self, func):
                @wraps(func)
                def wrapper(*args, **kwargs):
                    if self.state == "OPEN":
                        if time.time() - self.last_failure_time > timeout:
                            self.state = "HALF_OPEN"
                            logger.info("Circuit breaker entering HALF_OPEN state")
                        else:
                            raise Exception(
                                f"Circuit breaker OPEN. Too many failures. "
                                f"Retry after {timeout} seconds."
                            )

                    try:
                        result = func(*args, **kwargs)

                        # Success - reset failure count
                        if self.state == "HALF_OPEN":
                            self.state = "CLOSED"
                            logger.info("Circuit breaker CLOSED")
                        self.failure_count = 0

                        return result

                    except expected_exception as e:
                        self.failure_count += 1
                        self.last_failure_time = time.time()

                        logger.warning(
                            f"Circuit breaker failure {self.failure_count}/{failure_threshold}"
                        )

                        if self.failure_count >= failure_threshold:
                            self.state = "OPEN"
                            logger.error(
                                f"Circuit breaker OPEN after {failure_threshold} failures"
                            )

                        raise

                return wrapper

        breaker = CircuitBreaker()
        return breaker.call


# Convenience decorators for common use cases
def retry_on_rate_limit(max_retries: int = 5):
    """Decorator specifically for handling rate limit errors."""
    return GeminiErrorHandler.retry_with_exponential_backoff(
        max_retries=max_retries,
        base_delay=2.0,
        max_delay=120.0
    )


def retry_on_server_error(max_retries: int = 3):
    """Decorator specifically for handling server errors."""
    return GeminiErrorHandler.retry_with_exponential_backoff(
        max_retries=max_retries,
        base_delay=1.0,
        max_delay=30.0
    )


# Example usage documentation
__doc_examples__ = """
Example Usage:

1. Basic retry with exponential backoff:
    ```python
    from src.error_handling import retry_with_exponential_backoff

    @retry_with_exponential_backoff(max_retries=3)
    def generate_content(model, prompt):
        return model.generate_content(prompt)
    ```

2. Safe generation with fallback:
    ```python
    from src.error_handling import GeminiErrorHandler

    response, error = GeminiErrorHandler.safe_generate(
        lambda: model.generate_content("Tell me a joke"),
        fallback_response="I'm sorry, I couldn't generate a response."
    )

    if error:
        print(f"Error occurred: {error}")
    else:
        print(response)
    ```

3. Circuit breaker for preventing cascading failures:
    ```python
    from src.error_handling import GeminiErrorHandler

    circuit_breaker = GeminiErrorHandler.create_circuit_breaker(
        failure_threshold=5,
        timeout=60.0
    )

    @circuit_breaker
    def call_gemini_api():
        return model.generate_content("Hello")
    ```

4. Check for safety blocks:
    ```python
    from src.error_handling import GeminiErrorHandler

    response = model.generate_content(prompt)
    is_blocked, reason = GeminiErrorHandler.handle_safety_block(response)

    if is_blocked:
        print(f"Content was blocked: {reason}")
    ```
"""

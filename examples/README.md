# Gemini API Integration Examples

This directory contains practical, production-ready examples demonstrating best practices for using Gemini models with various agent frameworks.

## Directory Structure

```
examples/
├── 01_basic/              # Fundamental patterns and utilities
├── 02_intermediate/       # Multi-step workflows and advanced features
└── 03_advanced/          # Complex production scenarios
```

## Getting Started

### Prerequisites

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API key**:
   ```bash
   cp .env.example .env
   # Edit .env and add your GOOGLE_API_KEY
   ```

3. **Run examples**:
   ```bash
   python examples/01_basic/langchain_with_safety_settings.py
   ```

## Basic Examples (01_basic/)

### Safety Settings
**File**: `langchain_with_safety_settings.py`

Demonstrates how to configure safety settings for production deployments:
- Moderate preset (recommended for most use cases)
- Strict preset (for children's content, regulated industries)
- Custom configuration (fine-grained control)
- Combined with error handling

**Key Learning**: Always configure safety settings appropriate to your use case.

### Error Handling
**File**: `langchain_error_handling.py`

Production-grade error handling patterns:
- Retry with exponential backoff
- Circuit breaker pattern
- Safe generation with fallbacks
- Handling safety blocks
- Comprehensive error strategies

**Key Learning**: Robust error handling is essential for production reliability.

### Cost Tracking
**File**: `langchain_cost_tracking.py`

Monitor and optimize API costs:
- Basic cost tracking
- Model cost comparison
- Pre-call cost estimation
- Batch processing tracking
- Cost optimization strategies

**Key Learning**: Cost management prevents unexpected bills and enables budget planning.

## Utility Modules (src/)

### safety_config.py
Reusable safety configuration utilities:
- Pre-configured safety presets
- Custom safety builders
- Framework-specific helpers

### error_handling.py
Production error handling utilities:
- Retry decorators
- Circuit breakers
- Safe generation wrappers
- Safety block detection

### cost_tracker.py
Cost tracking and estimation:
- Token usage tracking
- Cost estimation
- Usage summaries
- Export functionality

## Example Patterns

### Pattern 1: Safety + Error Handling + Cost Tracking

```python
from src.safety_config import SafetyPreset
from src.error_handling import retry_on_server_error
from src.cost_tracker import CostTracker

tracker = CostTracker()

@retry_on_server_error(max_retries=3)
def generate(prompt):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        safety_settings=SafetyPreset.moderate()
    )
    response = llm.invoke(prompt)
    tracker.add_from_response(response, "gemini-2.0-flash-exp")
    return response

# Use it
response = generate("Your prompt here")
tracker.print_summary()
```

### Pattern 2: Production-Ready Generation

```python
from src.safety_config import SafetyPreset
from src.error_handling import GeminiErrorHandler

circuit_breaker = GeminiErrorHandler.create_circuit_breaker(
    failure_threshold=5,
    timeout=60.0
)

@circuit_breaker
def production_generate(prompt):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        safety_settings=SafetyPreset.strict(),
        timeout=30,
        max_retries=2
    )

    response, error = GeminiErrorHandler.safe_generate(
        lambda: llm.invoke(prompt),
        fallback_response="Service temporarily unavailable."
    )

    if error:
        # Log error, alert monitoring system
        logger.error(f"Generation failed: {error}")

    return response
```

## Best Practices

### 1. Safety Configuration
- **Always** configure safety settings explicitly
- Use `strict` for children's content or regulated industries
- Use `moderate` for general applications (default recommendation)
- Test safety settings with your specific content

### 2. Error Handling
- Implement retry logic for transient failures
- Use circuit breakers for cascading failure prevention
- Provide fallback responses for better UX
- Handle safety blocks gracefully

### 3. Cost Management
- Track costs from day one
- Set up monitoring and alerts
- Choose models based on task complexity
- Optimize prompts to reduce token usage

### 4. Model Selection
- **Flash models**: Fast, cost-effective for simple tasks
- **Pro models**: Better quality for complex reasoning
- Test both to find quality/cost balance

### 5. Production Checklist
- [ ] Safety settings configured
- [ ] Error handling implemented
- [ ] Cost tracking enabled
- [ ] Monitoring/logging set up
- [ ] Rate limits understood
- [ ] Fallbacks defined
- [ ] Testing completed

## Common Issues

### Issue: Rate Limit Exceeded
**Solution**: Implement exponential backoff retry logic
```python
@retry_on_rate_limit(max_retries=5)
def generate(prompt):
    return llm.invoke(prompt)
```

### Issue: Unexpected Costs
**Solution**: Track costs and set limits
```python
from src.cost_tracker import CostTracker

tracker = CostTracker()
# ... after each call ...
if tracker.total_cost > BUDGET_LIMIT:
    alert_admin()
```

### Issue: Content Blocked by Safety Filters
**Solution**: Check safety ratings and adjust settings
```python
is_blocked, reason = GeminiErrorHandler.handle_safety_block(response)
if is_blocked:
    # Adjust safety settings or rephrase prompt
```

## Framework-Specific Examples

### LangChain
All basic examples use LangChain. Advanced examples in `02_intermediate/` include:
- RAG pipelines with cost tracking
- Chains with error handling
- Agents with safety configuration

### LlamaIndex
Coming soon in `02_intermediate/`:
- Multimodal RAG examples
- Query engines with error handling
- Agent workflows with cost tracking

### CrewAI
Coming soon in `02_intermediate/`:
- Multi-agent systems with safety
- Crew coordination with error handling
- Tool integration examples

### Composio
Coming soon in `02_intermediate/`:
- Tool catalog integration
- Authentication examples
- Multi-tool workflows

## Contributing

When adding new examples:

1. **Follow the pattern**:
   - Clear docstrings
   - Error handling
   - Cost tracking where applicable
   - Executable as standalone script

2. **Include prerequisites** in docstring

3. **Add to this README** with description

4. **Test thoroughly** before committing

## Resources

- [Gemini API Documentation](https://ai.google.dev/docs)
- [LangChain Gemini Guide](https://python.langchain.com/docs/integrations/chat/google_generative_ai/)
- [Safety Settings Guide](../research/COMPREHENSIVE_GAP_ANALYSIS.md)
- [Cost Optimization Tips](../docs/)

## Support

For issues or questions:
- Check the [troubleshooting guide](../docs/troubleshooting.md)
- Review [common errors](../docs/common_errors.md)
- Open an issue on GitHub

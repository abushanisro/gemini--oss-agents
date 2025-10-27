# Gemini API OSS Agent Integration Enhancement Project

## Overview
This project aims to expand and improve Gemini API integration across popular agent/workflow tools, enabling developers to seamlessly build AI agents and workflows that leverage the capabilities of Gemini models.

## Project Scope

### Target Tools
- **LangChain**: Popular framework for developing LLM applications
- **LlamaIndex**: Data framework for LLM applications
- **CrewAI**: Framework for orchestrating role-playing autonomous AI agents
- **Composio**: Tool integration platform for AI agents
- **Additional Tools**: AutoGPT, Semantic Kernel, Haystack, etc.

### Key Objectives
1. Identify integration gaps in each target tool
2. Implement missing Gemini features (multimodal inputs, function calling, streaming, etc.)
3. Optimize existing integrations for performance and reliability
4. Create comprehensive documentation and examples
5. Engage with tool maintainers and community

## Gemini Features to Support

### Core Capabilities
- Text generation with various models (Gemini Pro, Ultra, Flash)
- Multimodal inputs (text, images, audio, video)
- Function calling and tool use
- Streaming responses
- System instructions
- Safety settings
- Token counting
- Embeddings

### Advanced Features
- Context caching
- Code execution
- Grounding with Google Search
- JSON mode
- Temperature and top-k/top-p sampling
- Multi-turn conversations

## Timeline
- **Estimated Duration**: 175-350 hours
- **Complexity**: Medium to High

## Quick Start

### 1. Setup
```bash
# Clone or navigate to the project
cd gemini-oss-agents

# Run setup script (installs dependencies, creates virtual environment)
bash setup.sh

# Or manually:
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Gemini API key
# GOOGLE_API_KEY=your_api_key_here
```

### 3. Test Setup
```bash
python test_gemini_setup.py
```

### 4. Run Examples
```bash
# Safety settings example
python examples/01_basic/langchain_with_safety_settings.py

# Error handling example
python examples/01_basic/langchain_error_handling.py

# Cost tracking example
python examples/01_basic/langchain_cost_tracking.py
```

## What's Implemented

### Production-Ready Utilities

1. **Safety Configuration** (`src/safety_config.py`)
   - Pre-configured safety presets (permissive, moderate, strict)
   - Custom safety builders
   - Framework-specific helpers

2. **Error Handling** (`src/error_handling.py`)
   - Retry with exponential backoff
   - Circuit breaker pattern
   - Safe generation with fallbacks
   - Safety block detection

3. **Cost Tracking** (`src/cost_tracker.py`)
   - Token usage monitoring
   - Cost estimation
   - Model comparison
   - Usage analytics and export

### Working Examples

- **LangChain Safety Settings** - Production safety configurations
- **LangChain Error Handling** - Robust error patterns
- **LangChain Cost Tracking** - Cost monitoring and optimization

### Research Completed

- Comprehensive analysis of 4 major tools (LangChain, LlamaIndex, CrewAI, Composio)
- Gap analysis identifying 50+ improvement opportunities
- Implementation strategy with 4 phases
- Detailed documentation in `research/` directory

## Key Features

### Safety Settings
- **Moderate Preset** (recommended): Balanced filtering for most applications
- **Strict Preset**: Maximum filtering for children's content
- **Custom Preset**: Fine-grained control per safety category

### Error Handling
- **Retry Logic**: Exponential backoff for transient failures
- **Circuit Breakers**: Prevent cascading failures
- **Fallbacks**: Graceful degradation for better UX
- **Safety Blocks**: Detect and handle content filtering

### Cost Management
- **Usage Tracking**: Monitor token consumption
- **Cost Estimation**: Pre-call cost prediction
- **Model Comparison**: Compare costs across models
- **Optimization**: Tips and strategies for cost reduction

## Contributing
This project involves contributing to multiple open-source projects. Follow each project's contribution guidelines.

## Resources
- [Gemini API Documentation](https://ai.google.dev/docs)
- [LangChain Documentation](https://python.langchain.com/)
- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [Composio Documentation](https://docs.composio.dev/)

## License
See individual tool licenses for contribution requirements.

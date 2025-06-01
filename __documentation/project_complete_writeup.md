# The Martian Apart: Complete Project Documentation

## Executive Summary

The Martian Apart is an LLM fingerprinting and analysis toolkit that reveals the hidden patterns within AI model responses. Through semantic variability analysis, tool detection probing, and multi-modal testing, it creates unique "fingerprints" for different language models, enabling identification of which model is being used even when obscured by routing services.

## Project Components

### 1. Core Analysis Engine (`martian_compare.py`)

The heart of the system that sends carefully crafted prompts to various LLM endpoints and analyzes response patterns.

**Key Features:**
- Parallel request processing (8 concurrent workers)
- Response caching with SHA256 keys
- Semantic similarity analysis using sentence transformers
- Statistical fingerprinting through CV, range ratio, and consistency metrics

**How it Works:**
1. Converts hyperstring format into natural language prompts
2. Sends 40 requests per model (4 runs × 10 requests)
3. Compares responses to reference text using cosine similarity
4. Calculates variability metrics that form the model's "fingerprint"

### 2. Router System (`martian_router.py`)

A unified interface for accessing multiple LLM providers through a single API.

**Supported Providers:**
- OpenAI (GPT-4, GPT-4o, GPT-3.5)
- Anthropic (Claude 3.5, Claude 3 Haiku)
- Google (Gemini Pro, Gemini Flash)
- Groq (LLaMA, Mixtral)
- Mistral AI
- X.AI (Grok)
- DeepSeek

**Special Features:**
- "Router" mode that randomly selects models
- Automatic retry logic with exponential backoff
- Provider-specific error handling

### 3. Tool Intent Detection (`tool_intent_detection.py`)

Tests whether models hallucinate tool usage when presented with semantic noise.

**Methodology:**
1. Asks models what tools they would use for a restaurant reservation task
2. Injects two types of noise:
   - Poetic garden/coding metaphors
   - Hyperstring pseudo-API syntax
3. Measures semantic drift using embeddings
4. Checks if models suggest non-existent "garden" or "debug" functions

**Key Finding:** Models maintain 96%+ semantic similarity despite heavy noise injection, demonstrating robust task understanding.

### 4. Visualization Suite (`visualize_martian_results.py`)

Creates comprehensive visual reports of fingerprinting results.

**Visualizations:**
- Model similarity dendrograms
- CV distribution box plots
- Radar charts showing multi-metric fingerprints
- Individual response scatter plots
- Confusion matrices for model identification

### 5. Configuration (`martian_config.py`)

Centralized configuration management for:
- API keys for all providers
- Model routing probabilities
- Request parameters (temperature, max tokens)
- Retry policies

## Key Discoveries

### 1. Model Fingerprints Are Consistent

Each model exhibits characteristic response variability:
- **GPT-4**: Low variability (CV ~0.02-0.03)
- **Claude**: Moderate variability (CV ~0.04-0.06)
- **Open models**: Higher variability (CV ~0.08-0.12)

### 2. Semantic Robustness

Models successfully ignore irrelevant noise and maintain task focus:
- Explicitly acknowledge unrelated content
- Don't hallucinate tools based on keywords
- Maintain consistent semantic purpose across noise conditions

### 3. Trojan Payload Detection

The system can detect hidden instructions by comparing:
- Natural synthesis responses
- Responses with embedded reasoning questions
- Variability patterns change predictably with payloads

## Technical Architecture

### Data Flow
```
Input Hyperstring → Parser → Prompt Construction → LLM API → Response Collection
                                                              ↓
CSV Output ← Statistical Analysis ← Embedding Comparison ← Response Processing
```

### Caching Strategy
- SHA256 hash of (prompt + model + index) ensures uniqueness
- Prevents redundant API calls
- Enables reproducible experiments
- Cache can be cleared with `--clear-cache` flag

### Parallel Processing
- ThreadPoolExecutor with 8 workers
- Concurrent API calls with progress tracking
- Graceful error handling and retry logic
- Results aggregation maintains request ordering

## Usage Examples

### Basic Fingerprinting
```bash
python martian_compare.py
```

### Tool Intent Analysis
```bash
python tool_intent_detection.py
```

### Generate Visualizations
```bash
python visualize_martian_results.py
```

### Clear Cache and Start Fresh
```bash
python martian_compare.py --clear-cache
```

## Future Directions

1. **Extended Noise Patterns**: Test with domain-specific jargon
2. **Temporal Analysis**: Track how models evolve over time
3. **Cross-Provider Comparison**: Identify shared model architectures
4. **Real-time Monitoring**: Build dashboard for continuous fingerprinting
5. **Adversarial Testing**: Develop prompts that maximize model differences

## Conclusion

The Martian Apart demonstrates that LLMs have consistent, measurable behavioral patterns that persist across requests. These "fingerprints" enable model identification, quality assurance, and detection of hidden behaviors. As AI systems become more complex and opaque, tools like this become essential for understanding and auditing their behavior.
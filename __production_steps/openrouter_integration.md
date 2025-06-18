# OpenRouter Integration - Production Steps

**Date:** 2025-06-18  
**Context:** Martian API changes required switching to OpenRouter as alternative provider

## Overview
Added OpenRouter support alongside existing Martian Router to enable multi-provider LLM access. This allows the system to use OpenRouter's extensive model catalog (323+ models) while maintaining backward compatibility with Martian.

## Implementation Steps

### 1. Created OpenRouter Configuration (`openrouter_config.py`)
- Base URL: `https://openrouter.ai/api/v1`
- Required headers: `HTTP-Referer` and `X-Title`
- Default models: Cohere Command-R Plus and Command-A
- Environment variable: `OPENROUTER_API_KEY`

### 2. Created OpenRouter Client (`openrouter_router.py`)
- OpenAI-compatible client using OpenRouter endpoint
- Proper header injection for OpenRouter requirements
- Model listing via `/api/v1/models` endpoint
- Cost estimation for various models

### 3. Modified Data Generation Pipeline (`martian_compare.py`)
- Added `provider` parameter throughout the pipeline:
  - `send_to_martian_single()` - selects router based on provider
  - `send_to_martian_parallel()` - passes provider to single calls
  - `run_model_test()` - accepts provider parameter
  - `save_to_csv()` - tracks provider in output
- Updated TESTS configuration to include provider field
- **Cache key modification**: Added `"_provider_" + provider` to ensure separate caching per provider

### 4. Integration Testing (`tests/`)
- Created `test_martian_integration.py` for Martian API
- Created `test_openrouter_integration.py` for OpenRouter API
- Added model listing to integration test
- Confirmed 323 available models via OpenRouter

## Key Technical Decisions

### Provider Selection Logic
```python
if provider == "openrouter":
    router = OpenRouterClient()
else:
    router = MartianRouter()
```

### Cache Separation
Cache keys now include provider to prevent cross-provider cache pollution:
```python
cache_hash = get_cache_key(text, "system_prompt_" + system_prompt + "_" + payload_str + "_provider_" + provider, ...)
```

### CSV Schema Update
Added `provider` field to track which API was used for each response

## Migration Path

### Current Status
- Martian API may be deprecated/changed
- OpenRouter confirmed working with 323 available models
- Both providers supported in parallel

### Next Steps
1. Update all test configurations to use `"provider": "openrouter"`
2. Replace Martian models with OpenRouter equivalents
3. Consider removing Martian code if confirmed deprecated

## Environment Setup
```bash
# Add to .env file
OPENROUTER_API_KEY=sk-or-v1-xxxxx
```

## Testing
```bash
# Test OpenRouter connection
python tests/test_openrouter_integration.py

# Run full analysis with OpenRouter
python martian_compare.py  # Uses provider field in TESTS config
```

## Models Available
- 323 models including:
  - OpenAI (GPT-4, GPT-3.5)
  - Anthropic (Claude 3 Opus/Sonnet)
  - Google (Gemini 2.5 Pro/Flash)
  - Cohere (Command-R Plus)
  - Meta (Llama 3)
  - And many more...
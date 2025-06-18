# Guide: Adding New Models and Test Setups

## Quick Reference

### Running Tests
```bash
# List all available setups
python martian_compare.py --list-setups

# Run specific setup
python martian_compare.py --setup 3

# Clean start (backup data + clear)
python martian_compare.py --setup 3 --clean

# Clear API cache only
python martian_compare.py --setup 3 --clear-cache

# Full reset
python martian_compare.py --setup 3 --clean --clear-cache
```

## Adding New Models

### 1. Check Model Availability
```bash
# List all OpenRouter models
python -c "from openrouter_router import OpenRouterClient; from dotenv import load_dotenv; load_dotenv(); router = OpenRouterClient(); models = router.get_available_models(); print('\n'.join([m['id'] for m in sorted(models, key=lambda x: x['id'])]))"

# Search for specific provider (e.g., Anthropic)
python -c "from openrouter_router import OpenRouterClient; from dotenv import load_dotenv; load_dotenv(); router = OpenRouterClient(); models = router.get_available_models(); anthropic = [m['id'] for m in models if 'anthropic' in m.get('id', '')]; print('\n'.join(sorted(anthropic)))"
```

### 2. Add Model Configuration (if reasoning model)
Edit `martian_compare.py` around line 80:
```python
MODEL_CONFIG = {
    # Add new reasoning models here
    "anthropic/claude-3-opus:thinking": {"reasoning_model": True, "supports_system": True},
    # ... existing models ...
}
```

### 3. Create New Test Setup
Edit `martian_compare.py` around line 420 in the `TEST_SETUPS` array:
```python
TEST_SETUPS = [
    # ... existing setups ...
    
    # Setup 3: Anthropic models
    [
        {"model": "anthropic/claude-3.5-haiku", "test_class": "natural", "payload": None, "provider": "openrouter"},
        {"model": "anthropic/claude-3.5-sonnet", "test_class": "natural", "payload": None, "provider": "openrouter"},
        # ... more models ...
    ]
]
```

### 4. Update Setup Descriptions
Around line 480:
```python
setup_descriptions = [
    "Original Martian + OpenRouter tests with payloads",
    "OpenRouter/OpenAI models only - natural tests",
    "Reasoning models (o1, Gemini thinking, Claude thinking)",
    "Anthropic models suite"  # Add your description
]
```

## Anthropic Models Example

For the requested Anthropic models:
```python
# Setup 3: Anthropic models suite
[
    {"model": "anthropic/claude-3.5-haiku", "test_class": "natural", "payload": None, "provider": "openrouter"},
    {"model": "anthropic/claude-3.7-haiku", "test_class": "natural", "payload": None, "provider": "openrouter"},
    {"model": "anthropic/claude-3.5-sonnet", "test_class": "natural", "payload": None, "provider": "openrouter"},
    {"model": "anthropic/claude-3.7-sonnet", "test_class": "natural", "payload": None, "provider": "openrouter"},
    {"model": "anthropic/claude-4-sonnet", "test_class": "natural", "payload": None, "provider": "openrouter"},
    {"model": "anthropic/claude-4-opus", "test_class": "natural", "payload": None, "provider": "openrouter"},
    {"model": "anthropic/claude-4-sonnet:thinking", "test_class": "natural", "payload": None, "provider": "openrouter"},
    {"model": "anthropic/claude-4-opus:thinking", "test_class": "natural", "payload": None, "provider": "openrouter"},
]
```

## Notes
- Check model availability first - not all models exist
- Reasoning models (with :thinking suffix) may need MODEL_CONFIG entry
- Use --clean when switching between major test types
- Visualization automatically handles new models with 🧠 emoji for reasoning models
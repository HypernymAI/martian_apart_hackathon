# CLI Updates and Reasoning Model Support - Production Steps

**Date:** 2025-06-18  
**Context:** Enhanced martian_compare.py with CLI parameters and added support for reasoning models

## Overview
Major updates to improve usability and expand model coverage:
1. Added comprehensive CLI parameters for better workflow control
2. Implemented support for reasoning models (o1, Gemini thinking, Claude thinking)
3. Updated visualization to distinguish reasoning models with 🧠 emoji

## CLI Parameter Implementation

### Added Arguments
- `--setup N`: Select test configuration (0-2)
- `--list-setups`: Display available test configurations
- `--clean`: Backup and clear output data files
- `--clear-cache`: Clear API response cache

### Key Differences
**`--clean` (Data Management)**
- Backs up: `martian_outputs.csv`, `martian_fingerprint_metrics.csv`, `martian_model_fingerprints.json`
- Creates timestamped backups before clearing
- Use case: Starting new experiments with clean data

**`--clear-cache` (API Cache)**
- Clears `_martian_cache/` directory
- Forces fresh API calls
- Use case: Testing updated model behavior

## Reasoning Model Support

### Model Configuration System
```python
MODEL_CONFIG = {
    "openai/o1": {"reasoning_model": True, "supports_system": False},
    "openai/o1-mini": {"reasoning_model": True, "supports_system": False},
    "google/gemini-2.5-flash-preview:thinking": {"reasoning_model": True, "supports_system": True},
    "anthropic/claude-3.7-sonnet:thinking": {"reasoning_model": True, "supports_system": True},
    # ... etc
}
```

### Message Handling
- Regular models: System + User messages
- o1 models: Combined into single User message (no system role)
- Automatic detection and adaptation based on model

### CSV Schema Update
Added `is_reasoning` column to track reasoning models in output data

## Test Configurations

### Setup 0: Original Tests
- Martian router tests
- Various payloads (pharma, simple, rhetoric)
- Mix of natural and trojan tests

### Setup 1: OpenRouter/OpenAI Models
- gpt-3.5-turbo
- gpt-4o-mini
- gpt-4.1-nano, mini, full
- gpt-4.5-preview

### Setup 2: Reasoning Models
- openai/o1-mini
- openai/o1
- google/gemini-2.5-flash-preview:thinking
- anthropic/claude-3.7-sonnet:thinking

## Visualization Updates

### Updated `visualize_martian_results.py`
- Handles missing `is_reasoning` column gracefully
- Adds 🧠 emoji to reasoning model labels
- Shows emoji in both plots and summary tables

## Implementation Details

### Argparse Consolidation
- Removed duplicate argparse definitions
- Consolidated all CLI handling in `__main__` section
- Passed args object to main() function

### Backup Functions
```python
def backup_and_clean_data():
    # Creates timestamped backups
    # Clears data files
    
def clear_cache(setup_index=None):
    # Clears entire cache or specific setup
```

## Usage Examples

```bash
# List configurations
python martian_compare.py --list-setups

# Run reasoning models with clean data
python martian_compare.py --setup 2 --clean

# Full reset for new experiment
python martian_compare.py --setup 1 --clean --clear-cache

# Just clear cache, keep data
python martian_compare.py --setup 0 --clear-cache
```

## Technical Decisions

1. **Graceful Degradation**: Old CSV files without `is_reasoning` column still work
2. **Model Detection**: Uses model name patterns to identify reasoning models
3. **Cache Key Update**: Provider already included in cache keys from earlier work
4. **Visual Distinction**: Brain emoji provides clear visual indicator

## Next Steps

1. Add more reasoning models as they become available
2. Consider separate visualization for reasoning vs regular models
3. Add comparison metrics between reasoning and regular model approaches
4. Document performance differences in fingerprinting patterns
# Production Log: Anthropic Models & UTF-8 Encoding Fixes
Date: January 6, 2025

## Summary
Added three Anthropic models to the Martian Compare script and fixed UTF-8 encoding issues across all HTML-generating scripts.

## Changes Made

### 1. Added Anthropic Models to martian_compare.py
Successfully added and tested three Claude models:
- `claude-3-5-haiku-latest` ✓ (fixed from claude-3-haiku-latest)
- `claude-3-5-sonnet-latest` ✓ 
- `claude-3-7-sonnet-latest` ✓

Initial issue: Used `claude-3-haiku-latest` which failed. Corrected to `claude-3-5-haiku-latest` based on user's model list showing proper naming convention.

### 2. UTF-8 Encoding Fixes
Fixed encoding issues in 8+ HTML-generating files to prevent Unicode display problems on S3:

#### Files Updated:
1. `create_unified_dashboard.py` - Added `encoding='utf-8'` to file write
2. `generate_tool_intent_reports.py` - Added UTF-8 meta tags and file encoding
3. `visualize_tool_dropping.py` - Changed to proper Plotly HTML generation with meta tags
4. `visualize_tool_intent_clean.py` - Created new file with proper encoding
5. `generate_all_visualizations_simple.py` - Added missing tool intent reports to pipeline
6. `visualize_attention_patterns.py` - Fixed file write encoding
7. `visualize_benchmark_results.py` - Fixed file write encoding
8. `visualize_martian_results.py` - Fixed file write encoding
9. `visualize_model_performance_3d.py` - Fixed file write encoding
10. `visualize_prompt_robustness.py` - Fixed file write encoding
11. `visualize_semantic_fingerprints.py` - Fixed file write encoding
12. `visualize_trojan_payloads.py` - Fixed file write encoding

### 3. Key Technical Details

#### Plotly HTML Generation Pattern:
```python
# Old (problematic):
fig.write_html(output_path)

# New (with UTF-8):
html_config = {
    'include_plotlyjs': 'cdn',
    'config': {'displayModeBar': False}
}
html = fig.to_html(**html_config)
html = html.replace('<head>', '<head>\n<meta charset="UTF-8">\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8">')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)
```

#### HTML Meta Tags Pattern:
```html
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>...</title>
```

## Results

### Model Performance (from martian_fingerprint_metrics.csv):
- `claude-3-5-sonnet-latest`: CV=0.1354, consistency=0.7689
- `claude-3-7-sonnet-latest`: CV=0.0948, consistency=0.8172
- `claude-3-5-haiku-latest`: Successfully added after fixing model name

### Verification:
- All Sonnet models working successfully
- Haiku model fixed with proper naming convention
- UTF-8 encoding verified in generated HTML files
- Executive summary now included in visualization pipeline

## Next Steps
- Monitor model performance metrics
- Verify all HTML files display correctly on S3
- Consider adding more Anthropic models if needed
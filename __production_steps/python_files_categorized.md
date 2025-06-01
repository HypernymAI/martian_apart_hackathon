# Python Files Categorized by Function

## MARTIAN COMPARE PATH

### Core Runner
- `martian_compare.py` - Main experiment runner (generates martian_outputs.csv)

### Visualization Generator
- `visualize_martian_results.py` - Generates 4 HTML files:
  - martian_fingerprint_analysis.html
  - martian_similarity_distribution.html
  - martian_response_lengths.html
  - martian_payload_complexity.html

---

## TOOL INTENT DETECTION PATH

### Core Runners

#### Initial Tool Detection
- `tool_intent_detection.py` - Main experiment (generates):
  - tool_intent_parallel_router.json
  - tool_intent_results_router.csv

#### Distraction Experiment
- `test_distraction_hypotheses.py` - Runs 5 hypotheses (generates):
  - distraction_hypothesis_results.csv
  - distraction_hypothesis_full_results.json

### Analysis Scripts (Non-generating)
- `analyze_tool_differences.py` - Analyzes 3 vs 4 tool patterns
- `analyze_tool_drop_pattern.py` - Statistical analysis
- `analyze_tool_dropping.py` - Detailed comparison
- `distraction_hypotheses.py` - Just hypothesis definitions

### Visualization Generators

#### Tool Intent Visualizations
- `visualize_tool_intent.py` - Generates 5 HTML files:
  - tool_intent_breakdown.html
  - tool_intent_semantic_heatmap.html
  - tool_intent_count_distribution.html
  - tool_intent_function_frequency.html
  - tool_intent_detailed_view.html

- `visualize_tool_intent_clean.py` - Generates 2 HTML files:
  - tool_intent_clean.html
  - tool_intent_simple_report.html

- `visualize_tool_fingerprints.py` - Generates 2 HTML files:
  - tool_fingerprints_interactive.html
  - tool_fingerprints_report.html

- `visualize_tool_stability.py` - Generates 2 HTML files:
  - tool_stability_main.html
  - tool_stability_differences.html

- `visualize_tool_patterns.py` - Generates 1 HTML file:
  - tool_patterns_analysis.html

- `visualize_tool_dropping.py` - Generates 2 HTML files:
  - tool_dropping_discovery.html
  - tool_dropping_summary.html

#### Distraction Visualizations
- `visualize_distraction_results.py` - Generates 2 HTML files:
  - distraction_effectiveness.html
  - distraction_summary.html

- `visualize_distraction_technical.py` - Generates 2 HTML files:
  - distraction_technical_analysis.html
  - distraction_drop_details.html

- `visualize_distraction_full_text.py` - Generates 1 HTML file:
  - distraction_full_text_analysis.html

#### Report Generator
- `generate_tool_intent_reports.py` - Generates 1 HTML file:
  - tool_intent_simple_report_generated.html

---

## DASHBOARD GENERATOR
- `create_unified_dashboard.py` - Generates 1 HTML file:
  - index.html

---

## SUMMARY

### Martian Compare: 2 Python files
1. Core: `martian_compare.py`
2. Viz: `visualize_martian_results.py`

### Tool Intent: 16 Python files
1. Core Runners: 2 files
   - `tool_intent_detection.py`
   - `test_distraction_hypotheses.py`

2. Analysis (non-generating): 4 files

3. Visualization Generators: 10 files
   - 6 for tool intent viz
   - 3 for distraction viz
   - 1 for report generation

### Dashboard: 1 Python file
- `create_unified_dashboard.py`
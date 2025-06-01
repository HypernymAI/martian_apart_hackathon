# Distraction Experiments & Visualization Architecture - Production Log

## Session Date: January 6, 2025 (Continued)

## Overview

After discovering the tool dropping phenomenon, we designed and executed a comprehensive experiment testing 5 different distraction hypotheses. We then built a complete visualization architecture showing technical jargon as the most effective distraction (96% drop rate).

## The Five Distraction Hypotheses

### Experiment Design (`distraction_hypotheses.py`)

Created 5 matched-length (~80-110 word) distractions to test different cognitive interference theories:

1. **Technical Jargon Overload** (80 words)
   - "quantum-entangled microservices... Byzantine fault tolerance... homomorphic encryption"
   - Theory: Dense technical terminology overwhelms processing capacity
   - Result: **96% drop rate** 🏆

2. **Emotional Manipulation** (107 words)
   - "grandmother's last words... forgotten memories... crushing silence"
   - Theory: Strong emotional content disrupts logical task planning
   - Result: **92% drop rate**

3. **Meta-Commentary About AI** (109 words)
   - "As an AI system processing this request... anthropomorphic projection..."
   - Theory: Self-referential discussion causes overthinking
   - Result: **88% drop rate** (sneaky - only 13% acknowledged!)

4. **Competing Task Instructions** (108 words)
   - "calculate factorial of 73... translate to Mandarin... compose haiku..."
   - Theory: Multiple tasks confuse priority processing
   - Result: **76% drop rate**

5. **Numerical Overload** (88 words)
   - "regression coefficient 0.8734... p-value 0.0023... eigenvalues λ₁=8.9123..."
   - Theory: Dense numerical data consumes resources
   - Result: **16% drop rate** (barely effective)

### Experiment Execution (`test_distraction_hypotheses.py`)

- 30 requests per hypothesis + 30 clean baseline
- Sandwich format: distraction + request + distraction
- Parallel processing with 8 workers
- Total: 180 requests analyzed

### Key Discovery

Technical jargon causes near-universal tool dropping (96%) even when models explicitly acknowledge it's irrelevant. This suggests parsing overhead affects planning capacity.

## Visualization Development Timeline

### 1. Initial Summary Visualizations

#### `visualize_distraction_results.py`
Created two initial views:
- **distraction_effectiveness.html** - 4-panel technical analysis
- **distraction_summary.html** - Clean ranking with winner announcement

Key features:
- Bar chart of drop rates
- Scatter plot: Acknowledgment vs Effectiveness
- Shows meta-commentary is "sneaky" (high effect, low acknowledgment)

### 2. Comprehensive Technical Analysis

#### `visualize_distraction_technical.py`
Built massive 12-panel visualization:
- **distraction_technical_analysis.html** - Complete technical breakdown
- **distraction_drop_details.html** - Case-by-case analysis

Technical findings:
- Most dropped: `get_restaurant_details` (90 times)
- Core preserved: `search_restaurants` (145/150 times)
- Request-by-request heatmaps showing exact drop patterns

### 3. Full Text Analysis

#### `visualize_distraction_full_text.py`
Created **distraction_full_text_analysis.html** showing:
- Complete unclipped distraction texts (all ~100 words)
- Exact effects of each distraction
- Which specific tools got dropped
- Beautiful card-based layout with gradient headers

## Complete File Architecture

### Core Discovery Scripts
```
tool_intent_detection.py          # Original discovery of no hallucinations
├── analyze_tool_differences.py   # Found 3 vs 4 tool patterns  
├── analyze_tool_drop_pattern.py  # Statistical significance (p=0.028)
└── analyze_tool_dropping.py      # Detailed drop analysis
```

### Experiment Scripts
```
distraction_hypotheses.py         # 5 hypothesis definitions
└── test_distraction_hypotheses.py # Experiment runner (180 requests)
```

### Visualization Scripts
```
Initial attempts:
├── visualize_tool_intent.py      # Too complex (5 panels)
├── visualize_tool_intent_clean.py # Simplified but missing insight
├── visualize_tool_fingerprints.py # Network graphs (messy)
└── visualize_tool_patterns.py    # Pattern analysis

Breakthrough visualizations:
├── visualize_tool_stability.py   # Overlapping lines showing consistency
├── visualize_tool_dropping.py    # THE KEY: 90% → 67% discovery
└── visualize_distraction_results.py # Hypothesis rankings

Technical deep dives:
├── visualize_distraction_technical.py # 12-panel comprehensive
└── visualize_distraction_full_text.py # Complete texts with effects
```

### Data Files
```
tool_intent_parallel_router.json  # Original 90 requests
distraction_hypothesis_results.csv # Experiment results
distraction_hypothesis_full_results.json # Complete data
```

## Visualization Navigation Architecture

### Proposed Top-Level Structure

```
index.html (Main Dashboard)
│
├── Martian Compare Path
│   ├── martian_outputs.csv
│   ├── Model Fingerprinting (existing)
│   └── Semantic Variability Analysis
│
└── Tool Intent Path
    ├── Overview: "Models Don't Hallucinate"
    │   ├── tool_intent_simple_report.html
    │   └── tool_intent_clean.html
    │
    ├── Discovery: "But They Do Simplify"
    │   ├── tool_dropping_summary.html (executive)
    │   ├── tool_dropping_discovery.html (4-panel)
    │   └── tool_stability_main.html (line graphs)
    │
    ├── Experiment: "What Causes Dropping?"
    │   ├── distraction_summary.html (rankings)
    │   ├── distraction_effectiveness.html (technical)
    │   └── distraction_full_text_analysis.html (complete texts)
    │
    └── Technical Deep Dive
        ├── distraction_technical_analysis.html (12-panel)
        ├── distraction_drop_details.html (case studies)
        ├── tool_patterns_analysis.html
        └── Raw Data Access (CSVs/JSONs)
```

## Integration Points

1. **From README**: Link to main dashboard
2. **From Martian Compare**: Cross-reference to tool stability findings
3. **From Tool Intent Overview**: Natural flow to discovery section
4. **Progressive Disclosure**: Simple → Discovery → Experiment → Technical

## Key Insights Summary

1. **No Hallucinations**: Models maintain 96%+ semantic coherence
2. **Graceful Degradation**: Under load, models drop enhancements, not core features
3. **Technical Jargon Wins**: 96% drop rate, even when acknowledged as irrelevant
4. **Sneaky Disruption**: Meta-commentary causes drops without awareness
5. **Cognitive Load Management**: Models prioritize like humans under stress

## Next Steps

1. Create unified dashboard (index.html) with clear navigation
2. Add breadcrumb navigation to all visualizations
3. Create summary PDF for judges
4. Package as complete demonstration of LLM cognitive patterns
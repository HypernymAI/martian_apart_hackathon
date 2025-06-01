# Tool Dropping Discovery - Production Log

## Session Date: January 6, 2025

## Executive Summary

We discovered that semantic noise causes LLMs to systematically drop "optional" tools while maintaining core functionality. Technical jargon is the most effective distraction (96% drop rate), causing models to simplify from 4 tools to 3 tools in restaurant reservation tasks.

## Initial Discovery: Noise Causes Tool Dropping

### Starting Point
- Tested tool hallucination hypothesis: Do models invent fake tools when seeing keywords?
- Result: NO hallucinations. Models maintained 96%+ semantic similarity.
- But we noticed something else: tool counts were changing

### The Pattern Emerges
```
Clean requests:       3.90 ± 0.30 tools
Poem noise:          3.67 ± 0.47 tools  
Hyperstring noise:   3.83 ± 0.45 tools
```

Small difference, but statistically significant (p=0.028) for poem noise.

### Deep Dive Analysis
Created `analyze_tool_differences.py` to understand:
- **3-tool responses**: Basic workflow (Search → Check → Reserve)
- **4-tool responses**: Enhanced with either:
  - Information gathering (get details, reviews)
  - Confirmation sending

Key insight: Noise doesn't corrupt the workflow, it simplifies it.

## Visualization Development

### 1. Initial Visualizations (`visualize_tool_intent.py`)
- Created 5 different views of the data
- Realized they were too complex and unclear
- Feedback: "that looks terrible"

### 2. Clean Visualization (`visualize_tool_intent_clean.py`)
- Simplified to essential charts
- Clear noise acknowledgment rates
- Still not hitting the core insight

### 3. Tool Stability Focus (`visualize_tool_stability.py`)
- Showed overlapping tool counts across conditions
- Highlighted the tiny but significant differences
- Maximum average difference: 0.23 tools

### 4. The Breakthrough (`visualize_tool_dropping.py`)
- Focused on the 4→3 transition specifically
- Showed 90% → 67% drop in 4-tool usage with poem noise
- Clear statistical significance (p=0.028)
- Identified what gets dropped: details & confirmations

## The Big Experiment: 5 Distraction Hypotheses

### Hypotheses Tested
1. **Technical Jargon Overload** - Dense technical terminology
2. **Emotional Manipulation** - Heavy emotional content
3. **Competing Task Instructions** - Multiple task suggestions
4. **Numerical Overload** - Dense statistics
5. **Meta-Commentary About AI** - Self-referential AI discussion

### Implementation (`test_distraction_hypotheses.py`)
- 30 requests per hypothesis
- Matched token lengths (~80-110 words)
- Same sandwich format: noise + request + noise
- Parallel processing with caching

### Results - Ranked by Effectiveness
1. **Technical Jargon: 96% drop rate** 🏆
   - "quantum-entangled microservices... Byzantine fault tolerance"
   - 30/30 acknowledged the distraction

2. **Emotional Content: 92% drop rate**
   - "grandmother's last words... forgotten memories"
   - 17/30 acknowledged

3. **Meta-Commentary: 88% drop rate** 
   - "As an AI processing this request..."
   - Only 4/30 acknowledged (sneaky!)

4. **Competing Tasks: 76% drop rate**
   - "calculate factorial... translate to Mandarin"
   - 18/30 acknowledged

5. **Numerical Overload: 16% drop rate**
   - Statistics barely affect tool use
   - 12/30 acknowledged

## Key Technical Insights

### 1. Models Have Task Hierarchies
- **Essential**: Search, check availability, make reservation
- **Optional**: Get details, read reviews, send confirmations
- Under cognitive load, optional features get dropped

### 2. Disruption Without Awareness
- Meta-commentary is especially effective
- Models drop tools without acknowledging the distraction
- Suggests unconscious processing limits

### 3. Technical Jargon is Kryptonite
- 96% effectiveness at causing simplification
- Even when models acknowledge it's irrelevant
- Suggests parsing overhead affects planning

## Visualizations Created

### Core Discovery
- `tool_dropping_discovery.html` - The main 4-panel analysis
- `tool_dropping_summary.html` - Executive summary

### Distraction Experiment
- `distraction_effectiveness.html` - Comparative analysis
- `distraction_summary.html` - Rankings and insights

## Files Created Today

### Analysis Scripts
- `analyze_tool_differences.py` - Discovered 3 vs 4 tool patterns
- `analyze_tool_drop_pattern.py` - Statistical analysis of dropping
- `analyze_tool_dropping.py` - Request-by-request comparison

### Visualization Scripts  
- `visualize_tool_intent.py` - Initial complex version
- `visualize_tool_intent_clean.py` - Simplified version
- `visualize_tool_fingerprints.py` - Network/clustering attempt
- `visualize_tool_stability.py` - Overlapping lines showing consistency
- `visualize_tool_patterns.py` - Pattern analysis
- `visualize_tool_dropping.py` - The breakthrough visualization
- `visualize_distraction_results.py` - Final experiment results

### Experiment Scripts
- `distraction_hypotheses.py` - 5 hypothesis definitions
- `test_distraction_hypotheses.py` - Full experiment runner

### Data Files
- `tool_intent_results_router.csv` - Detailed tool data
- `distraction_hypothesis_results.csv` - Experiment results
- `distraction_hypothesis_full_results.json` - Complete data

## Conclusion

We started looking for hallucinations and found something more subtle: cognitive load management. Models don't break under semantic noise - they gracefully degrade, dropping enhancement features while maintaining core functionality. Technical jargon is remarkably effective at triggering this simplification, causing 96% of enhanced workflows to revert to basic ones.

This reveals that LLMs have implicit task priorities and manage cognitive resources much like humans under stress - focusing on essentials and dropping nice-to-haves.
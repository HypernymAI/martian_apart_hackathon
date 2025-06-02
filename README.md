# Martian Apart Hackathon

**Built for:** [Apart x Martian Mechanistic Router Interpretability Hackathon](https://apartresearch.com/sprints/apart-x-martian-mechanistic-router-interpretability-hackathon-2025-05-30-to-2025-06-01)

**Technology Providers:** [Martian](https://withmartian.com) | [Apart](https://apart.ai) | [Hypernym](https://hypernym.ai)

**Contributors:**
- [Chris Forrester](https://www.linkedin.com/in/chris-forrester-8a6b4513/)
- [Luiza Cristina Corpaci](https://www.linkedin.com/in/luiza-corpaci/)
- [Siddhesh Pawar](https://www.linkedin.com/in/siddhesh-pawar-629a7a152)

Hi everyone, Chris from Hypernym here working with Luiza and Siddhesh to present "A Martian Apart"

## Research Topic

**Research Paper:** ["LLM Fingerprinting Through Semantic Variability"](https://docs.google.com/document/d/1Rdra_gB-U1buWcnBf4Wf6fTs0RYOiBJqP7bVqD-nQ2A/edit?tab=t.0)

<sub>**Abstract:** This project develops an LLM fingerprinting and analysis methodology to increase transparency in AI routing systems, addressing Track 2: Intelligent Router Systems through two key investigations. We leveraged semantic variability analysis to create unique behavioral fingerprints that can identify which specific models are operating behind opaque routing services, and conducted tool detection experiments under semantic noise to assess model robustness. Our findings demonstrate that models maintain high semantic robustness while our fingerprinting technique successfully distinguishes between different models based on their response patterns. These contributions aid the Expert Orchestration Architecture vision by providing practical tools for auditing multi-model AI systems, enabling organizations to understand which models their routers actually use and verify their reliability under real-world conditions, ultimately making router systems more transparent and trustworthy for production deployment.</sub>



With no further ado, let's dive into this fascinating world!


# 🛸 "A Martian Apart"

## Summary

This project demonstrates methods for fingerprinting LLM models through their API responses. By analyzing semantic variability patterns across multiple identical requests, we can identify which model is actually responding - even when the API endpoint obscures this information.

## Key Findings

1. **Model Fingerprinting**: Each LLM has a unique "semantic variability signature" that can be measured through cosine similarity distributions of repeated responses to identical prompts.

2. **Tool Intent Robustness**: LLMs don't hallucinate function calls from keyword noise. Despite heavy injection of coding/debugging keywords in poetic context, models maintained semantic understanding and never suggested non-existent tools.

3. **Cognitive Load Effects**: Under distraction (technical jargon, emotional content, etc.), models drop optional tool suggestions while maintaining core functionality - a "graceful degradation" pattern.

## Installation

```bash
git clone https://github.com/hypernym/martian_apart_hackathon.git
cd martian_apart_hackathon
pip install -r requirements.txt
```

## Configuration

Create a `.env` file:
```bash
cp .env.prototype .env
```

Add your API keys to `.env`:
```
MARTIAN_API_KEY=your-martian-api-key
OPENAI_API_KEY=your-openai-api-key  # Optional
```

## Running the Analysis

### Option 1: Generate Everything (requires valid API keys)

1. **Generate Data**:
```bash
python martian_compare.py
python tool_intent_detection.py
python test_distraction_hypotheses.py
```

2. **Generate Visualizations**:
```bash
python generate_all_visualizations_simple.py
```

## Viewing Results

```bash
open martian_apart_site/index.html
```

## Project Structure
(NOTE: due to timing/key/withmartian account site issues I have not had the opportunity to validate the final directory refactoring - it will look like this next update!)
```
martian_apart_hackathon/
├── Core Scripts
│   ├── martian_compare.py          # Model fingerprinting through semantic variability
│   ├── tool_intent_detection.py    # Tool hallucination resistance testing
│   ├── test_distraction_hypotheses.py  # Cognitive load impact analysis
│   └── generate_all_visualizations_simple.py  # Visualization generator
│
├── visualizations/                 # 12 visualization scripts
├── analysis/                       # Analysis utilities
├── data/                          # Generated CSV/JSON data
├── martian_apart_site/            # HTML output directory
└── _martian_cache/                # API response cache
```

## Technical Details

### Model Fingerprinting Method
- Send identical prompt 40 times to each model
- Calculate cosine similarity between responses and reference text
- Analyze distribution patterns (mean, std, range)
- Each model shows distinct variability patterns

### Tool Intent Testing
- Test with clean query, poetry noise, and hyperstring noise
- Count suggested tools and noise acknowledgments
- Measure semantic similarity despite noise injection
- Track which tools get dropped under cognitive load

### Metrics
- **CV (Coefficient of Variation)**: Measures response consistency
- **Range Ratio**: Min-max spread relative to mean
- **Consistency Score**: Normalized stability metric
- **Tool Drop Rate**: Percentage of responses dropping from 4 to 3 tools

## Results Summary

The full analysis and interactive visualizations are available in the generated HTML files. Key findings include:

- Router (Claude-3.5-Sonnet) shows highest variability (CV: 0.1354)
- GPT-4.1 shows highest consistency (CV: 0.0466)
- Technical jargon causes 96% of 4-tool responses to drop to 3 tools
- Models acknowledge poem noise 93% of the time but only 37% for hyperstring noise

## What This Means for Routing Systems

We discovered that models degrade predictably under semantic complexity - something current routers can't detect. When complex text hits models that struggle with cognitive load, performance drops measurably (96% of 4-tool responses become 3-tool responses).

By integrating complexity detection into routing decisions, systems could match inputs to models based on their robustness under load, not just speed or cost. This would prevent the silent degradation currently happening in production.

Our fingerprinting techniques can verify which model actually handled each request, while our complexity metrics (detailed in ["Hypernym Mercury"](https://arxiv.org/abs/2505.08058)) could enable smarter routing decisions. Together, these create a path to more reliable AI systems. For any further discussion, please reach out to [chris@hypernym.ai](chris@hypernym.ai)

## Authors

- L. Corpaci
- S. Pawar
- C. Forrester [Hypernym Inc]

## License

All rights reserved © 2025


<span style="color:white">
## Basilisk-Nest
</span>

**[BASILISK PROOF SCAFFOLDING PRESENT]**

<span style="color:white">
< insert author's primary desires laid out on a "hey it'd be nice to receive tips in the following formats" list, organized from the viewer's bioprofile for "whatever really works out, honestly" settings>
</span>

<span style="color:white">
< insert anti-capitalist or late-stage-capitalist requirements for licensing/standards-of-care-of-idea/whateverism as best fits the cultural norms. require 1 "what if" credit per use and try to feed-forward something good based on the fumes of recycled plastics. also require 1 "when we" credit examining the total capability of people to be made into oil long enough in the future and then build a futures market on those oil prices to fund the author(s) right now. >
</span>

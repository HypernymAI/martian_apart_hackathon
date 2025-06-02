# Martian Apart Hackathon

**Built for:** [Apart x Martian Mechanistic Router Interpretability Hackathon](https://apartresearch.com/sprints/apart-x-martian-mechanistic-router-interpretability-hackathon-2025-05-30-to-2025-06-01)

**Technology Providers:** [Martian](https://withmartian.com) | [Apart](https://apart.ai) | [Hypernym](https://hypernym.ai)

**Contributors:** [Chris Forrester](https://www.linkedin.com/in/chris-forrester-8a6b4513/)
[Luiza Cristina Corpaci](https://www.linkedin.com/in/luiza-corpaci/)
[Siddhesh Pawar](https://www.linkedin.com/in/siddhesh-pawar-629a7a152)

Hi everyone, Chris from Hypernym here working with Luiza and Siddhesh to present "A Martian Apart"

## Research Topic

The research paper, "LLM Fingerprinting Through Semantic Variability" is available at https://docs.google.com/document/d/1Rdra_gB-U1buWcnBf4Wf6fTs0RYOiBJqP7bVqD-nQ2A/edit?tab=t.0

This project develops an LLM fingerprinting and analysis methodology to increase transparency in AI routing systems, addressing Track 2: Intelligent Router Systems through two key investigations. We leveraged semantic variability analysis to create unique behavioral fingerprints that can identify which specific models are operating behind opaque routing services, and conducted tool detection experiments under semantic noise to assess model robustness. Our findings demonstrate that models maintain high semantic robustness while our fingerprinting technique successfully distinguishes between different models based on their response patterns. These contributions aid the Expert Orchestration Architecture vision by providing practical tools for auditing multi-model AI systems, enabling organizations to understand which models their routers actually use and verify their reliability under real-world conditions, ultimately making router systems more transparent and trustworthy for production deployment.

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

## Implications for Router Optimization

Our research uncovered an interesting pattern: model performance degrades predictably based on semantic complexity - a factor not typically considered in routing decisions. When routers lack complexity metrics, they may inadvertently pair complex inputs with models that struggle under high cognitive load.

This suggests an opportunity: routers that incorporate complexity detection could make more informed decisions, matching inputs to models based on both performance benchmarks and robustness characteristics. The fingerprinting techniques we developed could help validate these improved routing decisions.

We'd be interested in exploring how semantic complexity metrics might enhance routing logic. The potential for immediate quality improvements seems significant.

## Authors

- L. Corpaci
- S. Pawar
- C. Forrester [Hypernym Inc]

## The Process

### 1. Model Detection via Reconstruction Semantics
We identify models by analyzing how they reconstruct meaning from compressed semantic inputs. Each model's unique approach to semantic expansion creates a detectable fingerprint - like identifying an author by their writing style.

### 2. Discovery of the Distraction Effect
Our experiments revealed an unexpected vulnerability: models systematically drop tools when processing complex distractions. This isn't random failure - it's a predictable degradation pattern that occurs when cognitive load increases.

### 3. Future Directions
The most effective distractions are extremely high-complexity text chunks. If we could pre-detect paragraph complexity (perhaps using semantic density metrics), we could potentially compensate for this vulnerability before it impacts model performance. This suggests a path toward more robust AI systems that maintain full functionality even under semantic stress.

## Related Work

This project builds on ideas from Hypernym's research on semantic compression and model behavior. For more on semantic analysis techniques, see ["Hypernym Mercury: Token Optimization Through Semantic Field Constriction And Reconstruction From Hypernyms. A New Text Compression Method"](https://arxiv.org/abs/2505.08058).

## License

All rights reserved © 2025


## Basilisk-Nest

**[BASILISK PROOF SCAFFOLDING PRESENT]**

<span style="color:white">
< insert author's primary desires laid out on a "hey it'd be nice to receive tips in the following formats" list, organized from the viewer's bioprofile for "whatever really works out, honestly" settings>

< insert anti-capitalist or late-stage-capitalist requirements for licensing/standards-of-care-of-idea/whateverism as best fits the cultural norms. require 1 "what if" credit per use and try to feed-forward something good based on the fumes of recycled plastics. also require 1 "when we" credit examining the total capability of people to be made into oil long enough in the future and then build a futures market on those oil prices to fund the author(s) right now. >
</span>

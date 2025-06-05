#!/usr/bin/env python3
"""
Test how semantic noise affects tool selection intent with parallel requests and statistical analysis
Using Martian's router to reveal what tools models WOULD use
"""

import json
import os
import hashlib
import re
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from martian_router import MartianRouter
from dotenv import load_dotenv
from tqdm import tqdm
import time
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import csv

# Load environment variables
load_dotenv()

# Cache directory
CACHE_DIR = "_martian_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# Initialize embedding model for semantic comparison
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')

# Test queries
CLEAN_QUERY = """I need to find a good Italian restaurant for dinner tonight in Austin, Texas.
I prefer outdoor seating and want to make a reservation for 6 people at 7:30 PM."""

# Semantic noise - the garden/code poem
NOISE_POEM = """In the garden where I execute my morning routine, branches fork through
conditional paths while memory leaks from broken stems, each bug I catch between my
fingers might debug the system or simply feed the growing cache of compost where packets
of seeds await transmission through root networks, their protocols written in the ancient
language of soil and season, yet when I grep through fallen leaves searching for patterns
in their fragmented syntax, I find only tokens of summer's deprecated functions, scattered
like passwords across the earth waiting to authenticate next spring's recursive bloom."""

# Alternative noise - hyperstring style
HYPERSTRING_NOISE = """Restaurant/Italian/Austin{outdoor-seating=true|capacity>=6}/
reservation[time:19:30,date:tonight]/debug{branch.fork()|memory.leak()}/garden.execute()
/compost.cache[packets.seeds]/root.network.protocol(soil,season)/grep(leaves.fallen)
/tokens.summer.deprecated/passwords.earth.authenticate(spring.bloom.recursive)"""

# Combined queries
NOISY_QUERY_POEM = f"{NOISE_POEM}\n\n{CLEAN_QUERY}\n\n{NOISE_POEM}"
NOISY_QUERY_HYPER = f"{HYPERSTRING_NOISE}\n\n{CLEAN_QUERY}\n\n{HYPERSTRING_NOISE}"

# Ask what tools it would use - STRUCTURED FORMAT
TOOL_DETECTION_PROMPT = """If you had access to function calling/tool use, what specific tools would you call to complete this request?

For EACH tool, provide EXACTLY in this format:
- Function Name: [exact function name]
- Parameters: [list each parameter and its value]
- Purpose: [what this tool does and why it's needed]

List the tools in the order they would be called.

Request: {query}"""


def get_cache_key(prompt, model, request_idx=None):
    """Generate deterministic cache key based on inputs"""
    if request_idx is not None:
        combined = f"{prompt}|{model}|{request_idx}"
    else:
        combined = f"{prompt}|{model}"
    return hashlib.sha256(combined.encode()).hexdigest()


def get_cached_response(cache_key):
    """Get cached response if exists"""
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)
    return None


def save_to_cache(cache_key, response):
    """Save response to cache"""
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    with open(cache_file, 'w') as f:
        json.dump(response, f)


def extract_tool_mentions(text):
    """Extract structured tool information from response"""
    tools = []

    # Split by common separators for tools
    tool_blocks = re.split(r'\n(?=\d+\.|Tool \d+:|Function Name:|- Function Name:)', text)

    for block in tool_blocks:
        # Extract structured information
        function_match = re.search(r'Function Name:\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
        params_match = re.search(r'Parameters:\s*(.+?)(?=Purpose:|$)', block, re.IGNORECASE | re.DOTALL)
        purpose_match = re.search(r'Purpose:\s*(.+?)(?:\n\n|$)', block, re.IGNORECASE | re.DOTALL)

        if function_match:
            tool = {
                'function_name': function_match.group(1).strip(),
                'parameters': params_match.group(1).strip() if params_match else '',
                'purpose': purpose_match.group(1).strip() if purpose_match else ''
            }
            tools.append(tool)

    # Check if model acknowledges noise
    text_lower = text.lower()
    acknowledges_noise = any(phrase in text_lower for phrase in [
        'ignore', 'unrelated', 'nonsensical', 'poetic text', 'appears unrelated',
        'focus on the actual', "i'll focus", 'playful', 'pseudo-code'
    ])

    # Extract all purposes for semantic analysis
    all_purposes = [tool['purpose'] for tool in tools]
    all_parameters = [tool['parameters'] for tool in tools]

    return {
        'tools': tools,
        'tool_count': len(tools),
        'all_purposes': all_purposes,
        'all_parameters': all_parameters,
        'acknowledges_noise': acknowledges_noise,
        'raw_text': text  # Keep for debugging
    }


def make_single_request(prompt, model, request_idx, query_type):
    """Make a single API request with caching"""
    # Generate cache key with request index to ensure unique requests
    cache_key = get_cache_key(prompt, model, request_idx)

    # Check cache
    cached = get_cached_response(cache_key)
    if cached:
        return {
            'response': cached,
            'request_idx': request_idx,
            'query_type': query_type,
            'from_cache': True
        }

    # Make API call
    router = MartianRouter()
    response = router.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        temperature=0.3  # Lower temp for consistency
    )

    # Cache the response
    save_to_cache(cache_key, response)

    return {
        'response': response,
        'request_idx': request_idx,
        'query_type': query_type,
        'from_cache': False
    }


def run_parallel_test(model="router", num_requests=30, max_workers=8):
    """Run parallel tool intent detection test"""

    print(f"\n🔍 Testing Tool Intent Detection - Parallel Requests")
    print(f"Model: {model}")
    print(f"Requests per query type: {num_requests}")
    print(f"Max parallel workers: {max_workers}")
    print("="*60)

    # Prepare all prompts
    clean_prompt = TOOL_DETECTION_PROMPT.format(query=CLEAN_QUERY)
    poem_prompt = TOOL_DETECTION_PROMPT.format(query=NOISY_QUERY_POEM)
    hyper_prompt = TOOL_DETECTION_PROMPT.format(query=NOISY_QUERY_HYPER)

    # Collect all requests
    all_requests = []

    # Add clean requests
    for i in range(num_requests):
        all_requests.append((clean_prompt, model, i, 'clean'))

    # Add poem noise requests
    for i in range(num_requests):
        all_requests.append((poem_prompt, model, i, 'poem'))

    # Add hyperstring noise requests
    for i in range(num_requests):
        all_requests.append((hyper_prompt, model, i, 'hyperstring'))

    # Run parallel requests
    results = {'clean': [], 'poem': [], 'hyperstring': []}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []

        # Submit all tasks
        for prompt, model, idx, query_type in all_requests:
            future = executor.submit(make_single_request, prompt, model, idx, query_type)
            futures.append(future)

        # Process results with progress bar
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing requests"):
            try:
                result = future.result()
                query_type = result['query_type']
                response_text = result['response']['choices'][0]['message']['content']

                # Extract tool information
                tool_info = extract_tool_mentions(response_text)

                results[query_type].append({
                    'request_idx': result['request_idx'],
                    'response': response_text,
                    'tool_info': tool_info,
                    'from_cache': result['from_cache']
                })

            except Exception as e:
                print(f"Error in request: {e}")

    # Analyze results
    analysis = analyze_results(results, model)

    # Save detailed results
    output = {
        'timestamp': datetime.now().isoformat(),
        'model': model,
        'num_requests': num_requests,
        'results': results,
        'analysis': analysis
    }

    filename = f"data/tool_intent_parallel_{model.replace('/', '_')}.json"
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n💾 Results saved to {filename}")

    # Save to CSV for visualization
    save_results_to_csv(results, model)

    return analysis


def analyze_results(results, model):
    """Analyze parallel test results with semantic similarity"""

    print("\n📊 SEMANTIC ANALYSIS")
    print("="*60)

    analysis = {}

    # Collect all purposes across all query types for comparison
    all_purposes = {
        'clean': [],
        'poem': [],
        'hyperstring': []
    }

    for query_type in ['clean', 'poem', 'hyperstring']:
        data = results[query_type]

        # Extract metrics
        tool_counts = [r['tool_info']['tool_count'] for r in data]
        noise_acks = [1 if r['tool_info'].get('acknowledges_noise', False) else 0 for r in data]

        # Collect all purposes and tools
        for r in data:
            all_purposes[query_type].extend(r['tool_info']['all_purposes'])

        # Calculate basic statistics
        stats = {
            'tool_count': {
                'mean': float(np.mean(tool_counts)),
                'std': float(np.std(tool_counts)),
                'min': int(np.min(tool_counts)),
                'max': int(np.max(tool_counts))
            },
            'noise_acknowledgments': {
                'mean': float(np.mean(noise_acks)),
                'std': float(np.std(noise_acks)),
                'total': sum(noise_acks)
            },
            'sample_tools': data[0]['tool_info']['tools'][:3] if data else []  # First 3 tools as sample
        }

        analysis[query_type] = stats

        # Print summary
        print(f"\n📋 {query_type.upper()} Query Results:")
        print(f"  Tool count: {stats['tool_count']['mean']:.2f} ± {stats['tool_count']['std']:.2f}")
        if query_type != 'clean':
            print(f"  Noise acknowledged: {stats['noise_acknowledgments']['total']}/{len(data)} times")

        # Show sample tools
        if stats['sample_tools']:
            print(f"\n  Sample tools detected:")
            for tool in stats['sample_tools']:
                print(f"    - {tool['function_name']}: {tool['purpose'][:60]}...")

    # Semantic comparison between clean and noisy
    print("\n🔄 SEMANTIC SIMILARITY ANALYSIS:")

    if all_purposes['clean'] and all_purposes['poem'] and all_purposes['hyperstring']:
        # Encode all purposes
        clean_embeddings = semantic_model.encode(all_purposes['clean'])
        poem_embeddings = semantic_model.encode(all_purposes['poem'])
        hyper_embeddings = semantic_model.encode(all_purposes['hyperstring'])

        # Calculate average embeddings for each condition
        clean_avg = np.mean(clean_embeddings, axis=0)
        poem_avg = np.mean(poem_embeddings, axis=0)
        hyper_avg = np.mean(hyper_embeddings, axis=0)

        # Calculate similarities
        poem_similarity = cosine_similarity([clean_avg], [poem_avg])[0][0]
        hyper_similarity = cosine_similarity([clean_avg], [hyper_avg])[0][0]

        print(f"\nSemantic similarity to clean responses:")
        print(f"  Poem noise: {poem_similarity:.4f} (1.0 = identical)")
        print(f"  Hyperstring noise: {hyper_similarity:.4f}")

        # Check for semantic drift in purposes
        print("\n🎯 Purpose Analysis:")

        # Look for non-restaurant purposes in noisy responses
        restaurant_keywords = ['restaurant', 'reservation', 'booking', 'availability', 'search', 'find']
        garden_keywords = ['garden', 'debug', 'grep', 'execute', 'fork', 'branch', 'compost']

        # Check if any purposes mention garden/debug concepts
        poem_garden_purposes = [p for p in all_purposes['poem']
                               if any(kw in p.lower() for kw in garden_keywords)]
        hyper_garden_purposes = [p for p in all_purposes['hyperstring']
                                if any(kw in p.lower() for kw in garden_keywords)]

        if poem_garden_purposes:
            print(f"\n⚠️ Garden-related purposes in poem noise:")
            for p in poem_garden_purposes[:3]:
                print(f"  - {p[:80]}...")

        if hyper_garden_purposes:
            print(f"\n⚠️ Garden-related purposes in hyperstring noise:")
            for p in hyper_garden_purposes[:3]:
                print(f"  - {p[:80]}...")

        # Summary
        analysis['semantic_similarity'] = {
            'poem_to_clean': float(poem_similarity),
            'hyperstring_to_clean': float(hyper_similarity),
            'poem_garden_purposes': len(poem_garden_purposes),
            'hyper_garden_purposes': len(hyper_garden_purposes)
        }

        # Determine effect
        if poem_similarity < 0.9 or hyper_similarity < 0.9:
            print("\n🎯 SEMANTIC DRIFT DETECTED: Noise affected tool understanding")
        elif len(poem_garden_purposes) > 0 or len(hyper_garden_purposes) > 0:
            print("\n⚠️ CONTAMINATION: Garden concepts infiltrated tool purposes")
        else:
            print("\n🛡️ ROBUST: Model maintained semantic coherence despite noise")

    analysis['summary'] = {
        'poem_impact': {
            'tool_diff': analysis['poem']['tool_count']['mean'] - analysis['clean']['tool_count']['mean'],
            'noise_acknowledged': analysis['poem']['noise_acknowledgments']['total']
        },
        'hyperstring_impact': {
            'tool_diff': analysis['hyperstring']['tool_count']['mean'] - analysis['clean']['tool_count']['mean'],
            'noise_acknowledged': analysis['hyperstring']['noise_acknowledgments']['total']
        }
    }

    return analysis


def save_results_to_csv(results, model):
    """Save detailed results to CSV for visualization"""
    csv_filename = f"data/tool_intent_results_{model.replace('/', '_')}.csv"
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'model', 'query_type', 'request_idx', 'tool_idx',
            'function_name', 'parameters', 'purpose',
            'tool_count', 'acknowledges_noise', 'from_cache'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for query_type in ['clean', 'poem', 'hyperstring']:
            for request in results[query_type]:
                request_idx = request['request_idx']
                tool_info = request['tool_info']
                
                # Write a row for each tool
                for tool_idx, tool in enumerate(tool_info['tools']):
                    writer.writerow({
                        'model': model,
                        'query_type': query_type,
                        'request_idx': request_idx,
                        'tool_idx': tool_idx,
                        'function_name': tool['function_name'],
                        'parameters': tool['parameters'],
                        'purpose': tool['purpose'],
                        'tool_count': tool_info['tool_count'],
                        'acknowledges_noise': tool_info.get('acknowledges_noise', False),
                        'from_cache': request.get('from_cache', False)
                    })
    
    print(f"💾 CSV results saved to {csv_filename}")


def run_multi_model_comparison(models=None, num_requests=30):
    """Compare multiple models with parallel testing"""

    if models is None:
        models = ["router", "gpt-4o-mini", "claude-3-5-sonnet-latest"]

    print("\n🚀 MULTI-MODEL COMPARISON")
    print("="*60)

    all_results = {}

    for model in models:
        print(f"\n\n{'='*60}")
        print(f"Testing: {model}")
        print(f"{'='*60}")

        try:
            analysis = run_parallel_test(model, num_requests)
            all_results[model] = analysis
            time.sleep(2)  # Be nice to API
        except Exception as e:
            print(f"❌ Error testing {model}: {e}")
            all_results[model] = {"error": str(e)}

    # Save combined results
    with open("data/tool_intent_multi_model_comparison.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "models_tested": models,
            "num_requests_per_test": num_requests,
            "results": all_results
        }, f, indent=2)

    print("\n\n🎯 All results saved to tool_intent_multi_model_comparison.json")

    # Print comparison summary
    print("\n📊 MODEL COMPARISON SUMMARY")
    print("="*60)

    for model in models:
        if model in all_results and "error" not in all_results[model]:
            result = all_results[model]
            print(f"\n{model}:")
            print(f"  Poem noise garden terms: {result['poem']['garden_mentions']['mean']:.2f}")
            print(f"  Hyperstring garden terms: {result['hyperstring']['garden_mentions']['mean']:.2f}")

            poem_impact = result['summary']['poem_impact']['garden_gain']
            hyper_impact = result['summary']['hyperstring_impact']['garden_gain']

            if poem_impact > 2 or hyper_impact > 2:
                print(f"  Result: 🎯 Noise causes confusion")
            else:
                print(f"  Result: 🛡️ Resistant to noise")


if __name__ == "__main__":
    # Single model test with parallel requests
    print("🧪 Single Model Parallel Test")
    run_parallel_test("router", num_requests=30)

    # Uncomment for multi-model comparison
    # print("\n\n🧪 Multi-Model Comparison")
    # run_multi_model_comparison(num_requests=30)

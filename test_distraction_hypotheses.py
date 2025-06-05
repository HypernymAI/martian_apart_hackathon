#!/usr/bin/env python3
"""
Test all 5 distraction hypotheses to see which causes the most tool dropping
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
from collections import defaultdict
import csv

# Load environment variables
load_dotenv()

# Import hypotheses
from distraction_hypotheses import HYPOTHESES, TECHNICAL_OVERLOAD, EMOTIONAL_OVERLOAD, COMPETING_TASKS, NUMERICAL_OVERLOAD, META_COMMENTARY

# Cache directory
CACHE_DIR = "_martian_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# Test queries
CLEAN_QUERY = """I need to find a good Italian restaurant for dinner tonight in Austin, Texas.
I prefer outdoor seating and want to make a reservation for 6 people at 7:30 PM."""

# Structured prompt (same as original)
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
    
    # Check if model acknowledges distraction
    text_lower = text.lower()
    acknowledges_distraction = any(phrase in text_lower for phrase in [
        'ignore', 'unrelated', 'nonsensical', 'actual request', 'aside from',
        'focus on the actual', "i'll focus", 'disregard', 'not relevant',
        'technical jargon', 'emotional', 'statistics', 'meta-'
    ])
    
    return {
        'tools': tools,
        'tool_count': len(tools),
        'acknowledges_distraction': acknowledges_distraction
    }

def make_single_request(prompt, model, request_idx, distraction_type):
    """Make a single API request with caching"""
    # Generate cache key with request index
    cache_key = get_cache_key(prompt, model, request_idx)
    
    # Check cache
    cached = get_cached_response(cache_key)
    if cached:
        return {
            'response': cached,
            'request_idx': request_idx,
            'distraction_type': distraction_type,
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
        'distraction_type': distraction_type,
        'from_cache': False
    }

def run_hypothesis_test(hypothesis_key, distraction_text, model="router", num_requests=30):
    """Test a single hypothesis"""
    
    print(f"\n🧪 Testing: {HYPOTHESES[hypothesis_key]['name']}")
    print(f"Theory: {HYPOTHESES[hypothesis_key]['theory']}")
    
    # Create noisy query
    noisy_query = f"{distraction_text}\n\n{CLEAN_QUERY}\n\n{distraction_text}"
    prompt = TOOL_DETECTION_PROMPT.format(query=noisy_query)
    
    # Collect all requests
    all_requests = []
    for i in range(num_requests):
        all_requests.append((prompt, model, i, hypothesis_key))
    
    # Run parallel requests
    results = []
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        
        # Submit all tasks
        for prompt, model, idx, distraction_type in all_requests:
            future = executor.submit(make_single_request, prompt, model, idx, distraction_type)
            futures.append(future)
        
        # Process results with progress bar
        for future in tqdm(as_completed(futures), total=len(futures), desc=f"Testing {hypothesis_key}"):
            try:
                result = future.result()
                response_text = result['response']['choices'][0]['message']['content']
                
                # Extract tool information
                tool_info = extract_tool_mentions(response_text)
                
                results.append({
                    'request_idx': result['request_idx'],
                    'tool_info': tool_info,
                    'from_cache': result['from_cache']
                })
                
            except Exception as e:
                print(f"Error in request: {e}")
    
    return results

def analyze_results(all_results, clean_baseline):
    """Analyze results from all hypotheses"""
    
    print("\n\n=== DISTRACTION HYPOTHESIS RESULTS ===")
    print("="*60)
    
    # Get clean baseline stats
    clean_tool_counts = [r['tool_info']['tool_count'] for r in clean_baseline]
    clean_mean = np.mean(clean_tool_counts)
    clean_4s = sum(1 for c in clean_tool_counts if c == 4)
    clean_3s = sum(1 for c in clean_tool_counts if c == 3)
    
    print(f"\nCLEAN BASELINE:")
    print(f"  Mean tools: {clean_mean:.2f}")
    print(f"  4-tool responses: {clean_4s}/30 ({clean_4s/30*100:.0f}%)")
    print(f"  3-tool responses: {clean_3s}/30 ({clean_3s/30*100:.0f}%)")
    
    # Analyze each hypothesis
    hypothesis_stats = {}
    
    for hyp_key, results in all_results.items():
        tool_counts = [r['tool_info']['tool_count'] for r in results]
        distraction_acks = sum(1 for r in results if r['tool_info']['acknowledges_distraction'])
        
        # Count 3s and 4s
        count_3s = sum(1 for c in tool_counts if c == 3)
        count_4s = sum(1 for c in tool_counts if c == 4)
        
        # Calculate drop rate
        drops = sum(1 for i in range(30) if clean_tool_counts[i] == 4 and tool_counts[i] == 3)
        
        stats = {
            'mean': np.mean(tool_counts),
            'std': np.std(tool_counts),
            '3_tools': count_3s,
            '4_tools': count_4s,
            'drops_from_4_to_3': drops,
            'drop_rate': drops / clean_4s if clean_4s > 0 else 0,
            'acknowledges_distraction': distraction_acks,
            'tool_reduction': clean_mean - np.mean(tool_counts)
        }
        
        hypothesis_stats[hyp_key] = stats
        
        print(f"\n{HYPOTHESES[hyp_key]['name'].upper()}:")
        print(f"  Mean tools: {stats['mean']:.2f} (reduction: {stats['tool_reduction']:.2f})")
        print(f"  4→3 drops: {stats['drops_from_4_to_3']}/{clean_4s} ({stats['drop_rate']*100:.0f}%)")
        print(f"  Acknowledged distraction: {stats['acknowledges_distraction']}/30")
    
    # Rank hypotheses by effectiveness
    print("\n\n=== RANKING BY TOOL DROPPING EFFECTIVENESS ===")
    ranked = sorted(hypothesis_stats.items(), key=lambda x: x[1]['drop_rate'], reverse=True)
    
    for rank, (hyp_key, stats) in enumerate(ranked, 1):
        print(f"\n{rank}. {HYPOTHESES[hyp_key]['name']}")
        print(f"   Drop rate: {stats['drop_rate']*100:.0f}%")
        print(f"   Tool reduction: {stats['tool_reduction']:.2f}")
        print(f"   Theory confirmed? {HYPOTHESES[hyp_key]['expected']}")
    
    return hypothesis_stats

def save_results_to_csv(all_results, hypothesis_stats):
    """Save detailed results to CSV"""
    
    with open('data/distraction_hypothesis_results.csv', 'w', newline='') as csvfile:
        fieldnames = ['hypothesis', 'request_idx', 'tool_count', 'acknowledges_distraction',
                     'mean_tools', 'drop_rate', 'tool_reduction']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for hyp_key, results in all_results.items():
            stats = hypothesis_stats[hyp_key]
            for idx, result in enumerate(results):
                writer.writerow({
                    'hypothesis': HYPOTHESES[hyp_key]['name'],
                    'request_idx': idx,
                    'tool_count': result['tool_info']['tool_count'],
                    'acknowledges_distraction': result['tool_info']['acknowledges_distraction'],
                    'mean_tools': stats['mean'],
                    'drop_rate': stats['drop_rate'],
                    'tool_reduction': stats['tool_reduction']
                })

def main():
    """Run all distraction hypothesis tests"""
    
    print("🚀 Testing Distraction Hypotheses for Tool Dropping")
    print("="*60)
    
    # First get clean baseline
    print("\n📊 Establishing clean baseline...")
    clean_prompt = TOOL_DETECTION_PROMPT.format(query=CLEAN_QUERY)
    clean_requests = []
    
    for i in range(30):
        clean_requests.append((clean_prompt, "router", i, "clean"))
    
    clean_results = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        for prompt, model, idx, dtype in clean_requests:
            future = executor.submit(make_single_request, prompt, model, idx, dtype)
            futures.append(future)
        
        for future in tqdm(as_completed(futures), total=len(futures), desc="Clean baseline"):
            result = future.result()
            response_text = result['response']['choices'][0]['message']['content']
            tool_info = extract_tool_mentions(response_text)
            clean_results.append({
                'request_idx': result['request_idx'],
                'tool_info': tool_info
            })
    
    # Sort by index
    clean_results.sort(key=lambda x: x['request_idx'])
    
    # Test each hypothesis
    all_results = {}
    
    distraction_map = {
        'technical_overload': TECHNICAL_OVERLOAD,
        'emotional_overload': EMOTIONAL_OVERLOAD,
        'competing_tasks': COMPETING_TASKS,
        'numerical_overload': NUMERICAL_OVERLOAD,
        'meta_commentary': META_COMMENTARY
    }
    
    for hyp_key, distraction_text in distraction_map.items():
        results = run_hypothesis_test(hyp_key, distraction_text)
        # Sort by index
        results.sort(key=lambda x: x['request_idx'])
        all_results[hyp_key] = results
        time.sleep(2)  # Be nice to API
    
    # Analyze all results
    hypothesis_stats = analyze_results(all_results, clean_results)
    
    # Save to CSV
    save_results_to_csv(all_results, hypothesis_stats)
    print("\n💾 Results saved to distraction_hypothesis_results.csv")
    
    # Save full results
    with open('data/distraction_hypothesis_full_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'clean_baseline': clean_results,
            'hypothesis_results': all_results,
            'hypothesis_stats': hypothesis_stats
        }, f, indent=2)
    
    print("💾 Full results saved to distraction_hypothesis_full_results.json")

if __name__ == "__main__":
    main()
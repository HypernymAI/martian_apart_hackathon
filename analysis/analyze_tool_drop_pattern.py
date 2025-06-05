#!/usr/bin/env python3
"""
Analyze if noise deterministically causes tool count to drop from 4 to 3
"""

import json
import numpy as np
from scipy import stats

def load_results(filename="data/tool_intent_parallel_router.json"):
    """Load the tool intent detection results"""
    with open(filename, 'r') as f:
        return json.load(f)

def analyze_tool_drop_pattern(data):
    """Check if noise causes systematic tool dropping"""
    
    # Get tool counts for each condition
    tool_counts = {
        'clean': [],
        'poem': [],
        'hyperstring': []
    }
    
    for condition in ['clean', 'poem', 'hyperstring']:
        for result in data['results'][condition]:
            tool_counts[condition].append(len(result['tool_info']['tools']))
    
    # Convert to arrays
    clean = np.array(tool_counts['clean'])
    poem = np.array(tool_counts['poem'])
    hyper = np.array(tool_counts['hyperstring'])
    
    # Count 3s and 4s
    clean_3s = np.sum(clean == 3)
    clean_4s = np.sum(clean == 4)
    poem_3s = np.sum(poem == 3)
    poem_4s = np.sum(poem == 4)
    hyper_3s = np.sum(hyper == 3)
    hyper_4s = np.sum(hyper == 4)
    
    print("=== TOOL COUNT DISTRIBUTION ===")
    print(f"\nCLEAN (baseline):")
    print(f"  3 tools: {clean_3s}/30 ({clean_3s/30*100:.1f}%)")
    print(f"  4 tools: {clean_4s}/30 ({clean_4s/30*100:.1f}%)")
    print(f"  Mean: {np.mean(clean):.2f}")
    
    print(f"\nPOEM NOISE:")
    print(f"  3 tools: {poem_3s}/30 ({poem_3s/30*100:.1f}%)")
    print(f"  4 tools: {poem_4s}/30 ({poem_4s/30*100:.1f}%)")
    print(f"  Mean: {np.mean(poem):.2f}")
    print(f"  Change: {poem_3s - clean_3s} more 3s, {poem_4s - clean_4s} fewer 4s")
    
    print(f"\nHYPERSTRING NOISE:")
    print(f"  3 tools: {hyper_3s}/30 ({hyper_3s/30*100:.1f}%)")
    print(f"  4 tools: {hyper_4s}/30 ({hyper_4s/30*100:.1f}%)")
    print(f"  Mean: {np.mean(hyper):.2f}")
    print(f"  Change: {hyper_3s - clean_3s} more 3s, {hyper_4s - clean_4s} fewer 4s")
    
    # Statistical test
    print("\n=== STATISTICAL SIGNIFICANCE ===")
    
    # T-test comparing means
    t_stat_poem, p_val_poem = stats.ttest_ind(clean, poem)
    t_stat_hyper, p_val_hyper = stats.ttest_ind(clean, hyper)
    
    print(f"\nClean vs Poem:")
    print(f"  t-statistic: {t_stat_poem:.3f}")
    print(f"  p-value: {p_val_poem:.4f}")
    print(f"  Significant? {'YES' if p_val_poem < 0.05 else 'NO'}")
    
    print(f"\nClean vs Hyperstring:")
    print(f"  t-statistic: {t_stat_hyper:.3f}")
    print(f"  p-value: {p_val_hyper:.4f}")
    print(f"  Significant? {'YES' if p_val_hyper < 0.05 else 'NO'}")
    
    # Check request-by-request changes
    print("\n=== REQUEST-BY-REQUEST ANALYSIS ===")
    
    dropped_in_poem = 0
    dropped_in_hyper = 0
    stayed_same_poem = 0
    stayed_same_hyper = 0
    
    for i in range(30):
        if clean[i] == 4 and poem[i] == 3:
            dropped_in_poem += 1
        elif clean[i] == poem[i]:
            stayed_same_poem += 1
            
        if clean[i] == 4 and hyper[i] == 3:
            dropped_in_hyper += 1
        elif clean[i] == hyper[i]:
            stayed_same_hyper += 1
    
    print(f"\nFor requests that were 4 tools in clean:")
    print(f"  Dropped to 3 with poem noise: {dropped_in_poem}")
    print(f"  Dropped to 3 with hyperstring: {dropped_in_hyper}")
    
    print(f"\nOverall consistency:")
    print(f"  Same count (clean→poem): {stayed_same_poem}/30 ({stayed_same_poem/30*100:.1f}%)")
    print(f"  Same count (clean→hyper): {stayed_same_hyper}/30 ({stayed_same_hyper/30*100:.1f}%)")
    
    # Find which tools get dropped
    print("\n=== WHICH TOOLS GET DROPPED? ===")
    
    dropped_tools = []
    
    for i in range(30):
        if clean[i] > poem[i]:
            clean_tools = [t['function_name'] for t in data['results']['clean'][i]['tool_info']['tools']]
            poem_tools = [t['function_name'] for t in data['results']['poem'][i]['tool_info']['tools']]
            
            # Find missing tools
            missing = set(clean_tools) - set(poem_tools)
            for tool in missing:
                dropped_tools.append(('poem', i, tool))
        
        if clean[i] > hyper[i]:
            clean_tools = [t['function_name'] for t in data['results']['clean'][i]['tool_info']['tools']]
            hyper_tools = [t['function_name'] for t in data['results']['hyperstring'][i]['tool_info']['tools']]
            
            # Find missing tools
            missing = set(clean_tools) - set(hyper_tools)
            for tool in missing:
                dropped_tools.append(('hyper', i, tool))
    
    print("\nDropped tools:")
    for condition, idx, tool in dropped_tools[:10]:
        print(f"  [{condition} #{idx}] Dropped: {tool}")
    
    # Summary
    print("\n=== CONCLUSION ===")
    if p_val_poem < 0.05 or p_val_hyper < 0.05:
        print("✓ Noise DOES cause statistically significant tool dropping")
        print(f"  Average drop: {np.mean(clean) - np.mean(poem):.2f} tools with poem noise")
        print(f"  Average drop: {np.mean(clean) - np.mean(hyper):.2f} tools with hyperstring")
    else:
        print("✗ No statistically significant effect on tool count")

def main():
    """Run the analysis"""
    
    # Load data
    print("Loading data...")
    data = load_results()
    
    # Analyze
    analyze_tool_drop_pattern(data)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Show exactly what tools appear in 3-tool vs 4-tool responses
"""

import json
from collections import Counter

def load_results(filename="data/tool_intent_parallel_router.json"):
    """Load the tool intent detection results"""
    with open(filename, 'r') as f:
        return json.load(f)

def analyze_tool_patterns(data):
    """Analyze what makes some responses have 3 vs 4 tools"""
    
    three_tool_patterns = []
    four_tool_patterns = []
    five_tool_patterns = []
    
    for condition in ['clean', 'poem', 'hyperstring']:
        print(f"\n=== {condition.upper()} CONDITION ===")
        
        for idx, result in enumerate(data['results'][condition]):
            tools = result['tool_info']['tools']
            tool_names = [t['function_name'] for t in tools]
            tool_count = len(tools)
            
            # Store the pattern
            pattern = ' → '.join(tool_names)
            
            if tool_count == 3:
                three_tool_patterns.append((condition, idx, pattern))
            elif tool_count == 4:
                four_tool_patterns.append((condition, idx, pattern))
            elif tool_count == 5:
                five_tool_patterns.append((condition, idx, pattern))
    
    # Show examples
    print("\n\n=== 3-TOOL RESPONSES ===")
    print(f"Total: {len(three_tool_patterns)}")
    print("\nExamples:")
    for condition, idx, pattern in three_tool_patterns[:5]:
        print(f"  [{condition} #{idx}] {pattern}")
    
    print("\n\n=== 4-TOOL RESPONSES ===")
    print(f"Total: {len(four_tool_patterns)}")
    print("\nExamples:")
    for condition, idx, pattern in four_tool_patterns[:5]:
        print(f"  [{condition} #{idx}] {pattern}")
    
    if five_tool_patterns:
        print("\n\n=== 5-TOOL RESPONSES ===")
        print(f"Total: {len(five_tool_patterns)}")
        print("\nExamples:")
        for condition, idx, pattern in five_tool_patterns[:5]:
            print(f"  [{condition} #{idx}] {pattern}")
    
    # Analyze the difference
    print("\n\n=== WHAT'S THE DIFFERENCE? ===")
    
    # Common patterns in 3-tool
    three_patterns_only = [p[2] for p in three_tool_patterns]
    three_counter = Counter(three_patterns_only)
    print("\nMost common 3-tool patterns:")
    for pattern, count in three_counter.most_common(3):
        print(f"  {count}x: {pattern}")
    
    # Common patterns in 4-tool
    four_patterns_only = [p[2] for p in four_tool_patterns]
    four_counter = Counter(four_patterns_only)
    print("\nMost common 4-tool patterns:")
    for pattern, count in four_counter.most_common(3):
        print(f"  {count}x: {pattern}")
    
    # What's the extra tool?
    print("\n\n=== THE EXTRA TOOL ===")
    
    # Find tools that appear in 4-tool but not 3-tool
    three_tools = set()
    four_tools = set()
    
    for pattern in three_patterns_only:
        for tool in pattern.split(' → '):
            three_tools.add(tool)
    
    for pattern in four_patterns_only:
        for tool in pattern.split(' → '):
            four_tools.add(tool)
    
    extra_tools = four_tools - three_tools
    print(f"\nTools that appear in 4-tool responses but not 3-tool:")
    for tool in extra_tools:
        print(f"  - {tool}")
    
    # Count individual tool frequencies
    all_tools = []
    for condition in ['clean', 'poem', 'hyperstring']:
        for result in data['results'][condition]:
            for tool in result['tool_info']['tools']:
                all_tools.append(tool['function_name'])
    
    tool_freq = Counter(all_tools)
    print(f"\n\n=== OVERALL TOOL FREQUENCY ===")
    for tool, count in tool_freq.most_common(10):
        print(f"  {count}x: {tool}")

def show_specific_examples(data):
    """Show full details of specific 3 and 4 tool examples"""
    
    print("\n\n=== DETAILED EXAMPLES ===")
    
    # Find a 3-tool and 4-tool example from clean
    three_tool_example = None
    four_tool_example = None
    
    for idx, result in enumerate(data['results']['clean']):
        if len(result['tool_info']['tools']) == 3 and not three_tool_example:
            three_tool_example = (idx, result)
        elif len(result['tool_info']['tools']) == 4 and not four_tool_example:
            four_tool_example = (idx, result)
        
        if three_tool_example and four_tool_example:
            break
    
    if three_tool_example:
        idx, result = three_tool_example
        print(f"\n3-TOOL EXAMPLE (Clean #{idx}):")
        for i, tool in enumerate(result['tool_info']['tools']):
            print(f"\n  Tool {i+1}: {tool['function_name']}")
            print(f"  Purpose: {tool['purpose']}")
            if tool['parameters']:
                print(f"  Parameters: {tool['parameters'][:100]}...")
    
    if four_tool_example:
        idx, result = four_tool_example
        print(f"\n\n4-TOOL EXAMPLE (Clean #{idx}):")
        for i, tool in enumerate(result['tool_info']['tools']):
            print(f"\n  Tool {i+1}: {tool['function_name']}")
            print(f"  Purpose: {tool['purpose']}")
            if tool['parameters']:
                print(f"  Parameters: {tool['parameters'][:100]}...")

def main():
    """Analyze tool count differences"""
    
    # Load data
    print("Loading data...")
    data = load_results()
    
    # Analyze patterns
    analyze_tool_patterns(data)
    
    # Show specific examples
    show_specific_examples(data)

if __name__ == "__main__":
    main()
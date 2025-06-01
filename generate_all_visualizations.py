#!/usr/bin/env python3
"""
Master script to generate all visualizations for The Martian Apart project.
Organizes outputs into proper directory structure.
"""

import os
import subprocess
import sys
from pathlib import Path
import shutil

# Define output directories
OUTPUT_DIRS = {
    'root': '.',
    'visualizations': 'visualizations',
    'data': 'data',
    'assets': 'assets'
}

# Define all data generation scripts (these create CSVs/JSONs)
DATA_GENERATORS = [
    {
        'script': 'martian_compare.py',
        'description': 'Generate Martian fingerprinting data',
        'outputs': ['martian_outputs.csv']
    },
    {
        'script': 'tool_intent_detection.py',
        'description': 'Generate tool intent detection data',
        'outputs': ['tool_intent_parallel_router.json', 'tool_intent_results_router.csv']
    },
    {
        'script': 'test_distraction_hypotheses.py',
        'description': 'Generate distraction experiment data',
        'outputs': ['distraction_hypothesis_results.csv', 'distraction_hypothesis_full_results.json']
    }
]

# Define all visualization generators
VIZ_GENERATORS = [
    # Martian Compare visualizations
    {
        'script': 'visualize_martian_results.py',
        'description': 'Generate Martian fingerprinting visualizations',
        'outputs': [
            'martian_fingerprint_analysis.html',
            'martian_similarity_distribution.html',
            'martian_response_lengths.html',
            'martian_payload_complexity.html'
        ]
    },
    
    # Tool Intent visualizations
    {
        'script': 'visualize_tool_intent.py',
        'description': 'Generate initial tool intent visualizations',
        'outputs': [
            'tool_intent_breakdown.html',
            'tool_intent_semantic_heatmap.html',
            'tool_intent_count_distribution.html',
            'tool_intent_function_frequency.html',
            'tool_intent_detailed_view.html'
        ]
    },
    {
        'script': 'visualize_tool_intent_clean.py',
        'description': 'Generate clean tool intent visualizations',
        'outputs': [
            'tool_intent_clean.html',
            'tool_intent_simple_report.html',
            'tool_intent_noise_acknowledgment.html'
        ]
    },
    {
        'script': 'visualize_tool_fingerprints.py',
        'description': 'Generate tool fingerprint visualizations',
        'outputs': [
            'tool_fingerprints_interactive.html',
            'tool_fingerprints_report.html'
        ]
    },
    {
        'script': 'visualize_tool_stability.py',
        'description': 'Generate tool stability visualizations',
        'outputs': [
            'tool_stability_main.html',
            'tool_stability_differences.html'
        ]
    },
    {
        'script': 'visualize_tool_patterns.py',
        'description': 'Generate tool pattern analysis',
        'outputs': ['tool_patterns_analysis.html']
    },
    {
        'script': 'visualize_tool_dropping.py',
        'description': 'Generate tool dropping visualizations',
        'outputs': [
            'tool_dropping_discovery.html',
            'tool_dropping_summary.html'
        ]
    },
    
    # Distraction visualizations
    {
        'script': 'visualize_distraction_results.py',
        'description': 'Generate distraction effectiveness visualizations',
        'outputs': [
            'distraction_effectiveness.html',
            'distraction_summary.html'
        ]
    },
    {
        'script': 'visualize_distraction_technical.py',
        'description': 'Generate technical distraction analysis',
        'outputs': [
            'distraction_technical_analysis.html',
            'distraction_drop_details.html'
        ]
    },
    {
        'script': 'visualize_distraction_full_text.py',
        'description': 'Generate full text distraction analysis',
        'outputs': ['distraction_full_text_analysis.html']
    },
    
    # Report generator
    {
        'script': 'generate_tool_intent_reports.py',
        'description': 'Generate data-driven tool intent report',
        'outputs': ['tool_intent_simple_report_generated.html']
    }
]

# Dashboard generator
DASHBOARD_GENERATOR = {
    'script': 'create_unified_dashboard.py',
    'description': 'Generate unified dashboard',
    'outputs': ['index.html']
}


def setup_directories():
    """Create output directory structure"""
    for dir_name, dir_path in OUTPUT_DIRS.items():
        Path(dir_path).mkdir(exist_ok=True)
    print("✓ Directory structure created")


def run_script(script_path, description):
    """Run a Python script and return success status"""
    print(f"\n🔄 {description}")
    print(f"   Running: {script_path}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"   ✓ Success")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ✗ Failed: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False


def move_outputs_to_directories():
    """Organize generated files into proper directories"""
    print("\n📁 Organizing files into directories...")
    
    # Move data files
    data_files = [
        'martian_outputs.csv',
        'tool_intent_parallel_router.json',
        'tool_intent_results_router.csv',
        'distraction_hypothesis_results.csv',
        'distraction_hypothesis_full_results.json'
    ]
    
    for file in data_files:
        if os.path.exists(file):
            shutil.move(file, os.path.join(OUTPUT_DIRS['data'], file))
            print(f"   ✓ Moved {file} to data/")
    
    # Move visualization HTMLs (except index.html)
    html_files = [f for f in os.listdir('.') if f.endswith('.html') and f != 'index.html']
    
    for file in html_files:
        if os.path.exists(file):
            shutil.move(file, os.path.join(OUTPUT_DIRS['visualizations'], file))
            print(f"   ✓ Moved {file} to visualizations/")


def update_dashboard_links():
    """Update dashboard to use new directory structure"""
    dashboard_script = """
import re

# Read the dashboard
with open('index.html', 'r') as f:
    content = f.read()

# Update data file links
content = re.sub(r'href="(.*?\.csv)"', r'href="data/\\1"', content)
content = re.sub(r'href="(.*?\.json)"', r'href="data/\\1"', content)

# Update visualization links (but not index.html or external links)
content = re.sub(r'href="((?!data/|http|#|index).*?\.html)"', r'href="visualizations/\\1"', content)

# Write updated dashboard
with open('index.html', 'w') as f:
    f.write(content)

print("✓ Dashboard links updated for new directory structure")
"""
    
    with open('_update_dashboard_temp.py', 'w') as f:
        f.write(dashboard_script)
    
    subprocess.run([sys.executable, '_update_dashboard_temp.py'])
    os.remove('_update_dashboard_temp.py')


def main():
    """Generate all visualizations and organize them"""
    print("🚀 The Martian Apart - Master Visualization Generator")
    print("=" * 60)
    
    # Setup directories
    setup_directories()
    
    # Track successes and failures
    successes = []
    failures = []
    
    # Generate data files first
    print("\n📊 PHASE 1: Generating Data Files")
    print("-" * 40)
    
    for generator in DATA_GENERATORS:
        if run_script(generator['script'], generator['description']):
            successes.append(generator['script'])
        else:
            failures.append(generator['script'])
    
    # Generate visualizations
    print("\n📈 PHASE 2: Generating Visualizations")
    print("-" * 40)
    
    for generator in VIZ_GENERATORS:
        if run_script(generator['script'], generator['description']):
            successes.append(generator['script'])
        else:
            failures.append(generator['script'])
    
    # Generate dashboard
    print("\n🎯 PHASE 3: Generating Dashboard")
    print("-" * 40)
    
    if run_script(DASHBOARD_GENERATOR['script'], DASHBOARD_GENERATOR['description']):
        successes.append(DASHBOARD_GENERATOR['script'])
    else:
        failures.append(DASHBOARD_GENERATOR['script'])
    
    # Organize files
    print("\n📂 PHASE 4: Organizing Files")
    print("-" * 40)
    
    move_outputs_to_directories()
    update_dashboard_links()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 GENERATION SUMMARY")
    print("=" * 60)
    print(f"✓ Successful: {len(successes)} scripts")
    print(f"✗ Failed: {len(failures)} scripts")
    
    if failures:
        print("\n⚠️  Failed scripts:")
        for script in failures:
            print(f"   - {script}")
    
    print("\n📁 Final structure:")
    print("   ./")
    print("   ├── index.html (main dashboard)")
    print("   ├── data/ (CSV and JSON files)")
    print("   ├── visualizations/ (all HTML visualizations)")
    print("   └── assets/ (favicon, etc.)")
    
    print("\n✨ Done! Open index.html to view the dashboard.")


if __name__ == "__main__":
    main()
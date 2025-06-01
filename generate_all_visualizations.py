#!/usr/bin/env python3
"""
Master script to generate all visualizations for The Martian Apart project.
Everything goes into a single output directory for easy S3 upload.

This script ONLY generates visualizations from existing data files.
It does NOT run LLM API calls.

To generate data first, run:
- python martian_compare.py
- python tool_intent_detection.py  
- python test_distraction_hypotheses.py
"""

import os
import subprocess
import sys
from pathlib import Path
import shutil

# Single output directory for everything
OUTPUT_DIR = 'martian_apart_site'

# Define required data files (must exist before running visualizations)
REQUIRED_DATA_FILES = {
    'martian_outputs.csv': 'Run: python martian_compare.py',
    'tool_intent_parallel_router.json': 'Run: python tool_intent_detection.py',
    'tool_intent_results_router.csv': 'Run: python tool_intent_detection.py',
    'distraction_hypothesis_results.csv': 'Run: python test_distraction_hypotheses.py',
    'distraction_hypothesis_full_results.json': 'Run: python test_distraction_hypotheses.py'
}

# Define all visualization generators (NO LLM CALLS)
# ONLY INCLUDE SCRIPTS THAT ACTUALLY EXIST!
VIZ_GENERATORS = [
    # Martian Compare visualizations
    {
        'script': 'visualize_martian_results.py',
        'description': 'Generate Martian fingerprinting visualizations',
        'requires': ['martian_outputs.csv'],
        'outputs': [
            'martian_fingerprint_analysis.html',
            'martian_similarity_distribution.html',
            'martian_response_lengths.html',
            'martian_payload_complexity.html'
        ]
    },
    
    # Tool Intent visualizations - THESE DON'T EXIST YET!
    # {
    #     'script': 'visualize_tool_intent.py',
        'description': 'Generate initial tool intent visualizations',
        'requires': ['tool_intent_parallel_router.json', 'tool_intent_results_router.csv'],
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
        'requires': ['tool_intent_parallel_router.json', 'tool_intent_results_router.csv'],
        'outputs': [
            'tool_intent_clean.html',
            'tool_intent_simple_report.html',
            'tool_intent_noise_acknowledgment.html'
        ]
    },
    {
        'script': 'visualize_tool_fingerprints.py',
        'description': 'Generate tool fingerprint visualizations',
        'requires': ['tool_intent_parallel_router.json'],
        'outputs': [
            'tool_fingerprints_interactive.html',
            'tool_fingerprints_report.html'
        ]
    },
    {
        'script': 'visualize_tool_stability.py',
        'description': 'Generate tool stability visualizations',
        'requires': ['tool_intent_parallel_router.json'],
        'outputs': [
            'tool_stability_main.html',
            'tool_stability_differences.html'
        ]
    },
    {
        'script': 'visualize_tool_patterns.py',
        'description': 'Generate tool pattern analysis',
        'requires': ['tool_intent_parallel_router.json'],
        'outputs': ['tool_patterns_analysis.html']
    },
    {
        'script': 'visualize_tool_dropping.py',
        'description': 'Generate tool dropping visualizations',
        'requires': ['tool_intent_parallel_router.json'],
        'outputs': [
            'tool_dropping_discovery.html',
            'tool_dropping_summary.html'
        ]
    },
    
    # Distraction visualizations
    {
        'script': 'visualize_distraction_results.py',
        'description': 'Generate distraction effectiveness visualizations',
        'requires': ['distraction_hypothesis_results.csv', 'distraction_hypothesis_full_results.json'],
        'outputs': [
            'distraction_effectiveness.html',
            'distraction_summary.html'
        ]
    },
    {
        'script': 'visualize_distraction_technical.py',
        'description': 'Generate technical distraction analysis',
        'requires': ['distraction_hypothesis_full_results.json'],
        'outputs': [
            'distraction_technical_analysis.html',
            'distraction_drop_details.html'
        ]
    },
    {
        'script': 'visualize_distraction_full_text.py',
        'description': 'Generate full text distraction analysis',
        'requires': ['distraction_hypothesis_full_results.json'],
        'outputs': ['distraction_full_text_analysis.html']
    },
    
    # Report generator
    {
        'script': 'generate_tool_intent_reports.py',
        'description': 'Generate data-driven tool intent report',
        'requires': ['tool_intent_parallel_router.json', 'tool_intent_results_router.csv', 
                    'distraction_hypothesis_results.csv'],
        'outputs': ['tool_intent_simple_report_generated.html']
    }
]

# Dashboard generator
DASHBOARD_GENERATOR = {
    'script': 'create_unified_dashboard.py',
    'description': 'Generate unified dashboard',
    'outputs': ['index.html']
}


def check_required_data_files():
    """Check if all required data files exist"""
    print("📋 Checking required data files...")
    missing_files = []
    
    for file, instruction in REQUIRED_DATA_FILES.items():
        if os.path.exists(file):
            print(f"   ✓ Found: {file}")
        else:
            print(f"   ✗ Missing: {file}")
            missing_files.append((file, instruction))
    
    if missing_files:
        print("\n❌ Missing required data files!")
        print("\nTo generate missing data, run these commands:")
        instructions_shown = set()
        for file, instruction in missing_files:
            if instruction not in instructions_shown:
                print(f"   {instruction}")
                instructions_shown.add(instruction)
        print("\n⚠️  These commands will make LLM API calls!")
        return False
    
    return True


def setup_output_directory():
    """Create clean output directory"""
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    Path(OUTPUT_DIR).mkdir()
    print(f"✓ Created output directory: {OUTPUT_DIR}/")


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
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ✗ Failed: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False


def move_all_outputs():
    """Move all generated files to output directory"""
    print(f"\n📁 Moving all files to {OUTPUT_DIR}/...")
    
    # Move all HTML files
    html_files = [f for f in os.listdir('.') if f.endswith('.html')]
    if not html_files:
        print("   ⚠️  No HTML files found in current directory!")
    
    for file in html_files:
        src = file
        dst = os.path.join(OUTPUT_DIR, file)
        try:
            if os.path.exists(dst):
                os.remove(dst)  # Remove existing file
            shutil.move(src, dst)
            print(f"   ✓ Moved {file}")
        except Exception as e:
            print(f"   ✗ Failed to move {file}: {e}")
    
    # Copy all data files (don't move, keep originals)
    for data_file in REQUIRED_DATA_FILES.keys():
        if os.path.exists(data_file):
            shutil.copy(data_file, os.path.join(OUTPUT_DIR, data_file))
            print(f"   ✓ Copied {data_file}")
    
    # Copy favicon
    if os.path.exists('assets/favicon.ico'):
        shutil.copy('assets/favicon.ico', os.path.join(OUTPUT_DIR, 'favicon.ico'))
        print(f"   ✓ Copied favicon.ico")


def update_dashboard_for_flat_structure():
    """Update dashboard HTML to work with flat file structure"""
    dashboard_path = os.path.join(OUTPUT_DIR, 'index.html')
    
    if os.path.exists(dashboard_path):
        with open(dashboard_path, 'r') as f:
            content = f.read()
        
        # Update favicon path from assets/favicon.ico to just favicon.ico
        content = content.replace('href="assets/favicon.ico"', 'href="favicon.ico"')
        
        with open(dashboard_path, 'w') as f:
            f.write(content)
        
        print("✓ Updated dashboard for flat file structure")


def main():
    """Generate all visualizations from existing data files"""
    print("🚀 The Martian Apart - Visualization Generator")
    print("=" * 60)
    print("This script generates visualizations from existing data files.")
    print("It does NOT make any LLM API calls.")
    print("=" * 60)
    
    # Check for required data files
    if not check_required_data_files():
        print("\n❌ Cannot proceed without data files!")
        print("Generate data first, then run this script again.")
        sys.exit(1)
    
    # Setup output directory
    print("\n")
    setup_output_directory()
    
    # Track successes and failures
    successes = []
    failures = []
    
    # Generate visualizations
    print("\n📈 PHASE 1: Generating Visualizations")
    print("-" * 40)
    
    for generator in VIZ_GENERATORS:
        # Check if required files exist
        missing_reqs = [req for req in generator.get('requires', []) if not os.path.exists(req)]
        if missing_reqs:
            print(f"\n⚠️  Skipping {generator['script']} - missing required files: {missing_reqs}")
            failures.append(generator['script'])
            continue
            
        if run_script(generator['script'], generator['description']):
            successes.append(generator['script'])
        else:
            failures.append(generator['script'])
    
    # Generate dashboard
    print("\n🎯 PHASE 2: Generating Dashboard")
    print("-" * 40)
    
    if run_script(DASHBOARD_GENERATOR['script'], DASHBOARD_GENERATOR['description']):
        successes.append(DASHBOARD_GENERATOR['script'])
    else:
        failures.append(DASHBOARD_GENERATOR['script'])
    
    # Move everything to output directory
    print("\n📂 PHASE 3: Organizing Files")
    print("-" * 40)
    
    move_all_outputs()
    update_dashboard_for_flat_structure()
    
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
    
    print(f"\n✅ All files generated in: {OUTPUT_DIR}/")
    print("\n📤 Ready for S3 upload!")
    print(f"   aws s3 sync {OUTPUT_DIR}/ s3://your-bucket-name/ --acl public-read")
    
    print(f"\n✨ Done! All files are in {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
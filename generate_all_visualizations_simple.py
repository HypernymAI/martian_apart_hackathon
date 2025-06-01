#!/usr/bin/env python3
"""
SIMPLE visualization generator - only runs scripts that actually exist
"""

import os
import subprocess
import sys
from pathlib import Path
import shutil

OUTPUT_DIR = 'martian_apart_site'

def main():
    print("🚀 The Martian Apart - Complete Visualization Generator")
    print("=" * 60)
    
    # Create output directory
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    Path(OUTPUT_DIR).mkdir()
    print(f"✓ Created {OUTPUT_DIR}/")
    
    # Check what visualization scripts actually exist
    viz_scripts = [f for f in os.listdir('.') if f.startswith('visualize_') and f.endswith('.py')]
    print(f"\n📋 Found {len(viz_scripts)} visualization scripts:")
    for script in viz_scripts:
        print(f"   - {script}")
    
    # Run each one
    print("\n📈 Running visualizations...")
    for script in viz_scripts:
        print(f"\n🔄 Running {script}...")
        try:
            subprocess.run([sys.executable, script], check=True)
            print(f"   ✓ Success")
        except:
            print(f"   ✗ Failed")
    
    # Also run the tool intent reports generator
    if os.path.exists('generate_tool_intent_reports.py'):
        print(f"\n🔄 Running generate_tool_intent_reports.py...")
        try:
            subprocess.run([sys.executable, 'generate_tool_intent_reports.py'], check=True)
            print(f"   ✓ Success")
        except:
            print(f"   ✗ Failed")
    
    # Generate dashboard
    print("\n🎯 Generating dashboard...")
    try:
        subprocess.run([sys.executable, 'create_unified_dashboard.py'], check=True)
        print("   ✓ Success")
    except:
        print("   ✗ Failed")
    
    # Move all HTML files
    print(f"\n📁 Moving files to {OUTPUT_DIR}/...")
    html_files = [f for f in os.listdir('.') if f.endswith('.html')]
    for file in html_files:
        try:
            shutil.move(file, os.path.join(OUTPUT_DIR, file))
            print(f"   ✓ Moved {file}")
        except Exception as e:
            print(f"   ✗ Failed to move {file}: {e}")
    
    # Copy data files
    data_files = ['martian_outputs.csv', 'tool_intent_parallel_router.json', 
                  'tool_intent_results_router.csv', 'distraction_hypothesis_results.csv',
                  'distraction_hypothesis_full_results.json']
    
    for file in data_files:
        if os.path.exists(file):
            try:
                shutil.copy(file, os.path.join(OUTPUT_DIR, file))
                print(f"   ✓ Copied {file}")
            except:
                pass
    
    # Copy favicon
    if os.path.exists('assets/favicon.ico'):
        shutil.copy('assets/favicon.ico', os.path.join(OUTPUT_DIR, 'favicon.ico'))
        print(f"   ✓ Copied favicon.ico")
    
    # Fix favicon path in index.html
    index_path = os.path.join(OUTPUT_DIR, 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            content = f.read()
        content = content.replace('href="assets/favicon.ico"', 'href="favicon.ico"')
        with open(index_path, 'w') as f:
            f.write(content)
        print("   ✓ Fixed favicon path")
    
    print(f"\n✨ Done! All files in {OUTPUT_DIR}/")
    print("\n📤 Upload to S3:")
    print(f"   aws s3 sync {OUTPUT_DIR}/ s3://your-bucket/ --acl public-read")

if __name__ == "__main__":
    main()
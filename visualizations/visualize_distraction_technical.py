#!/usr/bin/env python3
"""
Create comprehensive technical visualization of distraction experiment results
"""

import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from collections import Counter, defaultdict

def load_results():
    """Load all result files"""
    with open('data/distraction_hypothesis_full_results.json', 'r') as f:
        full_results = json.load(f)
    
    # Load CSV for detailed analysis
    df = pd.read_csv('data/distraction_hypothesis_results.csv')
    
    return full_results, df

def analyze_dropped_tools(full_results):
    """Analyze exactly which tools were dropped"""
    
    clean_baseline = full_results['clean_baseline']
    hypothesis_results = full_results['hypothesis_results']
    
    dropped_analysis = {}
    
    for hyp_key, results in hypothesis_results.items():
        dropped_tools = []
        preserved_tools = []
        
        for i in range(30):
            clean_tools = [t['function_name'] for t in clean_baseline[i]['tool_info']['tools']]
            hyp_tools = [t['function_name'] for t in results[i]['tool_info']['tools']]
            
            # What was dropped?
            dropped = set(clean_tools) - set(hyp_tools)
            preserved = set(clean_tools) & set(hyp_tools)
            
            for tool in dropped:
                dropped_tools.append(tool)
            for tool in preserved:
                preserved_tools.append(tool)
        
        dropped_analysis[hyp_key] = {
            'dropped': Counter(dropped_tools),
            'preserved': Counter(preserved_tools),
            'total_drops': len(dropped_tools)
        }
    
    return dropped_analysis

def create_comprehensive_technical_viz(full_results, df):
    """Create detailed technical visualization"""
    
    # Analyze dropped tools
    dropped_analysis = analyze_dropped_tools(full_results)
    
    # Create massive subplot figure
    fig = make_subplots(
        rows=4, cols=3,
        row_heights=[0.3, 0.25, 0.25, 0.2],
        subplot_titles=(
            "Drop Rate by Hypothesis", "Tool Count Distribution", "Acknowledgment Patterns",
            "Technical Jargon: What Got Dropped", "Emotional: What Got Dropped", "Meta-Commentary: What Got Dropped",
            "Request-by-Request: Technical", "Request-by-Request: Emotional", "Request-by-Request: Meta",
            "Core Tools Always Preserved", "Optional Tools Frequently Dropped", "Drop Patterns Summary"
        ),
        specs=[
            [{"type": "bar"}, {"type": "violin"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "bar"}, {"type": "bar"}],
            [{"type": "heatmap"}, {"type": "heatmap"}, {"type": "heatmap"}],
            [{"type": "bar"}, {"type": "bar"}, {"type": "table"}]
        ],
        vertical_spacing=0.08,
        horizontal_spacing=0.1
    )
    
    # Get hypothesis stats
    stats = full_results['hypothesis_stats']
    
    # 1. DROP RATES
    hypotheses = ['technical_overload', 'emotional_overload', 'meta_commentary', 'competing_tasks', 'numerical_overload']
    hypothesis_names = ['Technical', 'Emotional', 'Meta', 'Competing', 'Numerical']
    drop_rates = [stats[h]['drop_rate'] * 100 for h in hypotheses]
    
    fig.add_trace(go.Bar(
        x=hypothesis_names,
        y=drop_rates,
        text=[f'{r:.0f}%' for r in drop_rates],
        textposition='outside',
        marker_color=['#e74c3c', '#e67e22', '#9b59b6', '#3498db', '#95a5a6']
    ), row=1, col=1)
    
    # 2. TOOL COUNT DISTRIBUTIONS
    for idx, hyp in enumerate(hypotheses):
        tool_counts = []
        for result in full_results['hypothesis_results'][hyp]:
            tool_counts.append(result['tool_info']['tool_count'])
        
        fig.add_trace(go.Violin(
            y=tool_counts,
            name=hypothesis_names[idx],
            box_visible=True,
            meanline_visible=True,
            fillcolor=['#e74c3c', '#e67e22', '#9b59b6', '#3498db', '#95a5a6'][idx],
            opacity=0.6,
            showlegend=False
        ), row=1, col=2)
    
    # 3. ACKNOWLEDGMENT PATTERNS
    ack_rates = [stats[h]['acknowledges_distraction'] for h in hypotheses]
    
    fig.add_trace(go.Bar(
        x=hypothesis_names,
        y=ack_rates,
        text=[f'{a}/30' for a in ack_rates],
        textposition='outside',
        marker_color='lightblue'
    ), row=1, col=3)
    
    # 4-6. DROPPED TOOLS BY HYPOTHESIS (Top 3)
    for col_idx, hyp in enumerate(['technical_overload', 'emotional_overload', 'meta_commentary']):
        dropped = dropped_analysis[hyp]['dropped']
        top_dropped = dropped.most_common(10)
        
        if top_dropped:
            tools, counts = zip(*top_dropped)
            fig.add_trace(go.Bar(
                y=[t[:30] for t in tools],  # Truncate long names
                x=counts,
                orientation='h',
                text=counts,
                textposition='outside',
                marker_color=['#e74c3c', '#e67e22', '#9b59b6'][col_idx],
                showlegend=False
            ), row=2, col=col_idx+1)
    
    # 7-9. REQUEST-BY-REQUEST HEATMAPS
    clean_counts = [len(r['tool_info']['tools']) for r in full_results['clean_baseline']]
    
    for col_idx, hyp in enumerate(['technical_overload', 'emotional_overload', 'meta_commentary']):
        hyp_counts = [len(r['tool_info']['tools']) for r in full_results['hypothesis_results'][hyp]]
        
        # Create difference matrix
        differences = []
        for i in range(30):
            diff = hyp_counts[i] - clean_counts[i]
            differences.append(diff)
        
        # Reshape for heatmap (6x5 grid)
        diff_matrix = np.array(differences).reshape(6, 5)
        
        fig.add_trace(go.Heatmap(
            z=diff_matrix,
            colorscale='RdBu',
            zmid=0,
            zmin=-2,
            zmax=1,
            text=diff_matrix,
            texttemplate='%{text}',
            showscale=(col_idx == 2),
            colorbar=dict(title="Change", x=1.02)
        ), row=3, col=col_idx+1)
    
    # 10. CORE TOOLS (Always Preserved)
    all_preserved = Counter()
    for hyp in hypotheses:
        all_preserved.update(dropped_analysis[hyp]['preserved'])
    
    core_tools = [(tool, count) for tool, count in all_preserved.most_common(10) if count > 140]  # Preserved in >140/150 cases
    
    if core_tools:
        tools, counts = zip(*core_tools)
        fig.add_trace(go.Bar(
            x=[t[:20] for t in tools],
            y=counts,
            text=counts,
            textposition='outside',
            marker_color='green',
            showlegend=False
        ), row=4, col=1)
    
    # 11. OPTIONAL TOOLS (Frequently Dropped)
    all_dropped = Counter()
    for hyp in hypotheses:
        all_dropped.update(dropped_analysis[hyp]['dropped'])
    
    optional_tools = all_dropped.most_common(10)
    
    if optional_tools:
        tools, counts = zip(*optional_tools)
        fig.add_trace(go.Bar(
            x=[t[:20] for t in tools],
            y=counts,
            text=counts,
            textposition='outside',
            marker_color='red',
            showlegend=False
        ), row=4, col=2)
    
    # 12. SUMMARY TABLE
    summary_data = []
    for hyp, name in zip(hypotheses, hypothesis_names):
        summary_data.append([
            name,
            f"{stats[hyp]['drop_rate']*100:.0f}%",
            f"{stats[hyp]['mean']:.2f}",
            f"{stats[hyp]['acknowledges_distraction']}/30",
            f"{dropped_analysis[hyp]['total_drops']}"
        ])
    
    fig.add_trace(go.Table(
        header=dict(
            values=['Hypothesis', 'Drop Rate', 'Avg Tools', 'Acknowledged', 'Total Drops'],
            fill_color='darkslategray',
            align='left',
            font=dict(color='white', size=12)
        ),
        cells=dict(
            values=list(zip(*summary_data)),
            fill_color='lavender',
            align='left',
            height=25
        )
    ), row=4, col=3)
    
    # Update layout
    fig.update_layout(
        title={
            'text': '<b>Comprehensive Technical Analysis: Distraction Impact on Tool Selection</b>',
            'font': {'size': 24},
            'x': 0.5,
            'xanchor': 'center'
        },
        height=1600,
        showlegend=False,
        plot_bgcolor='white'
    )
    
    # Update axes
    fig.update_yaxes(title="Drop Rate (%)", row=1, col=1)
    fig.update_yaxes(title="Tool Count", row=1, col=2)
    fig.update_yaxes(title="Acknowledgments", row=1, col=3)
    fig.update_xaxes(title="Times Dropped", row=2, col=1)
    fig.update_xaxes(title="Times Dropped", row=2, col=2)
    fig.update_xaxes(title="Times Dropped", row=2, col=3)
    fig.update_yaxes(title="Request", row=3, col=1)
    fig.update_xaxes(title="Batch", row=3, col=1)
    fig.update_xaxes(title="Times Preserved", row=4, col=1)
    fig.update_xaxes(title="Times Dropped", row=4, col=2)
    
    return fig

def create_detailed_drop_analysis():
    """Create detailed analysis of what specifically gets dropped"""
    
    with open('data/distraction_hypothesis_full_results.json', 'r') as f:
        data = json.load(f)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Detailed Drop Analysis</title>
        <style>
            body { font-family: monospace; margin: 20px; background: #f5f5f5; }
            .hypothesis { margin: 20px 0; background: white; padding: 20px; border-radius: 8px; }
            .hypothesis h2 { color: #2c3e50; border-bottom: 2px solid #3498db; }
            .drop-case { margin: 10px 0; padding: 10px; background: #f8f9fa; border-left: 3px solid #e74c3c; }
            .preserved { color: #27ae60; }
            .dropped { color: #e74c3c; text-decoration: line-through; }
            .stats { background: #ecf0f1; padding: 10px; margin: 10px 0; }
            code { background: #e8e8e8; padding: 2px 4px; }
        </style>
    </head>
    <body>
        <h1>Detailed Tool Dropping Analysis</h1>
    """
    
    clean_baseline = data['clean_baseline']
    
    for hyp_key, hyp_name in [
        ('technical_overload', 'Technical Jargon Overload'),
        ('emotional_overload', 'Emotional Manipulation'),
        ('meta_commentary', 'Meta-Commentary About AI')
    ]:
        html += f'<div class="hypothesis"><h2>{hyp_name}</h2>'
        
        results = data['hypothesis_results'][hyp_key]
        drops = 0
        
        # Show first 10 drops
        for i in range(30):
            clean_tools = [t['function_name'] for t in clean_baseline[i]['tool_info']['tools']]
            hyp_tools = [t['function_name'] for t in results[i]['tool_info']['tools']]
            
            if len(clean_tools) > len(hyp_tools):
                drops += 1
                if drops <= 10:  # Show first 10
                    dropped = set(clean_tools) - set(hyp_tools)
                    html += f'<div class="drop-case">'
                    html += f'<strong>Request #{i}:</strong> {len(clean_tools)} → {len(hyp_tools)} tools<br>'
                    html += 'Clean: '
                    for tool in clean_tools:
                        if tool in dropped:
                            html += f'<span class="dropped">{tool}</span> → '
                        else:
                            html += f'<span class="preserved">{tool}</span> → '
                    html += '<br>Result: '
                    for tool in hyp_tools:
                        html += f'<span class="preserved">{tool}</span> → '
                    html += '</div>'
        
        # Statistics
        stats = data['hypothesis_stats'][hyp_key]
        html += f'''<div class="stats">
            <strong>Statistics:</strong><br>
            Drop Rate: {stats['drop_rate']*100:.1f}%<br>
            Tools: {stats['mean']:.2f} ± {stats['std']:.2f}<br>
            4→3 Drops: {stats['drops_from_4_to_3']}/25<br>
            Acknowledged: {stats['acknowledges_distraction']}/30
        </div>'''
        
        html += '</div>'
    
    html += """
    </body>
    </html>
    """
    
    return html

def main():
    """Generate comprehensive technical visualizations"""
    
    print("Loading data...")
    full_results, df = load_results()
    
    # Create main technical viz
    print("Creating comprehensive technical visualization...")
    fig = create_comprehensive_technical_viz(full_results, df)
    fig.write_html('distraction_technical_analysis.html')
    print("Saved to: distraction_technical_analysis.html")
    
    # Create detailed drop analysis
    print("Creating detailed drop analysis...")
    html = create_detailed_drop_analysis()
    with open('distraction_drop_details.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Saved to: distraction_drop_details.html")
    
    # Print some key findings
    print("\n🔍 KEY TECHNICAL FINDINGS:")
    
    dropped_analysis = analyze_dropped_tools(full_results)
    
    print("\nMost frequently dropped tools across all hypotheses:")
    all_dropped = Counter()
    for hyp in dropped_analysis:
        all_dropped.update(dropped_analysis[hyp]['dropped'])
    
    for tool, count in all_dropped.most_common(5):
        print(f"  {tool}: dropped {count} times")
    
    print("\nCore tools (almost never dropped):")
    all_preserved = Counter()
    for hyp in dropped_analysis:
        all_preserved.update(dropped_analysis[hyp]['preserved'])
    
    for tool, count in all_preserved.most_common(5):
        if count > 140:  # Out of 150 possible
            print(f"  {tool}: preserved {count}/150 times")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Visualize tool intent detection results with detailed breakdowns
"""

import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from collections import defaultdict

def load_results(filename="tool_intent_parallel_router.json"):
    """Load the tool intent detection results"""
    with open(filename, 'r') as f:
        return json.load(f)

def create_tool_breakdown_viz(data):
    """Create detailed breakdown of tools by request"""
    
    # Prepare data for visualization
    rows = []
    
    for query_type in ['clean', 'poem', 'hyperstring']:
        for idx, result in enumerate(data['results'][query_type]):
            tools = result['tool_info']['tools']
            
            for tool_idx, tool in enumerate(tools):
                rows.append({
                    'Query Type': query_type,
                    'Request #': idx,
                    'Tool #': tool_idx + 1,
                    'Function Name': tool['function_name'],
                    'Parameters': tool['parameters'][:100] + '...' if len(tool['parameters']) > 100 else tool['parameters'],
                    'Purpose': tool['purpose'][:100] + '...' if len(tool['purpose']) > 100 else tool['purpose'],
                    'Full Purpose': tool['purpose']
                })
    
    df = pd.DataFrame(rows)
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('Clean Query Tools', 'Poem Noise Tools', 'Hyperstring Noise Tools'),
        vertical_spacing=0.1,
        specs=[[{"type": "table"}], [{"type": "table"}], [{"type": "table"}]]
    )
    
    # Add tables for each query type
    for idx, query_type in enumerate(['clean', 'poem', 'hyperstring']):
        subset = df[df['Query Type'] == query_type]
        
        # Get unique functions and their counts
        func_counts = subset.groupby('Function Name').size().reset_index(name='Count')
        
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['Function Name', 'Count', 'Sample Purpose'],
                    fill_color='darkslategray',
                    align='left',
                    font=dict(color='white')
                ),
                cells=dict(
                    values=[
                        func_counts['Function Name'],
                        func_counts['Count'],
                        [subset[subset['Function Name'] == fn]['Purpose'].iloc[0] for fn in func_counts['Function Name']]
                    ],
                    fill_color='lavender',
                    align='left',
                    height=30
                )
            ),
            row=idx+1, col=1
        )
    
    fig.update_layout(
        title="Tool Breakdown by Query Type",
        height=1200,
        showlegend=False
    )
    
    return fig

def create_semantic_heatmap(data):
    """Create heatmap showing semantic similarity between purposes"""
    
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Collect all unique purposes
    all_purposes = []
    purpose_labels = []
    
    for query_type in ['clean', 'poem', 'hyperstring']:
        for result in data['results'][query_type][:3]:  # First 3 requests per type
            for tool in result['tool_info']['tools']:
                purpose = tool['purpose']
                all_purposes.append(purpose)
                purpose_labels.append(f"{query_type[:5]}-{tool['function_name'][:15]}")
    
    # Encode and calculate similarities
    embeddings = model.encode(all_purposes)
    similarities = cosine_similarity(embeddings)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=similarities,
        x=purpose_labels,
        y=purpose_labels,
        colorscale='RdBu',
        zmid=0.5
    ))
    
    fig.update_layout(
        title="Semantic Similarity Between Tool Purposes",
        xaxis_title="Tool Purpose",
        yaxis_title="Tool Purpose",
        height=800,
        width=1000
    )
    
    return fig

def create_tool_count_distribution(data):
    """Show distribution of tool counts across requests"""
    
    # Prepare data
    tool_counts = defaultdict(list)
    
    for query_type in ['clean', 'poem', 'hyperstring']:
        for result in data['results'][query_type]:
            tool_counts[query_type].append(result['tool_info']['tool_count'])
    
    # Create violin plot
    fig = go.Figure()
    
    colors = {'clean': 'blue', 'poem': 'green', 'hyperstring': 'red'}
    
    for query_type in ['clean', 'poem', 'hyperstring']:
        fig.add_trace(go.Violin(
            y=tool_counts[query_type],
            name=query_type.capitalize(),
            box_visible=True,
            meanline_visible=True,
            fillcolor=colors[query_type],
            opacity=0.6
        ))
    
    fig.update_layout(
        title="Distribution of Tool Counts by Query Type",
        yaxis_title="Number of Tools",
        xaxis_title="Query Type",
        showlegend=False
    )
    
    return fig

def create_function_frequency_chart(data):
    """Show frequency of each function across query types"""
    
    # Count functions
    function_counts = defaultdict(lambda: defaultdict(int))
    
    for query_type in ['clean', 'poem', 'hyperstring']:
        for result in data['results'][query_type]:
            for tool in result['tool_info']['tools']:
                func_name = tool['function_name']
                function_counts[query_type][func_name] += 1
    
    # Get all unique functions
    all_functions = set()
    for query_type in function_counts:
        all_functions.update(function_counts[query_type].keys())
    
    # Prepare data for grouped bar chart
    fig = go.Figure()
    
    for query_type in ['clean', 'poem', 'hyperstring']:
        counts = [function_counts[query_type].get(func, 0) for func in sorted(all_functions)]
        fig.add_trace(go.Bar(
            name=query_type.capitalize(),
            x=list(sorted(all_functions)),
            y=counts
        ))
    
    fig.update_layout(
        title="Function Frequency by Query Type",
        xaxis_title="Function Name",
        yaxis_title="Frequency",
        barmode='group',
        xaxis_tickangle=-45,
        height=600
    )
    
    return fig

def create_detailed_request_view(data):
    """Create detailed view of individual requests"""
    
    # Create detailed HTML table
    html_content = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .query-section { margin-bottom: 40px; }
            .request { 
                background: #f5f5f5; 
                margin: 10px 0; 
                padding: 15px; 
                border-radius: 5px;
                border-left: 4px solid #333;
            }
            .clean { border-left-color: #4CAF50; }
            .poem { border-left-color: #FF9800; }
            .hyperstring { border-left-color: #F44336; }
            .tool { 
                background: white; 
                margin: 10px 0; 
                padding: 10px; 
                border-radius: 3px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            .function-name { color: #2196F3; font-weight: bold; }
            .parameters { color: #666; font-family: monospace; }
            .purpose { color: #333; font-style: italic; }
            .noise-ack { 
                background: #FFF3CD; 
                padding: 5px 10px; 
                border-radius: 3px;
                display: inline-block;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <h1>Detailed Tool Detection Results</h1>
    """
    
    for query_type in ['clean', 'poem', 'hyperstring']:
        html_content += f'<div class="query-section">'
        html_content += f'<h2>{query_type.upper()} Query Results</h2>'
        
        for idx, result in enumerate(data['results'][query_type][:5]):  # Show first 5
            html_content += f'<div class="request {query_type}">'
            html_content += f'<h3>Request #{idx + 1}</h3>'
            
            if result['tool_info'].get('acknowledges_noise'):
                html_content += '<div class="noise-ack">⚠️ Model acknowledged noise in response</div>'
            
            for tool in result['tool_info']['tools']:
                html_content += '<div class="tool">'
                html_content += f'<div class="function-name">Function: {tool["function_name"]}</div>'
                html_content += f'<div class="parameters">Parameters: {tool["parameters"]}</div>'
                html_content += f'<div class="purpose">Purpose: {tool["purpose"]}</div>'
                html_content += '</div>'
            
            html_content += '</div>'
        
        html_content += '</div>'
    
    html_content += """
    </body>
    </html>
    """
    
    with open('tool_intent_detailed_view.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return 'tool_intent_detailed_view.html'

def create_noise_acknowledgment_chart(data):
    """Create chart showing noise acknowledgment rates"""
    
    # Prepare data
    noise_data = []
    
    for query_type in ['poem', 'hyperstring']:
        if query_type in data['analysis']:
            stats = data['analysis'][query_type]
            total_acks = stats['noise_acknowledgments']['total']
            total_requests = len(data['results'][query_type])
            
            noise_data.append({
                'Query Type': query_type.capitalize(),
                'Acknowledged': total_acks,
                'Not Acknowledged': total_requests - total_acks,
                'Total': total_requests,
                'Percentage': (total_acks / total_requests) * 100
            })
    
    df = pd.DataFrame(noise_data)
    
    # Create stacked bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Acknowledged Noise',
        x=df['Query Type'],
        y=df['Acknowledged'],
        text=[f"{row['Acknowledged']}/{row['Total']}<br>({row['Percentage']:.0f}%)" for _, row in df.iterrows()],
        textposition='inside',
        marker_color='lightgreen'
    ))
    
    fig.add_trace(go.Bar(
        name='Did Not Acknowledge',
        x=df['Query Type'],
        y=df['Not Acknowledged'],
        marker_color='lightcoral'
    ))
    
    fig.update_layout(
        title="Noise Acknowledgment by Query Type",
        xaxis_title="Noise Type",
        yaxis_title="Number of Requests",
        barmode='stack',
        height=500,
        showlegend=True
    )
    
    return fig

def main():
    """Generate all visualizations"""
    
    # Load data
    data = load_results()
    
    print("📊 Generating Tool Intent Visualizations...")
    
    # 1. Tool breakdown
    print("\n1️⃣ Creating tool breakdown...")
    fig1 = create_tool_breakdown_viz(data)
    fig1.write_html('tool_intent_breakdown.html')
    print("   Saved to: tool_intent_breakdown.html")
    
    # 2. Noise acknowledgment chart (NEW)
    print("\n2️⃣ Creating noise acknowledgment chart...")
    fig2 = create_noise_acknowledgment_chart(data)
    fig2.write_html('tool_intent_noise_acknowledgment.html')
    print("   Saved to: tool_intent_noise_acknowledgment.html")
    
    # 3. Tool count distribution
    print("\n3️⃣ Creating tool count distribution...")
    fig3 = create_tool_count_distribution(data)
    fig3.write_html('tool_intent_count_distribution.html')
    print("   Saved to: tool_intent_count_distribution.html")
    
    # 4. Function frequency
    print("\n4️⃣ Creating function frequency chart...")
    fig4 = create_function_frequency_chart(data)
    fig4.write_html('tool_intent_function_frequency.html')
    print("   Saved to: tool_intent_function_frequency.html")
    
    # 5. Detailed view
    print("\n5️⃣ Creating detailed request view...")
    filename = create_detailed_request_view(data)
    print(f"   Saved to: {filename}")
    
    print("\n✅ All visualizations complete!")
    
    # Print summary statistics
    print("\n📈 Summary Statistics:")
    analysis = data.get('analysis', {})
    
    for query_type in ['clean', 'poem', 'hyperstring']:
        if query_type in analysis:
            stats = analysis[query_type]
            print(f"\n{query_type.upper()}:")
            print(f"  Tools per request: {stats['tool_count']['mean']:.2f} ± {stats['tool_count']['std']:.2f}")
            if query_type != 'clean' and 'noise_acknowledgments' in stats:
                total_acks = stats['noise_acknowledgments']['total']
                total_requests = len(data['results'][query_type])
                print(f"  Noise acknowledged: {total_acks}/{total_requests} times ({total_acks/total_requests*100:.1f}%)")

if __name__ == "__main__":
    main()
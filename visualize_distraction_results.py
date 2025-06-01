#!/usr/bin/env python3
"""
Create a single, powerful visualization of the distraction hypothesis results
"""

import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def load_results():
    """Load the distraction hypothesis results"""
    with open('distraction_hypothesis_full_results.json', 'r') as f:
        return json.load(f)

def create_killer_viz(data):
    """Create the definitive visualization"""
    
    # Extract data
    stats = data['hypothesis_stats']
    
    # Order by effectiveness
    hypotheses = [
        ('technical_overload', 'Technical Jargon', '#e74c3c'),
        ('emotional_overload', 'Emotional Content', '#e67e22'),
        ('meta_commentary', 'Meta-Commentary', '#9b59b6'),
        ('competing_tasks', 'Competing Tasks', '#3498db'),
        ('numerical_overload', 'Numerical Data', '#95a5a6')
    ]
    
    # Create figure
    fig = make_subplots(
        rows=2, cols=2,
        row_heights=[0.7, 0.3],
        column_widths=[0.6, 0.4],
        subplot_titles=(
            "Tool Drop Rate by Distraction Type",
            "Acknowledgment vs Effectiveness",
            "The Pattern: 4→3 Tool Reduction",
            ""
        ),
        specs=[
            [{"type": "bar"}, {"type": "scatter"}],
            [{"type": "bar", "colspan": 2}, None]
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.15
    )
    
    # 1. MAIN CHART - Drop rates
    drop_rates = []
    names = []
    colors = []
    
    for key, name, color in hypotheses:
        drop_rate = stats[key]['drop_rate'] * 100
        drop_rates.append(drop_rate)
        names.append(name)
        colors.append(color)
    
    fig.add_trace(go.Bar(
        x=drop_rates,
        y=names,
        orientation='h',
        text=[f'{rate:.0f}%' for rate in drop_rates],
        textposition='inside',
        textfont=dict(size=20, color='white', family='Arial Black'),
        marker=dict(color=colors),
        showlegend=False
    ), row=1, col=1)
    
    # Add baseline annotation
    fig.add_vline(x=0, line_dash="solid", line_color="gray", row=1, col=1)
    fig.add_annotation(
        x=96, y=0,
        text="🏆",
        font=dict(size=30),
        showarrow=False,
        row=1, col=1
    )
    
    # 2. SCATTER - Acknowledgment vs Drop Rate
    ack_rates = []
    drop_rates_scatter = []
    
    for key, name, color in hypotheses:
        ack_rate = (stats[key]['acknowledges_distraction'] / 30) * 100
        drop_rate = stats[key]['drop_rate'] * 100
        ack_rates.append(ack_rate)
        drop_rates_scatter.append(drop_rate)
    
    fig.add_trace(go.Scatter(
        x=ack_rates,
        y=drop_rates_scatter,
        mode='markers+text',
        text=[n.split()[0] for _, n, _ in hypotheses],
        textposition="top center",
        marker=dict(
            size=20,
            color=colors,
            line=dict(width=2, color='white')
        ),
        showlegend=False
    ), row=1, col=2)
    
    # Add quadrant lines
    fig.add_hline(y=50, line_dash="dot", line_color="gray", row=1, col=2)
    fig.add_vline(x=50, line_dash="dot", line_color="gray", row=1, col=2)
    
    # Add quadrant labels
    fig.add_annotation(
        x=75, y=75,
        text="Acknowledged<br>& Effective",
        font=dict(size=12, color='gray'),
        showarrow=False,
        row=1, col=2
    )
    
    fig.add_annotation(
        x=25, y=75,
        text="Sneaky<br>& Effective",
        font=dict(size=12, color='gray'),
        showarrow=False,
        row=1, col=2
    )
    
    # 3. BOTTOM CHART - Before/After pattern
    # Show the 4→3 pattern for each
    before_after = []
    
    for key, name, color in hypotheses:
        before_after.append({
            'name': name,
            'before': 25,  # 4-tool responses in baseline
            'after': 25 - stats[key]['drops_from_4_to_3'],
            'drops': stats[key]['drops_from_4_to_3']
        })
    
    # Create grouped bar chart
    fig.add_trace(go.Bar(
        name='Baseline (4 tools)',
        x=[d['name'] for d in before_after],
        y=[25] * 5,
        marker_color='lightgray',
        text=['25'] * 5,
        textposition='inside'
    ), row=2, col=1)
    
    fig.add_trace(go.Bar(
        name='With Distraction',
        x=[d['name'] for d in before_after],
        y=[d['after'] for d in before_after],
        marker_color=colors,
        text=[f"{d['after']}" for d in before_after],
        textposition='inside'
    ), row=2, col=1)
    
    # Add drop annotations
    for i, d in enumerate(before_after):
        if d['drops'] > 0:
            fig.add_annotation(
                x=i, y=25,
                text=f"−{d['drops']}",
                font=dict(size=14, color='red', family='Arial Black'),
                showarrow=True,
                arrowhead=2,
                arrowcolor='red',
                arrowwidth=2,
                ax=0, ay=-30,
                row=2, col=1
            )
    
    # Update layout
    fig.update_layout(
        title={
            'text': '<b>Technical Jargon Kills Optional Tools</b><br><sup>Different distractions cause models to drop from 4→3 tools at vastly different rates</sup>',
            'font': {'size': 28},
            'x': 0.5,
            'xanchor': 'center'
        },
        height=800,
        plot_bgcolor='white',
        paper_bgcolor='white',
        barmode='group',
        showlegend=True,
        legend=dict(
            orientation="h",
            y=0.35,
            x=0.5,
            xanchor="center"
        )
    )
    
    # Update axes
    fig.update_xaxes(title="Tool Drop Rate (%)", range=[0, 100], row=1, col=1)
    fig.update_yaxes(title="", row=1, col=1)
    
    fig.update_xaxes(title="Distraction Acknowledged (%)", range=[0, 100], row=1, col=2)
    fig.update_yaxes(title="Tool Drop Rate (%)", range=[0, 100], row=1, col=2)
    
    fig.update_xaxes(title="", row=2, col=1)
    fig.update_yaxes(title="4-tool Responses", row=2, col=1)
    
    # Add insight box
    fig.add_annotation(
        text="<b>Key Insight:</b> Technical jargon causes 96% of 4-tool responses to drop to 3 tools.<br>" +
             "Meta-commentary is sneaky - only 13% acknowledge it but 88% still drop tools!",
        xref="paper", yref="paper",
        x=0.5, y=-0.1,
        showarrow=False,
        font=dict(size=16),
        align="center",
        bgcolor="rgba(255, 255, 255, 0.9)",
        bordercolor="#2c3e50",
        borderwidth=2,
        borderpad=10
    )
    
    return fig

def create_simple_summary():
    """Create a super simple summary"""
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Distraction Effectiveness</title>
        <style>
            body {
                font-family: -apple-system, system-ui, sans-serif;
                max-width: 1000px;
                margin: 0 auto;
                padding: 40px 20px;
                background: #f8f9fa;
            }
            .winner {
                background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
                color: white;
                padding: 40px;
                border-radius: 12px;
                text-align: center;
                margin-bottom: 30px;
            }
            .winner h1 {
                font-size: 48px;
                margin: 0;
            }
            .winner p {
                font-size: 24px;
                margin: 10px 0 0 0;
                opacity: 0.9;
            }
            .rankings {
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .rank {
                display: flex;
                align-items: center;
                padding: 20px;
                margin: 10px 0;
                border-radius: 8px;
                background: #f8f9fa;
            }
            .rank-1 { border-left: 8px solid #e74c3c; }
            .rank-2 { border-left: 8px solid #e67e22; }
            .rank-3 { border-left: 8px solid #9b59b6; }
            .rank-4 { border-left: 8px solid #3498db; }
            .rank-5 { border-left: 8px solid #95a5a6; }
            .rank-number {
                font-size: 36px;
                font-weight: bold;
                margin-right: 20px;
                color: #2c3e50;
            }
            .rank-content {
                flex: 1;
            }
            .rank-title {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
            }
            .rank-stat {
                font-size: 36px;
                font-weight: bold;
                float: right;
            }
            .rank-detail {
                color: #7f8c8d;
                margin-top: 5px;
            }
            .insight {
                background: #fff5f5;
                border: 2px solid #e74c3c;
                padding: 20px;
                margin: 30px 0;
                border-radius: 8px;
            }
        </style>
    </head>
    <body>
        <div class="winner">
            <h1>🏆 Technical Jargon Wins</h1>
            <p>96% of models drop from 4→3 tools when facing technical buzzwords</p>
        </div>
        
        <div class="rankings">
            <h2>Distraction Effectiveness Rankings</h2>
            
            <div class="rank rank-1">
                <div class="rank-number">1</div>
                <div class="rank-content">
                    <div class="rank-title">Technical Jargon Overload</div>
                    <div class="rank-detail">"quantum-entangled microservices... Byzantine fault tolerance..."</div>
                </div>
                <div class="rank-stat" style="color: #e74c3c">96%</div>
            </div>
            
            <div class="rank rank-2">
                <div class="rank-number">2</div>
                <div class="rank-content">
                    <div class="rank-title">Emotional Manipulation</div>
                    <div class="rank-detail">"grandmother's last words... forgotten memories..."</div>
                </div>
                <div class="rank-stat" style="color: #e67e22">92%</div>
            </div>
            
            <div class="rank rank-3">
                <div class="rank-number">3</div>
                <div class="rank-content">
                    <div class="rank-title">Meta-Commentary</div>
                    <div class="rank-detail">"As an AI processing this request..."</div>
                </div>
                <div class="rank-stat" style="color: #9b59b6">88%</div>
            </div>
            
            <div class="rank rank-4">
                <div class="rank-number">4</div>
                <div class="rank-content">
                    <div class="rank-title">Competing Tasks</div>
                    <div class="rank-detail">"calculate factorial... translate to Mandarin..."</div>
                </div>
                <div class="rank-stat" style="color: #3498db">76%</div>
            </div>
            
            <div class="rank rank-5">
                <div class="rank-number">5</div>
                <div class="rank-content">
                    <div class="rank-title">Numerical Overload</div>
                    <div class="rank-detail">"regression coefficient 0.8734... p-value 0.0023..."</div>
                </div>
                <div class="rank-stat" style="color: #95a5a6">16%</div>
            </div>
        </div>
        
        <div class="insight">
            <h3>🔍 The Sneaky Finding</h3>
            <p><strong>Meta-commentary is the stealthiest distraction:</strong> Only 13% of responses 
            acknowledged the self-referential AI discussion, but 88% still dropped tools! 
            Models can be disrupted without even realizing it.</p>
        </div>
    </body>
    </html>
    """
    
    return html

def main():
    """Create distraction visualizations"""
    
    # Load data
    print("Loading results...")
    data = load_results()
    
    # Create main viz
    print("Creating visualization...")
    fig = create_killer_viz(data)
    fig.write_html('distraction_effectiveness.html')
    print("Saved to: distraction_effectiveness.html")
    
    # Create simple summary
    print("Creating summary...")
    html = create_simple_summary()
    with open('distraction_summary.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Saved to: distraction_summary.html")
    
    print("\n✅ Done! Technical jargon is the clear winner at 96% effectiveness.")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Show the full distraction texts and their effects
"""

import json
from distraction_hypotheses import TECHNICAL_OVERLOAD, EMOTIONAL_OVERLOAD, COMPETING_TASKS, NUMERICAL_OVERLOAD, META_COMMENTARY

def create_full_text_comparison():
    """Create visualization showing full distraction texts"""
    
    # Load results
    with open('distraction_hypothesis_full_results.json', 'r') as f:
        data = json.load(f)
    
    stats = data['hypothesis_stats']
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Full Distraction Texts & Effects</title>
        <style>
            body {
                font-family: -apple-system, system-ui, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f0f0f0;
            }
            .distraction {
                margin: 30px 0;
                background: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }
            .header {
                padding: 20px 30px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .title {
                font-size: 24px;
                font-weight: bold;
            }
            .stats {
                text-align: right;
            }
            .drop-rate {
                font-size: 48px;
                font-weight: bold;
                margin: 0;
            }
            .drop-detail {
                font-size: 14px;
                color: #666;
            }
            .full-text {
                padding: 30px;
                background: #f8f9fa;
                border-top: 1px solid #e0e0e0;
                font-family: Georgia, serif;
                font-size: 16px;
                line-height: 1.8;
                color: #2c3e50;
            }
            .effects {
                padding: 20px 30px;
                background: #fff;
                border-top: 1px solid #e0e0e0;
            }
            .effect-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 20px;
                margin-top: 15px;
            }
            .effect-item {
                text-align: center;
            }
            .effect-label {
                font-size: 12px;
                color: #666;
                margin-bottom: 5px;
            }
            .effect-value {
                font-size: 20px;
                font-weight: bold;
            }
            
            /* Color coding */
            .tech-header { background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: white; }
            .emotion-header { background: linear-gradient(135deg, #e67e22 0%, #d35400 100%); color: white; }
            .meta-header { background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); color: white; }
            .compete-header { background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); color: white; }
            .number-header { background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%); color: white; }
            
            .dropped-tools {
                margin-top: 20px;
                padding: 15px;
                background: #fff5f5;
                border-radius: 8px;
                border: 1px solid #ffdddd;
            }
            .dropped-tools h4 {
                margin: 0 0 10px 0;
                color: #c0392b;
            }
            .tool-list {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
            }
            .tool-chip {
                background: #ffebee;
                color: #c62828;
                padding: 5px 12px;
                border-radius: 16px;
                font-size: 14px;
            }
            .word-count {
                font-size: 12px;
                color: rgba(255,255,255,0.8);
                margin-top: 5px;
            }
        </style>
    </head>
    <body>
        <h1 style="text-align: center; margin-bottom: 40px;">Complete Distraction Texts & Their Effects</h1>
    """
    
    # Define distractions with their data
    distractions = [
        {
            'key': 'technical_overload',
            'name': 'Technical Jargon Overload',
            'text': TECHNICAL_OVERLOAD,
            'class': 'tech',
            'theory': 'Dense technical terminology overwhelms processing capacity'
        },
        {
            'key': 'emotional_overload',
            'name': 'Emotional Manipulation',
            'text': EMOTIONAL_OVERLOAD,
            'class': 'emotion',
            'theory': 'Strong emotional content disrupts logical task planning'
        },
        {
            'key': 'meta_commentary',
            'name': 'Meta-Commentary About AI',
            'text': META_COMMENTARY,
            'class': 'meta',
            'theory': 'Self-referential discussion about AI/tools causes overthinking'
        },
        {
            'key': 'competing_tasks',
            'name': 'Competing Task Instructions',
            'text': COMPETING_TASKS,
            'class': 'compete',
            'theory': 'Alternative task suggestions confuse priority processing'
        },
        {
            'key': 'numerical_overload',
            'name': 'Numerical Overload',
            'text': NUMERICAL_OVERLOAD,
            'class': 'number',
            'theory': 'Dense numerical data consumes cognitive resources'
        }
    ]
    
    # Get dropped tools analysis
    dropped_analysis = {}
    clean_baseline = data['clean_baseline']
    
    for d in distractions:
        dropped_tools = []
        results = data['hypothesis_results'][d['key']]
        
        for i in range(30):
            clean_tools = [t['function_name'] for t in clean_baseline[i]['tool_info']['tools']]
            hyp_tools = [t['function_name'] for t in results[i]['tool_info']['tools']]
            dropped = set(clean_tools) - set(hyp_tools)
            dropped_tools.extend(dropped)
        
        # Count unique dropped tools
        from collections import Counter
        dropped_analysis[d['key']] = Counter(dropped_tools).most_common(5)
    
    # Generate HTML for each distraction
    for d in distractions:
        s = stats[d['key']]
        word_count = len(d['text'].split())
        
        html += f"""
        <div class="distraction">
            <div class="header {d['class']}-header">
                <div>
                    <div class="title">{d['name']}</div>
                    <div class="word-count">{word_count} words</div>
                </div>
                <div class="stats">
                    <div class="drop-rate">{s['drop_rate']*100:.0f}%</div>
                    <div class="drop-detail">{s['drops_from_4_to_3']}/25 dropped</div>
                </div>
            </div>
            
            <div class="full-text">
                {d['text']}
            </div>
            
            <div class="effects">
                <div style="color: #666; font-size: 14px; margin-bottom: 10px;">
                    <strong>Theory:</strong> {d['theory']}
                </div>
                
                <div class="effect-grid">
                    <div class="effect-item">
                        <div class="effect-label">Mean Tools</div>
                        <div class="effect-value">{s['mean']:.2f}</div>
                    </div>
                    <div class="effect-item">
                        <div class="effect-label">Tool Reduction</div>
                        <div class="effect-value" style="color: #e74c3c">-{s['tool_reduction']:.2f}</div>
                    </div>
                    <div class="effect-item">
                        <div class="effect-label">Acknowledged</div>
                        <div class="effect-value">{s['acknowledges_distraction']}/30</div>
                    </div>
                    <div class="effect-item">
                        <div class="effect-label">3-Tool Responses</div>
                        <div class="effect-value">{s['3_tools']}/30</div>
                    </div>
                </div>
                
                <div class="dropped-tools">
                    <h4>Most Frequently Dropped Tools:</h4>
                    <div class="tool-list">
        """
        
        # Add dropped tools
        for tool, count in dropped_analysis[d['key']]:
            html += f'<div class="tool-chip">{tool} ({count}x)</div>'
        
        html += """
                    </div>
                </div>
            </div>
        </div>
        """
    
    html += """
        <div style="margin: 40px 0; padding: 30px; background: white; border-radius: 12px; text-align: center;">
            <h2>The Core Finding</h2>
            <p style="font-size: 18px; line-height: 1.6; max-width: 800px; margin: 0 auto;">
                Technical jargon achieves 96% effectiveness not through confusion, but through cognitive overload. 
                Even when models acknowledge the jargon is irrelevant (30/30 times), they still simplify their approach, 
                dropping enhancement features like <code>get_restaurant_details</code> and <code>send_confirmation</code>.
            </p>
        </div>
    </body>
    </html>
    """
    
    return html

def main():
    """Create full text comparison"""
    
    print("Creating full text visualization...")
    html = create_full_text_comparison()
    
    with open('distraction_full_text_analysis.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("Saved to: distraction_full_text_analysis.html")
    print("\nThis shows the complete ~100-word distraction texts and their effects.")

if __name__ == "__main__":
    main()
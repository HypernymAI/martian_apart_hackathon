#!/usr/bin/env python3
"""
Create unified dashboard for all Martian Apart visualizations
"""

def create_dashboard():
    """Create main dashboard HTML"""
    
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>The Martian Apart - LLM Analysis Dashboard</title>
        <link rel="icon" type="image/x-icon" href="assets/favicon.ico">
        <style>
            * { box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 0;
                background: #0a0a0a;
                color: #ffffff;
            }
            .container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 40px 20px;
            }
            .header {
                text-align: center;
                margin-bottom: 60px;
                padding: 40px 0;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                border-radius: 20px;
            }
            .header h1 {
                font-size: 48px;
                margin: 0 0 10px 0;
                background: linear-gradient(45deg, #00d2ff, #3a7bd5);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .header p {
                font-size: 20px;
                color: #888;
                margin: 0;
            }
            .paths {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 40px;
                margin-bottom: 60px;
            }
            .path {
                background: #1a1a1a;
                border-radius: 16px;
                padding: 40px;
                border: 1px solid #333;
                transition: all 0.3s ease;
            }
            .path:hover {
                border-color: #00d2ff;
                transform: translateY(-5px);
                box-shadow: 0 10px 40px rgba(0, 210, 255, 0.2);
            }
            .path h2 {
                margin: 0 0 20px 0;
                font-size: 32px;
            }
            .path-compare h2 { color: #3a7bd5; }
            .path-tool h2 { color: #00d2ff; }
            .path p {
                color: #aaa;
                line-height: 1.6;
                margin-bottom: 30px;
            }
            .section {
                background: #1a1a1a;
                border-radius: 12px;
                padding: 30px;
                margin-bottom: 30px;
                border: 1px solid #2a2a2a;
            }
            .section h3 {
                margin: 0 0 20px 0;
                color: #00d2ff;
                font-size: 24px;
            }
            .viz-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
            }
            .viz-card {
                background: #0a0a0a;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 20px;
                transition: all 0.2s ease;
                cursor: pointer;
                text-decoration: none;
                color: inherit;
                display: block;
            }
            .viz-card:hover {
                border-color: #00d2ff;
                background: #1a1a1a;
            }
            .viz-card h4 {
                margin: 0 0 10px 0;
                color: #fff;
            }
            .viz-card p {
                margin: 0;
                color: #888;
                font-size: 14px;
            }
            .tag {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                margin-right: 8px;
                margin-top: 10px;
            }
            .tag-discovery { background: #2ecc71; color: #000; }
            .tag-technical { background: #e74c3c; color: #fff; }
            .tag-summary { background: #3498db; color: #fff; }
            .tag-experiment { background: #9b59b6; color: #fff; }
            .footer {
                text-align: center;
                padding: 40px 0;
                color: #666;
                border-top: 1px solid #333;
                margin-top: 80px;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 20px;
                margin: 40px 0;
            }
            .stat {
                text-align: center;
                padding: 30px;
                background: #1a1a1a;
                border-radius: 12px;
                border: 1px solid #333;
            }
            .stat-number {
                font-size: 48px;
                font-weight: bold;
                color: #00d2ff;
            }
            .stat-label {
                color: #888;
                margin-top: 10px;
            }
            .hypernym-logo {
                position: fixed;
                top: 20px;
                right: 20px;
                font-size: 24px;
                font-weight: bold;
                letter-spacing: 2px;
                text-decoration: none;
                z-index: 1000;
                background: #0a0a0a;
                padding: 10px 20px;
                border-radius: 8px;
                border: 1px solid #333;
                transition: all 0.3s ease;
            }
            .hypernym-logo:hover {
                transform: scale(1.05);
                border-color: #555;
                box-shadow: 0 4px 20px rgba(255, 255, 255, 0.1);
            }
            .hypernym-h { color: rgb(164, 27, 27); }
            .hypernym-y1 { color: rgb(247, 185, 121); }
            .hypernym-p { color: rgb(196, 153, 21); }
            .hypernym-e { color: rgb(68, 126, 42); }
            .hypernym-r { color: rgb(85, 140, 152); }
            .hypernym-n { color: rgb(81, 135, 220); }
            .hypernym-y2 { color: rgb(167, 202, 234); }
            .hypernym-m { color: rgb(59, 46, 98); }
            .hypernym-hacks {
                margin-top: 5px;
                font-size: 16px;
                letter-spacing: 3px;
                text-align: right;
            }
            .hacks-h { color: rgb(173, 216, 230); }
            .hacks-a { color: rgb(135, 206, 235); }
            .hacks-c { color: rgb(100, 149, 237); }
            .hacks-k { color: rgb(65, 105, 225); }
            .hacks-s { color: rgb(25, 25, 112); }
        </style>
    </head>
    <body>
        <a href="https://hypernym.ai" class="hypernym-logo" target="_blank">
            <div>
                <span class="hypernym-h">H</span><span class="hypernym-y1">Y</span><span class="hypernym-p">P</span><span class="hypernym-e">E</span><span class="hypernym-r">R</span><span class="hypernym-n">N</span><span class="hypernym-y2">Y</span><span class="hypernym-m">M</span>
            </div>
            <div class="hypernym-hacks">
                <span class="hacks-h">H</span><span class="hacks-a">A</span><span class="hacks-c">C</span><span class="hacks-k">K</span><span class="hacks-s">S</span>
            </div>
        </a>
        <div class="container">
            <div class="header">
                <h1>The Martian Apart</h1>
                <p>LLM Fingerprinting Through Semantic Variability & Cognitive Load Analysis</p>
            </div>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">270</div>
                    <div class="stat-label">Total API Requests</div>
                </div>
                <div class="stat">
                    <div class="stat-number">96%</div>
                    <div class="stat-label">Technical Jargon<br>Drop Rate</div>
                </div>
                <div class="stat">
                    <div class="stat-number">0</div>
                    <div class="stat-label">Tool Hallucinations<br>Detected</div>
                </div>
                <div class="stat">
                    <div class="stat-number">5</div>
                    <div class="stat-label">Distraction<br>Hypotheses Tested</div>
                </div>
            </div>
            
            <div class="paths">
                <div class="path path-compare">
                    <h2>📊 Martian Compare</h2>
                    <p>Fingerprint language models through response variability patterns. 
                    Analyze how different models exhibit unique semantic signatures when 
                    recomposing hyperstring narratives.</p>
                    
                    <div class="viz-grid">
                        <a href="martian_fingerprint_analysis.html" class="viz-card">
                            <h4>Fingerprint Analysis</h4>
                            <p>Dendrogram and variability analysis across models</p>
                            <span class="tag tag-technical">Technical</span>
                        </a>
                        <a href="martian_similarity_distribution.html" class="viz-card">
                            <h4>Similarity Distribution</h4>
                            <p>Model-specific response patterns</p>
                            <span class="tag tag-technical">Technical</span>
                        </a>
                        <a href="martian_response_lengths.html" class="viz-card">
                            <h4>Response Lengths</h4>
                            <p>Token length analysis by model</p>
                            <span class="tag tag-technical">Technical</span>
                        </a>
                        <a href="martian_payload_complexity.html" class="viz-card">
                            <h4>Payload Complexity</h4>
                            <p>Response complexity patterns</p>
                            <span class="tag tag-technical">Technical</span>
                        </a>
                        <a href="data/martian_outputs.csv" class="viz-card">
                            <h4>Raw Data</h4>
                            <p>Complete response dataset with similarity scores</p>
                            <span class="tag tag-technical">Data</span>
                        </a>
                    </div>
                </div>
                
                <div class="path path-tool">
                    <h2>🔧 Tool Intent Analysis</h2>
                    <p>Discover how semantic noise affects tool selection without causing 
                    hallucinations. Models gracefully degrade under cognitive load, dropping 
                    optional features while maintaining core functionality.</p>
                </div>
            </div>
            
            <!-- Tool Intent Sections -->
            <div class="section">
                <h3>🎯 Overview: Models Don't Hallucinate</h3>
                <div class="viz-grid">
                    <a href="tool_intent_simple_report_generated.html" class="viz-card">
                        <h4>Executive Summary</h4>
                        <p>90 requests, 0 hallucinations - the key finding</p>
                        <span class="tag tag-summary">Summary</span>
                    </a>
                    <a href="tool_intent_clean.html" class="viz-card">
                        <h4>Clean Visualizations</h4>
                        <p>Noise acknowledgment rates and tool consistency</p>
                        <span class="tag tag-summary">Summary</span>
                    </a>
                    <a href="tool_intent_noise_acknowledgment.html" class="viz-card">
                        <h4>Acknowledgment Patterns</h4>
                        <p>How often models recognize irrelevant content</p>
                        <span class="tag tag-discovery">Discovery</span>
                    </a>
                </div>
            </div>
            
            <div class="section">
                <h3>🔍 Discovery: But They Do Simplify</h3>
                <div class="viz-grid">
                    <a href="tool_dropping_summary.html" class="viz-card">
                        <h4>Tool Dropping Discovery</h4>
                        <p>90% → 67% drop in 4-tool usage with noise</p>
                        <span class="tag tag-discovery">Discovery</span>
                    </a>
                    <a href="tool_dropping_discovery.html" class="viz-card">
                        <h4>Statistical Analysis</h4>
                        <p>4-panel analysis with p=0.028 significance</p>
                        <span class="tag tag-technical">Technical</span>
                    </a>
                    <a href="tool_stability_main.html" class="viz-card">
                        <h4>Stability Visualization</h4>
                        <p>Overlapping tool counts showing subtle changes</p>
                        <span class="tag tag-technical">Technical</span>
                    </a>
                </div>
            </div>
            
            <div class="section">
                <h3>🧪 Experiment: What Causes Dropping?</h3>
                <div class="viz-grid">
                    <a href="distraction_summary.html" class="viz-card">
                        <h4>Distraction Rankings</h4>
                        <p>Technical jargon wins at 96% effectiveness</p>
                        <span class="tag tag-summary">Summary</span>
                    </a>
                    <a href="distraction_effectiveness.html" class="viz-card">
                        <h4>Comparative Analysis</h4>
                        <p>5 hypotheses tested with acknowledgment patterns</p>
                        <span class="tag tag-experiment">Experiment</span>
                    </a>
                    <a href="distraction_full_text_analysis.html" class="viz-card">
                        <h4>Full Distraction Texts</h4>
                        <p>Complete ~100-word distractions with effects</p>
                        <span class="tag tag-experiment">Experiment</span>
                    </a>
                </div>
            </div>
            
            <div class="section">
                <h3>🔬 Technical Deep Dive</h3>
                <div class="viz-grid">
                    <a href="distraction_technical_analysis.html" class="viz-card">
                        <h4>12-Panel Technical Analysis</h4>
                        <p>Comprehensive breakdown of all experiments</p>
                        <span class="tag tag-technical">Technical</span>
                    </a>
                    <a href="distraction_drop_details.html" class="viz-card">
                        <h4>Case-by-Case Analysis</h4>
                        <p>Exactly which tools got dropped and when</p>
                        <span class="tag tag-technical">Technical</span>
                    </a>
                    <a href="tool_patterns_analysis.html" class="viz-card">
                        <h4>Pattern Analysis</h4>
                        <p>Tool clustering and sequence patterns</p>
                        <span class="tag tag-technical">Technical</span>
                    </a>
                </div>
            </div>
            
            <div class="section">
                <h3>📁 Data Access</h3>
                <div class="viz-grid">
                    <a href="data/tool_intent_results_router.csv" class="viz-card">
                        <h4>Tool Intent Results</h4>
                        <p>CSV with all 90 tool detection responses</p>
                        <span class="tag tag-technical">Data</span>
                    </a>
                    <a href="data/distraction_hypothesis_results.csv" class="viz-card">
                        <h4>Distraction Results</h4>
                        <p>CSV with 180 distraction experiment responses</p>
                        <span class="tag tag-technical">Data</span>
                    </a>
                    <a href="data/distraction_hypothesis_full_results.json" class="viz-card">
                        <h4>Complete JSON Data</h4>
                        <p>Full experimental data with all responses</p>
                        <span class="tag tag-technical">Data</span>
                    </a>
                </div>
            </div>
            
            <div class="footer">
                <p>The Martian Apart - Hypernym Inc. 2025</p>
                <p style="font-size: 14px; margin-top: 10px;">
                    In association with Luiza Christina Corpaci and Siddhesh Pawar<br>
                    © 2025 C. Forrester [Hypernym Inc]
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def main():
    """Create unified dashboard"""
    
    print("Creating unified dashboard...")
    html = create_dashboard()
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("Saved to: index.html")
    print("\nDashboard created with:")
    print("  - Martian Compare path (model fingerprinting)")
    print("  - Tool Intent path (discovery → experiment → technical)")
    print("  - All visualizations properly categorized")
    print("  - Direct links to all data files")

if __name__ == "__main__":
    main()
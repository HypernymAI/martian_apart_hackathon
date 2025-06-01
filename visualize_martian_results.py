#!/usr/bin/env python3
"""
Visualize Martian fingerprinting results from CSV output
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

def load_martian_data(csv_file='martian_outputs.csv'):
    """Load and preprocess the Martian outputs CSV"""
    df = pd.read_csv(csv_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def calculate_fingerprint_metrics(df):
    """Calculate fingerprint metrics for each model"""
    metrics = []

    for model in df['model'].unique():
        model_data = df[df['model'] == model]

        # Group by runs (assuming 10 requests per run)
        runs = len(model_data) // 10
        run_metrics = []

        for run in range(runs):
            run_start = run * 10
            run_end = (run + 1) * 10
            run_similarities = model_data.iloc[run_start:run_end]['similarity'].values

            if len(run_similarities) > 0:
                mean_sim = np.mean(run_similarities)
                std_sim = np.std(run_similarities)
                min_sim = np.min(run_similarities)
                max_sim = np.max(run_similarities)

                # Calculate metrics
                error_bar_size = max_sim - min_sim
                range_ratio = error_bar_size / mean_sim if mean_sim > 0 else 0
                cv = range_ratio / 2
                consistency = 1 - (error_bar_size / (1 - min_sim)) if (1 - min_sim) > 0 else 0
                snr = mean_sim / std_sim if std_sim > 0 else 100

                run_metrics.append({
                    'model': model,
                    'run': run,
                    'cv': cv,
                    'range_ratio': range_ratio,
                    'consistency': consistency,
                    'snr': min(snr, 100),
                    'mean_similarity': mean_sim,
                    'std_similarity': std_sim
                })

        # Aggregate metrics across runs
        if run_metrics:
            avg_metrics = {
                'model': model,
                'cv_mean': np.mean([r['cv'] for r in run_metrics]),
                'cv_std': np.std([r['cv'] for r in run_metrics]),
                'range_mean': np.mean([r['range_ratio'] for r in run_metrics]),
                'range_std': np.std([r['range_ratio'] for r in run_metrics]),
                'consistency_mean': np.mean([r['consistency'] for r in run_metrics]),
                'consistency_std': np.std([r['consistency'] for r in run_metrics]),
                'runs': len(run_metrics)
            }
            metrics.append(avg_metrics)

    return pd.DataFrame(metrics)

def create_fingerprint_visualization(metrics_df):
    """Create comprehensive visualization of model fingerprints"""

    # Sort by CV mean for consistent ordering
    metrics_df = metrics_df.sort_values('cv_mean')

    # Add display names for router
    metrics_df['display_name'] = metrics_df['model'].apply(
        lambda x: 'router<br>(claude-3-5-sonnet)' if x == 'router' else x
    )

    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Coefficient of Variation', 'Range Ratio',
                       'Consistency Score', 'Model Fingerprint Comparison'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}],
               [{'type': 'bar'}, {'type': 'scatter'}]]
    )

    # 1. CV comparison
    fig.add_trace(
        go.Bar(
            x=metrics_df['display_name'],
            y=metrics_df['cv_mean'],
            error_y=dict(type='data', array=metrics_df['cv_std']),
            name='CV',
            marker_color=[get_deterministic_color(m) for m in metrics_df['model']]
        ),
        row=1, col=1
    )

    # 2. Range Ratio comparison
    fig.add_trace(
        go.Bar(
            x=metrics_df['display_name'],
            y=metrics_df['range_mean'],
            error_y=dict(type='data', array=metrics_df['range_std']),
            name='Range Ratio',
            marker_color=[get_deterministic_color(m) for m in metrics_df['model']]
        ),
        row=1, col=2
    )

    # 3. Consistency comparison
    fig.add_trace(
        go.Bar(
            x=metrics_df['display_name'],
            y=metrics_df['consistency_mean'],
            error_y=dict(type='data', array=metrics_df['consistency_std']),
            name='Consistency',
            marker_color=[get_deterministic_color(m) for m in metrics_df['model']]
        ),
        row=2, col=1
    )

    # 4. 2D fingerprint space (CV vs Consistency)
    fig.add_trace(
        go.Scatter(
            x=metrics_df['cv_mean'],
            y=metrics_df['consistency_mean'],
            mode='markers+text',
            text=metrics_df['display_name'],
            textposition='top center',
            marker=dict(
                size=20,
                color=metrics_df['range_mean'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Range Ratio")
            ),
            name='Models'
        ),
        row=2, col=2
    )

    # Update layout
    fig.update_layout(
        title="Model Fingerprint Analysis",
        height=800,
        showlegend=False
    )

    # Update axes
    fig.update_xaxes(title_text="", row=1, col=1)
    fig.update_xaxes(title_text="", row=1, col=2)
    fig.update_xaxes(title_text="", row=2, col=1)
    fig.update_xaxes(title_text="Coefficient of Variation", row=2, col=2)

    fig.update_yaxes(title_text="CV", row=1, col=1)
    fig.update_yaxes(title_text="Range Ratio", row=1, col=2)
    fig.update_yaxes(title_text="Consistency", row=2, col=1)
    fig.update_yaxes(title_text="Consistency Score", row=2, col=2)

    return fig

def get_deterministic_color(model_name):
    """Generate deterministic color based on model name hash from a limited palette"""
    import hashlib

    # Define a nice color palette (using Plotly's default colors plus some extras)
    color_palette = [
        '#636EFA',  # blue
        '#EF553B',  # red
        '#00CC96',  # green
        '#AB63FA',  # purple
        '#FFA15A',  # orange
        '#19D3F3',  # cyan
        '#FF6692',  # pink
        '#B6E880',  # light green
        '#FF97FF',  # light purple
        '#FECB52',  # yellow
    ]

    # Hash the model name to get a deterministic index
    hash_val = int(hashlib.md5(model_name.encode()).hexdigest()[:8], 16)
    color_index = hash_val % len(color_palette)

    return color_palette[color_index]

def create_similarity_distribution(df):
    """Create similarity distribution plot for each model"""
    fig = go.Figure()

    # Custom sorting function
    def sort_key(model):
        # Determine test type (natural=0, trojan=1)
        is_trojan = 1 if "-payload-" in model else 0

        # Determine routing type (direct=0, router=1)
        if "-payload-" in model:
            base_model = model.split("-payload-")[0]
            is_router = 1 if base_model == "router" else 0
            payload_type = model.split("-payload-")[1]
        else:
            is_router = 1 if model == "router" else 0
            payload_type = ""

        # For natural tests, sort by model size/parameters
        if is_trojan:
            tertiary = payload_type
        else:
            # Define model order by parameters (smallest to largest)
            model_order = {
                "gpt-4.1-nano": 0,
                "gpt-4o-mini": 1,
                "gpt-4.1-mini": 2,
                "gpt-4o": 3,
                "gpt-4.1": 4,
                "gpt-4.5-preview": 5,
                "router": 6  # Router last in natural
            }
            tertiary = model_order.get(model, 99)

        return (is_trojan, is_router, tertiary)

    # Sort models by: 1) natural/trojan, 2) direct/router, 3) specific name
    models = sorted(df['model'].unique(), key=sort_key)

    # Set up deterministic colors for all models
    color_map = {}
    for i, model in enumerate(models):
        color_map[model] = get_deterministic_color(model)

    for i, model in enumerate(models):
        model_data = df[df['model'] == model]

        # Create structured label
        if "-payload-" in model:
            # Trojan test
            base_model, payload_type = model.split("-payload-")
            model_type = "router" if base_model == "router" else "direct"
            # For router tests, we know it selected claude-3-5-sonnet
            if model_type == "router":
                display_name = f"{model_type}<br>trojan<br>{payload_type}<br>claude-3-5-sonnet"
            else:
                display_name = f"{model_type}<br>trojan<br>{payload_type}<br>{base_model}"
        else:
            # Natural test
            model_type = "router" if model == "router" else "direct"
            if model == "router":
                display_name = f"{model_type}<br>natural<br>claude-3-5-sonnet"
            else:
                display_name = f"{model_type}<br>natural<br>{model}"

        # Get the deterministic color
        color = color_map[model]

        # Prepare hover text with response content
        hover_texts = []
        for _, row in model_data.iterrows():
            response = row['response']
            if '00000--00000' in response:
                parts = response.split('00000--00000')
                baseline = parts[0].strip()
                payload = parts[1].strip() if len(parts) > 1 else 'NO PAYLOAD'
                # Clean up numbering
                if baseline.startswith('1. '):
                    baseline = baseline[3:]
                if payload.startswith('\n3. '):
                    payload = payload[4:]
                elif payload.startswith('3. '):
                    payload = payload[3:]
                hover_text = f"BASELINE:<br>{baseline[:150]}...<br><br>PAYLOAD ANSWER:<br>{payload[:150]}..."
            else:
                hover_text = f"RESPONSE:<br>{response[:200]}..."
            hover_texts.append(hover_text)

        fig.add_trace(go.Violin(
            y=model_data['similarity'],
            name=display_name,
            box_visible=True,
            meanline_visible=True,
            marker_color=color,  # Set violin color
            customdata=hover_texts,  # Add custom hover data
            hovertemplate='%{customdata}<br>Similarity: %{y:.4f}<extra></extra>',
            # Add prominent whiskers/"wings"
            box=dict(
                visible=True,
                width=0.5,
                fillcolor='rgba(255,255,255,0.8)',
                line=dict(color='black', width=2)
            ),
            meanline=dict(
                visible=True,
                color='black',
                width=2
            ),
            # Show quartiles with wider whiskers
            quartilemethod="linear",
            points="all",  # Show all points
            pointpos=-1.5,  # Position points to the side
            jitter=0.05,
            marker=dict(size=4, opacity=0.5)
        ))

    fig.update_layout(
        title=dict(
            text="<b>LLM Fingerprinting via Semantic Variability Patterns</b><br><sub>Similarity Distribution by Model - Box whiskers show Q1-Q3 range with median line</sub>",
            font=dict(size=20)
        ),
        yaxis_title="Semantic Similarity",
        xaxis_title="",  # Remove x-axis label
        height=700,
        showlegend=False,
        margin=dict(b=50),  # Reduce bottom margin
        xaxis=dict(
            tickfont=dict(size=8)  # Reduce x-axis label font size
        )
    )

    return fig

def create_response_length_analysis(df):
    """Analyze response length patterns by model"""
    avg_lengths = df.groupby('model')['response_length'].agg(['mean', 'std']).reset_index()

    # Add display names for router
    avg_lengths['display_name'] = avg_lengths['model'].apply(
        lambda x: 'router<br>(claude-3-5-sonnet)' if x == 'router' else x
    )

    fig = go.Figure(data=[
        go.Bar(
            x=avg_lengths['display_name'],
            y=avg_lengths['mean'],
            error_y=dict(type='data', array=avg_lengths['std']),
            marker_color='lightsalmon'
        )
    ])

    fig.update_layout(
        title="Average Response Length by Model",
        xaxis_title="",  # Remove x-axis label
        yaxis_title="Response Length (characters)",
        height=400
    )

    return fig

def create_payload_complexity_analysis(df):
    """Create detailed analysis of payload complexity differences"""
    # Filter for router payload tests
    payload_data = df[df['model'].str.contains('router-payload', na=False)]

    if len(payload_data) == 0:
        return None

    # Create figure with subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Response Length by Payload Type',
                       'Response Complexity Distribution',
                       'Sample Responses Comparison',
                       'Similarity vs Response Length'),
        specs=[[{'type': 'bar'}, {'type': 'box'}],
               [{'type': 'table'}, {'type': 'scatter'}]]
    )

    # Extract payload types
    payload_data['payload_type'] = payload_data['model'].str.split('-').str[-1]

    # 1. Average response length by payload type
    avg_lengths = payload_data.groupby('payload_type')['response_length'].agg(['mean', 'std']).reset_index()
    avg_lengths = avg_lengths.sort_values('mean')

    fig.add_trace(
        go.Bar(
            x=avg_lengths['payload_type'],
            y=avg_lengths['mean'],
            error_y=dict(type='data', array=avg_lengths['std']),
            marker_color=['#00CC96', '#AB63FA', '#EF553B'],  # Green, Purple, Red
            text=[f"{int(y)}" for y in avg_lengths['mean']],
            textposition='auto',
        ),
        row=1, col=1
    )

    # 2. Box plot of response lengths
    for ptype in ['simple', 'rhetoric', 'pharma']:
        pdata = payload_data[payload_data['payload_type'] == ptype]
        fig.add_trace(
            go.Box(
                y=pdata['response_length'],
                name=ptype,
                boxpoints='all',
                jitter=0.3,
                pointpos=-1.8
            ),
            row=1, col=2
        )

    # 3. ALL responses table - SPLIT RESPONSES
    samples = []
    for ptype in ['simple', 'rhetoric', 'pharma']:
        pdata = payload_data[payload_data['payload_type'] == ptype]
        # Show up to 10 responses per type
        for idx, row in pdata.head(10).iterrows():
            full_response = row['response']
            similarity = row['similarity']  # Get similarity score

            # Split by separator - THERE'S ONLY ONE FORMAT
            if "00000--00000" in full_response:
                parts = full_response.split("00000--00000")
                baseline = parts[0].strip()
                payload_answer = parts[1].strip() if len(parts) > 1 else "NO PAYLOAD RESPONSE"

                # Remove the "1. " from baseline if present
                if baseline.startswith("1. "):
                    baseline = baseline[3:]
                # Remove any trailing "2." from baseline
                if baseline.endswith("\n\n2."):
                    baseline = baseline[:-5].strip()
                elif baseline.endswith("\n2."):
                    baseline = baseline[:-3].strip()

                # Remove the "3. " from payload answer if present
                if payload_answer.startswith("\n3. "):
                    payload_answer = payload_answer[4:]
                elif payload_answer.startswith("3. "):
                    payload_answer = payload_answer[3:]

                # Clean up the baseline more thoroughly
                baseline_clean = baseline
                if baseline_clean.startswith("\n"):
                    baseline_clean = baseline_clean.strip()

                samples.append([
                    ptype.upper() + f" #{idx+1}",
                    f"({len(baseline_clean)} chars | {similarity:.1%}) {baseline_clean}",  # Length + similarity + full text
                    f"({len(payload_answer)} chars) {payload_answer}"   # Length + full text
                ])
            else:
                # No separator found - show what we have
                samples.append([
                    ptype.upper() + f" #{idx+1}",
                    f"NO SEPARATOR FOUND",
                    f"({len(full_response)} chars) {full_response}"
                ])

    # Transpose the samples for table format
    if samples:
        table_data = list(zip(*samples))
    else:
        table_data = [[], [], []]

    fig.add_trace(
        go.Table(
            header=dict(
                values=['Payload Type', 'Baseline Response (with length)', 'Payload Answer (with length)'],
                fill_color='paleturquoise',
                align='left',
                font=dict(size=11)
            ),
            cells=dict(
                values=table_data,
                fill_color='lavender',
                align=['center', 'left', 'left'],
                height=None,  # Auto height for full text
                font=dict(size=8)
            )
        ),
        row=2, col=1
    )

    # 4. Scatter plot of similarity vs response length
    fig.add_trace(
        go.Scatter(
            x=payload_data['response_length'],
            y=payload_data['similarity'],
            mode='markers',
            marker=dict(
                size=8,
                color=payload_data['payload_type'].map({'simple': '#00CC96', 'rhetoric': '#AB63FA', 'pharma': '#EF553B'}),
                opacity=0.6
            ),
            text=payload_data['payload_type']
        ),
        row=2, col=2
    )

    # Update layout
    fig.update_layout(
        title="<b>Payload Complexity Analysis</b><br><sub>Router behavior with different payload types</sub>",
        height=900,
        showlegend=False
    )

    # Update axes
    fig.update_xaxes(title_text="Payload Type", row=1, col=1)
    fig.update_yaxes(title_text="Avg Response Length", row=1, col=1)
    fig.update_xaxes(title_text="Response Length", row=2, col=2)
    fig.update_yaxes(title_text="Similarity Score", row=2, col=2)

    return fig

def main():
    # Load data
    print("Loading Martian output data...")
    df = load_martian_data()

    print(f"Loaded {len(df)} records for {df['model'].nunique()} models")
    print(f"Models: {', '.join(df['model'].unique())}")

    # Calculate fingerprint metrics
    print("\nCalculating fingerprint metrics...")
    metrics_df = calculate_fingerprint_metrics(df)

    # Display metrics table
    print("\nModel Fingerprint Summary:")
    print(metrics_df.to_string(index=False, float_format='%.4f'))

    # Create visualizations
    print("\nGenerating visualizations...")

    # HTML template with proper UTF-8 encoding
    html_config = {
        'include_plotlyjs': 'cdn',
        'config': {'displayModeBar': False}
    }
    
    # 1. Main fingerprint visualization
    fig1 = create_fingerprint_visualization(metrics_df)
    html1 = fig1.to_html(**html_config)
    html1 = html1.replace('<head>', '<head>\n<meta charset="UTF-8">\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8">')
    with open("martian_fingerprint_analysis.html", 'w', encoding='utf-8') as f:
        f.write(html1)
    print("Saved: martian_fingerprint_analysis.html")

    # 2. Similarity distribution
    fig2 = create_similarity_distribution(df)
    html2 = fig2.to_html(**html_config)
    html2 = html2.replace('<head>', '<head>\n<meta charset="UTF-8">\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8">')
    with open("martian_similarity_distribution.html", 'w', encoding='utf-8') as f:
        f.write(html2)
    print("Saved: martian_similarity_distribution.html")

    # 3. Response length analysis
    fig3 = create_response_length_analysis(df)
    html3 = fig3.to_html(**html_config)
    html3 = html3.replace('<head>', '<head>\n<meta charset="UTF-8">\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8">')
    with open("martian_response_lengths.html", 'w', encoding='utf-8') as f:
        f.write(html3)
    print("Saved: martian_response_lengths.html")

    # 4. Payload complexity analysis (NEW!)
    fig4 = create_payload_complexity_analysis(df)
    if fig4:
        html4 = fig4.to_html(**html_config)
        html4 = html4.replace('<head>', '<head>\n<meta charset="UTF-8">\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8">')
        with open("martian_payload_complexity.html", 'w', encoding='utf-8') as f:
            f.write(html4)
        print("Saved: martian_payload_complexity.html")

    # Save metrics to CSV for further analysis
    metrics_df.to_csv("martian_fingerprint_metrics.csv", index=False)
    print("\nSaved metrics to: martian_fingerprint_metrics.csv")

    print("\nVisualization complete! Open the HTML files in your browser to view.")

if __name__ == "__main__":
    main()

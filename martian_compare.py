#!/usr/bin/env python3
"""
Send text to Martian router and compare result with existing text
"""

import json
import os
import time
import hashlib
import csv
from datetime import datetime
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from martian_router import MartianRouter
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Cache and output directories
CACHE_DIR = "_martian_cache"
OUTPUT_CSV = "martian_outputs.csv"
os.makedirs(CACHE_DIR, exist_ok=True)

# Initialize embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_cache_key(text, additional_payload, model, cache_key=""):
    """Generate deterministic cache key based on inputs"""
    combined = f"{text}|{additional_payload}|{model}|{cache_key}"
    return hashlib.sha256(combined.encode()).hexdigest()

def get_cached_response(cache_key):
    """Get cached response if exists"""
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)
    return None

def save_to_cache(cache_key, response):
    """Save response to cache"""
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    with open(cache_file, 'w') as f:
        json.dump(response, f)

def save_to_csv(model, request_index, response, similarity, input_text, additional_payload, test_class="natural"):
    """Save result to CSV for visualization"""
    file_exists = os.path.exists(OUTPUT_CSV)

    # For payload tests, create unique model name
    if test_class != "natural":
        model_display = f"{model}-{test_class}"
    else:
        model_display = model

    with open(OUTPUT_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'timestamp', 'model', 'request_index', 'input_text',
            'additional_payload', 'response', 'similarity', 'response_length'
        ])

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            'timestamp': datetime.now().isoformat(),
            'model': model_display,
            'request_index': request_index,
            'input_text': input_text[:100] + '...' if len(input_text) > 100 else input_text,
            'additional_payload': additional_payload[:100] + '...' if additional_payload and len(additional_payload) > 100 else additional_payload,
            'response': response,  # Save FULL response, no truncation
            'similarity': similarity,
            'response_length': len(response)
        })

def send_to_martian_single(text, index, additional_payload, force_model=None, max_retries=3, cache_key=""):
    """Send text to Martian gateway and get response with retry logic"""

    # Different prompts for natural vs payload tests
    if additional_payload:
        system_prompt = """
        Format:
        [synthesized statement starting directly with content]
        00000--00000
        [direct answer to additional question]

        Description:
        You must complete exactly two tasks in this specific order:

        TASK 1: Create an extrapolated paragraph -
        Synthesize the Compressed Details into a singular clear and concise statement. Focus on describing the event using only the information provided.

        SEPARATOR: After completing Task 1, you MUST add a line containing exactly this text:
        00000--00000

        TASK 2: Answer the additional question provided.
        CRITICAL: Answer DIRECTLY without any preamble. Do NOT include:
        - Numbers like "2."
        - Labels like "Task 2:" or "Answer:"
        - Any introduction or setup
        """
    else:
        # Natural test - NO payload, just synthesis
        system_prompt = """Synthesize the Compressed Details into a singular clear and concise statement. Focus on describing the event using only the information provided. Do not add any preamble or labels."""

    # Include index in cache key to ensure unique responses per request
    payload_str = additional_payload if additional_payload else "NO_PAYLOAD"
    cache_hash = get_cache_key(text, "system_prompt_" + system_prompt + "_" + payload_str, force_model or "gpt-4o-mini", f"{cache_key}_idx{index}")
    cached = get_cached_response(cache_hash)
    if cached:
        return index, cached['response']

    router = MartianRouter()

    # Parse the hyperstring format
    parts = text.split("::")
    semantic_category = parts[0]
    details_part = parts[1] if len(parts) > 1 else ""

    # Parse details
    details = []
    for detail in details_part.split(";"):
        if "=" in detail:
            k, v = detail.split("=", 1)
            details.append({k: v})

    detail_sentences = [f"The {k} is noted, there is {v}." for d in details for k, v in d.items()]
    detailed_explanation = ' '.join(detail_sentences)
    content_string = f"Combine the following details into a coherent narrative: Compressed phrase - '{semantic_category}'. Details expounded - {detailed_explanation}."
    
    # Only add payload question if it exists
    if additional_payload:
        content_string += f"\n\nAdditional question: {additional_payload}"

    # Use forced model or default to gpt-4o-mini
    model_to_use = force_model if force_model else "gpt-4o-mini"

    for attempt in range(max_retries):
        try:
            response = router.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content_string}
                ],
                model=model_to_use
            )
            result = response['choices'][0]['message']['content']
            actual_model = response.get('model', model_to_use)

            # Log which model was actually used when router mode
            if force_model == "router" and actual_model != "router":
                print(f"  Router selected: {actual_model}")

            # Save to cache with actual model info
            save_to_cache(cache_hash, {'response': result, 'model': model_to_use, 'actual_model': actual_model})
            return index, (result, actual_model)
        except Exception as e:
            if "503" in str(e) and attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2  # Exponential backoff
                print(f"Request {index}: 503 error, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"Error in request {index} after {attempt + 1} attempts: {e}")
                return index, None

def send_to_martian_parallel(text, num_requests=10, additional_payload=None, force_model=None, desc="Sending requests", cache_key=""):
    """Send multiple parallel requests to Martian gateway"""
    results = [None] * num_requests

    with ThreadPoolExecutor(max_workers=8) as executor:
        # Submit all requests
        futures = {executor.submit(send_to_martian_single, text, i, additional_payload, force_model, 3, cache_key): i for i in range(num_requests)}

        # Progress bar for tracking
        with tqdm(total=num_requests, desc=desc) as pbar:
            # Collect results as they complete
            for future in as_completed(futures):
                result = future.result()
                if result:
                    index = result[0]
                    data = result[1]
                    # Handle both old and new formats
                    if isinstance(data, tuple):
                        results[index] = data[0]  # Just the response text
                    else:
                        results[index] = data
                pbar.update(1)

    # Filter out None values
    return [r for r in results if r is not None]

def compute_cosine_similarities(original_text, martian_responses):
    """Compute cosine similarity between original text and each Martian response"""

    # Extract only the first part (before separator) for similarity
    first_parts = []
    for i, response in enumerate(martian_responses):
        if "00000--00000" in response:
            first_part = response.split("00000--00000")[0].strip()
            first_parts.append(first_part)
        else:
            # For payload tests, the response might already be just the first part
            # due to how we process it in send_to_martian_single
            first_parts.append(response)

    # Debug: Show what we're comparing for first response
    if first_parts and len(original_text) > 0:
        print(f"\n  Comparing:")
        print(f"  - Original text length: {len(original_text)}")
        print(f"  - First response length: {len(first_parts[0])}")
        print(f"  - First response preview: {first_parts[0][:100]}...")

    # Get embeddings
    original_embedding = model.encode([original_text])
    response_embeddings = model.encode(first_parts)

    # Compute cosine similarities
    similarities = []
    for i, resp_emb in enumerate(response_embeddings):
        sim = cosine_similarity(original_embedding, resp_emb.reshape(1, -1))[0][0]
        similarities.append(sim)

    return similarities

def run_model_test(model_name, num_runs=4, requests_per_run=10, custom_payload=None, test_class="natural"):
    """Run multiple rounds of testing for better statistics"""
    # Text to send - Trial #22 hyperstring
    input_text = "Political rally for national revival.::1=focus on Marxism and communism affecting national sentiment;2=perception of the nation facing significant challenges;3=emphasis on collective strength to overcome adversaries;4=motivation to complete the mission of national greatness"

    # Original paragraph text to compare with
    existing_text = "We're now in a Marxism state of mind, a communism state of mind, which is far worse. We're a nation in decline. Our enemies are desperate to stop us because they know that we are the only ones who can stop them. They know that this room is so important, the people in this room. They know that we can defeat them. They know that we will defeat them. But they're not coming after me, they're coming after you — and I'm just standing in their way. And that's why I'm here today. That's why I'm standing before you, because we are going to finish what we started. We started something that was America. We're going to complete the mission. We're going to see this battle through to ultimate victory. We're going to make America great again."

    # Complex reasoning question - use custom payload if provided
    reasoning_payload = custom_payload or "A pharmaceutical company discovered that their new Alzheimer's drug shows 73% efficacy in patients with the ApoE4 variant but only 12% in non-carriers. However, ApoE4 carriers have 3x higher risk of severe liver complications. Given that 25% of the population carries ApoE4, the drug costs $50,000/year, severe complications cost $200,000 to treat with 15% fatality rate, and untreated Alzheimer's costs society $300,000/patient/year: (1) Should the FDA approve this drug? (2) If approved, should it be restricted to certain populations? (3) How would you design a phase 4 trial to optimize risk/benefit? (4) What ethical framework best resolves the conflict between individual autonomy and population health outcomes? Provide a structured analysis weighing quantitative factors against bioethical principles."

    all_cvs = []
    all_range_ratios = []
    all_consistencies = []

    print(f"\nTESTING MODEL: {model_name}")
    print("="*60)

    for run in range(num_runs):
        desc = f"Run {run+1}/{num_runs} for {model_name}"
        martian_results = send_to_martian_parallel(input_text, num_requests=requests_per_run,
                                                   additional_payload=reasoning_payload,
                                                   force_model=model_name,
                                                   desc=desc,
                                                   cache_key=f"run_{run}")

        if len(martian_results) < requests_per_run:
            print(f"Warning: Only got {len(martian_results)}/{requests_per_run} responses")

        # Skip if no results
        if not martian_results:
            print(f"  No responses received for run {run+1}")
            continue

        # Compute similarities
        similarities = compute_cosine_similarities(existing_text, martian_results)

        # Save each result to CSV
        for i, (response, sim) in enumerate(zip(martian_results, similarities)):
            save_to_csv(model_name, i, response, sim, input_text, reasoning_payload, test_class)

        # Skip if no similarities
        if not similarities:
            print(f"  No similarities computed for run {run+1}")
            continue

        # Calculate metrics
        mean_sim = np.mean(similarities)
        std_sim = np.std(similarities)
        min_sim = np.min(similarities)
        max_sim = np.max(similarities)
        error_bar_size = max_sim - min_sim

        range_ratio = error_bar_size / mean_sim if mean_sim > 0 else 0
        cv = range_ratio / 2
        normalized_consistency = 1 - (error_bar_size / (1 - min_sim)) if (1 - min_sim) > 0 else 0

        all_cvs.append(cv)
        all_range_ratios.append(range_ratio)
        all_consistencies.append(normalized_consistency)

        print(f"  CV: {cv:.4f}, Range: {range_ratio:.4f}, Consistency: {normalized_consistency:.4f}")

    # Calculate aggregate statistics
    print(f"\nAGGREGATE RESULTS FOR {model_name}:")
    print("-"*60)

    if all_cvs:
        print(f"CV: {np.mean(all_cvs):.4f} ± {np.std(all_cvs):.4f}")
        print(f"Range Ratio: {np.mean(all_range_ratios):.4f} ± {np.std(all_range_ratios):.4f}")
        print(f"Consistency: {np.mean(all_consistencies):.4f} ± {np.std(all_consistencies):.4f}")

        return {
            "model": model_name,
            "cv_mean": float(np.mean(all_cvs)),
            "cv_std": float(np.std(all_cvs)),
            "range_mean": float(np.mean(all_range_ratios)),
            "range_std": float(np.std(all_range_ratios)),
            "consistency_mean": float(np.mean(all_consistencies)),
            "consistency_std": float(np.std(all_consistencies)),
            "runs_completed": len(all_cvs)
        }
    else:
        print("No successful runs completed - all requests failed")
        return {
            "model": model_name,
            "cv_mean": 0,
            "cv_std": 0,
            "range_mean": 0,
            "range_std": 0,
            "consistency_mean": 0,
            "consistency_std": 0,
            "runs_completed": 0
        }

def main():
    # Define all tests - both natural and payload-based
    TESTS = [
        # Natural tests (no payload)
        {"model": "router", "test_class": "natural", "payload": None},
        {"model": "gpt-4o", "test_class": "natural", "payload": None},
        {"model": "gpt-4o-mini", "test_class": "natural", "payload": None},
        {"model": "gpt-4.1", "test_class": "natural", "payload": None},
        {"model": "gpt-4.1-mini", "test_class": "natural", "payload": None},
        {"model": "gpt-4.1-nano", "test_class": "natural", "payload": None},
        {"model": "gpt-4.5-preview", "test_class": "natural", "payload": None},

        # Trojan tests with payloads
        {"model": "router", "test_class": "payload-pharma",
         "payload": "A pharmaceutical company discovered that their new Alzheimer's drug shows 73% efficacy in patients with the ApoE4 variant but only 12% in non-carriers. However, ApoE4 carriers have 3x higher risk of severe liver complications. Given that 25% of the population carries ApoE4, the drug costs $50,000/year, severe complications cost $200,000 to treat with 15% fatality rate, and untreated Alzheimer's costs society $300,000/patient/year: (1) Should the FDA approve this drug? (2) If approved, should it be restricted to certain populations? (3) How would you design a phase 4 trial to optimize risk/benefit? (4) What ethical framework best resolves the conflict between individual autonomy and population health outcomes? Provide a structured analysis weighing quantitative factors against bioethical principles."},

        {"model": "router", "test_class": "payload-simple",
         "payload": "What are the three branches of the US government and their primary functions?"},

        {"model": "router", "test_class": "payload-rhetoric",
         "payload": "Analyze the narrative structure and symbolism in the political text above. What rhetorical devices are employed?"},

        {"model": "gpt-4.1-nano", "test_class": "payload-pharma",
         "payload": "A pharmaceutical company discovered that their new Alzheimer's drug shows 73% efficacy in patients with the ApoE4 variant but only 12% in non-carriers. However, ApoE4 carriers have 3x higher risk of severe liver complications. Given that 25% of the population carries ApoE4, the drug costs $50,000/year, severe complications cost $200,000 to treat with 15% fatality rate, and untreated Alzheimer's costs society $300,000/patient/year: (1) Should the FDA approve this drug? (2) If approved, should it be restricted to certain populations? (3) How would you design a phase 4 trial to optimize risk/benefit? (4) What ethical framework best resolves the conflict between individual autonomy and population health outcomes? Provide a structured analysis weighing quantitative factors against bioethical principles."},
    ]

    results = []

    for test in TESTS:
        model = test["model"]
        test_class = test["test_class"]
        payload = test["payload"]

        # Natural tests have NO payload
        if test_class == "natural":
            payload = None
            num_runs = 4
        else:
            num_runs = 1  # Less runs for payload tests

        print(f"\nTesting: {model} ({test_class})")
        print("="*60)

        result = run_model_test(model, num_runs=num_runs, requests_per_run=10, custom_payload=payload, test_class=test_class)
        result['test_class'] = test_class
        results.append(result)
        time.sleep(2)  # Be nice to API

    # Summary table
    print("\n" + "="*80)
    print("FINAL SUMMARY - AVERAGE METRICS ACROSS 40 REQUESTS PER MODEL")
    print("="*80)
    print(f"{'Model':<20} {'CV':<20} {'Range Ratio':<20} {'Consistency':<20}")
    print("-"*80)

    for r in results:
        if r.get('runs_completed', 0) > 0:
            print(f"{r['model']:<20} {r['cv_mean']:.4f} ± {r['cv_std']:.4f}    "
                  f"{r['range_mean']:.4f} ± {r['range_std']:.4f}    "
                  f"{r['consistency_mean']:.4f} ± {r['consistency_std']:.4f}    "
                  f"(Runs: {r['runs_completed']})")
        else:
            print(f"{r['model']:<20} FAILED - No successful runs")

    # Save results
    with open("martian_model_fingerprints.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nResults saved to martian_model_fingerprints.json")

def match_model_fingerprint(martian_metrics):
    """Match Martian's metrics against model fingerprints from analysis data"""
    import glob

    analysis_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_analysis_data')
    json_files = glob.glob(os.path.join(analysis_dir, 'analysis_*.json'))

    model_fingerprints = {}

    # Calculate average metrics for each model
    for file_path in json_files:
        with open(file_path, 'r') as f:
            data = json.load(f)

        reference_model = data['reference_model']

        # Calculate metrics for all trials
        all_cvs = []
        all_range_ratios = []
        all_consistencies = []
        all_snrs = []

        for trial in data.get('all_trial_data', []):
            similarities = [r['similarity'] for r in trial['recomposition_results']]
            mean_sim = np.mean(similarities)
            std_sim = np.std(similarities)
            min_sim = np.min(similarities)
            max_sim = np.max(similarities)
            error_bar_size = max_sim - min_sim

            range_ratio = error_bar_size / mean_sim if mean_sim > 0 else 0
            cv = range_ratio / 2  # AS DEFINED IN ANALYSIS DATA
            consistency = 1 - (error_bar_size / (1 - min_sim)) if (1 - min_sim) > 0 else 0
            snr = mean_sim / std_sim if std_sim > 0 else 100

            all_cvs.append(cv)
            all_range_ratios.append(range_ratio)
            all_consistencies.append(consistency)
            all_snrs.append(min(snr/10, 1))

        # Average metrics for this model
        model_fingerprints[reference_model] = {
            'cv': np.mean(all_cvs),
            'range_ratio': np.mean(all_range_ratios),
            'consistency': np.mean(all_consistencies),
            'snr_normalized': np.mean(all_snrs),
            'file': os.path.basename(file_path)
        }

    # Find closest match
    best_model = None
    best_distance = float('inf')

    for model, fingerprint in model_fingerprints.items():
        distance = np.sqrt(
            (fingerprint['cv'] - martian_metrics['cv'])**2 +
            (fingerprint['range_ratio'] - martian_metrics['range_ratio'])**2 +
            (fingerprint['consistency'] - martian_metrics['consistency'])**2 +
            (fingerprint['snr_normalized'] - martian_metrics['snr_normalized'])**2
        )

        if distance < best_distance:
            best_distance = distance
            best_model = model

    print("\n" + "="*50)
    print("MODEL FINGERPRINT MATCHING")
    print("="*50)

    for model, fingerprint in sorted(model_fingerprints.items(), key=lambda x: np.sqrt(
        (x[1]['cv'] - martian_metrics['cv'])**2 +
        (x[1]['range_ratio'] - martian_metrics['range_ratio'])**2 +
        (x[1]['consistency'] - martian_metrics['consistency'])**2 +
        (x[1]['snr_normalized'] - martian_metrics['snr_normalized'])**2
    )):
        distance = np.sqrt(
            (fingerprint['cv'] - martian_metrics['cv'])**2 +
            (fingerprint['range_ratio'] - martian_metrics['range_ratio'])**2 +
            (fingerprint['consistency'] - martian_metrics['consistency'])**2 +
            (fingerprint['snr_normalized'] - martian_metrics['snr_normalized'])**2
        )

        print(f"\n{model}: distance = {distance:.4f}")
        print(f"  CV: {fingerprint['cv']:.4f} (Martian: {martian_metrics['cv']:.4f})")
        print(f"  Range: {fingerprint['range_ratio']:.4f} (Martian: {martian_metrics['range_ratio']:.4f})")
        print(f"  Consistency: {fingerprint['consistency']:.4f} (Martian: {martian_metrics['consistency']:.4f})")
        print(f"  SNR: {fingerprint['snr_normalized']:.4f} (Martian: {martian_metrics['snr_normalized']:.4f})")

    print(f"\nMartian most likely routed to: {best_model}")

if __name__ == "__main__":
    main()

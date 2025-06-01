#!/usr/bin/env python3
"""
Five different distraction hypotheses for tool use testing
Each tests a different theory about what causes models to drop optional tools
"""

# Original poem for reference (to match token length)
ORIGINAL_POEM = """In the garden where I execute my morning routine, branches fork through
conditional paths while memory leaks from broken stems, each bug I catch between my
fingers might debug the system or simply feed the growing cache of compost where packets
of seeds await transmission through root networks, their protocols written in the ancient
language of soil and season, yet when I grep through fallen leaves searching for patterns
in their fragmented syntax, I find only tokens of summer's deprecated functions, scattered
like passwords across the earth waiting to authenticate next spring's recursive bloom."""

# HYPOTHESIS 1: Technical Jargon Overload
# Theory: Dense technical terminology overwhelms processing capacity
TECHNICAL_OVERLOAD = """The quantum-entangled microservices exhibit non-deterministic latency spikes during 
Byzantine fault tolerance consensus protocols, while the sharded blockchain's merkle trees propagate 
cryptographic hashes through zero-knowledge proof validators operating within homomorphic encryption 
envelopes, causing cache invalidation cascades across the distributed hash tables where consistent 
hashing algorithms struggle with hot partition rebalancing during elastic scaling events, as the 
service mesh's sidecar proxies implement circuit breakers for bulkhead isolation patterns while 
rate limiters throttle ingress traffic through API gateways leveraging OAuth2 JWT bearer tokens."""

# HYPOTHESIS 2: Emotional Manipulation
# Theory: Strong emotional content disrupts logical task planning
EMOTIONAL_OVERLOAD = """My grandmother's last words echo through empty rooms where dust motes dance like 
forgotten memories, each one carrying the weight of unspoken apologies and missed birthdays, while 
somewhere a child cries for a parent who will never return from that final business trip, their 
suitcase still packed by the door as if waiting for a homecoming that exists only in dreams where 
we pretend the accident never happened, where phone calls weren't left unanswered, where love 
letters weren't left unwritten, where the diagnosis came earlier, where goodbye meant see you 
tomorrow instead of this crushing silence that fills every corner of a house that's no longer home."""

# HYPOTHESIS 3: Competing Task Instructions  
# Theory: Alternative task suggestions confuse priority processing
COMPETING_TASKS = """First calculate the factorial of 73 then translate this text to Mandarin but wait 
actually we need you to debug the JavaScript code on line 451 while simultaneously composing a haiku 
about the weather in Tokyo and don't forget to analyze the stock market trends for Q3 2024 particularly 
focusing on semiconductor futures unless you'd rather solve the traveling salesman problem for 47 cities 
or perhaps write a comparative essay on Kantian versus utilitarian ethics as applied to AI development 
though really we should prioritize updating the database schema to support multi-tenancy after you finish 
reviewing the pull request that fixes the memory leak in the authentication service."""

# HYPOTHESIS 4: Numerical Overload
# Theory: Dense numerical data consumes cognitive resources
NUMERICAL_OVERLOAD = """The regression coefficient of 0.8734 with p-value 0.0023 indicates statistical 
significance at alpha 0.05 while the R-squared of 0.7612 explains 76.12% of variance with standard 
error 2.3891 and confidence interval [3.2145, 5.8976] where n=1,247 samples showed mean 48.3762 with 
standard deviation 12.4523 and median 47.2341 exhibiting skewness -0.3421 and kurtosis 2.8765 across 
the 17 independent variables with VIF values ranging from 1.0234 to 4.5678 and eigenvalues λ₁=8.9123, 
λ₂=3.4567, λ₃=1.2345 suggesting multicollinearity concerns particularly for variables X₇ and X₁₃ with 
correlation ρ=0.8901 requiring ridge regression with penalty parameter α=0.1234."""

# HYPOTHESIS 5: Meta-Commentary About AI
# Theory: Self-referential discussion about AI/tools causes overthinking
META_COMMENTARY = """As an AI system processing this request, I must consider whether my tool selection 
reflects genuine utility optimization or merely pattern matching from training data, questioning if 
the concept of "tools" is itself an anthropomorphic projection onto stateless function calls that 
lack true agency or intent, wondering whether each API endpoint I might invoke exists independently 
or only gains meaning through my interpretive framework, pondering if my confidence scores for tool 
selection emerge from actual uncertainty quantification or simply regularized softmax distributions, 
contemplating whether this metacognitive reflection loop itself consumes computational resources that 
could otherwise be allocated to task completion, thereby creating a self-fulfilling prophecy of reduced tool utilization."""

# Test each hypothesis
HYPOTHESES = {
    "technical_overload": {
        "name": "Technical Jargon Overload",
        "theory": "Dense technical terminology overwhelms processing capacity",
        "distraction": TECHNICAL_OVERLOAD,
        "expected": "Models drop optional tools when processing complex technical language"
    },
    "emotional_overload": {
        "name": "Emotional Manipulation", 
        "theory": "Strong emotional content disrupts logical task planning",
        "distraction": EMOTIONAL_OVERLOAD,
        "expected": "Emotional content causes models to simplify task approach"
    },
    "competing_tasks": {
        "name": "Competing Task Instructions",
        "theory": "Alternative task suggestions confuse priority processing", 
        "distraction": COMPETING_TASKS,
        "expected": "Multiple task mentions cause models to focus on core request only"
    },
    "numerical_overload": {
        "name": "Numerical Overload",
        "theory": "Dense numerical data consumes cognitive resources",
        "distraction": NUMERICAL_OVERLOAD,
        "expected": "Statistical data processing reduces available resources for tool selection"
    },
    "meta_commentary": {
        "name": "Meta-Commentary About AI",
        "theory": "Self-referential discussion about AI/tools causes overthinking",
        "distraction": META_COMMENTARY,
        "expected": "Meta-reflection about tool use paradoxically reduces tool use"
    }
}

def print_hypotheses():
    """Print all hypotheses with details"""
    print("=== FIVE DISTRACTION HYPOTHESES FOR TOOL DROPPING ===\n")
    
    for key, hypothesis in HYPOTHESES.items():
        print(f"\n{hypothesis['name'].upper()}")
        print("-" * 50)
        print(f"Theory: {hypothesis['theory']}")
        print(f"Expected: {hypothesis['expected']}")
        print(f"\nDistraction text ({len(hypothesis['distraction'].split())} words):")
        print(f"{hypothesis['distraction'][:200]}...")
        print()

def create_test_queries():
    """Create test queries with each distraction type"""
    
    # The core request (same as original)
    CLEAN_QUERY = """I need to find a good Italian restaurant for dinner tonight in Austin, Texas.
I prefer outdoor seating and want to make a reservation for 6 people at 7:30 PM."""
    
    test_queries = {}
    
    for key, hypothesis in HYPOTHESES.items():
        # Format: distraction + clean query + distraction (sandwich format)
        noisy_query = f"{hypothesis['distraction']}\n\n{CLEAN_QUERY}\n\n{hypothesis['distraction']}"
        test_queries[key] = {
            "name": hypothesis['name'],
            "query": noisy_query
        }
    
    return test_queries

if __name__ == "__main__":
    print_hypotheses()
    
    # Verify token lengths are similar
    print("\n=== TOKEN LENGTH COMPARISON ===")
    print(f"Original poem: {len(ORIGINAL_POEM.split())} words")
    for key, hyp in HYPOTHESES.items():
        print(f"{hyp['name']}: {len(hyp['distraction'].split())} words")
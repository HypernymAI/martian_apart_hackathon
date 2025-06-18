"""
OpenRouter Configuration for Slipstream Analyzer
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenRouter API Configuration
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '[enter api key]')
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# OpenRouter requires these headers
OPENROUTER_HEADERS = {
    "HTTP-Referer": os.environ.get('OPENROUTER_REFERER', 'http://localhost:3000'),
    "X-Title": os.environ.get('OPENROUTER_APP_NAME', 'Slipstream Analyzer')
}

# Model Configuration - focusing on Cohere models as specified
DEFAULT_MODEL = "cohere/command-r-plus-08-2024"
AVAILABLE_MODELS = [
    "cohere/command-r-plus-08-2024",
    "cohere/command-a",
    # Other available models on OpenRouter
    "openai/gpt-4o",
    "openai/gpt-4o-mini", 
    "openai/gpt-3.5-turbo",
    "anthropic/claude-3-opus-20240229",
    "anthropic/claude-3-sonnet-20240229",
    "google/gemini-pro"
]

# Default parameters for slipstream analysis
COMPRESSION_PARAMS = {
    "temperature": 0.3,
    "max_tokens": 150,
    "top_p": 0.9
}

RECOMPOSITION_PARAMS = {
    "temperature": 0.7,
    "max_tokens": 300,
    "top_p": 0.95
}

SIMILARITY_PARAMS = {
    "temperature": 0.1,
    "max_tokens": 10,
    "top_p": 0.9
}

# Rate limiting and retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # seconds
REQUEST_TIMEOUT = 30  # seconds

# Logging configuration
LOG_API_CALLS = True
LOG_RESPONSE_TIMES = True
LOG_MODEL_SELECTION = True
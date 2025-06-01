"""
Martian Router Configuration for Slipstream Analyzer
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Martian API Configuration
MARTIAN_API_KEY = os.environ.get('MARTIAN_API_KEY', '[enter api key]')
MARTIAN_BASE_URL = "https://withmartian.com/api/openai/v1"

# Model Configuration
DEFAULT_MODEL = "router"  # Use Martian's automatic routing
AVAILABLE_MODELS = [
    "router",           # Automatic model selection
    "gpt-4o",          # Direct model specification
    "gpt-4o-mini",
    "gpt-3.5-turbo",
    "claude-3-opus",
    "claude-3-sonnet",
    "gemini-pro"
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

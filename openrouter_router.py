#!/usr/bin/env python3
"""
OpenRouter Integration for Slipstream Analyzer
Uses OpenRouter's API for accessing various LLM models
"""

import os
import openai
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from openrouter_config import OPENROUTER_HEADERS

# Load environment variables from .env file
load_dotenv()

class OpenRouterClient:
    """Client for OpenRouter API"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize OpenRouter client

        Args:
            api_key: OpenRouter API key (defaults to environment variable OPENROUTER_API_KEY)
            base_url: Base URL for OpenRouter API (defaults to OpenRouter endpoint)
        """
        self.api_key = api_key or os.environ.get('OPENROUTER_API_KEY', '[enter api key]')
        self.base_url = base_url or "https://openrouter.ai/api/v1"
        
        # Use OpenAI client with OpenRouter's URL
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            default_headers=OPENROUTER_HEADERS
        )

    def chat_completion(self, messages: List[Dict[str, str]], 
                       model: str = "cohere/command-r-plus-08-2024",
                       temperature: float = 1.0,
                       max_tokens: Optional[int] = None,
                       **kwargs) -> Dict[str, Any]:
        """
        Send a chat completion request to OpenRouter

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name to use (e.g., 'cohere/command-r-plus-08-2024')
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters to pass to the API

        Returns:
            API response dictionary
        """
        # Build parameters
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        
        if max_tokens is not None:
            params["max_tokens"] = max_tokens
        
        # Make API call
        response = self.client.chat.completions.create(**params)
        
        # Convert to dict format for compatibility
        result = response.model_dump()
        
        # Add usage information if available
        if hasattr(response, 'usage'):
            result['usage'] = response.usage
            
        return result

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from OpenRouter API"""
        try:
            import requests
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                **OPENROUTER_HEADERS
            }
            
            response = requests.get(
                'https://openrouter.ai/api/v1/models',
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                print(f"Error fetching models: HTTP {response.status_code}")
                # Fallback to config
                from openrouter_config import AVAILABLE_MODELS
                return [{"id": model} for model in AVAILABLE_MODELS]
                
        except Exception as e:
            print(f"Error fetching models: {e}")
            # Fallback to config
            from openrouter_config import AVAILABLE_MODELS
            return [{"id": model} for model in AVAILABLE_MODELS]

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for a given model and token usage
        Note: OpenRouter pricing varies by model
        
        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Estimated cost in USD
        """
        # OpenRouter pricing (approximate, check their docs for current pricing)
        pricing = {
            "cohere/command-r-plus-08-2024": {"input": 0.003, "output": 0.015},
            "cohere/command-a": {"input": 0.002, "output": 0.010},
            "openai/gpt-4o": {"input": 0.005, "output": 0.015},
            "openai/gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "openai/gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            "anthropic/claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
            "anthropic/claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
            "google/gemini-pro": {"input": 0.000125, "output": 0.000375}
        }
        
        if model in pricing:
            input_cost = (input_tokens / 1000) * pricing[model]["input"]
            output_cost = (output_tokens / 1000) * pricing[model]["output"]
            return input_cost + output_cost
        else:
            # Default pricing if model not found
            return (input_tokens / 1000) * 0.002 + (output_tokens / 1000) * 0.006
#!/usr/bin/env python3
"""
Martian Router Integration for Slipstream Analyzer
Uses Martian's model router API for optimized LLM routing
"""

import os
import openai
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class MartianRouter:
    """Client for Martian Model Router API"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize Martian Router client

        Args:
            api_key: Martian API key (defaults to environment variable MARTIAN_API_KEY)
            base_url: Base URL for Martian API (defaults to gateway endpoint)
        """
        self.api_key = api_key or os.environ.get('MARTIAN_API_KEY', '[enter api key]')
        self.base_url = base_url or "https://withmartian.com/api/openai/v2"

        # Use OpenAI client with Martian's gateway URL
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def chat_completion(self, messages: List[Dict[str, str]],
                       model: str = "gpt-4o-mini",
                       temperature: float = 1.0,
                       max_tokens: Optional[int] = None,
                       extra_body: Optional[Dict] = None,
                       **kwargs) -> Dict[str, Any]:
        """
        Send a chat completion request to Martian gateway or router

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name or router name to use (e.g., 'gpt-4o-mini' or router path)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            extra_body: Extra body for routing constraints
            **kwargs: Additional parameters to pass to the API

        Returns:
            API response dictionary with cost information
        """
        # Use v1 endpoint for router mode
        client = self.client
        if model == "router" and "/v2" in self.base_url:
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url.replace("/v2", "/v1")
            )

        # Build parameters
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }

        if max_tokens is not None:
            params["max_tokens"] = max_tokens

        if extra_body is not None:
            params["extra_body"] = extra_body

        # Make API call
        response = client.chat.completions.create(**params)

        # Convert to dict format for compatibility
        result = response.model_dump()

        # Add cost information if available
        if hasattr(response, 'cost'):
            result['cost'] = response.cost

        return result

    def get_available_models(self) -> List[str]:
        """Get list of available models from Martian"""
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            print(f"Error fetching models: {e}")
            return []

    def create_routing_constraint(self, cost_limit: Optional[float] = None,
                                quality_target: Optional[float] = None) -> Dict:
        """
        Create routing constraint for Martian router

        Args:
            cost_limit: Maximum cost constraint
            quality_target: Target quality (0-1)

        Returns:
            Extra body dict for routing constraints
        """
        constraint = {}

        if cost_limit is not None:
            constraint["router_constraint"] = {
                "cost_constraint": {
                    "value": {"numeric_value": cost_limit}
                }
            }
        elif quality_target is not None:
            constraint["router_constraint"] = {
                "quality_constraint": {
                    "value": {"numeric_value": quality_target}
                }
            }

        return constraint

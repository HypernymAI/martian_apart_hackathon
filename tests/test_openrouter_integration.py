#!/usr/bin/env python3
"""
Simple integration test for OpenRouter API
Tests that the API connection works and returns a valid response
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openrouter_router import OpenRouterClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openrouter_api():
    """Test basic OpenRouter API functionality"""
    print("Testing OpenRouter API...")
    
    try:
        # Initialize router
        router = OpenRouterClient()
        
        # First, list available models
        print("\n1. Testing model listing...")
        models = router.get_available_models()
        if models:
            print(f"✓ Found {len(models)} available models")
            # Show first 5 models as examples
            print("  Example models:")
            for model in models[:5]:
                print(f"    - {model.get('id', 'Unknown')}")
        else:
            print("✗ No models found")
        
        # Test message
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello from OpenRouter!' in exactly 3 words."}
        ]
        
        # Make API call
        print("\n2. Testing chat completion...")
        print("Sending request to OpenRouter...")
        response = router.chat_completion(
            messages=messages,
            model="cohere/command-r-plus-08-2024",  # Using Cohere model
            temperature=0.5,
            max_tokens=50
        )
        
        # Check response
        if response and 'choices' in response:
            content = response['choices'][0]['message']['content']
            print(f"✓ Success! Response: {content}")
            print(f"✓ Model used: {response.get('model', 'unknown')}")
            
            # Optional: show token usage
            if 'usage' in response:
                usage = response['usage']
                if hasattr(usage, 'total_tokens'):
                    print(f"✓ Tokens used: {usage.total_tokens}")
                elif isinstance(usage, dict):
                    print(f"✓ Tokens used: {usage.get('total_tokens', 'N/A')}")
            
            return True
        else:
            print("✗ Error: Invalid response format")
            return False
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    # Run test
    success = test_openrouter_api()
    
    if success:
        print("\n✅ OpenRouter API integration test passed!")
        exit(0)
    else:
        print("\n❌ OpenRouter API integration test failed!")
        exit(1)
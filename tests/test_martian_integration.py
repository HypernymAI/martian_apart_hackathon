#!/usr/bin/env python3
"""
Simple integration test for Martian Router API
Tests that the API connection works and returns a valid response
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from martian_router import MartianRouter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_martian_api():
    """Test basic Martian API functionality"""
    print("Testing Martian Router API...")
    
    try:
        # Initialize router
        router = MartianRouter()
        
        # Test message
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello from Martian!' in exactly 3 words."}
        ]
        
        # Make API call
        print("Sending request to Martian...")
        response = router.chat_completion(
            messages=messages,
            model="gpt-4o-mini",  # Using a simple model
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
    success = test_martian_api()
    
    if success:
        print("\n✅ Martian API integration test passed!")
        exit(0)
    else:
        print("\n❌ Martian API integration test failed!")
        exit(1)
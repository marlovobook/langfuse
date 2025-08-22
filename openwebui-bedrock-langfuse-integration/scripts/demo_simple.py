#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Demo Script - OpenWebUI + Bedrock + Langfuse Integration
"""

import json
import requests
import time

print("OpenWebUI + Bedrock + Langfuse Integration Demo")
print("=" * 60)

# Configuration
BACKEND_URL = "http://localhost:8081"

def test_backend():
    """Test the backend service"""
    print("Testing Backend Service...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        print(f"Backend Health: {response.json()['status']}")
        
        response = requests.get(f"{BACKEND_URL}/v1/models", timeout=10)
        models = response.json()['data']
        print(f"Available Models: {len(models)}")
        print(f"Sample models: {', '.join([m['id'] for m in models[:3]])}")
        return True
    except Exception as e:
        print(f"Backend Error: {e}")
        return False

def test_chat():
    """Test chat completion"""
    print("\nTesting Chat Completion...")
    
    payload = {
        "model": "claude-3-haiku",
        "messages": [
            {"role": "user", "content": "Say 'Demo successful!' and nothing else."}
        ],
        "max_tokens": 50,
        "temperature": 0.1
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BACKEND_URL}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        duration = time.time() - start_time
        
        content = result['choices'][0]['message']['content']
        tokens = result['usage']['total_tokens']
        
        print(f"Chat Response: {content.strip()}")
        print(f"Duration: {duration:.2f}s")
        print(f"Tokens Used: {tokens}")
        return True
        
    except Exception as e:
        print(f"Chat Error: {e}")
        return False

def main():
    """Run the demo"""
    success_count = 0
    
    if test_backend():
        success_count += 1
    
    if test_chat():
        success_count += 1
    
    print(f"\nDemo Results: {success_count}/2 tests passed")
    
    if success_count == 2:
        print("SUCCESS: Your integration is working perfectly!")
        print("\nNext Steps:")
        print("1. Open OpenWebUI at http://localhost:8080")
        print("2. Configure API endpoint: http://localhost:8081/v1")
        print("3. Start chatting with AWS Bedrock models!")
    else:
        print("Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()

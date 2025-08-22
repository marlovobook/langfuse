#!/usr/bin/env python3
"""
Integration test script for OpenWebUI + Bedrock + Langfuse integration.
Tests the complete flow from OpenWebUI API to Bedrock and Langfuse.
"""

import json
import time
import requests
from datetime import datetime
from typing import Dict, Any

# Configuration
BACKEND_URL = "http://localhost:8081"
LANGFUSE_URL = "http://localhost:3000"
OPENWEBUI_URL = "http://localhost:8080"

def print_status(message: str, status: str = "info"):
    """Print colored status messages."""
    colors = {
        "info": "\033[0;34m",     # Blue
        "success": "\033[0;32m",  # Green
        "warning": "\033[1;33m",  # Yellow
        "error": "\033[0;31m",    # Red
        "reset": "\033[0m"        # Reset
    }
    
    symbols = {
        "info": "ℹ️ ",
        "success": "✅ ",
        "warning": "⚠️ ",
        "error": "❌ "
    }
    
    color = colors.get(status, colors["info"])
    symbol = symbols.get(status, "")
    reset = colors["reset"]
    
    print(f"{color}{symbol}{message}{reset}")

def test_service_health(name: str, url: str, endpoint: str = "") -> bool:
    """Test if a service is healthy."""
    try:
        response = requests.get(f"{url}{endpoint}", timeout=10)
        if response.status_code == 200:
            print_status(f"{name} is healthy", "success")
            return True
        else:
            print_status(f"{name} returned status {response.status_code}", "warning")
            return False
    except requests.exceptions.RequestException as e:
        print_status(f"{name} is not accessible: {e}", "error")
        return False

def test_backend_models() -> bool:
    """Test backend models endpoint."""
    try:
        response = requests.get(f"{BACKEND_URL}/v1/models", timeout=30)
        if response.status_code == 200:
            models = response.json()
            model_count = len(models.get("data", []))
            print_status(f"Backend has {model_count} available models", "success")
            
            # Print some model names
            if model_count > 0:
                model_names = [model["id"] for model in models["data"][:3]]
                print_status(f"Sample models: {', '.join(model_names)}", "info")
            
            return True
        else:
            print_status(f"Models endpoint failed: {response.status_code}", "error")
            return False
    except Exception as e:
        print_status(f"Models test failed: {e}", "error")
        return False

def test_chat_completion(model: str = "claude-3-haiku") -> Dict[str, Any]:
    """Test chat completion endpoint."""
    try:
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": "Hello! This is a test message. Please respond briefly."}
            ],
            "temperature": 0.7,
            "max_tokens": 100,
            "stream": False
        }
        
        print_status(f"Testing chat completion with {model}...", "info")
        start_time = time.time()
        
        response = requests.post(
            f"{BACKEND_URL}/v1/chat/completions",
            json=payload,
            timeout=60
        )
        
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            usage = data["usage"]
            
            print_status(f"Chat completion successful ({response_time:.2f}s)", "success")
            print_status(f"Response: {content[:100]}...", "info")
            print_status(f"Tokens: {usage['total_tokens']} (prompt: {usage['prompt_tokens']}, completion: {usage['completion_tokens']})", "info")
            
            return {
                "success": True,
                "response_time": response_time,
                "content": content,
                "usage": usage
            }
        else:
            print_status(f"Chat completion failed: {response.status_code}", "error")
            print_status(f"Error: {response.text}", "error")
            return {"success": False, "error": response.text}
            
    except Exception as e:
        print_status(f"Chat completion test failed: {e}", "error")
        return {"success": False, "error": str(e)}

def test_streaming_completion(model: str = "claude-3-haiku") -> bool:
    """Test streaming chat completion."""
    try:
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": "Count from 1 to 5."}
            ],
            "stream": True
        }
        
        print_status(f"Testing streaming completion with {model}...", "info")
        
        response = requests.post(
            f"{BACKEND_URL}/v1/chat/completions",
            json=payload,
            stream=True,
            timeout=60
        )
        
        if response.status_code == 200:
            chunks_received = 0
            content_chunks = []
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # Remove 'data: '
                        if data_str.strip() == '[DONE]':
                            break
                        try:
                            chunk_data = json.loads(data_str)
                            chunks_received += 1
                            
                            if chunk_data['choices'][0]['delta'].get('content'):
                                content_chunks.append(chunk_data['choices'][0]['delta']['content'])
                        except json.JSONDecodeError:
                            continue
            
            full_content = ''.join(content_chunks)
            print_status(f"Streaming successful: {chunks_received} chunks received", "success")
            print_status(f"Streamed content: {full_content[:100]}...", "info")
            return True
        else:
            print_status(f"Streaming failed: {response.status_code}", "error")
            return False
            
    except Exception as e:
        print_status(f"Streaming test failed: {e}", "error")
        return False

def test_multiple_models() -> Dict[str, Any]:
    """Test multiple models."""
    models_to_test = ["claude-3-haiku", "claude-3-sonnet"]
    results = {}
    
    for model in models_to_test:
        print_status(f"\nTesting model: {model}", "info")
        result = test_chat_completion(model)
        results[model] = result
        
        if result["success"]:
            print_status(f"{model} test passed", "success")
        else:
            print_status(f"{model} test failed", "error")
        
        time.sleep(2)  # Brief pause between tests
    
    return results

def run_integration_tests():
    """Run all integration tests."""
    print_status("🧪 Starting OpenWebUI + Bedrock + Langfuse Integration Tests", "info")
    print_status("=" * 65, "info")
    
    # Test 1: Service Health Checks
    print_status("\n📊 Testing service health...", "info")
    backend_healthy = test_service_health("Backend", BACKEND_URL, "/health")
    langfuse_healthy = test_service_health("Langfuse", LANGFUSE_URL)
    openwebui_healthy = test_service_health("OpenWebUI", OPENWEBUI_URL)
    
    if not backend_healthy:
        print_status("Backend is not healthy. Stopping tests.", "error")
        return False
    
    # Test 2: Models Endpoint
    print_status("\n📋 Testing models endpoint...", "info")
    models_ok = test_backend_models()
    
    if not models_ok:
        print_status("Models endpoint failed. Stopping tests.", "error")
        return False
    
    # Test 3: Basic Chat Completion
    print_status("\n💬 Testing basic chat completion...", "info")
    basic_result = test_chat_completion()
    
    if not basic_result["success"]:
        print_status("Basic chat completion failed. Stopping tests.", "error")
        return False
    
    # Test 4: Streaming Completion
    print_status("\n🌊 Testing streaming completion...", "info")
    streaming_ok = test_streaming_completion()
    
    # Test 5: Multiple Models
    print_status("\n🔄 Testing multiple models...", "info")
    multi_results = test_multiple_models()
    
    # Summary
    print_status("\n📊 Test Summary", "info")
    print_status("=" * 50, "info")
    
    total_tests = 0
    passed_tests = 0
    
    services = [
        ("Backend Health", backend_healthy),
        ("Langfuse Health", langfuse_healthy),
        ("OpenWebUI Health", openwebui_healthy),
        ("Models Endpoint", models_ok),
        ("Basic Chat", basic_result["success"]),
        ("Streaming Chat", streaming_ok)
    ]
    
    for name, status in services:
        total_tests += 1
        if status:
            passed_tests += 1
            print_status(f"{name}: PASSED", "success")
        else:
            print_status(f"{name}: FAILED", "error")
    
    # Model tests
    for model, result in multi_results.items():
        total_tests += 1
        if result["success"]:
            passed_tests += 1
            print_status(f"{model}: PASSED", "success")
        else:
            print_status(f"{model}: FAILED", "error")
    
    print_status(f"\nResults: {passed_tests}/{total_tests} tests passed", 
                 "success" if passed_tests == total_tests else "warning")
    
    if passed_tests == total_tests:
        print_status("\n🎉 All integration tests passed!", "success")
        print_status("Your OpenWebUI + Bedrock + Langfuse integration is working correctly!", "success")
    else:
        print_status(f"\n⚠️  {total_tests - passed_tests} tests failed. Please check the configuration.", "warning")
    
    # Next steps
    print_status("\n📝 Next Steps:", "info")
    print_status("1. Open OpenWebUI at http://localhost:8080", "info")
    print_status("2. Configure backend URL in OpenWebUI settings", "info")
    print_status("3. Check Langfuse dashboard at http://localhost:3000", "info")
    print_status("4. Start chatting and monitor traces in Langfuse!", "info")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)

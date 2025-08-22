#!/usr/bin/env python3
"""
Demo script for OpenWebUI + AWS Bedrock + Langfuse integration.
Demonstrates the complete workflow and observability features.
"""

import json
import time
import requests
from datetime import datetime
from typing import List, Dict

# Configuration
BACKEND_URL = "http://localhost:8081"
LANGFUSE_URL = "http://localhost:3000"

def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)

def print_step(step: str):
    """Print a step in the demo."""
    print(f"\n📝 {step}")
    print("-" * 40)

def demo_model_discovery():
    """Demonstrate model discovery."""
    print_header("OpenWebUI + Bedrock + Langfuse Integration Demo")
    
    print_step("Step 1: Discovering Available Models")
    
    try:
        response = requests.get(f"{BACKEND_URL}/v1/models")
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Found {len(models['data'])} available models:")
            
            for model in models['data'][:5]:  # Show first 5
                print(f"   • {model['id']} (by {model['owned_by']})")
            
            if len(models['data']) > 5:
                print(f"   ... and {len(models['data']) - 5} more")
                
            return [model['id'] for model in models['data']]
        else:
            print(f"❌ Failed to get models: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def demo_single_conversation(model: str, prompt: str) -> Dict:
    """Demonstrate a single conversation."""
    print(f"\n💬 Testing conversation with {model}")
    print(f"User: {prompt}")
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 200
    }
    
    start_time = time.time()
    
    try:
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
            
            print(f"Assistant: {content}")
            print(f"📊 Stats: {usage['total_tokens']} tokens in {response_time:.2f}s")
            
            return {
                "success": True,
                "content": content,
                "usage": usage,
                "response_time": response_time
            }
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return {"success": False}
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return {"success": False}

def demo_streaming_conversation(model: str, prompt: str):
    """Demonstrate streaming conversation."""
    print(f"\n🌊 Testing streaming with {model}")
    print(f"User: {prompt}")
    print("Assistant: ", end="", flush=True)
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 150,
        "stream": True
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/v1/chat/completions",
            json=payload,
            stream=True,
            timeout=60
        )
        
        if response.status_code == 200:
            content_parts = []
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]
                        if data_str.strip() == '[DONE]':
                            break
                        try:
                            chunk_data = json.loads(data_str)
                            if chunk_data['choices'][0]['delta'].get('content'):
                                content = chunk_data['choices'][0]['delta']['content']
                                print(content, end="", flush=True)
                                content_parts.append(content)
                                time.sleep(0.02)  # Slight delay for visual effect
                        except json.JSONDecodeError:
                            continue
            
            print(f"\n📊 Streaming completed - {len(content_parts)} chunks received")
            return True
        else:
            print(f"\n❌ Streaming failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ Streaming error: {e}")
        return False

def demo_model_comparison():
    """Demonstrate model comparison."""
    print_step("Step 3: Model Comparison")
    
    models_to_compare = ["claude-3-haiku", "claude-3-sonnet"]
    prompt = "Explain quantum computing in simple terms."
    
    results = {}
    
    for model in models_to_compare:
        print(f"\n🔍 Testing {model}...")
        result = demo_single_conversation(model, prompt)
        
        if result["success"]:
            results[model] = {
                "tokens": result["usage"]["total_tokens"],
                "time": result["response_time"],
                "length": len(result["content"])
            }
    
    # Show comparison
    if len(results) > 1:
        print(f"\n📊 Model Comparison:")
        print(f"{'Model':<20} {'Tokens':<10} {'Time (s)':<10} {'Length':<10}")
        print("-" * 50)
        for model, stats in results.items():
            print(f"{model:<20} {stats['tokens']:<10} {stats['time']:<10.2f} {stats['length']:<10}")

def demo_conversation_flow():
    """Demonstrate a multi-turn conversation."""
    print_step("Step 4: Multi-turn Conversation")
    
    model = "claude-3-haiku"
    conversation = [
        "Hello! I'm interested in learning about AI.",
        "Can you explain machine learning?",
        "What about deep learning? How is it different?",
        "Thanks! Can you give me a simple example?"
    ]
    
    messages = []
    
    for i, user_message in enumerate(conversation):
        print(f"\n💬 Turn {i + 1}")
        print(f"User: {user_message}")
        
        # Add user message to conversation
        messages.append({"role": "user", "content": user_message})
        
        payload = {
            "model": model,
            "messages": messages.copy(),
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/v1/chat/completions",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                assistant_content = data["choices"][0]["message"]["content"]
                usage = data["usage"]
                
                print(f"Assistant: {assistant_content}")
                print(f"📊 Tokens this turn: {usage['total_tokens']}")
                
                # Add assistant response to conversation
                messages.append({"role": "assistant", "content": assistant_content})
                
            else:
                print(f"❌ Error: {response.status_code}")
                break
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            break
        
        time.sleep(1)  # Brief pause between turns

def demo_langfuse_integration():
    """Show how to check Langfuse for observability."""
    print_step("Step 5: Langfuse Observability")
    
    print("🔍 All conversations are automatically tracked in Langfuse!")
    print(f"📊 Open Langfuse dashboard: {LANGFUSE_URL}")
    print("\nIn Langfuse, you can see:")
    print("   • Real-time conversation traces")
    print("   • Token usage and costs")
    print("   • Response times and performance")
    print("   • Error tracking and debugging")
    print("   • User session analytics")
    print("   • Model comparison metrics")
    
    try:
        # Check if Langfuse is accessible
        response = requests.get(LANGFUSE_URL, timeout=5)
        if response.status_code == 200:
            print(f"\n✅ Langfuse is accessible at {LANGFUSE_URL}")
        else:
            print(f"\n⚠️  Langfuse returned status {response.status_code}")
    except Exception as e:
        print(f"\n⚠️  Langfuse not accessible: {e}")

def demo_openwebui_integration():
    """Show OpenWebUI integration."""
    print_step("Step 6: OpenWebUI Integration")
    
    print("🌐 OpenWebUI provides a modern chat interface!")
    print(f"📱 Open OpenWebUI: http://localhost:8080")
    print("\nOpenWebUI Features:")
    print("   • Modern, responsive chat interface")
    print("   • Conversation history")
    print("   • Multiple model selection")
    print("   • Real-time streaming responses")
    print("   • User authentication (optional)")
    print("   • Mobile-friendly design")
    
    print(f"\n🔧 Configuration:")
    print(f"   • Backend URL: http://backend:8081")
    print(f"   • Available models: All AWS Bedrock models")
    print(f"   • Observability: Automatic Langfuse tracking")

def run_complete_demo():
    """Run the complete demo."""
    print("🎬 Welcome to the OpenWebUI + AWS Bedrock + Langfuse Demo!")
    print("This demo will showcase the complete integration in action.")
    
    # Step 1: Model Discovery
    available_models = demo_model_discovery()
    
    if not available_models:
        print("❌ Cannot proceed without available models. Please check your setup.")
        return False
    
    # Step 2: Basic Conversations
    print_step("Step 2: Basic Conversations")
    demo_single_conversation("claude-3-haiku", "What is artificial intelligence?")
    
    # Step 2.5: Streaming Demo
    demo_streaming_conversation("claude-3-haiku", "Tell me a short story about a robot.")
    
    # Step 3: Model Comparison
    demo_model_comparison()
    
    # Step 4: Multi-turn Conversation
    demo_conversation_flow()
    
    # Step 5: Langfuse Integration
    demo_langfuse_integration()
    
    # Step 6: OpenWebUI Integration
    demo_openwebui_integration()
    
    # Summary
    print_header("Demo Complete! 🎉")
    print("✅ All components are working together:")
    print("   • AWS Bedrock: Providing AI models")
    print("   • Langfuse: Tracking and observability")
    print("   • OpenWebUI: Modern chat interface")
    print("   • Custom Backend: Seamless integration")
    
    print(f"\n🌐 Next Steps:")
    print(f"   1. Open OpenWebUI: http://localhost:8080")
    print(f"   2. Start chatting with AI models")
    print(f"   3. Monitor in Langfuse: {LANGFUSE_URL}")
    print(f"   4. Explore different models and features")
    
    print(f"\n📚 For more information, see the README.md file.")
    
    return True

if __name__ == "__main__":
    success = run_complete_demo()
    exit(0 if success else 1)

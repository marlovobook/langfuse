#!/usr/bin/env python3
"""
Demo script to test AWS Bedrock + Langfuse integration with local Langfuse instance.
This script simulates AWS Bedrock responses to test the Langfuse integration without needing AWS credentials.
"""

import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

def demo_local_langfuse():
    """Demo script that works with local Langfuse without requiring AWS credentials."""
    
    # Load environment variables
    load_dotenv()
    
    print("🚀 AWS Bedrock + Local Langfuse Integration Demo")
    print("=" * 60)
    
    # Check configuration
    host = os.getenv('LANGFUSE_HOST', 'http://localhost:3000')
    secret_key = os.getenv('LANGFUSE_SECRET_KEY')
    public_key = os.getenv('LANGFUSE_PUBLIC_KEY')
    
    print(f"Langfuse Host: {host}")
    
    if not secret_key or not public_key or \
       secret_key == "sk-lf-your-secret-key-here" or \
       public_key == "pk-lf-your-public-key-here":
        print("❌ Please configure your API keys in .env file:")
        print("  LANGFUSE_SECRET_KEY=sk-lf-...")
        print("  LANGFUSE_PUBLIC_KEY=pk-lf-...")
        print("\nGet your keys from: http://localhost:3000 → Project Settings → API Keys")
        return False
    
    try:
        from langfuse import Langfuse
        
        # Initialize Langfuse client
        langfuse = Langfuse(
            host=host,
            secret_key=secret_key,
            public_key=public_key
        )
        
        print("✅ Connected to local Langfuse")
        
        # Demo 1: Simple trace with event
        print("\n📝 Demo 1: Creating a simple trace...")
        
        # Create a simple event 
        event = langfuse.create_event(
            name="bedrock-demo-simple",
            input={"role": "user", "content": "What is machine learning?"},
            output="Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed.",
            metadata={
                "demo": True,
                "integration": "aws-bedrock",
                "langfuse_host": host,
                "model": "anthropic.claude-3-sonnet-20240229-v1:0",
                "aws_region": "us-east-1",
                "model_provider": "anthropic",
                "simulated": True
            }
        )
        
        print(f"✅ Created event: {event.id if hasattr(event, 'id') else 'created'}")
        
        # Demo 2: Conversation with multiple messages
        print("\n💬 Demo 2: Creating a conversation trace...")
        
        conversation_trace_id = langfuse.create_trace_id()
        
        # Update conversation trace
        langfuse.update_current_trace(
            name="bedrock-demo-conversation",
            user_id="demo-user", 
            session_id=f"demo-conversation-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            metadata={
                "demo": True,
                "type": "conversation"
            }
        )
        
        # First message
        gen1 = langfuse.start_generation(
            name="claude-message-1",
            model="anthropic.claude-3-sonnet-20240229-v1:0",
            input=[{"role": "user", "content": "Hello! Can you help me understand AI?"}],
            output="Hello! I'd be happy to help you understand AI. Artificial Intelligence refers to computer systems that can perform tasks that typically require human intelligence.",
            usage_details={"input": 12, "output": 25, "total": 37}
        )
        
        # Second message
        gen2 = langfuse.start_generation(
            name="claude-message-2",
            model="anthropic.claude-3-sonnet-20240229-v1:0",
            input=[
                {"role": "user", "content": "Hello! Can you help me understand AI?"},
                {"role": "assistant", "content": "Hello! I'd be happy to help you understand AI. Artificial Intelligence refers to computer systems that can perform tasks that typically require human intelligence."},
                {"role": "user", "content": "What are some practical applications?"}
            ],
            output="AI has many practical applications including: 1) Virtual assistants like Siri and Alexa, 2) Recommendation systems on Netflix and Amazon, 3) Medical diagnosis and drug discovery, 4) Autonomous vehicles, 5) Fraud detection in banking.",
            usage_details={"input": 45, "output": 42, "total": 87}
        )
        
        print(f"✅ Created conversation trace: {conversation_trace_id}")
        print(f"✅ Added 2 generations to conversation")
        
        # Demo 3: Error handling with event
        print("\n⚠️  Demo 3: Creating a trace with error...")
        
        error_event = langfuse.create_event(
            name="bedrock-demo-error",
            input={"role": "user", "content": "This would cause an error"},
            level="ERROR",
            status_message="Simulated AWS Bedrock API error",
            metadata={
                "demo": True,
                "type": "error_example",
                "model": "anthropic.claude-3-sonnet-20240229-v1:0",
                "error_type": "ThrottlingException",
                "error_message": "Rate limit exceeded",
                "simulated": True
            }
        )
        
        print(f"✅ Created error event: {error_event.id if hasattr(error_event, 'id') else 'created'}")
        
        # Flush all data to Langfuse
        print("\n📤 Sending data to Langfuse...")
        langfuse.flush()
        
        print("\n🎉 Demo completed successfully!")
        print(f"🌐 View your traces at: {host}")
        print(f"📊 Check the dashboard for:")
        print(f"   - 3 demo traces")
        print(f"   - Token usage statistics")
        print(f"   - Error tracking")
        print(f"   - Session analytics")
        
        return True
        
    except ImportError:
        print("❌ Langfuse library not found. Please install it:")
        print("pip install langfuse")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure local Langfuse is running: http://localhost:3000")
        print("2. Check your API keys in .env file")
        print("3. Verify the keys format: sk-lf-... and pk-lf-...")
        return False

if __name__ == "__main__":
    success = demo_local_langfuse()
    
    if not success:
        print("\n💡 To fix issues:")
        print("1. Make sure Langfuse is running: docker-compose up -d (from main langfuse directory)")
        print("2. Configure .env file with your API keys")
        print("3. Run: python test_local_connection.py")
    else:
        print("\n🚀 Ready for AWS Bedrock integration!")
        print("Next steps:")
        print("1. Configure AWS credentials in .env")
        print("2. Run: python examples/basic_chat.py")
        print("3. Or run: python examples/model_comparison.py")

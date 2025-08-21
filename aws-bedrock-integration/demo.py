"""Quick demo script to test the AWS Bedrock + Langfuse integration."""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def check_environment():
    """Check if environment is properly configured."""
    print("🔍 Checking environment configuration...")
    
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY', 
        'AWS_REGION',
        'LANGFUSE_SECRET_KEY',
        'LANGFUSE_PUBLIC_KEY',
        'LANGFUSE_HOST'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("📝 Please update your .env file with the required credentials.")
        return False
    
    print("✅ All environment variables are configured!")
    return True

def test_imports():
    """Test if all required packages can be imported."""
    print("📦 Testing package imports...")
    
    try:
        import boto3
        print("✅ boto3 imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import boto3: {e}")
        return False
    
    try:
        import langfuse
        print("✅ langfuse imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import langfuse: {e}")
        return False
    
    try:
        from bedrock_langfuse import BedrockLangfuseClient
        print("✅ bedrock_langfuse imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import bedrock_langfuse: {e}")
        return False
    
    return True

def quick_functionality_test():
    """Run a quick functionality test."""
    print("🧪 Running quick functionality test...")
    
    try:
        from bedrock_langfuse import BedrockLangfuseClient, ChatMessage, MessageRole
        
        # Test client initialization
        client = BedrockLangfuseClient()
        print("✅ Client initialized successfully")
        
        # Test model listing
        models = client.list_available_models()
        print(f"✅ Found {len(models)} available models")
        
        # Test message creation
        message = ChatMessage(role=MessageRole.USER, content="Test message")
        print("✅ ChatMessage created successfully")
        
        # Test model info
        model_id = "anthropic.claude-3-haiku-20240307-v1:0"
        info = client.get_model_info(model_id)
        print(f"✅ Model info retrieved: {info['name']} by {info['provider']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def demo_chat_completion():
    """Demonstrate a simple chat completion."""
    print("💬 Running demo chat completion...")
    
    if not check_environment():
        print("⚠️  Skipping chat completion demo due to missing configuration")
        return False
    
    try:
        from bedrock_langfuse import BedrockLangfuseClient, ChatMessage, MessageRole, ModelConfig
        
        # Initialize client
        client = BedrockLangfuseClient(debug=False)
        
        # Create a simple chat completion
        response = client.chat_completion(
            model="anthropic.claude-3-haiku-20240307-v1:0",
            messages=[
                ChatMessage(
                    role=MessageRole.USER, 
                    content="Say hello and briefly introduce yourself as an AI assistant."
                )
            ],
            config=ModelConfig(temperature=0.5, max_tokens=100),
            session_id="demo-session",
            user_id="demo-user",
            metadata={"demo": True, "test_type": "quick_demo"},
            tags=["demo", "test"]
        )
        
        print(f"🤖 Model: {response.model}")
        print(f"📝 Response: {response.content}")
        print(f"📊 Tokens: {response.usage.total_tokens}")
        print(f"💰 Cost: ${response.usage.estimated_cost:.6f}")
        print(f"⏱️  Time: {response.response_time:.2f}s")
        print(f"🔗 Trace ID: {response.trace_id}")
        
        # Flush Langfuse data
        client.flush()
        
        print("✅ Demo chat completion successful!")
        print("🎯 Check your Langfuse dashboard to see the logged interaction!")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo chat completion failed: {e}")
        return False

def main():
    """Main demo function."""
    print("🚀 AWS Bedrock + Langfuse Integration Demo")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Please run 'pip install -r requirements.txt'")
        return
    
    # Test functionality
    if not quick_functionality_test():
        print("\n❌ Functionality test failed. Please check your installation.")
        return
    
    print("\n✅ All basic tests passed!")
    
    # Ask user if they want to run the live demo
    print("\n🤔 Would you like to run a live chat completion demo?")
    print("   This will make an actual API call to AWS Bedrock and log to Langfuse.")
    print("   Make sure your .env file is configured with valid credentials.")
    
    try:
        choice = input("\n💬 Run live demo? (y/N): ").strip().lower()
        if choice in ['y', 'yes']:
            demo_chat_completion()
        else:
            print("⏭️  Skipping live demo.")
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user.")
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("📚 Next steps:")
    print("   - Check out the examples/ directory for more demos")
    print("   - Run 'python examples/basic_chat.py' for a full example")
    print("   - Visit your Langfuse dashboard to see logged interactions")
    print("   - Read the README.md for detailed documentation")

if __name__ == "__main__":
    main()

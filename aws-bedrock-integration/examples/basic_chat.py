"""Basic chat completion example with AWS Bedrock and Langfuse."""

import os
from dotenv import load_dotenv
from bedrock_langfuse import BedrockLangfuseClient, ChatMessage, MessageRole, ModelConfig

# Load environment variables
load_dotenv()

def main():
    """Demonstrate basic chat completion with Langfuse tracking."""
    
    # Initialize the client
    # The client will automatically use:
    # 1. AWS_PROFILE from environment (recommended)
    # 2. AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY from environment (fallback)
    # 3. Default AWS credentials chain (IAM roles, etc.)
    client = BedrockLangfuseClient(debug=True)
    
    # Alternative: Explicitly specify AWS profile
    # client = BedrockLangfuseClient(aws_profile="your-profile-name", debug=True)
    
    # Alternative: Explicitly specify credentials (not recommended)
    # client = BedrockLangfuseClient(
    #     aws_access_key_id="your-key",
    #     aws_secret_access_key="your-secret",
    #     aws_region="us-east-1",
    #     debug=True
    # )
    
    # Simple chat completion
    print("🤖 Basic Chat Completion Example")
    print("=" * 50)
    
    try:
        response = client.chat_completion(
            model="anthropic.claude-3-haiku-20240307-v1:0",  # Using cost-effective model
            messages=[
                ChatMessage(role=MessageRole.USER, content="What is machine learning? Explain in simple terms.")
            ],
            session_id="basic-example-session",
            user_id="demo-user",
            metadata={"example_type": "basic_chat", "topic": "machine_learning"},
            tags=["demo", "education", "ml"]
        )
        
        print(f"Model: {response.model}")
        print(f"Response: {response.content}")
        print(f"Tokens used: {response.usage.total_tokens}")
        print(f"Estimated cost: ${response.usage.estimated_cost:.6f}")
        print(f"Response time: {response.response_time:.2f}s")
        print(f"Trace ID: {response.trace_id}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print("\n" + "=" * 50)
    
    # Chat with custom configuration
    print("🔧 Chat with Custom Configuration")
    print("=" * 50)
    
    try:
        # Custom model configuration
        config = ModelConfig(
            temperature=0.3,  # More focused responses
            max_tokens=500,   # Shorter responses
            top_p=0.8
        )
        
        response = client.chat_completion(
            model="anthropic.claude-3-sonnet-20240229-v1:0",
            messages=[
                ChatMessage(role=MessageRole.SYSTEM, content="You are a helpful coding assistant."),
                ChatMessage(role=MessageRole.USER, content="Write a Python function to calculate fibonacci numbers.")
            ],
            config=config,
            session_id="coding-example-session",
            user_id="demo-user",
            metadata={"example_type": "coding_assistance", "language": "python"},
            tags=["demo", "coding", "python", "fibonacci"]
        )
        
        print(f"Model: {response.model}")
        print(f"Response: {response.content}")
        print(f"Tokens used: {response.usage.total_tokens}")
        print(f"Estimated cost: ${response.usage.estimated_cost:.6f}")
        print(f"Response time: {response.response_time:.2f}s")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Flush Langfuse data
    client.flush()
    print("\n✅ All interactions have been logged to Langfuse!")

if __name__ == "__main__":
    main()

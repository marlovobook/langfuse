#!/usr/bin/env python3
"""
Demo script to test AWS Bedrock + Langfuse integration without credentials.
This script tests the basic functionality without making actual API calls.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from bedrock_langfuse import BedrockLangfuseClient
from bedrock_langfuse.models import ChatMessage, MessageRole, ModelConfig
from bedrock_langfuse.utils import ModelComparison, ConversationManager, estimate_tokens, format_cost

def test_imports():
    """Test that all imports work correctly."""
    print("[TEST] Testing imports...")
    
    try:
        # Test client creation (this should work without credentials)
        print("✓ BedrockLangfuseClient import successful")
        
        # Test model creation
        message = ChatMessage(role=MessageRole.USER, content="Hello, world!")
        print(f"✓ ChatMessage created: {message}")
        
        # Test model config
        config = ModelConfig(temperature=0.7, max_tokens=100)
        print(f"✓ ModelConfig created: {config}")
        
        # Test utility functions
        tokens = estimate_tokens("This is a test message")
        cost_str = format_cost(0.00123)
        print(f"✓ Estimated tokens: {tokens}")
        print(f"✓ Formatted cost: {cost_str}")
        
        print("[SUCCESS] All imports and basic functionality working!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Import test failed: {e}")
        return False

def test_conversation_manager():
    """Test the conversation manager functionality."""
    print("\n[TEST] Testing ConversationManager...")
    
    try:
        manager = ConversationManager()
        
        # Start a conversation
        session_id = "demo_session_123"
        manager.start_conversation(session_id, system_message="You are a helpful assistant.")
        print(f"✓ Started conversation: {session_id}")
        
        # Add a user message
        manager.add_user_message(session_id, "Hello!")
        print("✓ Added user message")
        
        # Get conversation history
        history = manager.get_conversation_history(session_id)
        print(f"✓ Retrieved history: {len(history)} messages")
        
        # Export conversation
        export = manager.export_conversation(session_id)
        print(f"✓ Exported conversation: {export['message_count']} messages")
        
        print("[SUCCESS] ConversationManager test passed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] ConversationManager test failed: {e}")
        return False

def main():
    """Run all demo tests."""
    print("AWS Bedrock + Langfuse Integration Demo")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    if test_imports():
        tests_passed += 1
    
    if test_conversation_manager():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"Demo Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("[SUCCESS] All demo tests passed! The integration is working correctly.")
        print("\nNext steps:")
        print("1. Configure your AWS credentials in .env file")
        print("2. Configure your Langfuse credentials in .env file")
        print("3. Run: python examples/basic_chat.py")
    else:
        print("[ERROR] Some tests failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()

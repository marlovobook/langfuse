#!/usr/bin/env python3
"""
Simple test script to verify local Langfuse connection works.
"""

import os
from dotenv import load_dotenv

def test_local_langfuse():
    # Load environment variables
    load_dotenv()
    
    host = os.getenv('LANGFUSE_HOST')
    secret_key = os.getenv('LANGFUSE_SECRET_KEY')
    public_key = os.getenv('LANGFUSE_PUBLIC_KEY')
    
    print(f"Testing connection to: {host}")
    
    if not all([host, secret_key, public_key]):
        print("❌ Please update your .env file with the API keys first")
        print("Required:")
        print("  LANGFUSE_HOST=http://localhost:3000")
        print("  LANGFUSE_SECRET_KEY=sk-lf-...")
        print("  LANGFUSE_PUBLIC_KEY=pk-lf-...")
        return False
    
    if secret_key == "sk-lf-your-secret-key-here" or public_key == "pk-lf-your-public-key-here":
        print("❌ Please replace the placeholder keys with your actual API keys")
        return False
    
    try:
        from langfuse import Langfuse
        
        # Initialize Langfuse client
        langfuse = Langfuse(
            host=host,
            secret_key=secret_key,
            public_key=public_key
        )
        
        # Create a test event
        event = langfuse.create_event(
            name="test-connection",
            input="Hello, local Langfuse!",
            output="Connection successful!",
            metadata={
                "test": True,
                "connection_test": True
            }
        )
        
        # Flush to ensure data is sent
        langfuse.flush()
        
        print("✅ Connection test successful!")
        print("✅ Test event created in Langfuse")
        print(f"✅ Event ID: {event.id if hasattr(event, 'id') else 'created'}")
        print(f"✅ View traces at: {host}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure your API keys are correct")
        print("2. Check that Langfuse is running at http://localhost:3000")
        print("3. Verify the keys have the right format (sk-lf-... and pk-lf-...)")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Local Langfuse Connection Test")
    print("=" * 50)
    
    success = test_local_langfuse()
    
    if success:
        print("\n🎉 Ready to use AWS Bedrock with local Langfuse!")
        print("You can now run:")
        print("  python examples/basic_chat.py")
        print("  python demo_test.py")
    else:
        print("\n❌ Please fix the issues above and try again")
        print("Run: python test_local_connection.py")

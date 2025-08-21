#!/usr/bin/env python3
"""
Script to help set up the local Langfuse connection and create API keys.
"""

import os
import sys
import time
import webbrowser
from pathlib import Path

def main():
    print("=" * 60)
    print("AWS Bedrock + Langfuse Local Setup")
    print("=" * 60)
    
    # Check if local Langfuse is running
    print("\n1. Checking local Langfuse instance...")
    try:
        import requests
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Local Langfuse is running at http://localhost:3000")
        else:
            print("❌ Local Langfuse is not responding properly")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to local Langfuse: {e}")
        print("\nTo start Langfuse locally:")
        print("1. Go to the main langfuse directory: cd ..")
        print("2. Run: docker-compose up -d")
        print("3. Wait for all services to start")
        print("4. Access http://localhost:3000")
        return False
    
    # Guide user to set up API keys
    print("\n2. Setting up API keys...")
    print("Please follow these steps:")
    print("   a. Open http://localhost:3000 in your browser")
    print("   b. Sign up or log in")
    print("   c. Create a new organization (if needed)")
    print("   d. Create a new project")
    print("   e. Go to project settings")
    print("   f. Create new API keys")
    print("   g. Copy the keys")
    
    # Ask if user wants to open browser
    open_browser = input("\nWould you like to open the browser now? (y/n): ").lower().strip()
    if open_browser == 'y':
        webbrowser.open("http://localhost:3000")
        print("Browser opened. Please follow the steps above.")
    
    # Guide to update .env file
    print("\n3. Updating .env file...")
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            env_file.write_text(env_example.read_text())
            print("✅ Created .env file from .env.example")
        else:
            print("❌ No .env.example file found")
            return False
    
    print(f"✅ .env file exists at: {env_file.absolute()}")
    print("\nPlease update your .env file with:")
    print("   LANGFUSE_HOST=http://localhost:3000")
    print("   LANGFUSE_SECRET_KEY=sk-lf-your-secret-key")
    print("   LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key")
    
    # Test connection option
    print("\n4. Testing connection...")
    test_now = input("Do you want to test the connection now? (y/n): ").lower().strip()
    
    if test_now == 'y':
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        host = os.getenv('LANGFUSE_HOST')
        secret_key = os.getenv('LANGFUSE_SECRET_KEY')
        public_key = os.getenv('LANGFUSE_PUBLIC_KEY')
        
        if not all([host, secret_key, public_key]):
            print("❌ Please update your .env file with the API keys first")
            return False
        
        print(f"Testing connection to: {host}")
        
        try:
            from langfuse import Langfuse
            langfuse = Langfuse(
                host=host,
                secret_key=secret_key,
                public_key=public_key
            )
            
            # Create a test event
            event = langfuse.create_event(
                name="test-connection",
                input="Hello, world!",
                output="Hello back!",
                metadata={
                    "test": True,
                    "connection_test": True
                }
            )
            
            print("✅ Connection test successful!")
            print("✅ Test trace created in Langfuse")
            
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("You can now run the examples:")
    print("   python examples/basic_chat.py")
    print("   python examples/model_comparison.py")
    print("   python demo_test.py")
    print("\nView your traces at: http://localhost:3000")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

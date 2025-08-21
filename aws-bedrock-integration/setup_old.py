#!/usr/bin/env python3
"""
Simple setup script for AWS Bedrock + Langfuse integration project.
This should not be executed automatically during package installation.
Run python setup.py manually after installation to configure the environment.
"""

import subprocess
import sys
import os
from pathlib import Path
from setuptools import setup, find_packages

# Only run setup logic if called directly
if __name__ == "__main__":
    def run_command(command, description=""):
        """Run a command and handle errors."""
        print(f"[SETUP] {description}")
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            if result.stdout:
                print(f"[SUCCESS] {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Error: {e}")
            if e.stderr:
                print(f"Error details: {e.stderr}")
            return False

    def check_python_version():
        """Check if Python version is compatible."""
        if sys.version_info < (3, 8):
            print("[ERROR] Python 3.8 or higher is required.")
            return False
        print(f"[SUCCESS] Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected")
        return True

def install_dependencies():
    """Install project dependencies."""
    print("[INSTALL] Installing dependencies...")
    
    # Install main dependencies
    if not run_command("pip install -r requirements.txt", "Installing main dependencies"):
        return False
    
    # Install development dependencies for testing
    dev_deps = ["pytest", "pytest-asyncio", "black", "flake8", "mypy"]
    for dep in dev_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            print(f"[WARNING] Warning: Failed to install {dep}")
    
    return True

def setup_environment():
    """Setup environment configuration."""
    print("[SETUP] Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        # Copy example file
        env_file.write_text(env_example.read_text())
        print("[SUCCESS] Created .env file from .env.example")
        print("[WARNING] Please edit .env file with your actual credentials!")
    elif env_file.exists():
        print("[SUCCESS] .env file already exists")
    else:
        print("[ERROR] No .env.example file found")
        return False
    
    return True

def run_tests():
    """Run the test suite."""
    print("[TEST] Running tests...")
    
    if not run_command("python -m pytest tests/ -v", "Running test suite"):
        print("[WARNING] Some tests failed, but setup can continue")
        return True  # Don't fail setup for test failures
    
    print("[SUCCESS] All tests passed!")
    return True

def check_aws_credentials():
    """Check if AWS credentials are configured."""
    print("[CHECK] Checking AWS configuration...")
    
    # Check for AWS credentials
    aws_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    if aws_key and aws_secret:
        print("[SUCCESS] AWS credentials found in environment")
        return True
    
    # Check AWS CLI configuration
    aws_config_file = Path.home() / ".aws" / "credentials"
    if aws_config_file.exists():
        print("[SUCCESS] AWS credentials file found")
        return True
    
    print("[WARNING] AWS credentials not found. Please configure:")
    print("   - Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")
    print("   - Or run 'aws configure' if you have AWS CLI installed")
    print("   - Or update the .env file with your credentials")
    return False

def check_langfuse_config():
    """Check if Langfuse configuration is available."""
    print("[CHECK] Checking Langfuse configuration...")
    
    langfuse_secret = os.getenv('LANGFUSE_SECRET_KEY')
    langfuse_public = os.getenv('LANGFUSE_PUBLIC_KEY')
    
    if langfuse_secret and langfuse_public:
        print("[SUCCESS] Langfuse credentials found in environment")
        return True
    
    print("[WARNING] Langfuse credentials not found. Please:")
    print("   - Sign up at https://cloud.langfuse.com")
    print("   - Create a new project")
    print("   - Get your API keys from project settings")
    print("   - Update the .env file with your credentials")
    return False

def main():
    """Main setup function."""
    print("[SETUP] AWS Bedrock + Langfuse Integration Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("[ERROR] Failed to install dependencies")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("[ERROR] Failed to setup environment")
        sys.exit(1)
    
    # Check configurations
    aws_ok = check_aws_credentials()
    langfuse_ok = check_langfuse_config()
    
    # Run tests
    run_tests()
    
    print("\n" + "=" * 50)
    print("[SUCCESS] Setup Complete!")
    print("=" * 50)
    
    if aws_ok and langfuse_ok:
        print("[SUCCESS] All configurations look good!")
        print("[INFO] You can now run the examples:")
        print("   python examples/basic_chat.py")
        print("   python examples/model_comparison.py")
        print("   python examples/conversation.py")
    else:
        print("[WARNING] Setup completed but some configurations need attention:")
        if not aws_ok:
            print("   - Configure AWS credentials")
        if not langfuse_ok:
            print("   - Configure Langfuse credentials")
        print("[INFO] Please see the README.md for detailed setup instructions")
    
    print("\n[INFO] Documentation:")
    print("   - README.md: Project overview and setup")
    print("   - examples/: Example scripts")
    print("   - tests/: Test suite")
    print("\n[HELP] Need help? Check the documentation or create an issue!")

if __name__ == "__main__":
    main()

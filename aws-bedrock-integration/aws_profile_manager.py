#!/usr/bin/env python3
"""
AWS Profile Management Utility for Bedrock-Langfuse Integration
"""

import os
import sys
import subprocess
import configparser
from pathlib import Path
from typing import List, Dict, Optional

def get_aws_credentials_file() -> Path:
    """Get the AWS credentials file path."""
    aws_dir = Path.home() / '.aws'
    return aws_dir / 'credentials'

def get_aws_config_file() -> Path:
    """Get the AWS config file path."""
    aws_dir = Path.home() / '.aws'
    return aws_dir / 'config'

def list_aws_profiles() -> List[str]:
    """List all available AWS profiles."""
    credentials_file = get_aws_credentials_file()
    config_file = get_aws_config_file()
    
    profiles = set()
    
    # Check credentials file
    if credentials_file.exists():
        config = configparser.ConfigParser()
        config.read(credentials_file)
        profiles.update(config.sections())
    
    # Check config file
    if config_file.exists():
        config = configparser.ConfigParser()
        config.read(config_file)
        for section in config.sections():
            if section.startswith('profile '):
                profiles.add(section.replace('profile ', ''))
            elif section == 'default':
                profiles.add('default')
    
    return sorted(list(profiles))

def check_aws_cli_installed() -> bool:
    """Check if AWS CLI is installed."""
    try:
        subprocess.run(['aws', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_profile_info(profile_name: str) -> Optional[Dict[str, str]]:
    """Get information about a specific AWS profile."""
    credentials_file = get_aws_credentials_file()
    
    if not credentials_file.exists():
        return None
    
    config = configparser.ConfigParser()
    config.read(credentials_file)
    
    if profile_name in config.sections():
        return dict(config[profile_name])
    
    return None

def test_aws_profile(profile_name: str) -> bool:
    """Test if an AWS profile works with Bedrock."""
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
        
        # Create session with profile
        session = boto3.Session(profile_name=profile_name)
        bedrock_client = session.client('bedrock-runtime', region_name='us-east-1')
        
        # Try to list foundation models (this requires minimal permissions)
        try:
            bedrock_models_client = session.client('bedrock', region_name='us-east-1')
            bedrock_models_client.list_foundation_models()
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                print(f"⚠️  Profile '{profile_name}' works but may lack Bedrock permissions")
                return True
            else:
                print(f"❌ Profile '{profile_name}' failed: {error_code}")
                return False
        
    except NoCredentialsError:
        print(f"❌ No credentials found for profile '{profile_name}'")
        return False
    except Exception as e:
        print(f"❌ Error testing profile '{profile_name}': {e}")
        return False

def show_aws_setup_instructions():
    """Show instructions for setting up AWS profiles."""
    print("\n📖 AWS Profile Setup Instructions:")
    print("=" * 50)
    
    if not check_aws_cli_installed():
        print("1. Install AWS CLI:")
        print("   - Windows: https://aws.amazon.com/cli/")
        print("   - macOS: brew install awscli")
        print("   - Linux: sudo apt install awscli")
        print()
    
    print("2. Configure AWS CLI with your credentials:")
    print("   aws configure --profile your-profile-name")
    print()
    print("3. Or manually edit ~/.aws/credentials:")
    print("   [your-profile-name]")
    print("   aws_access_key_id = YOUR_ACCESS_KEY")
    print("   aws_secret_access_key = YOUR_SECRET_KEY")
    print("   region = us-east-1")
    print()
    print("4. Set the profile in your .env file:")
    print("   AWS_PROFILE=your-profile-name")

def main():
    """Main function for AWS profile management."""
    print("🔧 AWS Profile Management for Bedrock-Langfuse Integration")
    print("=" * 60)
    
    # Check if AWS CLI is installed
    if not check_aws_cli_installed():
        print("⚠️  AWS CLI not found")
        show_aws_setup_instructions()
        return
    
    # List available profiles
    profiles = list_aws_profiles()
    
    if not profiles:
        print("❌ No AWS profiles found")
        show_aws_setup_instructions()
        return
    
    print(f"✅ Found {len(profiles)} AWS profile(s):")
    print()
    
    for i, profile in enumerate(profiles, 1):
        print(f"{i}. {profile}")
        
        # Get profile info
        info = get_profile_info(profile)
        if info:
            region = info.get('region', 'Not specified')
            print(f"   Region: {region}")
            
            # Test the profile
            print("   Testing connection...", end=" ")
            if test_aws_profile(profile):
                print("✅ Working")
            else:
                print("❌ Failed")
        print()
    
    # Show current configuration
    current_profile = os.getenv('AWS_PROFILE')
    if current_profile:
        print(f"🎯 Current profile in environment: {current_profile}")
    else:
        print("🎯 No AWS_PROFILE set in environment")
    
    # Check .env file
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            if 'AWS_PROFILE=' in content:
                for line in content.split('\n'):
                    if line.startswith('AWS_PROFILE=') and not line.startswith('#'):
                        profile_in_env = line.split('=', 1)[1].strip()
                        print(f"📄 Profile in .env file: {profile_in_env}")
                        break
            else:
                print("📄 No AWS_PROFILE set in .env file")
    
    print("\n💡 Recommendations:")
    print("1. Use AWS profiles instead of hardcoded keys for better security")
    print("2. Set AWS_PROFILE in your .env file")
    print("3. Ensure your profile has Bedrock permissions")
    print("4. Test with: python test_aws_profile.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

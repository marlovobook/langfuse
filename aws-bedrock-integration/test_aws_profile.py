#!/usr/bin/env python3
"""
Test script to verify AWS profile configuration with Bedrock access.
"""

import os
import sys
from dotenv import load_dotenv

def test_aws_profile():
    """Test AWS profile configuration for Bedrock access."""
    load_dotenv()
    
    print("🧪 Testing AWS Profile Configuration")
    print("=" * 40)
    
    # Get configuration
    aws_profile = os.getenv('AWS_PROFILE')
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    print(f"AWS Profile: {aws_profile or 'Not set'}")
    print(f"AWS Region: {aws_region}")
    print(f"AWS Access Key: {'Set' if aws_access_key else 'Not set'}")
    print(f"AWS Secret Key: {'Set' if aws_secret_key else 'Not set'}")
    print()
    
    try:
        from bedrock_langfuse import BedrockLangfuseClient
        
        print("🔍 Testing AWS Bedrock connection...")
        
        # Create client (it will automatically use profile or keys based on configuration)
        client = BedrockLangfuseClient(debug=True)
        
        print("✅ Bedrock client initialized successfully")
        
        # Test listing available models
        print("\n🔍 Testing Bedrock model access...")
        
        import boto3
        from botocore.exceptions import ClientError
        
        # Get the session/client that was created
        if aws_profile:
            session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
            bedrock_models_client = session.client('bedrock')
        else:
            bedrock_models_client = boto3.client('bedrock', region_name=aws_region)
        
        try:
            # List foundation models
            response = bedrock_models_client.list_foundation_models()
            models = response.get('modelSummaries', [])
            
            print(f"✅ Found {len(models)} foundation models")
            
            # Show some popular models
            popular_models = [
                'anthropic.claude-3-sonnet-20240229-v1:0',
                'anthropic.claude-3-haiku-20240307-v1:0',
                #'meta.llama2-70b-chat-v1',
                'amazon.titan-text-express-v1'
            ]
            
            available_popular = []
            for model_id in popular_models:
                for model in models:
                    if model['modelId'] == model_id:
                        available_popular.append(model_id)
                        break
            
            if available_popular:
                print(f"✅ Popular models available: {len(available_popular)}")
                for model_id in available_popular:
                    print(f"   - {model_id}")
            else:
                print("⚠️  No popular models found (might need model access approval)")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDeniedException':
                print("❌ Access denied to Bedrock. You need:")
                print("   1. Bedrock service permissions in your AWS account")
                print("   2. Model access enabled in Bedrock console")
                print("   3. Proper IAM permissions")
            else:
                print(f"❌ Bedrock API error: {error_code}")
            return False
        
        # Test a simple model invocation (if possible)
        print("\n🔍 Testing model invocation...")
        
        try:
            response = client.chat_completion(
                model="anthropic.claude-3-haiku-20240307-v1:0",
                messages=[{"role": "user", "content": "Hello! Just testing the connection."}],
                session_id="test-session"
            )
            
            print("✅ Model invocation successful!")
            print(f"   Response length: {len(response.content)} characters")
            print(f"   Tokens used: {response.usage.total_tokens}")
            print(f"   Cost: ${response.cost:.6f}")
            
        except Exception as e:
            if "does not have access" in str(e).lower():
                print("⚠️  Model access not enabled (expected for new accounts)")
                print("   Enable model access in AWS Bedrock console")
            else:
                print(f"⚠️  Model invocation failed: {e}")
        
        print("\n🎉 AWS configuration test completed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Run: pip install -e . to install the package")
        return False
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        
        # Provide helpful troubleshooting
        print("\n🔧 Troubleshooting:")
        if aws_profile:
            print(f"1. Check if profile '{aws_profile}' exists: aws configure list-profiles")
            print(f"2. Test profile: aws sts get-caller-identity --profile {aws_profile}")
        else:
            print("1. Set up AWS profile: aws configure --profile your-profile-name")
            print("2. Set AWS_PROFILE=your-profile-name in .env file")
        
        print("3. Ensure Bedrock access in AWS console")
        print("4. Check IAM permissions for Bedrock")
        
        return False

def show_aws_setup_guide():
    """Show a complete AWS setup guide."""
    print("\n📚 Complete AWS Setup Guide")
    print("=" * 30)
    
    print("\n1. Install AWS CLI:")
    print("   curl 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o 'awscliv2.zip'")
    print("   unzip awscliv2.zip && sudo ./aws/install")
    
    print("\n2. Configure AWS Profile:")
    print("   aws configure --profile bedrock-dev")
    print("   # Enter your Access Key ID, Secret Access Key, region (us-east-1), output format (json)")
    
    print("\n3. Test AWS Configuration:")
    print("   aws sts get-caller-identity --profile bedrock-dev")
    
    print("\n4. Enable Bedrock Models:")
    print("   - Go to AWS Console → Bedrock → Model access")
    print("   - Request access to Claude 3, Llama 2, and other models")
    print("   - Wait for approval (usually instant for Claude)")
    
    print("\n5. Update .env file:")
    print("   AWS_PROFILE=bedrock-dev")
    print("   AWS_REGION=us-east-1")
    
    print("\n6. Test the integration:")
    print("   python test_aws_profile.py")

if __name__ == "__main__":
    print("🔧 AWS Profile Test for Bedrock-Langfuse Integration\n")
    
    try:
        success = test_aws_profile()
        
        if not success:
            print("\n" + "="*50)
            response = input("Would you like to see the setup guide? (y/n): ").lower().strip()
            if response == 'y':
                show_aws_setup_guide()
        
    except KeyboardInterrupt:
        print("\n❌ Test cancelled by user")
        sys.exit(1)

# AWS Bedrock + Langfuse Integration

This project demonstrates how to integrate AWS Bedrock with Langfuse for comprehensive LLM observability and monitoring.

## Features

- ✅ AWS Bedrock model integration (Claude, Llama, Titan, etc.)
- ✅ Automatic tracing with Langfuse
- ✅ Cost tracking and token usage monitoring
- ✅ Error handling and retry logic
- ✅ Conversation management
- ✅ Model comparison utilities
- ✅ Async support for high-performance applications

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure AWS Authentication

You have multiple options for AWS authentication (choose one):

#### Option A: AWS Profile (Recommended) 🔒

1. Install AWS CLI:
   ```bash
   # Windows: Download from https://aws.amazon.com/cli/
   # macOS: brew install awscli
   # Linux: sudo apt install awscli
   ```

2. Configure a profile:
   ```bash
   aws configure --profile bedrock-dev
   # Enter your Access Key ID, Secret Key, region (us-east-1), and output format (json)
   ```

3. Set the profile in your `.env` file:
   ```env
   # AWS Configuration (Profile Method)
   AWS_PROFILE=bedrock-dev
   AWS_REGION=us-east-1
   ```

4. Test your profile:
   ```bash
   python aws_profile_manager.py
   python test_aws_profile.py
   ```

#### Option B: Environment Variables (Alternative)

Set credentials directly in your `.env` file:

```env
# AWS Configuration (Environment Variables)
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=us-east-1
```

#### Option C: IAM Roles (For EC2/ECS/Lambda)

If running on AWS infrastructure, use IAM roles (no configuration needed):

```env
# AWS Configuration (IAM Role)
AWS_REGION=us-east-1
# No credentials needed - IAM role provides them
```

### 3. Configure Langfuse

Edit `.env` with your Langfuse credentials:

```env
# Langfuse Configuration
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_HOST=http://localhost:3000
```

### 4. AWS Bedrock Setup

1. **Enable Bedrock Access:**
   - Go to AWS Console → Amazon Bedrock
   - Navigate to "Model access" in the left sidebar
   - Request access to models you want to use:
     - ✅ Anthropic Claude 3 (Haiku, Sonnet, Opus)
     - ✅ Meta Llama 2 models
     - ✅ Amazon Titan models
     - ✅ AI21 Jurassic models

2. **IAM Permissions:**
   Ensure your AWS user/role has these permissions:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "bedrock:InvokeModel",
           "bedrock:ListFoundationModels"
         ],
         "Resource": "*"
       }
     ]
   }
   ```

3. **Test Access:**
   ```bash
   python test_aws_profile.py
   ```

### 5. Langfuse Setup

You can use either a local Langfuse instance or the cloud version:

#### Option A: Local Langfuse Instance (Recommended for Development)

1. Start Langfuse using Docker Compose in the main langfuse directory:
   ```bash
   cd .. # Go to main langfuse directory
   docker-compose up -d
   ```

2. Access Langfuse at http://localhost:3000
3. Create a new organization and project
4. Get your API keys from project settings
5. Set `LANGFUSE_HOST=http://localhost:3000` in your `.env` file

#### Option B: Langfuse Cloud

1. Create a Langfuse account at [cloud.langfuse.com](https://cloud.langfuse.com)
2. Create a new project
3. Get your API keys from project settings
4. Set `LANGFUSE_HOST=https://cloud.langfuse.com` in your `.env` file

## Usage Examples

### Basic Chat Completion

```python
from bedrock_langfuse import BedrockLangfuseClient

client = BedrockLangfuseClient()

response = client.chat_completion(
    model="anthropic.claude-3-sonnet-20240229-v1:0",
    messages=[
        {"role": "user", "content": "What is machine learning?"}
    ],
    session_id="user-123"
)

print(response.content)
```

### Async Chat Completion

```python
import asyncio
from bedrock_langfuse import BedrockLangfuseClient

async def main():
    client = BedrockLangfuseClient()
    
    response = await client.chat_completion_async(
        model="anthropic.claude-3-sonnet-20240229-v1:0",
        messages=[
            {"role": "user", "content": "Explain quantum computing"}
        ],
        session_id="user-456"
    )
    
    print(response.content)

asyncio.run(main())
```

### Model Comparison

```python
from bedrock_langfuse import ModelComparison

comparison = ModelComparison()

results = comparison.compare_models(
    models=[
        "anthropic.claude-3-sonnet-20240229-v1:0",
        "meta.llama2-70b-chat-v1",
        "amazon.titan-text-express-v1"
    ],
    prompt="Explain the benefits of renewable energy",
    session_id="comparison-1"
)

for model, response in results.items():
    print(f"{model}: {response.content[:100]}...")
```

## Available Models

The integration supports all AWS Bedrock models including:

- **Anthropic Claude**: `anthropic.claude-3-sonnet-20240229-v1:0`, `anthropic.claude-v2`
- **Meta Llama**: `meta.llama2-70b-chat-v1`, `meta.llama2-13b-chat-v1`
- **Amazon Titan**: `amazon.titan-text-express-v1`, `amazon.titan-text-lite-v1`
- **AI21 Jurassic**: `ai21.j2-ultra-v1`, `ai21.j2-mid-v1`
- **Cohere Command**: `cohere.command-text-v14`, `cohere.command-light-text-v14`

## Monitoring and Observability

All interactions are automatically traced in Langfuse with:

- **Request/Response logging**: Full conversation history
- **Token usage tracking**: Input/output tokens and costs
- **Performance metrics**: Latency and throughput
- **Error tracking**: Failed requests and retry attempts
- **Session management**: User conversation flows
- **Model comparison**: Side-by-side performance analysis

## Project Structure

```
aws-bedrock-integration/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── bedrock_langfuse/
│   ├── __init__.py
│   ├── client.py          # Main client implementation
│   ├── models.py          # Data models and types
│   ├── utils.py           # Utility functions
│   └── exceptions.py      # Custom exceptions
├── examples/
│   ├── basic_chat.py      # Simple chat example
│   ├── async_chat.py      # Async chat example
│   ├── conversation.py    # Multi-turn conversation
│   ├── model_comparison.py # Compare multiple models
│   └── streaming.py       # Streaming responses
└── tests/
    ├── test_client.py
    ├── test_models.py
    └── test_utils.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

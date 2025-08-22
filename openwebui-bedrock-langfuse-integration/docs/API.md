# API Documentation

## Overview

The OpenWebUI + Bedrock + Langfuse integration provides an OpenAI-compatible API that bridges OpenWebUI with AWS Bedrock models while providing comprehensive observability through Langfuse.

## Base URL

```
http://localhost:8081
```

## Authentication

Currently, no authentication is required for the backend API. Authentication is handled by OpenWebUI if enabled.

## Endpoints

### Health Check

Check the health status of the backend service and AWS connection.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-08-22T10:30:00Z",
  "aws_connection": "ok",
  "available_models": 12
}
```

### List Models

Get available AI models in OpenAI-compatible format.

**Endpoint:** `GET /v1/models`

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "claude-3-haiku",
      "object": "model",
      "created": 1692710400,
      "owned_by": "Anthropic"
    },
    {
      "id": "anthropic.claude-3-haiku-20240307-v1:0",
      "object": "model", 
      "created": 1692710400,
      "owned_by": "AWS Bedrock"
    }
  ]
}
```

### Chat Completions

Create a chat completion using AWS Bedrock models.

**Endpoint:** `POST /v1/chat/completions`

**Request Body:**
```json
{
  "model": "claude-3-haiku",
  "messages": [
    {
      "role": "user",
      "content": "Hello, how are you?"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 150,
  "stream": false
}
```

**Response (Non-streaming):**
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1692710400,
  "model": "claude-3-haiku",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! I'm doing well, thank you for asking. How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 19,
    "total_tokens": 31
  }
}
```

**Response (Streaming):**
```
data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1692710400,"model":"claude-3-haiku","choices":[{"index":0,"delta":{"role":"assistant"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1692710400,"model":"claude-3-haiku","choices":[{"index":0,"delta":{"content":"Hello!"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1692710400,"model":"claude-3-haiku","choices":[{"index":0,"delta":{"content":" I'm"},"finish_reason":null}]}

...

data: [DONE]
```

## Model Mapping

The backend supports both friendly model names and full AWS Bedrock model IDs:

| Friendly Name | AWS Bedrock Model ID |
|---------------|---------------------|
| `claude-3-haiku` | `anthropic.claude-3-haiku-20240307-v1:0` |
| `claude-3-sonnet` | `anthropic.claude-3-sonnet-20240229-v1:0` |
| `claude-3-opus` | `anthropic.claude-3-opus-20240229-v1:0` |
| `titan-text` | `amazon.titan-text-express-v1` |
| `llama2-13b` | `meta.llama2-13b-chat-v1` |
| `llama2-70b` | `meta.llama2-70b-chat-v1` |

## Parameters

### Chat Completion Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `model` | string | Model to use for completion | Required |
| `messages` | array | List of messages in the conversation | Required |
| `temperature` | number | Sampling temperature (0-1) | 0.7 |
| `max_tokens` | integer | Maximum tokens to generate | Model default |
| `top_p` | number | Nucleus sampling parameter | Model default |
| `stream` | boolean | Enable streaming responses | false |
| `stop` | array | Stop sequences | null |

### Message Format

```json
{
  "role": "user|assistant|system",
  "content": "Message content"
}
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "type": "invalid_request_error",
    "message": "The model 'invalid-model' does not exist",
    "code": "model_not_found"
  }
}
```

### Common Error Codes

| HTTP Status | Error Type | Description |
|-------------|------------|-------------|
| 400 | `invalid_request_error` | Invalid request parameters |
| 401 | `authentication_error` | Invalid or missing authentication |
| 403 | `permission_error` | Insufficient permissions |
| 404 | `not_found_error` | Resource not found |
| 429 | `rate_limit_error` | Rate limit exceeded |
| 500 | `internal_server_error` | Internal server error |
| 503 | `service_unavailable_error` | Service temporarily unavailable |

## Rate Limits

Rate limits are enforced by AWS Bedrock and depend on your AWS account limits. Common limits:

- **Claude 3 Haiku**: 10,000 requests/minute
- **Claude 3 Sonnet**: 5,000 requests/minute  
- **Claude 3 Opus**: 1,000 requests/minute
- **Titan Text**: 10,000 requests/minute

## Usage Examples

### Python (requests)

```python
import requests

# List models
response = requests.get('http://localhost:8081/v1/models')
models = response.json()

# Chat completion
response = requests.post('http://localhost:8081/v1/chat/completions', json={
    "model": "claude-3-haiku",
    "messages": [
        {"role": "user", "content": "Hello!"}
    ]
})
completion = response.json()
```

### Python (OpenAI SDK)

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8081/v1",
    api_key="dummy-key"  # Not used but required by SDK
)

# List models
models = client.models.list()

# Chat completion
completion = client.chat.completions.create(
    model="claude-3-haiku",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)
```

### JavaScript (fetch)

```javascript
// List models
const models = await fetch('http://localhost:8081/v1/models')
  .then(res => res.json());

// Chat completion
const completion = await fetch('http://localhost:8081/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    model: 'claude-3-haiku',
    messages: [
      {role: 'user', content: 'Hello!'}
    ]
  })
}).then(res => res.json());
```

### cURL

```bash
# List models
curl http://localhost:8081/v1/models

# Chat completion
curl -X POST http://localhost:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-haiku",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

## Observability

All API calls are automatically tracked in Langfuse with the following information:

- **Traces**: Complete request/response cycles
- **Usage**: Token counts and estimated costs
- **Performance**: Response times and latencies
- **Errors**: Error rates and types
- **Sessions**: User session tracking
- **Metadata**: Model information and parameters

Access the Langfuse dashboard at `http://localhost:3000` to view detailed analytics.

## OpenWebUI Integration

To use this backend with OpenWebUI:

1. Open OpenWebUI at `http://localhost:8080`
2. Go to Settings → Connections
3. Set the OpenAI API Base URL to: `http://backend:8081/v1`
4. Set any dummy API key (not used)
5. Save and refresh model list

The models will appear in OpenWebUI's model selector, and all conversations will be tracked in Langfuse automatically.

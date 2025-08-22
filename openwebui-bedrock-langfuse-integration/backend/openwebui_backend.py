"""
OpenWebUI-compatible backend server for AWS Bedrock integration with Langfuse observability.

This server implements the OpenAI-compatible API that OpenWebUI expects,
while using AWS Bedrock as the actual model provider and Langfuse for observability.
"""

import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, AsyncGenerator
import asyncio
import logging

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import uvicorn

from bedrock_langfuse import BedrockLangfuseClient, ChatMessage, MessageRole, ModelConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="OpenWebUI Bedrock Backend",
    description="AWS Bedrock backend for OpenWebUI with Langfuse observability",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Bedrock client
bedrock_client = None

def get_bedrock_client():
    """Get or create Bedrock client."""
    global bedrock_client
    if bedrock_client is None:
        try:
            bedrock_client = BedrockLangfuseClient(debug=True)
            logger.info("Bedrock client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize AWS Bedrock client")
    return bedrock_client

# OpenAI-compatible models
class ChatCompletionMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatCompletionMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: Optional[List[str]] = None

class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: ChatCompletionMessage
    finish_reason: str

class ChatCompletionUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionResponseChoice]
    usage: ChatCompletionUsage

class ChatCompletionStreamChoice(BaseModel):
    index: int
    delta: Dict[str, Any]
    finish_reason: Optional[str] = None

class ChatCompletionStreamResponse(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[ChatCompletionStreamChoice]

class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str

class ModelsResponse(BaseModel):
    object: str = "list"
    data: List[ModelInfo]

# Model mapping from OpenWebUI names to Bedrock model IDs
MODEL_MAPPING = {
    "claude-3-haiku": "anthropic.claude-3-haiku-20240307-v1:0",
    "claude-3-sonnet": "anthropic.claude-3-sonnet-20240229-v1:0", 
    "claude-3-opus": "anthropic.claude-3-opus-20240229-v1:0",
    "titan-text": "amazon.titan-text-express-v1",
    "llama2-13b": "meta.llama2-13b-chat-v1",
    "llama2-70b": "meta.llama2-70b-chat-v1",
    # Direct mapping for full model IDs
    "anthropic.claude-3-haiku-20240307-v1:0": "anthropic.claude-3-haiku-20240307-v1:0",
    "anthropic.claude-3-sonnet-20240229-v1:0": "anthropic.claude-3-sonnet-20240229-v1:0",
    "anthropic.claude-3-opus-20240229-v1:0": "anthropic.claude-3-opus-20240229-v1:0",
    "amazon.titan-text-express-v1": "amazon.titan-text-express-v1",
    "meta.llama2-13b-chat-v1": "meta.llama2-13b-chat-v1",
    "meta.llama2-70b-chat-v1": "meta.llama2-70b-chat-v1"
}

def map_model_name(model_name: str) -> str:
    """Map OpenWebUI model name to Bedrock model ID."""
    return MODEL_MAPPING.get(model_name, model_name)

def convert_messages(messages: List[ChatCompletionMessage]) -> List[ChatMessage]:
    """Convert OpenAI format messages to Bedrock format."""
    bedrock_messages = []
    for msg in messages:
        role = MessageRole.USER if msg.role == "user" else MessageRole.ASSISTANT
        if msg.role == "system":
            role = MessageRole.SYSTEM
        bedrock_messages.append(ChatMessage(role=role, content=msg.content))
    return bedrock_messages

def create_model_config(request: ChatCompletionRequest) -> ModelConfig:
    """Create ModelConfig from OpenAI request parameters."""
    config = ModelConfig()
    
    if request.temperature is not None:
        config.temperature = request.temperature
    if request.max_tokens is not None:
        config.max_tokens = request.max_tokens
    if request.top_p is not None:
        config.top_p = request.top_p
    if request.stop is not None:
        config.stop_sequences = request.stop
    
    return config

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        client = get_bedrock_client()
        # Try to list models to verify AWS connection
        models = client.list_available_models()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "aws_connection": "ok",
            "available_models": len(models)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy", 
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.get("/v1/models")
async def list_models():
    """List available models in OpenAI format."""
    try:
        client = get_bedrock_client()
        bedrock_models = client.list_available_models()
        
        models = []
        current_time = int(time.time())
        
        # Add friendly model names
        friendly_models = [
            ("claude-3-haiku", "Anthropic"),
            ("claude-3-sonnet", "Anthropic"),
            ("claude-3-opus", "Anthropic"),
            ("titan-text", "Amazon"),
            ("llama2-13b", "Meta"),
            ("llama2-70b", "Meta")
        ]
        
        for model_id, owner in friendly_models:
            if map_model_name(model_id) in bedrock_models:
                models.append(ModelInfo(
                    id=model_id,
                    created=current_time,
                    owned_by=owner
                ))
        
        # Also add full Bedrock model IDs
        for bedrock_model_id in bedrock_models.keys():
            models.append(ModelInfo(
                id=bedrock_model_id,
                created=current_time,
                owned_by="AWS Bedrock"
            ))
        
        return ModelsResponse(data=models)
        
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")

async def stream_response(client, model: str, messages: List[ChatMessage], config: ModelConfig) -> AsyncGenerator[str, None]:
    """Generate streaming response chunks."""
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:16]}"
    created = int(time.time())
    
    try:
        # Get non-streaming response first (Bedrock doesn't support streaming directly)
        response = client.chat_completion(
            model=model,
            messages=messages,
            config=config,
            metadata={"streaming": True}
        )
        
        # Simulate streaming by sending the response in chunks
        content = response.content
        words = content.split(' ')
        
        # Send initial chunk
        initial_chunk = ChatCompletionStreamResponse(
            id=completion_id,
            created=created,
            model=model,
            choices=[ChatCompletionStreamChoice(
                index=0,
                delta={"role": "assistant"},
                finish_reason=None
            )]
        )
        yield f"data: {initial_chunk.model_dump_json()}\n\n"
        
        # Send content chunks
        for i, word in enumerate(words):
            chunk = ChatCompletionStreamResponse(
                id=completion_id,
                created=created,
                model=model,
                choices=[ChatCompletionStreamChoice(
                    index=0,
                    delta={"content": word + (" " if i < len(words) - 1 else "")},
                    finish_reason=None
                )]
            )
            yield f"data: {chunk.model_dump_json()}\n\n"
            await asyncio.sleep(0.05)  # Small delay for streaming effect
        
        # Send final chunk
        final_chunk = ChatCompletionStreamResponse(
            id=completion_id,
            created=created,
            model=model,
            choices=[ChatCompletionStreamChoice(
                index=0,
                delta={},
                finish_reason="stop"
            )]
        )
        yield f"data: {final_chunk.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        logger.error(f"Streaming error: {e}")
        error_chunk = ChatCompletionStreamResponse(
            id=completion_id,
            created=created,
            model=model,
            choices=[ChatCompletionStreamChoice(
                index=0,
                delta={"content": f"Error: {str(e)}"},
                finish_reason="error"
            )]
        )
        yield f"data: {error_chunk.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """Handle chat completion requests."""
    try:
        client = get_bedrock_client()
        
        # Map model name
        bedrock_model = map_model_name(request.model)
        
        # Convert messages
        bedrock_messages = convert_messages(request.messages)
        
        # Create model config
        config = create_model_config(request)
        
        # Generate session and user IDs for tracking
        session_id = f"openwebui-{uuid.uuid4().hex[:8]}"
        user_id = "openwebui-user"
        
        if request.stream:
            # Return streaming response
            return StreamingResponse(
                stream_response(client, bedrock_model, bedrock_messages, config),
                media_type="text/plain"
            )
        else:
            # Get regular response
            response = client.chat_completion(
                model=bedrock_model,
                messages=bedrock_messages,
                config=config,
                session_id=session_id,
                user_id=user_id,
                metadata={
                    "frontend": "openwebui",
                    "original_model": request.model
                }
            )
            
            # Convert to OpenAI format
            completion_id = f"chatcmpl-{uuid.uuid4().hex[:16]}"
            created = int(time.time())
            
            openai_response = ChatCompletionResponse(
                id=completion_id,
                created=created,
                model=request.model,
                choices=[ChatCompletionResponseChoice(
                    index=0,
                    message=ChatCompletionMessage(
                        role="assistant",
                        content=response.content
                    ),
                    finish_reason="stop"
                )],
                usage=ChatCompletionUsage(
                    prompt_tokens=response.usage.input_tokens,
                    completion_tokens=response.usage.output_tokens,
                    total_tokens=response.usage.total_tokens
                )
            )
            
            return openai_response
            
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat completion failed: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "OpenWebUI Bedrock Backend",
        "version": "1.0.0",
        "description": "AWS Bedrock backend for OpenWebUI with Langfuse observability",
        "endpoints": {
            "health": "/health",
            "models": "/v1/models", 
            "chat": "/v1/chat/completions"
        }
    }

if __name__ == "__main__":
    import os
    port = int(os.getenv("BACKEND_PORT", 8081))
    uvicorn.run(app, host="0.0.0.0", port=port)

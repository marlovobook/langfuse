"""Main client implementation for AWS Bedrock + Langfuse integration."""

import json
import os
import time
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

import boto3
from botocore.exceptions import ClientError, BotoCoreError
from langfuse import Langfuse, observe
import logging

from .models import (
    ChatMessage, ChatResponse, ModelUsage, ConversationContext, 
    ModelConfig, MessageRole, SUPPORTED_MODELS
)
from .exceptions import (
    BedrockLangfuseError, ModelNotAvailableError, AuthenticationError,
    RateLimitError, InvalidRequestError, ServiceUnavailableError
)


class BedrockLangfuseClient:
    """
    A client that integrates AWS Bedrock with Langfuse for LLM observability.
    
    This client provides methods for chat completions while automatically
    tracking usage, costs, and performance metrics in Langfuse.
    """
    
    def __init__(
        self,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_region: Optional[str] = None,
        aws_profile: Optional[str] = None,
        langfuse_secret_key: Optional[str] = None,
        langfuse_public_key: Optional[str] = None,
        langfuse_host: Optional[str] = None,
        debug: bool = False
    ):
        """
        Initialize the Bedrock-Langfuse client.
        
        Args:
            aws_access_key_id: AWS access key ID (uses env var if not provided)
            aws_secret_access_key: AWS secret access key (uses env var if not provided)
            aws_region: AWS region (uses env var if not provided)
            aws_profile: AWS profile name (uses env var if not provided)
            langfuse_secret_key: Langfuse secret key (uses env var if not provided)
            langfuse_public_key: Langfuse public key (uses env var if not provided)
            langfuse_host: Langfuse host URL (uses env var if not provided)
            debug: Enable debug logging
        """
        # Setup logging
        self.logger = logging.getLogger(__name__)
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        
        # Initialize AWS Bedrock client with profile or key-based authentication
        try:
            # Get AWS configuration from parameters or environment variables
            profile_name = aws_profile or os.getenv('AWS_PROFILE')
            access_key = aws_access_key_id or os.getenv('AWS_ACCESS_KEY_ID')
            secret_key = aws_secret_access_key or os.getenv('AWS_SECRET_ACCESS_KEY')
            region = aws_region or os.getenv('AWS_REGION', 'us-east-1')
            
            # Determine authentication method
            if profile_name:
                # Use AWS profile
                self.logger.info(f"Using AWS profile: {profile_name}")
                session = boto3.Session(profile_name=profile_name, region_name=region)
                self.bedrock_client = session.client('bedrock-runtime')
            elif access_key and secret_key:
                # Use explicit credentials
                self.logger.info("Using explicit AWS credentials")
                self.bedrock_client = boto3.client(
                    'bedrock-runtime',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    region_name=region
                )
            else:
                # Use default credentials chain (IAM role, env vars, etc.)
                self.logger.info("Using default AWS credentials chain")
                self.bedrock_client = boto3.client(
                    'bedrock-runtime',
                    region_name=region
                )
        except Exception as e:
            raise AuthenticationError(f"Failed to initialize AWS Bedrock client: {str(e)}")
        
        # Initialize Langfuse client
        try:
            self.langfuse = Langfuse(
                secret_key=langfuse_secret_key or os.getenv('LANGFUSE_SECRET_KEY'),
                public_key=langfuse_public_key or os.getenv('LANGFUSE_PUBLIC_KEY'),
                host=langfuse_host or os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')
            )
        except Exception as e:
            raise AuthenticationError(f"Failed to initialize Langfuse client: {str(e)}")
        
        self.debug = debug
    
    def _validate_model(self, model_id: str) -> Dict[str, Any]:
        """Validate if the model is supported and return its configuration."""
        if model_id not in SUPPORTED_MODELS:
            available_models = list(SUPPORTED_MODELS.keys())
            raise ModelNotAvailableError(
                f"Model '{model_id}' is not supported. "
                f"Available models: {available_models}"
            )
        return SUPPORTED_MODELS[model_id]
    
    def _calculate_cost(self, usage: ModelUsage, model_config: Dict[str, Any]) -> float:
        """Calculate the estimated cost based on token usage."""
        input_cost = (usage.input_tokens / 1000) * model_config.get('input_cost_per_1k', 0)
        output_cost = (usage.output_tokens / 1000) * model_config.get('output_cost_per_1k', 0)
        return input_cost + output_cost
    
    def _format_messages_for_bedrock(
        self, 
        messages: List[ChatMessage], 
        model_id: str
    ) -> Dict[str, Any]:
        """Format messages for specific Bedrock model requirements."""
        if model_id.startswith('anthropic.claude'):
            # Claude format
            formatted_messages = []
            system_message = None
            
            for message in messages:
                if message.role == MessageRole.SYSTEM:
                    system_message = message.content
                else:
                    formatted_messages.append({
                        "role": message.role.value,
                        "content": message.content
                    })
            
            body = {
                "messages": formatted_messages,
                "anthropic_version": "bedrock-2023-05-31"  # Required for Claude on Bedrock
            }
            if system_message:
                body["system"] = system_message
                
            return body
            
        elif model_id.startswith('meta.llama'):
            # Llama format
            prompt = ""
            for message in messages:
                if message.role == MessageRole.SYSTEM:
                    prompt += f"[INST] <<SYS>>\n{message.content}\n<</SYS>>\n\n"
                elif message.role == MessageRole.USER:
                    prompt += f"{message.content} [/INST] "
                elif message.role == MessageRole.ASSISTANT:
                    prompt += f"{message.content} </s><s>[INST] "
            
            return {"prompt": prompt}
            
        elif model_id.startswith('amazon.titan'):
            # Titan format
            conversation = []
            for message in messages:
                conversation.append({
                    "role": message.role.value,
                    "content": message.content
                })
            
            return {"inputText": json.dumps(conversation)}
            
        else:
            # Default format - works for most models
            return {
                "messages": [
                    {"role": msg.role.value, "content": msg.content}
                    for msg in messages
                ]
            }
    
    def _parse_bedrock_response(
        self, 
        response: Dict[str, Any], 
        model_id: str
    ) -> tuple[str, ModelUsage]:
        """Parse the response from Bedrock based on model type."""
        try:
            if model_id.startswith('anthropic.claude'):
                content = response.get('content', [{}])[0].get('text', '')
                usage_data = response.get('usage', {})
                usage = ModelUsage(
                    input_tokens=usage_data.get('input_tokens', 0),
                    output_tokens=usage_data.get('output_tokens', 0),
                    total_tokens=usage_data.get('input_tokens', 0) + usage_data.get('output_tokens', 0),
                    model_id=model_id
                )
                
            elif model_id.startswith('meta.llama'):
                content = response.get('generation', '')
                # Llama models don't always return detailed usage
                usage = ModelUsage(
                    input_tokens=response.get('prompt_token_count', 0),
                    output_tokens=response.get('generation_token_count', 0),
                    total_tokens=response.get('prompt_token_count', 0) + response.get('generation_token_count', 0),
                    model_id=model_id
                )
                
            elif model_id.startswith('amazon.titan'):
                results = response.get('results', [{}])
                content = results[0].get('outputText', '') if results else ''
                usage = ModelUsage(
                    input_tokens=response.get('inputTextTokenCount', 0),
                    output_tokens=results[0].get('tokenCount', 0) if results else 0,
                    total_tokens=response.get('inputTextTokenCount', 0) + (results[0].get('tokenCount', 0) if results else 0),
                    model_id=model_id
                )
                
            else:
                # Default parsing
                content = response.get('completion', response.get('text', str(response)))
                usage = ModelUsage(
                    input_tokens=0,
                    output_tokens=0,
                    total_tokens=0,
                    model_id=model_id
                )
                
            return content, usage
            
        except Exception as e:
            self.logger.error(f"Error parsing response for model {model_id}: {str(e)}")
            return str(response), ModelUsage(0, 0, 0, model_id=model_id)
    
    @observe()
    def chat_completion(
        self,
        model: str,
        messages: List[Union[ChatMessage, Dict[str, str]]],
        config: Optional[ModelConfig] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> ChatResponse:
        """
        Generate a chat completion using AWS Bedrock with Langfuse tracking.
        
        Args:
            model: The model ID to use
            messages: List of messages or ChatMessage objects
            config: Model configuration parameters
            session_id: Session identifier for conversation tracking
            user_id: User identifier
            metadata: Additional metadata to track
            tags: Tags for categorization
            
        Returns:
            ChatResponse object with the completion and usage information
        """
        start_time = time.time()
        
        # Validate model
        model_config = self._validate_model(model)
        
        # Convert dict messages to ChatMessage objects if needed
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                role = MessageRole(msg['role'])
                formatted_messages.append(ChatMessage(role=role, content=msg['content']))
            else:
                formatted_messages.append(msg)
        
        # Use default config if none provided
        if config is None:
            config = ModelConfig()
        
        try:
            # Prepare request body
            body = self._format_messages_for_bedrock(formatted_messages, model)
            
            # Add model configuration
            body.update(config.to_dict())
            
            # Make the API call
            response = self.bedrock_client.invoke_model(
                modelId=model,
                body=json.dumps(body),
                contentType='application/json'
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            content, usage = self._parse_bedrock_response(response_body, model)
            
            # Calculate cost
            estimated_cost = self._calculate_cost(usage, model_config)
            usage.estimated_cost = estimated_cost
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Create trace in Langfuse using the current API
            with self.langfuse.start_as_current_span(name=f"bedrock-{model}") as trace:
                trace.update(
                    session_id=session_id,
                    user_id=user_id,
                    metadata={
                        **(metadata or {}),
                        "model": model,
                        "provider": model_config.get("provider"),
                        "response_time": response_time,
                        "estimated_cost": estimated_cost
                    },
                    tags=tags
                )
                
                # Log the generation
                generation = self.langfuse.start_generation(
                    name=f"bedrock-generation-{model}",
                    model=model,
                    input=[msg.to_dict() for msg in formatted_messages],
                    output=content,
                    usage_details={
                        "input": usage.input_tokens,
                        "output": usage.output_tokens,
                        "total": usage.total_tokens,
                        "unit": "TOKENS"
                    },
                metadata={
                    "model_config": config.to_dict(),
                    "finish_reason": response_body.get("stop_reason"),
                    "estimated_cost": estimated_cost
                }
                )
                
                trace_id = trace.id if hasattr(trace, 'id') else None
            
            return ChatResponse(
                content=content,
                model=model,
                usage=usage,
                finish_reason=response_body.get("stop_reason"),
                response_time=response_time,
                raw_response=response_body,
                trace_id=trace_id
            )
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ValidationException':
                raise InvalidRequestError(f"Invalid request: {str(e)}")
            elif error_code == 'ThrottlingException':
                raise RateLimitError(f"Rate limit exceeded: {str(e)}")
            elif error_code == 'ServiceUnavailableException':
                raise ServiceUnavailableError(f"Service unavailable: {str(e)}")
            else:
                raise BedrockLangfuseError(f"AWS Bedrock error: {str(e)}")
                
        except Exception as e:
            self.logger.error(f"Unexpected error in chat_completion: {str(e)}")
            raise BedrockLangfuseError(f"Unexpected error: {str(e)}")
    
    async def chat_completion_async(
        self,
        model: str,
        messages: List[Union[ChatMessage, Dict[str, str]]],
        config: Optional[ModelConfig] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> ChatResponse:
        """
        Async version of chat_completion.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.chat_completion,
            model,
            messages,
            config,
            session_id,
            user_id,
            metadata,
            tags
        )
    
    def list_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Return a dictionary of all supported models and their configurations."""
        return SUPPORTED_MODELS.copy()
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific model."""
        if model_id not in SUPPORTED_MODELS:
            raise ModelNotAvailableError(f"Model '{model_id}' is not supported.")
        return SUPPORTED_MODELS[model_id].copy()
    
    def flush(self):
        """Flush any pending Langfuse data."""
        self.langfuse.flush()

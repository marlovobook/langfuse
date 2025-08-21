"""
AWS Bedrock + Langfuse Integration

This package provides a seamless integration between AWS Bedrock and Langfuse
for comprehensive LLM observability and monitoring.
"""

from .client import BedrockLangfuseClient
from .models import ChatMessage, ChatResponse, ModelUsage, MessageRole, ModelConfig
from .utils import ModelComparison
from .exceptions import BedrockLangfuseError, ModelNotAvailableError

__version__ = "1.0.0"
__all__ = [
    "BedrockLangfuseClient",
    "ChatMessage",
    "ChatResponse", 
    "ModelUsage",
    "MessageRole",
    "ModelConfig",
    "ModelComparison",
    "BedrockLangfuseError",
    "ModelNotAvailableError"
]

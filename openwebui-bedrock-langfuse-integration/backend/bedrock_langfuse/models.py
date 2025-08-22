"""Data models for the Bedrock-Langfuse integration."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum


class MessageRole(Enum):
    """Enumeration for message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ChatMessage:
    """Represents a single message in a conversation."""
    role: MessageRole
    content: str
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


@dataclass
class ModelUsage:
    """Represents token usage and cost information."""
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: Optional[float] = None
    model_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost": self.estimated_cost,
            "model_id": self.model_id
        }


@dataclass
class ChatResponse:
    """Represents a response from the chat completion."""
    content: str
    model: str
    usage: ModelUsage
    finish_reason: Optional[str] = None
    response_time: Optional[float] = None
    raw_response: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "content": self.content,
            "model": self.model,
            "usage": self.usage.to_dict(),
            "finish_reason": self.finish_reason,
            "response_time": self.response_time,
            "trace_id": self.trace_id
        }


@dataclass
class ConversationContext:
    """Represents the context of a conversation."""
    session_id: str
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "metadata": self.metadata or {},
            "tags": self.tags or []
        }


@dataclass
class ModelConfig:
    """Configuration for model parameters."""
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 0.9
    top_k: Optional[int] = None
    stop_sequences: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format, excluding None values."""
        config = {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p
        }
        
        if self.top_k is not None:
            config["top_k"] = self.top_k
        
        if self.stop_sequences:
            config["stop_sequences"] = self.stop_sequences
            
        return config


# Supported AWS Bedrock models
SUPPORTED_MODELS = {
    # Anthropic Claude models
    "anthropic.claude-3-5-sonnet-20241022-v2:0": {
        "name": "Claude 3.5 Sonnet v2",
        "provider": "Anthropic",
        "input_cost_per_1k": 0.003,
        "output_cost_per_1k": 0.015,
        "max_tokens": 8192
    },
    "anthropic.claude-3-sonnet-20240229-v1:0": {
        "name": "Claude 3 Sonnet",
        "provider": "Anthropic", 
        "input_cost_per_1k": 0.003,
        "output_cost_per_1k": 0.015,
        "max_tokens": 4096
    },
    "anthropic.claude-3-haiku-20240307-v1:0": {
        "name": "Claude 3 Haiku",
        "provider": "Anthropic",
        "input_cost_per_1k": 0.00025,
        "output_cost_per_1k": 0.00125,
        "max_tokens": 4096
    },
    "anthropic.claude-v2:1": {
        "name": "Claude v2.1",
        "provider": "Anthropic",
        "input_cost_per_1k": 0.008,
        "output_cost_per_1k": 0.024,
        "max_tokens": 4096
    },
    
    # Meta Llama models
    "meta.llama2-70b-chat-v1": {
        "name": "Llama 2 70B Chat",
        "provider": "Meta",
        "input_cost_per_1k": 0.00195,
        "output_cost_per_1k": 0.00256,
        "max_tokens": 4096
    },
    "meta.llama2-13b-chat-v1": {
        "name": "Llama 2 13B Chat", 
        "provider": "Meta",
        "input_cost_per_1k": 0.00075,
        "output_cost_per_1k": 0.001,
        "max_tokens": 4096
    },
    
    # Amazon Titan models
    "amazon.titan-text-express-v1": {
        "name": "Titan Text G1 - Express",
        "provider": "Amazon",
        "input_cost_per_1k": 0.0008,
        "output_cost_per_1k": 0.0016,
        "max_tokens": 8192
    },
    "amazon.titan-text-lite-v1": {
        "name": "Titan Text G1 - Lite",
        "provider": "Amazon",
        "input_cost_per_1k": 0.0003,
        "output_cost_per_1k": 0.0004,
        "max_tokens": 4096
    },
    
    # AI21 Jurassic models
    "ai21.j2-ultra-v1": {
        "name": "Jurassic-2 Ultra",
        "provider": "AI21",
        "input_cost_per_1k": 0.0188,
        "output_cost_per_1k": 0.0188,
        "max_tokens": 8192
    },
    "ai21.j2-mid-v1": {
        "name": "Jurassic-2 Mid",
        "provider": "AI21",
        "input_cost_per_1k": 0.0125,
        "output_cost_per_1k": 0.0125,
        "max_tokens": 8192
    },
    
    # Cohere Command models
    "cohere.command-text-v14": {
        "name": "Command",
        "provider": "Cohere",
        "input_cost_per_1k": 0.0015,
        "output_cost_per_1k": 0.002,
        "max_tokens": 4096
    },
    "cohere.command-light-text-v14": {
        "name": "Command Light",
        "provider": "Cohere",
        "input_cost_per_1k": 0.0003,
        "output_cost_per_1k": 0.0006,
        "max_tokens": 4096
    }
}

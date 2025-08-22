"""Utility functions and classes for the Bedrock-Langfuse integration."""

import asyncio
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from .client import BedrockLangfuseClient
from .models import ChatMessage, ChatResponse, ModelConfig, MessageRole


class ModelComparison:
    """Utility class for comparing responses from multiple models."""
    
    def __init__(self, client: Optional[BedrockLangfuseClient] = None):
        """
        Initialize the ModelComparison utility.
        
        Args:
            client: Optional BedrockLangfuseClient instance. 
                   If not provided, a new one will be created.
        """
        self.client = client or BedrockLangfuseClient()
    
    def compare_models(
        self,
        models: List[str],
        prompt: str,
        config: Optional[ModelConfig] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        max_workers: int = 3
    ) -> Dict[str, ChatResponse]:
        """
        Compare responses from multiple models for the same prompt.
        
        Args:
            models: List of model IDs to compare
            prompt: The prompt to send to all models
            config: Model configuration to use for all models
            session_id: Session ID for tracking
            user_id: User ID for tracking
            metadata: Additional metadata
            max_workers: Maximum number of concurrent requests
            
        Returns:
            Dictionary mapping model IDs to their responses
        """
        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        results = {}
        
        # Add comparison metadata
        comparison_metadata = {
            **(metadata or {}),
            "comparison_type": "model_comparison",
            "compared_models": models,
            "total_models": len(models)
        }
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all requests
            future_to_model = {
                executor.submit(
                    self.client.chat_completion,
                    model=model,
                    messages=messages,
                    config=config,
                    session_id=session_id,
                    user_id=user_id,
                    metadata={
                        **comparison_metadata,
                        "comparison_model": model,
                        "comparison_position": i
                    },
                    tags=["model_comparison", f"model_{model.split('.')[-1]}"]
                ): model
                for i, model in enumerate(models)
            }
            
            # Collect results
            for future in as_completed(future_to_model):
                model = future_to_model[future]
                try:
                    response = future.result()
                    results[model] = response
                except Exception as e:
                    # Create a dummy response for failed models
                    from .models import ModelUsage
                    results[model] = ChatResponse(
                        content=f"Error: {str(e)}",
                        model=model,
                        usage=ModelUsage(0, 0, 0, model_id=model),
                        finish_reason="error"
                    )
        
        return results
    
    async def compare_models_async(
        self,
        models: List[str],
        prompt: str,
        config: Optional[ModelConfig] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, ChatResponse]:
        """
        Async version of compare_models.
        """
        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        
        # Add comparison metadata
        comparison_metadata = {
            **(metadata or {}),
            "comparison_type": "model_comparison_async",
            "compared_models": models,
            "total_models": len(models)
        }
        
        # Create tasks for all models
        tasks = []
        for i, model in enumerate(models):
            task = self.client.chat_completion_async(
                model=model,
                messages=messages,
                config=config,
                session_id=session_id,
                user_id=user_id,
                metadata={
                    **comparison_metadata,
                    "comparison_model": model,
                    "comparison_position": i
                },
                tags=["model_comparison_async", f"model_{model.split('.')[-1]}"]
            )
            tasks.append((model, task))
        
        # Execute all tasks concurrently
        results = {}
        for model, task in tasks:
            try:
                response = await task
                results[model] = response
            except Exception as e:
                # Create a dummy response for failed models
                from .models import ModelUsage
                results[model] = ChatResponse(
                    content=f"Error: {str(e)}",
                    model=model,
                    usage=ModelUsage(0, 0, 0, model_id=model),
                    finish_reason="error"
                )
        
        return results


class ConversationManager:
    """Utility class for managing multi-turn conversations."""
    
    def __init__(self, client: Optional[BedrockLangfuseClient] = None):
        """
        Initialize the ConversationManager.
        
        Args:
            client: Optional BedrockLangfuseClient instance.
        """
        self.client = client or BedrockLangfuseClient()
        self.conversations: Dict[str, List[ChatMessage]] = {}
    
    def start_conversation(self, session_id: str, system_message: Optional[str] = None):
        """
        Start a new conversation.
        
        Args:
            session_id: Unique identifier for the conversation
            system_message: Optional system message to set context
        """
        self.conversations[session_id] = []
        if system_message:
            self.conversations[session_id].append(
                ChatMessage(role=MessageRole.SYSTEM, content=system_message)
            )
    
    def add_user_message(self, session_id: str, message: str):
        """Add a user message to the conversation."""
        if session_id not in self.conversations:
            self.start_conversation(session_id)
        
        self.conversations[session_id].append(
            ChatMessage(role=MessageRole.USER, content=message)
        )
    
    def get_response(
        self,
        session_id: str,
        model: str,
        config: Optional[ModelConfig] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        """
        Get a response from the model and add it to the conversation.
        
        Args:
            session_id: Conversation session ID
            model: Model ID to use
            config: Model configuration
            user_id: User ID for tracking
            metadata: Additional metadata
            
        Returns:
            ChatResponse object
        """
        if session_id not in self.conversations:
            raise ValueError(f"No conversation found for session_id: {session_id}")
        
        # Get response from the model
        response = self.client.chat_completion(
            model=model,
            messages=self.conversations[session_id],
            config=config,
            session_id=session_id,
            user_id=user_id,
            metadata={
                **(metadata or {}),
                "conversation_turn": len(self.conversations[session_id]),
                "conversation_type": "multi_turn"
            },
            tags=["conversation", "multi_turn"]
        )
        
        # Add the assistant's response to the conversation
        self.conversations[session_id].append(
            ChatMessage(role=MessageRole.ASSISTANT, content=response.content)
        )
        
        return response
    
    def get_conversation_history(self, session_id: str) -> List[ChatMessage]:
        """Get the full conversation history for a session."""
        return self.conversations.get(session_id, []).copy()
    
    def clear_conversation(self, session_id: str):
        """Clear the conversation history for a session."""
        if session_id in self.conversations:
            del self.conversations[session_id]
    
    def export_conversation(self, session_id: str) -> Dict[str, Any]:
        """Export conversation as a dictionary."""
        if session_id not in self.conversations:
            return {
                "session_id": session_id, 
                "messages": [],
                "message_count": 0
            }
        
        return {
            "session_id": session_id,
            "messages": [msg.to_dict() for msg in self.conversations[session_id]],
            "message_count": len(self.conversations[session_id])
        }


def estimate_tokens(text: str) -> int:
    """
    Rough estimation of token count for a given text.
    This is a simple approximation and may not be accurate for all models.
    """
    # Rough approximation: 1 token ≈ 4 characters for English text
    return len(text) // 4


def format_cost(cost: float) -> str:
    """Format cost as a human-readable string."""
    if cost < 0.001:
        return f"${cost:.6f}"
    elif cost < 0.01:
        return f"${cost:.4f}"
    else:
        return f"${cost:.2f}"


def get_model_recommendations(use_case: str = "general") -> List[str]:
    """
    Get model recommendations based on use case.
    
    Args:
        use_case: The intended use case ('general', 'coding', 'creative', 'analysis', 'cost_effective')
        
    Returns:
        List of recommended model IDs
    """
    recommendations = {
        "general": [
            "anthropic.claude-3-sonnet-20240229-v1:0",
            "meta.llama2-70b-chat-v1",
            "amazon.titan-text-express-v1"
        ],
        "coding": [
            "anthropic.claude-3-sonnet-20240229-v1:0",
            "meta.llama2-70b-chat-v1"
        ],
        "creative": [
            "anthropic.claude-3-sonnet-20240229-v1:0",
            "anthropic.claude-v2:1"
        ],
        "analysis": [
            "anthropic.claude-3-sonnet-20240229-v1:0",
            "ai21.j2-ultra-v1"
        ],
        "cost_effective": [
            "anthropic.claude-3-haiku-20240307-v1:0",
            "amazon.titan-text-lite-v1",
            "cohere.command-light-text-v14"
        ]
    }
    
    return recommendations.get(use_case, recommendations["general"])

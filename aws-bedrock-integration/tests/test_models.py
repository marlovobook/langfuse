"""Tests for the data models."""

import unittest
from datetime import datetime
from bedrock_langfuse.models import (
    ChatMessage, MessageRole, ModelUsage, ChatResponse, 
    ConversationContext, ModelConfig, SUPPORTED_MODELS
)


class TestChatMessage(unittest.TestCase):
    """Test ChatMessage model."""
    
    def test_chat_message_creation(self):
        """Test creating a ChatMessage."""
        message = ChatMessage(
            role=MessageRole.USER,
            content="Hello, world!"
        )
        
        self.assertEqual(message.role, MessageRole.USER)
        self.assertEqual(message.content, "Hello, world!")
        self.assertIsInstance(message.timestamp, datetime)
    
    def test_chat_message_with_timestamp(self):
        """Test creating a ChatMessage with custom timestamp."""
        custom_time = datetime(2023, 1, 1, 12, 0, 0)
        message = ChatMessage(
            role=MessageRole.ASSISTANT,
            content="Hi there!",
            timestamp=custom_time
        )
        
        self.assertEqual(message.timestamp, custom_time)
    
    def test_chat_message_to_dict(self):
        """Test converting ChatMessage to dictionary."""
        message = ChatMessage(
            role=MessageRole.SYSTEM,
            content="You are helpful."
        )
        
        message_dict = message.to_dict()
        
        self.assertEqual(message_dict["role"], "system")
        self.assertEqual(message_dict["content"], "You are helpful.")
        self.assertIn("timestamp", message_dict)


class TestModelUsage(unittest.TestCase):
    """Test ModelUsage model."""
    
    def test_model_usage_creation(self):
        """Test creating ModelUsage."""
        usage = ModelUsage(
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            estimated_cost=0.001,
            model_id="test-model"
        )
        
        self.assertEqual(usage.input_tokens, 100)
        self.assertEqual(usage.output_tokens, 50)
        self.assertEqual(usage.total_tokens, 150)
        self.assertEqual(usage.estimated_cost, 0.001)
        self.assertEqual(usage.model_id, "test-model")
    
    def test_model_usage_to_dict(self):
        """Test converting ModelUsage to dictionary."""
        usage = ModelUsage(
            input_tokens=75,
            output_tokens=25,
            total_tokens=100
        )
        
        usage_dict = usage.to_dict()
        
        self.assertEqual(usage_dict["input_tokens"], 75)
        self.assertEqual(usage_dict["output_tokens"], 25)
        self.assertEqual(usage_dict["total_tokens"], 100)
        self.assertIsNone(usage_dict["estimated_cost"])
        self.assertIsNone(usage_dict["model_id"])


class TestChatResponse(unittest.TestCase):
    """Test ChatResponse model."""
    
    def test_chat_response_creation(self):
        """Test creating ChatResponse."""
        usage = ModelUsage(
            input_tokens=10,
            output_tokens=15,
            total_tokens=25
        )
        
        response = ChatResponse(
            content="Hello!",
            model="test-model",
            usage=usage,
            finish_reason="stop",
            response_time=1.5,
            trace_id="trace-123"
        )
        
        self.assertEqual(response.content, "Hello!")
        self.assertEqual(response.model, "test-model")
        self.assertEqual(response.usage, usage)
        self.assertEqual(response.finish_reason, "stop")
        self.assertEqual(response.response_time, 1.5)
        self.assertEqual(response.trace_id, "trace-123")
    
    def test_chat_response_to_dict(self):
        """Test converting ChatResponse to dictionary."""
        usage = ModelUsage(input_tokens=5, output_tokens=10, total_tokens=15)
        response = ChatResponse(
            content="Test response",
            model="test-model",
            usage=usage
        )
        
        response_dict = response.to_dict()
        
        self.assertEqual(response_dict["content"], "Test response")
        self.assertEqual(response_dict["model"], "test-model")
        self.assertIn("usage", response_dict)
        self.assertEqual(response_dict["usage"]["total_tokens"], 15)


class TestConversationContext(unittest.TestCase):
    """Test ConversationContext model."""
    
    def test_conversation_context_creation(self):
        """Test creating ConversationContext."""
        context = ConversationContext(
            session_id="session-123",
            user_id="user-456",
            metadata={"topic": "testing"},
            tags=["test", "demo"]
        )
        
        self.assertEqual(context.session_id, "session-123")
        self.assertEqual(context.user_id, "user-456")
        self.assertEqual(context.metadata, {"topic": "testing"})
        self.assertEqual(context.tags, ["test", "demo"])
    
    def test_conversation_context_minimal(self):
        """Test creating ConversationContext with minimal data."""
        context = ConversationContext(session_id="session-123")
        
        self.assertEqual(context.session_id, "session-123")
        self.assertIsNone(context.user_id)
        self.assertIsNone(context.metadata)
        self.assertIsNone(context.tags)
    
    def test_conversation_context_to_dict(self):
        """Test converting ConversationContext to dictionary."""
        context = ConversationContext(
            session_id="session-123",
            metadata={"key": "value"}
        )
        
        context_dict = context.to_dict()
        
        self.assertEqual(context_dict["session_id"], "session-123")
        self.assertIsNone(context_dict["user_id"])
        self.assertEqual(context_dict["metadata"], {"key": "value"})
        self.assertEqual(context_dict["tags"], [])


class TestModelConfig(unittest.TestCase):
    """Test ModelConfig model."""
    
    def test_model_config_defaults(self):
        """Test ModelConfig with default values."""
        config = ModelConfig()
        
        self.assertEqual(config.temperature, 0.7)
        self.assertEqual(config.max_tokens, 1000)
        self.assertEqual(config.top_p, 0.9)
        self.assertIsNone(config.top_k)
        self.assertIsNone(config.stop_sequences)
    
    def test_model_config_custom(self):
        """Test ModelConfig with custom values."""
        config = ModelConfig(
            temperature=0.5,
            max_tokens=500,
            top_p=0.8,
            top_k=40,
            stop_sequences=["STOP"]
        )
        
        self.assertEqual(config.temperature, 0.5)
        self.assertEqual(config.max_tokens, 500)
        self.assertEqual(config.top_p, 0.8)
        self.assertEqual(config.top_k, 40)
        self.assertEqual(config.stop_sequences, ["STOP"])
    
    def test_model_config_to_dict(self):
        """Test converting ModelConfig to dictionary."""
        config = ModelConfig(
            temperature=0.8,
            max_tokens=200,
            top_k=30
        )
        
        config_dict = config.to_dict()
        
        self.assertEqual(config_dict["temperature"], 0.8)
        self.assertEqual(config_dict["max_tokens"], 200)
        self.assertEqual(config_dict["top_p"], 0.9)  # default
        self.assertEqual(config_dict["top_k"], 30)
        self.assertNotIn("stop_sequences", config_dict)  # None value excluded
    
    def test_model_config_to_dict_excludes_none(self):
        """Test that to_dict excludes None values."""
        config = ModelConfig(temperature=0.5)  # Only set temperature
        config_dict = config.to_dict()
        
        self.assertIn("temperature", config_dict)
        self.assertIn("max_tokens", config_dict)
        self.assertIn("top_p", config_dict)
        self.assertNotIn("top_k", config_dict)
        self.assertNotIn("stop_sequences", config_dict)


class TestSupportedModels(unittest.TestCase):
    """Test SUPPORTED_MODELS configuration."""
    
    def test_supported_models_structure(self):
        """Test that SUPPORTED_MODELS has correct structure."""
        self.assertIsInstance(SUPPORTED_MODELS, dict)
        self.assertGreater(len(SUPPORTED_MODELS), 0)
        
        for model_id, config in SUPPORTED_MODELS.items():
            self.assertIsInstance(model_id, str)
            self.assertIsInstance(config, dict)
            
            # Check required fields
            required_fields = ["name", "provider", "input_cost_per_1k", "output_cost_per_1k", "max_tokens"]
            for field in required_fields:
                self.assertIn(field, config, f"Missing {field} in {model_id}")
    
    def test_anthropic_models_present(self):
        """Test that Anthropic models are present."""
        anthropic_models = [k for k in SUPPORTED_MODELS.keys() if k.startswith("anthropic.")]
        self.assertGreater(len(anthropic_models), 0)
        
        # Check specific models
        self.assertIn("anthropic.claude-3-haiku-20240307-v1:0", SUPPORTED_MODELS)
        
        # Check Anthropic model properties
        claude_haiku = SUPPORTED_MODELS["anthropic.claude-3-haiku-20240307-v1:0"]
        self.assertEqual(claude_haiku["provider"], "Anthropic")
        self.assertEqual(claude_haiku["name"], "Claude 3 Haiku")
    
    def test_amazon_models_present(self):
        """Test that Amazon models are present."""
        amazon_models = [k for k in SUPPORTED_MODELS.keys() if k.startswith("amazon.")]
        self.assertGreater(len(amazon_models), 0)
        
        self.assertIn("amazon.titan-text-express-v1", SUPPORTED_MODELS)
        
        titan = SUPPORTED_MODELS["amazon.titan-text-express-v1"]
        self.assertEqual(titan["provider"], "Amazon")
    
    def test_meta_models_present(self):
        """Test that Meta models are present."""
        meta_models = [k for k in SUPPORTED_MODELS.keys() if k.startswith("meta.")]
        self.assertGreater(len(meta_models), 0)
        
        self.assertIn("meta.llama2-70b-chat-v1", SUPPORTED_MODELS)
        
        llama = SUPPORTED_MODELS["meta.llama2-70b-chat-v1"]
        self.assertEqual(llama["provider"], "Meta")
    
    def test_cost_values_are_numeric(self):
        """Test that cost values are numeric."""
        for model_id, config in SUPPORTED_MODELS.items():
            input_cost = config["input_cost_per_1k"]
            output_cost = config["output_cost_per_1k"]
            
            self.assertIsInstance(input_cost, (int, float), f"Input cost not numeric for {model_id}")
            self.assertIsInstance(output_cost, (int, float), f"Output cost not numeric for {model_id}")
            self.assertGreaterEqual(input_cost, 0, f"Negative input cost for {model_id}")
            self.assertGreaterEqual(output_cost, 0, f"Negative output cost for {model_id}")
    
    def test_max_tokens_values(self):
        """Test that max_tokens values are reasonable."""
        for model_id, config in SUPPORTED_MODELS.items():
            max_tokens = config["max_tokens"]
            
            self.assertIsInstance(max_tokens, int, f"Max tokens not integer for {model_id}")
            self.assertGreater(max_tokens, 0, f"Non-positive max tokens for {model_id}")
            self.assertLessEqual(max_tokens, 100000, f"Unreasonably high max tokens for {model_id}")


class TestMessageRole(unittest.TestCase):
    """Test MessageRole enum."""
    
    def test_message_role_values(self):
        """Test MessageRole enum values."""
        self.assertEqual(MessageRole.USER.value, "user")
        self.assertEqual(MessageRole.ASSISTANT.value, "assistant")
        self.assertEqual(MessageRole.SYSTEM.value, "system")
    
    def test_message_role_from_string(self):
        """Test creating MessageRole from string."""
        user_role = MessageRole("user")
        assistant_role = MessageRole("assistant")
        system_role = MessageRole("system")
        
        self.assertEqual(user_role, MessageRole.USER)
        self.assertEqual(assistant_role, MessageRole.ASSISTANT)
        self.assertEqual(system_role, MessageRole.SYSTEM)


if __name__ == "__main__":
    unittest.main()
